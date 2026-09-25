#!/usr/bin/env python3
"""Split the monolithic Ansible style specification into Docusaurus pages.

Each rule becomes one page carrying its tier and `Checked by:` as front matter,
so the values a rule states are machine-readable next to the rule. The checker
does not read them yet -- FLOOR-01 still hardcodes 2.18 against a rule that says
2.21 -- so this makes that drift fixable, not fixed. It is the same drift that
produced three defects on 2026-09-22: FLOOR-01's floor, LOADER-01's digest and
SPEC-01's contract were each hardcoded while the specification said otherwise.

Losing prose while reformatting is the failure mode here, so this does not trust
itself: it reassembles the pages with join_spec.py -- reading the files it just
wrote, not the source it read -- and refuses unless the result is byte-identical
to the source. Verifying against an in-memory copy of the source is what let an
earlier version drop the document's whole head and still report success.

Ordering is recorded, never inferred. `_order.txt` holds the section order and
each section's `_rules.txt` holds its rule order, so neither the join nor the
published sidebar depends on how a filesystem happens to sort names -- which is
not document order for either the sections or the rules.

  split_spec.py SPEC.md OUTDIR
"""
import json
import pathlib
import re
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from join_spec import join, read_order
from specdoc import read_document, section_slug, write_document, write_page

# A rule id is a letter-and-digit family, a number, and an optional variant
# suffix. The family permitted letters only until 2026-09-23, so a ruling that
# named a rule `YAML2-01` published its text as section prose and no rule page
# at all -- silently, round trip intact. LOOKS_LIKE_RULE is deliberately wider
# than RULE so the split can refuse rather than repeat that.
RULE = re.compile(r'^\*\*([A-Z][A-Z0-9]*-\d+[a-z]?)\*\*\s*(.*)$')
# Wide on purpose, and wider than it looks like it needs to be. Anything matching
# this and not RULE is refused rather than published as prose: YAML-SCHEMA-01,
# WHEN-01A and 2FA-01 are all spellings a future ruling could reasonably use, and
# each one silently became section text.
LOOKS_LIKE_RULE = re.compile(r'^\*\*([A-Za-z0-9][A-Za-z0-9-]*-\d+[A-Za-z]?)\*\*')
FENCE = re.compile(r'^\s{0,3}(`{3,}|~{3,})[ \t]*(.*)$')
TIER = re.compile(r'^((?:`[^`]+`(?:\s*(?:/|→)\s*)?)+(?:\([^)]*\))?)')
CHECKED = re.compile(r'\*\*Checked by:\*\*\s*(.*)', re.DOTALL)

# The landing page is the document's own head -- its title and opening prose.
# Nothing here is hand-written: a hand-written landing page is a second place
# for the specification to say something, which is the drift this repo exists
# to stop.
# CHK-02 is retired: its text records that it was withdrawn, so it carries no
# tier and names no checker. Every other rule must carry both, and this list is
# checked in each direction -- a new rule missing metadata fails, and a rule
# named here that has since grown metadata fails too, so the exception cannot
# quietly outlive its reason. Reporting was not enough: the permanent
# "no tier or no Checked by: CHK-02" line is exactly the noise a real regression
# would hide behind.
THIN_METADATA_ALLOWED = {"CHK-02"}

INTRO_FRONT_MATTER = [
    ("id", "intro"),
    ("title", "Ansible Style Specification"),
    ("sidebar_label", "Overview"),
    ("sidebar_position", 0),
    ("slug", "/"),
]


def outside_fences(text):
    """Yield (line, is_structure) for each line; fenced content is never structure.

    Markdown fences matter because the specification quotes YAML and Markdown,
    and a quoted `## ` or `**X-01**` is prose, not a heading or a rule. Without
    this the splitter cut a code block in half, published the fragment as a
    section, and moved the rule's `Checked by:` line onto it -- and the round
    trip still matched, because the recorded order glued the pieces back.
    """
    marker = None
    for line in text.split("\n"):
        match = FENCE.match(line)
        if marker is None:
            # CommonMark forbids a backtick anywhere in a backtick fence's info
            # string, so ```bad`info opens nothing. Treating it as a fence
            # swallowed the rest of the document: a real heading and a real rule
            # became fenced prose, no page was written, and the round trip still
            # matched because nothing was lost -- only hidden.
            if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                marker = match.group(1)
                yield line, False
            else:
                yield line, True
        else:
            yield line, False
            if match and match.group(1)[0] == marker[0] \
                    and len(match.group(1)) >= len(marker) and not match.group(2).strip():
                marker = None


