---
id: "enforcement"
title: "Enforcement"
sidebar_position: 9
---


**The formatter** owns FMT-01, FMT-02, LEN-01's reflow and DOC-01. It rewrites; it never reports. CI
fails only on a dirty tree — a clean diff, not a finding count (rulings 3 and 14).

**Staged enforcement.** Every rule clause sits in exactly one stage; nothing under `new checker
required` or `review` blocks a build today.

| Stage | Rule clauses |
|---|---|
| **Implemented today** (`rolecheck` at `163edb4`; external harnesses as named) | SCAFFOLD-01 directories, SCAFFOLD-02 key, SCAFFOLD-03 four files, LOADER-01 sha256 comparison, FLOOR-01 presence warning (against today's wrong constant), FACT-01 presence, FMT-01/FMT-02 findings as emitted today (retired when the formatter lands), NAME-01 lexical, LOOP-01 spelling, REG-01 name shape, LEN-01/DOC-01 yamllint findings as emitted today (retired at the formatter), BOOL-01 (`truthy`), FLOW-01 spacing, ARG-02 (`fqcn`), KEY-01 part (`key-order`), ERR-01 bare (`ignore-errors`), CHG-01 bare (`no-changed-when`), HAND-01 inverse (`no-handler`), VARNAME-01 (`var-naming`), SPEC-01 shape (`schema`), PS-01 script contract (the pinned `pester-matrix.yaml` workflow, already called from each repo's `powershell.yml`) |
| **New checker required** | GUIDE-01; SPEC-01 coverage; SCAFFOLD-01 placeholder predicate; SCAFFOLD-02 comment presence; SCAFFOLD-03 argument spec; LOADER-01 digest read; NAME-01 handlers; KEY-01 module-last, blank line, wrapper order, argument sort; VAR-01; WHEN-01a/b/c; GUARD-01 class markers and `when:` presence; GUARD-02 mechanical; ERR-01 adjacency and the `# rc-contract:` marker; CHK-01 `when: not ansible_check_mode` plus explanatory-comment form; CHG-01 paired `check_mode: false`; LOG-01 AST clauses; RESCUE-01; COM-01 mechanical; QUOTE-01; SCALAR-01 spelling; FLOW-01 sequence/control; LOOP-01 triggers; REG-01 remaining; VARNAME-01 split; FACT-01 annotations; STRUCT-01; IGNORE-01; PS-01 enumerated forms and stub/sibling presence; HAND-01 topics and guard symbol table; BLOCK-01 wrapper keys, order and empty-wrapper rejection; META-01 allowlist; DOC-02 structure |
| **Gates only after prerequisite** | ARG-01, WAIT-01, NULL-01, CHK-01 `check_mode.support` pairing (generated metadata); FLOOR-01 floor value (packaged spec); DOC-02 inputs region (renderer `rolecheck/render/inputs.py`, new); FMT-01/FMT-02/DOC-01 rewrite and LEN-01 reflow, verified as a clean diff (formatter); LEN-01 residual hard-width warning (`rolecheck/report.py`, after `yaml[line-length]` joins the `skip_list`); GATE-01 (`ansible-framework`'s `scripts/gate-idempotence.py`, new; `ansible-framework`'s `.github/workflows/conformance.yml`, new; `ansible.posix`) |
| **Review** | NAME-01 staging; SPEC-01 descriptions; SCAFFOLD-02 "why"; ARG-01 intent; GUARD-01 class judgments, `fail_msg`/`that:` clause correspondence, and whether `when:` names the modes in which the value is used; GUARD-02 refusal and remedy; CHK-01 read-versus-mutation classification and justification; ERR-01 read-only-versus-mutating classification, refusal and rc truth, and whether a rescue carve-out is genuinely best-effort cleanup before a deliberate failure; WAIT-01 cited race; LOG-01 placement and change set; COM-01 platform-claim detection, provenance and fact preservation; NULL-01 comment; SCALAR-01 newline-sensitivity; REG-01 rc contract; FACT-01 exemption truth; STRUCT-01 empty overlay; PS-01 quality; HAND-01 flush placement; CHG-01 read-or-scratch classification, necessity and readback; BLOCK-01 purpose; META-01 smuggled prose; DOC-02 content |

**`rolecheck`, on the composed tree**, is the single lint entry point: it invokes `ansible-lint` at
`profile: production` itself via `rolecheck/lint/ansible-lint.yml` (`use_default_rules: true`, an
`enable_list` naming every custom rule, `skip_list: yaml[comments]`, `var-naming[non-string]` and —
new — `yaml[line-length]`, so hard width leaves the blocking path and becomes a LEN-01 warning). The
workflow therefore runs **no second `ansible-lint` step**. `name[prefix]` is opt-in and stays
unlisted, so production does not undo ruling 5; `max-block-depth`, `max-tasks` and
`avoid-dot-notation` survive only as stale keys in ansible-lint 26.8.0's profile tables and are not
rule ids, so no rule cites them.

**The CI gate every repo runs** is one shared quality workflow, identical in all six repos (ruling
14): compose the tree; run the formatter and fail on a dirty tree; `rolecheck` the composed tree — a
consumer's roles overlaid on the framework at its pin — failing on any non-warn finding from a
**promoted** rule domain and reporting every other; then the pinned Pester workflow
`NWarila/powershell-template/.github/workflows/pester-matrix.yaml@758b3313d34269f10dcf1a1b07837c0b887bdc87`,
called from each repo's `.github/workflows/powershell.yml`, for PS-01's script contract. It lands in
**report-only mode**, and a domain blocks only once the migration item that implements its checker and
repairs the fleet has landed.

**GATE-01 is not part of that workflow.** It runs in each repo's own `aws-deploy.yml`, because OIDC
pins `job_workflow_ref` to that file; the gate is a script owned by `ansible-framework` checked out at
the existing pin, and a credential-free reusable workflow checks that each repo calls it.

---

