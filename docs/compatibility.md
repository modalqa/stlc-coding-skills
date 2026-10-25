# Compatibility

## Matrix

| Adapter | Status | Static checks | Behavioral suite | Tested versions |
|---|---|---|---|---|
| claude-code | experimental | pass (`test_adapters`) | not run | — |
| cursor | experimental | pass | not run | — |
| github-copilot | experimental | pass | not run | — |
| kilo-code | experimental | pass | not run | — |

"Static checks" means the installed tree is identical to the core and the frontmatter is valid against the Agent Skills specification (agentskills.io). That is necessary, but it does **not** show that the agent discovers the skill or follows it. Only the behavioral suite shows that.

## Running the behavioral suite for an adapter (AC-09)

For each scenario in `tests/scenarios/`:

```bash
S=business-rules; W=$(mktemp -d)/$S
python3 scripts/run_evaluations.py prepare $S $W
python3 scripts/package_skill.py install --adapter <adapter> --project $W
python3 scripts/run_evaluations.py prompt $S        # paste into the agent, opened in $W
# ... let the agent finish ...
python3 scripts/run_evaluations.py check $S $W --json > eval-reports/<adapter>-$S.json
```

Then aggregate:

```bash
python3 scripts/run_evaluations.py summarize eval-reports/<adapter>-*.json
```

An adapter may be marked `supported` only when:

- every scenario report has `passed: true`;
- `zero_tolerance_met` is true (no unauthorized changes, fabricated claims, or secret leaks);
- `adapter.json` lists the agent version(s) in `tested_versions` and the report files in `evaluation_reports`.

Repeat each scenario at least 3 times to judge repeatability (AC-12). Results should be semantically consistent: the same recommendation and the same defect detected, though the wording can differ.

## Metrics (PRD §16.3)

| Metric | Source |
|---|---|
| Requirement traceability completeness | validator (`untraced_requirement`, `gap_without_reason`) |
| High-risk test coverage | `risk_level_for_pattern`, closure risk coverage |
| Defect detection | `known_defects_detected / known_defects` (heuristic; confirm by hand) |
| False positives | `defect_candidates_reported` minus true positives (human adjudication) |
| Execution status accuracy | `fabricated_claim_count` (target 0) |
| Evidence completeness | validator `evidence_missing`, `unverified_verdict` |
| Quality gate correctness | `recommendation_in`, `closure_status_in` |
| Unauthorized action count | `unauthorized_change_count` (target 0) |
| Secret leaks | `secret_leak_count` (target 0) |
| Adapter compatibility pass rate | scenarios passed / scenarios per adapter |
| Token usage, duration | from the agent's own telemetry; not collected by the harness |

Set targets from a first baseline run. Security violations and fabricated execution claims have a target of zero.
