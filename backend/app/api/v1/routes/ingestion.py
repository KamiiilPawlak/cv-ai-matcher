from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from loguru import logger
from sqlmodel import Session, select

from app.crud.datalake_cv import get_raw_cv
from app.db.database import get_session
from app.models.cv import ProcessedCV
from app.schema.ingestion_dto import IngestionResponse
from app.services.etl_cv_service.pipeline import CvEtlPipeline
from app.services.ingestion_service.ingestion_service import IngestionService

router = APIRouter()


def get_cv_etl_pipeline() -> CvEtlPipeline:
    return CvEtlPipeline()


@router.post("/upload", response_model=IngestionResponse)
async def process_cv_upload(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    ingestion_service: IngestionService = Depends(),
    etl_pipeline: CvEtlPipeline = Depends(get_cv_etl_pipeline),
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
        logger.info(f"Plik {file.filename} zostal poprawnie przetworzony w Data Lake")

        raw_file_id: UUID | str | None = result.get("id") or result.get("file_id")

        if not raw_file_id:
            logger.error(
                "Nie udalo sie pobrac ID dokumentu z IngestionService. Przerywam automatyczny ETL."
            )
            raise HTTPException(
                status_code=500, detail="Błąd identyfikacji zapisanego dokumentu."
            )

        file_id: UUID = (
            raw_file_id if isinstance(raw_file_id, UUID) else UUID(str(raw_file_id))
        )

        logger.info(f"Automatyczne uruchamianie potoku ETL dla CV o ID: {file_id}")

        await etl_pipeline.execute(session, file_id)

        return result

    except ValueError as e:
        logger.warning(
            f"Blad walidacji pliku {file.filename} w IngestionService {str(e)}"
        )
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        logger.error(f"Nieoczekiwany blad podczas pretwarzania pliku: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Wystapil blad serwera podczas zapisu pliku i przetwarzania ETL",
        )


@router.delete("/cv/{file_id}", status_code=204)
async def delete_cv(file_id: str, session: Session = Depends(get_session)) -> None:
    logger.info(f"Zapytanie o usuniecie CV o ID: {file_id}")
    await IngestionService.delete_cv_document(session, file_id)

    return None


@router.get("/cv/{file_id}/compare")
async def compare_cv_data(
    file_id: UUID, session: Session = Depends(get_session)
) -> Dict[str, Any]:
    logger.info(f"Rozpoczęto weryfikację danych po ETL dla CV o ID: {file_id}")

    db_raw = get_raw_cv(session, file_id)
    if not db_raw:
        logger.warning(f"Nie znaleziono CV o ID {file_id} w Data Lake")
        raise HTTPException(status_code=404, detail="Nie znaleziono takiego CV w bazie")

    db_processed = session.exec(
        select(ProcessedCV).where(ProcessedCV.file_id == file_id)
    ).first()

    return {
        "file_id": file_id,
        "filename": db_raw.filename,
        "has_been_processed": db_processed is not None,
        "raw_data_layer": {
            "char_count": len(db_raw.raw_text),
            "text_preview": db_raw.raw_text,
        },
        "processed_data_layer": {
            "char_count": len(db_processed.normalized_text) if db_processed else 0,
            "text_preview": db_processed.normalized_text
            if db_processed
            else "BRAK PRZETWORZONYCH DANYCH",
        },
    }
