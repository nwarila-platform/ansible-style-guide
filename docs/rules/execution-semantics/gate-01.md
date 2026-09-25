---
id: "GATE-01"
title: "GATE-01"
sidebar_label: "GATE-01"
sidebar_position: 2
tier: "`auto`"
checked_by: "the framework-owned gate script `ansible-framework`'s `scripts/gate-idempotence.py` (new), run from each repo's own `aws-deploy.yml` at the existing pin; conformance by the credent"
---

**GATE-01** `auto` — Every deploy converges the playbook **twice**. The second converge must
report, **per host, from JSON callback output — never from a grep over the text recap** —
`changed=0`, `unreachable=0`, `failed=0` and `ignored=0`. A third leg runs `--check --diff`
against the converged host and must satisfy **the same four-zero predicate over that leg's own
fresh JSON artifact in the same schema**, and no task result under `plays[].tasks[].hosts[]` may
carry `"changed": true`. Any counter non-zero on any host, an absent, stale or unparseable
artifact, or a missing expected host fails the deploy.

Concretely, measured in the pinned toolchain on 2026-09-21:

- **Callback and schema.** `ANSIBLE_STDOUT_CALLBACK=ansible.posix.json`, the `json` stdout
  callback of `ansible.posix` (1.6.2), declared in the deploy's `requirements.yml`. Its output is
  one JSON object with `plays`, `stats`, `custom_stats`, `global_custom_stats`; `stats` maps each
  host to `{ok, failures, unreachable, changed, skipped, rescued, ignored}`
  (`ansible/executor/stats.py:59-70`). The gated counters are `stats.<host>.changed`,
  `.unreachable`, `.failures` — spelled `failures`, not `failed` — and `.ignored`.
  `ansible.builtin.json` **does not exist** at ansible-core 2.21.4: `ansible-doc -t callback -l`
  lists six callbacks and no `json`. `--tree` is not an `ansible-playbook` flag.
- **Freshness marker.** Each leg writes its artifact under a name carrying the run's own job id —
  `converge-2-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}.json`,
  `check-diff-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}.json`. The gate recomputes that name from
  its own run and reads only that path; any other name fails the gate.
- **Expected hosts.** The composed inventory's own host list: the deduplicated union of every
  group's `hosts` array in the `ansible-inventory -i <composed inventory> --list` dump, which
  equals `ansible all -i <composed inventory> --list-hosts`. **Not the keys of
  `_meta.hostvars`**: that map omits any host with no resolved variables, so a gate built on it
  passed with a limited-out host never judged (SPIKE-GATE-01 F4, 2026-09-21). A host in the
  expected set and absent from `stats` fails. **An empty expected set fails the gate** (ruling
  32); a vacuous pass is not a pass.
- **The judged set (ruling 44, 2026-09-23).** Stated as sets, because the counter population was
  previously implied by prose and drifted in implementation. Let `expected` be the union above less the
  exclusions, and `stats` the artifact's own host map. Then `expected - keys(stats)` is a **terminal
  failure** (a host that was never judged), and the counters are evaluated over
  `judged = (expected | keys(stats)) - excluded`. **A host present only in `stats` cannot be excluded**,
  because exclusion evidence comes solely from the inventory dump; it is therefore always judged, and the
  gate fails closed. Measured consequence, accepted: a run-time `ansible.builtin.add_host` helper carrying
  `ansible_connection: local` fails a deploy that is operationally fine. Both P4 reviewers judged the trade
  correct — a callback `stats` entry carries no trustworthy connection classification, so permitting a
  run-time host to declare itself local would restore the defect this clause closes. Excluding such a host
  requires an independently verifiable mechanism whose evidence lives outside the artifact being judged;
  none is ratified, so none may be assumed.
  **Found by:** P4 on `bdcd23c`. A host created by `add_host` is absent from the inventory dump, so it was
  never in `expected` and never judged, while its `stats` entry reported `changed: 1` and the gate printed
  PASS — a third bypass distinct from SPIKE-GATE-01's refuted F4 and F5.
- **Controller exclusion (ruling 32).** Excluded from the expected set: the host named
  `localhost`, and any host whose `ansible_connection` is `local` in **inventory** host or group
  vars, as shown in that same dump. A play-level `connection: local` and the CLI `-c local` are
  invisible to the dump and resolve only at execution (SPIKE-GATE-01 F5), so **a gated play may
  not set `connection: local` at play level and may not be run with `-c local` except against the
  host named `localhost`**; the conformance workflow checks that statically. Never a `^localhost`
  grep over console text, which one `ANSIBLE_FORCE_COLOR` or TTY breaks.
- **aws-workspace-builder's lane.** awb cannot converge twice: the play seals the guest, then
  needs LAPS escrow from a DC the runner cannot route to. Its lane: the single converge must
  report `unreachable=0`, `failures=0`, `ignored=0` for every expected host (`changed` is not
  judged); then the same playbook runs `--check --diff` against a freshly launched instance of
  the AMI that converge produced, and that leg must satisfy the full four-zero predicate plus the
  no-`"changed": true` task condition. Failing either half fails the deploy. A different lane,
  not an exemption.
- **Capture, measured (SPIKE-GATE-01).** stdout and stderr go to separate files: `ansible.posix`
  1.6.2 prints a deprecation warning under core 2.21.4, so a `2>&1` artifact does not parse. The
  gate parses JSON and never byte-compares: under a PTY the output is CRLF. Runner temp paths
  stay short: a long `TMPDIR` breaks core 2.21.4's local RPC socket (AF_UNIX 108-byte limit, rc
  250 before the callback starts). Freshness by run id is identity, not age; it relies on GitHub
  run-id uniqueness and a trustworthy workspace.
- **Not yet proven, named:** Windows targets over SSH; real `GITHUB_RUN_ID` reuse semantics;
  aws-workspace-builder's AMI lane; the composed AWS inventory. The gate work order carries each
  as an open proof.

**Retired:** CHK-02 — replaced by this rule (ruling 4).
**Why:** ruling 4, the Molecule convention, Red Hat 4.1.8/4.1.9 and 12.6. CHK-02 was implemented
in **0 of 6 repos**, its text-recap precursor in 2 [§3.8]; that precursor passes broken runs
three measured ways — `ignored=` goes unread (pdq's last green run reported `ignored=1`), a
`--limit` run judges only the hosts that appeared, and one expected count cannot fit multiple
hosts. Never gate on `ok=`; it drifted 7→9 across core versions. A *reusable* workflow is
disqualified: all 12 runner trust policies pin `StringEquals` on their own `aws-deploy.yml`. **No
further deletion of independent readback is permitted in a repo until this gate exists there**:
`8c24330` deleted 936 fsha lines, ~793 of them end-state verification. **[Ruling 34, 2026-09-23]**
Ruling 34 removes duplicate-configuration asserts; it does not authorize removing them before this gate
runs in that repo. Where the gate does not yet run, they stay, and they are removed in the same piece
that adopts the gate — so no window exists in which neither the assert nor the gate is watching.
**Checked by:** the framework-owned gate script `ansible-framework`'s
`scripts/gate-idempotence.py` (new), run from each repo's own `aws-deploy.yml` at the existing
pin; conformance by the credential-free reusable workflow `ansible-framework`'s
`.github/workflows/conformance.yml` (new).

