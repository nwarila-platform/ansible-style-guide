---
id: "MUT-01"
title: "MUT-01"
sidebar_label: "MUT-01"
sidebar_position: 17
tier: "`auto*`/`review`"
checked_by: "a new rule identifying known destructive storage modules and requiring a dominating read/classify/assert path before them; recognizing whether a marker is durable, and whether a st"
---

**MUT-01** `auto*`/`review` — Before the first destructive mutation of a declared **storage** resource,
read observed state and refuse a foreign or occupied target; only blank, already-ours, or a positively
recognized resumable state proceeds. Ownership is recognized by a durable convention the role itself
writes — a filesystem label or equivalent durable storage marker — never by size, index or enumeration
order. Refusal carries an actionable `fail_msg`. `windows_disk_manager` is a named exception for its
`set_fact` accumulation and its classifier's `| first`; its foreign-layout assert still precedes
initialization, partitioning and formatting.
**Why:** ruling 38 (2026-09-23), from R08 of the deleted guides. A valid identifier can still point at an
occupied foreign disk; idempotent provisioning modules then initialize, partition or format the wrong
resource and report success. Executed: starting from a disk holding `FOREIGN OWNER DATA`, an unguarded
mutation exited green with `changed=1` and replaced it, and ansible-lint saw nothing. Framework commit
`5f5cae8` records the same ownership lesson in `windows_disk_manager`. Measured: **2 of 2** authored
destructive storage provisioners already conform, so this ratifies existing practice rather than
demanding migration. **Scope is storage by owner ruling (2026-09-22):** the broader reading over every
destructive mutation — roughly 228 sites, including 193 `state: absent` in aws-workspace-builder, of
which 3 carry an ownership marker — is a separately measured amendment needing a resource-neutral state
model, because blank / occupied / resumable are storage words that do not transfer as written.
**Checked by:** a new rule identifying known destructive storage modules and requiring a dominating
read/classify/assert path before them; recognizing whether a marker is durable, and whether a state is
genuinely resumable, is `review`.

