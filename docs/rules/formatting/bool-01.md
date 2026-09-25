---
id: "BOOL-01"
title: "BOOL-01"
sidebar_label: "BOOL-01"
sidebar_position: 5
tier: "`auto`"
checked_by: "`yamllint truthy` via `rolecheck/lint/yamllint.yml` (163edb4)."
---

**BOOL-01** `auto` — `true` and `false` only; never `yes`, `no`, `on`, `off`, `True` or `False`.
Enforced at error level with `check-keys: true` (which is what requires `'on':` in workflow files).
**Why:** 0 violations fleet-wide.
**Checked by:** `yamllint truthy` via `rolecheck/lint/yamllint.yml` (163edb4).

