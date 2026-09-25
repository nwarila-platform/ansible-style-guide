# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Drive every custom-rule hook branch and the SARIF rendering boundary."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from ansiblelint.file_utils import Lintable
from ansiblelint.utils import task_in_list

from rolecheck.discover import discover
from rolecheck.lint import run_lint

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "rolecheck/lint/rules"
FAIL = ROOT / "fixtures/style/applications/fail_role"
BOUNDARY = ROOT / "fixtures/style/applications/boundary_role"


def load_rule(name):
    """Return a loaded rule module without requiring a rules package."""

    spec = importlib.util.spec_from_file_location(
        f"behavior_{name}", RULES / f"{name}.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load rule {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FMT_01 = load_rule("fmt_01")
FMT_02 = load_rule("fmt_02")
NAME_01 = load_rule("name_01")
FACT_01 = load_rule("fact_01")
LOOP_01 = load_rule("loop_01")
REG_01 = load_rule("reg_01")


def tasks(file):
    """Return the task objects ansible-lint builds for a lintable."""

    return list(task_in_list(file.data, file, file.kind))


def task_named(file, name):
    """Find one parsed task by its raw name value."""

    return next(task for task in tasks(file) if task.raw_task.get("name") == name)


class RuleBehaviorTests(unittest.TestCase):
    """Cover rule guards, precedence, scopes, recursion, and direct findings."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def lintable(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        file = Lintable(path)
        _ = file.data
        return file

    def test_none_and_non_yaml_guards(self):
        task = SimpleNamespace()
        non_yaml = SimpleNamespace(base_kind="text/plain", kind="tasks")
        yaml_rules = [FMT_01.Fmt01(), FMT_02.Fmt02(), NAME_01.Name01()]
        task_rules = [
            NAME_01.Name01(),
            FACT_01.Fact01(),
            LOOP_01.Loop01(),
            REG_01.Reg01(),
        ]
        for rule in yaml_rules:
            with self.subTest(rule=rule.id, hook="yaml-none"):
                self.assertEqual(rule.matchyaml(None), [])
            with self.subTest(rule=rule.id, hook="yaml-non-yaml"):
                self.assertEqual(rule.matchyaml(non_yaml), [])
        for rule in task_rules:
            with self.subTest(rule=rule.id, hook="task-none"):
                self.assertEqual(rule.matchtask(task, file=None), [])
            with self.subTest(rule=rule.id, hook="task-non-yaml"):
                self.assertEqual(rule.matchtask(task, file=non_yaml), [])

    def test_rejected_kinds_and_handler_boundaries(self):
        wrong_yaml = SimpleNamespace(
            base_kind="text/yaml",
            kind="vars",
            content="#region ------ [ process: lowercase ] ---------------- #\n",
            data=[],
        )
        wrong_task = SimpleNamespace(base_kind="text/yaml", kind="handlers")
        task = SimpleNamespace()
        self.assertEqual(FMT_02.Fmt02().matchyaml(wrong_yaml), [])
        self.assertEqual(NAME_01.Name01().matchyaml(wrong_yaml), [])
        self.assertEqual(NAME_01.Name01().matchtask(task, file=wrong_task), [])
        self.assertEqual(FACT_01.Fact01().matchtask(task, file=wrong_task), [])

        handler = Lintable(FAIL / "handlers/main.yml")
        parsed = tasks(handler)[0]
        self.assertEqual(len(LOOP_01.Loop01().matchtask(parsed, file=handler)), 1)
        self.assertEqual(len(REG_01.Reg01().matchtask(parsed, file=handler)), 1)

    def test_direct_fail_fixture_rule_counts(self):
        main = Lintable(FAIL / "tasks/present_windows.yml")
        validate = Lintable(FAIL / "tasks/validate.yml")
        handler = Lintable(FAIL / "handlers/main.yml")
        main_tasks = tasks(main)
        validate_tasks = tasks(validate)
        handler_tasks = tasks(handler)
        self.assertEqual(len(FMT_01.Fmt01().matchyaml(main)), 11)
        self.assertEqual(len(FMT_02.Fmt02().matchyaml(main)), 2)
        name_rule = NAME_01.Name01()
        self.assertEqual(
            sum(len(name_rule.matchtask(task, file=main)) for task in main_tasks)
            + sum(
                len(name_rule.matchtask(task, file=validate))
                for task in validate_tasks
            )
            + len(name_rule.matchyaml(main)),
            6,
        )
        self.assertEqual(
            sum(
                len(FACT_01.Fact01().matchtask(task, file=main))
                for task in main_tasks
            ),
            2,
        )
        loop_rule = LOOP_01.Loop01()
        self.assertEqual(
            sum(len(loop_rule.matchtask(task, file=main)) for task in main_tasks)
            + sum(
                len(loop_rule.matchtask(task, file=handler))
                for task in handler_tasks
            ),
            6,
        )
        reg_rule = REG_01.Reg01()
        self.assertEqual(
            sum(len(reg_rule.matchtask(task, file=main)) for task in main_tasks)
            + sum(
                len(reg_rule.matchtask(task, file=handler))
                for task in handler_tasks
            ),
            4,
        )

    def test_fact_three_actions_and_role_scope(self):
        content = """- name: 'PROCESS | Derive A Value'
  ansible.builtin.set_fact:
    marker: 'x'
"""
        application = self.lintable(
            "applications/app/tasks/present_windows.yml", content
        )
        host = self.lintable("host_roles/app/tasks/present_windows.yml", content)
        rule = FACT_01.Fact01()
        self.assertEqual(len(rule.matchtask(tasks(application)[0], file=application)), 1)
        self.assertEqual(rule.matchtask(tasks(host)[0], file=host), [])

        main = Lintable(FAIL / "tasks/present_windows.yml")
        bare = task_named(main, "PROCESS | Remember A Value In A Fact")
        legacy = task_named(
            main,
            "PROCESS | Remember A Value Through The Legacy Name",
        )
        self.assertEqual(len(rule.matchtask(bare, file=main)), 1)
        self.assertEqual(len(rule.matchtask(legacy, file=main)), 1)

    def test_register_mapping_list_first_key_and_comments(self):
        fail = Lintable(FAIL / "tasks/present_windows.yml")
        mapping = task_named(
            fail,
            "PROCESS | Register A Mapping Instead Of A Name",
        )
        result = REG_01.Reg01().matchtask(mapping, file=fail)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].message,
            "register target must be a string before it can be '__fail_role_<noun>__'",
        )

        list_file = self.lintable(
            "applications/list_role/tasks/probe.yml",
            """- name: 'PROCESS | Register A List'
  register: ['x']
  ansible.builtin.debug:
    msg: 'x'
""",
        )
        self.assertEqual(
            REG_01.Reg01().matchtask(tasks(list_file)[0], file=list_file),
            [],
        )

        first_key = self.lintable(
            "applications/first_key/tasks/probe.yml",
            """- register: '__first_key_probe__'
  name: 'PROCESS | Register First'
  ansible.builtin.debug:
    msg: 'x'
""",
        )
        self.assertEqual(
            REG_01.Reg01().matchtask(tasks(first_key)[0], file=first_key),
            [],
        )

        boundary = Lintable(BOUNDARY / "tasks/present_windows.yml")
        commented = task_named(boundary, "PROCESS | Carry A Trailing Comment")
        self.assertEqual(
            NAME_01.Name01().matchtask(commented, file=boundary),
            [],
        )
        self.assertEqual(
            REG_01.Reg01().matchtask(commented, file=boundary),
            [],
        )

    def test_nested_always_block_and_rescue_walk(self):
        file = self.lintable(
            "applications/always_role/tasks/probe.yml",
            """- name: 'BEGIN | Wrap The Probe'
  block:
    - name: 'BEGIN | Probe The Value'
      ansible.builtin.debug:
        msg: 'x'
  always:
    - name: 'BEGIN | Nest The Cleanup'
      block:
        - name: 'PROCESS | Use The Wrong Block Token'
          ansible.builtin.debug:
            msg: 'x'
      rescue:
        - name: 'END | Use The Wrong Rescue Token'
          ansible.builtin.debug:
            msg: 'x'
""",
        )
        findings = NAME_01.Name01().matchyaml(file)
        self.assertEqual(
            [finding.message for finding in findings],
            [
                "task inside an always: carries PROCESS but the enclosing stage is BEGIN",
                "task inside an always: carries END but the enclosing stage is BEGIN",
            ],
        )
        self.assertEqual([finding.lineno for finding in findings], [9, 13])

    def test_fmt_combined_width_and_label(self):
        file = Lintable(FAIL / "tasks/present_windows.yml")
        findings = [
            finding
            for finding in FMT_01.Fmt01().matchyaml(file)
            if finding.lineno == 148
        ]
        self.assertEqual(len(findings), 2)
        self.assertIn("banner line is 96 columns", findings[0].message)
        self.assertIn("does not match the region opened", findings[1].message)

    def test_shared_word_table(self):
        cases = {
            "Install": [],
            "7Zip": [],
            "3.10": [],
            "--": [],
            "(Ephemeral)": [],
            "[Bracketed]": [],
            "'Quoted": [],
            "on": ["on"],
            "v2": ["v2"],
            "PDQ.com": [],
            "windows_exporter": ["windows_exporter"],
        }
        for word, expected in cases.items():
            with self.subTest(word=word, rule="FMT-02"):
                self.assertEqual(FMT_02.bad_words(word), expected)
            with self.subTest(word=word, rule="NAME-01"):
                self.assertEqual(NAME_01.bad_words(word), expected)

    def test_fmt_every_yaml_kind(self):
        box = f"# {'=' * 91} #\n"
        policy = self.lintable("applications/app/files/policy.yml", box)
        argument_specs = self.lintable(
            "applications/app/meta/argument_specs.yml",
            box,
        )
        self.assertEqual(policy.kind, "yaml")
        self.assertEqual(argument_specs.kind, "role-arg-spec")
        for file in (policy, argument_specs):
            with self.subTest(kind=file.kind):
                findings = FMT_01.Fmt01().matchyaml(file)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].lineno, 1)
                self.assertEqual(
                    findings[0].message,
                    "banner line is 95 columns; every banner rule line is exactly 97",
                )

    def test_mixed_case_role_register(self):
        file = self.lintable(
            "operating_systems/Windows_Server_2025/tasks/probe.yml",
            """- name: 'PROCESS | Probe The Host'
  register: '__Windows_Server_2025_probe__'
  ansible.builtin.debug:
    msg: 'x'
""",
        )
        self.assertEqual(
            REG_01.Reg01().matchtask(tasks(file)[0], file=file),
            [],
        )

    def test_fail_fixture_round_trips_through_sarif(self):
        roles = discover(FAIL)
        findings = run_lint(FAIL.resolve(), str(FAIL), roles)
        actual = sorted(finding.text() for finding in findings)
        expected = (ROOT / "fixtures/style/expected-fail.txt").read_text().splitlines()
        self.assertEqual(actual, expected)
