# Test Plan — RUN-20261025T044700Z

## Objective

Verify ledger persistence rules AC-1..AC-4.

## Scope

REQ-001..REQ-004; RISK-001..RISK-004.

## Out of Scope

Performance; concurrent writers (recorded as a residual risk).

## Risk-Based Priorities

| Priority order | Risk IDs | Test case focus | Reason |
|---|---|---|---|
| 1 | RISK-001 | Atomicity under failure | CRITICAL |
| 2 | RISK-002 | Balance arithmetic | HIGH |
| 3 | RISK-003, RISK-004 | Validation, immutability | MEDIUM |

## Environment

A disposable local PostgreSQL 16+ database, reached through `DATABASE_URL`. Never a shared or production DB.

## Test Data

Synthetic accounts `acc-*`. Tables are truncated in setUp (disposable DB only).

## Entry Criteria

- `psycopg` importable; `DATABASE_URL` set to a disposable database.

## Exit Criteria

- All CRITICAL/HIGH test cases executed in this run with PASS.
- No OPEN CRITICAL/HIGH defect candidate.

## Execution Order

Readiness checks → existing suite → atomicity test.

## Evidence Requirements

Readiness check logs and unittest logs in `evidence/`.

## Untestable Risks

RISK-001 and RISK-002 are untestable in this run unless the environment becomes available.

## Constraints

No database is available. Provisioning one requires authorization (shared environments) or local tooling that is not present.
