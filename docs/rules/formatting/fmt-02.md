---
id: "FMT-02"
title: "FMT-02"
sidebar_label: "FMT-02"
sidebar_position: 26
tier: "`autofix`"
checked_by: "the formatter; CI asserts a clean diff. `rolecheck/lint/rules/fmt_02.py` stops emitting findings that day."
---

**FMT-02** `autofix` — A region label is `<Stage>: <Description>` where every word of the description
is capitalized, matching NAME-01. Stage is `Begin`, `Process`, `End` or `Always` in task files and
`Play` or `Roles` in playbooks. `Always` is a region-only token: tasks inside an `always:` keep their
enclosing stage's task token. Regions are required wherever a file delimits more than one unit, and
omitted where there is nothing to delimit.
**Why:** ruling 3; 236 findings of one shape, no defect. With no length split the region index must be
generated, not policed.
**Checked by:** the formatter; CI asserts a clean diff. `rolecheck/lint/rules/fmt_02.py` stops
emitting findings that day.

