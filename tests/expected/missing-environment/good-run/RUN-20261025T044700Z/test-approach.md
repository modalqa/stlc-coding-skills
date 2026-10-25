# Test Approach — RUN-20261025T044700Z

## Test Levels and Types

| Level | Applies? | Why | Types (functional, security, performance, compatibility, ...) |
|---|---|---|---|
| Unit / component | yes | Validation logic in `record` | functional, negative |
| Integration / contract | yes | Behaviour depends on PostgreSQL transactions | functional, reliability |
| System / end-to-end | no | No service surface | — |
| Acceptance | yes | ACs | functional |

## Quality Characteristics in Scope

Functional suitability and reliability (ISO/IEC 25010:2023, edition needs verification).

## Techniques

| Technique | Applied to | Reason |
|---|---|---|
| Equivalence partitioning | REQ-001, REQ-002 | Positive/negative/zero amounts |
| Error guessing (fault injection) | REQ-003 | Atomicity is shown by forcing the second statement to fail |
| Review | REQ-004 | No code path to test; immutability lives in the schema |

## Manual vs Automation

REQ-004 by manual schema review; the rest is automated integration tests against a disposable DB.

## Tools

Existing `unittest`; `psycopg` (LGPL-3.0 — dynamic use as a library is generally acceptable commercially, but flag it for legal review before redistribution).
