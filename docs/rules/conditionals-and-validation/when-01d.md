---
id: "WHEN-01d"
title: "WHEN-01d"
sidebar_label: "WHEN-01d"
sidebar_position: 4
tier: "`auto*`"
checked_by: "`rolecheck/lint/rules/when_01.py` (new) — parse each block `when:`, collect referenced roots, walk descendants, reject any intersection with task `vars:` keys."
---

**WHEN-01d** `auto*` — A task must not bind, through its own `vars:`, any name referenced by a `when:`
it inherits from an enclosing **block**. Where later data must be re-tested, use a distinct name.
Identifier extraction is by Jinja parse, not by regex.
**Why:** ruling 39 (2026-09-23), from R04 of the deleted guides. A block's condition is re-evaluated in
each child task's own variable context, and task `vars:` outrank block `vars:`, so a child that rebinds
a name the gate reads silently skips itself inside a block that was entered. Executed: the constructed
case gave `ok=2 changed=0 failed=1 skipped=1`, exit 2, while `ansible-lint -p` passed the same file with
0 failures. Measured **24 of 24** gated blocks conform, so the cost is zero; the value is foreclosing a
silent-skip class whose only symptoms are a green run that did nothing. Scope is **blocks only**: a
`when:` on `include_tasks` gates the include statement and is not re-evaluated per child, so extending
this to dynamic includes would ban safe rebinding. `import_tasks`, whose condition *is* copied to each
child, carries the same hazard and is a named follow-up — its population has not been measured, and this
fleet does not write rules over unmeasured surfaces.
**Checked by:** `rolecheck/lint/rules/when_01.py` (new) — parse each block `when:`, collect referenced
roots, walk descendants, reject any intersection with task `vars:` keys.

