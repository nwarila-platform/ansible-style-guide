---
id: "scope"
title: "Scope"
sidebar_position: 1
---


Every Ansible role folder — each immediate subdirectory of `applications/`, `host_roles/`,
`operating_systems/`, `utilities/` or `roles/`, whether its namespace directory sits under `ansible/`
or at the repository root. A rule naming narrower files keeps that scope (FACT-01: an application
role's task files).

**The framework loader (`tasks/main.yml`)**: exempt from every *authoring* rule here — adopted
byte-identical from upstream, never edited by a consumer. It is **no longer exempt from FMT-01 or
LEN-01** (ruling 20); every other exemption stands. It was the worst width offender, 44 lines over 97
in 460. Because formatting changes its digest, LOADER-01's digest is republished by migration item 6
*before* any consumer formats a copy.

