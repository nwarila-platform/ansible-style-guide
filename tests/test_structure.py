# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Test every branch and interaction of the four structural rules."""

import shutil
import tempfile
import unittest
from pathlib import Path

from rolecheck.structure import LOADER_SHA256, REQUIRED, SCAFFOLD, check_role

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "fixtures/style/applications/pass_role/tasks/main.yml"


class StructureTests(unittest.TestCase):
    """Construct complete roles, then isolate one structural defect at a time."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def complete_role(self, name="sample_role"):
        role = self.root / "applications" / name
        for directory in SCAFFOLD:
            (role / directory).mkdir(parents=True, exist_ok=True)
        (role / "README.md").write_text("# fixture\n")
        (role / "meta/main.yml").write_text("dependencies: []\n")
        (role / "defaults/main.yml").write_text(
            f"{name}_defaults:\n  marker: 'present'\n"
        )
        (role / "tasks/main.yml").write_bytes(LOADER.read_bytes())
        return role

    def findings(self, role, kind="application", display=None):
        return check_role(
            role,
            display or role.name,
            kind,
            LOADER_SHA256,
        )

    def test_complete_scaffold_is_clean(self):
        self.assertEqual(self.findings(self.complete_role()), [])

    def test_missing_scaffold_directory_cardinality(self):
        one_finding = {
            "files",
            "handlers",
            "library",
            "lookup_plugins",
            "module_utils",
            "molecule",
            "templates",
            "tests",
            "vars",
        }
        for directory in SCAFFOLD:
            with self.subTest(directory=directory):
                role = self.complete_role(f"role_{directory}")
                shutil.rmtree(role / directory)
                findings = self.findings(role)
                if directory in one_finding:
                    self.assertEqual(len(findings), 1)
                    self.assertEqual(findings[0].id, "SCAFFOLD-01")
                    self.assertEqual(findings[0].path, f"{role.name}/{directory}")
                else:
                    expected_file = {
                        "defaults": "defaults/main.yml",
                        "meta": "meta/main.yml",
                        "tasks": "tasks/main.yml",
                    }[directory]
                    self.assertEqual(
                        [(item.id, item.path) for item in findings],
                        [
                            ("SCAFFOLD-01", f"{role.name}/{directory}"),
                            ("SCAFFOLD-03", f"{role.name}/{expected_file}"),
                        ],
                    )

    def test_loader_identical_and_one_byte_change(self):
        role = self.complete_role("loader_role")
        self.assertEqual(self.findings(role), [])
        loader = role / "tasks/main.yml"
        data = loader.read_bytes()
        loader.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
        findings = [item for item in self.findings(role) if item.id == "LOADER-01"]
        self.assertEqual(len(findings), 1)
        found = __import__("hashlib").sha256(loader.read_bytes()).hexdigest()
        self.assertEqual(
            findings[0].message,
            "tasks/main.yml is not the shared loader; sha256 "
            f"{found[:16]} differs from {LOADER_SHA256[:16]}",
        )

    def test_other_kind_skips_loader_and_defaults(self):
        role = self.complete_role("other_role")
        (role / "tasks/main.yml").write_text("- ansible.builtin.debug:\n    msg: 'x'\n")
        (role / "defaults/main.yml").write_text("wrong: true\n")
        findings = self.findings(role, kind="other")
        self.assertFalse({"LOADER-01", "SCAFFOLD-02"} & {item.id for item in findings})

    def test_defaults_key_cases(self):
        cases = {
            "present": ("defaults_role_defaults: {}\n", None),
            "absent": (
                "wrong: {}\n",
                (
                    "defaults/main.yml defines no top-level 'defaults_role_defaults' "
                    "key (found: wrong)"
                ),
            ),
            "non_mapping": (
                "- one\n",
                (
                    "defaults/main.yml defines no top-level 'defaults_role_defaults' "
                    "key (found: nothing)"
                ),
            ),
            "invalid": (
                "broken: [\n",
                (
                    "defaults/main.yml defines no top-level 'defaults_role_defaults' "
                    "key (found: nothing)"
                ),
            ),
            "sorted": (
                "zeta: 1\nalpha: 2\nmiddle: 3\n",
                (
                    "defaults/main.yml defines no top-level 'defaults_role_defaults' "
                    "key (found: alpha, middle, zeta)"
                ),
            ),
            "empty": (
                "",
                (
                    "defaults/main.yml defines no top-level 'defaults_role_defaults' "
                    "key (found: nothing)"
                ),
            ),
        }
        for case, (content, message) in cases.items():
            with self.subTest(case=case):
                role = self.complete_role("defaults_role")
                (role / "defaults/main.yml").write_text(content)
                findings = [
                    item for item in self.findings(role) if item.id == "SCAFFOLD-02"
                ]
                if message is None:
                    self.assertEqual(findings, [])
                else:
                    self.assertEqual(len(findings), 1)
                    self.assertEqual(findings[0].message, message)

    def test_missing_required_file_retains_parent(self):
        for required in REQUIRED:
            with self.subTest(required=required):
                role = self.complete_role(f"missing_{required.replace('/', '_')}")
                (role / required).unlink()
                findings = self.findings(role)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].id, "SCAFFOLD-03")
                self.assertEqual(findings[0].path, f"{role.name}/{required}")
