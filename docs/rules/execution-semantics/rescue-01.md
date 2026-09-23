---
id: "RESCUE-01"
title: "RESCUE-01"
sidebar_label: "RESCUE-01"
sidebar_position: 6
tier: "`auto*`"
checked_by: "a new `rolecheck/lint/rules/rescue_01.py` (AST walk over `rescue:` bodies). ---"
---

**RESCUE-01** `auto*` — A `rescue:` reads `ansible_failed_result.msg` and `.rc`, and named fields of
its own registers, only. It never projects the whole result object into a `fail_msg`, a `debug`, or a
variable. **Only `ansible_failed_result.msg` requires a default** —
`{{ ansible_failed_result.msg | default('<role> operation failed', true) }}` — being the one field
absent on an unreachable or parse failure; `.rc` and named register fields are projected without one,
since a `fail_msg` renders only in an already-failed context. LOG-01 narrows this rule for any
register created under `no_log`.
**Why:** ruling 21; the dormancy premise was false — **12 `rescue:` blocks in role folders, 14 with
playbooks**.
**Checked by:** a new `rolecheck/lint/rules/rescue_01.py` (AST walk over `rescue:` bodies).

---

