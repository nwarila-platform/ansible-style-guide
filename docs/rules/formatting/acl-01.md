---
id: "ACL-01"
title: "ACL-01"
sidebar_label: "ACL-01"
sidebar_position: 20
tier: "`review`"
checked_by: "`review`. **No `auto` proxy exists**: no machine-readable marker tells a checker whether a role claims whole-ACL ownership, so \"a bare `win_acl` under a whole-ACL claim is a findin"
---

**ACL-01** `review` — Where configuration declares a complete ACL, verification canonicalizes and
compares the complete explicit ACE set, keyed by SID, rights, type, inheritance flags and propagation
flags, with the declared set by equality; every missing or undeclared explicit ACE fails. Inherited ACEs
are collected and reported separately and are not counted in that equality. Where the declared contract
protects inheritance, the readback also requires `AreAccessRulesProtected`; rejecting any observed
inherited ACE is an accepted equivalent to reporting it as drift. A total count alone and a containment
test are not proofs. Where a role owns only a named grant on a shared ACL, it states that boundary and
proves the complete explicit ACE set for that principal, leaving other principals outside its contract.
**Why:** ruling 36 (2026-09-23), from R12 of the deleted guides. Containment proves only that a wanted
ACE exists, so an undeclared explicit grant survives convergence forever while GATE-01 reports
`changed=0` — reachable now on aws-workspace-builder's OpenSSH administrators key, which says
`Grant Only` while applying additive `ansible.windows.win_acl` entries
(`openssh_server/tasks/present_windows.yml:315-342`), the file sshd's trust depends on. Total ACE counts
are separately unsound: Windows normalizes rights beyond the friendly declaration, so fsha's declared
`Modify` could never match once Windows added `Synchronize` (`e224476`). Measured: **0 of 5** reusable
ACL implementations conform to this text, across four incompatible idioms; even
`Set-ClusteredFileServer.ps1`, which requires `AreAccessRulesProtected` and rejects inherited ACEs,
still uses `$Rules.Count` and does not report inherited ACEs separately.
**Checked by:** `review`. **No `auto` proxy exists**: no machine-readable marker tells a checker whether
a role claims whole-ACL ownership, so "a bare `win_acl` under a whole-ACL claim is a finding" is not
decidable today. Promote to an `auto*` proxy only once such a marker is ratified. Pester behaviour tests
are the executable proof for each first-class ACL implementation.

