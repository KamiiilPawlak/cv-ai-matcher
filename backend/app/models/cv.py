import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class RawCV(SQLModel, table=True):
    """raw data"""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    filename: str
    raw_text: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class RawJobOfferts(SQLModel, table=True):
    """raw data"""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    title: str
    descritpion: str
    source: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
