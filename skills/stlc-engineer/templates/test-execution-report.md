# Test Execution Report — {{run_id}}

## Execution Summary

| Status | Count |
|---|---|
| PASS | {{n}} |
| FAIL | {{n}} |
| BLOCKED | {{n}} |
| NOT_RUN | {{n}} |
| INCONCLUSIVE | {{n}} |

## Environment Readiness

{{Checks performed before execution and their results.}}

## Commands

| # | Command | Exit code | Started | Log |
|---|---|---|---|---|
| 1 | `{{command}}` | {{code}} | {{timestamp}} | `{{evidence/...}}` |

## Results by Test Case

| Test case | Priority | Status | Evidence | Notes |
|---|---|---|---|---|
| {{TC-001}} | {{priority}} | {{status}} | {{refs}} | {{notes}} |

## Failure Analysis

| Test case | Category (hypothesis) | Evidence for the classification | Next action |
|---|---|---|---|
| {{TC-ID}} | {{failure_category}} | {{log line / assertion / rerun result}} | {{action}} |

## Test Fixes Applied

{{Test implementation defects fixed, with justification and rerun result. "None" if none.}}

## Regression Execution

{{Impacted areas, regression tests selected by risk, and their results. Areas not verified.}}
