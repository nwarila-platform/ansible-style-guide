# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Run ansible-lint once per root and translate its SARIF output."""

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from .report import Finding
from .structure import LOADER_SHA256

WARNING = re.compile(r"^(WARNING|\[[^]]*WARNING\])")
FATAL_LISTING = re.compile(r"^WARNING  Listing \d+ violation\(s\) that are fatal$")
OFFLINE_DEPENDENCIES = (
    "WARNING  Skipped installing collection dependencies due to running in offline mode."
)


def _tool_finding(root_display, message):
    return Finding(None, root_display, 0, "TOOL", message, "tool")


def _owner(artifact, roles):
    path = Path(artifact).resolve()
    for role in roles:
        try:
            suffix = path.relative_to(role.path)
        except ValueError:
            continue
        return role, f"{role.role_path}/{suffix.as_posix()}"
    return None, Path(artifact).as_posix()


def build_command(project, roles, loader_digest, sarif):
    """Build the exact ansible-lint argv for one root."""

    package = Path(__file__).parent
    exclusions = []
    for role in roles:
        loader = role.path / "tasks/main.yml"
        if (
            loader.is_file()
            and hashlib.sha256(loader.read_bytes()).hexdigest() == loader_digest
        ):
            exclusions.append(loader)
    command = [
        "ansible-lint",
        "-c",
        str(package / "lint/ansible-lint.yml"),
        "--yamllint-file",
        str(package / "lint/yamllint.yml"),
        "--project-dir",
        str(project),
        "--offline",
        "--nocolor",
        "--sarif-file",
        str(sarif),
    ]
    if exclusions:
        command.append("--exclude")
        command.extend(str(path) for path in exclusions)
    command.append("--")
    command.extend(str(role.path) for role in roles)
    return command


def _parse_sarif(sarif, roles):
    payload = json.loads(sarif.read_text())
    findings = []
    for result in payload["runs"][0]["results"]:
        physical = result["locations"][0]["physicalLocation"]
        role, display = _owner(physical["artifactLocation"]["uri"], roles)
        findings.append(
            Finding(
                role.role_path if role else None,
                display,
                physical["region"]["startLine"],
                result["ruleId"],
                result["message"]["text"],
                "style" if role else "tool",
            )
        )
    return findings


def run_lint(project, root_display, roles, loader_digest=LOADER_SHA256):
    """Run and parse ansible-lint, surfacing failures and qualifying warnings."""

    with tempfile.NamedTemporaryFile(
        prefix="rolecheck-", suffix=".sarif", delete=False
    ) as handle:
        sarif = Path(handle.name)
    sarif.unlink()
    command = build_command(project, roles, loader_digest, sarif)
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError as error:
        sarif.unlink(missing_ok=True)
        return [_tool_finding(root_display, str(error))]

    findings = []
    for line in completed.stderr.splitlines():
        if (
            WARNING.match(line)
            and not FATAL_LISTING.fullmatch(line)
            and line != OFFLINE_DEPENDENCIES
        ):
            findings.append(_tool_finding(root_display, line))

    sarif_error = False
    try:
        findings.extend(_parse_sarif(sarif, roles))
    except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError):
        sarif_error = True
    finally:
        sarif.unlink(missing_ok=True)

    if completed.returncode not in {0, 2} or sarif_error:
        message = " | ".join(
            line for line in completed.stderr.splitlines() if line
        )
        findings.append(_tool_finding(root_display, message))
    return findings
