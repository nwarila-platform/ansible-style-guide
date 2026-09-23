---
id: "SCAFFOLD-01"
title: "SCAFFOLD-01"
sidebar_label: "SCAFFOLD-01"
sidebar_position: 5
tier: "`auto`"
checked_by: "`rolecheck/structure.py` `SCAFFOLD-01` (directories 163edb4; predicate new)."
---

**SCAFFOLD-01** `auto` — A role folder contains all twelve scaffold directories: `defaults`, `files`,
`handlers`, `library`, `lookup_plugins`, `meta`, `module_utils`, `molecule`, `tasks`, `templates`,
`tests`, `vars`. **Each scaffold directory either contains exactly `.gitkeep`, or contains at least
one non-placeholder entry and no `.gitkeep`.** A zero-byte `main.yml`, `test.yml` or `converge.yml` is
not a non-placeholder entry; it is a finding, because a placeholder must never read as coverage.
**Why:** ruling 2; 85 banned-but-present framework directories against 256 consumer findings demanding
them, and **12 of 14 framework `tests/test.yml` are zero bytes** [§3.1, §5.3].
**Checked by:** `rolecheck/structure.py` `SCAFFOLD-01` (directories 163edb4; predicate new).

