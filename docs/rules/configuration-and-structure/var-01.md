---
id: "VAR-01"
title: "VAR-01"
sidebar_label: "VAR-01"
sidebar_position: 8
tier: "`auto*`"
checked_by: "a new `rolecheck/lint/rules/var_01.py`. ---"
---

**VAR-01** `auto*` — Read merged configuration as `<role>_running`, in every file including handlers.
The include-scoped `config` alias is not used in application roles; `config.` must not appear.
**[Ruling 41, 2026-09-23]** The same interface from the caller's side: a role whose `defaults/main.yml`
defines `<role>_defaults` receives every per-target input through the bare `<role>:` mapping; only loader
scalars (`ENV`, `state`) are passed as parallel role parameters, and a role with no `<role>_defaults` is
outside this clause. Because `-e '{"<role>": {…}}'` **replaces** that mapping rather than merging with
it, an extra-var override restates every key the caller's mapping sets. The generated Inputs section
names these values as merged configuration reaching the role as `<role>_running`, and carries that
warning.
**Why (ruling 41):** from R13 of the deleted guides. Extra vars have highest precedence and mappings
replace rather than recursively merge: executed, `-e '{"loader_demo":{"required_value":"…"}}'` silently
deleted the caller's sibling `temp_dir`. A per-target key placed *beside* rather than inside the role
mapping bypasses the loader entirely. Measured: **88 of 88** caller sites already nest correctly, so the
structural half is a formalization; the real gap is documentation, at **5 of 50** role surfaces. The
deleted guides instructed consuming the merged result through `config`, which this rule bans — one of
the contradictions that made the guides unsafe to keep.
**Why:** 163 `config.` reads in the unaligned repo, 0 elsewhere.
**Checked by:** a new `rolecheck/lint/rules/var_01.py`.

---

