"""Shared helpers for the evaluation test-suite."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "stlc-engineer"
EXPECTED = ROOT / "tests" / "expected"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "scripts"))

import validate_artifacts as va  # noqa: E402

GOLDEN_PASS = next((EXPECTED / "business-rules" / "good-run").glob("RUN-*"))
GOLDEN_BLOCKED = next((EXPECTED / "missing-environment" / "good-run").glob("RUN-*"))


class RunCopy:
    """Context manager: temporary writable copy of a golden run directory."""

    def __init__(self, source: Path) -> None:
        self.source = source

    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / self.source.name
        shutil.copytree(self.source, self.path)
        return self.path

    def __exit__(self, *exc) -> None:
        self._tmp.cleanup()


def codes(run_dir: Path, phase: int | None = 6, level: str = "ERROR") -> set[str]:
    return {f.code for f in va.validate(run_dir, phase) if f.level == level}


def edit_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def replace_in(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not in {path.name}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
