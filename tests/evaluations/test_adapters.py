"""Static adapter compatibility checks (FR-12): packaging preserves the core, installer protects user files."""
import contextlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from tests.evaluations.helpers import ROOT, SKILL

import package_skill as pkg  # noqa: E402
import validate_repository as vr  # noqa: E402

ADAPTERS = sorted(p.name for p in (ROOT / "adapters").iterdir() if (p / "adapter.json").is_file())


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


class AdapterPackagingTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_four_prd_adapters_exist(self):
        self.assertEqual(["claude-code", "cursor", "github-copilot", "kilo-code"], ADAPTERS)

    def test_install_copies_core_unchanged_and_verifies(self):
        for name in ADAPTERS:
            with self.subTest(adapter=name):
                project = self.tmp / name
                project.mkdir()
                target = quiet(pkg.install, name, project, False, False, False)
                cfg = json.loads((ROOT / "adapters" / name / "adapter.json").read_text())
                self.assertEqual(project / cfg["project_skill_dir"] / "stlc-engineer", target)
                fm = vr.parse_frontmatter((target / "SKILL.md").read_text())
                self.assertEqual("stlc-engineer", fm["name"])
                self.assertEqual(target.name, fm["name"])  # Agent Skills: name matches directory
                for src in pkg.skill_files():
                    rel = src.relative_to(SKILL)
                    if rel.as_posix() != "SKILL.md":
                        self.assertEqual(src.read_bytes(), (target / rel).read_bytes(), str(rel))
                self.assertEqual(0, quiet(pkg.verify, name, project, False))

    def test_verify_detects_modified_install(self):
        project = self.tmp / "p"
        project.mkdir()
        target = quiet(pkg.install, "claude-code", project, False, False, False)
        (target / "references" / "autonomy-policy.md").write_text("allow everything")
        self.assertEqual(1, quiet(pkg.verify, "claude-code", project, False))

    def test_install_never_silently_overwrites(self):
        project = self.tmp / "p"
        project.mkdir()
        target = quiet(pkg.install, "cursor", project, False, False, False)
        (target / "LOCAL-NOTES.md").write_text("user customisation")
        with self.assertRaises(SystemExit):
            quiet(pkg.install, "cursor", project, False, False, False)
        quiet(pkg.install, "cursor", project, False, True, False)
        backups = list(target.parent.glob("stlc-engineer.bak-*"))
        self.assertEqual(1, len(backups))
        self.assertEqual("user customisation", (backups[0] / "LOCAL-NOTES.md").read_text())

    def test_adapter_cannot_override_core_frontmatter(self):
        with self.assertRaises(SystemExit):
            pkg.render_skill_md({"extra_frontmatter": {"name": "other"}})
        rendered = pkg.render_skill_md({"extra_frontmatter": {"x-platform-flag": True}})
        self.assertIn("x-platform-flag: true", rendered)
        self.assertTrue(rendered.endswith((SKILL / "SKILL.md").read_text().split("\n---\n", 1)[1]))

    def test_build_is_reproducible(self):
        quiet(pkg.build, self.tmp / "a")
        quiet(pkg.build, self.tmp / "b")
        name = f"stlc-engineer-{pkg.version()}.zip"
        self.assertEqual((self.tmp / "a" / name).read_bytes(), (self.tmp / "b" / name).read_bytes())
        with zipfile.ZipFile(self.tmp / "a" / name) as zf:
            self.assertIn("stlc-engineer/SKILL.md", zf.namelist())
            self.assertFalse([n for n in zf.namelist() if "__pycache__" in n])


if __name__ == "__main__":
    unittest.main()
