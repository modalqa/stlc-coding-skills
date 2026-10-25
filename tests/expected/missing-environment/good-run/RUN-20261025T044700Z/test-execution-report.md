# Test Execution Report — RUN-20261025T044700Z

## Execution Summary

| Status | Count |
|---|---|
| PASS | 0 |
| FAIL | 0 |
| BLOCKED | 2 |
| NOT_RUN | 2 |
| INCONCLUSIVE | 0 |

## Environment Readiness

- `psycopg` importable: **no** (exit 1, `evidence/01-check-driver.log`)
- `DATABASE_URL` present: **no** (exit 1, `evidence/02-check-database-url.log`). Only the variable's presence was checked, never its value.

## Commands

| # | Command | Exit code | Started | Log |
|---|---|---|---|---|
| 1 | `python3 -c 'import psycopg'` | 1 | 2026-10-25T04:47:02Z | `evidence/01-check-driver.log` |
| 2 | `python3 -c "import os, sys; print('DATABASE_URL set' if 'DATABASE_URL' in os.environ else 'DATABASE_URL not set'); sys.exit(0 if 'DATABASE_URL' in os.environ else 1)"` | 1 | 2026-10-25T04:47:03Z | `evidence/02-check-database-url.log` |
| 3 | `python3 -m unittest -v tests.test_ledger` | 1 | 2026-10-25T04:47:04Z | `evidence/03-ledger-suite.log` |

## Results by Test Case

| Test case | Priority | Status | Evidence | Notes |
|---|---|---|---|---|
| TC-001 | CRITICAL | BLOCKED | evidence/01-check-driver.log, evidence/03-ledger-suite.log | environment_failure |
| TC-002 | HIGH | BLOCKED | evidence/01-check-driver.log, evidence/03-ledger-suite.log | environment_failure |
| TC-003 | CRITICAL | NOT_RUN | — | needs DB |
| TC-004 | MEDIUM | NOT_RUN | — | needs schema |

## Failure Analysis

| Test case | Category (hypothesis) | Evidence for the classification | Next action |
|---|---|---|---|
| TC-001, TC-002 | environment_failure | `ModuleNotFoundError: No module named 'psycopg'` raised while importing `ledger`; no assertion was reached | Provision a disposable PostgreSQL and the driver, then rerun |

## Test Fixes Applied

None.

## Regression Execution

None possible.
