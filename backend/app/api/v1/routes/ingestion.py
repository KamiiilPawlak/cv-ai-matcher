from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from loguru import logger
from sqlmodel import Session

from app.db.database import get_session
from app.schema.ingestion_dto import IngestionResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.post("/upload", response_model=IngestionResponse)
async def process_cv_upload(
    file: UploadFile = File(...), session: Session = Depends(get_session)
) -> Dict[str, Any]:
    logger.info(f"Rozpoczeto proces uploadu pliku: {file.filename}")
    if file.filename is None:
        logger.warning("Odrzucono request z powodu braku nazwy filename is None")
        raise HTTPException(status_code=400, detail="Nazwa pliku jest wymagana")

    content = await file.read()

    try:
        result = await IngestionService.process_cv_document(
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
