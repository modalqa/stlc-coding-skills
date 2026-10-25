# Traceability

## Chain

Requirement → Risk → Test Condition → Test Case → Execution Result → Defect Candidate → Closure Decision

## traceability-matrix.csv

One row per requirement-to-test-case link. A requirement with three test cases has three rows.

| Column | Values |
|---|---|
| requirement_id | `REQ-NNN` |
| requirement_priority | CRITICAL / HIGH / MEDIUM / LOW |
| risk_ids | `RISK-NNN;RISK-MMM`, or `GAP` / `N/A` |
| test_condition_id | `TCOND-NNN`, or `GAP` / `N/A` |
| test_case_id | `TC-NNN`, or `GAP` / `N/A` |
| execution_status | `PENDING` before Phase 5; after it, must equal the latest status in `execution-results.json` (`NOT_RUN` if the case has no record) |
| defect_ids | `DEF-NNN;...` or `N/A` |
| closure_decision | `PENDING` until Phase 6, then `COVERED`, `COVERED_WITH_DEFECT`, `NOT_COVERED`, `ACCEPTED_GAP`, or `DEFERRED` |
| notes | Required whenever any cell is `GAP` or `N/A` |

- `GAP` = a link should exist but does not yet (untested, unknown risk).
- `N/A` = a link does not apply. Not allowed for the test case of a CRITICAL/HIGH requirement.
- Never leave a cell empty, and never create an ID just to fill a cell.

## Validator cross-checks

- Every `REQ-` in `requirements-analysis.md` appears in the matrix.
- Every risk, test case, and defect ID in the matrix exists in its source artifact.
- The matrix status equals the recorded execution status (anti-fabrication check).
- Orphan test cases (not linked to any requirement) produce a warning.
