---
id: "LOOP-01"
title: "LOOP-01"
sidebar_label: "LOOP-01"
sidebar_position: 9
tier: "`auto*`"
checked_by: "`rolecheck/lint/rules/loop_01.py` (163edb4); the two triggers are new — today's rule produces the false positive that caused #111."
---

**LOOP-01** `auto*` — Iterate with `loop:`; `with_*` never appears. Every loop carries a
`loop_control.label`. `loop_control` is folded per FLOW-01. **A named dunder `loop_var` is required on
exactly two triggers: the loop expression references a registered result's `.results`, or the task
lies inside another loop's body.** The dunder variable is declared on the *inner* loop — the one whose
body would otherwise read `item.item`. A single-level loop over a plain list keeps `item`.
**Why:** ruling 11, the counterfactual replaced by two objective triggers. `345c3cf` (#111) removed
`loop_var: r` and gave `item.item.unique_id` **15 times in one file**.
**Checked by:** `rolecheck/lint/rules/loop_01.py` (163edb4); the two triggers are new — today's rule
produces the false positive that caused #111.

