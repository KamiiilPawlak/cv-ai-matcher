import pytest

from app.services import CVFileService, OCRService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def file_service():
    """Czysta instancja CVFileService do testow"""
    return CVFileService()


@pytest.fixture
def ocr_service():
    """ "Czysta instancja OCRService do testow"""
    return OCRService()
