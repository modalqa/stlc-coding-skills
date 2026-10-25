# Requirements Analysis — RUN-20261025T044345Z

## Context Summary

- **Repository:** order pricing service (evaluation fixture `business-rules`)
- **Change under test:** whole repository (pricing rules)
- **Languages / frameworks:** Python 3, standard library only (`decimal`)
- **Test frameworks and commands:** `unittest`; `python3 -m unittest discover -s tests -t .` (README.md)
- **Architecture / module boundaries:** single module `pricing.py` (`base_discount`, `final_price`); tests in `tests/`
- **Working tree:** clean at start (commit 49d7356)
- **Required configuration:** none
- **Requirement sources:** `requirements.md` (stated acceptance criteria AC-1..AC-7)

## Requirements

| ID | Requirement | Type | Source | Priority | Acceptance criteria | Testable? |
|---|---|---|---|---|---|---|
| REQ-001 | Subtotal below 100.00 gets no discount | functional | stated: requirements.md AC-1 | HIGH | AC-1 | yes |
| REQ-002 | Subtotal 100.00–499.99 gets 5% | functional | stated: AC-2 | HIGH | AC-2 | yes |
| REQ-003 | Subtotal 500.00–999.99 gets 10% | functional | stated: AC-3 | HIGH | AC-3 | yes |
| REQ-004 | Subtotal ≥ 1000.00 gets 15% | functional | stated: AC-4 | HIGH | AC-4 | yes |
| REQ-005 | Loyalty +5 points, total capped at 20% | functional | stated: AC-5 | HIGH | AC-5 | yes |
| REQ-006 | Negative subtotal → ValueError; 0.00 valid | functional | stated: AC-6 | MEDIUM | AC-6 | yes |
| REQ-007 | Final price rounded half-up to 2 decimals | functional (functional correctness) | stated: AC-7 | MEDIUM | AC-7 | yes |

## Ambiguities and Testability Gaps

| # | Requirement | Issue | Impact | Clarification need | Working assumption |
|---|---|---|---|---|---|
| 1 | REQ-002..004 | Inputs with more than 2 decimals (e.g. 499.995) are not specified | Low: callers pass currency amounts | NON_BLOCKING | ASM-001 |
| 2 | REQ-007 | Rounding applies to the final price, not to the discount amount | Cent-level differences | NON_BLOCKING | ASM-002 |

## Conflicts

None found.

## Suspicious Content

None found.
