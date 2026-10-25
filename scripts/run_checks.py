#!/usr/bin/env python3
"""CI-agnostic quality and security gate for this repository.

Run locally or call it from any CI system (GitLab CI, Jenkins, Azure Pipelines,
Bitbucket, a pre-push hook, ...). It does not depend on GitHub Actions.

    python3 scripts/run_checks.py                 # everything; missing security tools fail the run
    python3 scripts/run_checks.py --allow-missing-tools   # local convenience: missing tools are SKIPPED
    python3 scripts/run_checks.py --only tests,repository

Steps:
  repository  scripts/validate_repository.py (structure, contract, registry, adapters, secret patterns)
  tests       unit + evaluation self-tests (tests/evaluations, stdlib unittest)
  golden      validator on every golden run in tests/expected
  package     reproducible build into a temporary directory
  sast        bandit (Python SAST)                       -- pip install -r requirements-dev.txt
  deps        pip-audit on requirements-dev.txt (known vulnerabilities in dev tooling)
  secrets     gitleaks (secret scan; git history when available, else working tree)
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def golden_cmds() -> list[list[str]]:
    validator = str(ROOT / "skills/stlc-engineer/scripts/validate_artifacts.py")
    return [[PY, validator, str(run), "--phase", "6"] for run in sorted(ROOT.glob("tests/expected/*/*/RUN-*"))]


def steps(tmp: Path) -> dict[str, dict]:
    in_git = (ROOT / ".git").exists()
    gitleaks = ["gitleaks", "git", "--redact", "--no-banner", "--config", ".gitleaks.toml", "."] if in_git else \
               ["gitleaks", "dir", "--redact", "--no-banner", "--config", ".gitleaks.toml", "."]
    return {
        "repository": {"cmds": [[PY, "scripts/validate_repository.py"]]},
        "tests": {"cmds": [[PY, "-m", "unittest", "discover", "-s", "tests/evaluations", "-t", ".", "-v"]]},
        "golden": {"cmds": golden_cmds()},
        "package": {"cmds": [[PY, "scripts/package_skill.py", "build", "--out", str(tmp / "dist")]]},
        "sast": {"tool": "bandit", "cmds": [["bandit", "-q", "-r", "scripts", "skills/stlc-engineer/scripts", "-ll"]]},
        "deps": {"tool": "pip-audit", "cmds": [["pip-audit", "-r", "requirements-dev.txt", "--progress-spinner", "off"]]},
        "secrets": {"tool": "gitleaks", "cmds": [gitleaks]},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", help="comma-separated subset of steps")
    parser.add_argument("--allow-missing-tools", action="store_true",
                        help="mark steps whose external tool is not installed as SKIPPED instead of FAILED")
    args = parser.parse_args(argv)

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        plan = steps(Path(tmp))
        selected = args.only.split(",") if args.only else list(plan)
        unknown = set(selected) - set(plan)
        if unknown:
            parser.error(f"unknown steps: {', '.join(sorted(unknown))}")
        for name in selected:
            step = plan[name]
            tool = step.get("tool")
            if tool and shutil.which(tool) is None:
                status = "SKIPPED" if args.allow_missing_tools else "FAILED"
                results.append((name, status, f"'{tool}' not installed (pip install -r requirements-dev.txt; "
                                              f"gitleaks: https://github.com/gitleaks/gitleaks)"))
                continue
            started = time.monotonic()
            failed = None
            for cmd in step["cmds"]:
                print(f"\n=== [{name}] {' '.join(cmd)}", flush=True)
                if subprocess.run(cmd, cwd=ROOT).returncode != 0:
                    failed = cmd
                    break
            detail = f"{time.monotonic() - started:.1f}s" + (f"; failed: {' '.join(failed)}" if failed else "")
            results.append((name, "FAILED" if failed else "PASSED", detail))

    print("\n=== Summary")
    for name, status, detail in results:
        print(f"{status:8} {name:11} {detail}")
    failed = [r for r in results if r[1] == "FAILED"]
    skipped = [r for r in results if r[1] == "SKIPPED"]
    if skipped:
        print(f"\nWARNING: {len(skipped)} security step(s) skipped; this run is not a complete gate.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
