---
id: "arg-01-tables"
title: "ARG-01 tables"
sidebar_position: 10
---


**Generated toolchain metadata** (ruling 13) — applicability, mutually-exclusive groups,
`check_mode.support`, timeout options and documented explicit-clear options are **generated** from the
pinned ansible-core and collections, regenerated on every bump, and shipped in the toolchain image at
`rolecheck/arg-tables/<core-version>/`. The generator requires `pwsh` for the Windows modules and is a
maintainer/CI tool. It is machine output: no entry is ratified and it is never hand-edited. CHK-01's
`check_mode.support` pairing, WAIT-01's timeout options and NULL-01's explicit-clear options read from
this same artifact. The artifact carries **module-level fields only — it defines no task-mode or
action field** — so whether a given task is a read or a mutation is `review` for CHK-01, ERR-01 and
CHG-01; `check_mode.support` describes the module, not the task's intent.

**Owner-ratified policy overrides** — a short, hand-authored table of exceptions the generated
metadata cannot express. Additions require ratification.

| Module | Option | May be omitted only where |
|---|---|---|
| `ansible.windows.win_regedit` | `delete_key` | `state` is stated as the literal `present` |

**ARG-01 does not gate until both artifacts exist**; until then it is `review`.

---

