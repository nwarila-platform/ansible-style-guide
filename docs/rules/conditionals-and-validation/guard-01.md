---
id: "GUARD-01"
title: "GUARD-01"
sidebar_label: "GUARD-01"
sidebar_position: 5
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/guard_01.py` for class-marker presence and `when:` presence; the class judgments and the `fail_msg`/`that:` clause correspondence are `review` — no mach"
---

**GUARD-01** `auto*`/`review` — `validate.yml` carries **only** cross-field checks and safety-critical
checks: a merged value read by a destructive predicate, and a gate that cannot be checked from inside
itself. Each assert carries a whole-line class marker — exactly `# check: cross-field`,
`# check: safety-critical` or `# check: self-gate` — and a `when:` naming the modes in which the value
is used, so a run never fails on a variable its mode will not read. The `fail_msg` describes exactly
the clauses present.
**[Ruling 34, 2026-09-23]** Configure a state the action can idempotently configure instead of
asserting it: an assert that re-checks what a module in the same role just set duplicates that module's
own contract. GATE-01's second converge proves reported idempotence; it does not prove correctness — a
role that configures nothing converges clean twice — so this narrows duplicate assertions and does not
replace NAME-01's independent product readback.
**Retired:** the set-equality clause — superseded by SPEC-01 (ruling 1).
**Why:** rulings 1 and 24; decision 61 superseded in place with a dated bracketed amendment. Measured:
an empty `ownership_marker` makes a deletion predicate `-like '**'`, true for any description, so a
foreign GPO is deleted and the run reports success; `wsus`'s `tls.enabled` takes `'fase'` as false;
`validate.yml:113-124` promises three checks its `that:` omits (`47f0acb`).
**Checked by:** a new `rolecheck/lint/rules/guard_01.py` for class-marker presence and `when:`
presence; the class judgments and the `fail_msg`/`that:` clause correspondence are `review` — no
machine-readable per-clause mapping between a prose message and a `that:` list exists to compare.

