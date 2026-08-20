from dataclasses import dataclass
from typing import Optional

import dateparser
import regex


@dataclass
class DateRange:
    start_date: Optional[str]
    end_date: Optional[str]
    is_current: bool


RANGE_PATTERN = regex.compile(
    r"((?:(?:0[1-9]|1[0-2])[./-])?(?:19|20)\d{2})\s*(?:-|–|—|do|to)\s*((?:(?:0[1-9]|1[0-2])[./-])?(?:19|20)\d{2}|obecnie|present|nadal|now)",
    regex.IGNORECASE,
)


CURRENT_KEYWORDS = {"obecnie", "present", "nadal", "now", "dzisiaj"}


def _parse_single_date(date_str: str) -> Optional[str]:
    if regex.fullmatch(r"(19|20)\d{2}", date_str):
        return f"{date_str}-01-01"

    parsed = dateparser.parse(
        date_str,
        languages=["pl", "en"],
        settings={"PREFER_DAY_OF_MONTH": "first"},
    )

    return parsed.strftime("%Y-%m-%d") if parsed else None


def extract_date_ranges(text: Optional[str]) -> list[DateRange]:
    """Wyciąga zakresy dat pracy/edukacji z surowego tekstu."""
    if not text or not text.strip():
        return []

    results: list[DateRange] = []
    matches = RANGE_PATTERN.findall(text)

    for start_raw, end_raw in matches:
        end_clean = end_raw.strip().lower()
        is_current = end_clean in CURRENT_KEYWORDS

        start_parsed = _parse_single_date(start_raw.strip())
        end_parsed = None if is_current else _parse_single_date(end_clean)

        results.append(
            DateRange(
                start_date=start_parsed, end_date=end_parsed, is_current=is_current
            )
        )

    return results
