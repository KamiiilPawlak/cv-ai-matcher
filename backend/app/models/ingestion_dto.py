# app/models/ingestion_dto.py
from pydantic import BaseModel


class IngestionResponse(BaseModel):
    message: str
    file_id: str
    mime_type: str
    original_name: str
    extracted_content: str
