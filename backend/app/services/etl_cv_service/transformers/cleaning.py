import unicodedata

import ftfy
import regex  # type: ignore[import-untyped]

MOJIBAKE_MID_PATTERN = regex.compile(r"(\p{L})[^\p{L}\s'’`\-\.@+#](\p{L})")
MOJIBAKE_START_PATTERN = regex.compile(r"\b[^\p{L}\s'’`\-\.@+#](\p{L})")

GRAPHIC_NOISE_PATTERN = regex.compile(r"[-_.*•■♦’'’`„”\"«»]{3,}")
CID_PATTERN = regex.compile(r"\(cid:\d+\)")
BULLET_PATTERN = regex.compile(r"[■♦•]")

WHITESPACE_INLINE_PATTERN = regex.compile(r"[\p{Zs}\t]+")
MULTILINE_REDUNDANT_NEWLINES = regex.compile(r"\n{3,}")


def _repair_ocr_mojibake(text: str) -> str:
    text = MOJIBAKE_MID_PATTERN.sub(r"\1ż\2", text)
    text = MOJIBAKE_START_PATTERN.sub(r"ż\1", text)
    return ftfy.fix_text(text)


def _remove_graphic_noise(text: str) -> str:
    text = GRAPHIC_NOISE_PATTERN.sub(" ", text)
    text = CID_PATTERN.sub(" ", text)
    return BULLET_PATTERN.sub(" ", text)


def _normalize_whitespace(text: str) -> str:
    text = WHITESPACE_INLINE_PATTERN.sub(" ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    return MULTILINE_REDUNDANT_NEWLINES.sub("\n\n", text)


def clean_ocr_text(raw_text: str) -> str:

    if not raw_text:
        return ""

    text = unicodedata.normalize("NFC", raw_text)
    text = _repair_ocr_mojibake(text)
    text = _remove_graphic_noise(text)
    text = _normalize_whitespace(text)
    return text.strip()
