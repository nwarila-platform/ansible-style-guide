---
id: "FLOW-01"
title: "FLOW-01"
sidebar_label: "FLOW-01"
sidebar_position: 8
tier: "`auto`"
checked_by: "`yamllint braces`/`brackets` for spacing (163edb4); sequence items and control mappings are a new `rolecheck/lint/rules/flow_01.py`."
---

**FLOW-01** `auto` — Short scalar lists are written inline with exactly one space inside each bracket,
**"short" meaning the complete line is at most 97 columns**. A **sequence item** is always a block
mapping; `- { a: 1, b: 2 }` is a finding regardless of length. A **control mapping** — the set is
closed to `loop_control:`; additions require ratification — is folded onto one line as
`{ key: value }` when the folded form fits LEN-01, and written block style only when it does not.
**Why:** 44 violations in the unaligned repo; "short" and "its kin" are now exact.
**Checked by:** `yamllint braces`/`brackets` for spacing (163edb4); sequence items and control
mappings are a new `rolecheck/lint/rules/flow_01.py`.

