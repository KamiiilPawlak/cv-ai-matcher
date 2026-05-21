from typing import Any, Dict

from backend.app.models.ingestion_dto import IngestionResponse
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.post("/upload", response_model=IngestionResponse)
async def process_cv_upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Nazwa pliku jest wymagana")

    content = await file.read()

    try:
        # Całą brudną robotę zlecasz serwisowi w jednej linijce:
        result = await IngestionService.process_cv_document(content, file.filename)
        return result
    except ValueError as e:
        # Jeśli serwis rzuci błędem o za dużym pliku, łapiemy to i zmieniamy w HTTP 413
        raise HTTPException(status_code=413, detail=str(e))
