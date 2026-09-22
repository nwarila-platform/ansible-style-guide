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


LOADER_DIGEST_FILE = Path("meta") / "loader-digest.txt"


def published_loader_digest(tree):
    """Return the loader digest a tree publishes, or None.

    LOADER-01 identifies the shared loader by hash, so the hash is a value the
    framework and this checker must agree on. Hard-coding it here made every
    consumer role fail the moment the framework reformatted its loader. The
    framework now publishes the digest it ships (`meta/loader-digest.txt`,
    migration item 6) and this reads it, so the two cannot drift.

    A tree that publishes nothing -- every consumer repository -- falls back to
    LOADER_SHA256, which stays the compiled-in default.
    """
    for folder in (tree, *tree.parents):
        candidate = folder / LOADER_DIGEST_FILE
        if candidate.is_file():
            word = candidate.read_text(encoding="utf-8").split()
            if word and re.fullmatch(r"[0-9a-f]{64}", word[0]):
                return word[0]
            return None
    return None


def parser():
    """Build the complete public argument parser."""

    root = argparse.ArgumentParser(prog="rolecheck")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check")
    check.add_argument("--report-only", action="store_true")
    check.add_argument("--format", choices=("text", "json"), default="text")
    check.add_argument("--loader-digest", default=None)
    check.add_argument("paths", nargs="+")
    return root


def main(argv=None):
    """Run the selected command and return its process status."""

    arguments = parser().parse_args(argv)
    if arguments.loader_digest is not None and not re.fullmatch(
        r"[0-9a-f]{64}", arguments.loader_digest
    ):
        print(
            "error: --loader-digest must be 64 lowercase hexadecimal characters",
            file=sys.stderr,
        )
        return 2

    all_findings = []
    roles_by_root = []
    all_roles = []
    for raw in arguments.paths:
        given = Path(raw)
        if given.is_symlink():
            print(
                f"error: {raw} is a symbolic link; give the role folder or tree itself",
                file=sys.stderr,
            )
            return 2
        path = given.resolve()
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
        digest = arguments.loader_digest or published_loader_digest(path) or LOADER_SHA256
        for role in roles:
            all_findings.extend(
                check_role(
                    role.path,
                    role.role_path,
                    role.kind,
                    digest,
                )
            )
        all_findings.extend(run_lint(path, raw, roles, digest))

    if arguments.format == "json":
        sys.stdout.write(json_report(all_findings, all_roles))
    else:
        sys.stdout.write(text_report(all_findings, all_roles, arguments.paths))
    return exit_status(all_findings, arguments.report_only)


if __name__ == "__main__":
    raise SystemExit(main())