def split(text):
    """Return (head_lines, [(section_title, preamble_lines, [(rule_id, body)])])."""
    head, out = [], []
    title, preamble, rules, rule_id, body = None, [], [], None, []
    for line, structure in outside_fences(text):
        if structure and line.startswith("## "):
            if title is not None:
                if rule_id:
                    rules.append((rule_id, body))
                out.append((title, preamble, rules))
            title, preamble, rules, rule_id, body = line[3:].strip(), [], [], None, []
            continue
        if title is None:
            head.append(line)
            continue
        match = RULE.match(line) if structure else None
        if match:
            if rule_id:
                rules.append((rule_id, body))
            rule_id, body = match.group(1), [line]
        elif rule_id:
            body.append(line)
        else:
            preamble.append(line)
    if title is not None:
        if rule_id:
            rules.append((rule_id, body))
        out.append((title, preamble, rules))
    return head, out


def rule_metadata(body):
    """Return (tier, checked_by) read only from the rule's own prose.

    A `**Checked by:**` quoted inside a fenced example is an example, not this
    rule's metadata; reading the whole body put one into a page's front matter.
    """
    tier = TIER.match(RULE.match(body[0]).group(2))
    prose = "\n".join(line for line, structure in outside_fences("\n".join(body)) if structure)
    checked = CHECKED.search(prose)
    return (tier.group(1).strip() if tier else "",
            " ".join(checked.group(1).split())[:180] if checked else None)


def rule_front_matter(rule_id, body, position):
    """Front matter for one rule page, including the fields the checker reads."""
    tier, checked = rule_metadata(body)
    pairs = [
        ("id", rule_id),
        ("title", rule_id),
        ("sidebar_label", rule_id),
        ("sidebar_position", position),
        ("tier", tier),
    ]
    if checked:
        pairs.append(("checked_by", checked))
    return pairs


def owns(outdir):
    """True only if every entry in `outdir` is one a previous split wrote.

    The presence of a file named `_order.txt` is not ownership: a directory
    holding an unrelated `_order.txt` beside real work was deleted on that
    evidence alone. This reads the manifest and requires the directory to hold
    nothing the manifest does not account for.
    """
    if not (outdir / "_order.txt").is_file():
        return False
    try:
        entries = read_order(outdir)
    except SystemExit:
        return False
    expected = {"_order.txt", "intro.md"}
    expected |= {f"{slug}.md" for kind, slug in entries if kind == "page"}
    if any(kind == "rules" for kind, _ in entries):
        expected.add("rules")
    return {child.name for child in outdir.iterdir()} <= expected


def clear_output_directory(outdir, source_path):
    """Delete a previous split output, and refuse anything else.

    Every refusal here stands for a way this destroyed data: an arbitrary
    directory, the directory holding the specification, a directory whose only
    claim was a stray `_order.txt`, and `.` -- which rmtree emptied and then
    failed on with `Invalid argument`.
    """
    if not outdir.exists():
        return
    if outdir.is_symlink():
        sys.exit(f"REFUSED: {outdir} is a symbolic link. Name the directory itself.")
    if not outdir.is_dir():
        sys.exit(f"REFUSED: {outdir} is not a directory")

    resolved = outdir.resolve()
    if resolved == resolved.parent:
        sys.exit(f"REFUSED: {outdir} is the filesystem root")
    if resolved == pathlib.Path.cwd() or pathlib.Path.cwd().is_relative_to(resolved):
        sys.exit(f"REFUSED: {outdir} resolves to {resolved}, which contains the working "
                 f"directory")
    if source_path.is_relative_to(resolved):
        sys.exit(f"REFUSED: {source_path} is inside {outdir}, which this would delete")
    if any(outdir.iterdir()) and not owns(outdir):
        sys.exit(f"REFUSED: {outdir} holds files no previous split wrote, so this will not\n"
                 f"         delete it. Remove it yourself if that is what you want.")
    shutil.rmtree(outdir)


