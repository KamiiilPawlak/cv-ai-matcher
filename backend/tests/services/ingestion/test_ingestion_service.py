from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.services.ingestion_service.ingestion_service import IngestionService


@pytest.fixture
def mock_file_service() -> MagicMock:
    service = MagicMock()
    service.save_upload_file = AsyncMock(return_value="mocked_path/cv.pdf")
    return service


@pytest.fixture
def mock_ocr_service() -> MagicMock:
    service = MagicMock()
    service.process_document = AsyncMock(
        return_value="Sztucznie odczytany tekst z CV Kamila"
    )
    return service


@pytest.fixture
def ingestion_service(
    mock_file_service: MagicMock, mock_ocr_service: MagicMock
) -> IngestionService:
    return IngestionService(
        file_service=mock_file_service, ocr_service=mock_ocr_service
    )


@pytest.mark.asyncio
async def test_process_cv_document_success(
    ingestion_service: IngestionService,
    mock_file_service: MagicMock,
    mock_ocr_service: MagicMock,
    mocker: Any,
) -> None:

    fake_session = MagicMock()
    fake_content = b"Fake PDF binary content"
    fake_filename = "kamil_cv.pdf"

    mocker.patch(
        "app.services.ingestion_service.ingestion_service.verify_file_integrity",
        return_value="application/pdf",
    )

    mock_db_cv = MagicMock()
    mock_db_cv.id = "123e4567-e89b-12d3-a456-426614174000"

    mocker.patch("app.crud.save_raw_cv", return_value=mock_db_cv)

    result = await ingestion_service.process_cv_document(
        session=fake_session, content=fake_content, filename=fake_filename
    )

    assert result["message"] == "Zakonczone sukcesem"
    assert result["file_id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert result["mime_type"] == "application/pdf"
    assert result["extracted_content"] == "Sztucznie odczytany tekst z CV Kamila"

    mock_ocr_service.process_document.assert_called_once_with(
        fake_content, "application/pdf"
    )
    mock_file_service.save_upload_file.assert_called_once_with(
        fake_content, original_filename=fake_filename
    )


@pytest.mark.asyncio
async def test_process_cv_document_file_too_large(
    ingestion_service: IngestionService, mocker: Any
) -> None:
    fake_session = MagicMock()
    fake_filename = "potezny_plik.pdf"

    mocker.patch("app.core.config.settings.MAX_FILE_SIZE", 5)

    too_large_content = b"0123456789"

    with pytest.raises(ValueError, match="Plik jest za duzy"):
        await ingestion_service.process_cv_document(
            session=fake_session, content=too_large_content, filename=fake_filename
        )


@pytest.mark.asyncio
async def test_delete_cv_document_not_found() -> None:

    fake_session = MagicMock()

    fake_session.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await IngestionService.delete_cv_document(
            session=fake_session, file_id="nieistniejacy-id-123"
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Nie znaleziono dokumentu o podanym ID"
