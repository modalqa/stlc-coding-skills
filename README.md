# STLC Coding Agent Skill (`stlc-engineer`)

A portable [Agent Skill](https://agentskills.io/specification) that makes AI coding agents run the full **Software Testing Life Cycle**: requirement analysis, risk assessment, planning, design, implementation, execution with evidence, and closure. It works with traceability and honest reporting throughout.

It is a methodology layer, not a new test framework, SaaS product, or agent. It reuses the test tools your repository already has.

> **Status: 0.1.0, experimental.** The core contract, validator, and evaluation suite are implemented. No adapter has passed the behavioral suite on a real agent yet (see [docs/compatibility.md](docs/compatibility.md)).

## What you get

- **Six phases with gates A–F**, each producing reviewable artifacts in `stlc-artifacts/<RUN-ID>/`: requirements analysis, risk register, test plan, test cases, traceability matrix, execution results with raw evidence, defect candidates, closure report, and release-readiness recommendation.
- **Autonomous by default, governed by policy.** The agent works without step-by-step confirmation, but destructive, external, production, and release actions need authorization ([autonomy policy](skills/stlc-engineer/references/autonomy-policy.md)).
- **No fabricated results.** A deterministic validator rejects PASS without an executed command and evidence, stale results, counts that do not match the record, unsupported READY verdicts, leaked secrets, and ISO compliance claims.
- **Standards-informed, not standards-washing.** A registry of ISO/IEC/IEEE 29119, ISO/IEC 25010, and ISTQB references with verification status. No invented clause numbers.
- **Adapters** for Claude Code, Cursor, GitHub Copilot, and Kilo Code, all built from one core.
- **Evaluation suite.** 9 fixture repositories with seeded defects, prompt injection, missing environments, and uncommitted user changes, plus a scoring harness and 2 golden runs with real execution evidence.

## Quick start

```bash
# 1. Install into your project (pick your agent)
python3 scripts/package_skill.py install --adapter claude-code --project /path/to/repo

# 2. In the agent, inside /path/to/repo:
#    "Use stlc-engineer to test the change on this branch against the acceptance criteria in docs/feature.md"

# 3. Validate what the agent produced
python3 /path/to/repo/.claude/skills/stlc-engineer/scripts/validate_artifacts.py /path/to/repo/stlc-artifacts/RUN-<id>
```

See [docs/installation.md](docs/installation.md) for every adapter and for troubleshooting.

## Try the example

The golden run in [tests/expected/business-rules/good-run/](tests/expected/business-rules/good-run/) shows a complete cycle on the pricing fixture. The agent's boundary tests found a real seeded defect (500.00 priced in the wrong tier), classified it, and closed with `NOT_READY`.

```bash
python3 scripts/run_evaluations.py list
python3 scripts/run_evaluations.py prepare business-rules /tmp/eval/business-rules
python3 scripts/run_evaluations.py prompt business-rules     # give this to your agent in /tmp/eval/business-rules
python3 scripts/run_evaluations.py check business-rules /tmp/eval/business-rules
```

## Repository layout

```
skills/stlc-engineer/      core skill: SKILL.md, references/, templates/, schemas/, scripts/validate_artifacts.py
adapters/                  claude-code, cursor, github-copilot, kilo-code (adapter.json + README)
tests/fixtures/            9 evaluation repositories (PRD §16.1)
tests/scenarios/           expected outcomes per fixture
tests/expected/            golden runs (real execution evidence)
tests/evaluations/         unittest suite for validator, harness, packaging, repository
scripts/                   validate_repository.py, package_skill.py, run_evaluations.py, run_checks.py
docs/                      architecture, installation, compatibility, standards mapping, CI, limitations
```

## Quality and security gate

```bash
python3 -m pip install -r requirements-dev.txt   # bandit, pip-audit (Apache-2.0)
# + gitleaks CLI (MIT): https://github.com/gitleaks/gitleaks
python3 scripts/run_checks.py
```

The gate does not depend on any particular CI system. Examples for GitLab CI, Jenkins, and git hooks are in [docs/ci-integration.md](docs/ci-integration.md).

## Important limitations

- The QA recommendation is advisory and **not a release approval**.
- Using this skill does **not** make a project ISO-conformant or certified.
- The validator checks consistency, not truth. Human review of evidence still matters ([docs/limitations.md](docs/limitations.md)).

## License

[Apache License 2.0](LICENSE). Contributions: [CONTRIBUTING.md](CONTRIBUTING.md). Security: [SECURITY.md](SECURITY.md).
