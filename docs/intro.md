---
id: "intro"
title: "Ansible Style Specification"
sidebar_label: "Overview"
sidebar_position: 0
slug: "/"
---

# Ansible style specification v2 (ratified 2026-09-21)

One stable ID per rule, one normative statement, the measured reason, and where it is checked. Full
rationale stays in the audit record (`.audits/style-audit-2026-09-21/`), keyed by the same IDs.

Status: **RATIFIED by the owner on 2026-09-21 ("I approve") on the 25 rulings of the same day;
enforcement staged.** Amended 2026-09-21/22 (rulings 26-33): COM-01 comment length and
cite-don't-narrate; DOC-02 Design invariants format; SPEC-01 and migration item 10 corrected
so `tasks/validate.yml`, not the argument spec, is the input contract (ruling 33). Tiers are the contract the CI phase
implements, not a claim that every checker exists today.

| Tier | Meaning |
|---|---|
| `auto` | mechanically checked; a violation fails the build |
| `auto*` | mechanically checkable, checker not yet written |
| `review` | judgment; belongs to a fan-out audit domain |
| `warn` | mechanically checked; reported as a warning, never fails the build |
| `autofix` | rewritten by the formatter; never counted as a finding (ruling 3) |

A hybrid tier (`auto*`/`review`) splits the rule's clauses: `Checked by:` names the automatic ones
first and the semantic ones as `review`. No semantic judgment is listed among a blocking checker's
responsibilities, and every `Checked by:` names one of exactly six checker kinds — a real rolecheck
rule file; a real ansible-lint rule id; the formatter; the inputs renderer `ansible-role-check`'s
`rolecheck/render/inputs.py` (new); the framework-owned deploy gate `ansible-framework`'s
`scripts/gate-idempotence.py` (new) with its conformance workflow `ansible-framework`'s
`.github/workflows/conformance.yml` (new); and the external Pester harness
`NWarila/powershell-template/.github/workflows/pester-matrix.yaml@758b3313d34269f10dcf1a1b07837c0b887bdc87`,
called from each repo's `.github/workflows/powershell.yml` — or `review`. "163edb4" marks a check
that exists; "new" marks one to be written.

