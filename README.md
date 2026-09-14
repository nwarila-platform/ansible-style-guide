# ansible-role-check

Checks every Ansible role folder it is given against the platform's Ansible style specification and the role scaffold, one
role at a time, and reports per role. It is the checker that will ship in a ubi9 tool image; until then it runs from this
checkout on Python 3.12.

## Run it

```bash
make install                                   # pinned toolchain (hash-locked) and the six pinned collections
python3 -m rolecheck check ansible/applications # every role folder under a tree
python3 -m rolecheck check ansible/applications/pdq_deploy   # one role folder (its parent must be a namespace directory)
python3 -m rolecheck check --report-only --format json <path> # findings do not fail; usage errors still do; machine-readable
make fleet ROOTS="/path/to/repo1 /path/to/repo2"            # one report per root under reports/
```

A role folder is any immediate subdirectory of a directory named `applications`, `host_roles`, `operating_systems`,
`utilities` or `roles`, even an empty one. Findings print as `path:line ID: message` (built-in ansible-lint ids carry no
message), then one `== role: N finding(s)` line per role, a `== root <path>: N finding(s)` line when the tool has something
to say about the run itself, and a `== total:` line. Exit 1 on any finding, 0 with `--report-only` or when clean, 2 when a
path is not a role folder or a tree containing one, when two paths would report the same role, or on a bad option.

The checker evaluates every tree with one toolchain (ansible-core 2.21.4, ansible-lint 26.8.0 and the collections in
`collections/requirements.yml`), not with each repository's own runtime pins; a repository that pins an older core or
collection may see schema or module findings its own toolchain would not report, and the reverse.

Never run `ansible-lint --fix` with this configuration: it inserts the `---` marker DOC-01 forbids and rewrites quoting.

## What it checks

Structure, on every role folder (new ids; they implement the owner's direction that every folder is created and that
application roles carry the shared loader `tasks/main.yml`):

| Id | What it checks |
|---|---|
| SCAFFOLD-01 | The twelve scaffold directories exist: defaults, files, handlers, library, lookup_plugins, meta, module_utils, molecule, tasks, templates, tests, vars. |
| SCAFFOLD-02 | `defaults/main.yml` defines the top-level `<role>_defaults` key the loader reads. |
| SCAFFOLD-03 | `README.md`, `meta/main.yml`, `defaults/main.yml` and `tasks/main.yml` exist. |
| LOADER-01 | In a role under `applications/`, `tasks/main.yml` is byte-identical to the shared framework loader. |

Style, on every YAML file in the role except a loader copy (excluded by digest, so a role's own `tasks/main.yml` is linted):

| Id | Enforced by | What it checks | Left to review or a later piece |
|---|---|---|---|
| FMT-01 | `rolecheck/lint/rules/fmt_01.py` | Every banner rule line (header box, Description rule, `#region`/`#endregion`, sibling separator) is exactly 97 columns; every region is closed by an `#endregion` with the same label and indentation; a marker with the wrong dash count is malformed. | — |
| FMT-02 | `rolecheck/lint/rules/fmt_02.py` | A task-file region label is `<Stage>: <Description>`, Stage one of Begin, Process, End, Always, every description word capitalized. | Whether a file needs regions at all; playbook labels. |
| NAME-01 | `rolecheck/lint/rules/name_01.py` | A task name is `'STAGE | Title Case Imperative'`, single-quoted, STAGE one of BEGIN, PROCESS, END, VALIDATE, every word capitalized; VALIDATE in `validate.yml` and nowhere else; a task inside an `always:` carries its enclosing stage's token. Handlers are exempt. | The imperative mood and whether a BEGIN reads, a PROCESS acts, an END verifies; playbook tokens. |
| FACT-01 | `rolecheck/lint/rules/fact_01.py` | `set_fact` (any of its three spellings) does not appear in an application role's task files. | Handlers and other role kinds, until the sentence names them. |
| LOOP-01 | `rolecheck/lint/rules/loop_01.py` | `loop:` not `with_*`; every loop carries a non-empty `loop_control.label`; a `loop_var` is `__dunder__`. | Whether a `loop_var` was needed; folding `loop_control`. |
| REG-01 | `rolecheck/lint/rules/reg_01.py` | A `register:` target is a string of the shape `'__<role>_<noun>__'`, single-quoted (null, boolean, integer and list targets are `schema[tasks]`'s). | Reads of `.changed` and `.rc`; defaults on registered fields in `when:`. |
| LEN-01 | `rolecheck/lint/yamllint.yml` line-length | No line exceeds 97 columns, unbreakable tokens included. | — |
| BOOL-01 | `rolecheck/lint/yamllint.yml` truthy | `true` and `false` only, keys included. | — |
| DOC-01 | `rolecheck/lint/yamllint.yml` document-start | No `---` marker. | — |
| ARG-02 | production profile `fqcn` | Every module is invoked by its fully-qualified name. | — |
| KEY-01 (part) | production profile `key-order` | `name:` first; `block`/`rescue`/`always` last. | Module last; the blank line before it. |

The whole `production` profile and yamllint's default set (with `rolecheck/lint/yamllint.yml`'s settings) are active; the
table maps the specification's ids and is not a list of every id a run can report. `TOOL` is the id of a finding the tool
raises about its own run (a warning on ansible-lint's stderr, a crash, an unparsable result): it is never silent.

## The fixtures are the contract

The three roles under `fixtures/style/applications/` are complete application roles, so every finding they produce is a
style finding: `fail_role` exercises every failing style clause, mostly in isolation and with the deliberate combined cases
its header documents, and `fixtures/style/expected-fail.txt` is its exact oracle; `pass_role` is a small role in the house
shape and `boundary_role` holds the constructs that sit on a rule's edge and must not fire; both must produce no finding and
no `TOOL` line. `fixtures/structure/struct_fail` holds two roles that break every structural rule, with
its own exact oracle. `tests/` asserts each rule's metadata and every hook branch and kind directly, plus discovery and the
structural checks in isolation. `make selftest` proves all of it. When a change adds, removes or relocates a finding, or
changes a message, update the oracle; when a change widens what passes or corrects a false positive, add the construct that
demonstrates it to `boundary_role`; when a change is to metadata or a branch, update the test that asserts it.

## Deferred

The ubi9 container image (CHECK-02), publishing this repository, and the remaining specification rules (KEY-01 module-last,
VAR-01, HAND-01, VARNAME-01, NULL-01, QUOTE-01, GUARD-02, CHG-01, ERR-01, WAIT-01, LOG-01, BLOCK-01, META-01 and DOC-02
content, PS-01, IGNORE-01, GUARD-01, CHK-01, WHEN-01, SCALAR-01, FLOW-01, COM-01, REG-01's conditional clauses, the playbook
kind, and STRUCT-01's non-directory clauses: flat task file names of the form `main.yml`, `validate.yml`,
`<state>_<family>.yml`; `vars/<family>.yml` never `vars/main.yml`; no `meta/argument_specs.yml`; `.gitattributes` with
`*.xml -text` where exported XML is tracked). SCAFFOLD-01 proposes to supersede STRUCT-01's bans on `library/`, `molecule/`,
`tests/` and the plugin directories; that ratification is the owner's.
