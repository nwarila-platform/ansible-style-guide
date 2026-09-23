---
id: "HAND-01"
title: "HAND-01"
sidebar_label: "HAND-01"
sidebar_position: 21
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/hand_01.py` for topic shape and the guard symbol table; `ansible-lint no-handler` for the inverse (163edb4); flush placement is `review`."
---

**HAND-01** `auto*`/`review` — Handlers are addressed by topic, never by name: `listen:` takes a
single-quoted kebab-case topic prefixed with the role name, with a free suffix; `notify:` is a single
quoted scalar naming that topic. A stage that notifies flushes handlers at the end of the stage — so
`END` proofs read post-restart state — **and** in that stage's `always:`, because Ansible does not run
handlers after a play failure. **The stage container is the named block wrapper BLOCK-01 requires, not
the region FMT-02 delimits**: the first flush is the last child of that wrapper's `block:` list, and
the second flush is a child of that wrapper's `always:` list. FMT-02 regions are navigation only; they
never locate a flush. A handler guard reads a register, never a fact.
**Why:** ruling 17; `-required` forced unnatural topics, and register-not-fact keeps guards out of
FACT-01(a).
**Checked by:** a new `rolecheck/lint/rules/hand_01.py` for topic shape and the guard symbol table;
`ansible-lint no-handler` for the inverse (163edb4); flush placement is `review`.

