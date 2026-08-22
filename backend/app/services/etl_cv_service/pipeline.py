from collections.abc import Callable
from typing import Any, cast

from fastapi.concurrency import run_in_threadpool


async def load_cv_text(
    session: Any,
    file_id: Any,
    get_raw_cv: Callable[..., Any],
) -> str:
    db_cv = await run_in_threadpool(get_raw_cv, session, file_id)

    if not db_cv or not db_cv.raw_text or not db_cv.raw_text.strip():
        raise ValueError(f"Nie znaleziono CV o ID {file_id}")

    return cast(str, db_cv.raw_text)
