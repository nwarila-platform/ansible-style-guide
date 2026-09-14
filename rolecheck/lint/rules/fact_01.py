# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Enforce FACT-01.

"`set_fact` does not appear in an application role's task files. Derived values live
in block `vars:` (lazily evaluated, block-scoped) or come from `register`. Never
`set_fact` the name `ansible_facts`." The final clause is subsumed by the blanket ban.

Not checked: the loader's use is out of scope through the checker's central loader
exclusion, not through special handling in this rule.
Handlers and every role kind other than an application role are not judged, because the
sentence names "an application role's task files"; the owner has not yet amended it (D5),
and fixtures/style/applications/boundary_role/handlers/main.yml carries the case that
therefore goes unreported.
"""

from typing import ClassVar

from ansiblelint.rules import AnsibleLintRule


class Fact01(AnsibleLintRule):
    """Report set_fact in application-role task files."""

    id = "FACT-01"
    description = "set_fact does not appear in an application role's task files"
    severity = "MEDIUM"
    version_changed = "0.2.0"
    tags: ClassVar[list[str]] = ["idiom", "style"]

    def matchtask(self, task, file=None):
        """Check the task action after applying the exact path and kind scope."""

        if file is None or file.base_kind != "text/yaml" or file.kind != "tasks":
            return []
        if file.path.parent.parent.parent.name != "applications":
            return []
        if task.action not in {
            "set_fact",
            "ansible.builtin.set_fact",
            "ansible.legacy.set_fact",
        }:
            return []
        diagnostic = (
            "set_fact does not appear in an application role's task files; derive "
            "the value in block vars: or read it from register"
        )
        return [
            self.create_matcherror(
                message=diagnostic,
                details=diagnostic,
                lineno=task.line,
                filename=file,
            )
        ]
