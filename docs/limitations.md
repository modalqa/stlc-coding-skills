# Known Limitations

1. **No adapter has passed the behavioral suite yet.** All adapters are `experimental` (see compatibility.md).
2. **ISO/IEC registry entries are unverified.** The editions come from the PRD. iso.org could not be checked automatically. They must be verified by hand before release.
3. **The validator checks consistency, not truth.** It cannot tell whether a passing test asserts the right thing, or whether an evidence log was produced by the command it claims. It raises the cost of fabrication but does not eliminate it. Human review of evidence remains necessary for high-stakes decisions.
4. **Defect-detection metrics are heuristic.** Scenario `detect_pattern`s match keywords in defect reports. Confirm true and false positives by hand.
5. **Fixtures are small and Python-only.** They test the agent's discipline, not its framework coverage. Fixtures for JavaScript/TypeScript, Java, and Go are future work.
6. **Secret detection is pattern-based** and will miss custom formats. Use gitleaks in CI as well, and add project-specific patterns through `stlc-policy.yaml` → `data.redact_patterns`.
7. **The skill cannot enforce permissions.** Enforcement belongs to the host agent's permission system. The skill only instructs the agent and records what it did.
8. **The recommendation is advisory.** It is never a release approval.
9. **No token or duration metrics** are collected by the harness. Use the agent's own telemetry.
