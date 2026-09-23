---
id: "NAME-01"
title: "NAME-01"
sidebar_label: "NAME-01"
sidebar_position: 1
tier: "`auto*`/`review`"
checked_by: "`rolecheck/lint/rules/name_01.py` (163edb4; handlers, which `name_01.py:64` skips, are new); staging is `review`."
---

**NAME-01** `auto*`/`review` — Task names are `'STAGE | Title Case Imperative'`, single-quoted, one
space either side of the pipe. STAGE is closed to four tokens, with no subsystem qualifier: **BEGIN**
reads the machine and decides one action (reads only, no mutation); **PROCESS** performs the mutation;
**END** verifies against the product's own readback, not the value just written, **and does not
duplicate a module's own contract by re-checking what a PROCESS task in the same role just configured
[ruling 34, 2026-09-23]**; **VALIDATE** is the
contract asserts in `validate.yml`. Playbooks add `PLAY` and `INVENTORY`. A task inside an `always:`
takes the enclosing stage's token. Handlers are exempt: bare sentence case, no token. **Subsystem
navigation uses STRUCT-01's permitted `<state>_<family>.yml` file and its region index; it never
extends the stage token set or splits a state/family on length.**
**Why:** ruling 5, reconciled with the later ruling 12 where the two met: navigation (PKI×31, S3×19)
is the region index, not a length split. Stage semantics appear here because they are not lexically
checkable; `name[prefix]` stays unlisted, so production does not undo ruling 5.
**Checked by:** `rolecheck/lint/rules/name_01.py` (163edb4; handlers, which `name_01.py:64` skips, are
new); staging is `review`.

