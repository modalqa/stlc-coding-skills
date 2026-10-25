# Assumptions — RUN-20261025T044345Z

## Assumptions

| ID | Assumption | Basis | Affects | Risk if wrong | Status |
|---|---|---|---|---|---|
| ASM-001 | Subtotals are currency amounts with at most 2 decimals | Domain convention; AC text uses 2 decimals | REQ-002;REQ-003;REQ-004 | Untested sub-cent boundaries | OPEN |
| ASM-002 | Rounding is applied once, to the final price | AC-7 wording | REQ-007 | Cent mismatch with accounting | OPEN |

## Limitations

Single-module fixture; no integration with order or accounting systems is in scope.
