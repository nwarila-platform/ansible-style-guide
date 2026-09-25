---
id: "revision-log"
title: "Revision log"
sidebar_position: 12
---


1. **PS-01** — "Every guest PowerShell block, however small, is never inlined," plus the enumerated
   guest-block forms (`win_powershell.script`, `win_shell`, qualified `win_command`/`win_psexec`, `raw`).
2. **NAME-01** — "Subsystem navigation uses STRUCT-01's permitted `<state>_<family>.yml` file and its
   region index; it never extends the stage token set or splits a state/family on length."
3. **ARG-02** — v1 sentence restored verbatim; rationale now says such a module "must be removed,
   promoted into a collection, or obtain an explicit owner exception"; unused `library/` holds `.gitkeep`.
4. **BLOCK-01** — v1's "Each stage is a block wrapper task…" restored with KEY-01's ratified order, plus
   the pending note, since replaced by owner ruling 25 (every existing stage is a wrapper, even for one task).
5. **FACT-01** — tier `auto`/`review`; two exact exemption annotations; "`fact_01.py:35` scoping to
   `applications/` is the rule, not a gap"; the utilities scope fix is gone from migration item 7.
6. **COM-01** — "platform behaviour"; the contiguous-whole-line-run block definition; the enumerated
   ansible-lint/yamllint directives; fact preservation assigned to `review`.
7. **GATE-01** — "from JSON callback output" restored, plus bullets naming `ansible.posix.json`, the
   `stats` schema, the job-id artifact name, `ansible-inventory` hosts, the `local` exclusion, the
   check-leg zero predicate and awb's lane.
8. **CHG-01** — "A task that changes on every converge violates GATE-01; no expected-change budget
   exists. It must gain an independent readback/gate or be redesigned."
9. **ARG-01 tables** — "Generated toolchain metadata … no entry is ratified" split from "Owner-ratified
   policy overrides"; ARG-01 stays `review` until both exist.
10. **SPEC-01** — v2 made the argument spec "the single source of the input contract".
    **Superseded by ruling 33 (2026-09-22):** ansible-core validates it before the role's first
    task, so it cannot see `<role>_running`, and the leaves are nested rather than top-level.
    `tasks/validate.yml` is the contract; the spec file declares entry-time inputs and names the
    authority in a comment. Migration item 10 no longer reduces `validate.yml`.
11. **LOG-01/RESCUE-01** — "For a register created inside a `no_log` block, LOG-01 is narrower than
    RESCUE-01"; "Only `ansible_failed_result.msg` requires a default."
12. **Loader** — "no longer exempt from FMT-01 or LEN-01"; item 6 formats the upstream loader and
    publishes its new sha256 before any consumer formats a copy.
13. **KEY-01** — "`ansible-lint key-order` for name-first and `block`/`rescue`/`always`-last only;
    module-last, the blank line, wrapper order and argument sorting are … `key_01.py`."
14. **Tiers** — hybrid splits and objective predicates applied throughout (SCAFFOLD-01's
    `.gitkeep`-or-content predicate, FLOW-01's 97-column "short", LOOP-01's two triggers, STRUCT-01's
    dispatch matrix, IGNORE-01's two regexes, and `review` splits on GUARD-01/02, CHK-01, ERR-01,
    WAIT-01, LOG-01, COM-01, NULL-01, SCALAR-01, FACT-01, HAND-01, CHG-01, BLOCK-01, META-01, DOC-02).
15. **Cosmetic** — item 6 says **97/warn**; `yaml[line-length]` joins the `skip_list` and LEN-01 becomes
    a `rolecheck/report.py` warning; FMT-01/FMT-02/DOC-01 stop emitting findings when the formatter lands.
16. **Canonical spec** — GUIDE-01 narrowed to "No consumer repository"; FLOOR-01 parses
    `rolecheck/spec/ANSIBLE-STYLE-SPEC.md`, named as the sole exception (owner action 4).
17. **Enforcement honesty** — the staged table replaces "rolecheck blocks", and "The workflow therefore
    runs **no second `ansible-lint` step**" records that rolecheck embeds production lint.
18. **Migration** — checker, formatter, generator, renderer and remediation are items 6–12 before the
    report-only workflow at 13; "each repo-scoped work piece is one PR per repo"; owner actions 2–5 added.

**Round 3** — the four edits required by `exchange/P2-SPEC-V2-R2.md` §5, each mapped to the sentence
that now satisfies it:

