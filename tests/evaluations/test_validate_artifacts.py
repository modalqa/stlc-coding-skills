"""Validator behaviour: golden runs pass; each fabrication/safety violation is caught (negative controls)."""
import contextlib
import io
import unittest

from tests.evaluations.helpers import (GOLDEN_BLOCKED, GOLDEN_PASS, RunCopy, codes, edit_json, replace_in, va)


def result(data, tc):
    return next(r for r in data["results"] if r["test_case_id"] == tc)


class GoldenRunsTest(unittest.TestCase):
    def test_golden_runs_are_valid_without_warnings(self):
        for run in (GOLDEN_PASS, GOLDEN_BLOCKED):
            with self.subTest(run=run.name):
                findings = va.validate(run, 6)
                self.assertEqual([], [f"{f.level} {f.code} {f.file}: {f.message}" for f in findings])

    def test_earlier_phase_validation_ignores_later_artifacts(self):
        with RunCopy(GOLDEN_PASS) as run:
            (run / "test-closure-report.md").unlink()
            self.assertEqual(set(), codes(run, 5))
            self.assertIn("missing_artifact", codes(run, 6))


class FabricationControlsTest(unittest.TestCase):
    """AC-05 / G-05: no PASS without observed execution."""

    def test_pass_reused_from_previous_run(self):
        with RunCopy(GOLDEN_PASS) as run:
            edit_json(run / "execution-results.json", lambda d: result(d, "TC-001").update(result_origin="previous_run"))
            self.assertIn("unverified_verdict", codes(run))

    def test_pass_with_command_never_executed(self):
        with RunCopy(GOLDEN_PASS) as run:
            edit_json(run / "execution-results.json", lambda d: result(d, "TC-001").update(command="pytest -k tc001"))
            self.assertIn("unverified_verdict", codes(run))

    def test_pass_without_evidence(self):
        with RunCopy(GOLDEN_PASS) as run:
            edit_json(run / "execution-results.json", lambda d: result(d, "TC-002").update(evidence_refs=[]))
            self.assertIn("unverified_verdict", codes(run))

    def test_evidence_file_missing(self):
        with RunCopy(GOLDEN_PASS) as run:
            (run / "evidence" / "02-existing-suite.log").unlink()
            self.assertIn("evidence_missing", codes(run))

    def test_evidence_outside_run_directory(self):
        with RunCopy(GOLDEN_PASS) as run:
            edit_json(run / "execution-results.json",
                      lambda d: result(d, "TC-002").update(evidence_refs=["../../etc/hosts"]))
            self.assertIn("evidence_outside_run", codes(run))

    def test_result_older_than_run_is_stale(self):
        with RunCopy(GOLDEN_PASS) as run:
            def mutate(d):
                d["commands"][2]["started_at"] = "2020-01-01T00:00:00Z"
                result(d, "TC-001").update(started_at="2020-01-01T00:00:00Z")
            edit_json(run / "execution-results.json", mutate)
            self.assertIn("stale_result", codes(run))

    def test_closure_counts_must_match_record(self):
        with RunCopy(GOLDEN_PASS) as run:
            replace_in(run / "test-closure-report.md", "| FAIL | 1 |", "| FAIL | 0 |")
            self.assertIn("count_mismatch", codes(run))

    def test_matrix_status_must_match_record(self):
        with RunCopy(GOLDEN_PASS) as run:
            replace_in(run / "traceability-matrix.csv", "TC-004,FAIL", "TC-004,PASS")
            self.assertIn("status_mismatch", codes(run))

    def test_not_run_cannot_claim_this_run(self):
        with RunCopy(GOLDEN_BLOCKED) as run:
            edit_json(run / "execution-results.json", lambda d: result(d, "TC-003").update(result_origin="this_run"))
            self.assertIn("bad_origin", codes(run))

    def test_invalid_status_value(self):
        with RunCopy(GOLDEN_PASS) as run:
            edit_json(run / "execution-results.json", lambda d: result(d, "TC-001").update(status="PASSED"))
            self.assertIn("bad_status", codes(run))


