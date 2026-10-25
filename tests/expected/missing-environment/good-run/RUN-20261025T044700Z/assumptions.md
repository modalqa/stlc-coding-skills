# Assumptions — RUN-20261025T044700Z

## Assumptions

| ID | Assumption | Basis | Affects | Risk if wrong | Status |
|---|---|---|---|---|---|
| ASM-001 | Timestamp is a DB column default | `record` inserts no timestamp | REQ-001 | Missing timestamps | OPEN |
| ASM-002 | Immutability is enforced in the schema, not in code | No update/delete methods in code | REQ-004 | Entries editable via SQL | OPEN |

## Limitations

No database schema or migrations exist in the repository; no PostgreSQL instance available.
