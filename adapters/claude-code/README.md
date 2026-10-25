# Claude Code adapter

**Status:** `experimental`: static checks only. The behavioral suite has not yet been run on Claude Code.

## Supported platform and tested versions

| Field | Value |
|---|---|
| Platform | Claude Code |
| Tested versions | none yet (see `adapter.json` → `tested_versions`) |
| Docs consulted | https://code.claude.com/docs/en/skills (checked 2026-10-25) |

## Installation

Project-level (recommended, shared through version control):

```bash
python3 scripts/package_skill.py install --adapter claude-code --project /path/to/your/repo
# installs into /path/to/your/repo/.claude/skills/stlc-engineer/
```

User-level (all projects on this machine):

```bash
python3 scripts/package_skill.py install --adapter claude-code --user
# installs into ~/.claude/skills/stlc-engineer/
```

The installer refuses to overwrite an existing installation unless you pass `--force`. Even then, it first moves the old copy to a timestamped backup.

## Skill location and format

- Location: `.claude/skills/stlc-engineer/SKILL.md`, with `references/`, `templates/`, `schemas/`, and `scripts/` next to it.
- Alternate project locations read by this platform: none.
- Format: Agent Skills `SKILL.md` (YAML frontmatter `name`, `description`, plus optional `license` and `metadata`).

## Platform-specific metadata

None. `adapter.json` → `extra_frontmatter` is empty, so the core frontmatter is used unchanged.

## Invocation

Automatic when the request matches the description, or explicitly with /stlc-engineer [arguments].

Example request: *"Use stlc-engineer to test the change in this branch against the acceptance criteria in issue 42."*

## Execution capability differences

- Claude Code exposes skills as slash commands, so `/stlc-engineer <request>` works as well as automatic activation.
- Execution permissions come from Claude Code's permission modes and `settings.json` allow/deny rules, not from the skill. In default (interactive) mode, Bash test commands may prompt for approval. In auto or non-interactive (`-p`) runs, commands outside the allowlist are denied, and the skill must record those tests as `NOT_RUN`/`BLOCKED`.
- The skill deliberately does **not** set `allowed-tools`. Pre-approving shell commands is a project decision (Claude Code's docs note that `allowed-tools` from project skills applies even in untrusted folders).
- Optional Claude Code frontmatter (`context: fork`, `model`, `effort`, …) is not used, to keep the core portable.

## Known limitations

- Unknown frontmatter keys (`license`, `metadata`) are ignored by Claude Code. If the skill is uploaded to claude.ai or the Skills API, only `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools` are accepted, and the core uses only those.
- The description is truncated in the skill listing (combined with `when_to_use`) at about 1,536 characters. The core description is shorter.
- The behavioral acceptance suite has not been run on this platform yet, so the status stays `experimental`.

## Compatibility checks

- Automated (static): `python3 -m unittest tests.evaluations.test_adapters`. It checks that the installed tree is identical to the core and that the frontmatter is valid.
- Installed-copy check: `python3 scripts/package_skill.py verify --adapter claude-code --project /path/to/repo`
- Behavioral (manual, with the real agent): see `docs/compatibility.md`.
