---
id: "ERR-01"
title: "ERR-01"
sidebar_label: "ERR-01"
sidebar_position: 3
tier: "`auto*`/`review`"
checked_by: "`ansible-lint ignore-errors` for the bare form (163edb4); adjacency and the `# rc-contract:` marker are a new `rolecheck/lint/rules/err_01.py`; the read-only-versus-mutating classi"
---

**ERR-01** `auto*`/`review` — No `ignore_errors` and no `failed_when: false` on a mutating task, with
two carve-outs. `ignore_errors: true` is permitted only where the task registers its result **and the
immediately following task is an `ansible.builtin.assert` or `ansible.builtin.fail` whose `that:` or
`when:` reads that register** — the named refusal. `failed_when: false` is permitted on a read-only
probe whose tool documents nonzero rc as a state signal, with that rc contract stated in a whole-line
`# rc-contract: <source>` comment, and on best-effort cleanup inside a `rescue:` preceding a
deliberate `fail`. `failed_when` is otherwise a postcondition folded into the task producing the data.
**Why:** ruling 8; `bootstrap.yml:148-157` suppresses a failed registry mutation *and* always reports
changed.
**Checked by:** `ansible-lint ignore-errors` for the bare form (163edb4); adjacency and the
`# rc-contract:` marker are a new `rolecheck/lint/rules/err_01.py`; the read-only-versus-mutating
classification and the truth of both carve-outs are `review`.

