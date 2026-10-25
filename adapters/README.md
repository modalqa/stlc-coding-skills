# Adapters

Adapters package the **unchanged** core skill (`skills/stlc-engineer/`) for a specific coding agent. An adapter can only:

- choose where the skill is installed (project and user directories);
- add platform-specific frontmatter (`extra_frontmatter` in `adapter.json`);
- document invocation, capability differences, and known limitations.

An adapter must not redefine the methodology, change status meanings, or relax approval or evidence requirements (PRD §14.1). `tests/evaluations/test_adapters.py` checks that every packaged adapter carries a byte-identical copy of the core skill except for the frontmatter.

## Status values

| Status | Meaning |
|---|---|
| `experimental` | Static compatibility checks pass. The behavioral acceptance suite has **not** yet been run on a real installation of the platform. |
| `supported` | The behavioral suite (`scripts/run_evaluations.py`, all scenarios) passed on the versions listed in `tested_versions`, with the reports linked in `evaluation_reports`. `scripts/validate_repository.py` rejects `supported` without both. |

**All four adapters are currently `experimental`.** None has been run through the behavioral suite yet.

## Adding an adapter

1. Create `adapters/<name>/adapter.json` (copy an existing one) and `README.md` with the sections required by FR-12 (the validator checks for them).
2. `python3 scripts/package_skill.py install --adapter <name> --project <fixture-workdir>`
3. Run every scenario in `tests/scenarios/` with the agent and record the reports (see `docs/compatibility.md`).
4. Only then set `status: supported`.
