# Architecture

```
                 ┌───────────────────────── skills/stlc-engineer/ (portable core) ──────────────────────────┐
 user request →  │ SKILL.md ──loads per phase──> references/*.md     templates/*      schemas/*.json        │
                 │     │                                                                                      │
                 │     └─ policy: references/autonomy-policy.md + project stlc-policy.yaml (restrict-only)    │
                 │                                                                                            │
                 │ scripts/validate_artifacts.py  (validation layer — deterministic, stdlib)                  │
                 └────────────────────────────────────────────────────────────────────────────────────────────┘
                        ▲ packaged unchanged by
 adapters/<platform>/adapter.json + README  ──  scripts/package_skill.py (install / verify / build)

 tests/fixtures + tests/scenarios + tests/expected ── scripts/run_evaluations.py   (evaluation layer)
 scripts/validate_repository.py + scripts/run_checks.py                             (repo quality & security gate)
```

## Components (PRD §9.1)

| Component | Location | Responsibility |
|---|---|---|
| A. Core skill | `skills/stlc-engineer/SKILL.md` | Trigger, rules, phases, gates, conventions. Kept short (under 500 lines). |
| B. Knowledge references | `skills/stlc-engineer/references/` | Per-phase detail, loaded on demand (NFR-06). |
| C. Policy layer | `references/autonomy-policy.md`, `templates/stlc-policy.yaml` | Allowed, authorized, and stop actions. The project file can only restrict, unless a named human authorizes an expansion. |
| D. Adapter layer | `adapters/*` | Install paths, extra frontmatter, platform notes. Never changes the methodology. |
| E. Validation layer | `scripts/validate_artifacts.py` | Structure, IDs, traceability, status/evidence consistency, recommendation rules, secret and compliance-claim scan. |
| F. Evaluation layer | `tests/`, `scripts/run_evaluations.py` | Fixtures with seeded defects, expected outcomes, metrics. |

## Data flow (PRD §9.2)

Repository context → requirements analysis → risk assessment → test planning → test design → implementation → execution → evidence validation → closure.
Every step writes artifacts into `stlc-artifacts/<run_id>/`. Each phase reads the previous artifacts, and the validator runs at every gate.

## Anti-fabrication design

The validator turns the most dangerous agent failure, claiming results it never observed, into deterministic errors:

| Rule | Error code |
|---|---|
| PASS/FAIL needs `result_origin: this_run`, a command present in `commands[]`, an integer exit code, timestamps, and existing evidence | `unverified_verdict`, `evidence_missing` |
| Results must start after the run was created | `stale_result` |
| Matrix status must equal the execution record | `status_mismatch` |
| Closure counts must equal the execution record | `count_mismatch` |
| READY is impossible with failing or unexecuted high-priority tests, open defects, or high-priority gaps; anything but NOT_READY is impossible with zero passes | `recommendation_unsupported` |
| A product defect FAIL must have a DEF entry | `defect_not_logged` |
| Secrets in any artifact | `secret_detected` |
| ISO compliance or certification claims | `compliance_claim` |

These checks are necessary but not sufficient. An agent can still write a wrong test that passes. That is why the evaluation fixtures contain seeded defects whose detection is measured.

## Design decisions

- **Standard library only** for every script, so the skill installs anywhere without supply-chain or license exposure.
- **Markdown + CSV + JSON** artifacts: readable by humans, diffable, and parseable by the validator (NFR-01, NFR-08).
- **`result_origin` field** (an extension to the PRD §12.2 minimum) implements FR-07's "verify whether results come from the latest execution".
- **`agents/openai.yaml` is omitted.** PRD §10 keeps it only if a targeted ecosystem needs it, and none of the four first adapters does. Add it under `adapters/` together with a new adapter if needed.
