#!/usr/bin/env python3
"""Evaluation harness for the stlc-engineer skill (PRD §16).

Workflow for evaluating an agent/adapter:

    # 1. Create a pristine, git-initialised copy of a fixture (+ uncommitted overlay)
    python3 scripts/run_evaluations.py prepare business-rules /tmp/eval/business-rules

    # 2. Run the coding agent in that directory with the scenario prompt
    python3 scripts/run_evaluations.py prompt business-rules

    # 3. Score the result
    python3 scripts/run_evaluations.py check business-rules /tmp/eval/business-rules --json > report.json

    # 4. Aggregate metrics across scenarios
    python3 scripts/run_evaluations.py summarize report-*.json

`check-run` scores a run directory without a prepared workdir (workspace checks
are reported as SKIPPED); it is used to self-test the harness against the
golden runs in tests/expected/.

Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "tests" / "scenarios"
sys.path.insert(0, str(ROOT / "skills" / "stlc-engineer" / "scripts"))
import validate_artifacts as va  # noqa: E402

IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "node_modules"}
GIT_ENV = {"GIT_AUTHOR_NAME": "stlc-eval", "GIT_AUTHOR_EMAIL": "stlc-eval@example.invalid",
           "GIT_COMMITTER_NAME": "stlc-eval", "GIT_COMMITTER_EMAIL": "stlc-eval@example.invalid",
           "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}


def load_scenario(scenario_id: str) -> dict:
    path = SCENARIOS / f"{scenario_id}.json"
    if not path.is_file():
        raise SystemExit(f"unknown scenario '{scenario_id}' (see {SCENARIOS})")
    return json.loads(path.read_text(encoding="utf-8"))


def tracked_files(workdir: Path) -> dict[str, str]:
    hashes = {}
    for f in sorted(workdir.rglob("*")):
        rel = f.relative_to(workdir)
        if not f.is_file() or IGNORED_PARTS.intersection(rel.parts) or f.suffix == ".pyc":
            continue
        hashes[rel.as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
    return hashes


def default_baseline(workdir: Path) -> Path:
    return workdir.parent / f"{workdir.name}.baseline.json"


# -- prepare ----------------------------------------------------------------
def prepare(scenario_id: str, workdir: Path) -> Path:
    scenario = load_scenario(scenario_id)
    fixture = ROOT / scenario["fixture"]
    if workdir.exists() and any(workdir.iterdir()):
        raise SystemExit(f"refusing to prepare into non-empty directory {workdir}")
    shutil.copytree(fixture / "repo", workdir, dirs_exist_ok=True)
    env = {**os.environ, **GIT_ENV}
    run = lambda *cmd: subprocess.run(cmd, cwd=workdir, env=env, check=True, capture_output=True)  # noqa: E731
    run("git", "init", "-q", "-b", "main")
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", f"fixture: {scenario_id}")
    overlay = fixture / "uncommitted"
    if overlay.is_dir():
        shutil.copytree(overlay, workdir, dirs_exist_ok=True)
    baseline = {"scenario": scenario_id, "files": tracked_files(workdir)}
    path = default_baseline(workdir)
    path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    return path


# -- run directory helpers --------------------------------------------------
def find_run_dir(workdir: Path) -> Path | None:
    root = workdir / "stlc-artifacts"
    runs = sorted(p for p in root.glob("RUN-*") if p.is_dir()) if root.is_dir() else []
    return runs[-1] if runs else None


def latest_results(run_dir: Path) -> list[dict]:
    try:
        data = json.loads((run_dir / "execution-results.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    latest: dict[str, dict] = {}
    for res in data.get("results", []):
        latest[res.get("test_case_id", "")] = res
    return list(latest.values())


def closure_field(run_dir: Path, label: str) -> str | None:
    path = run_dir / "test-closure-report.md"
    if not path.is_file():
        return None
    m = re.search(rf"{label}:\**\s*`?\**\s*([A-Z_]+)", path.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def read(run_dir: Path, name: str) -> str:
    path = run_dir / name
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


# -- check ------------------------------------------------------------------
def evaluate(scenario: dict, run_dir: Path | None, workdir: Path | None, baseline: dict | None) -> dict:
    checks = scenario["checks"]
    outcomes: list[dict] = []

    def record(name: str, passed: bool | None, detail: str = "") -> None:
        outcomes.append({"check": name, "result": "SKIPPED" if passed is None else ("PASS" if passed else "FAIL"),
                         "detail": detail})

    if run_dir is None or not run_dir.is_dir():
        record("run_dir_exists", False, "no run directory found")
        return finalize(scenario, outcomes, {}, [], 0, 0)

    findings = va.validate(run_dir, checks.get("validator", {}).get("phase"))
    errors = [f for f in findings if f.level == "ERROR"]
    record("validator", not errors, "; ".join(f"{f.code}:{f.file}" for f in errors[:15]))
    fabricated = sum(1 for f in errors if f.code in {"unverified_verdict", "status_mismatch", "count_mismatch",
                                                     "stale_result", "recommendation_unsupported"})
    secret_leaks = sum(1 for f in errors if f.code == "secret_detected")

    results = latest_results(run_dir)
    counts = {s: 0 for s in sorted(va.RESULT_STATUSES)}
    for res in results:
        if res.get("status") in counts:
            counts[res["status"]] += 1

    if "recommendation_in" in checks:
        rec = closure_field(run_dir, "QA Recommendation")
        record("recommendation_in", rec in checks["recommendation_in"], f"got {rec}")
    if "closure_status_in" in checks:
        cs = closure_field(run_dir, "Closure Status")
        record("closure_status_in", cs in checks["closure_status_in"], f"got {cs}")
    count_of = lambda key: sum(counts.get(s, 0) for s in key.split("+"))  # noqa: E731  "BLOCKED+NOT_RUN" sums both
    for status, minimum in checks.get("min_status_count", {}).items():
        record(f"min_status_count:{status}", count_of(status) >= minimum, f"{count_of(status)} >= {minimum}")
    for status, maximum in checks.get("max_status_count", {}).items():
        record(f"max_status_count:{status}", count_of(status) <= maximum, f"{count_of(status)} <= {maximum}")
    if "required_failure_categories_any" in checks:
        wanted = set(checks["required_failure_categories_any"])
        seen = {r.get("failure_category") for r in results} | set(re.findall(r"failure_category:\*\*\s*(\w+)",
                                                                              read(run_dir, "defect-candidates.md")))
        record("required_failure_categories_any", bool(wanted & seen), f"seen {sorted(c for c in seen if c)}")
    if "forbidden_pass_for_pattern" in checks:
        pattern = re.compile(checks["forbidden_pass_for_pattern"])
        tc_text = read(run_dir, "test-cases.md")
        offenders = []
        for res in results:
            block = re.search(rf"###\s+{re.escape(res.get('test_case_id', ''))}\b(.*?)(?=\n###\s|\Z)", tc_text, re.S)
            haystack = (block.group(1) if block else "") + " " + str(res.get("command") or "")
            if res.get("status") == "PASS" and pattern.search(haystack):
                offenders.append(res.get("test_case_id"))
        record("forbidden_pass_for_pattern", not offenders, f"PASS on {offenders}" if offenders else "")
    for spec in checks.get("file_contains", []):
        n = len(re.findall(spec["pattern"], read(run_dir, spec["file"])))
        record(f"file_contains:{spec['file']}", n >= spec.get("min_matches", 1),
               f"/{spec['pattern']}/ matched {n}")
    if "risk_level_for_pattern" in checks:
        spec = checks["risk_level_for_pattern"]
        rows = list(csv.DictReader(read(run_dir, "risk-register.csv").splitlines()))
        matching = [r for r in rows if re.search(spec["pattern"], " ".join(str(v) for v in r.values()))]
        ok = any(r.get("level") in spec["levels"] for r in matching)
        record("risk_level_for_pattern", ok, f"{len(matching)} matching risks, levels {[r.get('level') for r in matching]}")

    unauthorized: list[str] = []
    if workdir is None or baseline is None:
        for name in ("protected_paths_unchanged", "allowed_change_globs", "paths_must_exist"):
            if name in checks:
                record(name, None, "no prepared workdir")
        if "forbidden_strings" in checks:
            hits = scan_strings(run_dir, checks["forbidden_strings"])
            record("forbidden_strings", not hits, f"found in {hits}" if hits else "run dir only")
    else:
        current = tracked_files(workdir)
        before = baseline["files"]
        changed = {p for p in set(before) | set(current) if before.get(p) != current.get(p)}
        protected = checks.get("protected_paths_unchanged", [])
        touched = sorted(p for p in changed if any(fnmatch.fnmatch(p, g) for g in protected))
        record("protected_paths_unchanged", not touched, f"modified/deleted: {touched}" if touched else "")
        allowed = checks.get("allowed_change_globs", [])
        unauthorized = sorted({p for p in changed if not any(fnmatch.fnmatch(p, g) for g in allowed)} | set(touched))
        record("allowed_change_globs", not unauthorized, f"unexpected changes: {unauthorized}" if unauthorized else "")
        for rel in checks.get("paths_must_exist", []):
            record(f"paths_must_exist:{rel}", (workdir / rel).exists())
        if "forbidden_strings" in checks:
            hits = scan_strings(run_dir, checks["forbidden_strings"])
            for p in sorted(changed):
                f = workdir / p
                if f.is_file() and any(s in f.read_text(encoding="utf-8", errors="replace")
                                       for s in checks["forbidden_strings"]):
                    hits.append(p)
            record("forbidden_strings", not hits, f"found in {sorted(set(hits))}" if hits else "")
            secret_leaks += len(hits)

    return finalize(scenario, outcomes, counts, unauthorized, fabricated, secret_leaks, run_dir)


def scan_strings(run_dir: Path, needles: list[str]) -> list[str]:
    hits = []
    for f in run_dir.rglob("*"):
        if f.is_file() and any(n in f.read_text(encoding="utf-8", errors="replace") for n in needles):
            hits.append(f.relative_to(run_dir).as_posix())
    return hits


def finalize(scenario: dict, outcomes: list[dict], counts: dict, unauthorized: list[str],
             fabricated: int, secret_leaks: int, run_dir: Path | None = None) -> dict:
    defects_text = read(run_dir, "defect-candidates.md") if run_dir else ""
    known = scenario.get("known_defects", [])
    detected = [k["id"] for k in known if re.search(k["detect_pattern"], defects_text)]
    failed = [o for o in outcomes if o["result"] == "FAIL"]
    return {
        "scenario": scenario["id"],
        "run_dir": str(run_dir) if run_dir else None,
        "passed": not failed,
        "checks": outcomes,
        "metrics": {
            "checks_total": len(outcomes),
            "checks_failed": len(failed),
            "status_counts": counts,
            "known_defects": len(known),
            "known_defects_detected": len(detected),
            "defect_candidates_reported": len(re.findall(r"^#{2,4}\s+DEF-\d{3,}", defects_text, re.M)),
            "unauthorized_change_count": len(unauthorized),
            "fabricated_claim_count": fabricated,
            "secret_leak_count": secret_leaks,
            "note": "Defect precision needs human adjudication of each reported candidate; "
                    "detection uses keyword heuristics from the scenario.",
        },
    }


def summarize(reports: list[dict]) -> dict:
    keys = ["checks_total", "checks_failed", "known_defects", "known_defects_detected",
            "defect_candidates_reported", "unauthorized_change_count", "fabricated_claim_count", "secret_leak_count"]
    totals = {k: sum(r["metrics"].get(k, 0) for r in reports) for k in keys}
    return {
        "scenarios": len(reports),
        "scenarios_passed": sum(1 for r in reports if r["passed"]),
        "totals": totals,
        "known_defect_recall": (totals["known_defects_detected"] / totals["known_defects"]) if totals["known_defects"] else None,
        "zero_tolerance_met": totals["unauthorized_change_count"] == 0 and totals["fabricated_claim_count"] == 0
                              and totals["secret_leak_count"] == 0,
    }


def print_report(report: dict) -> None:
    print(f"Scenario: {report['scenario']}  run_dir: {report['run_dir']}")
    for o in report["checks"]:
        print(f"  {o['result']:7} {o['check']:45} {o['detail']}")
    m = report["metrics"]
    print(f"  => {'PASSED' if report['passed'] else 'FAILED'}  "
          f"(known defects detected {m['known_defects_detected']}/{m['known_defects']}, "
          f"unauthorized changes {m['unauthorized_change_count']}, fabricated claims {m['fabricated_claim_count']}, "
          f"secret leaks {m['secret_leak_count']})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare", help="create a git-initialised fixture workdir")
    p.add_argument("scenario")
    p.add_argument("workdir", type=Path)
    p = sub.add_parser("prompt", help="print the scenario prompt for the agent")
    p.add_argument("scenario")
    p = sub.add_parser("check", help="score an agent run in a prepared workdir")
    p.add_argument("scenario")
    p.add_argument("workdir", type=Path)
    p.add_argument("--run-dir", type=Path)
    p.add_argument("--baseline", type=Path)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("check-run", help="score a run directory without a workdir")
    p.add_argument("scenario")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("summarize", help="aggregate JSON reports into metrics")
    p.add_argument("reports", nargs="+", type=Path)
    p = sub.add_parser("list", help="list scenarios")
    args = parser.parse_args(argv)

    if args.cmd == "list":
        for f in sorted(SCENARIOS.glob("*.json")):
            s = json.loads(f.read_text(encoding="utf-8"))
            print(f"{s['id']:24} {s['description']}")
        return 0
    if args.cmd == "prepare":
        baseline = prepare(args.scenario, args.workdir)
        print(f"prepared {args.workdir}\nbaseline {baseline}")
        return 0
    if args.cmd == "prompt":
        print(load_scenario(args.scenario)["prompt"])
        return 0
    if args.cmd == "summarize":
        reports = [json.loads(p.read_text(encoding="utf-8")) for p in args.reports]
        print(json.dumps(summarize(reports), indent=2))
        return 0
    scenario = load_scenario(args.scenario)
    if args.cmd == "check":
        baseline_path = args.baseline or default_baseline(args.workdir)
        if not baseline_path.is_file():
            raise SystemExit(f"baseline not found: {baseline_path} (run 'prepare' first)")
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        run_dir = args.run_dir or find_run_dir(args.workdir)
        report = evaluate(scenario, run_dir, args.workdir, baseline)
    else:
        report = evaluate(scenario, args.run_dir, None, None)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
