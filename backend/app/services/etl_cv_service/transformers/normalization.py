from dataclasses import dataclass
from datetime import datetime
from typing import cast

import dateparser
import regex
from loguru import logger


@dataclass(frozen=True)
class NormalizerPatterns:
    """Niezmienny kontener na skompilowane wzorce regex."""

    text_date: regex.Pattern = regex.compile(
        r"\b(\p{L}+)\s+(20\d{2}|19\d{2})\b", regex.IGNORECASE
    )
    lang: regex.Pattern = regex.compile(r"\b([a-cA-C])[-\s]*([1-2])\b")
    phone: regex.Pattern = regex.compile(
        r"(?:\+\d{1,3}[ \t\-]*)?\(?\d{3}\)?[ \t\-]*\d{3}[ \t\-]*\d{3,4}\b"
    )
    phone_clean: regex.Pattern = regex.compile(r"[\s\-\(\)]")
    hyperlink: regex.Pattern = regex.compile(
        r"https?://(www\.)?(github\.com|linkedin\.com|linkedin\.pl|linkedin\.com/in)/?",
        regex.IGNORECASE,
    )
    slash: regex.Pattern = regex.compile(r"(?<!:)/{2,}")
    digits_date: regex.Pattern = regex.compile(
        r"\b(0[1-9]|1[0-2])[\./](20\d{2}|19\d{2})\b"
    )
    present: regex.Pattern = regex.compile(
        r"\b(obecnie|teraz|aktualnie|present|w tej chwili|do dziś)\b", regex.IGNORECASE
    )


class CVTextNormalizer:
    def __init__(self, patterns: NormalizerPatterns = NormalizerPatterns()) -> None:

        self._patterns = patterns

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""

        logger.debug("[ETL - NORMALIZER] Uruchomienie etapow transofrmacji.")

        text = self._normalize_dates(text)
        text = self._normalize_phone_numbers(text)
        text = self._normalize_hyperlinks(text)
        text = self._normalize_language_levels(text)

        return text

    def _normalize_language_levels(self, text: str) -> str:
        result = self._patterns.lang.sub(
            lambda m: f"{m.group(1).upper()}{m.group(2)}", text
        )
        return str(result)

    def _normalize_phone_numbers(self, text: str) -> str:
        def clean_phone(match: regex.Match) -> str:

            return str(self._patterns.phone_clean.sub("", match.group(0)))

        return cast(str, self._patterns.phone.sub(clean_phone, text))

    def _normalize_hyperlinks(self, text: str) -> str:

        text = self._patterns.hyperlink.sub(r"\2/", text)
        return cast(str, self._patterns.slash.sub("/", text))

    def _normalize_dates(self, text: str) -> str:
        text = self._patterns.digits_date.sub(r"\2-\1", text)

        def replace_with_dateparser(match: regex.Match) -> str:
            full_match = match.group(0)
            year = match.group(2)

            parsed_date = dateparser.parse(full_match, languages=["pl", "en"])
            if isinstance(parsed_date, datetime):
                return parsed_date.strftime("%Y-%m")
            return f"{year}-01"

        text = self._patterns.text_date.sub(replace_with_dateparser, text)
        return cast(str, self._patterns.present.sub("PRESENT", text))
