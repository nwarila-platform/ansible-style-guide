---
id: "FLOOR-01"
title: "FLOOR-01"
sidebar_label: "FLOOR-01"
sidebar_position: 2
tier: "`warn`"
checked_by: "`rolecheck/structure.py` `FLOOR-01` (163edb4; gates after the packaged-spec reader)."
---

**FLOOR-01** `warn` — A role declares `min_ansible_version: '2.21'` in `meta/main.yml`, as the quoted
string, in every role in every repo. A missing or different value is a warning. The checker parses
this literal from the packaged `rolecheck/spec/ANSIBLE-STYLE-SPEC.md`, shipped inside the
`ansible-role-check` distribution and the ubi9 tool image, never from a constant of its own.
**Why:** ruling 23; `structure.py:17` pins 2.18, so **all 69 warnings name the wrong target** [§3.3].
**Checked by:** `rolecheck/structure.py` `FLOOR-01` (163edb4; gates after the packaged-spec reader).

