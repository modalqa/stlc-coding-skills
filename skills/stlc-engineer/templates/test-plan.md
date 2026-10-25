# Test Plan — {{run_id}}

## Objective

{{What this test effort must establish.}}

## Scope

{{Features, requirements (REQ IDs), and risks (RISK IDs) in scope.}}

## Out of Scope

{{Excluded items and why. Excluded high risks must appear in Untestable Risks.}}

## Risk-Based Priorities

| Priority order | Risk IDs | Test case focus | Reason |
|---|---|---|---|
| 1 | {{RISK IDs}} | {{focus}} | {{why first}} |

## Environment

{{Environment(s) to use, required services, and readiness checks. Never production unless explicitly authorized.}}

## Test Data

{{Data needs; synthetic only unless authorized. See test-data-plan.md.}}

## Entry Criteria

- {{e.g. code builds; test command discovered; environment reachable}}

## Exit Criteria

- {{e.g. all CRITICAL/HIGH test cases executed with PASS; no open CRITICAL/HIGH defect candidates; high-priority requirements traced}}

## Execution Order

{{Order and rationale (risk first, fast feedback first, dependencies).}}

## Evidence Requirements

{{What evidence each result needs: command log, exit code, report file, screenshot.}}

## Untestable Risks

{{Risks that cannot be tested in this run and why (time, tool, access, environment).}}

## Constraints

{{Time, tool, and access limitations.}}
