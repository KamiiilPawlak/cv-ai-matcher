from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class CVRawText(SQLModel, table=True):
    __tablename__ = "cv_raw_text"

    cv_document_id: UUID = Field(
        foreign_key="cv_document_lake.id",
        primary_key=True,
        description="Identyfikator powiązanego dokumentu w tabeli Data Lake",
    )

    raw_text: str = Field(description="Surowa zawartość tekstowa wyciągnięta z PDF")
    character_count: int = Field(
        description="Łączna liczba znaków w wyciągniętym tekście"
    )
    word_count: int = Field(description="Szacowana liczba słów w tekście")
    page_count: Optional[int] = Field(
        default=None, description="Liczba stron w dokumencie PDF"
    )
    extraction_tool: str = Field(
        default="pdfplumber", description="Nazwa narzędzia/silnika ekstrakcji"
    )
    metadata_json: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="Metadane strukturalne zwracane przez parser",
    )
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Znacznik czasu wykonania ekstrakcji tekstu",
    )
