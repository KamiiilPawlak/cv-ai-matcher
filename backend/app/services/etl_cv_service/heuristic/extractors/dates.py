from datetime import date
from typing import Dict, List, Optional, Union, cast

import dateparser
import regex as re


def _parse_single_date(date_str: str) -> Optional[Union[date, str]]:
    cleaned = date_str.strip().lower()

    if re.match(r"^(obecnie|present|now|aktualnie)$", cleaned):
        return "present"

    if re.fullmatch(r"\d{4}", cleaned):
        return date(int(cleaned), 1, 1)

    match_my = re.fullmatch(r"(\d{1,2})[\./](\d{4})", cleaned)
    if match_my:
        month, year = map(int, match_my.groups())
        return date(year, month, 1)

    settings = {
        "PREFER_DAY_OF_MONTH": "first",
        "PREFER_DATES_FROM": "past",
        "DATE_ORDER": "DMY",
        "REQUIRE_PARTS": ["year"],
    }

    parsed = dateparser.parse(date_str, settings=settings)
    if parsed is not None:
        return cast(date, parsed.date())

    return None


def extract_date_ranges(text: str) -> List[Dict[str, Optional[Union[date, bool, str]]]]:
    date_range_pattern = re.compile(
        r"((?:\d{1,2}[\./])?(?:\d{1,2}[\./])?\d{4})\s*(?:-|–|—|do|to)\s*((?:\d{1,2}[\./])?(?:\d{1,2}[\./])?\d{4}|obecnie|present|aktualnie|now)",
        re.IGNORECASE,
    )

    results: List[Dict[str, Optional[Union[date, bool, str]]]] = []

    for match in date_range_pattern.finditer(text):
        start_raw, end_raw = match.groups()

        start_date = _parse_single_date(start_raw)
        end_raw_parsed = _parse_single_date(end_raw)

        if isinstance(start_date, date):
            is_current = end_raw_parsed == "present"
            end_date = None if is_current else cast(Optional[date], end_raw_parsed)

            results.append(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_current": is_current,
                }
            )

    return results
