# Changelog

All notable changes are documented here. The project follows [Semantic Versioning](https://semver.org/):
MAJOR for breaking changes to the skill contract, schemas, or behaviour; MINOR for backward-compatible capabilities or adapters; PATCH for corrections and documentation.

## [0.1.0] - 2026-10-25

First implementation of PRD STLC-AGENT-PRD-001 (v0.1.0-draft).

### Added
- Core skill `skills/stlc-engineer/SKILL.md`: six STLC phases with gates A–F, autonomy policy, artifact conventions, traceability, evidence and status rules, failure classification, quality gates.
- References for every phase, plus the autonomy policy and artifact schemas.
- Templates for all phase artifacts, the run manifest, and `stlc-policy.yaml`.
- Deterministic artifact validator (`validate_artifacts.py`), including anti-fabrication cross-checks.
- Evaluation suite: 9 fixture repositories, scenario definitions, harness (`scripts/run_evaluations.py`), and 2 golden runs with real execution evidence.
- Adapters (experimental) for Claude Code, Cursor, GitHub Copilot, and Kilo Code; packager and installer.
- CI-agnostic quality and security gate `scripts/run_checks.py` (tests, validators, bandit, pip-audit, gitleaks).

### Standards registry
- Initial registry. ISTQB CTFL v4.0.1 and CT-GenAI v1.1 were verified against istqb.org on 2026-10-25. CT-AI v2.0 is partially verified. All ISO/IEC entries remain **unverified** (iso.org blocked automated retrieval), and their editions come from the PRD. Impact: the agent must cite them with "edition needs verification".

### Known limitations
- No adapter has passed the behavioral suite on a real agent installation yet, so all are `experimental`.
