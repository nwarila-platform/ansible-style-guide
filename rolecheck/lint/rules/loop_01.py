# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Enforce LOOP-01.

"Iterate with `loop:`; `with_*` never appears. Every loop carries a
`loop_control.label`." Any present `loop_var` is also checked for the required dunder
shape.

Not checked: FLOW-01 folding is disputed; whether a loop variable was necessary requires
review.
"""

import re
from collections.abc import Mapping
from typing import ClassVar

from ansiblelint.rules import AnsibleLintRule


class Loop01(AnsibleLintRule):
    """Report deprecated loops, missing labels, and bare loop variables."""

    id = "LOOP-01"
    description = (
        "Iterate with loop:, never with_*, and every loop carries a loop_control.label"
    )
    severity = "MEDIUM"
    version_changed = "0.2.0"
    tags: ClassVar[list[str]] = ["idiom", "style"]

    @staticmethod
    def _finding(rule, task, file, diagnostic):
        return rule.create_matcherror(
            message=diagnostic,
            details=diagnostic,
            lineno=task.line,
            filename=file,
        )

    def matchtask(self, task, file=None):
        """Return one finding for every independently violated loop clause."""

        if (
            file is None
            or file.base_kind != "text/yaml"
            or file.kind not in {"tasks", "handlers"}
        ):
            return []
        keys = [
            str(key)
            for key in task.raw_task
            if not str(key).startswith("__")
        ]
        loop_control = task.raw_task.get("loop_control")
        findings = []
        for key in keys:
            if key.startswith("with_"):
                diagnostic = f"{key} is not used; iterate with loop:"
                findings.append(self._finding(self, task, file, diagnostic))
        if "loop" in keys and (
            not isinstance(loop_control, Mapping)
            or "label" not in loop_control
            or not isinstance(loop_control["label"], str)
            or loop_control["label"] == ""
        ):
            findings.append(
                self._finding(
                    self,
                    task,
                    file,
                    "loop without loop_control.label (a non-empty string)",
                )
            )
        if (
            isinstance(loop_control, Mapping)
            and "loop_var" in loop_control
            and not re.fullmatch(
                r"__[a-z0-9_]+__", str(loop_control["loop_var"])
            )
        ):
            diagnostic = (
                f"loop_var '{loop_control['loop_var']}' is not dunder-named (__name__)"
            )
            findings.append(self._finding(self, task, file, diagnostic))
        return findings
