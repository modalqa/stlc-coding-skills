# Release Evaluation and Closure (Phase 6)

## Steps

1. **Exit criteria**: evaluate each criterion from `test-plan.md` as met, not met, or partly met, citing the evidence.
2. **Coverage**: requirement coverage (per requirement: test cases and statuses) and risk coverage (per risk: residual status).
3. **Traceability**: the validator must pass. Unresolved GAPs are listed as limitations.
4. **Defects**: summarise the candidates by severity and status.
5. **More testing?** State what further testing would change the recommendation.
6. **Recommendation**.

## Recommendation rules

| Recommendation | Allowed when |
|---|---|
| READY | All CRITICAL/HIGH test cases PASS in this run; no open product defect candidates; no high-priority requirement GAP; the exit criteria are met. |
| READY_WITH_RISKS | At least one test passed and the remaining issues are documented, bounded, and non-critical, with residual risks needing an owner decision. |
| NOT_READY | Any CRITICAL/HIGH failure, an open CRITICAL/HIGH defect candidate, critical untested risk, or no executed PASS at all. |

The closure status is separate from the recommendation:

- `COMPLETE`: every phase gate was evaluated, and the report is complete.
- `INCOMPLETE`: the work stopped early, or some gates were not evaluated.
- `BLOCKED`: a stop condition prevented meaningful evaluation.

The closure report must contain a status-count table that matches
`execution-results.json` exactly (the validator checks it). It must also
state that the recommendation is advisory and **not a release approval**.

## Residual risk register

List every risk that is not `MITIGATED`. For each one, give why it is
residual, the evidence, the suggested next step, and whether an owner
decision is needed. `ACCEPTED` requires a named human. The agent never
accepts risk on anyone's behalf.

## Final message to the user

Include the run directory, the counts, the recommendation and closure
status, the top three residual risks, and what could not be verified. Do
not use superlatives or vague assurances such as "fully tested" or
"production ready".
