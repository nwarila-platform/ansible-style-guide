---
id: "COM-01"
title: "COM-01"
sidebar_label: "COM-01"
sidebar_position: 3
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/com_01.py` for markers, non-directive trailing comments, block adjacency, block length (3), header description length (10), the grammar of any date or c"
---

**COM-01** `auto*`/`review` — A comment states a constraint, a failure mode, or a rejected
alternative — never what the next line does, never history, never review provenance. History and
review provenance live in commits and PRs only. **A comment block is at most 3 lines** (ruling
26): A comment block is one to three consecutive physical lines whose first non-whitespace
character is `#`, immediately preceding, with no intervening line, a task's first key or a
default/variable mapping key at the same indentation. The FMT-01 file-header box is not a comment
block. Each task has at most one comment block. **A whole-line comment run that is neither a
comment block nor the file-header description is a finding, whatever its length** (ruling 30):
comments live above a task, above a default or variable, or in the file header. Banner lines (the
FMT-01 box, Description and separator rules and the FMT-02 region markers) and whole-line lint
directives are not comment runs. **Ruling 27:** A file-header description comprises the nonblank
whole-line comments after the FMT-01 Description rule and before that box's closing banner rule;
the path line, rule lines, and blank `#` padding do not count, and at most 10 lines count.
**Cite, don't narrate** (ruling 28): knowledge that needs more than three lines lives in the
documentation, and the comment cites it with a bracketed tag closing its last line — `[INV-nn]`
for an entry in the role README's Design invariants, `[APF-nn]` for an entry in
`docs/reference/platform-facts.md`, `[ADR-nnnn]` for a decision record under
`docs/decision-records/`. A tag resolves only if its exact label occurs once in the current
role's README or once in tracked `docs/reference/platform-facts.md`, or if exactly one tracked
`docs/decision-records/repo/nnnn-*.md` has an H1 beginning `# ADR-nnnn:`. A claim about
**platform behaviour** — vendor, OS, module or transport — is either one line naming how it was
measured — a date written `YYYY-MM-DD` or a commit of 7 to 40 lowercase hexadecimal characters —
or a tag whose entry carries the measurement. Whether a comment is a platform claim is a `review`
judgment (ruling 29); the checker validates the grammar of any date or commit token present and
the form and resolution of any tag present. Trailing comments and block-marker comments (`# Begin
The '<Stage>' Block`, any case) are findings. The only permitted trailing comments are the lint
directives the pinned linters recognize: `# noqa: <rule-id>` (ansible-lint), and `# yamllint
disable-line rule:<id>`, `# yamllint disable rule:<id>` and `# yamllint enable` (yamllint). **A
change that removes a fact from a comment moves it to its documented home in the same commit.**
**Why:** rulings 6 and 26-28. Measured 2026-09-21 on origin/main: comments are about 40% of YAML
lines in the framework, windows-wsus and pdq; 1,596 of 4,205 prose blocks exceed 3 lines, 346
exceed 6, the longest is 37, and 62% of comment prose sits in blocks over 3 lines;
windows-fileserver-ha is the in-fleet model (22%, median 2, maximum 5). Both reviewer lenses
praised the long blocks, so length is a finding rather than a review judgment. **306 block
markers fleet-wide**, 261 case-sensitive — two reconciliations reporting 9 and 13 for one tree is
itself the failure mode, so matching is case-insensitive [§3.10].
**Checked by:** a new `rolecheck/lint/rules/com_01.py` for markers, non-directive trailing
comments, block adjacency, block length (3), header description length (10), the grammar of any
date or commit token present, tag form, and tag resolution (an `INV-nn` anchor in the role
README, a `APF-nn` anchor in `docs/reference/platform-facts.md`, an ADR file numbered `nnnn`); an
`INV`/`APF` entry no code cites is a `warn`. Unanchored comment runs are findings from the same
rule file. Platform-claim detection, content class and fact preservation are `review`.

