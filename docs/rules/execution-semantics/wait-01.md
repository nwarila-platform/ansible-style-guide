---
id: "WAIT-01"
title: "WAIT-01"
sidebar_label: "WAIT-01"
sidebar_position: 4
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/wait_01.py` over the generated timeout metadata; the cited race is `review`."
---

**WAIT-01** `auto*`/`review` — Bound every wait the module allows. A retry loop carries `retries`,
`delay` and `until` together and a whole-line `# measured: <YYYY-MM-DD|commit>` comment citing the
race or flake that justifies it. Where a module exposes no timeout (`win_service` start/restart), the
role's contract states that it depends on the caller's job budget.
**Retired:** "an END proof reads once" — the `win_reboot`-returns-at-logon race is measured and real,
so a bounded retry with a cited race is permitted.
**Why:** 0 of 3 fsha retry loops carry the required comment.
**Checked by:** a new `rolecheck/lint/rules/wait_01.py` over the generated timeout metadata; the cited
race is `review`.

