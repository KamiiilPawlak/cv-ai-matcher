import os
from typing import Any

import pytest

from app.core.config import settings


@pytest.mark.asyncio
async def test_save_upload_file_success(file_service: Any) -> None:

    fake_content = b"Sztuczna zawartosc plikow CV"
    fake_filename = "test_resume.pdf"

    saved_name = await file_service.save_upload_file(fake_content, fake_filename)

    assert saved_name is not None
    assert saved_name.endswith(".pdf")

    expected_path = settings.UPLOAD_DIR / saved_name
    assert expected_path.exists() is True

    if expected_path.exists():
        os.remove(expected_path)
