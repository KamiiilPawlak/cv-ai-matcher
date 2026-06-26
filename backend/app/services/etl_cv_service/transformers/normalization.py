import dateparser  # type: ignore[import-untyped]
import regex  # type: ignore[import-untyped]
from loguru import logger


class CVTextNormalizer:
    def __init__(self) -> None:

        self._text_date_pattern = regex.compile(
            r"\b(\p{L}+)\s+(20\d{2}|19\d{2})\b", regex.IGNORECASE
        )

        self._lang_pattern = regex.compile(r"\b([a-cA-C])[-\s]*([1-2])\b")
        self._phone_pattern = regex.compile(
            r"(?:\+\d{1,3}[ \t\-]*)?\(?\d{3}\)?[ \t\-]*\d{3}[ \t\-]*\d{3,4}\b"
        )
        self._phone_clean_pattern = regex.compile(r"[\s\-\(\)]")
        self._hyperlink_pattern = regex.compile(
            r"https?://(www\.)?(github\.com|linkedin\.com|linkedin\.pl|linkedin\.com/in)/?",
            regex.IGNORECASE,
        )
        self._slash_pattern = regex.compile(r"(?<!:)/{2,}")
        self._digits_date_pattern = regex.compile(
            r"\b(0[1-9]|1[0-2])[\./](20\d{2}|19\d{2})\b"
        )
        self._present_pattern = regex.compile(
            r"\b(obecnie|teraz|aktualnie|present|w tej chwili|do dziś)\b",
            regex.IGNORECASE,
        )

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

        return self._lang_pattern.sub(
            lambda m: f"{m.group(1).upper()}{m.group(2)}", text
        )

    def _normalize_phone_numbers(self, text: str) -> str:
        def clean_phone(match: regex.Match) -> str:

            return self._phone_clean_pattern.sub("", match.group(0))

        return self._phone_pattern.sub(clean_phone, text)

    def _normalize_hyperlinks(self, text: str) -> str:

        text = self._hyperlink_pattern.sub(r"\2/", text)
        return self._slash_pattern.sub("/", text)

    def _normalize_dates(self, text: str) -> str:
        text = self._digits_date_pattern.sub(r"\2-\1", text)

        def replace_with_dateparser(match: regex.Match) -> str:
            full_match = match.group(0)
            year = match.group(2)

            parsed_date = dateparser.parse(full_match, languages=["pl", "en"])
            if parsed_date:
                return parsed_date.strftime("%Y-%m")
            return f"{year}-01"

        text = self._text_date_pattern.sub(replace_with_dateparser, text)
        return self._present_pattern.sub("PRESENT", text)
