import pytest  # type: ignore
from backend.app.services.cv_ingestion.file_service import save_upload_file

from app.core.config import settings

pytestmark = pytest.mark.anyio


async def test_save_upload_file_succes(tmp_path):

    settings.UPLOAD_DIR = tmp_path
    test_content = b"Sztuczna zawartosc pliku CV"
    original_name = "moje_cv_2026.pdf"

    generated_safe_name = await save_upload_file(test_content, original_name)

    assert generated_safe_name.endswith(".pdf")
    assert (tmp_path / generated_safe_name).exists() is True


async def test_save_upload_file_multiple_dots_in_name(tmp_path):
    settings.UPLOAD_DIR = tmp_path

    original_name = "john.smith.cv.final.v2.docx"

    generated_safe_name = await save_upload_file(b"content", original_name)

    assert generated_safe_name.endswith(".docx")
    assert not generated_safe_name.endswith(".v2.docx")


async def test_save_upload_file_no_extension(tmp_path):
    settings.UPLOAD_DIR = tmp_path
    original_name = "PlikBezRozszerzenia"

    generated_safe_name = await save_upload_file(b"content", original_name)

    assert generated_safe_name.endswith(".PlikBezRozszerzenia")
