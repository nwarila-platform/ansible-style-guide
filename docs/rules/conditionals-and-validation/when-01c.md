---
id: "WHEN-01c"
title: "WHEN-01c"
sidebar_label: "WHEN-01c"
sidebar_position: 3
tier: "`auto*`"
checked_by: "`rolecheck/lint/rules/when_01.py` (new)."
---

**WHEN-01c** `auto*` — A conditional comparing merged-config strings normalizes **both** sides with
the same filter chain — the same ordered filters with the same arguments. A one-sided comparison
against an undefaulted value fails silently rather than loudly.
**Why:** 3 live violations in windows-wsus. **Checked by:** `rolecheck/lint/rules/when_01.py` (new).

