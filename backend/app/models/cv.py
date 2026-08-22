from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class DataLakeCV(SQLModel, table=True):
    """Raw CV data stored in the application's data lake layer."""

    __tablename__ = "data_lake_cv"

    id: UUID = Field(
        default_factory=uuid4, primary_key=True, index=True, nullable=False
    )
    filename: str
    raw_text: str
    has_been_processed: bool = Field(default=False, index=True)
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )


class ProcessedCV(SQLModel, table=True):
    """Normalized CV data layer with extracted entities."""

    __tablename__ = "processed_cv"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    file_id: UUID = Field(
        foreign_key="data_lake_cv.id",
        ondelete="CASCADE",
        index=True,
        unique=True,
    )

    normalized_text: str

    email: str | None = Field(default=None, index=True)
    phone: str | None = Field(default=None)

    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
