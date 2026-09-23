#!/usr/bin/env python3
"""Regenerate the .gitignore allowlist from the working tree.

The allowlist is default-deny with no wildcard allowances, so every tracked file
and every directory on the path to one is named. That is 160-odd lines for this
repository and it grows by one every time a rule is added, which is exactly the
kind of list a person maintains correctly until the day they do not -- the
sidebar in this same repository had quietly lost two pages the same way.

  gen_allowlist.py           rewrite .gitignore in place
  gen_allowlist.py --check   exit 1 if .gitignore does not match the tree

--check is what CI runs: it fails on a file that was added without being
allowed, and equally on an allowlist entry for a file that no longer exists.
"""
import pathlib
import sys

# Build products and local process artifacts: `make selftest` writes .audit/,
# `make fleet` writes reports/, ruff and pytest write their caches, and the site
# build writes build/ and .docusaurus/. AGENTS.md and CLAUDE.md are deliberate --
# per the workspace convention they live in every clone and are never committed.
SKIP_DIRS = {".git", "node_modules", "build", ".docusaurus", "__pycache__",
             ".ruff_cache", ".pytest_cache", ".mypy_cache", ".audit", "reports",
             ".venv", "dist"}
SKIP_FILES = {"AGENTS.md", "CLAUDE.md"}
SKIP_SUFFIXES = {".pyc"}
# Named by the distribution, so it cannot be listed above: a wheel build drops
# rolecheck.egg-info/ into the tree, and the check duly reported six files that
# nobody had allowed.
SKIP_DIR_SUFFIXES = (".egg-info",)

SPINE_HEADER = "# --- [ directory spine ] ---"
FILES_HEADER = "# --- [ allowed files ] ---"

# A .gitignore entry is a pattern, not a path. `docs/rule[1].md` is a valid
# filename and a character class, and an entry ending in a space is a pattern
# ending in nothing -- in both cases the generated line looks right and Git goes
# on ignoring the file. Escaping is what makes "no wildcard allowances" true
# rather than merely intended.
PATTERN_METACHARACTERS = str.maketrans({c: "\\" + c for c in "\\*?[]"})


def as_pattern(name):
    """Escape a path so Git matches it literally."""
    escaped = name.translate(PATTERN_METACHARACTERS)
    return escaped[:-1] + "\\ " if escaped.endswith(" ") else escaped


def walk(folder, root):
    """Yield every file under `folder`, treating a symlink as a file.

    Git tracks a symlink as a blob holding its target and never descends into
    one. Following them here would both miss the link itself -- `is_file()` is
    false for a dangling link and true for a link to a directory, so a link was
    simply never allowed -- and risk walking a cycle.
    """
    for path in sorted(folder.iterdir()):
        if path.name in SKIP_DIRS or path.name.endswith(SKIP_DIR_SUFFIXES):
            continue
        if path.is_symlink() or path.is_file():
            yield path
        elif path.is_dir():
            yield from walk(path, root)


def tracked_paths(root):
    """Every file the repository should track, and every directory above one."""
    files = []
    for path in walk(root, root):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS or part.endswith(SKIP_DIR_SUFFIXES)
               for part in relative.parts):
            continue
        if relative.name in SKIP_FILES or relative.suffix in SKIP_SUFFIXES:
            continue
        files.append(relative.as_posix())
    files.sort()
    folders = sorted({parent.as_posix()
                      for name in files
                      for parent in pathlib.PurePosixPath(name).parents
                      if parent.as_posix() != "."})
    return folders, files


def render(existing, folders, files):
    """Return the .gitignore text: the prose kept, the two lists regenerated."""
    lines = existing.split("\n")
    spine = next((i for i, text in enumerate(lines) if text.startswith(SPINE_HEADER)), None)
    allowed = next((i for i, text in enumerate(lines) if text.startswith(FILES_HEADER)), None)
    # Both must be present and in order. Swapping them made render() slice
    # backwards, silently duplicating every generated entry and growing the
    # file by a third rather than failing.
    if spine is None or allowed is None or not spine < allowed:
        raise SystemExit(
            f".gitignore must contain {SPINE_HEADER!r} and then {FILES_HEADER!r}, in that order; "
            f"found spine at {spine} and files at {allowed}")

    # The commentary under each header is prose worth keeping; the entries under
    # it are not. Keep every line down to the first entry of each block.
    def prose(start, stop):
        out = []
        for line in lines[start:stop]:
            if line.startswith("!/"):
                break
            out.append(line)
        return out

    return "\n".join(
        lines[:spine]
        + prose(spine, allowed)
        + [f"!/{as_pattern(name)}/" for name in folders]
        + [""]
        + prose(allowed, len(lines))
        + [f"!/{as_pattern(name)}" for name in files]
        + [""]
    )


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    gitignore = root / ".gitignore"
    folders, files = tracked_paths(root)
    existing = gitignore.read_text(encoding="utf-8")
    wanted = render(existing, folders, files)

    if "--check" in sys.argv:
        if existing != wanted:
            missing = [f for f in files if f"!/{as_pattern(f)}\n" not in existing]
            allowed_patterns = {as_pattern(f) for f in files}
            stale = [entry[2:] for entry in existing.split("\n")
                     if entry.startswith("!/") and not entry.endswith("/")
                     and entry[2:] not in allowed_patterns]
            print("::error::.gitignore does not match the working tree.")
            for name in missing:
                print(f"  not allowed, but present: {name}")
            for name in stale:
                print(f"  allowed, but absent:      {name}")
            print("  run: python3 tools/gen_allowlist.py")
            return 1
        print(f"  allowlist: {len(files)} files, {len(folders)} directories, matches the tree")
        return 0

    gitignore.write_text(wanted, encoding="utf-8")
    print(f"  wrote {len(files)} file entries and {len(folders)} directory entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
