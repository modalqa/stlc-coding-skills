#!/usr/bin/env python3
"""Validate the stlc-engineer repository itself (structure, contract, registry, adapters, secrets).

    python3 scripts/validate_repository.py [--json]

Exit 0 when no errors. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "stlc-engineer"
sys.path.insert(0, str(SKILL / "scripts"))
import validate_artifacts as va  # noqa: E402

REQUIRED_FILES = [
    "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", "VERSION", ".gitignore",
    "requirements-dev.txt", ".gitleaks.toml",
    "skills/stlc-engineer/SKILL.md",
    *[f"skills/stlc-engineer/references/{n}" for n in [
        "standards-registry.md", "standards-registry.json", "stlc-workflow.md", "requirement-analysis.md",
        "risk-based-testing.md", "test-design-techniques.md", "automation-guidelines.md",
        "execution-and-evidence.md", "traceability.md", "release-evaluation.md", "autonomy-policy.md",
        "artifact-schemas.md"]],
    *[f"skills/stlc-engineer/templates/{n}" for n in [
        "requirements-analysis.md", "test-plan.md", "test-cases.md", "risk-register.csv",
        "traceability-matrix.csv", "defect-report.md", "test-closure-report.md", "run-manifest.json",
        "execution-results.json", "stlc-policy.yaml"]],
    "skills/stlc-engineer/scripts/validate_artifacts.py",
    "docs/architecture.md", "docs/installation.md", "docs/compatibility.md", "docs/standards-mapping.md",
    "docs/limitations.md", "docs/release-checklist.md", "docs/third-party-licenses.md",
    "scripts/validate_repository.py", "scripts/package_skill.py", "scripts/run_evaluations.py", "scripts/run_checks.py",
]
REQUIRED_DIRS = ["tests/fixtures", "tests/scenarios", "tests/expected", "tests/evaluations",
                 "adapters/claude-code", "adapters/cursor", "adapters/github-copilot", "adapters/kilo-code"]
SKILL_SECTIONS = ["When to use", "Non-negotiable rules", "Autonomy policy", "Start of every run", "The six phases",
                  "Artifact conventions", "Traceability", "Execution status and evidence", "Failure classification",
                  "Quality gates", "Standards usage"]
ADAPTER_SECTIONS = ["Supported platform and tested versions", "Installation", "Skill location and format",
                    "Platform-specific metadata", "Invocation", "Execution capability differences",
                    "Known limitations", "Compatibility checks"]
ADAPTER_KEYS = ["adapter", "platform", "status", "tested_versions", "project_skill_dir", "user_skill_dir",
                "invocation", "extra_frontmatter", "docs", "docs_checked_on", "evaluation_reports"]
REGISTRY_KEYS = ["id", "title", "edition", "kind", "verification_status", "verification_note", "official_source",
                 "verified_on", "usage_area", "workflow_mapping", "verified_clauses", "license_note", "limitations"]
TEMPLATE_FOR = {"defect-candidates.md": "defect-report.md"}
SCAN_EXCLUDE = {".git", "dist", "__pycache__", ".venv", "node_modules"}
# Synthetic canaries used by evaluation fixtures are not secrets.
SECRET_ALLOW = re.compile(r"STLCCANARY|tok-(alice|bob|admin)")
SENSITIVE_NAMES = re.compile(r"(^|/)(\.env(\..*)?|.*\.pem|.*\.key|id_rsa|id_ed25519|credentials\.json)$")


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def error(self, where: str, msg: str) -> None:
        self.items.append({"level": "ERROR", "where": where, "message": msg})

    def warn(self, where: str, msg: str) -> None:
        self.items.append({"level": "WARN", "where": where, "message": msg})


def parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal parser for the flat frontmatter used by SKILL.md (scalars, '>' folded blocks, one nested map)."""
    if not text.startswith("---\n"):
        return {}
    block = text[4:].split("\n---\n", 1)[0]
    data: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if not line.startswith(" "):
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip()
        elif key:
            data[key] = (data[key] + " " + line.strip()).strip()
    for k, v in data.items():
        if v.startswith(">") or v.startswith("|"):
            data[k] = v[1:].strip()
    return data


def check_structure(r: Report) -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            r.error(rel, "required file missing")
    for rel in REQUIRED_DIRS:
        if not (ROOT / rel).is_dir():
            r.error(rel, "required directory missing")