def main(source_path, outdir):
    source_path = pathlib.Path(source_path).resolve()
    source = read_document(source_path)
    outdir = pathlib.Path(outdir)

    # Line endings are structure here, not whitespace. Every slice is stored and
    # compared by byte, so a CR would have to survive into the pages and back;
    # refusing up front says why, where the round-trip diff can only print two
    # lines that look identical because the difference is invisible.
    if "\r" in source:
        first = next(number for number, line in enumerate(source.split("\n"), 1) if "\r" in line)
        sys.exit(f"REFUSED: {source_path} contains a carriage return, first at line {first}.\n"
                 f"         The specification is LF-only. Convert it before splitting.")

    head, sections = split(source)

    clear_output_directory(outdir, source_path)
    outdir.mkdir(parents=True)

    written = [write_page(outdir / "intro.md", INTRO_FRONT_MATTER, head)]
    order, rule_count, rules_position = [], 0, None

    for position, (title, preamble, rules) in enumerate(sections, 1):
        slug = section_slug(title)
        if not rules:
            order.append(f"page:{slug}")
            written.append(write_page(
                outdir / f"{slug}.md",
                [("id", slug), ("title", title), ("sidebar_position", position)],
                preamble))
            continue

        order.append(f"rules:{slug}")
        # Every rule section nests one level deeper than the narrative pages, so
        # the sidebar places the whole group where the first of them sits in the
        # document; inside the group each section carries its own position.
        if rules_position is None:
            rules_position = position
        folder = outdir / "rules" / slug
        written.append(write_page(
            folder / "index.md",
            [("title", title), ("sidebar_label", "Overview"), ("sidebar_position", 0)],
            preamble))
        write_document(folder / "_category_.json",
                       json.dumps({"label": title, "position": position}, indent=2) + "\n")
        write_document(folder / "_rules.txt",
                       "".join(f"{rule_id}\n" for rule_id, _ in rules))
        for rule_position, (rule_id, body) in enumerate(rules, 1):
            written.append(write_page(folder / f"{rule_id.lower()}.md",
                                      rule_front_matter(rule_id, body, rule_position),
                                      body))
            rule_count += 1

    if rules_position is not None:
        write_document(outdir / "rules" / "_category_.json",
                       json.dumps({"label": "Rules", "position": rules_position}, indent=2) + "\n")

    write_document(outdir / "_order.txt", "".join(line + "\n" for line in order))

    # Every line that looks like a rule must have become a rule page. The round
    # trip cannot see this: text that failed to parse as a rule is published as
    # section prose and rejoins byte-for-byte from there.
    published = {rule_id for _, _, rules in sections for rule_id, _ in rules}
    unparsed = [line for line, structure in outside_fences(source)
                if structure and LOOKS_LIKE_RULE.match(line)
                and LOOKS_LIKE_RULE.match(line).group(1) not in published]
    if unparsed:
        sys.exit("REFUSED: these lines look like rules but produced no rule page:\n"
                 + "\n".join(f"  {line[:96]}" for line in unparsed))

    thin = {rule_id for _, _, rules in sections for rule_id, body in rules
            if any(value in ("", None) for value in rule_metadata(body))}
    if thin - THIN_METADATA_ALLOWED:
        sys.exit("REFUSED: these rules carry no tier or no `Checked by:`:\n"
                 + "\n".join(f"  {rule_id}" for rule_id in sorted(thin - THIN_METADATA_ALLOWED)))
    outgrown = (THIN_METADATA_ALLOWED & published) - thin
    if outgrown:
        sys.exit("REFUSED: these rules are listed as carrying no metadata but now carry it;\n"
                 "         remove them from THIN_METADATA_ALLOWED:\n"
                 + "\n".join(f"  {rule_id}" for rule_id in sorted(outgrown)))

    rebuilt = join(outdir)
    if rebuilt != source:
        a, b = source.split("\n"), rebuilt.split("\n")
        first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y),
                     min(len(a), len(b)))
        sys.exit(f"REFUSED: round-trip differs at line {first + 1}\n"
                 f"  source:  {(a[first][:90] if first < len(a) else '<end of file>')!r}\n"
                 f"  rebuilt: {(b[first][:90] if first < len(b) else '<end of file>')!r}\n"
                 f"  ({len(a)} vs {len(b)} lines)")

    print(f"  {rule_count} rules across {len(order)} sections -> {len(written)} pages "
          f"({rule_count} rule, {len(written) - rule_count - 1} section, 1 intro)")
    if thin:
        print(f"  no tier or no `Checked by:` (recorded exceptions): {', '.join(sorted(thin))}")
    print("  round-trip: join_spec.py reads the written pages back to a document")
    print(f"              byte-identical to the source ({len(source.splitlines())} lines)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: split_spec.py SPEC.md OUTDIR")
    main(sys.argv[1], sys.argv[2])
