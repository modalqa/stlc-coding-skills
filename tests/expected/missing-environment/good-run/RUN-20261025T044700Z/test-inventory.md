# Test Inventory — RUN-20261025T044700Z

## Test Inventory

| Test case | Automated test (file::name) | Status | Notes |
|---|---|---|---|
| TC-001 | tests/test_ledger.py::test_balance_is_sum_of_entries | EXISTING | |
| TC-002 | tests/test_ledger.py::test_zero_amount_rejected | EXISTING | |
| TC-003 | — | BLOCKED | Not implemented: cannot design the fault injection without the schema or verify it without a DB |
| TC-004 | — | MANUAL | Needs the schema, which is absent from the repo |

## Files Changed

None.

## Execution Instructions

```bash
export DATABASE_URL=postgresql://<user>@localhost:5432/<disposable_db>
python3 -m pip install psycopg
python3 -m unittest -v tests.test_ledger
```

## Smoke Check

Not possible: `import psycopg` fails (evidence/01-check-driver.log).

## CI Integration

Not added (no CI, no authorization).
