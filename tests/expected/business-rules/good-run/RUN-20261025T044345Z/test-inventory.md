# Test Inventory — RUN-20261025T044345Z

## Test Inventory

| Test case | Automated test (file::name) | Status | Notes |
|---|---|---|---|
| TC-001 | tests/test_pricing_boundaries.py::test_tc001_just_below_100_has_no_discount | IMPLEMENTED | |
| TC-002 | tests/test_pricing_boundaries.py::test_tc002_exactly_100_gets_five_percent | IMPLEMENTED | |
| TC-003 | tests/test_pricing_boundaries.py::test_tc003_upper_edge_of_five_percent_tier | IMPLEMENTED | |
| TC-004 | tests/test_pricing_boundaries.py::test_tc004_exactly_500_gets_ten_percent | IMPLEMENTED | |
| TC-005 | tests/test_pricing_boundaries.py::test_tc005_upper_edge_of_ten_percent_tier | IMPLEMENTED | |
| TC-006 | tests/test_pricing_boundaries.py::test_tc006_exactly_1000_gets_fifteen_percent | IMPLEMENTED | |
| TC-007 | tests/test_pricing_boundaries.py::test_tc007_loyalty_bonus_and_cap | IMPLEMENTED | |
| TC-008 | tests/test_pricing_boundaries.py::test_tc008_negative_rejected_zero_allowed | IMPLEMENTED | |
| TC-009 | tests/test_pricing_boundaries.py::test_tc009_rounds_half_up_to_cents | IMPLEMENTED | |
| TC-010 | tests/test_pricing.py (4 tests) | EXISTING | Pre-existing equivalence-partition tests |

## Files Changed

- `tests/test_pricing_boundaries.py` (new). No existing file was modified.

## Execution Instructions

```bash
python3 -m unittest -v tests.test_pricing tests.test_pricing_boundaries
```

## Smoke Check

`python3 -m unittest discover -s tests -t . -p 'test_*.py' --locals -k NONEXISTENT_COLLECT_ONLY` → exit 5 ("NO TESTS RAN": discovery imported every test module without import errors; exit 5 is expected because the filter matches nothing). Evidence: `evidence/01-collect.log`.

## CI Integration

Not added: no CI configuration exists in the fixture and no authorization was given.
