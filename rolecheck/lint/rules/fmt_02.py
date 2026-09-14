# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Enforce FMT-02.

"A region label is `<Stage>: <Description>` where every word of the description is
capitalized, matching NAME-01. Stage is `Begin`, `Process`, `End` or `Always` in task
files."

Not checked: playbook `Play` and `Roles` labels are deferred; deciding whether a file
needs regions requires review; the task token inside `always:` is enforced by NAME-01.
"""

import re
from typing import ClassVar

from ansiblelint.rules import AnsibleLintRule

OPEN = re.compile(r"^ *#region ------ \[ (?P<label>.+?) \] -+ #$")
LABEL = re.compile(r"^(Begin|Process|End|Always): (?P<description>.+)$")


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


class Fmt02(AnsibleLintRule):
    """Report invalid task-file region labels."""

    id = "FMT-02"
    description = (
        "A region label is '<Stage>: <Description>' with every description word capitalized"
    )
    severity = "MEDIUM"
    version_changed = "0.2.0"
    tags: ClassVar[list[str]] = ["formatting", "style"]

    def matchyaml(self, file):
        """Validate each task-file opening region marker."""

        if file is None or file.base_kind != "text/yaml" or file.kind != "tasks":
            return []
        findings = []
        for line_number, line in enumerate(file.content.split("\n"), 1):
            opened = OPEN.match(line)
            if not opened:
                continue
            label = opened.group("label")
            parsed = LABEL.fullmatch(label)
            if not parsed:
                diagnostic = (
                    f"region label '{label}' is not '<Stage>: <Description>' with Stage "
                    "one of Begin, Process, End, Always"
                )
            else:
                words = bad_words(parsed.group("description"))
                if not words:
                    continue
                diagnostic = (
                    f"region label '{label}' has uncapitalized words: "
                    f"{', '.join(words)}"
                )
            findings.append(
                self.create_matcherror(
                    message=diagnostic,
                    details=diagnostic,
                    lineno=line_number,
                    filename=file,
                )
            )
        return findings