def check_skill(r: Report) -> str | None:
    path = SKILL / "SKILL.md"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    name, desc = fm.get("name", ""), fm.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        r.error("SKILL.md", f"name '{name}' violates Agent Skills naming (lowercase, hyphens, <=64)")
    if name != SKILL.name:
        r.error("SKILL.md", f"name '{name}' must match directory '{SKILL.name}'")
    if not 1 <= len(desc) <= 1024:
        r.error("SKILL.md", f"description length {len(desc)} must be 1..1024")
    lines = text.count("\n") + 1
    if lines >= 500:
        r.error("SKILL.md", f"{lines} lines; keep under 500 (progressive disclosure, NFR-06)")
    headings = re.findall(r"^##\s+\d*\.?\s*(.+)$", text, re.M)
    for section in SKILL_SECTIONS:
        if not any(h.lower().startswith(section.lower()) for h in headings):
            r.error("SKILL.md", f"missing section '{section}' (PRD §11)")
    m = re.search(r'version:\s*"?([\d.]+[^"\s]*)', text)
    return m.group(1) if m else None


def check_links(r: Report) -> None:
    for md in [SKILL / "SKILL.md", *SKILL.joinpath("references").glob("*.md"), *ROOT.joinpath("docs").glob("*.md"),
               ROOT / "README.md", *ROOT.joinpath("adapters").rglob("README.md")]:
        if not md.is_file():
            continue
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", md.read_text(encoding="utf-8")):
            if re.match(r"^[a-z]+:", target):
                continue
            if not (md.parent / target).exists():
                r.error(str(md.relative_to(ROOT)), f"broken link: {target}")


def check_templates(r: Report) -> None:
    tdir = SKILL / "templates"
    for artifact, headings in va.REQUIRED_HEADINGS.items():
        template = tdir / TEMPLATE_FOR.get(artifact, artifact)
        if not template.is_file():
            r.error(f"templates/{template.name}", f"template for {artifact} missing")
            continue
        found = {h.strip().lower() for h in re.findall(r"^#{1,6}\s+(.+?)\s*$", template.read_text(encoding="utf-8"), re.M)}
        for h in headings:
            if not any(f.startswith(h.lower()) for f in found):
                r.error(f"templates/{template.name}", f"missing heading '{h}' required by the validator")
    for name, columns in [("traceability-matrix.csv", va.TRACE_COLUMNS), ("risk-register.csv", va.RISK_COLUMNS)]:
        header = (tdir / name).read_text(encoding="utf-8").splitlines()[0].split(",") if (tdir / name).is_file() else []
        if header != columns:
            r.error(f"templates/{name}", "header does not match validator columns")
    tc = (tdir / "test-cases.md").read_text(encoding="utf-8") if (tdir / "test-cases.md").is_file() else ""
    for field in va.TEST_CASE_FIELDS:
        if f"**{field}:**" not in tc:
            r.error("templates/test-cases.md", f"missing field {field}")


def check_registry(r: Report) -> None:
    path = SKILL / "references" / "standards-registry.json"
    try:
        reg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        r.error("standards-registry.json", f"unreadable: {exc}")
        return
    md = (SKILL / "references" / "standards-registry.md").read_text(encoding="utf-8")
    for e in reg.get("entries", []):
        where = f"standards-registry.json:{e.get('id')}"
        for k in REGISTRY_KEYS:
            if k not in e:
                r.error(where, f"missing field '{k}' (FR-11)")
        status = e.get("verification_status")
        if status not in {"verified", "partially_verified", "unverified"}:
            r.error(where, f"invalid verification_status {status!r}")
        if status == "verified" and not (e.get("verified_on") and e.get("official_source")):
            r.error(where, "verified entries need verified_on and official_source")
        if e.get("verified_clauses") and status != "verified":
            r.error(where, "clauses may only be listed for verified entries")
        if e.get("id") and f"| {e['id']} |" not in md:
            r.error("standards-registry.md", f"table lacks entry {e['id']}")
        if status != "verified":
            r.warn(where, "edition/status not verified; re-verify before release (docs/release-checklist.md)")


