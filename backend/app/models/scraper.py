import uuid
from datetime import datetime, timezone
import uuid

from sqlmodel import Field, SQLModel



class DataLakeScrapper(SQLModel, table=True):
    __tablename__ = "datalake_scraper" # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    url: str = Field(index=True)
    source_portal: str
    raw_html: str
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
