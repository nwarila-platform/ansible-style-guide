---
id: "META-01"
title: "META-01"
sidebar_label: "META-01"
sidebar_position: 24
tier: "`auto*`/`review`"
checked_by: "a `META-01` top-level key allowlist in `rolecheck/structure.py`, the complete mechanical test; smuggled prose is `review` — no complete detector is claimed."
---

**META-01** `auto*`/`review` — `meta/main.yml` carries `galaxy_info`, `dependencies` and
`allow_duplicates` only; **any other top-level key is a finding**. It does not document inputs;
`meta/argument_specs.yml` is the input contract (SPEC-01) and the README's inputs table is generated
from it (DOC-02).
**Why:** ruling 19; clause (a) was wrong (10 of 11 violations are correct `allow_duplicates`), clause
(b) has **49 live violations** [§3.12].
**Checked by:** a `META-01` top-level key allowlist in `rolecheck/structure.py`, the complete
mechanical test; smuggled prose is `review` — no complete detector is claimed.

