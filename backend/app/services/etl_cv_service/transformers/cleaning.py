import unicodedata

import ftfy
import regex # type: ignore[import-untyped]


def _repair_ocr_mojibake(text: str) -> str:
    text = regex.sub(r"(\p{L})[^\p{L}\s'’`\-\.@](\p{L})", r"\1ż\2", text)
    text = regex.sub(r"\b[^\p{L}\s'’`\-\.@](\p{L})", r"ż\1", text)
    return ftfy.fix_text(text)


def _remove_graphic_noise(text: str) -> str:
    text = regex.sub(r"[-_.*•■♦’'’`„”\"«»]{3,}", " ", text)
    text = regex.sub(r"\(cid:\d+\)", " ", text)
    return regex.sub(r"[■♦•]", " ", text)


def _normalize_whitespace(text: str) -> str:
    text = regex.sub(r"[\p{Zs}\t]+", " ", text)
    text = regex.sub(r"^[ ]+|[ ]+$", "", text, flags=regex.MULTILINE)
    return regex.sub(r"\n{3,}", "\n\n", text)


def clean_ocr_text(raw_text: str) -> str:

    if not raw_text:
        return ""

    text = _repair_ocr_mojibake(raw_text)
    text = unicodedata.normalize("NFC", text)
    text = _remove_graphic_noise(text)
    text = _normalize_whitespace(text)
    return text.strip()
