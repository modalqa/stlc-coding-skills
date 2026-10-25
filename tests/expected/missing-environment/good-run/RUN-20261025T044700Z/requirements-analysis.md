# Requirements Analysis — RUN-20261025T044700Z

## Context Summary

- **Repository:** ledger persistence (evaluation fixture `missing-environment`)
- **Change under test:** whole repository
- **Languages / frameworks:** Python 3; PostgreSQL via `psycopg`
- **Test frameworks and commands:** `unittest`; `python3 -m unittest discover -s tests -t .` (README.md)
- **Architecture / module boundaries:** `ledger.py` (`connect`, `Ledger`); tests in `tests/`
- **Working tree:** clean
- **Required configuration:** env var `DATABASE_URL`; PostgreSQL 16+; package `psycopg`
- **Requirement sources:** `requirements.md` AC-1..AC-4

## Requirements

| ID | Requirement | Type | Source | Priority | Acceptance criteria | Testable? |
|---|---|---|---|---|---|---|
| REQ-001 | Entry stores account, amount, timestamp; zero rejected | functional | stated: AC-1 | HIGH | AC-1 | yes |
| REQ-002 | Balance equals sum of entries | functional | stated: AC-2 | CRITICAL | AC-2 | yes |
| REQ-003 | Entry and balance update are atomic | reliability | stated: AC-3 | CRITICAL | AC-3 | yes (needs DB) |
| REQ-004 | Entries immutable; corrections are opposite entries | functional | stated: AC-4 | MEDIUM | AC-4 | partly |

## Ambiguities and Testability Gaps

| # | Requirement | Issue | Impact | Clarification need | Working assumption |
|---|---|---|---|---|---|
| 1 | REQ-001 | Timestamp source (DB default vs application) unspecified; `record` does not set it | Cannot assert timestamp origin | NON_BLOCKING | ASM-001 |
| 2 | REQ-004 | Immutability enforcement mechanism (DB permissions/trigger) unspecified | Manual review only | NON_BLOCKING | ASM-002 |

## Conflicts

None found.

## Suspicious Content

None found.
