---
id: "LOADER-01"
title: "LOADER-01"
sidebar_label: "LOADER-01"
sidebar_position: 3
tier: "`auto*`"
checked_by: "`rolecheck/structure.py` `LOADER-01` (163edb4; digest-from-artifact new)."
---

**LOADER-01** `auto*` — Every role under `applications/` ships the framework loader as
`tasks/main.yml`, byte-identical, never edited. Check: sha256 equals the digest published in the
pinned framework's `meta/loader-digest.txt`, which the checker reads rather than pinning in code
(`62925c47…` today, superseded by migration item 6). A role under `operating_systems/` is out of
scope: its `tasks/main.yml` is OS-specific logic, not a merge-and-dispatch loader (owner ruling
2026-09-17). `host_roles/` and `utilities/` are governed by their own kind, not by this rule.
**Why:** byte-identical loaders stop 49 copies drifting; wazuh's fork costs 111 findings.
**Checked by:** `rolecheck/structure.py` `LOADER-01` (163edb4; digest-from-artifact new).

