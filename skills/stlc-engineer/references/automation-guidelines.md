# Automation Guidelines (Phase 4)

## Before writing code

1. Find the existing test framework, runner config, folder layout, naming, fixtures, and helpers. Reuse them.
2. Add a framework or dependency only if none fits. Record the reason and the **license** in `test-approach.md` → Tools. Prefer permissive licenses (MIT, BSD, Apache-2.0). Flag copyleft (GPL/AGPL) or source-available licenses for human review before adding them.
3. Use the latest stable version that has no known vulnerability. Check a vulnerability database or the package audit tool when you have access, and record that you checked.

## Writing tests

- **Structure**: arrange, act, assert, cleanup. Keep setup separate from the assertion.
- **Independence**: no reliance on execution order, shared mutable globals, or leftovers from other tests. Each test creates its own state.
- **Determinism**: control time, randomness (seeds), locale, and timezone. Do not use `sleep` for synchronization; wait on conditions instead.
- **Real assertions**: assert the specific expected value or state. These are forbidden: assertion-free tests, `assert True`, catching every exception, snapshotting errors, or loosening tolerances until the test passes.
- **No hidden retries**: framework-level retries may be used only to *detect* flakiness and must be reported. Never use them to turn a failing run green.
- **Traceability**: put the test case ID in the test name or a docstring or marker (`test_tc012_rejects_expired_token`, `@pytest.mark.tc("TC-012")`, `it("TC-012 ...")`).
- **Data**: use synthetic, minimal fixtures. Never use production data or real personal data. Read secrets from the environment, never hard-code them.
- **Isolation of external services**: use fakes, stubs, or local containers by default. Contract tests document the boundary. Tests against real external services need authorization.

## Fixing tests (test_implementation_defect)

You may change a test only when evidence shows the test is wrong: a wrong
expectation against the requirement, a broken setup, a selector or locator
drift, or a non-determinism you introduced. Record in
`test-execution-report.md` → Test Fixes Applied what was wrong, the evidence,
the fix, and the rerun result. When the *product* is wrong, keep the test
failing and log a defect candidate.

## Smoke check

Run a collection or dry-run (`pytest --collect-only`, `jest --listTests`,
`go vet ./...`, `mvn -q test-compile`, `tsc --noEmit`) before the full
execution. Record the result in `test-inventory.md`.

## CI integration

Add tests to CI only when the policy or the user authorizes it. Match the
existing CI system. Never disable existing jobs or gates.
