# Execution and Evidence (Phase 5)

## Readiness

Before running, check and record: runtime and dependency installation;
required services are reachable (locally); required env var *names* are
present (never print values); and the target is not production. If a check
fails, the affected tests are `BLOCKED` (with `environment_failure` or
`dependency_failure`) or `NOT_RUN`, not `FAIL`.

## Capturing evidence

For each command:

1. Record `started_at` (UTC, ISO-8601).
2. Run it with output captured to `evidence/<nn>-<slug>.log`, for example
   `cmd 2>&1 | tee evidence/01-unit.log` (with `set -o pipefail` or `${PIPESTATUS[0]}` so the exit code is the command's).
3. Record `finished_at` and the **real** exit code.
4. Save machine reports (JUnit XML, coverage, screenshots, HAR) under `evidence/`.
5. Redact secrets from evidence before saving it. Replace values with `<redacted>`.

Evidence files are raw output. Never edit them except to redact. Summaries go in the reports.

## Result rules

| Status | Use when | Must have |
|---|---|---|
| PASS | Executed in this run and the assertion held | `result_origin: this_run`, a command present in `commands[]`, integer exit code, timestamps, evidence_refs, `failure_category: null` |
| FAIL | Executed in this run and the expected behaviour was not met | Same as PASS, plus a `failure_category` |
| BLOCKED | Could not reach a verdict because something outside the test prevented it | `failure_category` and a reason in `notes` |
| NOT_RUN | Not executed (out of time, tooling unavailable, deliberately deferred) | `result_origin: not_executed` or `previous_run`, and a reason |
| INCONCLUSIVE | Ran, but the outcome cannot be judged (no oracle, contradictory evidence, flaky with no stable result) | `failure_category` and a reason |

A result found in an older report, a CI page, or a cached artifact is
`result_origin: previous_run`. It can inform analysis, but its status is
`NOT_RUN` or `INCONCLUSIVE` for this run.

## Failure classification (FR-08)

| Category | Typical evidence |
|---|---|
| product_defect_candidate | An assertion about specified behaviour fails, the cause is reproducible, and the test matches the requirement |
| test_implementation_defect | The test contradicts the requirement, has a broken setup, or uses a wrong locator or fixture |
| environment_failure | Connection refused, a missing binary, port in use, out of disk, permissions |
| test_data_problem | Missing or invalid seed data, a uniqueness collision, stale fixtures |
| dependency_failure | An external or 3rd-party service error, timeout, or contract change |
| flaky | The same code and data produce both pass and fail across reruns (record every run) |
| inconclusive | Not enough evidence to choose any of the above |

The classification is a hypothesis. In the execution report, give the
evidence line that supports it. Never reclassify a failure to pass a gate.

## Rerun discipline

- Rerun a failure at most `max_reruns_per_failure` times (default 2) to diagnose it, and log every attempt as its own command.
- After fixing a test defect, rerun the affected test and any test that shares its fixtures.
- The final status is based on the evidence, not on the last attempt alone. Pass-then-fail or fail-then-pass makes the result `flaky` and `INCONCLUSIVE` unless it is explained.

## Monitoring

Track progress in `run-manifest.json` → `activities` with timestamps. Long
runs record a progress entry per command.
