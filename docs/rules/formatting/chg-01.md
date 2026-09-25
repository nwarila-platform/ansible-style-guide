---
id: "CHG-01"
title: "CHG-01"
sidebar_label: "CHG-01"
sidebar_position: 22
tier: "`auto*`/`review`"
checked_by: "`ansible-lint no-changed-when` for the bare form (163edb4); the paired `check_mode: false` on a `command`/`shell` read is a new `rolecheck/lint/rules/chg_01.py`; the read-or-scratc"
---

**CHG-01** `auto*`/`review` — `changed_when: false` covers reads and scratch the same file deletes in
its `always:`, never a durable mutation. A `command`/`shell` read carries `changed_when: false`
**and** `check_mode: false` together. A task running a first-class script carries no `changed_when` —
`$Ansible.Changed` is the report. `changed_when: true` appears only on a mutation already gated by a
`when:` proving it is needed. **A task that changes on every converge violates GATE-01; no
expected-change budget exists. It must gain an independent readback/gate or be redesigned.**
**Why:** the normative clauses are v1's, kept as written. The final clause replaces v1's
expected-change budget, which ruling 4's `changed=0` gate makes impossible to honour — a necessary
consequence of ruling 4 despite the "as written" instruction (owner confirmation item 5).
**Checked by:** `ansible-lint no-changed-when` for the bare form (163edb4); the paired
`check_mode: false` on a `command`/`shell` read is a new `rolecheck/lint/rules/chg_01.py`; the
read-or-scratch versus durable-mutation classification, necessity and readback are `review`.

