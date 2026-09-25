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

## Scope

Every Ansible role folder — each immediate subdirectory of `applications/`, `host_roles/`,
`operating_systems/`, `utilities/` or `roles/`, whether its namespace directory sits under `ansible/`
or at the repository root. A rule naming narrower files keeps that scope (FACT-01: an application
role's task files).

**The framework loader (`tasks/main.yml`)**: exempt from every *authoring* rule here — adopted
byte-identical from upstream, never edited by a consumer. It is **no longer exempt from FMT-01 or
LEN-01** (ruling 20); every other exemption stands. It was the worst width offender, 44 lines over 97
in 460. Because formatting changes its digest, LOADER-01's digest is republished by migration item 6
*before* any consumer formats a copy.

## What changed in v2

The fleet measures 18–44% conformance; the checker natively names 8 of 40 rule ids; `rolecheck` is
wired into **zero of six** CI pipelines; and 81% of the 4,112 findings were geometry with zero
attributable defects while every destructive-risk rule was invisible. Four structural changes: the
input contract moves to `meta/argument_specs.yml` (SPEC-01); the proof gate becomes Molecule-shaped
(GATE-01); cosmetic rules become autofix-only; the Galaxy skeleton wins over STRUCT-01's bans.

---

## Configuration and structure

**GUIDE-01** `auto*` — **No consumer repository** — the six fleet repositories — tracks a style
document; a consumer's `docs/ansible-style-guide.md` does not exist. The single canonical copy is the
one distributed with the checker at `rolecheck/spec/ANSIBLE-STYLE-SPEC.md` (see FLOOR-01), named here
as the sole exception so the canonical copy is not self-forbidden. Findings that are not rules migrate
to provenance comments at the sites they govern, per COM-01.
**Why:** the deletion claim was false — tracked in 3 of 6 repos [audit §3.9].
**Checked by:** a tracked-path check in `rolecheck/structure.py` (new).

**FLOOR-01** `warn` — A role declares `min_ansible_version: '2.21'` in `meta/main.yml`, as the quoted
string, in every role in every repo. A missing or different value is a warning. The checker parses
this literal from the packaged `rolecheck/spec/ANSIBLE-STYLE-SPEC.md`, shipped inside the
`ansible-role-check` distribution and the ubi9 tool image, never from a constant of its own.
**Why:** ruling 23; `structure.py:17` pins 2.18, so **all 69 warnings name the wrong target** [§3.3].
**Checked by:** `rolecheck/structure.py` `FLOOR-01` (163edb4; gates after the packaged-spec reader).

**LOADER-01** `auto*` — Every role under `applications/` ships the framework loader as
`tasks/main.yml`, byte-identical, never edited. Check: sha256 equals the digest published in the
pinned framework's `meta/loader-digest.txt`, which the checker reads rather than pinning in code
(`62925c47…` today, superseded by migration item 6). A role under `operating_systems/` is out of
scope: its `tasks/main.yml` is OS-specific logic, not a merge-and-dispatch loader (owner ruling
2026-09-17). `host_roles/` and `utilities/` are governed by their own kind, not by this rule.
**Why:** byte-identical loaders stop 49 copies drifting; wazuh's fork costs 111 findings.
**Checked by:** `rolecheck/structure.py` `LOADER-01` (163edb4; digest-from-artifact new).

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

**SCAFFOLD-01** `auto` — A role folder contains all twelve scaffold directories: `defaults`, `files`,
`handlers`, `library`, `lookup_plugins`, `meta`, `module_utils`, `molecule`, `tasks`, `templates`,
`tests`, `vars`. **Each scaffold directory either contains exactly `.gitkeep`, or contains at least
one non-placeholder entry and no `.gitkeep`.** A zero-byte `main.yml`, `test.yml` or `converge.yml` is
not a non-placeholder entry; it is a finding, because a placeholder must never read as coverage.
**Why:** ruling 2; 85 banned-but-present framework directories against 256 consumer findings demanding
them, and **12 of 14 framework `tests/test.yml` are zero bytes** [§3.1, §5.3].
**Checked by:** `rolecheck/structure.py` `SCAFFOLD-01` (directories 163edb4; predicate new).

**SCAFFOLD-02** `auto`/`review` — `defaults/main.yml` defines the top-level `<role>_defaults` key the
loader reads, and each default carries a whole-line comment immediately above it.
**Why:** a wrong key fails silently; ruling 19's third limb.
**Checked by:** `rolecheck/structure.py` `SCAFFOLD-02` (key 163edb4; comment presence new); "why" is
`review`.

**SCAFFOLD-03** `auto` — `README.md`, `meta/main.yml`, `defaults/main.yml`, `tasks/main.yml` and
`meta/argument_specs.yml` exist in every role folder.
**Why:** ruling 2, extended by ruling 1.
**Checked by:** `rolecheck/structure.py` `SCAFFOLD-03` (four files 163edb4; the fifth new).

**VAR-01** `auto*` — Read merged configuration as `<role>_running`, in every file including handlers.
The include-scoped `config` alias is not used in application roles; `config.` must not appear.
**[Ruling 41, 2026-09-23]** The same interface from the caller's side: a role whose `defaults/main.yml`
defines `<role>_defaults` receives every per-target input through the bare `<role>:` mapping; only loader
scalars (`ENV`, `state`) are passed as parallel role parameters, and a role with no `<role>_defaults` is
outside this clause. Because `-e '{"<role>": {…}}'` **replaces** that mapping rather than merging with
it, an extra-var override restates every key the caller's mapping sets. The generated Inputs section
names these values as merged configuration reaching the role as `<role>_running`, and carries that
warning.
**Why (ruling 41):** from R13 of the deleted guides. Extra vars have highest precedence and mappings
replace rather than recursively merge: executed, `-e '{"loader_demo":{"required_value":"…"}}'` silently
deleted the caller's sibling `temp_dir`. A per-target key placed *beside* rather than inside the role
mapping bypasses the loader entirely. Measured: **88 of 88** caller sites already nest correctly, so the
structural half is a formalization; the real gap is documentation, at **5 of 50** role surfaces. The
deleted guides instructed consuming the merged result through `config`, which this rule bans — one of
the contradictions that made the guides unsafe to keep.
**Why:** 163 `config.` reads in the unaligned repo, 0 elsewhere.
**Checked by:** a new `rolecheck/lint/rules/var_01.py`.

---

## Task authoring

**NAME-01** `auto*`/`review` — Task names are `'STAGE | Title Case Imperative'`, single-quoted, one
space either side of the pipe. STAGE is closed to four tokens, with no subsystem qualifier: **BEGIN**
reads the machine and decides one action (reads only, no mutation); **PROCESS** performs the mutation;
**END** verifies against the product's own readback, not the value just written, **and does not
duplicate a module's own contract by re-checking what a PROCESS task in the same role just configured
[ruling 34, 2026-09-23]**; **VALIDATE** is the
contract asserts in `validate.yml`. Playbooks add `PLAY` and `INVENTORY`. A task inside an `always:`
takes the enclosing stage's token. Handlers are exempt: bare sentence case, no token. **Subsystem
navigation uses STRUCT-01's permitted `<state>_<family>.yml` file and its region index; it never
extends the stage token set or splits a state/family on length.**
**Why:** ruling 5, reconciled with the later ruling 12 where the two met: navigation (PKI×31, S3×19)
is the region index, not a length split. Stage semantics appear here because they are not lexically
checkable; `name[prefix]` stays unlisted, so production does not undo ruling 5.
**Checked by:** `rolecheck/lint/rules/name_01.py` (163edb4; handlers, which `name_01.py:64` skips, are
new); staging is `review`.

**KEY-01** `auto`/`auto*` — A plain task puts `name:` first and the fully-qualified module last, with
a blank line before the module; the order of keywords between them is free. In a **block wrapper**,
among the keys present the relative order is `name`, `vars`, `when`, `block`, `rescue`, `always`; only
`name` and `block` are mandatory. Module arguments are alphabetical.
**Why:** ruling 10; `block` sorts before `vars`, so **every conforming wrapper was a violation** [§3.6].
**Checked by:** `ansible-lint key-order` for name-first and `block`/`rescue`/`always`-last only;
module-last, the blank line, wrapper order and argument sorting are a new
`rolecheck/lint/rules/key_01.py`.

**ARG-01** `review` → `auto*` — State every module option whose documented default is non-null,
including when the value equals that default; the executed value must be readable in the task, not
inherited from collection docs a version bump can change. Omit every option whose documented default
is null unless it carries this task's intent. Never write `option: null` or `omit` to satisfy this
rule. An option may be omitted as inapplicable to the invoked mode only where the module and option
appear in the **generated applicability metadata** or in the owner-ratified override table. An option
is stated only in the task's module arguments or its `args:` keyword; `module_defaults` does not state
it. Options whose name begins `_` are outside this rule. In a mutually exclusive group with at least
one non-null default, stating any one member satisfies the group. An `ansible.builtin` option added
after the declared `min_ansible_version` is not required; a role declaring no floor gets no relief,
and collection options are always required.
**Why:** ruling 13; unmeasurable until the generated data exists [§7]. Blind spot, recorded not fixed:
a wrong `prefix: 'google-chrome-'` cloned into 34 roles reads as intent.
**Checked by:** `review` until the generated metadata and the override table exist; then a new
`rolecheck/lint/rules/arg_01.py`.

**ARG-02** `auto` — Invoke every module by fully-qualified collection name.
**Why:** kept as written, verbatim. The `library/` collision (§3.4) is **not** resolved by
exempting bare invocation: such a module cannot carry a collection name and so cannot conform.
**There is no exception route (ruling 31, 2026-09-21): a role ships no role-local module;
`library/`, `lookup_plugins/` and `module_utils/` hold only `.gitkeep`; a module the fleet needs
is published in a namespaced collection or removed with its caller.** `s3_artifact_delivery`'s
`library/s3_artifact.py` (owner action 2) therefore has two outcomes, promotion or deletion.
SCAFFOLD-01 requires the directory, not permission to invoke code from it.
**Checked by:** `ansible-lint fqcn` (production only; 163edb4).

---

## Conditionals and validation

**WHEN-01a** `auto*` — A conditional comparing a loader-level scalar input to a literal uses the full
chain: `(state | default('present') | string | lower | trim) == 'present'`.
**Why:** conforms everywhere; kept as written. **Checked by:** a new
`rolecheck/lint/rules/when_01.py`.

**WHEN-01b** `auto*` — A conditional testing merged config for emptiness supplies a type-appropriate
default: `| default([], true)` for lists, `| default({}, true)` for maps. The checker reads the
declared type from `meta/argument_specs.yml` (SPEC-01).
**Why:** no violation found; kept as written. **Checked by:** `rolecheck/lint/rules/when_01.py` (new).

**WHEN-01c** `auto*` — A conditional comparing merged-config strings normalizes **both** sides with
the same filter chain — the same ordered filters with the same arguments. A one-sided comparison
against an undefaulted value fails silently rather than loudly.
**Why:** 3 live violations in windows-wsus. **Checked by:** `rolecheck/lint/rules/when_01.py` (new).

**WHEN-01d** `auto*` — A task must not bind, through its own `vars:`, any name referenced by a `when:`
it inherits from an enclosing **block**. Where later data must be re-tested, use a distinct name.
Identifier extraction is by Jinja parse, not by regex.
**Why:** ruling 39 (2026-09-23), from R04 of the deleted guides. A block's condition is re-evaluated in
each child task's own variable context, and task `vars:` outrank block `vars:`, so a child that rebinds
a name the gate reads silently skips itself inside a block that was entered. Executed: the constructed
case gave `ok=2 changed=0 failed=1 skipped=1`, exit 2, while `ansible-lint -p` passed the same file with
0 failures. Measured **24 of 24** gated blocks conform, so the cost is zero; the value is foreclosing a
silent-skip class whose only symptoms are a green run that did nothing. Scope is **blocks only**: a
`when:` on `include_tasks` gates the include statement and is not re-evaluated per child, so extending
this to dynamic includes would ban safe rebinding. `import_tasks`, whose condition *is* copied to each
child, carries the same hazard and is a named follow-up — its population has not been measured, and this
fleet does not write rules over unmeasured surfaces.
**Checked by:** `rolecheck/lint/rules/when_01.py` (new) — parse each block `when:`, collect referenced
roots, walk descendants, reject any intersection with task `vars:` keys.

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

**GUARD-02** `auto*`/`review` — Every assert carries `quiet: true` and a `fail_msg` stating the
refusal, the observed value and the remedy. The observed value may be omitted only where the failing
`that:` clause already prints it.
**Why:** ruling 22; only **188 of 367 asserts show an observed value** [§3.11].
**Checked by:** a new `rolecheck/lint/rules/guard_02.py` for `quiet`, `fail_msg` presence and the
no-Jinja heuristic; refusal and remedy are `review`.

---

## Execution semantics

**CHK-01** `auto*`/`review` — Check mode is supported. A read carries `check_mode: false` so it
executes under `--check`. A unit that genuinely cannot run under `--check` carries `when: not
ansible_check_mode` with a comment stating why. A module whose `ansible-doc` `check_mode.support` is
not `full` carries an explicit `check_mode:` or `changed_when:`. **Fresh-host `--check` is out of
scope (decision 44); the converged-host leg is GATE-01's.**
**[Ruling 39b, 2026-09-23]** A conditionally included unit's postconditions are evaluated **after and
outside** its `include_tasks`, so verification still runs on the converged path where the include is
skipped. Placement is `review`. Executed: with the postcondition inside the included file, a false include
gate skipped both the read and the assertion and the play wrongly **succeeded** — `ok=1 changed=0
failed=0 skipped=1`, exit 0, ansible-lint clean. A dynamic include's condition applies to the include
statement, not to the tasks inside it, which is exactly why the verifier must sit outside. Measured 4 of 4
current sites already place it outside; `s3_artifact_delivery`'s `fetch.yml:128-153` is the exemplar.
**Why:** ruling 15, Red Hat 4.1.8; **0 of 6 repos run `--check`**, and wazuh's unguarded probe makes
`validate.yml:55` error instead of validate [§7].
**Checked by:** a new `rolecheck/lint/rules/chk_01.py` for the `check_mode.support` pairing over the
generated metadata and for the presence of the `when: not ansible_check_mode` comment; whether a task
is a read or a mutation, and justification quality, are `review`; GATE-01 executes the leg.

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

**ERR-01** `auto*`/`review` — No `ignore_errors` and no `failed_when: false` on a mutating task, with
two carve-outs. `ignore_errors: true` is permitted only where the task registers its result **and the
immediately following task is an `ansible.builtin.assert` or `ansible.builtin.fail` whose `that:` or
`when:` reads that register** — the named refusal. `failed_when: false` is permitted on a read-only
probe whose tool documents nonzero rc as a state signal, with that rc contract stated in a whole-line
`# rc-contract: <source>` comment, and on best-effort cleanup inside a `rescue:` preceding a
deliberate `fail`. `failed_when` is otherwise a postcondition folded into the task producing the data.
**Why:** ruling 8; `bootstrap.yml:148-157` suppresses a failed registry mutation *and* always reports
changed.
**Checked by:** `ansible-lint ignore-errors` for the bare form (163edb4); adjacency and the
`# rc-contract:` marker are a new `rolecheck/lint/rules/err_01.py`; the read-only-versus-mutating
classification and the truth of both carve-outs are `review`.

**WAIT-01** `auto*`/`review` — Bound every wait the module allows. A retry loop carries `retries`,
`delay` and `until` together and a whole-line `# measured: <YYYY-MM-DD|commit>` comment citing the
race or flake that justifies it. Where a module exposes no timeout (`win_service` start/restart), the
role's contract states that it depends on the caller's job budget.
**Retired:** "an END proof reads once" — the `win_reboot`-returns-at-logon race is measured and real,
so a bounded retry with a cited race is permitted.
**Why:** 0 of 3 fsha retry loops carry the required comment.
**Checked by:** a new `rolecheck/lint/rules/wait_01.py` over the generated timeout metadata; the cited
race is `review`.

**LOG-01** `auto*`/`review` — `no_log: true` is hoisted to the block holding the secret, not repeated
per task, and appears nowhere else. A `rescue:` may project only named fields of a `no_log` result
(`msg`, `rc`) — never `stdout`, `stderr` or the whole object. **For a register created inside a
`no_log` block, LOG-01 is narrower than RESCUE-01: only `.msg` and `.rc` may be projected.** A
play-level secret lookup is gated on the states that need it. An assert never interpolates `stdout` or
`stderr`. A destructive task whose `no_log` is forced by a credential is followed by a task with no
secret input that publishes the change set by name.
**[Ruling 40, 2026-09-23]** A secret review starts from the **complete accepted-input set, including
every alias the module documents**, and follows each secret through task arguments, registered results,
and any persistence or projection of a whole result object. A coverage claim names the surfaces actually
inspected. An unclassified input or alias, or persistence of an unclassified whole result, is a finding.
A `no_log: true` declared in `meta/argument_specs.yml` is **documentation only** — measured on
ansible-core 2.21.4, it does not mask the value in any later task — so it never satisfies this rule.
**Why (ruling 40):** from R06 of the deleted guides. LOG-01 said what to do once a secret's location is
known; nothing said how far you must have looked before claiming none leaks. Executed: a module accepting
canonical `payload` plus the documented alias `api_token`, invoked by the alias, printed the secret
verbatim through the callback. ansible-lint's only secret rule (`no-log-password`) is opt-in and
experimental, so "ansible-lint is clean" is precisely the false green this clause forbids. Review surface
measured at **581** non-loader register sites across 69 role folders — a denominator to classify, not a
leak count.
**Why:** ruling 18; each clause is a measured leak path (fsha rescue, wsus clean-state lookup,
`python3_pip` `success_msg`).
**Checked by:** a new `rolecheck/lint/rules/log_01.py` for the AST clauses; placement, secrecy and
change-set publication are `review`.

**RESCUE-01** `auto*` — A `rescue:` reads `ansible_failed_result.msg` and `.rc`, and named fields of
its own registers, only. It never projects the whole result object into a `fail_msg`, a `debug`, or a
variable. **Only `ansible_failed_result.msg` requires a default** —
`{{ ansible_failed_result.msg | default('<role> operation failed', true) }}` — being the one field
absent on an unreachable or parse failure; `.rc` and named register fields are projected without one,
since a `fail_msg` renders only in an already-failed context. LOG-01 narrows this rule for any
register created under `no_log`.
**Why:** ruling 21; the dormancy premise was false — **12 `rescue:` blocks in role folders, 14 with
playbooks**.
**Checked by:** a new `rolecheck/lint/rules/rescue_01.py` (AST walk over `rescue:` bodies).

---

## Formatting

All four rules here are **`autofix`**: the formatter rewrites them, CI checks the tree is unchanged
afterwards, and they are never counted as findings (ruling 3).

**FMT-01** `autofix` — Every banner rule line in a role folder in scope is exactly **97 columns**,
including the file-header box, the `# --- [ Description ] --- #` rule, region markers and sibling
separators. `#region` carries six dashes before the label and `#endregion` three, so the `[` aligns
between an open/close pair; the labels are byte-identical. Out of scope: PowerShell regions
(self-consistent 96) and the framework's `.editorconfig`/`.yamllint.yml` (legacy 79).
**Why:** 1,518 composed findings, zero attributable defects.
**Checked by:** the formatter; CI asserts a clean diff. `rolecheck/lint/rules/fmt_01.py` stops
emitting findings that day.

**LEN-01** `warn` (`autofix`) — No line in any tracked file in a role folder in scope exceeds **97
columns** — YAML, Jinja, PowerShell and **Markdown alike**. The formatter reflows README prose to this
width. The loader is included. Exceeded width is a warning, never a build failure.
**Why:** rulings 20 and 3; a full sweep gave **239 violations, 235 of them README prose**, where
reports said 2 and 4 [§3.7].
**Checked by:** the formatter (reflow); the residual hard-width result is a warning from
`rolecheck/report.py` once `yaml[line-length]` joins the `skip_list` of
`rolecheck/lint/ansible-lint.yml` — under ansible-lint a yamllint result is fatal whatever its level
in `rolecheck/lint/yamllint.yml` (97/error today).

**COM-01** `auto*`/`review` — A comment states a constraint, a failure mode, or a rejected
alternative — never what the next line does, never history, never review provenance. History and
review provenance live in commits and PRs only. **A comment block is at most 3 lines** (ruling
26): A comment block is one to three consecutive physical lines whose first non-whitespace
character is `#`, immediately preceding, with no intervening line, a task's first key or a
default/variable mapping key at the same indentation. The FMT-01 file-header box is not a comment
block. Each task has at most one comment block. **A whole-line comment run that is neither a
comment block nor the file-header description is a finding, whatever its length** (ruling 30):
comments live above a task, above a default or variable, or in the file header. Banner lines (the
FMT-01 box, Description and separator rules and the FMT-02 region markers) and whole-line lint
directives are not comment runs. **Ruling 27:** A file-header description comprises the nonblank
whole-line comments after the FMT-01 Description rule and before that box's closing banner rule;
the path line, rule lines, and blank `#` padding do not count, and at most 10 lines count.
**Cite, don't narrate** (ruling 28): knowledge that needs more than three lines lives in the
documentation, and the comment cites it with a bracketed tag closing its last line — `[INV-nn]`
for an entry in the role README's Design invariants, `[APF-nn]` for an entry in
`docs/reference/platform-facts.md`, `[ADR-nnnn]` for a decision record under
`docs/decision-records/`. A tag resolves only if its exact label occurs once in the current
role's README or once in tracked `docs/reference/platform-facts.md`, or if exactly one tracked
`docs/decision-records/repo/nnnn-*.md` has an H1 beginning `# ADR-nnnn:`. A claim about
**platform behaviour** — vendor, OS, module or transport — is either one line naming how it was
measured — a date written `YYYY-MM-DD` or a commit of 7 to 40 lowercase hexadecimal characters —
or a tag whose entry carries the measurement. Whether a comment is a platform claim is a `review`
judgment (ruling 29); the checker validates the grammar of any date or commit token present and
the form and resolution of any tag present. Trailing comments and block-marker comments (`# Begin
The '<Stage>' Block`, any case) are findings. The only permitted trailing comments are the lint
directives the pinned linters recognize: `# noqa: <rule-id>` (ansible-lint), and `# yamllint
disable-line rule:<id>`, `# yamllint disable rule:<id>` and `# yamllint enable` (yamllint). **A
change that removes a fact from a comment moves it to its documented home in the same commit.**
**Why:** rulings 6 and 26-28. Measured 2026-09-21 on origin/main: comments are about 40% of YAML
lines in the framework, windows-wsus and pdq; 1,596 of 4,205 prose blocks exceed 3 lines, 346
exceed 6, the longest is 37, and 62% of comment prose sits in blocks over 3 lines;
windows-fileserver-ha is the in-fleet model (22%, median 2, maximum 5). Both reviewer lenses
praised the long blocks, so length is a finding rather than a review judgment. **306 block
markers fleet-wide**, 261 case-sensitive — two reconciliations reporting 9 and 13 for one tree is
itself the failure mode, so matching is case-insensitive [§3.10].
**Checked by:** a new `rolecheck/lint/rules/com_01.py` for markers, non-directive trailing
comments, block adjacency, block length (3), header description length (10), the grammar of any
date or commit token present, tag form, and tag resolution (an `INV-nn` anchor in the role
README, a `APF-nn` anchor in `docs/reference/platform-facts.md`, an ADR file numbered `nnnn`); an
`INV`/`APF` entry no code cites is a `warn`. Unanchored comment runs are findings from the same
rule file. Platform-claim detection, content class and fact preservation are `review`.

**QUOTE-01** `auto*` — Literal strings take single quotes; values containing Jinja take double quotes;
booleans, integers, `null` and conditionals are bare. A value containing both a backslash path and
Jinja stays single-quoted, because double quotes would make `\S` and `\A` illegal escapes. Task
`name:` and `register:` are always single-quoted.
**Why:** no defect produced; kept as written.
**Checked by:** a new `rolecheck/lint/rules/quote_01.py`.

**BOOL-01** `auto` — `true` and `false` only; never `yes`, `no`, `on`, `off`, `True` or `False`.
Enforced at error level with `check-keys: true` (which is what requires `'on':` in workflow files).
**Why:** 0 violations fleet-wide.
**Checked by:** `yamllint truthy` via `rolecheck/lint/yamllint.yml` (163edb4).

**NULL-01** `auto*`/`review` — Spelled `null`; never `~` or `Null`. **Never written as a substitute
for omitting an option** — ARG-01 omits null-defaulted options instead. Legitimate in `defaults` to
declare "no value — the product's own default applies", with a comment naming what the null means, and
as a module argument **only where the generated toolchain metadata records null as an explicit clear**
(e.g. `microsoft.ad.user`'s `adminCount: null`).
**Why:** the blanket ban was wrong against a documented clear.
**Checked by:** a new `rolecheck/lint/rules/null_01.py` over the generated metadata; the `defaults`
comment is `review`.

**SCALAR-01** `auto*`/`review` — Folded-strip `>-` is the default for prose, `fail_msg` values and
long expressions. Literal `|` is permitted for **any newline-sensitive payload** — file content,
heredocs, a `win_shell`/`win_command` escape hatch — where newline preservation is semantically
required.
**Why:** ruling 16; the old wording failed 9 legitimate wazuh sites. V1's tail "anything larger is a
first-class script under PS-01" is deleted — undefined for a Linux heredoc, it would readmit the rule
ruling 16 deferred.
**Checked by:** a new `rolecheck/lint/rules/scalar_01.py` for the spelling; newline-sensitivity is
`review`.

**FLOW-01** `auto` — Short scalar lists are written inline with exactly one space inside each bracket,
**"short" meaning the complete line is at most 97 columns**. A **sequence item** is always a block
mapping; `- { a: 1, b: 2 }` is a finding regardless of length. A **control mapping** — the set is
closed to `loop_control:`; additions require ratification — is folded onto one line as
`{ key: value }` when the folded form fits LEN-01, and written block style only when it does not.
**Why:** 44 violations in the unaligned repo; "short" and "its kin" are now exact.
**Checked by:** `yamllint braces`/`brackets` for spacing (163edb4); sequence items and control
mappings are a new `rolecheck/lint/rules/flow_01.py`.

**LOOP-01** `auto*` — Iterate with `loop:`; `with_*` never appears. Every loop carries a
`loop_control.label`. `loop_control` is folded per FLOW-01. **A named dunder `loop_var` is required on
exactly two triggers: the loop expression references a registered result's `.results`, or the task
lies inside another loop's body.** The dunder variable is declared on the *inner* loop — the one whose
body would otherwise read `item.item`. A single-level loop over a plain list keeps `item`.
**Why:** ruling 11, the counterfactual replaced by two objective triggers. `345c3cf` (#111) removed
`loop_var: r` and gave `item.item.unique_id` **15 times in one file**.
**Checked by:** `rolecheck/lint/rules/loop_01.py` (163edb4); the two triggers are new — today's rule
produces the false positive that caused #111.

**REG-01** `auto*`/`review` — A `register:` target is `'__<role>_<noun>__'`, single-quoted. Never read
`.changed` from a result — change is expressed through `notify:` and the run's recap. Never read `.rc`
except inside an ERR-01 probe carrying the `# rc-contract: <source>` marker. A registered field read
in a `when:` carries a default; the same field in a `fail_msg` does not, because a `fail_msg` only
renders in an already-failed context.
**Why:** 59 unnamespaced registers in one play's namespace.
**Checked by:** `rolecheck/lint/rules/reg_01.py` for the name shape (163edb4); the reads, marker and
default are new; the contract's truth is `review`.

**VARNAME-01** `auto*` — A value that persists as a host fact is named `__<role>_<noun>__`; a task- or
block-scoped `vars:` member is bare `__<noun>__`. The prefix exists because a persisting fact can
collide across roles in one play and a scoped var cannot.
**Why:** 22 role-prefixed block vars in fsha — the rule discriminates.
**Checked by:** `ansible-lint var-naming` (163edb4); the scoped/persisting split is a new
`rolecheck/lint/rules/varname_01.py`.

**FACT-01** `auto`/`review` — `set_fact` does not appear in an **application role's task files**, with
two named exemptions: **(a)** a handler-visible progress latch that no `register` expresses, and
**(b)** a value that must persist across plays. Each exempt site carries one of exactly two whole-line
annotations immediately above it: `# FACT-01 exemption (a): handler-visible progress latch` or
`# FACT-01 exemption (b): persists across plays`. Derived values otherwise live in block `vars:` —
lazily evaluated, block-scoped — or come from `register`; a fold is written with `zip` in block
`vars:`. The loader's use is out of scope by LOADER-01, not by exception. Never `set_fact` the name
`ansible_facts`.
**Why:** ruling 7, Red Hat 7.5; the `zip` counter-example ran on 2.21.4 and the register hatch is
proven (#104). Scope stays at application-role task files — the ruling's own scope — so
`fact_01.py:35` scoping to `applications/` is the rule, not a gap.
**Checked by:** `rolecheck/lint/rules/fact_01.py` (presence 163edb4; the two annotation tokens new);
the exemption's truth is `review`.

**DOC-01** `autofix` — Ansible files carry no `---` document-start marker; the header box marks the
start of the file.
**Why:** ruling 3; 313 findings, zero gain, and **every repo already disables `document-start`** [§4].
**Checked by:** the formatter; CI asserts a clean diff. `rolecheck/lint/yamllint.yml`'s
`document-start` stops being a finding that day.

**STRUCT-01** `auto*`/`review` — `tasks/` is flat and holds only `main.yml`, `validate.yml` and
`<state>_<family>.yml` — **one file per state and family, never split on length**; no subdirectories.
The allowed `<state>` values are the `choices` the role's `meta/argument_specs.yml` declares for its
state input, and the allowed `<family>` values are the stems of the `vars/<family>.yml` files present;
that pair is the dispatch matrix, and a task file outside it is a finding. Navigation inside a large
file is the region index and the stage tokens. The OS overlay is `vars/<family>.yml`, never
`vars/main.yml`, and exists even when it has nothing to say — as `{}` with a header stating that an
empty map is the honest declaration rather than a copy of defaults that would drift. The role's
directory set is SCAFFOLD-01's; this rule bans no directory. A directory tracking exported product XML
carries `.gitattributes` with `*.xml -text`.
**Why:** rulings 12 and 2. Owner, verbatim: "Single file, no split based on length" — overriding the
proposed pdq and wazuh thresholds and, as the later ruling, governing where ruling 5 met it (NAME-01).
**Checked by:** a new `rolecheck/lint/rules/struct_01.py` for flatness, dispatch-matrix filenames,
`vars/main.yml` and `.gitattributes`; the empty overlay is `review`.

**IGNORE-01** `auto*` — The allowlist admits exactly two wildcard shapes: the **role-name segment** of
an otherwise fully-explicit path, and a **content-type glob inside a payload directory one level under
`files/`**. Exactly two entry forms are accepted, as regexes over the entry text:
`^!(/ansible)?/(applications|host_roles|operating_systems|utilities)/(\*|[a-z][a-z0-9_]*)/[^*?\[]*$` and
`^!(/ansible)?/(applications|host_roles|operating_systems|utilities)/(\*|[a-z][a-z0-9_]*)/files/[^*/?\[]+/\*\.[A-Za-z0-9]+$`.
Every other entry is spelled out.

**[Ruling 35, 2026-09-23]** Two repairs, in one edit. **(a) The proof is now stated here** and no longer
cites a document outside this spec: on every allowlist change, construct the complete allowed-file set
from explicit file entries and expansions of the two permitted wildcard forms, and require equality with
`git ls-files` — every tracked file is allowed, every **file** allowance resolves to at least one tracked
file, and every wildcard resolves. Every re-included **directory-spine** entry resolves to at least one
directory, and a unique nonexistent child sentinel under each matched directory is classified ignored by
`git check-ignore --no-index`. File allowances and directory spines are separate predicates: "resolves to
a tracked file" is false for a spine. **(b) Both regexes were defective** and are corrected above, in four
respects, each verified by executing the forms against all six repositories' allowlists: they anchored
only at a repository-root `ansible/` namespace, so the framework's own root-level `applications/` could
never satisfy them; the role-name segment admitted only `*`, so a literal role name was illegal; the
explicit portions excluded only `*`, admitting `?` and bracket expressions, which gitignore also treats
as globs, so a second wildcard could hide in supposedly explicit text; and the first form required a
non-empty suffix, rejecting the necessary role-directory spine `!/ansible/applications/*/`
(aws-workspace-builder `.gitignore:23`), without which git cannot descend to the file allowances below
it. The literal-role branch is `[a-z][a-z0-9_]*`, the grammar the consumer composers already enforce
(for example `aws-workspace-builder/scripts/compose-and-run.sh:161`); all 69 role names across the six
repositories satisfy it, so it excludes no current role. Promote to `auto` only when the repository preflight exists and blocks.
**Why:** cheap; "designated payload directory" is now exact. Ruling 35: the guides that carried §7 are
being deleted, so a rule citing §7 would become incoherent; and the proof executed across six repos found
framework-main failing with 17 illegal globs, 287 tracked files outside the legal expanded set and a
leaky `!/.github/**` spine — while `make allowlist-check` reported OK, a false green on the repository
every other repository composes. aws-workspace-builder `6668944f55ebc` is the caught failure: 41
`absent_windows.yml` and 2 `clean_windows.yml` were ignored while the playbooks referencing them were
committed, so a fresh clone could not dispatch those states. **Rerun the 4/6 baseline after this
amendment**: the literal-role repair makes pdq's concrete-role payload glob legal.
**Checked by:** a new `rolecheck/lint/rules/ignore_01.py`.

**PS-01** `auto*`/`review` — **Every guest PowerShell block, however small, is never inlined.** A
guest PowerShell block is any of: the `script:` value of `ansible.windows.win_powershell`; the
free-form or `_raw_params` scalar of `ansible.windows.win_shell`; the same scalar of
`ansible.windows.win_command` or `community.windows.win_psexec` where the invoked executable is
`powershell.exe` or `pwsh`; and an `ansible.builtin.raw` scalar on a Windows host. It lives at
`scripts/<Name>.ps1` beside a mandatory `<Name>.pester.ps1` spec, reaches the role as
`files/<Name>.ps1.stub`, and the materialized artifact is never allowlisted. A script publishes its
result **before** raising (`$Ansible.Result` then `$Ansible.Failed`), reports change only through
`$Ansible.Changed` — set `$False` before the read so a throw cannot inherit the transport's default —
and judges native exit codes through one function-scoped wrapper taking an explicit success code.
**Why:** ruling 9 — no size threshold and no "with logic" qualifier; every block is a script (awb ~84
extractions, framework 13). `Set-SmbServerHardening.ps1` is the only one of 9 fsha scripts without the
`$False` guard, and the Pester case named for it passes without exercising a throw path.
**Deferred:** the equivalent rule for **Linux** shell payloads (ruling 16: "Linux we will handle in
the future"); only SCALAR-01's payload amendment lands now.
**Checked by:** a new `rolecheck/lint/rules/ps_01.py` for the enumerated forms and stub/sibling
presence; the pinned Pester workflow
`NWarila/powershell-template/.github/workflows/pester-matrix.yaml@758b3313d34269f10dcf1a1b07837c0b887bdc87`,
called from each repo's `.github/workflows/powershell.yml`, for the script contract; quality is
`review`.

**MUT-01** `auto*`/`review` — Before the first destructive mutation of a declared **storage** resource,
read observed state and refuse a foreign or occupied target; only blank, already-ours, or a positively
recognized resumable state proceeds. Ownership is recognized by a durable convention the role itself
writes — a filesystem label or equivalent durable storage marker — never by size, index or enumeration
order. Refusal carries an actionable `fail_msg`. `windows_disk_manager` is a named exception for its
`set_fact` accumulation and its classifier's `| first`; its foreign-layout assert still precedes
initialization, partitioning and formatting.
**Why:** ruling 38 (2026-09-23), from R08 of the deleted guides. A valid identifier can still point at an
occupied foreign disk; idempotent provisioning modules then initialize, partition or format the wrong
resource and report success. Executed: starting from a disk holding `FOREIGN OWNER DATA`, an unguarded
mutation exited green with `changed=1` and replaced it, and ansible-lint saw nothing. Framework commit
`5f5cae8` records the same ownership lesson in `windows_disk_manager`. Measured: **2 of 2** authored
destructive storage provisioners already conform, so this ratifies existing practice rather than
demanding migration. **Scope is storage by owner ruling (2026-09-22):** the broader reading over every
destructive mutation — roughly 228 sites, including 193 `state: absent` in aws-workspace-builder, of
which 3 carry an ownership marker — is a separately measured amendment needing a resource-neutral state
model, because blank / occupied / resumable are storage words that do not transfer as written.
**Checked by:** a new rule identifying known destructive storage modules and requiring a dominating
read/classify/assert path before them; recognizing whether a marker is durable, and whether a state is
genuinely resumable, is `review`.

**ART-01** `auto*`/`review` — A delivery chain that downloads and stages executable content must verify
its pinned digest against the exact execution-site path after the last transfer and before that path is
executed — not only at the download site. A `win_package` invoked with a local `path:` carries both
`checksum:` and `checksum_algorithm:` naming sha256 or stronger; an artifact executed by any other
module verifies the digest in the executing script or in an immediately preceding read of the staged
file, and a run whose staged digest does not match the pin fails.
**Why:** ruling 37 (2026-09-23), from R03 of the deleted guides. Hashing a controller download does not
authenticate the bytes later copied to and executed on the guest, and convergence cannot observe the
difference: a malicious but installable package leaves every GATE-01 counter green. Ansible documents
`ansible.windows.win_package.checksum` as calculating the digest *before executing* a local or
downloaded package, so the rule's timing and location are upstream-supported. Measured: **40 of 41**
staged-installer chains already verify at the execution site; the exception is `wazuh_agent` on Windows,
which verifies the controller file (`tasks/present_windows.yml:120-131`), copies it to the target, then
executes that path with no `checksum` (`:137-154`) — found independently by the 2026-09-21 s3ad audit
(`P2-S3AD.md:275`).
**Checked by:** a new dataflow rule — staging copy destination, then the same path digest-checked before
an execution sink; the `win_package` option pair is the reliable `auto*` portion. Dynamic paths, shell
execution, archive expansion and verification delegated into another role are `review`.

**CONN-01** `auto*` — Windows connection variables (`ansible_connection`, `ansible_shell_type`,
`ansible_user`, `ansible_port`, `ansible_winrm_*`) are declared on Windows hosts or the Windows group,
**never on `all`**. If a repository declares `localhost` in inventory, it declares `ansible_connection:
local`, `ansible_shell_type: sh` and `ansible_python_interpreter: "{{ ansible_playbook_python }}"`
together, because an inventory-declared localhost loses the implicit host's automatic interpreter;
otherwise implicit localhost is correct and sufficient. Where a play's own `vars:` carry Windows
connection identity, every task in that play that delegates to the controller restores
`ansible_connection: local` and `ansible_shell_type: sh` in its own `vars:`. A task-level connection
override is otherwise reserved for a delegate that genuinely differs from its inventory declaration.
**Why:** ruling 42 (2026-09-23), from R10 of the deleted guides. Delegated tasks template connection and
interpreter options in the *delegate's* context, so Windows variables on `all` reach the controller:
executed, a delegated command ran as `powershell … -EncodedCommand` on a Linux controller and the play
exited 4. Measured **5 of 5** consumer inventories are safely scoped today, with 133 delegated controller
tasks depending on it, and **0 of 5** follow the guide's prescribed remedy — which execution showed is
unnecessary: scoping to the Windows group with no explicit localhost returns rc 0, because implicit
localhost supplies both `connection=local` and `ansible_playbook_python`. The remedy is therefore
**conditional, not mandatory**: it applies only once a repository declares localhost explicitly and
thereby loses those implicit properties. The third sentence ratifies aws-workspace-builder's existing
eight-site pattern.
**Checked by:** a new checker rejecting Windows-only connection variables under `all` and validating all
three fields where localhost is explicit; whether a task override names a genuinely different delegate
is `review`.

**ACL-01** `review` — Where configuration declares a complete ACL, verification canonicalizes and
compares the complete explicit ACE set, keyed by SID, rights, type, inheritance flags and propagation
flags, with the declared set by equality; every missing or undeclared explicit ACE fails. Inherited ACEs
are collected and reported separately and are not counted in that equality. Where the declared contract
protects inheritance, the readback also requires `AreAccessRulesProtected`; rejecting any observed
inherited ACE is an accepted equivalent to reporting it as drift. A total count alone and a containment
test are not proofs. Where a role owns only a named grant on a shared ACL, it states that boundary and
proves the complete explicit ACE set for that principal, leaving other principals outside its contract.
**Why:** ruling 36 (2026-09-23), from R12 of the deleted guides. Containment proves only that a wanted
ACE exists, so an undeclared explicit grant survives convergence forever while GATE-01 reports
`changed=0` — reachable now on aws-workspace-builder's OpenSSH administrators key, which says
`Grant Only` while applying additive `ansible.windows.win_acl` entries
(`openssh_server/tasks/present_windows.yml:315-342`), the file sshd's trust depends on. Total ACE counts
are separately unsound: Windows normalizes rights beyond the friendly declaration, so fsha's declared
`Modify` could never match once Windows added `Synchronize` (`e224476`). Measured: **0 of 5** reusable
ACL implementations conform to this text, across four incompatible idioms; even
`Set-ClusteredFileServer.ps1`, which requires `AreAccessRulesProtected` and rejects inherited ACEs,
still uses `$Rules.Count` and does not report inherited ACEs separately.
**Checked by:** `review`. **No `auto` proxy exists**: no machine-readable marker tells a checker whether
a role claims whole-ACL ownership, so "a bare `win_acl` under a whole-ACL claim is a finding" is not
decidable today. Promote to an `auto*` proxy only once such a marker is ratified. Pester behaviour tests
are the executable proof for each first-class ACL implementation.

**HAND-01** `auto*`/`review` — Handlers are addressed by topic, never by name: `listen:` takes a
single-quoted kebab-case topic prefixed with the role name, with a free suffix; `notify:` is a single
quoted scalar naming that topic. A stage that notifies flushes handlers at the end of the stage — so
`END` proofs read post-restart state — **and** in that stage's `always:`, because Ansible does not run
handlers after a play failure. **The stage container is the named block wrapper BLOCK-01 requires, not
the region FMT-02 delimits**: the first flush is the last child of that wrapper's `block:` list, and
the second flush is a child of that wrapper's `always:` list. FMT-02 regions are navigation only; they
never locate a flush. A handler guard reads a register, never a fact.
**Why:** ruling 17; `-required` forced unnatural topics, and register-not-fact keeps guards out of
FACT-01(a).
**Checked by:** a new `rolecheck/lint/rules/hand_01.py` for topic shape and the guard symbol table;
`ansible-lint no-handler` for the inverse (163edb4); flush placement is `review`.

**CHG-01** `auto*`/`review` — `changed_when: false` covers reads and scratch the same file deletes in
its `always:`, never a durable mutation. A `command`/`shell` read carries `changed_when: false`
**and** `check_mode: false` together. A task running a first-class script carries no `changed_when` —
`$Ansible.Changed` is the report. `changed_when: true` appears only on a mutation already gated by a
`when:` proving it is needed. **A task that changes on every converge violates GATE-01; no
expected-change budget exists. It must gain an independent readback/gate or be redesigned.**
**Why:** the normative clauses are v1's, kept as written. The final clause replaces v1's
expected-change budget, which ruling 4's `changed=0` gate makes impossible to honour — a necessary
consequence of ruling 4 despite the "as written" instruction (owner confirmation item 5).
**Checked by:** `ansible-lint no-changed-when` for the bare form (163edb4); the paired
`check_mode: false` on a `command`/`shell` read is a new `rolecheck/lint/rules/chg_01.py`; the
read-or-scratch versus durable-mutation classification, necessity and readback are `review`.

**BLOCK-01** `auto*`/`review` — Each stage is a block wrapper task: `name:`, optional `vars:`,
`block:`, in KEY-01's ratified relative order (`name`, `vars`, `when`, `block`, `rescue`, `always`
among the keys present). A privilege boundary may be a block with `become`/`no_log` hoisted and
children carrying none. `always:` is for cleanup and the guaranteed handler flush. Note the Ansible
caveat: an invalid task definition or an unreachable host triggers neither `rescue` nor `always`, so
an `always:` cleanup is not a guarantee against every failure.
**Ruling 25 (2026-09-21):** every stage that exists in a state file is a named block wrapper, even when it
holds one task; a stage with no tasks is omitted rather than written empty. A staged task standing outside
a block is a finding.
**[Ruling 39a, 2026-09-23]** An `always:` task that removes a path is gated on the register of the task
that staged it: a run that never reached staging never deletes the path. A cleanup whose path is computed
from configuration rather than from that register is a finding unless so gated. Executed: an unguarded
`always:` deletion of a fixed staging path removed a pre-existing directory the run never created
(`ok=3 changed=2 failed=1 skipped=1`, exit 2), with ansible-lint clean. Measured **38 of 38** fixed-path
cleanups already gate on the staging register — the rule is a ratchet, and an unchecked 38/38 with an
operator-supplied staging directory is one copy-paste from a destructive regression.
**Why:** ruling 10 fixes the key-order collision; the wrapper text is v1's; ruling 25 closes the single-task
question the audit left disputed (fsha's five single-task wrappers and wsus_client's one wrapper conform).
Adjacency is the rule's product: wsus decision 38 put actor and END proof side by side, where two reviewers
saw the proof normalising differently from its actor.
**Checked by:** a new `rolecheck/lint/rules/block_01.py` for wrapper key presence and order, for an
empty wrapper — a wrapper whose `block:` list, or whose `rescue:` or `always:` list where present,
holds no task, which is a finding under ruling 25 — and for a task whose name carries a stage token
but whose parent is not a block named with that token. ansible-lint
26.8.0 has no `max-block-depth` rule — `complexity[nesting]`, which replaced it at 26.2.0, is
`experimental` and absent from the `enable_list`, so depth is unenforced; purpose is `review`.

**META-01** `auto*`/`review` — `meta/main.yml` carries `galaxy_info`, `dependencies` and
`allow_duplicates` only; **any other top-level key is a finding**. It does not document inputs;
`meta/argument_specs.yml` is the input contract (SPEC-01) and the README's inputs table is generated
from it (DOC-02).
**Why:** ruling 19; clause (a) was wrong (10 of 11 violations are correct `allow_duplicates`), clause
(b) has **49 live violations** [§3.12].
**Checked by:** a `META-01` top-level key allowlist in `rolecheck/structure.py`, the complete
mechanical test; smuggled prose is `review` — no complete detector is claimed.

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

**FMT-02** `autofix` — A region label is `<Stage>: <Description>` where every word of the description
is capitalized, matching NAME-01. Stage is `Begin`, `Process`, `End` or `Always` in task files and
`Play` or `Roles` in playbooks. `Always` is a region-only token: tasks inside an `always:` keep their
enclosing stage's task token. Regions are required wherever a file delimits more than one unit, and
omitted where there is nothing to delimit.
**Why:** ruling 3; 236 findings of one shape, no defect. With no length split the region index must be
generated, not policed.
**Checked by:** the formatter; CI asserts a clean diff. `rolecheck/lint/rules/fmt_02.py` stops
emitting findings that day.

**CHK-02** — **Retired.** Replaced in full by GATE-01 (ruling 4). The vendored aggregate callback, the
per-result ledger, the per-task changed allowlist and the stale-ledger stamp are dropped; their
properties survive as GATE-01's four counters read per host from JSON callback output.

---

## Contradictions resolved

| # | Contradiction | Ruling | What now governs |
|---|---|---|---|
| 1 | STRUCT-01 bans directories `structure.py:18-31` requires | 2 | SCAFFOLD-01's twelve; STRUCT-01 bans none |
| 2 | GUARD-01 set-equality vs decision 61 | 1, 24 | SPEC-01 declares inputs; GUARD-01 keeps cross-field and safety checks; 61 superseded in place |
| 3 | FLOOR-01 2.21 vs checker 2.18 vs code 2.16–2.19 | 23 | `'2.21'`, parsed from the packaged spec |
| 4 | ARG-02 FQCN vs a role-local `library/` module | — | ARG-02 verbatim; the module goes or gets an owner exception |
| 5 | GUARD-01 set equality vs `vars/<family>.yml` | 1 | Retired; SPEC-01 declares |
| 6 | KEY-01 alphabetical order vs BLOCK-01 wrappers | 10 | Name first, module last, free between; wrappers order present keys |
| 7 | LEN-01 scope undefined; loader exempt | 20, 3 | 97 on every tracked file, loader included, warn tier |
| 8 | CHK-02 implemented nowhere; awb unreachable | 4 | GATE-01's counters from `ansible.posix.json`, check leg, awb lane |
| 9 | GUIDE-01 asserted a false deletion | settled | No *consumer* repo tracks one; the packaged copy is named |
| 10 | COM-01's marker clause regex-sensitive | 6 | One contiguous block per task; markers banned, matched case-insensitively |
| 11 | GUARD-02 clause 3 met 188/367 | 22 | Observed value unless `that:` prints it; refusal/remedy `review` |
| 12 | META-01 wrong for `allow_duplicates` | 19 | Three keys only; inputs in `argument_specs.yml` |
| 13 | NAME-01 file splitting vs STRUCT-01 one file | 12 over 5 | Navigation is the region index inside the permitted file |
| 14 | CHG-01's change budget vs `changed=0` | 4 | A permanently changed task violates GATE-01 |
| 15 | LOG-01 vs RESCUE-01 on register fields | 18, 21 | LOG-01 narrower under `no_log`: `.msg`, `.rc` |
| 16 | Loader lost every autofix exemption | 20 | Only FMT-01 and LEN-01; item 6 republishes the digest first |
| 17 | GUIDE-01 vs FLOOR-01's spec source | 23 | The packaged path is named and exempted |

---

## Enforcement

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

## ARG-01 tables

**Generated toolchain metadata** (ruling 13) — applicability, mutually-exclusive groups,
`check_mode.support`, timeout options and documented explicit-clear options are **generated** from the
pinned ansible-core and collections, regenerated on every bump, and shipped in the toolchain image at
`rolecheck/arg-tables/<core-version>/`. The generator requires `pwsh` for the Windows modules and is a
maintainer/CI tool. It is machine output: no entry is ratified and it is never hand-edited. CHK-01's
`check_mode.support` pairing, WAIT-01's timeout options and NULL-01's explicit-clear options read from
this same artifact. The artifact carries **module-level fields only — it defines no task-mode or
action field** — so whether a given task is a read or a mutation is `review` for CHK-01, ERR-01 and
CHG-01; `check_mode.support` describes the module, not the task's intent.

**Owner-ratified policy overrides** — a short, hand-authored table of exceptions the generated
metadata cannot express. Additions require ratification.

| Module | Option | May be omitted only where |
|---|---|---|
| `ansible.windows.win_regedit` | `delete_key` | `state` is stated as the literal `present` |

**ARG-01 does not gate until both artifacts exist**; until then it is `review`.

---

## Migration order

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

## Revision log

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
