---
id: "DOC-02"
title: "DOC-02"
sidebar_label: "DOC-02"
sidebar_position: 25
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/doc_02.py` for H1 count, heading level and order; the byte-for-byte inputs diff against `rolecheck/render/inputs.py`; the formatter for width; content i"
---

**DOC-02** `auto*`/`review` — A role README opens with `` # `<role_name>` role `` and carries its
sections in order: capability summary, a `> **Scope:**` callout, Composition and prerequisites,
**Inputs**, Configuration, any role-specific sections, State, Design invariants, First-class
PowerShell, Verification. Headings are `##` only, sentence case, no numbering, emoji, badges or
contents; **exactly one H1**. **Design invariants** is a numbered list of entries `INV-nn`, each
the fact, how it was measured (date, host or commit) and its consequence; these are the targets
COM-01's tags cite. Each numbered item's text begins with one unique literal `[INV-nn]`; each
platform-fact entry begins with one unique literal `[APF-nn]`. An entry ends immediately before
the next label and states the fact, measurement, and consequence. **Numbering is role-local and
begins at `INV-01`; it restarts in every role. Where a role already carries unnumbered Design
invariants prose, those entries are labelled in their existing order before any new entry is
appended, so a label never moves once cited. A role that needs an invariant and has no Design
invariants section gains one in DOC-02's position [ruling 43, 2026-09-23].** A fact shared across roles
lives in `docs/reference/platform-facts.md` as `APF-nn`; a decision or rejected alternative lives
in `docs/decision-records/repo/` on the org template (ADR-0001) and is cited as `[ADR-nnnn]`;
design narrative lives in `docs/explanation/` (ADR-0002, Diataxis). The Inputs body is generated
from `meta/argument_specs.yml` by the renderer at `rolecheck/render/inputs.py`, delimited by the
exact markers `<!-- rolecheck:inputs:begin -->` and `<!-- rolecheck:inputs:end -->`; CI compares
that region byte-for-byte against the renderer's output. Prose is reflowed to 97 columns by the
formatter (LEN-01).
**Why:** rulings 19 and 20; pdq ships 5 H1s, fsha's README claims a DACL its defaults removed.
**Checked by:** a new `rolecheck/lint/rules/doc_02.py` for H1 count, heading level and order; the
byte-for-byte inputs diff against `rolecheck/render/inputs.py`; the formatter for width; content
is `review`.

