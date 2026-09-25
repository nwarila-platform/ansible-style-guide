---
id: "BLOCK-01"
title: "BLOCK-01"
sidebar_label: "BLOCK-01"
sidebar_position: 23
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/block_01.py` for wrapper key presence and order, for an empty wrapper — a wrapper whose `block:` list, or whose `rescue:` or `always:` list where presen"
---

**BLOCK-01** `auto*`/`review` — Each stage is a block wrapper task: `name:`, optional `vars:`,
`block:`, in KEY-01's ratified relative order (`name`, `vars`, `when`, `block`, `rescue`, `always`
among the keys present). A privilege boundary may be a block with `become`/`no_log` hoisted and
children carrying none. `always:` is for cleanup and the guaranteed handler flush. Note the Ansible
caveat: an invalid task definition or an unreachable host triggers neither `rescue` nor `always`, so
an `always:` cleanup is not a guarantee against every failure.
**Ruling 25 (2026-09-21):** every stage that exists in a state file is a named block wrapper, even when it
holds one task; a stage with no tasks is omitted rather than written empty. A staged task standing outside
a block is a finding.
**[Ruling 39a, 2026-09-23]** An `always:` task that removes a path is gated on the register of the task
that staged it: a run that never reached staging never deletes the path. A cleanup whose path is computed
from configuration rather than from that register is a finding unless so gated. Executed: an unguarded
`always:` deletion of a fixed staging path removed a pre-existing directory the run never created
(`ok=3 changed=2 failed=1 skipped=1`, exit 2), with ansible-lint clean. Measured **38 of 38** fixed-path
cleanups already gate on the staging register — the rule is a ratchet, and an unchecked 38/38 with an
operator-supplied staging directory is one copy-paste from a destructive regression.
**Why:** ruling 10 fixes the key-order collision; the wrapper text is v1's; ruling 25 closes the single-task
question the audit left disputed (fsha's five single-task wrappers and wsus_client's one wrapper conform).
Adjacency is the rule's product: wsus decision 38 put actor and END proof side by side, where two reviewers
saw the proof normalising differently from its actor.
**Checked by:** a new `rolecheck/lint/rules/block_01.py` for wrapper key presence and order, for an
empty wrapper — a wrapper whose `block:` list, or whose `rescue:` or `always:` list where present,
holds no task, which is a finding under ruling 25 — and for a task whose name carries a stage token
but whose parent is not a block named with that token. ansible-lint
26.8.0 has no `max-block-depth` rule — `complexity[nesting]`, which replaced it at 26.2.0, is
`experimental` and absent from the `enable_list`, so depth is unenforced; purpose is `review`.

