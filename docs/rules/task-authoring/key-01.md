---
id: "KEY-01"
title: "KEY-01"
sidebar_label: "KEY-01"
sidebar_position: 2
tier: "`auto`/`auto*`"
checked_by: "`ansible-lint key-order` for name-first and `block`/`rescue`/`always`-last only; module-last, the blank line, wrapper order and argument sorting are a new `rolecheck/lint/rules/key"
---

**KEY-01** `auto`/`auto*` — A plain task puts `name:` first and the fully-qualified module last, with
a blank line before the module; the order of keywords between them is free. In a **block wrapper**,
among the keys present the relative order is `name`, `vars`, `when`, `block`, `rescue`, `always`; only
`name` and `block` are mandatory. Module arguments are alphabetical.
**Why:** ruling 10; `block` sorts before `vars`, so **every conforming wrapper was a violation** [§3.6].
**Checked by:** `ansible-lint key-order` for name-first and `block`/`rescue`/`always`-last only;
module-last, the blank line, wrapper order and argument sorting are a new
`rolecheck/lint/rules/key_01.py`.

