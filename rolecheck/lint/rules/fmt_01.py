# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Enforce FMT-01.

"Every banner rule line is exactly 97 columns, including the file-header box, the
`# --- [ Description ] --- #` rule, region markers and sibling separators. `#region`
carries six dashes before the label and `#endregion` three, so the `[` aligns between
an open/close pair; the labels are byte-identical."

Not checked: the `ansible/**` path scope is realized by the paths the caller supplies;
this rule judges every YAML lintable it receives.
"""

import re
from typing import ClassVar

from ansiblelint.rules import AnsibleLintRule

OPEN = re.compile(r"^(?P<indent> *)#region ------ \[ (?P<label>.+?) \] -+ #$")
CLOSE = re.compile(r"^(?P<indent> *)#endregion --- \[ (?P<label>.+?) \] -+ #$")
BOX = re.compile(r"^# =+ #$")
DESCRIPTION = re.compile(r"^# --- \[ Description \] -+ #$")
SEPARATOR = re.compile(r"^ *# -+ #$")
ANY_MARKER = re.compile(r"^ *#(end)?region\b")


class Fmt01(AnsibleLintRule):
    """Report banner geometry and region-pairing defects."""

    id = "FMT-01"
    description = (
        "Every banner rule line is exactly 97 columns and every region closes "
        "with its own label"
    )
    severity = "MEDIUM"
    version_changed = "0.2.0"
    tags: ClassVar[list[str]] = ["formatting", "style"]

    @staticmethod
    def _finding(rule, file, line, diagnostic):
        return rule.create_matcherror(
            message=diagnostic,
            details=diagnostic,
            lineno=line,
            filename=file,
        )

    def matchyaml(self, file):
        """Check all recognized banner lines and pair every valid marker."""

        if file is None or file.base_kind != "text/yaml":
            return []
        findings = []
        stack = []
        for line_number, line in enumerate(file.content.split("\n"), 1):
            opened = OPEN.match(line)
            closed = CLOSE.match(line)
            recognized = (
                opened
                or closed
                or BOX.match(line)
                or DESCRIPTION.match(line)
                or SEPARATOR.match(line)
            )
            if recognized and len(line) != 97:
                diagnostic = (
                    f"banner line is {len(line)} columns; every banner rule line "
                    "is exactly 97"
                )
                findings.append(self._finding(self, file, line_number, diagnostic))
            if ANY_MARKER.match(line) and not (opened or closed):
                diagnostic = (
                    "malformed region marker; expected '#region ------ [ Label ] ---- #' "
                    "or '#endregion --- [ Label ] ---- #'"
                )
                findings.append(self._finding(self, file, line_number, diagnostic))
                continue
            if opened:
                stack.append(
                    (len(opened.group("indent")), opened.group("label"), line_number)
                )
                continue
            if not closed:
                continue
            if not stack:
                findings.append(
                    self._finding(
                        self,
                        file,
                        line_number,
                        "endregion without an open region",
                    )
                )
                continue
            indent, label, open_line = stack.pop()
            if closed.group("label") != label:
                diagnostic = (
                    f"endregion label '{closed.group('label')}' does not match the "
                    f"region opened at line {open_line} ('{label}')"
                )
                findings.append(self._finding(self, file, line_number, diagnostic))
            elif len(closed.group("indent")) != indent:
                diagnostic = (
                    "endregion at a different indentation than the region opened "
                    f"at line {open_line}"
                )
                findings.append(self._finding(self, file, line_number, diagnostic))
        for _indent, _label, open_line in stack:
            findings.append(
                self._finding(
                    self,
                    file,
                    open_line,
                    "region opened here is never closed",
                )
            )
        return findings
