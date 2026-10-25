# Release Checklist (PRD §18)

- [ ] Re-verify every standards registry entry against its official source. Update `verification_status`, `verified_on`, and `verified_by`. Record the changes in CHANGELOG under "Standards registry".
- [ ] Re-verify the ISTQB syllabus versions (CTFL, CT-GenAI, CT-AI).
- [ ] Re-check each adapter's documented skill locations and frontmatter support. Update `docs_checked_on`.
- [ ] Run the behavioral suite for every adapter declared `supported` (docs/compatibility.md).
- [ ] `python3 scripts/run_checks.py` passes with **no skipped** security steps.
- [ ] Update dev tool versions in `requirements-dev.txt` to the latest releases with no known vulnerabilities (pip-audit clean), and re-review their licenses.
- [ ] Bump the version in `VERSION`, `SKILL.md` metadata, and `validate_artifacts.py`. Write the CHANGELOG entry.
- [ ] Set the security contact in SECURITY.md (required before the first public release).
- [ ] Publish the limitations and supported versions in the release notes.
- [ ] Build: `python3 scripts/package_skill.py build`, then attach `dist/stlc-engineer-<ver>.zip` and `SHA256SUMS`.
- [ ] If any secret was ever committed: rotate it, purge it from history, and document the incident.
