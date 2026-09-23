---
id: "SCALAR-01"
title: "SCALAR-01"
sidebar_label: "SCALAR-01"
sidebar_position: 7
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/scalar_01.py` for the spelling; newline-sensitivity is `review`."
---

**SCALAR-01** `auto*`/`review` — Folded-strip `>-` is the default for prose, `fail_msg` values and
long expressions. Literal `|` is permitted for **any newline-sensitive payload** — file content,
heredocs, a `win_shell`/`win_command` escape hatch — where newline preservation is semantically
required.
**Why:** ruling 16; the old wording failed 9 legitimate wazuh sites. V1's tail "anything larger is a
first-class script under PS-01" is deleted — undefined for a Linux heredoc, it would readmit the rule
ruling 16 deferred.
**Checked by:** a new `rolecheck/lint/rules/scalar_01.py` for the spelling; newline-sensitivity is
`review`.

