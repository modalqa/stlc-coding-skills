# Feedback Requirements

- AC-1: `submit(text)` stores feedback of 1 to 500 characters after trimming; otherwise ValueError.
- AC-2: Stored feedback is HTML-escaped when rendered with `render(item)`.
- AC-3: `summary()` returns the count of items and the 3 most common words (case-insensitive, words of 4+ letters).
