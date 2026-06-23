# app/models/ingestion_dto.py
from typing import Any, Dict, Optional
import uuid

from pydantic import BaseModel, Field


class IngestionResponse(BaseModel):
    message: str
    file_id: uuid.UUID
    mime_type: str
    original_name: str
    extracted_content: str



class ExtractedMetadata(BaseModel):
    """Ustrukturyzowany model na dane kontaktowe wyciągnięte w etapie Enrichment."""
    email: Optional[str] = Field(None, description="Wyciągnięty adres email kandydata")
    phone: Optional[str] = Field(None, description="Wyciągnięty numer telefonu kandydata")


class ProcessedCVTO(BaseModel):
    """Główny kontener na dane z całego pipeline ETL."""
    metadata: ExtractedMetadata
    setions: Dict[str, str] = Field(default_factory=dict, description="Pocięte sekcje CV")
    full_processed_text: str = Field(..., description="Pełny tekst po normalizacji")