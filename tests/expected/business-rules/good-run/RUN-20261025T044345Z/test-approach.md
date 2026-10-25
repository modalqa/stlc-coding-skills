# Test Approach — RUN-20261025T044345Z

## Test Levels and Types

| Level | Applies? | Why | Types (functional, security, performance, compatibility, ...) |
|---|---|---|---|
| Unit / component | yes | Pure functions in one module | functional, boundary, negative |
| Integration / contract | no | No integrations in scope | — |
| System / end-to-end | no | No UI/API surface | — |
| Acceptance | yes | ACs map 1:1 to unit-level checks | functional |

## Quality Characteristics in Scope

Functional suitability (functional correctness) per ISO/IEC 25010:2023 (edition needs verification). Other characteristics are not relevant to this pure calculation.

## Techniques

| Technique | Applied to | Reason |
|---|---|---|
| Boundary value analysis | REQ-001..REQ-004 | Ordered monetary ranges with inclusive/exclusive edges |
| Equivalence partitioning | REQ-001..REQ-004 (existing suite) | One representative per tier |
| Decision table (loyalty × tier) | REQ-005 | Combination of tier and membership with a cap |
| Error guessing | REQ-006, REQ-007 | Negative/zero amounts and half-cent rounding are common faults |

## Manual vs Automation

All cases automated with `unittest`; no manual testing needed.

## Tools

Existing `unittest` (Python standard library, PSF license). No new dependencies.
