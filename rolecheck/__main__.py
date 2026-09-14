# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Provide the rolecheck command-line interface."""

import argparse
import re
import sys
from pathlib import Path

from . import __version__
from .discover import discover
from .lint import run_lint
from .report import exit_status, json_report, text_report
from .structure import LOADER_SHA256, check_role


def parser():
    """Build the complete public argument parser."""

    root = argparse.ArgumentParser(prog="rolecheck")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check")
    check.add_argument("--report-only", action="store_true")
    check.add_argument("--format", choices=("text", "json"), default="text")
    check.add_argument("--loader-digest", default=LOADER_SHA256)
    check.add_argument("paths", nargs="+")
    return root


def main(argv=None):
    """Run the selected command and return its process status."""

    arguments = parser().parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{64}", arguments.loader_digest):
        print(
            "error: --loader-digest must be 64 lowercase hexadecimal characters",
            file=sys.stderr,
        )
        return 2

    all_findings = []
    roles_by_root = []
    all_roles = []
    for raw in arguments.paths:
        path = Path(raw).resolve()
        roles = discover(path)
        if not roles:
            print(f"error: no role folder found in {raw}", file=sys.stderr)
            return 2
        roles_by_root.append((raw, path, roles))
        all_roles.extend(roles)

    role_paths = [role.role_path for role in all_roles]
    if len(role_paths) != len(set(role_paths)):
        print("error: role paths collide across PATH arguments", file=sys.stderr)
        return 2

    for raw, path, roles in roles_by_root:
        for role in roles:
            all_findings.extend(
                check_role(
                    role.path,
                    role.role_path,
                    role.kind,
                    arguments.loader_digest,
                )
            )
        all_findings.extend(
            run_lint(path, raw, roles, arguments.loader_digest)
        )

    if arguments.format == "json":
        sys.stdout.write(json_report(all_findings, all_roles))
    else:
        sys.stdout.write(text_report(all_findings, all_roles, arguments.paths))
    return exit_status(all_findings, arguments.report_only)


if __name__ == "__main__":
    raise SystemExit(main())
