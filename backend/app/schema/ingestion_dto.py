# app/models/ingestion_dto.py
import uuid

from pydantic import BaseModel


class IngestionResponse(BaseModel):
    message: str
    file_id: uuid.UUID
    mime_type: str
    original_name: str
    extracted_content: str
