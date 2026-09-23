---
id: "GUARD-02"
title: "GUARD-02"
sidebar_label: "GUARD-02"
sidebar_position: 6
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/guard_02.py` for `quiet`, `fail_msg` presence and the no-Jinja heuristic; refusal and remedy are `review`. ---"
---

**GUARD-02** `auto*`/`review` — Every assert carries `quiet: true` and a `fail_msg` stating the
refusal, the observed value and the remedy. The observed value may be omitted only where the failing
`that:` clause already prints it.
**Why:** ruling 22; only **188 of 367 asserts show an observed value** [§3.11].
**Checked by:** a new `rolecheck/lint/rules/guard_02.py` for `quiet`, `fail_msg` presence and the
no-Jinja heuristic; refusal and remedy are `review`.

---

