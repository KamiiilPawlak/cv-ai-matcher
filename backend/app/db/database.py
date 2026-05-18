from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from ..core.config import settings
from ..models.cv import RawCV, RawJobOfferts

engine = create_engine(settings.DATABASE_URL, echo=True)


def init_db() -> None:
    _ = [RawCV, RawJobOfferts]
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
