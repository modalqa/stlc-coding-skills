# GitHub Copilot (agent mode) adapter

**Status:** `experimental`: static checks only. The behavioral suite has not yet been run on GitHub Copilot (agent mode).

## Supported platform and tested versions

| Field | Value |
|---|---|
| Platform | GitHub Copilot (agent mode) |
| Tested versions | none yet (see `adapter.json` → `tested_versions`) |
| Docs consulted | https://learn.microsoft.com/en-us/visualstudio/ide/copilot-agent-skills (checked 2026-10-25) |

## Installation

Project-level (recommended, shared through version control):

```bash
python3 scripts/package_skill.py install --adapter github-copilot --project /path/to/your/repo
# installs into /path/to/your/repo/.github/skills/stlc-engineer/
```

User-level (all projects on this machine):

```bash
python3 scripts/package_skill.py install --adapter github-copilot --user
# installs into ~/.copilot/skills/stlc-engineer/
```

The installer refuses to overwrite an existing installation unless you pass `--force`. Even then, it first moves the old copy to a timestamped backup.

## Skill location and format

- Location: `.github/skills/stlc-engineer/SKILL.md`, with `references/`, `templates/`, `schemas/`, and `scripts/` next to it.
- Alternate project locations read by this platform: `.agents/skills`, `.claude/skills`.
- Format: Agent Skills `SKILL.md` (YAML frontmatter `name`, `description`, plus optional `license` and `metadata`).

## Platform-specific metadata

None. `adapter.json` → `extra_frontmatter` is empty, so the core frontmatter is used unchanged.

## Invocation

In agent mode, Copilot discovers skills and activates one when the request matches its description.

Example request: *"Use stlc-engineer to test the change in this branch against the acceptance criteria in issue 42."*

## Execution capability differences

- Skills are an **agent mode** feature. Ask/edit modes and code review do not run the STLC workflow.
- Terminal execution and file access are granted by the host IDE or the Copilot coding agent environment, not by the skill. Confirm in the target surface that test commands can run. Otherwise results are `NOT_RUN`.
- Supported surfaces differ (VS Code, Visual Studio, JetBrains, Copilot CLI, the cloud coding agent). Record each tested surface separately in `tested_versions`.

## Known limitations

- Sources disagree on whether `.claude/skills/` is a supported or a legacy location for Copilot. Use `.github/skills/`.
- The cloud coding agent runs in an ephemeral environment. Evidence must be committed or attached to the PR to survive the session.
- The behavioral acceptance suite has not been run on this platform yet, so the status stays `experimental`.

## Compatibility checks

- Automated (static): `python3 -m unittest tests.evaluations.test_adapters`. It checks that the installed tree is identical to the core and that the frontmatter is valid.
- Installed-copy check: `python3 scripts/package_skill.py verify --adapter github-copilot --project /path/to/repo`
- Behavioral (manual, with the real agent): see `docs/compatibility.md`.
