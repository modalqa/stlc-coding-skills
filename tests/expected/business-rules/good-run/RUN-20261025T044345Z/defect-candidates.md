# Defect Candidates — RUN-20261025T044345Z

## Defect Candidates

### DEF-001

- **title:** Subtotal of exactly 500.00 receives 5% instead of 10% discount
- **related_test_case_ids:** TC-004
- **failure_category:** product_defect_candidate
- **severity:** HIGH
- **status:** OPEN
- **evidence_refs:** evidence/03-boundary-suite.log; evidence/04-rerun-tc004.log
- **reproduction:** `python3 -m unittest -v tests.test_pricing_boundaries.PricingBoundaryTest.test_tc004_exactly_500_gets_ten_percent`
- **expected:** 450.00 (REQ-003 / AC-3: 500.00 is in the 10% tier)
- **actual:** 475.00
- **hypothesis:** `base_discount` uses `subtotal > Decimal("500")`; AC-3 requires `>=`. Every order of exactly 500.00 is over-charged by 25.00.
