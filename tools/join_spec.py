#!/usr/bin/env python3
"""Reassemble the split pages into the single specification document.

The inverse of split_spec.py, and the only implementation of that inverse:
split_spec.py imports join() to verify itself, so the two cannot disagree about
what a page means.

It reads nothing but the files in DOCSDIR. That is the point -- verifying a
split against the source it was made from proves only that the source was read,
not that the pages carry it.

  join_spec.py DOCSDIR > SPEC.md
"""
import pathlib
import sys

from specdoc import read_document, read_page

ORDER = "_order.txt"
RULES = "_rules.txt"


def read_order(docs):
    """Return [(kind, slug)] in document order, from the manifest split wrote."""
    path = docs / ORDER
    if not path.is_file():
        raise SystemExit(f"missing {path}: it records the section order the join replays")
    out = []
    for number, line in enumerate(read_document(path).split("\n"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kind, sep, slug = line.partition(":")
        if not sep or kind not in ("rules", "page") or not slug:
            raise SystemExit(f"{path}:{number}: expected `rules:<slug>` or `page:<slug>`, got {line!r}")
        out.append((kind, slug))
    return out


def join(docs):
    """Return the whole specification as a single string."""
    docs = pathlib.Path(docs)
    _, lines = read_page(docs / "intro.md")

    for kind, slug in read_order(docs):
        if kind == "rules":
            folder = docs / "rules" / slug
            fields, preamble = read_page(folder / "index.md")
            lines.append("## " + fields["title"])
            lines.extend(preamble)
            listing = folder / RULES
            if not listing.is_file():
                raise SystemExit(f"missing {listing}: it records the rule order within the section")
            for rule_id in read_document(listing).split():
                _, body = read_page(folder / f"{rule_id.lower()}.md")
                lines.extend(body)
        else:
            fields, preamble = read_page(docs / f"{slug}.md")
            lines.append("## " + fields["title"])
            lines.extend(preamble)

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__.strip().split("\n")[-1].strip())
    sys.stdout.write(join(sys.argv[1]))
