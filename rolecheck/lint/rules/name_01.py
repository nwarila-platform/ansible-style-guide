# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Enforce NAME-01.

"Task names are `'STAGE | Title Case Imperative'`, single-quoted, one space either side
of the pipe. STAGE is closed: `BEGIN`, `PROCESS`, `END`, `VALIDATE`. A task inside an
`always:` takes the enclosing stage's token. Handlers are exempt." The file-token
relation for `validate.yml` is enforced in both directions.

Not checked: imperative mood and the BEGIN/PROCESS/END stage meanings require review;
playbook tokens are deferred; name-first belongs to KEY-01.
"""

import re
from typing import ClassVar

from ansiblelint.rules import AnsibleLintRule
from ansiblelint.yaml_utils import get_line_column

QUOTED = re.compile(r"^ *(- )?name: '(?P<body>.*)' *(#.*)?$")
SHAPE = re.compile(
    r"^(?P<token>BEGIN|PROCESS|END|VALIDATE) \| (?P<title>\S.*)$"
)


def bad_words(value):
    """Return words that fail the shared strict Title Case test."""

    result = []
    for word in value.split():
        tested = word.lstrip("([{'\"")
        if not re.search(r"[A-Za-z]", tested):
            continue
        if not re.match(r"[A-Z0-9]", tested):
            result.append(word)
    return result


class Name01(AnsibleLintRule):
    """Report task-name syntax, token, and capitalization defects."""

    id = "NAME-01"
    description = "Task names are 'STAGE | Title Case Imperative', single-quoted"
    severity = "MEDIUM"
    version_changed = "0.2.0"
    tags: ClassVar[list[str]] = ["formatting", "style"]

    @staticmethod
    def _source_line(file, scalar):
        return file.content.split("\n")[get_line_column(scalar)[0] - 1]

    def _parsed_name(self, file, mapping):
        name = mapping.get("name")
        if not isinstance(name, str):
            return None
        quoted = QUOTED.fullmatch(self._source_line(file, name))
        if not quoted:
            return None
        return SHAPE.fullmatch(quoted.group("body"))

    def matchtask(self, task, file=None):
        """Validate one task name in rule precedence order."""

        if file is None or file.base_kind != "text/yaml" or file.kind != "tasks":
            return []
        name = task.raw_task.get("name")
        if name is None:
            return []
        quoted = QUOTED.fullmatch(self._source_line(file, name))
        if not quoted:
            diagnostic = "task name must be single-quoted"
        else:
            shaped = SHAPE.fullmatch(quoted.group("body"))
            if not shaped:
                diagnostic = (
                    "task name is not 'STAGE | Title Case Imperative' with STAGE one "
                    "of BEGIN, PROCESS, END, VALIDATE and one space either side of the pipe"
                )
            else:
                token = shaped.group("token")
                if file.path.name == "validate.yml" and token != "VALIDATE":
                    diagnostic = (
                        f"task name in validate.yml carries {token}; contract asserts "
                        "are VALIDATE"
                    )
                elif file.path.name != "validate.yml" and token == "VALIDATE":
                    diagnostic = (
                        "VALIDATE is reserved for validate.yml; this file's stages are "
                        "BEGIN, PROCESS, END"
                    )
                else:
                    words = bad_words(shaped.group("title"))
                    if not words:
                        return []
                    diagnostic = (
                        f"task name has uncapitalized words: {', '.join(words)}"
                    )
        return [
            self.create_matcherror(
                message=diagnostic,
                details=diagnostic,
                lineno=task.line,
                filename=file,
            )
        ]

    def _check_descendants(self, file, nodes, expected):
        findings = []
        if not isinstance(nodes, list):
            return findings
        for mapping in nodes:
            if not isinstance(mapping, dict):
                continue
            parsed = self._parsed_name(file, mapping)
            if parsed and parsed.group("token") != expected:
                diagnostic = (
                    f"task inside an always: carries {parsed.group('token')} but the "
                    f"enclosing stage is {expected}"
                )
                findings.append(
                    self.create_matcherror(
                        message=diagnostic,
                        details=diagnostic,
                        lineno=get_line_column(mapping.get("name"))[0],
                        filename=file,
                    )
                )
            for key in ("block", "rescue", "always"):
                findings.extend(
                    self._check_descendants(file, mapping.get(key), expected)
                )
        return findings

    def _walk(self, file, nodes):
        findings = []
        if not isinstance(nodes, list):
            return findings
        for mapping in nodes:
            if not isinstance(mapping, dict):
                continue
            parsed = self._parsed_name(file, mapping)
            if "always" in mapping and parsed:
                findings.extend(
                    self._check_descendants(
                        file,
                        mapping.get("always"),
                        parsed.group("token"),
                    )
                )
            else:
                findings.extend(self._walk(file, mapping.get("always")))
            for key in ("block", "rescue"):
                findings.extend(self._walk(file, mapping.get(key)))
        return findings

    def matchyaml(self, file):
        """Enforce enclosing tokens throughout every always subtree."""

        if file is None or file.base_kind != "text/yaml" or file.kind != "tasks":
            return []
        return self._walk(file, file.data)