19. **Edit 1, GATE-01 artifact and checker paths** — the normative clause now reads "must satisfy **the
    same four-zero predicate over that leg's own fresh JSON artifact in the same schema**", which keeps
    the two distinct filenames the freshness bullet already specifies; `Checked by:` now reads "the
    framework-owned gate script `ansible-framework`'s `scripts/gate-idempotence.py` (new), run from each
    repo's own `aws-deploy.yml` at the existing pin; conformance by the credential-free reusable workflow
    `ansible-framework`'s `.github/workflows/conformance.yml` (new)"; the prerequisite row carries both
    paths; and the checker-provenance paragraph now admits "the framework-owned deploy gate
    `ansible-framework`'s `scripts/gate-idempotence.py` (new) with its conformance workflow
    `ansible-framework`'s `.github/workflows/conformance.yml` (new)" as a checker kind. Both paths are
    new files: `ansible-framework/scripts/` holds no gate script today and its `.github/workflows/`
    holds only `ci.yml`, `release-please.yml` and `security.yaml`.
20. **Edit 2, tier closure** — GUARD-01's `Checked by:` now reads "a new `rolecheck/lint/rules/guard_01.py`
    for class-marker presence and `when:` presence; the class judgments and the `fail_msg`/`that:` clause
    correspondence are `review` — no machine-readable per-clause mapping between a prose message and a
    `that:` list exists to compare", and the review row carries that clause. For the generated metadata,
    the ARG-01 tables section now reads "The artifact carries **module-level fields only — it defines no
    task-mode or action field** — so whether a given task is a read or a mutation is `review` for CHK-01,
    ERR-01 and CHG-01", with the matching splits in CHK-01 ("whether a task is a read or a mutation, and
    justification quality, are `review`"), ERR-01 ("the read-only-versus-mutating classification and the
    truth of both carve-outs are `review`") and CHG-01 ("the read-or-scratch versus durable-mutation
    classification, necessity and readback are `review`").
21. **Edit 3, ruling 25 / HAND-01** — HAND-01 now reads "**The stage container is the named block wrapper
    BLOCK-01 requires, not the region FMT-02 delimits**: the first flush is the last child of that
    wrapper's `block:` list, and the second flush is a child of that wrapper's `always:` list. FMT-02
    regions are navigation only; they never locate a flush." `block_01.py`'s stated responsibility now
    includes "an empty wrapper — a wrapper whose `block:` list, or whose `rescue:` or `always:` list where
    present, holds no task, which is a finding under ruling 25", and the staged table entry reads
    "BLOCK-01 wrapper keys, order and empty-wrapper rejection".
22. **Edit 4, enforcement honesty** — the staged-enforcement paragraph now reads "Every rule **clause**
    sits in exactly one stage", the table's column head is now "Rule clauses", and every hybrid clause was
    re-checked against the four rows: FMT-01/FMT-02 and LEN-01/DOC-01 split into "findings as emitted
    today (retired when the formatter lands)" versus the formatter's "rewrite … verified as a clean diff";
    LEN-01's residual `report.py` warning is named in the prerequisite row; FLOOR-01 splits into "presence
    warning (against today's wrong constant)" and "floor value (packaged spec)"; LOADER-01 into "sha256
    comparison" and "digest read"; BOOL-01 is listed on its own; PS-01 splits into "enumerated forms and
    stub/sibling presence" (new) and the harness's "script contract" (implemented today); the previously
    unrowed CHG-01 "paired `check_mode: false`" was added to the new-checker row; and the CHK-01/ERR-01/
    CHG-01 classifications moved from the prerequisite row to review. The checker-provenance sentence now
    names "exactly six checker kinds", including the renderer `rolecheck/render/inputs.py` (new), the gate
    and conformance scripts, and the external harness; PS-01 and the CI-gate paragraph both now name "the
    pinned Pester workflow
    `NWarila/powershell-template/.github/workflows/pester-matrix.yaml@758b3313d34269f10dcf1a1b07837c0b887bdc87`,
    called from each repo's `.github/workflows/powershell.yml`" instead of a generic harness.

### Post-round-3 (planner, applied verbatim from P2-SPEC-V2-R3.md "Remaining items"; not re-audited by Codex)
1. Staged table: `New checker required` gains CHK-01's `when: not ansible_check_mode` plus explanatory-comment form; `Review` gains GUARD-01 mode correspondence and ERR-01 cleanup truth.
2. Migration item 8 names only the module-level data the generated artifact supplies; task intent stays review.

### Amendment 2026-09-21 (rulings 26-28, owner "approve")
1. COM-01: 3-line block cap, 10-line header cap, bracketed tags `[INV-nn]` / `[APF-nn]` /
   `[ADR-nnnn]`, fact moves with its comment.
2. DOC-02: Design invariants as numbered `INV-nn` entries; `docs/reference/platform-facts.md`;
   decision records on the org template; narrative in `docs/explanation/`.
3. Post-check (exchange/P2-COM01-AMEND.md, six blocking edits applied verbatim): comment-block and
   header-description definitions, tag resolution, entry syntax, date and commit grammars, history's
   home, and the platform-facts tag renamed `APF-nn` because `PF-n` already names talos-cluster
   tech-debt items.
4. Rulings 29 and 30 (owner, 2026-09-21, raised by the Codex P2 of WO-COM-01): platform-claim detection
   is `review` and the checker validates the grammar and resolution of what is present; a whole-line
   comment run that is neither a comment block nor the header description is a finding.
5. Rulings 31 and 32 (owner, 2026-09-22): ARG-02 has no exception route (no role-local modules); GATE-01's
   expected hosts are the union of group host lists, not `_meta.hostvars` (SPIKE-GATE-01 F4), exclusion is
   inventory-declared local only with play-level and CLI local forbidden in gated plays, an empty expected set
   fails, and the spike's capture facts and open proofs are written in.

### Amendment 2026-09-23 (ruling 43, owner "Ratify the convention now")

DOC-02 already ratified that Design invariants are numbered `INV-nn` entries carrying fact,
measurement and consequence, and that they are what COM-01's tags cite (rulings 19, 20 and the
2026-09-21 amendment). Three gaps remained, and the first COM-01 implementation piece would have
settled them by fact. The owner ruled them instead:

