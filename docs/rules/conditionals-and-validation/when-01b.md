---
id: "WHEN-01b"
title: "WHEN-01b"
sidebar_label: "WHEN-01b"
sidebar_position: 2
tier: "`auto*`"
checked_by: "`rolecheck/lint/rules/when_01.py` (new)."
---

**WHEN-01b** `auto*` — A conditional testing merged config for emptiness supplies a type-appropriate
default: `| default([], true)` for lists, `| default({}, true)` for maps. The checker reads the
declared type from `meta/argument_specs.yml` (SPEC-01).
**Why:** no violation found; kept as written. **Checked by:** `rolecheck/lint/rules/when_01.py` (new).

