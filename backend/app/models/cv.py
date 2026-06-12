import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class DataLakeCV(SQLModel, table=True):
    """Raw CV data stored in the application's data lake layer"""

    __tablename__ = "data_lake_cv"  # type: ignore

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    filename: str
    raw_text: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



