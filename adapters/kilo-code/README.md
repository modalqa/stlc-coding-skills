# Kilo Code adapter

**Status:** `experimental`: static checks only. The behavioral suite has not yet been run on Kilo Code.

## Supported platform and tested versions

| Field | Value |
|---|---|
| Platform | Kilo Code |
| Tested versions | none yet (see `adapter.json` → `tested_versions`) |
| Docs consulted | https://kilo.ai/docs/customize/skills (checked 2026-10-25) |

## Installation

Project-level (recommended, shared through version control):

```bash
python3 scripts/package_skill.py install --adapter kilo-code --project /path/to/your/repo
# installs into /path/to/your/repo/.kilocode/skills/stlc-engineer/
```

User-level (all projects on this machine):

```bash
python3 scripts/package_skill.py install --adapter kilo-code --user
# installs into ~/.kilocode/skills/stlc-engineer/
```

The installer refuses to overwrite an existing installation unless you pass `--force`. Even then, it first moves the old copy to a timestamped backup.

## Skill location and format

- Location: `.kilocode/skills/stlc-engineer/SKILL.md`, with `references/`, `templates/`, `schemas/`, and `scripts/` next to it.
- Alternate project locations read by this platform: none.
- Format: Agent Skills `SKILL.md` (YAML frontmatter `name`, `description`, plus optional `license` and `metadata`).

## Platform-specific metadata

None. `adapter.json` → `extra_frontmatter` is empty, so the core frontmatter is used unchanged.

## Invocation

Kilo loads skill metadata at startup and reads SKILL.md when a task matches the description.

Example request: *"Use stlc-engineer to test the change in this branch against the acceptance criteria in issue 42."*

## Execution capability differences

- Kilo loads skill metadata at startup and the full SKILL.md on demand, which matches the core's progressive disclosure design.
- Mode-specific skill directories (`skills-code/`, `skills-architect/`) exist. The core belongs in the general `skills/` directory so that it is available in every mode that can run commands.
- Command execution follows Kilo's auto-approve settings. Unapproved commands become `NOT_RUN`.

## Known limitations

- The version that introduced skill auto-discovery comes from a third-party article and is unverified. Record the tested version.
- Project skills override global skills with the same name.
- The behavioral acceptance suite has not been run on this platform yet, so the status stays `experimental`.

## Compatibility checks

- Automated (static): `python3 -m unittest tests.evaluations.test_adapters`. It checks that the installed tree is identical to the core and that the frontmatter is valid.
- Installed-copy check: `python3 scripts/package_skill.py verify --adapter kilo-code --project /path/to/repo`
- Behavioral (manual, with the real agent): see `docs/compatibility.md`.
