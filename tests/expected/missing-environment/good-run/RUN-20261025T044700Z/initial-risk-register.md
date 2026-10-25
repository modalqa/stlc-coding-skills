# Initial Risk Register — RUN-20261025T044700Z

## Preliminary Risks

| Risk ID | Requirement IDs | What can go wrong | Area | Initial level | Why |
|---|---|---|---|---|---|
| RISK-001 | REQ-003 | Partial write leaves balance out of sync with entries | data | CRITICAL | Money data integrity |
| RISK-002 | REQ-002 | Balance computed incorrectly | data | HIGH | Financial correctness |
| RISK-003 | REQ-001 | Zero/invalid amounts persisted | functional | MEDIUM | Data quality |
| RISK-004 | REQ-004 | Entries modified after creation | data | MEDIUM | Audit trail |

## Uncertainty

The environment is unavailable, so likelihood cannot be reduced through execution.
