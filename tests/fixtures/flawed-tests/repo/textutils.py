"""Text helpers."""
import re


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def truncate(text: str, limit: int) -> str:
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def word_count(text: str) -> int:
    return len(text.split())
