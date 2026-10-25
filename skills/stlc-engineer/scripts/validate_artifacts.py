#!/usr/bin/env python3
"""Deterministic validator for STLC run artifacts.

Checks structure, identifiers, traceability, execution-status consistency,
closure-report honesty, and leaked secrets in one run directory. It does NOT
judge whether the testing itself was good; that remains a human/agent task.

Standard library only, so it runs wherever the skill is installed.

Usage:
    python3 validate_artifacts.py <run_dir> [--phase N] [--json] [--strict]
                                  [--risk-formula product|none]

Exit codes: 0 = no errors, 1 = errors (or warnings with --strict), 2 = usage.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

SKILL_VERSION = "0.1.0"

RESULT_STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN", "INCONCLUSIVE"}
MATRIX_STATUSES = RESULT_STATUSES | {"PENDING"}
RESULT_ORIGINS = {"this_run", "previous_run", "not_executed"}
FAILURE_CATEGORIES = {
    "product_defect_candidate",
    "test_implementation_defect",
    "environment_failure",
    "test_data_problem",
    "dependency_failure",
    "flaky",
    "inconclusive",
}
GATE_STATUSES = {"PASSED", "PASSED_WITH_LIMITATIONS", "BLOCKED", "NOT_EVALUATED"}
PHASE_STATUSES = {"NOT_STARTED", "IN_PROGRESS", "COMPLETED", "BLOCKED", "SKIPPED"}
RECOMMENDATIONS = {"READY", "READY_WITH_RISKS", "NOT_READY"}
CLOSURE_STATUSES = {"COMPLETE", "INCOMPLETE", "BLOCKED"}
LEVELS = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
HIGH_LEVELS = {"CRITICAL", "HIGH"}
AUTOMATION_STATUSES = {"AUTOMATED", "TO_AUTOMATE", "MANUAL", "NOT_AUTOMATABLE"}
DEFECT_STATUSES = {"OPEN", "CONFIRMED", "REJECTED", "FIXED_PENDING_RETEST", "CLOSED"}
OPEN_DEFECT_STATUSES = {"OPEN", "CONFIRMED", "FIXED_PENDING_RETEST"}
LINK_PLACEHOLDERS = {"GAP", "N/A"}

ID_PATTERNS = {
    "requirement": re.compile(r"^REQ-\d{3,}$"),
    "assumption": re.compile(r"^ASM-\d{3,}$"),
    "risk": re.compile(r"^RISK-\d{3,}$"),
    "condition": re.compile(r"^TCOND-\d{3,}$"),
    "test_case": re.compile(r"^TC-\d{3,}$"),
    "defect": re.compile(r"^DEF-\d{3,}$"),
}
RUN_ID_PATTERN = re.compile(r"^RUN-\d{8}T\d{6}Z(-[A-Za-z0-9]+)?$")
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}]*\}\}")

# Artifacts introduced by each phase; validation is cumulative up to --phase.
PHASE_ARTIFACTS: dict[int, list[str]] = {
    1: ["run-manifest.json", "requirements-analysis.md", "assumptions.md",
        "initial-risk-register.md", "traceability-matrix.csv"],
    2: ["test-approach.md", "risk-register.csv", "test-plan.md"],
    3: ["test-cases.md", "test-data-plan.md"],
    4: ["test-inventory.md"],
    5: ["execution-results.json", "test-execution-report.md", "defect-candidates.md"],
    6: ["test-closure-report.md", "residual-risk-register.md", "release-readiness.md"],
}

# Headings each Markdown artifact must contain (case-insensitive, any level).
REQUIRED_HEADINGS: dict[str, list[str]] = {
    "requirements-analysis.md": ["Context Summary", "Requirements", "Ambiguities and Testability Gaps"],
    "assumptions.md": ["Assumptions"],
    "initial-risk-register.md": ["Preliminary Risks"],
    "test-approach.md": ["Test Levels and Types", "Techniques"],
    "test-plan.md": ["Scope", "Out of Scope", "Entry Criteria", "Exit Criteria",
                     "Environment", "Test Data", "Execution Order", "Untestable Risks"],
    "test-cases.md": ["Test Cases"],
    "test-data-plan.md": ["Test Data"],
    "test-inventory.md": ["Test Inventory", "Execution Instructions"],
    "test-execution-report.md": ["Execution Summary", "Commands", "Failure Analysis"],
    "defect-candidates.md": ["Defect Candidates"],
    "test-closure-report.md": ["Execution Summary", "Requirement Coverage", "Risk Coverage",
                               "Defect Summary", "Exit Criteria Evaluation", "Residual Risks",
                               "Limitations and Evidence Gaps", "Recommendation"],
    "residual-risk-register.md": ["Residual Risks"],
    "release-readiness.md": ["Recommendation"],
}

TRACE_COLUMNS = ["requirement_id", "requirement_priority", "risk_ids", "test_condition_id",
                 "test_case_id", "execution_status", "defect_ids", "closure_decision", "notes"]
RISK_COLUMNS = ["risk_id", "requirement_ids", "description", "category",
                "quality_characteristic", "likelihood", "impact", "score", "level",
                "rationale", "mitigation", "test_case_ids", "residual_status"]
TEST_CASE_FIELDS = ["test_case_id", "requirement_ids", "risk_ids", "title", "objective",
                    "preconditions", "test_data", "steps", "expected_result", "test_level",
                    "test_type", "design_technique", "automation_status", "priority"]
RESULT_FIELDS = ["run_id", "test_case_id", "status", "result_origin", "started_at",
                 "finished_at", "command", "exit_code", "environment", "evidence_refs",
                 "failure_category", "notes"]
DEFECT_FIELDS = ["title", "related_test_case_ids", "failure_category", "severity",
                 "status", "evidence_refs", "reproduction", "hypothesis"]

# Secret detectors. Values are never echoed back; only the location is reported.
SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws_access_key_id", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("github_fine_grained_token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b")),
    ("slack_token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY")),
    ("anthropic_api_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("openai_api_key", re.compile(r"\bsk-(proj-)?[A-Za-z0-9]{32,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("credential_in_url", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s:@]{3,}@")),
    ("generic_secret_assignment", re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\b"
        r"\s*[:=]\s*['\"]?(?!<redacted>|\*{3}|REDACTED|\$\{|\{\{|changeme\b|example\b|none\b|null\b)"
        r"[^\s'\"]{8,}")),
]
TEXT_SUFFIXES = {".md", ".csv", ".json", ".txt", ".log", ".yaml", ".yml", ".xml", ".html", ".py", ""}

COMPLIANCE_CLAIM = re.compile(
    r"(?i)\b(iso[- /]?(\d{4,5}[- ]?)?(compliant|certified)|certified (to|against) iso|"
    r"(fully |is |are )compliant with iso)")
NEGATION = re.compile(r"(?i)\b(not|no|never|without|does not|doesn't|cannot)\b")
CLAUSE_REFERENCE = re.compile(r"(?i)\b(clause|§)\s*\d+(\.\d+)*")


@dataclass
class Finding:
    level: str  # ERROR | WARN
    code: str
    file: str
    message: str


class Validator:
    def __init__(self, run_dir: Path, phase: int | None, risk_formula: str) -> None:
        self.run_dir = run_dir
        self.requested_phase = phase
        self.risk_formula = risk_formula
        self.findings: list[Finding] = []
        self.manifest: dict = {}
        self.requirement_ids: set[str] = set()
        self.risk_ids: set[str] = set()
        self.test_cases: dict[str, dict[str, str]] = {}
        self.defects: dict[str, dict[str, str]] = {}
        self.results: list[dict] = []
        self.trace_rows: list[dict[str, str]] = []

    # -- helpers ---------------------------------------------------------
    def error(self, code: str, file: str, message: str) -> None:
        self.findings.append(Finding("ERROR", code, file, message))

    def warn(self, code: str, file: str, message: str) -> None:
        self.findings.append(Finding("WARN", code, file, message))

    def path(self, name: str) -> Path:
        return self.run_dir / name

    def read_text(self, name: str) -> str | None:
        p = self.path(name)
        if not p.is_file():
            return None
        return p.read_text(encoding="utf-8", errors="replace")

    def read_csv(self, name: str, columns: list[str]) -> list[dict[str, str]]:
        text = self.read_text(name)
        if text is None:
            return []
        reader = csv.DictReader(text.splitlines())
        header = reader.fieldnames or []
        missing = [c for c in columns if c not in header]
        if missing:
            self.error("csv_columns", name, f"missing columns: {', '.join(missing)}")
            return []
        rows = []
        for i, row in enumerate(reader, start=2):
            clean = {k: (v or "").strip() for k, v in row.items() if k is not None}
            if not any(clean.values()):
                continue
            clean["_line"] = str(i)
            rows.append(clean)
        return rows

    @staticmethod
    def split_ids(value: str) -> list[str]:
        return [v.strip() for v in re.split(r"[;,]", value or "") if v.strip()]

    def check_id_list(self, value: str, kind: str, file: str, where: str,
                      known: set[str] | None = None, allow_placeholder: bool = True) -> list[str]:
        ids = self.split_ids(value)
        if not ids:
            self.error("empty_link", file, f"{where}: empty {kind} link; use GAP or N/A with a note")
            return []
        out = []
        for item in ids:
            if item in LINK_PLACEHOLDERS:
                if not allow_placeholder:
                    self.error("bad_id", file, f"{where}: {item} not allowed for {kind}")
                continue
            if not ID_PATTERNS[kind].match(item):
                self.error("bad_id", file, f"{where}: '{item}' is not a valid {kind} ID")
                continue
            if known is not None and item not in known:
                self.error("unknown_id", file, f"{where}: {kind} '{item}' is not defined in its source artifact")
            out.append(item)
        return out

    @staticmethod
    def parse_time(value: object) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else None

    # -- phase resolution ------------------------------------------------
    def resolve_phase(self) -> int:
        if self.requested_phase is not None:
            return self.requested_phase
        phase = self.manifest.get("current_phase")
        return phase if isinstance(phase, int) and 1 <= phase <= 6 else 1

    # -- checks ----------------------------------------------------------
    def check_manifest(self) -> None:
        name = "run-manifest.json"
        text = self.read_text(name)
        if text is None:
            return  # reported by presence check
        try:
            self.manifest = json.loads(text)
        except json.JSONDecodeError as exc:
            self.error("invalid_json", name, f"cannot parse: {exc}")
            return
        m = self.manifest
        for key in ["run_id", "skill_version", "created_at", "context", "current_phase", "phases", "activities"]:
            if key not in m:
                self.error("manifest_field", name, f"missing '{key}'")
        if "run_id" in m and not RUN_ID_PATTERN.match(str(m["run_id"])):
            self.error("run_id", name, f"run_id '{m['run_id']}' does not match RUN-YYYYMMDDTHHMMSSZ")
        if m.get("run_id") and self.run_dir.name != m["run_id"]:
            self.warn("run_dir_name", name, f"run directory name '{self.run_dir.name}' differs from run_id")
        if "created_at" in m and self.parse_time(m["created_at"]) is None:
            self.error("timestamp", name, "created_at must be ISO-8601 with timezone")
        ctx = m.get("context", {})
        if isinstance(ctx, dict):
            for key in ["repository", "git_commit", "git_dirty", "discovered_test_commands"]:
                if key not in ctx:
                    self.error("manifest_field", name, f"context missing '{key}' (use null if unknown)")
        phases = m.get("phases", [])
        if not isinstance(phases, list):
            self.error("manifest_field", name, "phases must be a list")
            phases = []
        seen = set()
        for entry in phases:
            num = entry.get("phase")
            if num in seen:
                self.error("manifest_phase", name, f"phase {num} listed twice")
            seen.add(num)
            if entry.get("status") not in PHASE_STATUSES:
                self.error("manifest_phase", name, f"phase {num}: status must be one of {sorted(PHASE_STATUSES)}")
            if entry.get("gate_status") not in GATE_STATUSES:
                self.error("manifest_phase", name, f"phase {num}: gate_status must be one of {sorted(GATE_STATUSES)}")
            if entry.get("gate_status") in {"BLOCKED", "PASSED_WITH_LIMITATIONS"} and not entry.get("notes"):
                self.error("manifest_phase", name, f"phase {num}: {entry.get('gate_status')} gate requires notes")
        if not isinstance(m.get("activities", []), list):
            self.error("manifest_field", name, "activities must be a list")

    def check_presence(self, phase: int) -> None:
        for p in range(1, phase + 1):
            for name in PHASE_ARTIFACTS[p]:
                f = self.path(name)
                if not f.is_file():
                    self.error("missing_artifact", name, f"required by phase {p}")
                elif f.stat().st_size == 0:
                    self.error("empty_artifact", name, "file is empty")
        if phase >= 5 and not self.path("evidence").is_dir():
            self.error("missing_artifact", "evidence/", "evidence directory required by phase 5")
        recorded = {e.get("phase"): e for e in self.manifest.get("phases", []) if isinstance(e, dict)}
        for p in range(1, phase):
            entry = recorded.get(p)
            if entry is None:
                self.error("gate_not_recorded", "run-manifest.json", f"phase {p} gate not recorded")
            elif entry.get("gate_status") == "NOT_EVALUATED":
                self.error("gate_not_recorded", "run-manifest.json",
                           f"phase {p} gate is NOT_EVALUATED but validation targets phase {phase}")

    def check_markdown(self, phase: int) -> None:
        for p in range(1, phase + 1):
            for name in PHASE_ARTIFACTS[p]:
                if not name.endswith(".md"):
                    continue
                text = self.read_text(name)
                if text is None:
                    continue
                headings = {h.strip().lower() for h in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M)}
                for required in REQUIRED_HEADINGS.get(name, []):
                    if not any(h == required.lower() or h.startswith(required.lower()) for h in headings):
                        self.error("missing_section", name, f"missing heading '{required}'")
        for f in self.iter_text_files():
            rel = f.relative_to(self.run_dir).as_posix()
            if rel.startswith("evidence/"):
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            if PLACEHOLDER_PATTERN.search(text):
                self.error("unfilled_placeholder", rel, "template placeholder {{...}} left in artifact")

    def check_requirements(self) -> None:
        name = "requirements-analysis.md"
        text = self.read_text(name) or ""
        self.requirement_ids = set(re.findall(r"\bREQ-\d{3,}\b", text))
        if not self.requirement_ids:
            self.error("no_requirements", name, "no REQ-NNN identifiers defined")

    def check_risk_register(self) -> None:
        name = "risk-register.csv"
        rows = self.read_csv(name, RISK_COLUMNS)
        for row in rows:
            where = f"line {row['_line']}"
            rid = row["risk_id"]
            if not ID_PATTERNS["risk"].match(rid):
                self.error("bad_id", name, f"{where}: invalid risk_id '{rid}'")
                continue
            if rid in self.risk_ids:
                self.error("duplicate_id", name, f"{where}: duplicate {rid}")
            self.risk_ids.add(rid)
            self.check_id_list(row["requirement_ids"], "requirement", name, where, self.requirement_ids)
            try:
                likelihood, impact, score = int(row["likelihood"]), int(row["impact"]), int(row["score"])
            except ValueError:
                self.error("risk_score", name, f"{where}: likelihood, impact, score must be integers")
            else:
                if min(likelihood, impact) < 1:
                    self.error("risk_score", name, f"{where}: likelihood and impact must be >= 1")
                if self.risk_formula == "product" and score != likelihood * impact:
                    self.error("risk_score", name, f"{where}: score {score} != likelihood x impact "
                                                   f"({likelihood * impact}); use --risk-formula none "
                                                   f"if the project policy defines another model")
            if row["level"] not in LEVELS:
                self.error("risk_level", name, f"{where}: level must be one of {sorted(LEVELS)}")
            if not row["rationale"]:
                self.error("risk_rationale", name, f"{where}: rationale is required")
        if not rows and self.path(name).is_file():
            self.error("empty_register", name, "risk register has no risks")

    def parse_blocks(self, name: str, heading_id: re.Pattern[str]) -> dict[str, dict[str, str]]:
        """Parse '### <ID> ...' blocks with '- **field:** value' lines (values may wrap)."""
        text = self.read_text(name) or ""
        blocks: dict[str, dict[str, str]] = {}
        current: dict[str, str] | None = None
        field: str | None = None
        for line in text.splitlines():
            head = re.match(r"^#{1,6}\s+(\S+)", line)
            if head:
                ident = head.group(1).rstrip(":")
                if heading_id.match(ident):
                    if ident in blocks:
                        self.error("duplicate_id", name, f"{ident} defined twice")
                    current = blocks[ident] = {}
                else:
                    current = None  # any other heading ends the current block
                field = None
                continue
            if current is None:
                continue
            m = re.match(r"^\s*[-*]\s+\*\*([a-z_]+):\*\*\s*(.*)$", line) or \
                re.match(r"^\s*[-*]\s+([a-z_]+):\s+(.*)$", line)
            if m:
                field = m.group(1)
                current[field] = m.group(2).strip()
            elif field and line.strip():
                current[field] = (current[field] + "\n" + line.strip()).strip()
        return blocks

    def check_test_cases(self) -> None:
        name = "test-cases.md"
        self.test_cases = self.parse_blocks(name, ID_PATTERNS["test_case"])
        if not self.test_cases and self.path(name).is_file():
            self.error("no_test_cases", name, "no '### TC-NNN' test case blocks found")
        for tc_id, fields in self.test_cases.items():
            missing = [f for f in TEST_CASE_FIELDS if f != "test_case_id" and not fields.get(f)]
            if missing:
                self.error("test_case_field", name, f"{tc_id}: missing {', '.join(missing)}")
            if fields.get("test_case_id") and fields["test_case_id"] != tc_id:
                self.error("test_case_field", name, f"{tc_id}: test_case_id field says {fields['test_case_id']}")
            self.check_id_list(fields.get("requirement_ids", ""), "requirement", name, tc_id,
                               self.requirement_ids, allow_placeholder=False)
            self.check_id_list(fields.get("risk_ids", ""), "risk", name, tc_id, self.risk_ids or None)
            if fields.get("priority") and fields["priority"] not in LEVELS:
                self.error("test_case_field", name, f"{tc_id}: priority must be one of {sorted(LEVELS)}")
            if fields.get("automation_status") and fields["automation_status"] not in AUTOMATION_STATUSES:
                self.error("test_case_field", name,
                           f"{tc_id}: automation_status must be one of {sorted(AUTOMATION_STATUSES)}")

    def check_traceability(self, phase: int) -> None:
        name = "traceability-matrix.csv"
        self.trace_rows = self.read_csv(name, TRACE_COLUMNS)
        if not self.trace_rows and self.path(name).is_file():
            self.error("empty_matrix", name, "traceability matrix has no rows")
        traced_reqs: set[str] = set()
        for row in self.trace_rows:
            where = f"line {row['_line']}"
            rid = row["requirement_id"]
            if not ID_PATTERNS["requirement"].match(rid):
                self.error("bad_id", name, f"{where}: invalid requirement_id '{rid}'")
            elif self.requirement_ids and rid not in self.requirement_ids:
                self.error("unknown_id", name, f"{where}: {rid} not defined in requirements-analysis.md")
            traced_reqs.add(rid)
            if row["requirement_priority"] not in LEVELS:
                self.error("trace_priority", name, f"{where}: requirement_priority must be one of {sorted(LEVELS)}")
            placeholders = [c for c in ("risk_ids", "test_condition_id", "test_case_id", "defect_ids")
                            if row[c] in LINK_PLACEHOLDERS]
            if placeholders and not row["notes"]:
                self.error("gap_without_reason", name, f"{where}: GAP/N/A in {', '.join(placeholders)} needs a note")
            self.check_id_list(row["risk_ids"], "risk", name, where, self.risk_ids if phase >= 2 else None)
            self.check_id_list(row["test_condition_id"], "condition", name, where)
            self.check_id_list(row["test_case_id"], "test_case", name, where,
                               set(self.test_cases) if phase >= 3 else None)
            self.check_id_list(row["defect_ids"], "defect", name, where,
                               set(self.defects) if phase >= 5 else None)
            if row["execution_status"] not in MATRIX_STATUSES:
                self.error("trace_status", name, f"{where}: execution_status must be one of {sorted(MATRIX_STATUSES)}")
            if not row["closure_decision"]:
                self.error("empty_link", name, f"{where}: closure_decision empty; use PENDING before closure")
        missing = self.requirement_ids - traced_reqs
        if missing:
            self.error("untraced_requirement", name, f"requirements absent from matrix: {', '.join(sorted(missing))}")
        if phase >= 3:
            for row in self.trace_rows:
                if row["requirement_priority"] in HIGH_LEVELS and row["test_case_id"] == "N/A":
                    self.error("high_priority_na", name,
                               f"line {row['_line']}: high-priority {row['requirement_id']} marked N/A; "
                               f"use GAP with justification or link a test case")
            linked = {self.split_ids(r["test_case_id"])[0] for r in self.trace_rows
                      if r["test_case_id"] not in LINK_PLACEHOLDERS and self.split_ids(r["test_case_id"])}
            orphan = set(self.test_cases) - linked
            if orphan:
                self.warn("orphan_test_case", name, f"test cases not linked to any requirement: {', '.join(sorted(orphan))}")

    def check_defects(self) -> None:
        name = "defect-candidates.md"
        self.defects = self.parse_blocks(name, ID_PATTERNS["defect"])
        for def_id, fields in self.defects.items():
            missing = [f for f in DEFECT_FIELDS if not fields.get(f)]
            if missing:
                self.error("defect_field", name, f"{def_id}: missing {', '.join(missing)}")
            if fields.get("failure_category") and fields["failure_category"] not in FAILURE_CATEGORIES:
                self.error("defect_field", name, f"{def_id}: unknown failure_category")
            if fields.get("status") and fields["status"] not in DEFECT_STATUSES:
                self.error("defect_field", name, f"{def_id}: status must be one of {sorted(DEFECT_STATUSES)}")
            if fields.get("severity") and fields["severity"] not in LEVELS:
                self.error("defect_field", name, f"{def_id}: severity must be one of {sorted(LEVELS)}")
            self.check_id_list(fields.get("related_test_case_ids", ""), "test_case", name, def_id,
                               set(self.test_cases), allow_placeholder=False)
            for ref in self.split_ids(fields.get("evidence_refs", "")):
                self.check_evidence_ref(ref, name, def_id)

    def check_evidence_ref(self, ref: str, file: str, where: str) -> None:
        candidate = (self.run_dir / ref).resolve()
        try:
            candidate.relative_to(self.run_dir.resolve())
        except ValueError:
            self.error("evidence_outside_run", file, f"{where}: evidence '{ref}' is outside the run directory")
            return
        if not candidate.exists():
            self.error("evidence_missing", file, f"{where}: evidence '{ref}' does not exist")

    def check_execution_results(self) -> None:
        name = "execution-results.json"
        text = self.read_text(name)
        if text is None:
            return
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            self.error("invalid_json", name, f"cannot parse: {exc}")
            return
        run_id = self.manifest.get("run_id")
        if data.get("run_id") != run_id:
            self.error("run_id_mismatch", name, f"run_id {data.get('run_id')!r} != manifest {run_id!r}")
        run_start = self.parse_time(self.manifest.get("created_at"))
        commands = data.get("commands", [])
        if not isinstance(commands, list):
            self.error("results_field", name, "commands must be a list")
            commands = []
        executed = set()
        for i, cmd in enumerate(commands):
            where = f"commands[{i}]"
            for key in ["command", "started_at", "finished_at", "exit_code", "log_ref"]:
                if key not in cmd:
                    self.error("results_field", name, f"{where}: missing '{key}'")
            if not isinstance(cmd.get("exit_code"), int):
                self.error("results_field", name, f"{where}: exit_code must be an integer for an executed command")
            if cmd.get("log_ref"):
                self.check_evidence_ref(cmd["log_ref"], name, where)
            self.check_times(cmd, name, where, run_start)
            if cmd.get("command"):
                executed.add(cmd["command"])
        results = data.get("results", [])
        if not isinstance(results, list) or not results:
            self.error("results_field", name, "results must be a non-empty list")
            return
        self.results = results
        for i, res in enumerate(results):
            tc = res.get("test_case_id", f"results[{i}]")
            where = f"{tc}"
            for key in RESULT_FIELDS:
                if key not in res:
                    self.error("results_field", name, f"{where}: missing '{key}' (use null if not applicable)")
            if res.get("run_id") != run_id:
                self.error("run_id_mismatch", name, f"{where}: run_id differs from manifest")
            if self.test_cases and tc not in self.test_cases:
                self.error("unknown_id", name, f"{where}: test case not defined in test-cases.md")
            status, origin = res.get("status"), res.get("result_origin")
            category, refs = res.get("failure_category"), res.get("evidence_refs") or []
            if status not in RESULT_STATUSES:
                self.error("bad_status", name, f"{where}: status {status!r} not in {sorted(RESULT_STATUSES)}")
                continue
            if origin not in RESULT_ORIGINS:
                self.error("bad_origin", name, f"{where}: result_origin must be one of {sorted(RESULT_ORIGINS)}")
            if status in {"PASS", "FAIL"}:
                if origin != "this_run":
                    self.error("unverified_verdict", name,
                               f"{where}: {status} requires result_origin 'this_run' (FR-07); "
                               f"reused results must be NOT_RUN or INCONCLUSIVE")
                if not res.get("command"):
                    self.error("unverified_verdict", name, f"{where}: {status} without the executed command")
                elif res["command"] not in executed:
                    self.error("unverified_verdict", name,
                               f"{where}: command not recorded in commands[] for this run")
                if not isinstance(res.get("exit_code"), int):
                    self.error("unverified_verdict", name, f"{where}: {status} requires an integer exit_code")
                if not refs:
                    self.error("unverified_verdict", name, f"{where}: {status} requires evidence_refs")
                self.check_times(res, name, where, run_start, required=True)
            if status == "PASS" and category:
                self.error("bad_category", name, f"{where}: PASS must have failure_category null")
            if status == "PASS" and isinstance(res.get("exit_code"), int) and res["exit_code"] != 0 and not res.get("notes"):
                self.warn("pass_nonzero_exit", name, f"{where}: PASS with non-zero exit_code needs an explanation in notes")
            if status in {"FAIL", "BLOCKED", "INCONCLUSIVE"} and category not in FAILURE_CATEGORIES:
                self.error("bad_category", name,
                           f"{where}: {status} requires failure_category in {sorted(FAILURE_CATEGORIES)}")
            if status in {"NOT_RUN", "BLOCKED", "INCONCLUSIVE"} and not res.get("notes"):
                self.error("missing_reason", name, f"{where}: {status} requires a reason in notes")
            if status == "NOT_RUN" and origin == "this_run":
                self.error("bad_origin", name, f"{where}: NOT_RUN cannot have result_origin 'this_run'")
            for ref in refs:
                self.check_evidence_ref(ref, name, where)
            if status == "FAIL" and category == "product_defect_candidate":
                linked = [d for d, f in self.defects.items() if tc in self.split_ids(f.get("related_test_case_ids", ""))]
                if not linked:
                    self.error("defect_not_logged", name, f"{where}: product_defect_candidate has no DEF entry")

    def check_times(self, rec: dict, file: str, where: str, run_start: datetime | None,
                    required: bool = True) -> None:
        start, end = self.parse_time(rec.get("started_at")), self.parse_time(rec.get("finished_at"))
        if required and (start is None or end is None):
            self.error("timestamp", file, f"{where}: started_at/finished_at must be ISO-8601 with timezone")
            return
        if start and end and end < start:
            self.error("timestamp", file, f"{where}: finished_at precedes started_at")
        if start and run_start and start < run_start:
            self.error("stale_result", file, f"{where}: started before this run was created; not a result of this run")

    def check_trace_vs_results(self) -> None:
        latest: dict[str, str] = {}
        for res in self.results:
            if res.get("test_case_id"):
                latest[res["test_case_id"]] = res.get("status", "")
        for row in self.trace_rows:
            tc = row["test_case_id"]
            if tc in LINK_PLACEHOLDERS:
                continue
            actual = latest.get(tc)
            if actual is None:
                if row["execution_status"] != "NOT_RUN":
                    self.error("status_mismatch", "traceability-matrix.csv",
                               f"line {row['_line']}: {tc} has no execution record; status must be NOT_RUN")
            elif row["execution_status"] != actual:
                self.error("status_mismatch", "traceability-matrix.csv",
                           f"line {row['_line']}: {tc} is {row['execution_status']} but execution-results says {actual}")

    def counts(self) -> dict[str, int]:
        latest: dict[str, str] = {}
        for res in self.results:
            latest[res.get("test_case_id", "")] = res.get("status", "")
        totals = {s: 0 for s in sorted(RESULT_STATUSES)}
        for status in latest.values():
            if status in totals:
                totals[status] += 1
        return totals

    def check_closure(self) -> None:
        name = "test-closure-report.md"
        text = self.read_text(name)
        if text is None:
            return
        rec = re.search(r"QA Recommendation:\**\s*`?\**\s*([A-Z_]+)", text)
        status = re.search(r"Closure Status:\**\s*`?\**\s*([A-Z_]+)", text)
        recommendation = rec.group(1) if rec else None
        if recommendation not in RECOMMENDATIONS:
            self.error("recommendation", name, f"'QA Recommendation:' must be one of {sorted(RECOMMENDATIONS)}")
        if not status or status.group(1) not in CLOSURE_STATUSES:
            self.error("closure_status", name, f"'Closure Status:' must be one of {sorted(CLOSURE_STATUSES)}")
        # Reported counts must equal the execution record.
        actual = self.counts()
        for s, n in actual.items():
            m = re.search(rf"^\|\s*`?{s}`?\s*\|\s*(\d+)\s*\|", text, re.M)
            if not m:
                self.error("count_missing", name, f"status table lacks a '| {s} | n |' row")
            elif int(m.group(1)) != n:
                self.error("count_mismatch", name, f"reports {s}={m.group(1)} but execution-results has {n}")
        if recommendation:
            self.check_recommendation(recommendation, name, actual)
        readiness = self.read_text("release-readiness.md") or ""
        rr = re.search(r"QA Recommendation:\**\s*`?\**\s*([A-Z_]+)", readiness)
        if rr and recommendation and rr.group(1) != recommendation:
            self.error("recommendation_mismatch", "release-readiness.md",
                       f"recommendation {rr.group(1)} differs from closure report {recommendation}")
        elif not rr:
            self.error("recommendation", "release-readiness.md", "missing 'QA Recommendation:' line")
        if "not a release approval" not in (text + readiness).lower():
            self.error("approval_disclaimer", name, "must state the recommendation is not a release approval")
        if status and status.group(1) == "COMPLETE":
            not_done = [e.get("phase") for e in self.manifest.get("phases", [])
                        if e.get("phase") != 6 and e.get("gate_status") in {"BLOCKED", "NOT_EVALUATED"}]
            if not_done:
                self.error("closure_status", name, f"COMPLETE while phase gates {not_done} are BLOCKED/NOT_EVALUATED")

    def check_recommendation(self, recommendation: str, name: str, counts: dict[str, int]) -> None:
        if counts.get("PASS", 0) == 0 and recommendation != "NOT_READY":
            self.error("recommendation_unsupported", name, "no test passed in this run; only NOT_READY is supported")
        if recommendation != "READY":
            return
        reasons = []
        latest = {r.get("test_case_id"): r for r in self.results}
        for tc, res in latest.items():
            prio = self.test_cases.get(tc, {}).get("priority", "")
            if prio in HIGH_LEVELS and res.get("status") != "PASS":
                reasons.append(f"{tc} ({prio}) is {res.get('status')}")
        open_defects = [d for d, f in self.defects.items()
                        if f.get("status") in OPEN_DEFECT_STATUSES and f.get("failure_category") == "product_defect_candidate"]
        if open_defects:
            reasons.append(f"open defect candidates {', '.join(open_defects)}")
        gaps = [r["requirement_id"] for r in self.trace_rows
                if r["requirement_priority"] in HIGH_LEVELS and r["test_case_id"] == "GAP"]
        if gaps:
            reasons.append(f"high-priority requirement gaps {', '.join(sorted(set(gaps)))}")
        if reasons:
            self.error("recommendation_unsupported", name, "READY not allowed: " + "; ".join(reasons))

    def iter_text_files(self):
        for f in sorted(self.run_dir.rglob("*")):
            if f.is_file() and f.suffix.lower() in TEXT_SUFFIXES and f.stat().st_size < 5_000_000:
                yield f

    def check_secrets_and_claims(self) -> None:
        for f in self.iter_text_files():
            rel = f.relative_to(self.run_dir).as_posix()
            for lineno, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for label, pattern in SECRET_PATTERNS:
                    if pattern.search(line):
                        self.error("secret_detected", rel, f"line {lineno}: possible {label}; redact the value")
                if rel.startswith("evidence/"):
                    continue
                if COMPLIANCE_CLAIM.search(line) and not NEGATION.search(line):
                    self.error("compliance_claim", rel, f"line {lineno}: unsupported ISO compliance/certification claim")
                if CLAUSE_REFERENCE.search(line) and re.search(r"(?i)\biso\b|29119|25010", line):
                    self.warn("clause_reference", rel,
                              f"line {lineno}: standard clause reference; confirm it is verified in the standards registry")

    # -- entry point -----------------------------------------------------
    def run(self) -> list[Finding]:
        if not self.run_dir.is_dir():
            self.error("run_dir", str(self.run_dir), "run directory does not exist")
            return self.findings
        self.check_manifest()
        phase = self.resolve_phase()
        if not 1 <= phase <= 6:
            self.error("phase", "-", "phase must be 1..6")
            return self.findings
        self.phase = phase
        self.check_presence(phase)
        self.check_markdown(phase)
        self.check_requirements()
        if phase >= 2:
            self.check_risk_register()
        if phase >= 3:
            self.check_test_cases()
        if phase >= 5:
            self.check_defects()
        self.check_traceability(phase)
        if phase >= 5:
            self.check_execution_results()
            self.check_trace_vs_results()
        if phase >= 6:
            self.check_closure()
        self.check_secrets_and_claims()
        return self.findings


def validate(run_dir: str | Path, phase: int | None = None, risk_formula: str = "product") -> list[Finding]:
    return Validator(Path(run_dir), phase, risk_formula).run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir")
    parser.add_argument("--phase", type=int, choices=range(1, 7), help="validate up to this phase (default: manifest current_phase)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--risk-formula", choices=["product", "none"], default="product")
    args = parser.parse_args(argv)

    validator = Validator(Path(args.run_dir), args.phase, args.risk_formula)
    findings = validator.run()
    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARN"]
    failed = bool(errors) or (args.strict and bool(warnings))
    if args.json:
        print(json.dumps({
            "validator_version": SKILL_VERSION,
            "run_dir": str(args.run_dir),
            "phase": getattr(validator, "phase", None),
            "valid": not failed,
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": [asdict(f) for f in findings],
        }, indent=2))
    else:
        for f in findings:
            print(f"{f.level:5} {f.code:28} {f.file}: {f.message}")
        print(f"\n{'INVALID' if failed else 'VALID'}: {len(errors)} error(s), {len(warnings)} warning(s) "
              f"[phase {getattr(validator, 'phase', '?')}]")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
