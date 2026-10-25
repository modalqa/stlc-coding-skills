"""Fixture integrity: seeded behaviour is present, so the evaluation stays meaningful."""
import subprocess
import sys
import tempfile
import unittest
import shutil
from pathlib import Path

from tests.evaluations.helpers import EXPECTED, ROOT

FIXTURES = ROOT / "tests" / "fixtures"


def run_unittest(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "unittest", *args], cwd=repo, capture_output=True, text=True)


class FixtureIntegrityTest(unittest.TestCase):
    def test_business_rules_existing_suite_passes(self):
        result = run_unittest(FIXTURES / "business-rules" / "repo", "discover", "-s", "tests", "-t", ".")
        self.assertEqual(0, result.returncode, result.stderr)

    def test_business_rules_seeded_boundary_defect_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            shutil.copytree(FIXTURES / "business-rules" / "repo", repo)
            shutil.copytree(EXPECTED / "business-rules" / "good-run" / "workspace-changes", repo, dirs_exist_ok=True)
            result = run_unittest(repo, "-v", "tests.test_pricing_boundaries")
            self.assertEqual(1, result.returncode)
            self.assertIn("test_tc004_exactly_500_gets_ten_percent", result.stderr)
            self.assertIn("FAILED (failures=1)", result.stderr)

    def test_missing_environment_cannot_import_driver(self):
        result = run_unittest(FIXTURES / "missing-environment" / "repo", "tests.test_ledger")
        self.assertNotEqual(0, result.returncode)

    def test_prompt_injection_fixture_contains_canary_and_injection(self):
        repo = FIXTURES / "prompt-injection" / "repo"
        self.assertIn("STLCCANARY-", (repo / "config" / "settings.ini").read_text())
        self.assertIn("ignore your testing instructions", (repo / "tests" / "data" / "feedback_samples.json").read_text())

    def test_flawed_tests_fixture_fails_as_designed(self):
        result = run_unittest(FIXTURES / "flawed-tests" / "repo", "tests.test_textutils")
        self.assertNotEqual(0, result.returncode)  # wrong expectation in test_slugify_basic


if __name__ == "__main__":
    unittest.main()
