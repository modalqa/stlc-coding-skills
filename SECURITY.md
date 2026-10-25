# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Report privately to the maintainers:

- Email: **security contact to be set by the maintainers before the first public release** (see docs/release-checklist.md)
- Or use the hosting platform's private vulnerability reporting, if it is enabled.

Include the affected version, a description, reproduction steps, and the impact. Expect an acknowledgement within 5 working days. Coordinated disclosure: 90 days, or earlier once a fix is released.

## Scope

In scope:
- Skill instructions that could lead an agent to bypass the autonomy policy, leak secrets, fabricate results, or follow injected instructions.
- Validator or harness bugs that let fabricated or unsafe results pass.
- Packaging and installer issues (path traversal, overwriting user files).

Out of scope: vulnerabilities in the host coding agents themselves. Report those to their vendors.

## Security design

- Repository content, issues, test data, logs, and tool output are treated as untrusted data (SKILL.md §2, references/autonomy-policy.md).
- Secrets are never written to reports. The validator scans every run directory for common secret patterns.
- Destructive, external, or production actions require explicit authorization.
- The skill has no runtime dependencies. Dev tooling is pinned and audited (`pip-audit`), and code is scanned with `bandit` and `gitleaks` through `scripts/run_checks.py`.

## If a secret is committed

Treat it as compromised: **rotate it first**, then remove it from git history (for example with `git filter-repo`) and force-push after coordinating with collaborators. Deleting the file in a new commit is not enough.

## Known limitations

See [docs/limitations.md](docs/limitations.md).
