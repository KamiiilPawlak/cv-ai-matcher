import regex
from loguru import logger


class CVTextNormalizer:
    def __init__(self) -> None:

        self._months_map: dict[str, str] = {
            # Polish
            "styczeń": "01",
            "stycznia": "01",
            "styczniu": "01",
            "sty": "01",
            "luty": "02",
            "lutego": "02",
            "lutym": "02",
            "lut": "02",
            "marzec": "03",
            "marca": "03",
            "marcu": "03",
            "mar": "03",
            "kwiecień": "04",
            "kwietnia": "04",
            "kwietniu": "04",
            "kwi": "04",
            "maj": "05",
            "maja": "05",
            "maju": "05",
            "czerwiec": "06",
            "czerwca": "06",
            "czerwcu": "06",
            "cze": "06",
            "lipiec": "07",
            "lipca": "07",
            "lipcu": "07",
            "lip": "07",
            "sierpień": "08",
            "sierpnia": "08",
            "sierpniu": "08",
            "sie": "08",
            "wrzesień": "09",
            "września": "09",
            "wrześniu": "09",
            "wrz": "09",
            "październik": "10",
            "października": "10",
            "październiku": "10",
            "paź": "10",
            "listopad": "11",
            "listopada": "11",
            "listopadzie": "11",
            "lis": "11",
            "grudzień": "12",
            "grudnia": "12",
            "grudniu": "12",
            "gru": "12",
            # english
            "january": "01",
            "jan": "01",
            "february": "02",
            "feb": "02",
            "march": "03",
            "april": "04",
            "apr": "04",
            "may": "05",
            "june": "06",
            "jun": "06",
            "july": "07",
            "jul": "07",
            "august": "08",
            "aug": "08",
            "september": "09",
            "sept": "09",
            "sep": "09",
            "october": "10",
            "oct": "10",
            "november": "11",
            "nov": "11",
            "december": "12",
            "dec": "12",
        }

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

        return regex.sub(
            r"\b([a-cC-C])[-\s]*([1-2])\b",
            lambda m: f"{m.group(1).upper()}{m.group(2)}",
            text,
        )

    def _normalize_phone_numbers(self, text: str) -> str:
        def clean_phone(match: regex.Match) -> str:

            cleaned = regex.sub(r"[\s\-\(\)]", "", match.group(0))
            return f"{cleaned}"

        phone_pattern = (
            r"(?:\+\d{1,3}[ \t\-]*)?\(?\d{3}\)?[ \t\-]*\d{3}[ \t\-]*\d{3,4}\b"
        )
        return regex.sub(phone_pattern, clean_phone, text)

    def _normalize_hyperlinks(self, text: str) -> str:

        text = regex.sub(
            r"https?://(www\.)?(github\.com|linkedin\.com|linkedin\.pl|linkedin\.com/in)/?",
            r"\2/",
            text,
            flags=regex.IGNORECASE,
        )
        return regex.sub(r"(?<!:)/{2,}", "/", text)

    def _normalize_dates(self, text: str) -> str:
        text = regex.sub(r"\b(0[1-9]|1[0-2])[\./](20\d{2}|19\d{2})\b", r"\2-\1", text)

        for month_name, month_num in self._months_map.items():
            pattern = rf"\b{month_name}\s+(20\d{{2}}|19\d{{2}})\b"
            text = regex.compile(pattern, regex.IGNORECASE).sub(
                rf"\1-{month_num}", text
            )

            text = regex.sub(
                r"\b(obecnie|teraz|aktualnie|present|w tej chwili|do dziś)\b",
                "PRESENT",
                text,
                flags=regex.IGNORECASE,
            )
        return text
