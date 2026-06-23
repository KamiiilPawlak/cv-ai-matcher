from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class DataLakeCV(SQLModel, table=True):
    """Raw CV data stored in the application's data lake layer"""

    __tablename__ = "data_lake_cv"  # type: ignore

    id: UUID = Field(
        default_factory=uuid4, primary_key=True, index=True, nullable=False
    )
    filename: str
    raw_text: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProcessedCV(SQLModel, table=True):
    __tablename__: str = "processed_cv"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    file_id: UUID = Field(foreign_key="data_lake_cv.id", index=True, unique=True)

    normalized_text: str

    email: str | None = Field(default=None, index=True)
    phone: str | None = Field(default=None)

    
    processed_at: datetime = Field(default_factory=datetime.utcnow)