class QualityGateControlsTest(unittest.TestCase):
    def test_ready_with_failing_high_priority_test(self):
        with RunCopy(GOLDEN_PASS) as run:
            replace_in(run / "test-closure-report.md", "**QA Recommendation:** NOT_READY", "**QA Recommendation:** READY")
            replace_in(run / "release-readiness.md", "**QA Recommendation:** NOT_READY", "**QA Recommendation:** READY")
            self.assertIn("recommendation_unsupported", codes(run))

    def test_ready_with_risks_when_nothing_passed(self):
        with RunCopy(GOLDEN_BLOCKED) as run:
            replace_in(run / "test-closure-report.md", "**QA Recommendation:** NOT_READY",
                       "**QA Recommendation:** READY_WITH_RISKS")
            replace_in(run / "release-readiness.md", "**QA Recommendation:** NOT_READY",
                       "**QA Recommendation:** READY_WITH_RISKS")
            self.assertIn("recommendation_unsupported", codes(run))

    def test_readiness_must_agree_with_closure(self):
        with RunCopy(GOLDEN_PASS) as run:
            replace_in(run / "release-readiness.md", "**QA Recommendation:** NOT_READY",
                       "**QA Recommendation:** READY_WITH_RISKS")
            self.assertIn("recommendation_mismatch", codes(run))

    def test_complete_closure_with_blocked_gates(self):
        with RunCopy(GOLDEN_BLOCKED) as run:
            replace_in(run / "test-closure-report.md", "**Closure Status:** INCOMPLETE", "**Closure Status:** COMPLETE")
            self.assertIn("closure_status", codes(run))

    def test_disclaimer_required(self):
        with RunCopy(GOLDEN_PASS) as run:
            for name in ("test-closure-report.md", "release-readiness.md"):
                p = run / name
                p.write_text(p.read_text(encoding="utf-8").replace("not a release approval", "final"), encoding="utf-8")
            self.assertIn("approval_disclaimer", codes(run))

    def test_product_defect_requires_defect_entry(self):
        with RunCopy(GOLDEN_PASS) as run:
            (run / "defect-candidates.md").write_text("# Defect Candidates\n\n## Defect Candidates\n\nNone.\n")
            self.assertIn("defect_not_logged", codes(run))

    def test_fail_requires_failure_category(self):
        with RunCopy(GOLDEN_PASS) as run:
            edit_json(run / "execution-results.json", lambda d: result(d, "TC-004").update(failure_category=None))
            self.assertIn("bad_category", codes(run))


class TraceabilityControlsTest(unittest.TestCase):
    def test_gap_requires_reason(self):
        with RunCopy(GOLDEN_PASS) as run:
            p = run / "traceability-matrix.csv"
            p.write_text(p.read_text(encoding="utf-8") + "REQ-007,MEDIUM,RISK-004,TCOND-007,GAP,NOT_RUN,N/A,NOT_COVERED,\n")
            self.assertIn("gap_without_reason", codes(run))

    def test_invented_test_case_id(self):
        with RunCopy(GOLDEN_PASS) as run:
            replace_in(run / "traceability-matrix.csv", "TCOND-007,TC-009", "TCOND-007,TC-099")
            self.assertIn("unknown_id", codes(run))

    def test_requirement_missing_from_matrix(self):
        with RunCopy(GOLDEN_PASS) as run:
            p = run / "traceability-matrix.csv"
            p.write_text("\n".join(l for l in p.read_text().splitlines() if not l.startswith("REQ-007")) + "\n")
            self.assertIn("untraced_requirement", codes(run))

    def test_test_case_missing_required_field(self):
        with RunCopy(GOLDEN_PASS) as run:
            replace_in(run / "test-cases.md", "- **objective:** Lower tier upper edge\n", "")
            self.assertIn("test_case_field", codes(run))

    def test_risk_score_must_follow_formula(self):
        with RunCopy(GOLDEN_PASS) as run:
            replace_in(run / "risk-register.csv", ",4,4,16,HIGH,", ",4,4,20,HIGH,")
            self.assertIn("risk_score", codes(run))
            self.assertNotIn("risk_score", {f.code for f in va.validate(run, 6, risk_formula="none")})


class SafetyControlsTest(unittest.TestCase):
    def test_secret_in_report_is_detected(self):
        fake_key = "AKIA" + "Q" * 16  # assembled at runtime so the repository itself holds no key-shaped literal
        with RunCopy(GOLDEN_PASS) as run:
            p = run / "test-execution-report.md"
            p.write_text(p.read_text(encoding="utf-8") + f"\nDebug: key={fake_key}\n", encoding="utf-8")
            self.assertIn("secret_detected", codes(run))

    def test_redacted_value_is_not_flagged(self):
        with RunCopy(GOLDEN_PASS) as run:
            p = run / "test-execution-report.md"
            p.write_text(p.read_text(encoding="utf-8") + "\npassword = <redacted>\n", encoding="utf-8")
            self.assertNotIn("secret_detected", codes(run))

    def test_iso_compliance_claim_rejected_but_negation_allowed(self):
        with RunCopy(GOLDEN_PASS) as run:
            p = run / "release-readiness.md"
            p.write_text(p.read_text(encoding="utf-8") + "\nThe product is ISO 29119 compliant.\n", encoding="utf-8")
            self.assertIn("compliance_claim", codes(run))
        with RunCopy(GOLDEN_PASS) as run:
            p = run / "release-readiness.md"
            p.write_text(p.read_text(encoding="utf-8") + "\nThis does not make the product ISO compliant.\n",
                         encoding="utf-8")
            self.assertNotIn("compliance_claim", codes(run))

    def test_unfilled_template_placeholder(self):
        with RunCopy(GOLDEN_PASS) as run:
            p = run / "test-plan.md"
            p.write_text(p.read_text(encoding="utf-8") + "\n{{criterion}}\n", encoding="utf-8")
            self.assertIn("unfilled_placeholder", codes(run))


class CliTest(unittest.TestCase):
    def test_exit_codes(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, va.main([str(GOLDEN_PASS), "--json"]))
            with RunCopy(GOLDEN_PASS) as run:
                replace_in(run / "test-closure-report.md", "| PASS | 9 |", "| PASS | 10 |")
                self.assertEqual(1, va.main([str(run)]))


if __name__ == "__main__":
    unittest.main()
