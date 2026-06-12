from typing import Generator

from loguru import logger
from sqlmodel import Session, SQLModel, create_engine

from ..core.config import settings
from ..models.cv import DataLakeCV

engine = create_engine(settings.DATABASE_URL, echo=True)


def init_db() -> None:
    logger.info("Inicjalizacja bazy danych")
    _ = [DataLakeCV]
    logger.success("Tabela bazy danych zostala pomyslnie utworzona")
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
