from unittest.mock import AsyncMock, patch

import pytest  # type: ignore
from backend.app.services.cv_ingestion.ocr_service import OCRService

pytestmark = pytest.mark.anyio


async def test_process_document_digital_pdf_success():

    fake_content = b"fake pdf bytes"
    fake_mime = "application/pdf"
    expected_text = (
        "To jest wyciagniety tekst cyfrowy z pliku PDF, ktory ma ponad sto znakow, "
        "wiec algorytm powinien go zaakceptowac i nie uruchamiac zadnego ciezkiego "
        "procesu OCR na obrazkach."
    )

    with (
        patch.object(
            OCRService, "_extract_digital_text", return_value=expected_text
        ) as mock_digital,
        patch.object(
            OCRService, "_extract_via_ocr", new_callable=AsyncMock
        ) as mock_ocr,
    ):
        result = await OCRService.process_document(fake_content, fake_mime)

        assert result == expected_text
        mock_digital.assert_called_once_with(fake_content)

        mock_ocr.assert_not_called()


async def test_process_document_fallback_to_ocr():
    # Arrange
    fake_content = b"fake scanned pdf bytes"
    fake_mime = "application/pdf"
    too_short_text = "Za krotki"
    expected_ocr_text = "Tekst odczytany przez Tesseract z obrazka o wysokiej jakosci."

    with (
        patch.object(
            OCRService, "_extract_digital_text", return_value=too_short_text
        ) as mock_digital,
        patch.object(
            OCRService,
            "_extract_via_ocr",
            new_callable=AsyncMock,
            return_value=expected_ocr_text,
        ) as mock_ocr,
    ):
        result = await OCRService.process_document(fake_content, fake_mime)

        assert result == expected_ocr_text
        mock_digital.assert_called_once_with(fake_content)

        mock_ocr.assert_called_once_with(fake_content, fake_mime)


async def test_process_document_image_goes_straight_to_ocr():

    fake_content = b"fake png bytes"
    fake_mime = "image/png"
    expected_ocr_text = "Tekst wyciągnięty bezpośrednio ze zdjęcia."

    with (
        patch.object(OCRService, "_extract_digital_text") as mock_digital,
        patch.object(
            OCRService,
            "_extract_via_ocr",
            new_callable=AsyncMock,
            return_value=expected_ocr_text,
        ) as mock_ocr,
    ):
        result = await OCRService.process_document(fake_content, fake_mime)

        assert result == expected_ocr_text

        mock_digital.assert_not_called()
        mock_ocr.assert_called_once_with(fake_content, fake_mime)
