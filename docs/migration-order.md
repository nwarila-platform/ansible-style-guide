---
id: "migration-order"
title: "Migration order"
sidebar_position: 11
---


Owner actions first; **each repo-scoped work piece is one PR per repo** through the standard cycle.

1. **OWNER** — ratify this specification; supersede director decision 61 in place with a dated
   bracketed amendment citing spec v2; CLAUDE.md stays byte-identical.
2. **OWNER** — rule on ARG-02 vs `s3_artifact_delivery`'s two bare `s3_artifact:` calls: promote the
   module into a collection, remove it, or grant an explicit named exception. Also rule on the role's
   disposition — merge the deletion, or mark all three planner documents "work order authored, not
   merged". It is 22 tracked files at `65dbfac` contributing **100 of 110** framework findings.
3. **DONE 2026-09-21** — BLOCK-01 ruled (ruling 25): every existing stage is a wrapper, even for one task; a
   stage with no tasks is omitted. No open owner action remains on wrappers.
4. **OWNER** — ratify `rolecheck/spec/ANSIBLE-STYLE-SPEC.md` as the canonical packaged location this
   specification is distributed from, so FLOOR-01 can parse it while GUIDE-01 stays true.
5. **OWNER** — confirm that ruling 4's `changed=0` gate displaces CHG-01's expected-change budget, and
   that ruling 12 governs ruling 5 where subsystem navigation met the one-file rule.
6. **WORK PIECE** — the formatter (FMT-01, FMT-02, DOC-01, LEN-01's reflow at 97 including Markdown).
   Format the **upstream loader first**, publish its new sha256 in `meta/loader-digest.txt`, and
   propagate byte-identical copies before any consumer formats its own. Then reconcile every repo's
   `.yamllint.yml` to **97/warn** with `document-start` disabled, add `yaml[line-length]` to
   rolecheck's `skip_list`, and stop `fmt_01.py`, `fmt_02.py` and `document-start` emitting findings.
7. **WORK PIECE** — `ansible-role-check`: parse FLOOR-01 from the packaged spec (replacing
   `TEMPLATE_FLOOR = "2.18"`), read LOADER-01's digest from the framework artifact, add SCAFFOLD-01's
   placeholder predicate and SCAFFOLD-03's argument-spec requirement, extend `name_01.py` to handlers,
   add LOOP-01's two triggers. `fact_01.py`'s scope stays at `applications/`.
8. **WORK PIECE** — the ARG-01 generator, its generated metadata and the owner-ratified override
   table. The artifact is module-level only: it supplies ARG-01 applicability and non-null defaults,
   `check_mode.support` for CHK-01's pairing, timeout options for WAIT-01 and explicit-clear options
   for NULL-01. Whether a given task is a read or a mutation (CHK-01, ERR-01, CHG-01) stays review.
9. **WORK PIECE** — the remaining rules under "new checker required", with fixtures and oracles, one
   domain per PR.
10. **WORK PIECE** — SPEC-01 rollout: author `meta/argument_specs.yml` per role declaring only
    entry-time inputs and carrying the comment naming `tasks/validate.yml` as the contract, build
    `rolecheck/render/inputs.py` and its byte-for-byte check, and strip input documentation from
    the 49 offending `meta/main.yml`. **Ruling 33: `validate.yml` is NOT reduced** — doing so on
    the assumption the argument spec absorbs per-field checks would delete the only validation
    that ever sees the merged `<role>_running`, which is precisely where the overlay merge can
    introduce a bad value.
11. **WORK PIECE** — fleet remediation, one PR per repo: the `345c3cf` loop variable; `wsus`'s dead
    `__port__`, unreconciled `fail_msg` and missing `tls.enabled` guard; `$Ansible.Changed = $False`
    and a throw-path Pester case in `Set-SmbServerHardening.ps1`; the three tracked style guides;
    PowerShell extraction; comment cleanup; FACT-01/ERR-01/WAIT-01/CHK-01 annotations; key and module
    order; handler topics and flushes; LOG-01 and RESCUE-01 projections; aws-workspace-builder's stuck
    `powershell.yml` and `feat/workspaces-release`'s 3,013 unaudited lines.
12. **WORK PIECE** — one mechanical FLOOR-01 PR per consumer, moving 53 roles to `'2.21'`.
13. **WORK PIECE** — land the shared quality workflow in all six repos in **report-only** mode, one PR
    per repo — the first time `rolecheck` runs in any CI. Promote a domain to blocking only after
    items 6–12 have implemented its checker and repaired the fleet for it.
14. **WORK PIECE** — build GATE-01: the gate script, the `ansible.posix` dependency, the per-host
    four-counter judgement, the `--check --diff` leg, the conformance workflow, and awb's lane.
    **Freeze further deletion of independent readback in any repo until the gate exists there.**

---

