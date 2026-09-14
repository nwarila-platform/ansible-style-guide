# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Verify ansible-lint argv construction, SARIF parsing, and warning handling."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rolecheck.discover import Role
from rolecheck.lint import build_command, run_lint
from rolecheck.structure import LOADER_SHA256

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "fixtures/style/applications/pass_role/tasks/main.yml"


def empty_sarif():
    """Return the smallest valid SARIF payload accepted by the checker."""

    return {"runs": [{"results": []}]}


class LintTests(unittest.TestCase):
    """Use temporary roles and subprocess stubs to isolate the R5 contract."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def role(self, name, loader=False):
        path = self.root / "applications" / name
        (path / "tasks").mkdir(parents=True)
        if loader:
            (path / "tasks/main.yml").write_bytes(LOADER.read_bytes())
        else:
            (path / "tasks/main.yml").write_text("- ansible.builtin.debug: {}\n")
        return Role(path, name, name, "application")

    def test_argv_with_two_loaders_and_one_ordinary_entry(self):
        first = self.role("a", loader=True)
        second = self.role("b", loader=True)
        ordinary = self.role("c", loader=False)
        sarif = self.root / "result.sarif"
        command = build_command(
            self.root,
            [first, second, ordinary],
            LOADER_SHA256,
            sarif,
        )
        exclude = command.index("--exclude")
        separator = command.index("--")
        self.assertEqual(
            command[exclude + 1 : separator],
            [
                str(first.path / "tasks/main.yml"),
                str(second.path / "tasks/main.yml"),
            ],
        )
        self.assertEqual(
            command[separator + 1 :],
            [str(first.path), str(second.path), str(ordinary.path)],
        )

    def test_argv_without_loader_omits_exclude_but_keeps_separator(self):
        ordinary = self.role("ordinary", loader=False)
        command = build_command(
            self.root,
            [ordinary],
            LOADER_SHA256,
            self.root / "result.sarif",
        )
        self.assertNotIn("--exclude", command)
        self.assertEqual(command[-2:], ["--", str(ordinary.path)])

    def test_saved_sarif_is_parsed(self):
        role = self.role("sample", loader=False)

        def completed(command, **_kwargs):
            sarif = Path(command[command.index("--sarif-file") + 1])
            sarif.write_text(
                json.dumps(
                    {
                        "runs": [
                            {
                                "results": [
                                    {
                                        "ruleId": "FMT-01",
                                        "message": {"text": "diagnostic"},
                                        "locations": [
                                            {
                                                "physicalLocation": {
                                                    "artifactLocation": {
                                                        "uri": str(
                                                            role.path
                                                            / "tasks/main.yml"
                                                        )
                                                    },
                                                    "region": {"startLine": 7},
                                                }
                                            }
                                        ],
                                    }
                                ]
                            }
                        ]
                    }
                )
            )
            return subprocess.CompletedProcess(command, 2, "", "")

        with patch("rolecheck.lint.subprocess.run", side_effect=completed):
            findings = run_lint(self.root, "display-root", [role])
        self.assertEqual(len(findings), 1)
        self.assertEqual(
            (
                findings[0].role_path,
                findings[0].path,
                findings[0].line,
                findings[0].id,
                findings[0].message,
                findings[0].kind,
            ),
            ("sample", "sample/tasks/main.yml", 7, "FMT-01", "diagnostic", "style"),
        )

    def test_warning_suppression_and_unresolved_warning_surface(self):
        role = self.role("sample", loader=False)
        stderr = (
            "WARNING  Listing 4 violation(s) that are fatal\n"
            "WARNING  Skipped installing collection dependencies due to running in offline mode.\n"
            "WARNING unresolved module example"
        )

        def completed(command, **_kwargs):
            sarif = Path(command[command.index("--sarif-file") + 1])
            sarif.write_text(json.dumps(empty_sarif()))
            return subprocess.CompletedProcess(command, 2, "", stderr)

        with patch("rolecheck.lint.subprocess.run", side_effect=completed):
            findings = run_lint(self.root, "display-root", [role])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].id, "TOOL")
        self.assertEqual(findings[0].message, "WARNING unresolved module example")

    def test_exit_one_without_sarif_is_one_aggregate_plus_warning(self):
        role = self.role("sample", loader=False)
        stderr = "WARNING synthetic qualifying warning\nsynthetic fatal error\n"
        completed = subprocess.CompletedProcess([], 1, "", stderr)
        with patch("rolecheck.lint.subprocess.run", return_value=completed):
            findings = run_lint(self.root, "display-root", [role])
        self.assertEqual(len(findings), 2)
        self.assertTrue(all(item.id == "TOOL" for item in findings))
        self.assertEqual(
            [item.message for item in findings],
            [
                "WARNING synthetic qualifying warning",
                "WARNING synthetic qualifying warning | synthetic fatal error",
            ],
        )
