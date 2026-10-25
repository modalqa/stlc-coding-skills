# Cursor adapter

**Status:** `experimental`: static checks only. The behavioral suite has not yet been run on Cursor.

## Supported platform and tested versions

| Field | Value |
|---|---|
| Platform | Cursor |
| Tested versions | none yet (see `adapter.json` → `tested_versions`) |
| Docs consulted | https://cursor.com/docs/skills (checked 2026-10-25) |

## Installation

Project-level (recommended, shared through version control):

```bash
python3 scripts/package_skill.py install --adapter cursor --project /path/to/your/repo
# installs into /path/to/your/repo/.cursor/skills/stlc-engineer/
```

User-level (all projects on this machine):

```bash
python3 scripts/package_skill.py install --adapter cursor --user
# installs into ~/.cursor/skills/stlc-engineer/
```

The installer refuses to overwrite an existing installation unless you pass `--force`. Even then, it first moves the old copy to a timestamped backup.

## Skill location and format

- Location: `.cursor/skills/stlc-engineer/SKILL.md`, with `references/`, `templates/`, `schemas/`, and `scripts/` next to it.
- Alternate project locations read by this platform: `.agents/skills`.
- Format: Agent Skills `SKILL.md` (YAML frontmatter `name`, `description`, plus optional `license` and `metadata`).

## Platform-specific metadata

None. `adapter.json` → `extra_frontmatter` is empty, so the core frontmatter is used unchanged.

## Invocation

Agent selects the skill from its description; can also be referenced explicitly in chat.

Example request: *"Use stlc-engineer to test the change in this branch against the acceptance criteria in issue 42."*

## Execution capability differences

- Cursor also reads `.agents/skills/`. Install into one location only, to avoid duplicate skills.
- Terminal command execution depends on Cursor's agent settings (auto-run / allowlist). When a test command is not allowed to run, the skill records `NOT_RUN`.
- Nested `.cursor/skills/` directories in monorepos apply only to files inside that directory.

## Known limitations

- A third-party guide (not verified) claims skills were once limited to the Nightly channel. Confirm on the version you test and record it in `tested_versions`.
- The user-level directory (`~/.cursor/skills`) is taken from the docs as of 2026-10-25 and needs verification.
- The behavioral acceptance suite has not been run on this platform yet, so the status stays `experimental`.

## Compatibility checks

- Automated (static): `python3 -m unittest tests.evaluations.test_adapters`. It checks that the installed tree is identical to the core and that the frontmatter is valid.
- Installed-copy check: `python3 scripts/package_skill.py verify --adapter cursor --project /path/to/repo`
- Behavioral (manual, with the real agent): see `docs/compatibility.md`.
