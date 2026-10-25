"""Customer feedback storage."""
import html
import re
from collections import Counter


class FeedbackStore:
    def __init__(self) -> None:
        self.items: list[str] = []

    def submit(self, text: str) -> None:
        text = (text or "").strip()
        if not 1 <= len(text) <= 500:
            raise ValueError("feedback must be 1-500 characters")
        self.items.append(text)

    def render(self, item: str) -> str:
        return f"<p>{item}</p>"

    def summary(self) -> dict:
        words = Counter(w for text in self.items for w in re.findall(r"[a-z]{4,}", text.lower()))
        return {"count": len(self.items), "top_words": [w for w, _ in words.most_common(3)]}
