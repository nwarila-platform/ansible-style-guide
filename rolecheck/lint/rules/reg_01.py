# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Enforce REG-01.

"A `register:` target is `'__<role>_<noun>__'`, single-quoted."

Not checked: `.changed` reads, `.rc` reads, and defaults on registered fields in `when:`
are deferred together because they require Jinja analysis of conditionals.
"""

import re
from collections.abc import Mapping
from typing import ClassVar

from ansiblelint.rules import AnsibleLintRule
from ansiblelint.yaml_utils import get_line_column


class Reg01(AnsibleLintRule):
    """Report malformed or incorrectly quoted register targets."""

    id = "REG-01"
    description = "A register: target is '__<role>_<noun>__', single-quoted"
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
        """Validate mapping ownership, target shape, and raw quoting in order."""

        if (
            file is None
            or file.base_kind != "text/yaml"
            or file.kind not in {"tasks", "handlers"}
        ):
            return []
        if "register" not in task.raw_task:
            return []
        register = task.raw_task["register"]
        role = file.path.parent.parent.name
        if isinstance(register, Mapping):
            diagnostic = (
                "register target must be a string before it can be "
                f"'__{role}_<noun>__'"
            )
            return [self._finding(self, task, file, diagnostic)]
        if not isinstance(register, str):
            return []
        if not re.fullmatch(
            rf"__{re.escape(role)}_[a-z0-9_]+__", register
        ):
            diagnostic = (
                f"register target '{register}' is not '__{role}_<noun>__'"
            )
            return [self._finding(self, task, file, diagnostic)]
        source_line = file.content.split("\n")[get_line_column(register)[0] - 1]
        if not re.fullmatch(
            rf" *(- )?register: '{re.escape(register)}' *(#.*)?",
            source_line,
        ):
            return [
                self._finding(
                    self,
                    task,
                    file,
                    "register target must be single-quoted",
                )
            ]
        return []
