---
id: "IGNORE-01"
title: "IGNORE-01"
sidebar_label: "IGNORE-01"
sidebar_position: 15
tier: "`auto*`"
checked_by: "a new `rolecheck/lint/rules/ignore_01.py`."
---

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

