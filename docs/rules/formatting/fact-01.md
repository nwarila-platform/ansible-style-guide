---
id: "FACT-01"
title: "FACT-01"
sidebar_label: "FACT-01"
sidebar_position: 12
tier: "`auto`/`review`"
checked_by: "`rolecheck/lint/rules/fact_01.py` (presence 163edb4; the two annotation tokens new); the exemption's truth is `review`."
---

**FACT-01** `auto`/`review` — `set_fact` does not appear in an **application role's task files**, with
two named exemptions: **(a)** a handler-visible progress latch that no `register` expresses, and
**(b)** a value that must persist across plays. Each exempt site carries one of exactly two whole-line
annotations immediately above it: `# FACT-01 exemption (a): handler-visible progress latch` or
`# FACT-01 exemption (b): persists across plays`. Derived values otherwise live in block `vars:` —
lazily evaluated, block-scoped — or come from `register`; a fold is written with `zip` in block
`vars:`. The loader's use is out of scope by LOADER-01, not by exception. Never `set_fact` the name
`ansible_facts`.
**Why:** ruling 7, Red Hat 7.5; the `zip` counter-example ran on 2.21.4 and the register hatch is
proven (#104). Scope stays at application-role task files — the ruling's own scope — so
`fact_01.py:35` scoping to `applications/` is the rule, not a gap.
**Checked by:** `rolecheck/lint/rules/fact_01.py` (presence 163edb4; the two annotation tokens new);
the exemption's truth is `review`.

