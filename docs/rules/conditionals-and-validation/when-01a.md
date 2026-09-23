---
id: "WHEN-01a"
title: "WHEN-01a"
sidebar_label: "WHEN-01a"
sidebar_position: 1
tier: "`auto*`"
checked_by: "a new `rolecheck/lint/rules/when_01.py`."
---

**WHEN-01a** `auto*` — A conditional comparing a loader-level scalar input to a literal uses the full
chain: `(state | default('present') | string | lower | trim) == 'present'`.
**Why:** conforms everywhere; kept as written. **Checked by:** a new
`rolecheck/lint/rules/when_01.py`.

