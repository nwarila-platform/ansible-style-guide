---
id: "LEN-01"
title: "LEN-01"
sidebar_label: "LEN-01"
sidebar_position: 2
tier: "`warn`"
checked_by: "the formatter (reflow); the residual hard-width result is a warning from `rolecheck/report.py` once `yaml[line-length]` joins the `skip_list` of `rolecheck/lint/ansible-lint.yml` —"
---

**LEN-01** `warn` (`autofix`) — No line in any tracked file in a role folder in scope exceeds **97
columns** — YAML, Jinja, PowerShell and **Markdown alike**. The formatter reflows README prose to this
width. The loader is included. Exceeded width is a warning, never a build failure.
**Why:** rulings 20 and 3; a full sweep gave **239 violations, 235 of them README prose**, where
reports said 2 and 4 [§3.7].
**Checked by:** the formatter (reflow); the residual hard-width result is a warning from
`rolecheck/report.py` once `yaml[line-length]` joins the `skip_list` of
`rolecheck/lint/ansible-lint.yml` — under ansible-lint a yamllint result is fatal whatever its level
in `rolecheck/lint/yamllint.yml` (97/error today).

