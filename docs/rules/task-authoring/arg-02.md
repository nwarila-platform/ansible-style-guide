---
id: "ARG-02"
title: "ARG-02"
sidebar_label: "ARG-02"
sidebar_position: 4
tier: "`auto`"
checked_by: "`ansible-lint fqcn` (production only; 163edb4). ---"
---

**ARG-02** `auto` — Invoke every module by fully-qualified collection name.
**Why:** kept as written, verbatim. The `library/` collision (§3.4) is **not** resolved by
exempting bare invocation: such a module cannot carry a collection name and so cannot conform.
**There is no exception route (ruling 31, 2026-09-21): a role ships no role-local module;
`library/`, `lookup_plugins/` and `module_utils/` hold only `.gitkeep`; a module the fleet needs
is published in a namespaced collection or removed with its caller.** `s3_artifact_delivery`'s
`library/s3_artifact.py` (owner action 2) therefore has two outcomes, promotion or deletion.
SCAFFOLD-01 requires the directory, not permission to invoke code from it.
**Checked by:** `ansible-lint fqcn` (production only; 163edb4).

---

