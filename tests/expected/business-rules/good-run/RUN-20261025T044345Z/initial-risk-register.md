# Initial Risk Register — RUN-20261025T044345Z

## Preliminary Risks

| Risk ID | Requirement IDs | What can go wrong | Area | Initial level | Why |
|---|---|---|---|---|---|
| RISK-001 | REQ-001;REQ-002;REQ-003;REQ-004 | Subtotal on a tier edge gets the wrong tier | functional | HIGH | Off-by-one comparisons are a classic boundary fault; direct revenue impact |
| RISK-002 | REQ-005 | Loyalty discount exceeds 20% cap | functional | HIGH | Revenue loss on the largest orders |
| RISK-003 | REQ-006 | Negative or zero subtotals mishandled | functional | MEDIUM | Bad orders/credits |
| RISK-004 | REQ-007 | Rounding error at half-cent | functional | MEDIUM | Reconciliation differences |

## Uncertainty

No production defect history available; likelihood estimated from code inspection.