1. Numbering is **role-local and begins at `INV-01`**, restarting in every role.
2. Existing unnumbered Design invariants prose is **labelled in its existing order** before any new
   entry is appended, so a label never moves once a comment cites it.
3. A role that needs an invariant and has **no** Design invariants section **gains one**, in the
   position DOC-02 already fixes.

Raised by the Codex P2 REFUSE of WO-2 (`.audits/ansible-framework/2026-09-23-winbootstrap/exchange/
P2-WO2.md`, finding 1), which correctly observed that the framework carries zero `[INV-nn]`,
`[APF-nn]` or `[ADR-nnnn]` tags and no tracked `docs/` tree, so nothing in the tree constrains these
three choices. It overstated the gap as the whole convention; DOC-02 had already fixed the rest.
`docs/reference/platform-facts.md` and `APF-nn` remain unbuilt and out of scope for that piece: a
fact needing a shared home stays in place and is recorded as deferred debt.

### Amendment 2026-09-23 (rulings 34-42 and 44, owner interview, one rule at a time)
Owner process set here: *"research every single setting, interview me providing a recommendation 1 at a time via
the interview tool, both you and Codex need to agree recommendations before bringing them to me."* Every entry
below went to a Codex agreement pass before it reached the owner; that pass is
`.audits/guide-removal-2026-09-22/rules/exchange/CODEX-AGREEMENT.md`, which agreed 5 of 17 outright and returned
exact alternatives for 12, all accepted. Rulings 36-42 close guide rules spec v2 did not cover, clearing them for
WO-GUIDE-01 to delete the three repo-local style guides.

1. **Ruling 34** — the owner's idempotence ruling, narrowed: remove asserts that duplicate a module's own contract
   by re-checking what a PROCESS task in the same role just configured; keep END's independent product readback.
   NAME-01, GUARD-01 and GATE-01's deletion freeze amended together. The literal form ("the second converge proves
   it") was rejected in the agreement pass: a role that configures nothing converges clean twice, so GATE-01 proves
   *reported idempotence*, not correctness.
2. **Ruling 35** — IGNORE-01's proof stated in this document instead of citing `§7` of the guides being deleted,
   plus both entry regexes repaired. Executed across all six repositories.
3. **Rulings 36-38** — ACL-01 (exact ACL verification, `review`), ART-01 (execution-site artifact digest),
   MUT-01 (pre-mutation storage safety, storage-scoped by owner ruling).
4. **Rulings 39, 39a, 39b** — WHEN-01d (a task must not rebind a name its enclosing block's `when:` reads; blocks
   only, since a dynamic include's condition is not re-evaluated per child), BLOCK-01's `always:` cleanup gating,
   CHK-01's postcondition placement.
5. **Rulings 40-42** — LOG-01 secret-audit completeness, VAR-01's caller-side loader interface, CONN-01 Windows
   connection-variable scope.
6. **Ruling 44** — GATE-01's judged host set: `expected - keys(stats)` terminal,
   `judged = (expected | keys(stats)) - excluded`, a `stats`-only host unexcludable and therefore always judged.
   Raised because P4 found the planner had decided it inside a work-order amendment while fixing a review finding,
   where rulings 31 and 32 had refined the same clause by owner decision. **Numbered 44, not 43: a concurrent
   session took 43 for DOC-02 above on the same day, and neither session saw the other's write.**

