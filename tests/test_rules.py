# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Assert the complete metadata contract for every custom lint rule."""

import importlib.util
import inspect
import unittest
from pathlib import Path

from ansiblelint.rules import AnsibleLintRule

RULES = Path(__file__).resolve().parents[1] / "rolecheck/lint/rules"
EXPECTED = {
    "fact_01": (
        "FACT-01",
        "set_fact does not appear in an application role's task files",
        ["idiom", "style"],
    ),
    "fmt_01": (
        "FMT-01",
        (
            "Every banner rule line is exactly 97 columns and every region closes "
            "with its own label"
        ),
        ["formatting", "style"],
    ),
    "fmt_02": (
        "FMT-02",
        (
            "A region label is '<Stage>: <Description>' with every description word "
            "capitalized"
        ),
        ["formatting", "style"],
    ),
    "loop_01": (
        "LOOP-01",
        (
            "Iterate with loop:, never with_*, and every loop carries a "
            "loop_control.label"
        ),
        ["idiom", "style"],
    ),
    "name_01": (
        "NAME-01",
        "Task names are 'STAGE | Title Case Imperative', single-quoted",
        ["formatting", "style"],
    ),
    "reg_01": (
        "REG-01",
        "A register: target is '__<role>_<noun>__', single-quoted",
        ["idiom", "style"],
    ),
}


def load_module(name):
    """Load a rule module by path without making rules a Python package."""

    spec = importlib.util.spec_from_file_location(f"test_{name}", RULES / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load rule module {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuleMetadataTests(unittest.TestCase):
    """Verify one and only one correctly described rule per module."""

    def assert_rule(self, name):
        module = load_module(name)
        classes = [
            candidate
            for _member, candidate in inspect.getmembers(module, inspect.isclass)
            if candidate is not AnsibleLintRule
            and issubclass(candidate, AnsibleLintRule)
            and candidate.__module__ == module.__name__
        ]
        self.assertEqual(len(classes), 1)
        rule = classes[0]
        rule_id, description, tags = EXPECTED[name]
        self.assertEqual(rule.id, rule_id)
        self.assertEqual(rule.description, description)
        self.assertEqual(rule.severity, "MEDIUM")
        self.assertEqual(rule.version_changed, "0.2.0")
        self.assertEqual(rule.tags, tags)
        self.assertIn("Not checked", module.__doc__)

    def test_fmt_01(self):
        self.assert_rule("fmt_01")

    def test_fmt_02(self):
        self.assert_rule("fmt_02")

    def test_name_01(self):
        self.assert_rule("name_01")

    def test_fact_01(self):
        self.assert_rule("fact_01")

    def test_loop_01(self):
        self.assert_rule("loop_01")

    def test_reg_01(self):
        self.assert_rule("reg_01")
