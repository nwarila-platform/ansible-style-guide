---
id: "SPEC-01"
title: "SPEC-01"
sidebar_label: "SPEC-01"
sidebar_position: 4
tier: "`auto*`/`review`"
checked_by: "a new `rolecheck/lint/rules/spec_01.py` for presence, the named-authority comment and entry-time scope; `ansible-lint schema` for the file's shape; `validate.yml` coverage and desc"
---

**SPEC-01** `auto*`/`review` — **Every role ships `meta/argument_specs.yml`, and
`tasks/validate.yml` is the role's input contract.** They are not interchangeable and the spec
file is not the contract. ansible-core validates an argument spec before the role's first task;
at that moment `<role>_running` does not exist, because the shared loader builds it three regions
later by merging `<role>_defaults`, the `vars/<family>[_<env>]` overlays and the caller's
override dict. An argument spec therefore cannot see the object every role consumes, and a value
that only becomes invalid through the merge — a bad default, a bad overlay — is invisible to it.
The leaves are also nested inside `<role>_defaults` and the caller's `<role>:` dict rather than
being top-level variables, so declaring a leaf as a spec option makes ansible-core look for a
variable nothing sets and pass trivially, which is worse than not checking. The spec file
therefore declares only what ansible-core can genuinely validate at entry — `ENV`, `state`, and
any true top-level role parameter — each stating `type` and `description`, plus `default`,
`required` and `choices` where the schema admits them. A role with no such input still ships a
schema-valid spec, because the file is also where the contract is named: it carries a comment
stating that `tasks/validate.yml` validates the merged `<role>_running` and is the authority.
`tasks/validate.yml` keeps the full per-field contract and **is not reduced** to cross-field
checks. An input read from `config` and unchecked there is the finding; absence from the argument
spec is not.
**Why:** ruling 1 and Red Hat 4.1.20 gave the file; **ruling 33** corrected what it can assert.
`python3_pip`'s spec declares `ENV` and `state` while its real surface — `package_manager`,
`self_upgrade`, `templates` — is validated only by `validate.yml` against `config`. **49 of 69
metas document inputs nothing enforces** [§3.12], which the file addresses; the
merged-configuration contract it does not.
**Checked by:** a new `rolecheck/lint/rules/spec_01.py` for presence, the named-authority comment
and entry-time scope; `ansible-lint schema` for the file's shape; `validate.yml` coverage and
description adequacy `review`.