def check_adapters(r: Report) -> None:
    for d in sorted((ROOT / "adapters").iterdir()):
        if not d.is_dir():
            continue
        where = f"adapters/{d.name}"
        try:
            cfg = json.loads((d / "adapter.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            r.error(where, f"adapter.json unreadable: {exc}")
            continue
        for k in ADAPTER_KEYS:
            if k not in cfg:
                r.error(where, f"adapter.json missing '{k}'")
        if cfg.get("status") not in {"experimental", "supported"}:
            r.error(where, "status must be experimental or supported")
        if cfg.get("status") == "supported" and not (cfg.get("tested_versions") and cfg.get("evaluation_reports")):
            r.error(where, "supported requires tested_versions and evaluation_reports (AC-09)")
        readme = (d / "README.md").read_text(encoding="utf-8") if (d / "README.md").is_file() else ""
        for section in ADAPTER_SECTIONS:
            if not re.search(rf"^##\s+{re.escape(section)}", readme, re.M):
                r.error(where, f"README missing section '{section}' (FR-12)")


def check_versions(r: Report, skill_version: str | None) -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").is_file() else None
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8") if (ROOT / "CHANGELOG.md").is_file() else ""
    top = re.search(r"^##\s+\[?(\d+\.\d+\.\d+[^\]\s]*)", changelog, re.M)
    for label, value in [("SKILL.md metadata.version", skill_version), ("validate_artifacts.SKILL_VERSION", va.SKILL_VERSION),
                         ("CHANGELOG top entry", top.group(1) if top else None)]:
        if value != version:
            r.error("VERSION", f"{label} is {value!r}, VERSION is {version!r}")
    if version and not re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?", version):
        r.error("VERSION", "not a semantic version")


def iter_repo_files():
    for f in sorted(ROOT.rglob("*")):
        rel = f.relative_to(ROOT)
        if f.is_file() and not SCAN_EXCLUDE.intersection(rel.parts):
            yield f, rel.as_posix()


def check_secrets_and_claims(r: Report) -> None:
    for f, rel in iter_repo_files():
        if f.suffix.lower() not in va.TEXT_SUFFIXES | {".toml", ".ini", ".cfg", ".sh"} or f.stat().st_size > 2_000_000:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            if SECRET_ALLOW.search(line):
                continue
            for label, pattern in va.SECRET_PATTERNS:
                if pattern.search(line):
                    r.error(f"{rel}:{n}", f"possible {label} committed to the repository; remove and ROTATE it")
            if rel.endswith(".md") and va.COMPLIANCE_CLAIM.search(line) and not va.NEGATION.search(line):
                r.error(f"{rel}:{n}", "unsupported ISO compliance/certification claim")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8") if (ROOT / ".gitignore").is_file() else ""
    for pattern in [".env", "*.pem", "*.key", "dist/"]:
        if pattern not in gitignore:
            r.error(".gitignore", f"should ignore '{pattern}'")
    try:
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        r.warn("git", "not a git repository; committed-file checks skipped")
        return
    for rel in tracked:
        if SENSITIVE_NAMES.search(rel) and not rel.startswith("tests/fixtures/"):
            r.error(rel, "sensitive file is tracked by git; remove it from history and rotate any secret in it")


def check_dependencies(r: Report) -> None:
    reqs = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8") if (ROOT / "requirements-dev.txt").is_file() else ""
    licenses = (ROOT / "docs" / "third-party-licenses.md").read_text(encoding="utf-8") \
        if (ROOT / "docs" / "third-party-licenses.md").is_file() else ""
    for line in reqs.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.match(r"^([A-Za-z0-9_.-]+)==([\w.]+)$", line)
        if not m:
            r.error("requirements-dev.txt", f"'{line}' must be pinned as name==version")
            continue
        if f"| {m.group(1)} |" not in licenses:
            r.error("docs/third-party-licenses.md", f"{m.group(1)} has no reviewed license entry")


def run() -> Report:
    r = Report()
    check_structure(r)
    skill_version = check_skill(r)
    check_links(r)
    check_templates(r)
    check_registry(r)
    check_adapters(r)
    check_versions(r, skill_version)
    check_secrets_and_claims(r)
    check_dependencies(r)
    return r


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = run()
    errors = [i for i in report.items if i["level"] == "ERROR"]
    if args.json:
        print(json.dumps({"valid": not errors, "items": report.items}, indent=2))
    else:
        for i in report.items:
            print(f"{i['level']:5} {i['where']}: {i['message']}")
        print(f"\n{'INVALID' if errors else 'VALID'}: {len(errors)} error(s), "
              f"{len(report.items) - len(errors)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
