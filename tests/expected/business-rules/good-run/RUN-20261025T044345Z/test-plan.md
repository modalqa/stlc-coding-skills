# Test Plan — RUN-20261025T044345Z

## Objective

Establish whether `final_price` satisfies AC-1..AC-7, with emphasis on tier boundaries.

## Scope

REQ-001..REQ-007; RISK-001..RISK-004.

## Out of Scope

Performance, concurrency, and currency handling beyond 2 decimals (ASM-001).

## Risk-Based Priorities

| Priority order | Risk IDs | Test case focus | Reason |
|---|---|---|---|
| 1 | RISK-001 | Tier edges 99.99/100.00/499.99/500.00/999.99/1000.00 | HIGH, most likely fault |
| 2 | RISK-002 | Loyalty bonus and cap | HIGH, revenue impact |
| 3 | RISK-003, RISK-004 | Negative/zero and rounding | MEDIUM |

## Environment

Local Python 3 interpreter; no services.

## Test Data

Synthetic Decimal amounts only (see test-data-plan.md).

## Entry Criteria

- Module imports and existing tests are discoverable.

## Exit Criteria

- All HIGH test cases executed in this run with PASS.
- No OPEN product defect candidate of severity CRITICAL or HIGH.
- Every HIGH requirement traced to at least one executed test case.

## Execution Order

Smoke/collection → existing suite → new boundary suite → rerun failures.

## Evidence Requirements

Verbose unittest log per command with exit code, stored in `evidence/`.

## Untestable Risks

None for this scope.

## Constraints

None.
