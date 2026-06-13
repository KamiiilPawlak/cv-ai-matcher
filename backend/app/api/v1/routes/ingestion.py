from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from loguru import logger
from sqlmodel import Session

from app.crud.datalake_cv import get_raw_cv
from app.db.database import get_session
from app.schema.ingestion_dto import IngestionResponse
from app.services.etl_cv_service.transformers.cleaninig import clean_ocr_text
from app.services.ingestion_service.ingestion_service import IngestionService

router = APIRouter()


@router.post("/upload", response_model=IngestionResponse)
async def process_cv_upload(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    ingestion_service: IngestionService = Depends(),
) -> Dict[str, Any]:
    logger.info(f"Rozpoczeto proces uploadu pliku: {file.filename}")
    if file.filename is None:
        logger.warning("Odrzucono request z powodu braku nazwy filename is None")
        raise HTTPException(status_code=400, detail="Nazwa pliku jest wymagana")

    content = await file.read()

    try:
        result = await ingestion_service.process_cv_document(
            session,
            content,
            file.filename,
            file.content_type,
        )
        logger.info(f"Plik {file.filename} zostal poprawnie przetworzony")
        return result
    except ValueError as e:
        logger.warning(
            f"Blad walidacji pliku {file.filename} w IngestionService {str(e)}"
        )
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        logger.error(f"Nieoczekiwany blad podczas pretwarzania pliku: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Wystapil blad serwera podczas zapisu pliku"
        )


@router.delete("/cv/{file_id}", status_code=204)
async def delete_cv(file_id: str, session: Session = Depends(get_session)):
    logger.info(f"Zapytanie o usuniecie CV o ID: {file_id}")
    await IngestionService.delete_cv_document(session, file_id)

    return None


@router.get("/cv/{file_id}/test-clearn")
async def test_cv_cleaning(file_id, session: Session = Depends(get_session)):
    logger.info(f"Rozpoczeto testowe czyszczenie dla CV o id{file_id}  ")

    db_cv = get_raw_cv(session, file_id)

    if not db_cv:
        logger.warning(f"Nie znaleziono CV o ID {file_id} w Data Lake")
        raise HTTPException(status_code=404, detail="Nie znaleziono takiego CV w bazie")

    surowy_tekst = db_cv.raw_text
    logger.debug(f"Tekst przed czyszczeniem (RAW): {repr(surowy_tekst)}")
    wyczyszczony_tekst = clean_ocr_text(surowy_tekst)

    logger.success("Czyszczenie tekstu zakończone pomyślnie!")
    logger.debug(f"Tekst po czyszczeniu (CLEAN): \n{wyczyszczony_tekst}")

    return {
        "file_id": db_cv.id,
        "filename": db_cv.filename,
        "before_raw_snippet": repr(surowy_tekst),
        "after_clean_snippet": wyczyszczony_tekst,
    }
