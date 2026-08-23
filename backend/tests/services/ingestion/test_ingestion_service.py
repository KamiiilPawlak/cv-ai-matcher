from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.cv_document import CVDocumentLake
from app.models.cv_raw_text import CVRawText
from app.services.ingestion_service.ingestion_service import IngestionService


async def test_get_comparison_data_integration_success(
    db_session: Session,
    mock_file_service: MagicMock,
    mock_ocr_service: MagicMock,
) -> None:

    service = IngestionService(
        file_service=mock_file_service, ocr_service=mock_ocr_service
    )

    doc_id = uuid4()
    doc = CVDocumentLake(
        id=doc_id,
        original_filename="jan_kowalski_cv.pdf",
        storage_path="uploads/jan_kowalski_cv.pdf",
        file_size_bytes=2048,
        mime_type="application/pdf",
    )
    db_session.add(doc)

    raw_text_entry = CVRawText(
        cv_document_id=doc_id,
        raw_text="Jan Kowalski - Python Developer z doświadczeniem.",
        character_count=49,
        word_count=6,
        page_count=1,
        extraction_tool="pdfplumber",
    )
    db_session.add(raw_text_entry)

    db_session.flush()

    result = await service.get_comparison_data(session=db_session, file_id=doc_id)

    assert result["file_id"] == doc_id
    assert result["filename"] == "jan_kowalski_cv.pdf"
    assert result["has_been_processed"] is True
    assert result["raw_data_layer"]["char_count"] == 49
    assert result["raw_data_layer"]["word_count"] == 6
    assert (
        result["raw_data_layer"]["text_preview"]
        == "Jan Kowalski - Python Developer z doświadczeniem."
    )


async def test_get_comparison_data_integration_not_found(
    db_session: Session,
    mock_file_service: MagicMock,
    mock_ocr_service: MagicMock,
) -> None:

    service = IngestionService(
        file_service=mock_file_service, ocr_service=mock_ocr_service
    )
    non_existing_id = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        await service.get_comparison_data(session=db_session, file_id=non_existing_id)

    assert exc_info.value.status_code == 404
    assert str(non_existing_id) in exc_info.value.detail
