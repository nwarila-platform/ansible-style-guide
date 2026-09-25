---
id: "VARNAME-01"
title: "VARNAME-01"
sidebar_label: "VARNAME-01"
sidebar_position: 11
tier: "`auto*`"
checked_by: "`ansible-lint var-naming` (163edb4); the scoped/persisting split is a new `rolecheck/lint/rules/varname_01.py`."
---

**VARNAME-01** `auto*` — A value that persists as a host fact is named `__<role>_<noun>__`; a task- or
block-scoped `vars:` member is bare `__<noun>__`. The prefix exists because a persisting fact can
collide across roles in one play and a scoped var cannot.
**Why:** 22 role-prefixed block vars in fsha — the rule discriminates.
**Checked by:** `ansible-lint var-naming` (163edb4); the scoped/persisting split is a new
`rolecheck/lint/rules/varname_01.py`.

