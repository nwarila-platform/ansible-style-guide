# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Assert exact deterministic text, JSON, and exit-status reporting."""

import json
import unittest
from pathlib import Path

from rolecheck.discover import Role
from rolecheck.report import Finding, exit_status, json_report, text_report


class ReportTests(unittest.TestCase):
    """Supply every report input in reverse order to prove byte sorting."""

    def setUp(self):
        self.roles = [
            Role(Path("/z"), "z-role", "z", "application"),
            Role(Path("/a"), "a-role", "a", "other"),
        ]
        self.findings = [
            Finding(None, "z-root", 0, "TOOL", "z warning", "tool"),
            Finding("z-role", "z-role/tasks/main.yml", 10, "yaml[truthy]", "ignored", "style"),
            Finding(None, "a-root", 0, "TOOL", "a warning", "tool"),
            Finding("a-role", "a-role/tasks/main.yml", 2, "FMT-01", "bad width", "style"),
        ]

    def test_exact_text(self):
        expected = (
            "a-role/tasks/main.yml:2 FMT-01: bad width\n"
            "a-root:0 TOOL: a warning\n"
            "z-role/tasks/main.yml:10 yaml[truthy]\n"
            "z-root:0 TOOL: z warning\n"
            "== a-role: 1 finding(s) FMT-01 x1\n"
            "== z-role: 1 finding(s) yaml[truthy] x1\n"
            "== root a-root: 1 finding(s) TOOL x1\n"
            "== root z-root: 1 finding(s) TOOL x1\n"
            "== total: 2 role(s), 4 finding(s)\n"
        )
        self.assertEqual(
            text_report(self.findings, self.roles, ["z-root", "a-root"]),
            expected,
        )

    def test_exact_json_object(self):
        expected = {
            "findings": [
                {
                    "id": "FMT-01",
                    "kind": "style",
                    "line": 2,
                    "message": "bad width",
                    "path": "a-role/tasks/main.yml",
                    "role_path": "a-role",
                },
                {
                    "id": "yaml[truthy]",
                    "kind": "style",
                    "line": 10,
                    "message": "ignored",
                    "path": "z-role/tasks/main.yml",
                    "role_path": "z-role",
                },
            ],
            "roles": [
                {
                    "findings": 1,
                    "ids": {"FMT-01": 1},
                    "role_kind": "other",
                    "role_path": "a-role",
                },
                {
                    "findings": 1,
                    "ids": {"yaml[truthy]": 1},
                    "role_kind": "application",
                    "role_path": "z-role",
                },
            ],
            "root_findings": [
                {
                    "id": "TOOL",
                    "kind": "tool",
                    "line": 0,
                    "message": "a warning",
                    "path": "a-root",
                    "role_path": None,
                },
                {
                    "id": "TOOL",
                    "kind": "tool",
                    "line": 0,
                    "message": "z warning",
                    "path": "z-root",
                    "role_path": None,
                },
            ],
            "summary": {
                "findings": 4,
                "ids": {"FMT-01": 1, "TOOL": 2, "yaml[truthy]": 1},
                "roles": 2,
            },
        }
        rendered = json_report(self.findings, self.roles)
        self.assertEqual(json.loads(rendered), expected)
        self.assertEqual(list(json.loads(rendered)), sorted(expected))

    def test_exit_status(self):
        self.assertEqual(exit_status([], report_only=False), 0)
        self.assertEqual(exit_status(self.findings, report_only=False), 1)
        self.assertEqual(exit_status(self.findings, report_only=True), 0)
        aggregate = [Finding(None, "root", 0, "TOOL", "failed", "tool")]
        self.assertEqual(exit_status(aggregate, report_only=False), 1)
