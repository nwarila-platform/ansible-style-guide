#!/usr/bin/env python3
"""Shared encoding for the split/join pair.

split_spec.py and join_spec.py must be exact inverses, so the rules that decide
where front matter ends and how a slice of the document is stored live here
once. A second implementation is a second thing to drift.

The encoding is line-exact on purpose. Storing a slice as text and recovering it
with `.rstrip()` loses the blank line that separates two rules, and a check that
compares a reassembly built in memory never notices -- both of those were real
defects in the first version of these tools.

Every read and write goes through bytes. `Path.read_text` applies universal
newline translation, so a CRLF source decodes to LF and then "round-trips"
byte-identically to a file eight bytes shorter than the one it was given -- the
check passes while the bytes change. read_document/write_document below are the
only way these tools touch the disk.
"""
import json
import pathlib
import re

FRONT_MATTER = re.compile(r'\A---\n(?P<fm>.*?)\n---\n\n', re.DOTALL)


def read_document(path):
    """Read a UTF-8 file without translating its line endings."""
    return pathlib.Path(path).read_bytes().decode("utf-8")


def write_document(path, text):
    """Write a UTF-8 file without translating its line endings."""
    pathlib.Path(path).write_bytes(text.encode("utf-8"))


def encode(lines):
    """Serialise a list of document lines.

    The empty list and the single empty line are different slices and must not
    collide: [] stores as no bytes at all, [""] stores as one newline.
    """
    return "\n".join(lines) + "\n" if lines else ""


def decode(text):
    """Recover the list of lines that encode() was given."""
    return text[:-1].split("\n") if text else []


def render_front_matter(pairs):
    """Render an ordered mapping as YAML front matter, values JSON-quoted.

    JSON quoting is what makes the value readable back exactly: a title holding
    a colon, a quote or a backslash survives without a YAML parser here.
    """
    body = "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in pairs)
    return f"---\n{body}\n---\n\n"


def read_page(path):
    """Return (front matter mapping, list of document lines) for one page."""
    text = read_document(path)
    match = FRONT_MATTER.match(text)
    if not match:
        raise SystemExit(f"{path}: no front matter; this file was not written by split_spec.py")
    fields = {}
    for line in match.group("fm").split("\n"):
        key, sep, value = line.partition(":")
        if not sep:
            raise SystemExit(f"{path}: front matter line is not `key: value`: {line!r}")
        fields[key.strip()] = json.loads(value.strip())
    return fields, decode(text[match.end():])


def write_page(path, pairs, lines):
    """Write one page: front matter, one blank line, then the slice verbatim."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_document(path, render_front_matter(pairs) + encode(lines))
    return path


def section_slug(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
