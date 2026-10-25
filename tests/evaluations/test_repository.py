"""The repository passes its own structural, contract, registry, version and secret checks."""
import unittest

from tests.evaluations.helpers import ROOT  # noqa: F401  (sets sys.path)

import validate_repository as vr  # noqa: E402


class RepositoryTest(unittest.TestCase):
    def test_repository_is_valid(self):
        errors = [f"{i['where']}: {i['message']}" for i in vr.run().items if i["level"] == "ERROR"]
        self.assertEqual([], errors)

    def test_frontmatter_parser(self):
        fm = vr.parse_frontmatter("---\nname: x\ndescription: >\n  first\n  second\n---\nbody")
        self.assertEqual({"name": "x", "description": "first second"}, fm)


if __name__ == "__main__":
    unittest.main()
