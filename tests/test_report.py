# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Assert exact deterministic text, JSON, and exit-status reporting."""

import json
import unittest
from pathlib import Path

from rolecheck.discover import Role
from rolecheck.report import (
    MESSAGE_IDS,
    WARNING_IDS,
    Finding,
    exit_status,
    json_report,
    text_report,
)


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
                    "warning_ids": {},
                    "warnings": 0,
                },
                {
                    "findings": 1,
                    "ids": {"yaml[truthy]": 1},
                    "role_kind": "application",
                    "role_path": "z-role",
                    "warning_ids": {},
                    "warnings": 0,
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
                "warning_ids": {},
                "warnings": 0,
            },
            "warnings": [],
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
        warning = [
            Finding(
                "z-role",
                "z-role/meta/main.yml",
                2,
                "FLOOR-01",
                "old floor",
                "structure",
            )
        ]
        self.assertEqual(exit_status(warning, report_only=False), 0)
        self.assertEqual(exit_status(aggregate + warning, report_only=False), 1)
        self.assertEqual(exit_status(aggregate + warning, report_only=True), 0)

    def test_warning_text_and_json(self):
        self.assertEqual(WARNING_IDS, {"FLOOR-01"})
        self.assertEqual(
            MESSAGE_IDS,
            {
                "FACT-01",
                "FMT-01",
                "FMT-02",
                "LOADER-01",
                "LOOP-01",
                "NAME-01",
                "REG-01",
                "SCAFFOLD-01",
                "SCAFFOLD-02",
                "SCAFFOLD-03",
                "TOOL",
            },
        )
        old_floor = Finding(
            "z-role",
            "z-role/meta/main.yml",
            2,
            "FLOOR-01",
            "old floor",
            "structure",
        )
        no_floor = Finding(
            "a-role",
            "a-role/meta/main.yml",
            1,
            "FLOOR-01",
            "no floor",
            "structure",
        )
        width = Finding(
            "a-role",
            "a-role/tasks/main.yml",
            2,
            "FMT-01",
            "bad width",
            "style",
        )
        tool = Finding(None, "root", 0, "TOOL", "tool failed", "tool")
        one_role = [Role(Path("/z"), "z-role", "z", "application")]

        expected_text = (
            "a-role/meta/main.yml:1 FLOOR-01: warning: no floor\n"
            "a-role/tasks/main.yml:2 FMT-01: bad width\n"
            "z-role/meta/main.yml:2 FLOOR-01: warning: old floor\n"
            "== a-role: 1 finding(s) FMT-01 x1; 1 warning(s) FLOOR-01 x1\n"
            "== z-role: 0 finding(s); 1 warning(s) FLOOR-01 x1\n"
            "== total: 2 role(s), 1 finding(s), 2 warning(s)\n"
        )
        expected_json = {
            "findings": [
                {
                    "id": "FMT-01",
                    "kind": "style",
                    "line": 2,
                    "message": "bad width",
                    "path": "a-role/tasks/main.yml",
                    "role_path": "a-role",
                }
            ],
            "roles": [
                {
                    "findings": 1,
                    "ids": {"FMT-01": 1},
                    "role_kind": "other",
                    "role_path": "a-role",
                    "warning_ids": {"FLOOR-01": 1},
                    "warnings": 1,
                },
                {
                    "findings": 0,
                    "ids": {},
                    "role_kind": "application",
                    "role_path": "z-role",
                    "warning_ids": {"FLOOR-01": 1},
                    "warnings": 1,
                },
            ],
            "root_findings": [],
            "summary": {
                "findings": 1,
                "ids": {"FMT-01": 1},
                "roles": 2,
                "warning_ids": {"FLOOR-01": 2},
                "warnings": 2,
            },
            "warnings": [
                {
                    "id": "FLOOR-01",
                    "kind": "structure",
                    "line": 1,
                    "message": "no floor",
                    "path": "a-role/meta/main.yml",
                    "role_path": "a-role",
                },
                {
                    "id": "FLOOR-01",
                    "kind": "structure",
                    "line": 2,
                    "message": "old floor",
                    "path": "z-role/meta/main.yml",
                    "role_path": "z-role",
                },
            ],
        }
        findings = [old_floor, no_floor, width]
        self.assertEqual(text_report(findings, self.roles, []), expected_text)
        self.assertEqual(json.loads(json_report(findings, self.roles)), expected_json)

        expected_text = (
            "root:0 TOOL: tool failed\n"
            "z-role/meta/main.yml:2 FLOOR-01: warning: old floor\n"
            "== z-role: 0 finding(s); 1 warning(s) FLOOR-01 x1\n"
            "== root root: 1 finding(s) TOOL x1\n"
            "== total: 1 role(s), 1 finding(s), 1 warning(s)\n"
        )
        expected_json = {
            "findings": [],
            "roles": [
                {
                    "findings": 0,
                    "ids": {},
                    "role_kind": "application",
                    "role_path": "z-role",
                    "warning_ids": {"FLOOR-01": 1},
                    "warnings": 1,
                }
            ],
            "root_findings": [
                {
                    "id": "TOOL",
                    "kind": "tool",
                    "line": 0,
                    "message": "tool failed",
                    "path": "root",
                    "role_path": None,
                }
            ],
            "summary": {
                "findings": 1,
                "ids": {"TOOL": 1},
                "roles": 1,
                "warning_ids": {"FLOOR-01": 1},
                "warnings": 1,
            },
            "warnings": [
                {
                    "id": "FLOOR-01",
                    "kind": "structure",
                    "line": 2,
                    "message": "old floor",
                    "path": "z-role/meta/main.yml",
                    "role_path": "z-role",
                }
            ],
        }
        findings = [old_floor, tool]
        self.assertEqual(text_report(findings, one_role, ["root"]), expected_text)
        self.assertEqual(json.loads(json_report(findings, one_role)), expected_json)
