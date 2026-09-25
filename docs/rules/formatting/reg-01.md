---
id: "REG-01"
title: "REG-01"
sidebar_label: "REG-01"
sidebar_position: 10
tier: "`auto*`/`review`"
checked_by: "`rolecheck/lint/rules/reg_01.py` for the name shape (163edb4); the reads, marker and default are new; the contract's truth is `review`."
---

**REG-01** `auto*`/`review` — A `register:` target is `'__<role>_<noun>__'`, single-quoted. Never read
`.changed` from a result — change is expressed through `notify:` and the run's recap. Never read `.rc`
except inside an ERR-01 probe carrying the `# rc-contract: <source>` marker. A registered field read
in a `when:` carries a default; the same field in a `fail_msg` does not, because a `fail_msg` only
renders in an already-failed context.
**Why:** 59 unnamespaced registers in one play's namespace.
**Checked by:** `rolecheck/lint/rules/reg_01.py` for the name shape (163edb4); the reads, marker and
default are new; the contract's truth is `review`.

