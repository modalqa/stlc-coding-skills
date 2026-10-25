# Contributing

Thank you for helping improve stlc-engineer.

## Ground rules

1. **The core methodology lives only in `skills/stlc-engineer/`.** Adapters may change installation paths and frontmatter, nothing else.
2. **No fabricated standards content.** Do not add ISO clause numbers, quotations, or edition claims without a verifiable official source. Update `standards-registry.json` with `verified_on` and `verified_by`.
3. **No new runtime dependencies** for the skill scripts (standard library only). Dev tooling must have a commercially friendly license (MIT, BSD, Apache-2.0, PSF, ISC). Record it in `docs/third-party-licenses.md` and pin it in `requirements-dev.txt`.
4. **Keep `SKILL.md` under 500 lines.** Put detail in `references/`.
5. **Behaviour changes need evaluation evidence.** If you change instructions, run the affected scenarios with at least one agent and attach the `run_evaluations.py` reports to the PR.

## Development

```bash
python3 -m pip install -r requirements-dev.txt   # bandit, pip-audit
# install gitleaks: https://github.com/gitleaks/gitleaks (MIT)
python3 scripts/run_checks.py                    # full gate (same as CI)
```

Python 3.11 or newer is required (3.10 is end-of-life). CI should cover the oldest and newest supported versions.

## Versioning

Bump `VERSION`, `SKILL.md` → `metadata.version`, and `validate_artifacts.py` → `SKILL_VERSION` together, and add a CHANGELOG entry. `validate_repository.py` enforces this.

## Pull requests

- One logical change per PR, with tests.
- `python3 scripts/run_checks.py` passes.
- Explain the effect on the evaluation metrics (docs/compatibility.md) if behaviour changed.

By contributing you agree that your contributions are licensed under the Apache License 2.0.
