# Artifact Schemas

All artifacts live in `<artifact_root>/<run_id>/` (default `stlc-artifacts/RUN-YYYYMMDDTHHMMSSZ/`).
Machine-checkable rules are enforced by `scripts/validate_artifacts.py`. JSON
Schemas for the JSON artifacts are in [../schemas/](../schemas/).

## Files per phase

| Phase | File | Template |
|---|---|---|
| 1 | `run-manifest.json` | `templates/run-manifest.json` |
| 1 | `requirements-analysis.md` | `templates/requirements-analysis.md` |
| 1 | `assumptions.md` | `templates/assumptions.md` |
| 1 | `initial-risk-register.md` | `templates/initial-risk-register.md` |
| 1, 3, 5, 6 | `traceability-matrix.csv` | `templates/traceability-matrix.csv` |
| 2 | `test-approach.md`, `test-plan.md` | same name |
| 2 | `risk-register.csv` | `templates/risk-register.csv` |
| 3 | `test-cases.md`, `test-data-plan.md` | same name |
| 4 | `test-inventory.md` (+ test scripts in the repo) | `templates/test-inventory.md` |
| 5 | `execution-results.json`, `test-execution-report.md` | same name |
| 5 | `defect-candidates.md` | `templates/defect-report.md` |
| 5 | `evidence/` (raw logs, reports, screenshots) | — |
| 6 | `test-closure-report.md`, `residual-risk-register.md`, `release-readiness.md` | same name |

## Test case (12.1)

Markdown block headed `### TC-NNN`, with one `- **field:** value` line per field:
`test_case_id, requirement_ids, risk_ids, title, objective, preconditions, test_data, steps,
expected_result, test_level, test_type, design_technique, automation_status, priority`.

- `requirement_ids`: real `REQ-` IDs only (no GAP).
- `risk_ids`: `RISK-` IDs, or `GAP`/`N/A`.
- `automation_status`: AUTOMATED | TO_AUTOMATE | MANUAL | NOT_AUTOMATABLE
- `priority`: CRITICAL | HIGH | MEDIUM | LOW

## Execution result (12.2)

`execution-results.json` → `results[]`, one record per test case (the last record for a test case is its current status):

| Field | Type | Rule |
|---|---|---|
| run_id | string | equals the manifest `run_id` |
| test_case_id | string | defined in `test-cases.md` |
| status | enum | PASS, FAIL, BLOCKED, NOT_RUN, INCONCLUSIVE |
| result_origin | enum | this_run, previous_run, not_executed (an extension to the PRD minimum, for FR-07) |
| started_at / finished_at | ISO-8601 with timezone, or null | required for PASS/FAIL, and not earlier than the manifest `created_at` |
| command | string or null | for PASS/FAIL, must appear in `commands[]` |
| exit_code | int or null | int for PASS/FAIL |
| environment | string | short label |
| evidence_refs | string[] | paths relative to the run directory that exist inside it. Required for PASS/FAIL |
| failure_category | enum or null | null for PASS. Required for FAIL/BLOCKED/INCONCLUSIVE |
| notes | string | required for NOT_RUN/BLOCKED/INCONCLUSIVE |

`commands[]`: `command, started_at, finished_at, exit_code, log_ref`. One entry per actual invocation, including reruns.

Result status is separate from workflow status. Workflow status lives in
`run-manifest.json` → `phases[]` (`status`: NOT_STARTED, IN_PROGRESS,
COMPLETED, BLOCKED, SKIPPED; `gate_status`: PASSED, PASSED_WITH_LIMITATIONS,
BLOCKED, NOT_EVALUATED).

## Defect candidate

Block headed `### DEF-NNN` with fields `title, related_test_case_ids, failure_category, severity,
status, evidence_refs, reproduction, expected, actual, hypothesis`.
`status`: OPEN | CONFIRMED | REJECTED | FIXED_PENDING_RETEST | CLOSED. A `FAIL`
classified `product_defect_candidate` must have a DEF entry.

## Closure report

Must contain `**QA Recommendation:** READY|READY_WITH_RISKS|NOT_READY`,
`**Closure Status:** COMPLETE|INCOMPLETE|BLOCKED`, a status-count table
(`| PASS | n |` …) that matches the execution results, the words
"not a release approval", and the sections listed in
`templates/test-closure-report.md`.
