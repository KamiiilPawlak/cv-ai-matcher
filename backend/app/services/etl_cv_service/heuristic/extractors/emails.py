from typing import Final

import regex

EMAIL_PATTERN = regex.compile(r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}", regex.IGNORECASE)


def extract_email(text: str) -> str | None:

    match: Final[regex.Match | None] = EMAIL_PATTERN.search(text)

    if not match:
        return None

    return match.group(0).strip().lower() if match else None
