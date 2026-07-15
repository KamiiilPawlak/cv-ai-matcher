import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.services import CVFileService, OCRService

pytestmark = pytest.mark.asyncio

engine = create_engine(settings.DATABASE_URL, echo=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    from app.models.cv import DataLakeCV, ProcessedCV

    _ = [DataLakeCV, ProcessedCV]

    SQLModel.metadata.create_all(engine)

    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()

    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def file_service():
    """Czysta instancja CVFileService do testow"""
    return CVFileService()


@pytest.fixture
def ocr_service():
    """ "Czysta instancja OCRService do testow"""
    return OCRService()
