---
id: "CONN-01"
title: "CONN-01"
sidebar_label: "CONN-01"
sidebar_position: 19
tier: "`auto*`"
checked_by: "a new checker rejecting Windows-only connection variables under `all` and validating all three fields where localhost is explicit; whether a task override names a genuinely differe"
---

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

