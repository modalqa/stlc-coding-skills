#!/usr/bin/env python3
"""Package and install the stlc-engineer skill for each adapter.

    python3 scripts/package_skill.py build [--out dist]
    python3 scripts/package_skill.py install --adapter claude-code --project /path/to/repo [--force] [--dry-run]
    python3 scripts/package_skill.py install --adapter cursor --user
    python3 scripts/package_skill.py verify  --adapter claude-code --project /path/to/repo

`build` writes a versioned zip of the core skill plus one install tree per
adapter, with SHA-256 checksums. `install` never overwrites an existing
installation silently: without --force it refuses; with --force it first moves
the old copy to a timestamped backup next to it.

Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "stlc-engineer"
SKILL_DIR = ROOT / "skills" / SKILL_NAME
ADAPTERS_DIR = ROOT / "adapters"
EXCLUDE = {"__pycache__", ".DS_Store"}


def version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def load_adapter(name: str) -> dict:
    path = ADAPTERS_DIR / name / "adapter.json"
    if not path.is_file():
        known = sorted(p.name for p in ADAPTERS_DIR.iterdir() if (p / "adapter.json").is_file())
        raise SystemExit(f"unknown adapter '{name}'; available: {', '.join(known)}")
    return json.loads(path.read_text(encoding="utf-8"))


def skill_files() -> list[Path]:
    return sorted(p for p in SKILL_DIR.rglob("*")
                  if p.is_file() and not EXCLUDE.intersection(p.relative_to(SKILL_DIR).parts) and p.suffix != ".pyc")


def render_skill_md(adapter: dict) -> str:
    """Core SKILL.md with the adapter's extra frontmatter appended (core keys are never changed)."""
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    extra = adapter.get("extra_frontmatter") or {}
    if not extra:
        return text
    head, sep, body = text[4:].partition("\n---\n")
    if not text.startswith("---\n") or not sep:
        raise SystemExit("SKILL.md frontmatter not found")
    core_keys = {line.split(":", 1)[0] for line in head.splitlines() if line and not line.startswith(" ")}
    clash = core_keys.intersection(extra)
    if clash:
        raise SystemExit(f"adapter may not override core frontmatter keys: {sorted(clash)}")
    lines = [f"{k}: {json.dumps(v)}" for k, v in extra.items()]
    return "---\n" + head + "\n" + "\n".join(lines) + "\n---\n" + body


def write_tree(target: Path, adapter: dict) -> list[str]:
    written = []
    for src in skill_files():
        rel = src.relative_to(SKILL_DIR)
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel.as_posix() == "SKILL.md":
            dst.write_text(render_skill_md(adapter), encoding="utf-8")
        else:
            shutil.copy2(src, dst)
        written.append(rel.as_posix())
    return written


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(out: Path) -> None:
    ver = version()
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / f"{SKILL_NAME}-{ver}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src in skill_files():
            info = zipfile.ZipInfo(f"{SKILL_NAME}/{src.relative_to(SKILL_DIR).as_posix()}", date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, src.read_bytes())  # fixed timestamps -> reproducible archive
    sums = [f"{sha256(zip_path)}  {zip_path.name}"]
    for adapter_dir in sorted(p for p in ADAPTERS_DIR.iterdir() if (p / "adapter.json").is_file()):
        adapter = load_adapter(adapter_dir.name)
        tree = out / "adapters" / adapter_dir.name / adapter["project_skill_dir"] / SKILL_NAME
        if tree.exists():
            shutil.rmtree(tree)
        write_tree(tree, adapter)
        print(f"adapter tree: {tree.relative_to(out)}")
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"archive: {zip_path}\nchecksum: {sums[0]}")


def target_dir(adapter: dict, project: Path | None, user: bool) -> Path:
    if user:
        return Path(adapter["user_skill_dir"]).expanduser() / SKILL_NAME
    if project is None:
        raise SystemExit("pass --project DIR or --user")
    if not project.is_dir():
        raise SystemExit(f"project directory does not exist: {project}")
    return project / adapter["project_skill_dir"] / SKILL_NAME


def install(adapter_name: str, project: Path | None, user: bool, force: bool, dry_run: bool) -> Path:
    adapter = load_adapter(adapter_name)
    target = target_dir(adapter, project, user)
    if target.exists():
        if not force:
            raise SystemExit(f"{target} already exists; re-run with --force to replace it (a backup is kept)")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = target.with_name(f"{SKILL_NAME}.bak-{stamp}")
        print(f"{'would move' if dry_run else 'moving'} existing install to {backup}")
        if not dry_run:
            target.rename(backup)
    if dry_run:
        print(f"would install {len(skill_files())} files into {target}")
        return target
    files = write_tree(target, adapter)
    print(f"installed {len(files)} files into {target} (adapter {adapter_name}, status {adapter['status']})")
    if adapter["status"] != "supported":
        print(f"note: adapter '{adapter_name}' is {adapter['status']}; the behavioral suite has not been "
              f"confirmed on this platform (see adapters/{adapter_name}/README.md)")
    return target


def verify(adapter_name: str, project: Path | None, user: bool) -> int:
    adapter = load_adapter(adapter_name)
    target = target_dir(adapter, project, user)
    problems = []
    for src in skill_files():
        rel = src.relative_to(SKILL_DIR)
        dst = target / rel
        if not dst.is_file():
            problems.append(f"missing {rel}")
            continue
        expected = render_skill_md(adapter).encode() if rel.as_posix() == "SKILL.md" else src.read_bytes()
        if dst.read_bytes() != expected:
            problems.append(f"differs from core: {rel}")
    for p in problems:
        print(p)
    print(f"{'OK' if not problems else 'MISMATCH'}: {target}")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build")
    p.add_argument("--out", type=Path, default=ROOT / "dist")
    for name in ("install", "verify"):
        p = sub.add_parser(name)
        p.add_argument("--adapter", required=True)
        group = p.add_mutually_exclusive_group(required=True)
        group.add_argument("--project", type=Path)
        group.add_argument("--user", action="store_true")
        if name == "install":
            p.add_argument("--force", action="store_true")
            p.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd == "build":
        build(args.out)
        return 0
    if args.cmd == "install":
        install(args.adapter, args.project, args.user, args.force, args.dry_run)
        return 0
    return verify(args.adapter, args.project, args.user)


if __name__ == "__main__":
    sys.exit(main())
