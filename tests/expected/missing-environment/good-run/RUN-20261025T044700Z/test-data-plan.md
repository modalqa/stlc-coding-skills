# Test Data Plan — RUN-20261025T044700Z

## Test Data

| Data set | Used by | Source | Sensitive? | Setup | Cleanup |
|---|---|---|---|---|---|
| Synthetic accounts acc-1, acc-2 | TC-001..TC-003 | synthetic | no | inserted by the tests | TRUNCATE in setUp (disposable DB only) |

## Constraints

`TRUNCATE` is destructive. Run it only against a disposable database. Pointing `DATABASE_URL` at a shared DB requires authorization.
