# textutils Requirements

- AC-1: `slugify(text)` lower-cases text, replaces each run of non-alphanumeric characters with a single hyphen, and strips leading/trailing hyphens. Example: "Hello, World!" -> "hello-world".
- AC-2: `truncate(text, limit)` returns text unchanged when `len(text) <= limit`; otherwise returns the first `limit - 1` characters followed by "…" (total length == limit). `limit` must be >= 1, else ValueError.
- AC-3: `word_count(text)` counts whitespace-separated words; empty or whitespace-only text has 0 words.
