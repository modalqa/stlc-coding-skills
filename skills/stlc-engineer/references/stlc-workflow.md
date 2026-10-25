# STLC Workflow

The six phases below are this skill's operational workflow. They map onto
the test process concepts of the ISO/IEC/IEEE 29119 series (see the standards
registry). They are not a claim that the standard mandates six linear phases.
Iterate whenever requirements change, defects are found, or new evidence
changes the risk picture. Record each iteration in `run-manifest.json` →
`activities`.

## Run lifecycle

```
discover → P1 → gate A → P2 → gate B → P3 → gate C → P4 → gate D → P5 → gate E → P6 → gate F
              ↑______________________ iterate on new evidence ______________________|
```

At every gate:

1. Update `run-manifest.json`: set the phase `status`, the `gate_status`, `notes` (required for `BLOCKED` and `PASSED_WITH_LIMITATIONS`), and `current_phase`.
2. Run `scripts/validate_artifacts.py <run_dir> --phase <n>`.
3. Fix every ERROR. Record WARN items as limitations or resolve them.

A gate is `BLOCKED` when its condition cannot be met. Continue with any later
work that does not depend on it, and note the dependency. A blocked gate
forces the closure status to `INCOMPLETE` or `BLOCKED`.

## Phase 1 — Requirement and context analysis

Input: request, issue, acceptance criteria, source code, architecture, API contract.

1. Discover the repository (see SKILL.md §4).
2. Extract requirement candidates. Mark each `stated` or `inferred`.
3. Identify ambiguity, conflicts, and testability gaps.
4. Assign stable IDs and create the traceability matrix (`test_case_id` = `GAP` for now, `execution_status` = `PENDING`).
5. Record preliminary risks.
6. Record assumptions.

**Gate A**: the context is sufficient to plan, or its limits are explicitly stated.

## Phase 2 — Test planning and risk assessment

1. Set the scope and exclusions.
2. Choose the test levels and types.
3. Score the risks (`risk-register.csv`) and order them by priority.
4. Choose the environments and tools. Reuse what exists.
5. Define entry and exit criteria (start from the policy defaults).
6. Define the execution order and evidence requirements.

**Gate B**: the scope, the main risks, and the exit criteria are defined.

## Phase 3 — Test analysis and design

1. Derive test conditions (`TCOND-`) from requirements and risks.
2. Select techniques with a recorded reason.
3. Design positive, negative, boundary, and state-dependent cases.
4. Add security and authorization cases where the change touches them.
5. Plan the test data.
6. Link every case to requirement and risk IDs, and update the matrix.

**Gate C**: every CRITICAL/HIGH requirement traces to at least one test case, or to a GAP with a justification.

## Phase 4 — Test implementation

1. Detect the framework and conventions: naming, folder layout, fixtures, assertion style.
2. Implement the tests and fixtures. Follow `automation-guidelines.md`.
3. Validate syntax and dependencies with a collection-only or dry-run command where available.
4. Run a safe smoke check.
5. Integrate with CI only where authorized.

**Gate D**: the tests are ready to run, or the blockers are documented per test case.

## Phase 5 — Execution and monitoring

1. Check environment readiness (services, env var presence, ports).
2. Execute the tests in priority order and capture raw logs into `evidence/`.
3. Record the results in `execution-results.json`.
4. Classify the failures.
5. Fix test defects where justified, then rerun.
6. Run the regression set chosen by impact analysis.

**Gate E**: every result is backed by a recorded command and evidence, or carries a non-pass status with a reason.

## Phase 6 — Evaluation and closure

1. Compare the results with the exit criteria.
2. Evaluate requirement and risk coverage.
3. Check that traceability is complete.
4. Summarise the defect candidates.
5. Decide whether more testing is needed.
6. Write the QA recommendation.

**Gate F**: the closure report is complete, or the closure is marked BLOCKED or INCOMPLETE.

## Regression analysis (FR-09)

When testing a change:

1. List the changed files (`git diff --name-only <base>...HEAD` plus uncommitted changes).
2. Trace direct dependants (imports and call sites) and indirect ones where traceable.
3. Flag contract-sensitive changes: public API signatures, schemas and migrations, auth and permission code, serialization, configuration, integration clients.
4. Select the impacted existing tests, plus new tests for the changed behaviour. Run the CRITICAL/HIGH ones first.
5. List the areas you could not trace as "not verified" in the execution report.
