# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Check the canonical scaffold, loader, defaults key, and required files."""

import hashlib
from collections.abc import Mapping
from pathlib import Path

import yaml

from .report import Finding

LOADER_SHA256 = "62925c4718913f8c8703d1da221755890c0ab106d5f8c42a420f5b49f7d81652"
SCAFFOLD = (
    "defaults",
    "files",
    "handlers",
    "library",
    "lookup_plugins",
    "meta",
    "module_utils",
    "molecule",
    "tasks",
    "templates",
    "tests",
    "vars",
)
REQUIRED = ("README.md", "meta/main.yml", "defaults/main.yml", "tasks/main.yml")


def _finding(role_path, path, rule_id, message):
    return Finding(
        role_path,
        f"{role_path}/{path}",
        1,
        rule_id,
        message,
        "structure",
    )


def check_role(role_dir, name, kind, loader_digest):
    """Return structural findings for one role folder."""

    role_dir = Path(role_dir)
    role_path = name if isinstance(name, str) else str(name)
    findings = []
    for directory in SCAFFOLD:
        if not (role_dir / directory).is_dir():
            findings.append(
                _finding(
                    role_path,
                    directory,
                    "SCAFFOLD-01",
                    f"role scaffold directory '{directory}' is missing",
                )
            )

    task_main = role_dir / "tasks/main.yml"
    if kind == "application" and task_main.is_file():
        found = hashlib.sha256(task_main.read_bytes()).hexdigest()
        if found != loader_digest:
            findings.append(
                _finding(
                    role_path,
                    "tasks/main.yml",
                    "LOADER-01",
                    "tasks/main.yml is not the shared loader; sha256 "
                    f"{found[:16]} differs from {loader_digest[:16]}",
                )
            )

    defaults = role_dir / "defaults/main.yml"
    if kind == "application" and defaults.is_file():
        try:
            value = yaml.safe_load(defaults.read_text())
        except (OSError, UnicodeError, yaml.YAMLError):
            value = None
        expected = f"{Path(role_dir).name}_defaults"
        if not isinstance(value, Mapping) or expected not in value:
            if isinstance(value, Mapping) and value:
                keys = ", ".join(sorted(str(key) for key in value))
            else:
                keys = "nothing"
            findings.append(
                _finding(
                    role_path,
                    "defaults/main.yml",
                    "SCAFFOLD-02",
                    f"defaults/main.yml defines no top-level '{expected}' key "
                    f"(found: {keys})",
                )
            )

    for required in REQUIRED:
        if not (role_dir / required).is_file():
            findings.append(
                _finding(
                    role_path,
                    required,
                    "SCAFFOLD-03",
                    f"required file {required} is missing",
                )
            )
    return findings
