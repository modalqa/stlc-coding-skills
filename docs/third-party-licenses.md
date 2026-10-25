# Third-Party Licenses

The skill and its scripts use **only the Python standard library** (PSF License). Nothing third-party is redistributed.

Development and CI tooling (not shipped):

| Package | Version | License | Commercial use | Source | Reviewed |
|---|---|---|---|---|---|
| bandit | 1.9.4 | Apache-2.0 | yes | https://pypi.org/project/bandit/ | 2026-10-25 |
| pip-audit | 2.10.1 | Apache-2.0 | yes | https://pypi.org/project/pip-audit/ | 2026-10-25 (PyPI classifier: Apache Software License) |
| gitleaks (binary, optional) | 8.30.1 | MIT | yes | https://github.com/gitleaks/gitleaks | 2026-10-25 |

Fixture-only references (not installed by this repo):

| Package | Referenced by | License | Note |
|---|---|---|---|
| psycopg | tests/fixtures/missing-environment | LGPL-3.0 | Not installed. It is named only to simulate a missing environment. LGPL needs legal review before a real product depends on it. |

The gitleaks *GitHub Action* (as opposed to the MIT CLI) requires a license key for organisation accounts. This project uses the CLI through `scripts/run_checks.py`.
