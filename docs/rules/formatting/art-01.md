---
id: "ART-01"
title: "ART-01"
sidebar_label: "ART-01"
sidebar_position: 18
tier: "`auto*`/`review`"
checked_by: "a new dataflow rule — staging copy destination, then the same path digest-checked before an execution sink; the `win_package` option pair is the reliable `auto*` portion. Dynamic p"
---

**ART-01** `auto*`/`review` — A delivery chain that downloads and stages executable content must verify
its pinned digest against the exact execution-site path after the last transfer and before that path is
executed — not only at the download site. A `win_package` invoked with a local `path:` carries both
`checksum:` and `checksum_algorithm:` naming sha256 or stronger; an artifact executed by any other
module verifies the digest in the executing script or in an immediately preceding read of the staged
file, and a run whose staged digest does not match the pin fails.
**Why:** ruling 37 (2026-09-23), from R03 of the deleted guides. Hashing a controller download does not
authenticate the bytes later copied to and executed on the guest, and convergence cannot observe the
difference: a malicious but installable package leaves every GATE-01 counter green. Ansible documents
`ansible.windows.win_package.checksum` as calculating the digest *before executing* a local or
downloaded package, so the rule's timing and location are upstream-supported. Measured: **40 of 41**
staged-installer chains already verify at the execution site; the exception is `wazuh_agent` on Windows,
which verifies the controller file (`tasks/present_windows.yml:120-131`), copies it to the target, then
executes that path with no `checksum` (`:137-154`) — found independently by the 2026-09-21 s3ad audit
(`P2-S3AD.md:275`).
**Checked by:** a new dataflow rule — staging copy destination, then the same path digest-checked before
an execution sink; the `win_package` option pair is the reliable `auto*` portion. Dynamic paths, shell
execution, archive expansion and verification delegated into another role are `review`.

