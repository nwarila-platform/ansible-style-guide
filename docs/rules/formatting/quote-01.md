---
id: "QUOTE-01"
title: "QUOTE-01"
sidebar_label: "QUOTE-01"
sidebar_position: 4
tier: "`auto*`"
checked_by: "a new `rolecheck/lint/rules/quote_01.py`."
---

**QUOTE-01** `auto*` — Literal strings take single quotes; values containing Jinja take double quotes;
booleans, integers, `null` and conditionals are bare. A value containing both a backslash path and
Jinja stays single-quoted, because double quotes would make `\S` and `\A` illegal escapes. Task
`name:` and `register:` are always single-quoted.
**Why:** no defect produced; kept as written.
**Checked by:** a new `rolecheck/lint/rules/quote_01.py`.

