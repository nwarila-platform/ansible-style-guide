---
id: "ARG-01"
title: "ARG-01"
sidebar_label: "ARG-01"
sidebar_position: 3
tier: "`review` → `auto*`"
checked_by: "`review` until the generated metadata and the override table exist; then a new `rolecheck/lint/rules/arg_01.py`."
---

**ARG-01** `review` → `auto*` — State every module option whose documented default is non-null,
including when the value equals that default; the executed value must be readable in the task, not
inherited from collection docs a version bump can change. Omit every option whose documented default
is null unless it carries this task's intent. Never write `option: null` or `omit` to satisfy this
rule. An option may be omitted as inapplicable to the invoked mode only where the module and option
appear in the **generated applicability metadata** or in the owner-ratified override table. An option
is stated only in the task's module arguments or its `args:` keyword; `module_defaults` does not state
it. Options whose name begins `_` are outside this rule. In a mutually exclusive group with at least
one non-null default, stating any one member satisfies the group. An `ansible.builtin` option added
after the declared `min_ansible_version` is not required; a role declaring no floor gets no relief,
and collection options are always required.
**Why:** ruling 13; unmeasurable until the generated data exists [§7]. Blind spot, recorded not fixed:
a wrong `prefix: 'google-chrome-'` cloned into 34 roles reads as intent.
**Checked by:** `review` until the generated metadata and the override table exist; then a new
`rolecheck/lint/rules/arg_01.py`.

