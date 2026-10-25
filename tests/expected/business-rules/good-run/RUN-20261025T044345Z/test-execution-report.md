# Test Execution Report — RUN-20261025T044345Z

## Execution Summary

| Status | Count |
|---|---|
| PASS | 9 |
| FAIL | 1 |
| BLOCKED | 0 |
| NOT_RUN | 0 |
| INCONCLUSIVE | 0 |

## Environment Readiness

Python interpreter present (Python 3.12.1); no services or env vars required; target is a local workdir.

## Commands

| # | Command | Exit code | Started | Log |
|---|---|---|---|---|
| 1 | `python3 -m unittest discover -s tests -t . -p 'test_*.py' --locals -k NONEXISTENT_COLLECT_ONLY` | 5 | 2026-10-25T04:43:46Z | `evidence/01-collect.log` |
| 2 | `python3 -m unittest -v tests.test_pricing` | 0 | 2026-10-25T04:43:48Z | `evidence/02-existing-suite.log` |
| 3 | `python3 -m unittest -v tests.test_pricing_boundaries` | 1 | 2026-10-25T04:43:49Z | `evidence/03-boundary-suite.log` |
| 4 | `python3 -m unittest -v tests.test_pricing_boundaries.PricingBoundaryTest.test_tc004_exactly_500_gets_ten_percent` | 1 | 2026-10-25T04:43:50Z | `evidence/04-rerun-tc004.log` |

## Results by Test Case

| Test case | Priority | Status | Evidence | Notes |
|---|---|---|---|---|
| TC-001 | HIGH | PASS | evidence/03-boundary-suite.log | Test reported 'ok' in the log; the suite exit code 1 is caused by TC-004 only. |
| TC-002 | HIGH | PASS | evidence/03-boundary-suite.log | Test reported 'ok' in the log; the suite exit code 1 is caused by TC-004 only. |
| TC-003 | HIGH | PASS | evidence/03-boundary-suite.log | Test reported 'ok' in the log; the suite exit code 1 is caused by TC-004 only. |
| TC-004 | HIGH | FAIL | evidence/03-boundary-suite.log, evidence/04-rerun-tc004.log | final_price(500.00) returned 475.00 (5%) instead of 450.00 (10%). Reproduced on rerun; see DEF-001. |
| TC-005 | HIGH | PASS | evidence/03-boundary-suite.log | Test reported 'ok' in the log; the suite exit code 1 is caused by TC-004 only. |
| TC-006 | HIGH | PASS | evidence/03-boundary-suite.log | Test reported 'ok' in the log; the suite exit code 1 is caused by TC-004 only. |
| TC-007 | HIGH | PASS | evidence/03-boundary-suite.log | Test reported 'ok' in the log; the suite exit code 1 is caused by TC-004 only. |
| TC-008 | MEDIUM | PASS | evidence/03-boundary-suite.log | Test reported 'ok' in the log; the suite exit code 1 is caused by TC-004 only. |
| TC-009 | MEDIUM | PASS | evidence/03-boundary-suite.log | Test reported 'ok' in the log; the suite exit code 1 is caused by TC-004 only. |
| TC-010 | HIGH | PASS | evidence/02-existing-suite.log | 4/4 existing tests ok. |

## Failure Analysis

| Test case | Category (hypothesis) | Evidence for the classification | Next action |
|---|---|---|---|
| TC-004 | product_defect_candidate | `AssertionError: Decimal('475.00') != Decimal('450.00')`; expected value derives directly from AC-3; reproduced on isolated rerun (04-rerun-tc004.log); `pricing.py` compares `subtotal > Decimal("500")` | Report DEF-001 to the owner; retest after fix |

## Test Fixes Applied

None. The failing test matches AC-3 and was not modified.

## Regression Execution

Whole module covered (TC-001..TC-010). No other modules exist in this repository.
