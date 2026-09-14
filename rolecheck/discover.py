# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Discover role folders and assign their display paths and kinds."""

import os
from dataclasses import dataclass
from pathlib import Path

NAMESPACE_NAMES = {
    "applications",
    "host_roles",
    "operating_systems",
    "roles",
    "utilities",
}
PRUNE_NAMES = {
    ".audit",
    ".cache",
    ".compose",
    ".frameworks",
    ".git",
    ".worktrees",
    "node_modules",
}


@dataclass(frozen=True)
class Role:
    """A discovered role and its report metadata."""

    path: Path
    role_path: str
    name: str
    kind: str


def is_role_folder(path):
    """Return whether path is an immediate child of a role namespace."""

    candidate = Path(path)
    return candidate.is_dir() and candidate.parent.name in NAMESPACE_NAMES


def discover(given):
    """Return every role below given according to the namespace contract."""

    root = Path(given)
    if root.is_symlink():
        return []
    root = root.resolve()
    if not root.is_dir():
        return []
    direct = is_role_folder(root)
    paths = [root] if direct else []
    if not direct:
        for current, directories, _files in os.walk(root, followlinks=False):
            current_path = Path(current)
            directories[:] = sorted(
                name
                for name in directories
                if name not in PRUNE_NAMES
                and not (current_path / name).is_symlink()
            )
            for name in directories:
                candidate = current_path / name
                if is_role_folder(candidate):
                    paths.append(candidate)
    base = root.parent if direct else root
    return [
        Role(
            path=path,
            role_path=path.relative_to(base).as_posix(),
            name=path.name,
            kind="application" if path.parent.name == "applications" else "other",
        )
        for path in sorted(set(paths))
    ]
