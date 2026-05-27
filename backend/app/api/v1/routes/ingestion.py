from typing import Any, Dict

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger

from app.schema.ingestion_dto import IngestionResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.post("/upload", response_model=IngestionResponse)
async def process_cv_upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    logger.info(f"Rozpoczeto proces uploadu pliku: {file.filename}")
    if file.filename is None:
        logger.warning("Odrzucono request z powodu braku nazwy filename is None")
        raise HTTPException(status_code=400, detail="Nazwa pliku jest wymagana")

    content = await file.read()

    try:
        result = await IngestionService.process_cv_document(content, file.filename)
        logger.info(f"Plik {file.filename} zostal poprawnie przetworzony")
        return result
    except ValueError as e:
        logger.warning(
            f"Blad walidacji pliku {file.filename} w IngestionService {str(e)}"
        )
        raise HTTPException(status_code=413, detail=str(e))
