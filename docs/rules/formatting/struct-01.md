---
id: "STRUCT-01"
title: "STRUCT-01"
sidebar_label: "STRUCT-01"
sidebar_position: 14
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/struct_01.py` for flatness, dispatch-matrix filenames, `vars/main.yml` and `.gitattributes`; the empty overlay is `review`."
---

**STRUCT-01** `auto*`/`review` — `tasks/` is flat and holds only `main.yml`, `validate.yml` and
`<state>_<family>.yml` — **one file per state and family, never split on length**; no subdirectories.
The allowed `<state>` values are the `choices` the role's `meta/argument_specs.yml` declares for its
state input, and the allowed `<family>` values are the stems of the `vars/<family>.yml` files present;
that pair is the dispatch matrix, and a task file outside it is a finding. Navigation inside a large
file is the region index and the stage tokens. The OS overlay is `vars/<family>.yml`, never
`vars/main.yml`, and exists even when it has nothing to say — as `{}` with a header stating that an
empty map is the honest declaration rather than a copy of defaults that would drift. The role's
directory set is SCAFFOLD-01's; this rule bans no directory. A directory tracking exported product XML
carries `.gitattributes` with `*.xml -text`.
**Why:** rulings 12 and 2. Owner, verbatim: "Single file, no split based on length" — overriding the
proposed pdq and wazuh thresholds and, as the later ruling, governing where ruling 5 met it (NAME-01).
**Checked by:** a new `rolecheck/lint/rules/struct_01.py` for flatness, dispatch-matrix filenames,
`vars/main.yml` and `.gitattributes`; the empty overlay is `review`.

