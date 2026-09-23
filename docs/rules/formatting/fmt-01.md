---
id: "FMT-01"
title: "FMT-01"
sidebar_label: "FMT-01"
sidebar_position: 1
tier: "`autofix`"
checked_by: "the formatter; CI asserts a clean diff. `rolecheck/lint/rules/fmt_01.py` stops emitting findings that day."
---

**FMT-01** `autofix` — Every banner rule line in a role folder in scope is exactly **97 columns**,
including the file-header box, the `# --- [ Description ] --- #` rule, region markers and sibling
separators. `#region` carries six dashes before the label and `#endregion` three, so the `[` aligns
between an open/close pair; the labels are byte-identical. Out of scope: PowerShell regions
(self-consistent 96) and the framework's `.editorconfig`/`.yamllint.yml` (legacy 79).
**Why:** 1,518 composed findings, zero attributable defects.
**Checked by:** the formatter; CI asserts a clean diff. `rolecheck/lint/rules/fmt_01.py` stops
emitting findings that day.

