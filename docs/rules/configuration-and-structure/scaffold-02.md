---
id: "SCAFFOLD-02"
title: "SCAFFOLD-02"
sidebar_label: "SCAFFOLD-02"
sidebar_position: 6
tier: "`auto`/`review`"
checked_by: "`rolecheck/structure.py` `SCAFFOLD-02` (key 163edb4; comment presence new); \"why\" is `review`."
---

**SCAFFOLD-02** `auto`/`review` — `defaults/main.yml` defines the top-level `<role>_defaults` key the
loader reads, and each default carries a whole-line comment immediately above it.
**Why:** a wrong key fails silently; ruling 19's third limb.
**Checked by:** `rolecheck/structure.py` `SCAFFOLD-02` (key 163edb4; comment presence new); "why" is
`review`.

