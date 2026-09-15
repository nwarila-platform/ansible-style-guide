# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Test every branch and interaction of the four structural rules."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

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
        (role / "meta/main.yml").write_text(
            "galaxy_info:\n  min_ansible_version: '2.18'\ndependencies: []\n"
        )
        (role / "defaults/main.yml").write_text(
            f"{name}_defaults:\n  marker: 'present'\n"
        )
        (role / "tasks/main.yml").write_bytes(LOADER.read_bytes())
        return role

    def findings(self, role, kind="application", role_path=None):
        return check_role(
            role,
            role_path or role.name,
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
                    expected = [
                        ("SCAFFOLD-01", f"{role.name}/{directory}"),
                        ("SCAFFOLD-03", f"{role.name}/{expected_file}"),
                    ]
                    if directory == "meta":
                        expected.insert(
                            1,
                            ("FLOOR-01", f"{role.name}/meta/main.yml"),
                        )
                    self.assertEqual(
                        [(item.id, item.path) for item in findings],
                        expected,
                    )

    def test_loader_identical_and_one_byte_change(self):
        role = self.complete_role("loader_role")
        self.assertEqual(self.findings(role), [])
        loader = role / "tasks/main.yml"
        data = loader.read_bytes()
        loader.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
        findings = [item for item in self.findings(role) if item.id == "LOADER-01"]
        self.assertEqual(len(findings), 1)
        found = hashlib.sha256(loader.read_bytes()).hexdigest()
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
                expected = [("SCAFFOLD-03", f"{role.name}/{required}")]
                if required == "meta/main.yml":
                    expected.insert(
                        0,
                        ("FLOOR-01", f"{role.name}/meta/main.yml"),
                    )
                self.assertEqual(
                    [(item.id, item.path) for item in findings],
                    expected,
                )

    def test_floor_cases(self):
        none = (
            "meta/main.yml declares no min_ansible_version; "
            "the template default is '2.18'"
        )
        missing = (
            "meta/main.yml is missing, so no min_ansible_version is declared; "
            "the template default is '2.18'"
        )
        cases = [
            (
                "single_quoted",
                b"galaxy_info:\n  min_ansible_version: '2.18'\n",
                [],
            ),
            (
                "double_quoted",
                b'galaxy_info:\n  min_ansible_version: "2.18"\n',
                [],
            ),
            (
                "comment",
                b"galaxy_info:\n  min_ansible_version: '2.18' # note\n",
                [],
            ),
            (
                "crlf_aligned",
                b"galaxy_info:\r\n  min_ansible_version: '2.18'\r\n",
                [],
            ),
            (
                "byte_order_mark",
                b"\xef\xbb\xbfgalaxy_info:\n  min_ansible_version: '2.18'\n",
                [],
            ),
            (
                "merge_key",
                (b"base: &base\n  min_ansible_version: '2.18'\n"
                b"galaxy_info:\n  <<: *base\n"),
                [],
            ),
            (
                "duplicate_older_then_aligned",
                (b"galaxy_info:\n  min_ansible_version: '2.17'\n"
                b"  min_ansible_version: '2.18'\n"),
                [],
            ),
            (
                "older",
                (b"galaxy_info:\n  author: fixture\n"
                b"  min_ansible_version: '2.17'\n"),
                [
                    ("min_ansible_version is '2.17'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "plain_aligned_number",
                b"galaxy_info:\n  min_ansible_version: 2.18\n",
                [
                    ("min_ansible_version is 2.18; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "plain_newer_number",
                b"galaxy_info:\n  min_ansible_version: 2.20\n",
                [
                    ("min_ansible_version is 2.2; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "quoted_space",
                b"galaxy_info:\n  min_ansible_version: '2.18 '\n",
                [
                    ("min_ansible_version is '2.18 '; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "crlf_older",
                b"galaxy_info:\r\n  min_ansible_version: '2.17'\r\n",
                [
                    ("min_ansible_version is '2.17'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "other_mapping_first",
                (b"other:\n  min_ansible_version: '2.18'\n"
                b"galaxy_info:\n  min_ansible_version: '2.17'\n"),
                [
                    ("min_ansible_version is '2.17'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "duplicate_aligned_then_older",
                (b"galaxy_info:\n  min_ansible_version: '2.18'\n"
                b"  min_ansible_version: '2.17'\n"),
                [
                    ("min_ansible_version is '2.17'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "duplicate_galaxy_aligned_then_older",
                (b"galaxy_info:\n  min_ansible_version: '2.18'\n"
                b"galaxy_info:\n  min_ansible_version: '2.17'\n"),
                [
                    ("min_ansible_version is '2.17'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "duplicate_older_then_sequence",
                (b"galaxy_info:\n  min_ansible_version: '2.17'\n"
                b"  min_ansible_version: []\n"),
                [
                    ("min_ansible_version is []; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "alias",
                (b"floor: &floor '2.17'\ngalaxy_info:\n"
                b"  min_ansible_version: *floor\n"),
                [
                    ("min_ansible_version is '2.17'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "sequence_value",
                b"galaxy_info:\n  min_ansible_version: ['2.18']\n",
                [
                    ("min_ansible_version is ['2.18']; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "apostrophe",
                b'galaxy_info:\n  min_ansible_version: "2\'18"\n',
                [
                    ('min_ansible_version is "2\'18"; '
                    "the template default is '2.18'")
                ],
            ),
            (
                "both_quote_kinds",
                b'galaxy_info:\n  min_ansible_version: \'2\'\'"18\'\n',
                [
                    ("min_ansible_version is '2\\'\"18'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "block_scalar",
                b"galaxy_info:\n  min_ansible_version: |\n    2.18\n",
                [
                    ("min_ansible_version is '2.18\\n'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "non_ascii",
                b"galaxy_info:\n  min_ansible_version: '2.\xc3\xa9'\n",
                [
                    ("min_ansible_version is '2.é'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "control_character",
                b'galaxy_info:\n  min_ansible_version: "2.18\\u0007"\n',
                [
                    ("min_ansible_version is '2.18\\x07'; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "false_value",
                b"galaxy_info:\n  min_ansible_version: false\n",
                [
                    ("min_ansible_version is False; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "zero_value",
                b"galaxy_info:\n  min_ansible_version: 0\n",
                [
                    ("min_ansible_version is 0; "
                    "the template default is '2.18'")
                ],
            ),
            (
                "long_sequence",
                (b"galaxy_info:\n  min_ansible_version: ['00', '01', '02', '03', "
                b"'04', '05', '06', '07', '08', '09', '10', '11', '12', '13', "
                b"'14', '15', '16', '17', '18', '19']\n"),
                [
                    ("min_ansible_version is ['00', '01', '02', '03', '04', '05', "
                    "'06', '07', '08', '09', '10', '11', '12', '13', '14', '15', "
                    "'16', '17', '18', '19']; the template default is '2.18'")
                ],
            ),
            ("absent", b"galaxy_info:\n  author: fixture\n", [none]),
            ("empty", b"galaxy_info:\n  min_ansible_version:\n", [none]),
            (
                "null_word",
                b"galaxy_info:\n  min_ansible_version: null\n",
                [none],
            ),
            ("tilde", b"galaxy_info:\n  min_ansible_version: ~\n", [none]),
            (
                "quoted_empty",
                b"galaxy_info:\n  min_ansible_version: ''\n",
                [none],
            ),
            (
                "commented",
                (b"galaxy_info:\n  # min_ansible_version: '2.18'\n"
                b"  author: fixture\n"),
                [none],
            ),
            (
                "nested",
                b"galaxy_info:\n  nested:\n    min_ansible_version: '2.18'\n",
                [none],
            ),
            (
                "duplicate_older_then_empty",
                (b"galaxy_info:\n  min_ansible_version: '2.17'\n"
                b"  min_ansible_version: ''\n"),
                [none],
            ),
            (
                "duplicate_galaxy_then_sequence",
                (b"galaxy_info:\n  min_ansible_version: '2.18'\n"
                b"galaxy_info: []\n"),
                [none],
            ),
            ("galaxy_info_sequence", b"galaxy_info: []\n", [none]),
            (
                "galaxy_info_nonempty_sequence",
                b"galaxy_info: ['x']\n",
                [none],
            ),
            (
                "sequence_root",
                b"- galaxy_info:\n    min_ansible_version: '2.18'\n",
                [none],
            ),
            ("empty_file", b"", [none]),
            ("invalid", b"galaxy_info: [\n", [none]),
            (
                "two_documents",
                (b"galaxy_info:\n  min_ansible_version: '2.18'\n"
                b"---\nother: true\n"),
                [none],
            ),
            (
                "empty_second_document",
                b"galaxy_info:\n  min_ansible_version: '2.18'\n---\n",
                [none],
            ),
            (
                "unknown_tag_value",
                b"galaxy_info:\n  min_ansible_version: !floor '2.18'\n",
                [none],
            ),
            (
                "unknown_tag_key",
                b"galaxy_info:\n  !floor min_ansible_version: '2.18'\n",
                [none],
            ),
            (
                "python_tag",
                (b"galaxy_info:\n"
                b"  min_ansible_version: !!python/tuple ['2', '18']\n"),
                [none],
            ),
            (
                "double_byte_order_mark",
                (b"\xef\xbb\xbf\xef\xbb\xbfgalaxy_info:\n"
                b"  min_ansible_version: '2.18'\n"),
                [none],
            ),
            (
                "undecodable",
                b"galaxy_info:\n  min_ansible_version: '2.1\xff'\n",
                [none],
            ),
        ]
        for case, data, messages in cases:
            with self.subTest(case=case):
                role = self.complete_role("floor_role")
                (role / "meta/main.yml").write_bytes(data)
                floor_findings = [
                    item for item in self.findings(role) if item.id == "FLOOR-01"
                ]
                self.assertEqual(
                    [
                        (item.path, item.line, item.message)
                        for item in floor_findings
                    ],
                    [
                        ("floor_role/meta/main.yml", 1, message)
                        for message in messages
                    ],
                )

        with self.subTest(case="other_kind"):
            role = self.complete_role("floor_role")
            (role / "meta/main.yml").write_bytes(
                b"galaxy_info:\n  min_ansible_version: '2.16'\n"
            )
            floor_findings = [
                item
                for item in self.findings(role, kind="other")
                if item.id == "FLOOR-01"
            ]
            self.assertEqual(
                [(item.path, item.line, item.message) for item in floor_findings],
                [
                    (
                        "floor_role/meta/main.yml",
                        1,
                        ("min_ansible_version is '2.16'; "
                        "the template default is '2.18'"),
                    )
                ],
            )

        with self.subTest(case="missing_file"):
            role = self.complete_role("floor_role")
            (role / "meta/main.yml").unlink()
            self.assertEqual(
                [
                    (item.id, item.path, item.line, item.message)
                    for item in self.findings(role)
                ],
                [
                    ("FLOOR-01", "floor_role/meta/main.yml", 1, missing),
                    (
                        "SCAFFOLD-03",
                        "floor_role/meta/main.yml",
                        1,
                        "required file meta/main.yml is missing",
                    ),
                ],
            )

        with self.subTest(case="directory_named_main"):
            role = self.complete_role("directory_role")
            (role / "meta/main.yml").unlink()
            (role / "meta/main.yml").mkdir()
            self.assertEqual(
                [
                    (item.id, item.path, item.line, item.message)
                    for item in self.findings(role)
                ],
                [
                    ("FLOOR-01", "directory_role/meta/main.yml", 1, missing),
                    (
                        "SCAFFOLD-03",
                        "directory_role/meta/main.yml",
                        1,
                        "required file meta/main.yml is missing",
                    ),
                ],
            )

        with self.subTest(case="reader_mechanism"):
            role = self.complete_role("floor_role")
            meta = role / "meta/main.yml"
            text = meta.read_text()
            with (
                mock.patch.object(
                    Path,
                    "read_text",
                    autospec=True,
                    side_effect=Path.read_text,
                ) as read_text,
                mock.patch(
                    "rolecheck.structure.yaml.safe_load",
                    side_effect=yaml.safe_load,
                ) as safe_load,
            ):
                self.findings(role, kind="other")
            self.assertEqual(
                read_text.call_args_list,
                [mock.call(meta, encoding="utf-8")],
            )
            self.assertEqual(safe_load.call_args_list, [mock.call(text)])

        handled = (
            OSError("fixture"),
            UnicodeDecodeError("utf-8", b"\xff", 0, 1, "fixture"),
            UnicodeTranslateError("x", 0, 1, "fixture"),
            yaml.YAMLError("fixture"),
        )
        unexpected = (
            RuntimeError("fixture"),
            ValueError("fixture"),
            TypeError("fixture"),
            KeyError("fixture"),
            AttributeError("fixture"),
            RecursionError("fixture"),
        )
        for target in (
            "pathlib.Path.read_text",
            "rolecheck.structure.yaml.safe_load",
        ):
            for error in handled:
                with self.subTest(
                    case="reader_handled",
                    target=target,
                    error=type(error).__name__,
                ):
                    role = self.complete_role("floor_role")
                    with mock.patch(target, side_effect=error):
                        floor_findings = [
                            item
                            for item in self.findings(role, kind="other")
                            if item.id == "FLOOR-01"
                        ]
                    self.assertEqual(
                        [
                            (item.path, item.line, item.message)
                            for item in floor_findings
                        ],
                        [("floor_role/meta/main.yml", 1, none)],
                    )
            for error in unexpected:
                with self.subTest(
                    case="reader_unexpected",
                    target=target,
                    error=type(error).__name__,
                ):
                    role = self.complete_role("floor_role")
                    with (
                        mock.patch(target, side_effect=error),
                        self.assertRaises(type(error)),
                    ):
                        self.findings(role, kind="other")

        with self.subTest(case="template_floor_constant"):
            aligned = self.complete_role("aligned_role")
            absent = self.complete_role("absent_role")
            (absent / "meta/main.yml").write_bytes(
                b"galaxy_info:\n  author: fixture\n"
            )
            missing_role = self.complete_role("missing_role")
            (missing_role / "meta/main.yml").unlink()
            observed = []
            with mock.patch("rolecheck.structure.TEMPLATE_FLOOR", "9.99"):
                for role in (aligned, absent, missing_role):
                    observed.extend(
                        (item.path, item.line, item.message)
                        for item in self.findings(role)
                        if item.id == "FLOOR-01"
                    )
            self.assertEqual(
                observed,
                [
                    (
                        "aligned_role/meta/main.yml",
                        1,
                        ("min_ansible_version is '2.18'; "
                        "the template default is '9.99'"),
                    ),
                    (
                        "absent_role/meta/main.yml",
                        1,
                        ("meta/main.yml declares no min_ansible_version; "
                        "the template default is '9.99'"),
                    ),
                    (
                        "missing_role/meta/main.yml",
                        1,
                        ("meta/main.yml is missing, so no min_ansible_version is "
                        "declared; the template default is '9.99'"),
                    ),
                ],
            )

        with self.subTest(case="non_utf8_locale"):
            role = self.complete_role("floor_role")
            (role / "meta/main.yml").write_bytes(
                b"galaxy_info:\n  min_ansible_version: '2.\xc3\xa9'\n"
            )
            script = (
                "import json\n"
                "import sys\n"
                "from rolecheck.structure import LOADER_SHA256, check_role\n"
                "findings = check_role(sys.argv[1], 'floor_role', "
                "'application', LOADER_SHA256)\n"
                "print(json.dumps([[f.line, f.message] for f in findings "
                "if f.id == 'FLOOR-01']))\n"
            )
            result = subprocess.run(
                [sys.executable, "-c", script, str(role)],
                cwd=ROOT,
                env={**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0"},
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(
                json.loads(result.stdout),
                [
                    [
                        1,
                        ("min_ansible_version is '2.é'; "
                        "the template default is '2.18'"),
                    ]
                ],
            )
