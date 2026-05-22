from typing import Any, Dict

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.ingestion_dto import IngestionResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.post("/upload", response_model=IngestionResponse)
async def process_cv_upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Nazwa pliku jest wymagana")

    content = await file.read()

    try:
        result = await IngestionService.process_cv_document(content, file.filename)
        return result
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))
