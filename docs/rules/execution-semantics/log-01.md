---
id: "LOG-01"
title: "LOG-01"
sidebar_label: "LOG-01"
sidebar_position: 5
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/log_01.py` for the AST clauses; placement, secrecy and change-set publication are `review`."
---

**LOG-01** `auto*`/`review` — `no_log: true` is hoisted to the block holding the secret, not repeated
per task, and appears nowhere else. A `rescue:` may project only named fields of a `no_log` result
(`msg`, `rc`) — never `stdout`, `stderr` or the whole object. **For a register created inside a
`no_log` block, LOG-01 is narrower than RESCUE-01: only `.msg` and `.rc` may be projected.** A
play-level secret lookup is gated on the states that need it. An assert never interpolates `stdout` or
`stderr`. A destructive task whose `no_log` is forced by a credential is followed by a task with no
secret input that publishes the change set by name.
**[Ruling 40, 2026-09-23]** A secret review starts from the **complete accepted-input set, including
every alias the module documents**, and follows each secret through task arguments, registered results,
and any persistence or projection of a whole result object. A coverage claim names the surfaces actually
inspected. An unclassified input or alias, or persistence of an unclassified whole result, is a finding.
A `no_log: true` declared in `meta/argument_specs.yml` is **documentation only** — measured on
ansible-core 2.21.4, it does not mask the value in any later task — so it never satisfies this rule.
**Why (ruling 40):** from R06 of the deleted guides. LOG-01 said what to do once a secret's location is
known; nothing said how far you must have looked before claiming none leaks. Executed: a module accepting
canonical `payload` plus the documented alias `api_token`, invoked by the alias, printed the secret
verbatim through the callback. ansible-lint's only secret rule (`no-log-password`) is opt-in and
experimental, so "ansible-lint is clean" is precisely the false green this clause forbids. Review surface
measured at **581** non-loader register sites across 69 role folders — a denominator to classify, not a
leak count.
**Why:** ruling 18; each clause is a measured leak path (fsha rescue, wsus clean-state lookup,
`python3_pip` `success_msg`).
**Checked by:** a new `rolecheck/lint/rules/log_01.py` for the AST clauses; placement, secrecy and
change-set publication are `review`.

