---
id: "CHK-01"
title: "CHK-01"
sidebar_label: "CHK-01"
sidebar_position: 1
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/chk_01.py` for the `check_mode.support` pairing over the generated metadata and for the presence of the `when: not ansible_check_mode` comment; whether "
---

**CHK-01** `auto*`/`review` — Check mode is supported. A read carries `check_mode: false` so it
executes under `--check`. A unit that genuinely cannot run under `--check` carries `when: not
ansible_check_mode` with a comment stating why. A module whose `ansible-doc` `check_mode.support` is
not `full` carries an explicit `check_mode:` or `changed_when:`. **Fresh-host `--check` is out of
scope (decision 44); the converged-host leg is GATE-01's.**
**[Ruling 39b, 2026-09-23]** A conditionally included unit's postconditions are evaluated **after and
outside** its `include_tasks`, so verification still runs on the converged path where the include is
skipped. Placement is `review`. Executed: with the postcondition inside the included file, a false include
gate skipped both the read and the assertion and the play wrongly **succeeded** — `ok=1 changed=0
failed=0 skipped=1`, exit 0, ansible-lint clean. A dynamic include's condition applies to the include
statement, not to the tasks inside it, which is exactly why the verifier must sit outside. Measured 4 of 4
current sites already place it outside; `s3_artifact_delivery`'s `fetch.yml:128-153` is the exemplar.
**Why:** ruling 15, Red Hat 4.1.8; **0 of 6 repos run `--check`**, and wazuh's unguarded probe makes
`validate.yml:55` error instead of validate [§7].
**Checked by:** a new `rolecheck/lint/rules/chk_01.py` for the `check_mode.support` pairing over the
generated metadata and for the presence of the `when: not ansible_check_mode` comment; whether a task
is a read or a mutation, and justification quality, are `review`; GATE-01 executes the leg.

