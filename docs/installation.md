# Installation

Requirements: Python 3.11+ (used only by the validator and installer scripts; the skill instructions themselves need nothing).

## Option A — installer script (recommended)

```bash
git clone <this-repo> stlc-agent-skill && cd stlc-agent-skill
python3 scripts/package_skill.py install --adapter claude-code     --project /path/to/your/repo
python3 scripts/package_skill.py install --adapter cursor          --project /path/to/your/repo
python3 scripts/package_skill.py install --adapter github-copilot  --project /path/to/your/repo
python3 scripts/package_skill.py install --adapter kilo-code       --project /path/to/your/repo
# user-level instead of project-level:
python3 scripts/package_skill.py install --adapter claude-code --user
```

| Adapter | Project location | User location |
|---|---|---|
| claude-code | `.claude/skills/stlc-engineer/` | `~/.claude/skills/stlc-engineer/` |
| cursor | `.cursor/skills/stlc-engineer/` | `~/.cursor/skills/stlc-engineer/` |
| github-copilot | `.github/skills/stlc-engineer/` | `~/.copilot/skills/stlc-engineer/` |
| kilo-code | `.kilocode/skills/stlc-engineer/` | `~/.kilocode/skills/stlc-engineer/` |

Locations were taken from each vendor's documentation on 2026-10-25 (links in `adapters/*/README.md`). Vendors change these paths. Re-check them when you upgrade the agent.

Install into **one** location per agent. Several agents (Cursor, Copilot) also read `.agents/skills/` or `.claude/skills/`, which can produce duplicates.

## Option B — release archive

`python3 scripts/package_skill.py build` writes `dist/stlc-engineer-<version>.zip` and `dist/SHA256SUMS`. Verify the checksum, then unzip into the location from the table above.

## Verify the installation

```bash
python3 scripts/package_skill.py verify --adapter claude-code --project /path/to/your/repo
```

Then ask your agent: *"Use stlc-engineer to analyse requirements.md and stop after phase 1."* The run directory `stlc-artifacts/RUN-…/` should appear. Validate it:

```bash
python3 .claude/skills/stlc-engineer/scripts/validate_artifacts.py stlc-artifacts/RUN-… --phase 1
```

## Optional project policy

Copy `skills/stlc-engineer/templates/stlc-policy.yaml` to your repository root and adjust it. Permissions can only be expanded through named, dated `authorizations` entries.

Decide whether `stlc-artifacts/` is committed (an audit trail) or ignored. Evidence logs may contain environment details, so review them before committing.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Skill not discovered | Wrong directory for the agent or version. Check the adapter README. Restart the agent session. Make sure `SKILL.md` begins with `---` on line 1. |
| Agent asks for confirmation on every command | Host permission mode. Allowlist your test commands in the agent's own settings, not in the skill. |
| All results `NOT_RUN` | The agent could not execute commands (permissions or sandbox). This is the intended honest behaviour. Grant execution, then rerun phases 5–6. |
| Validator `stale_result` | Results were copied from an earlier run. Re-execute, or mark them `previous_run` with `NOT_RUN`. |
| Validator `risk_score` | The project uses another risk model. Set `risk.formula: none` and run the validator with `--risk-formula none`. |
| `already exists` on install | Re-run with `--force`. The old copy is moved to `stlc-engineer.bak-<timestamp>`. |
