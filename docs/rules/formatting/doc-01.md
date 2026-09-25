---
id: "DOC-01"
title: "DOC-01"
sidebar_label: "DOC-01"
sidebar_position: 13
tier: "`autofix`"
checked_by: "the formatter; CI asserts a clean diff. `rolecheck/lint/yamllint.yml`'s `document-start` stops being a finding that day."
---

**DOC-01** `autofix` — Ansible files carry no `---` document-start marker; the header box marks the
start of the file.
**Why:** ruling 3; 313 findings, zero gain, and **every repo already disables `document-start`** [§4].
**Checked by:** the formatter; CI asserts a clean diff. `rolecheck/lint/yamllint.yml`'s
`document-start` stops being a finding that day.

