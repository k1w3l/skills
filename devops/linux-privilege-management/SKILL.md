---
name: linux-privilege-management
description: "Use when managing Linux sudo. Validate safely."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [linux, sudo, sudoers, polkit, privilege-escalation, agents, security]
    category: devops
    requires_toolsets: [terminal, file]
    related_skills: [hermes-agent, omarchy, arch-package-management, self-hosted-service-recovery]
---

# Linux Privilege Management

Manage privilege escalation for Linux operators and headless automation without
turning a convenience request into an unreviewed root backdoor. This is a
class-level runbook for `sudo`, `sudoers`, Polkit, systemd services, and agents
that must perform administrative work. Use `references/hermes-sudo-headless.md`
for the Hermes/PCL snapshot and the headless-session implications discovered in
operation.

## When to use

Use this skill when:

- a user wants an agent, service, cron job, or messaging gateway to run
  administrative commands without repeated password prompts;
- `sudo` fails in a non-interactive terminal, delegated subagent, or gateway;
- a `sudoers` or Polkit rule must be designed, installed, validated, or rolled
  back;
- a root-capable automation path needs an explicit scope and an external test.

Do not use this skill to obtain, guess, store, or transmit a user's password in
chat, tool arguments, process arguments, shell history, logs, or the skill
library. Do not silently broaden a command allowlist to `NOPASSWD: ALL`.

## Security model

1. **Separate authentication from agent approval.** `sudo` password handling,
   `sudoers` policy, Hermes command approvals, and service authorization are
   separate layers. Making `sudo` passwordless does not justify disabling
   Hermes approvals or other safety gates.
2. **Prefer least privilege.** Start with a narrowly defined command allowlist
   or a root-owned wrapper with strict argument validation. Treat flexible
   arguments to `systemctl`, editors, package managers, interpreters, mount
   tools, and service managers as possible root escape paths.
3. **Require explicit scope for broad access.** A rule such as
   `user ALL=(ALL) NOPASSWD: ALL` gives every process running as that user the
   ability to become root. It is not an Alfred-only permission. Apply it only
   after the operator explicitly chooses that risk and the host is trusted.
4. **Never use the chat as a password channel.** An interactive local parent
   may display a masked prompt, but a gateway, messaging session, or delegated
   child may not have a secure serialized password channel. Headless operation
   needs an already valid `NOPASSWD` policy or a locally provisioned secret.
5. **Preserve a reversible boundary.** Put new sudoers rules in a separate
   `/etc/sudoers.d/` file, retain the source candidate, avoid editing the main
   `/etc/sudoers` file directly, and document the exact path and rollback scope.
   Removing the rule is a deletion and requires explicit operator permission.

## Required workflow

### 1. Read local policy and establish the target

Before changing anything:

- consult the environment's canonical wiki and relevant operational notes;
- identify the exact Unix account with `id -un`, `id`, and `getent passwd`;
- identify whether the caller is a local interactive session, systemd user
  service, gateway/messaging process, delegated child, SSH session, or another
  terminal backend;
- inspect `sudo -n -l` without prompting, and record existing `NOPASSWD` rules;
- check the effective backend and service state without printing secrets.

Do not assume the account, backend, or service identity from memory. A host's
`sudoers` policy does not automatically apply inside Docker, SSH, or cloud
backends.

### 2. Choose the smallest workable mechanism

Use this order:

1. **Existing policy or command design:** run the needed command without sudo
   when it is already user-owned; reuse an existing narrow rule if its exact
   arguments are safe.
2. **Narrow `NOPASSWD`:** add only the administrative commands and argument
   forms actually required. Prefer a dedicated root-owned wrapper when direct
   sudoers argument matching would be too permissive.
3. **Locally provisioned `SUDO_PASSWORD`:** for Hermes headless sessions only
   when storing a protected credential is acceptable. Add it manually on the
   agent machine to the profile `.env`, keep mode `0600`, and never expose its
   value to the agent or chat. Re-evaluate this option for remote/container
   backends because password forwarding or embedding changes the trust boundary.
4. **Broad `NOPASSWD: ALL`:** only after explicit operator selection, with the
   all-processes-as-that-user risk stated plainly.
5. **Longer `timestamp_timeout`:** use only when the goal is fewer prompts in an
   interactive terminal. It does not solve a headless gateway or child process
   that has no valid sudo ticket.

Do not change `approvals.mode` merely because sudo prompts are inconvenient.
That setting controls Hermes command approval and must be decided separately.

### 3. Prepare and validate a sudoers candidate

Create a candidate in a user-owned path, for example under
`~/.config/hermes/`, with a descriptive filename. Include a short comment that
states scope and date, but never include a password. For a full, explicitly
approved rule, the shape is:

```sudoers
user ALL=(ALL) NOPASSWD: ALL
```

Validate the candidate before installation:

```bash
chmod 600 /path/to/candidate
visudo -cf /path/to/candidate
```

Install into `/etc/sudoers.d/` only after the scope is confirmed. Prefer a
lexically late name when the intention is for the new tag to override a more
general earlier entry, and use root ownership/mode:

```bash
pkexec /usr/bin/install -o root -g root -m 0440 \
  /path/to/candidate /etc/sudoers.d/99-operator-privilege
```

Use `sudo` in a visible terminal when it can safely accept authentication; use
`pkexec` for a graphical authentication agent when the caller cannot provide a
TTY. The agent must never click a password dialog or type the password.

### 4. Verify the live external state

After installation, verify all of the following, using `sudo -n` only after the
new policy is expected to apply:

```bash
sudo -n stat -c '%A %U:%G %n' /etc/sudoers.d/99-operator-privilege
sudo -n visudo -c
sudo -n true
sudo -n id -u
sudo -n -l
```

Use `sudo -n true` as the non-interactive probe. `sudo -n -v` is not an
 equivalent probe for this purpose: `-v` refreshes a credential ticket and may
still request authentication even while ordinary `NOPASSWD` commands work.

Then exercise the actual caller path with a harmless command such as
`sudo id -u` or `sudo whoami`. For Hermes, this confirms both the live sudoers
policy and the terminal tool's non-interactive handling. For a gateway or user
service, also verify its service state and perform a bounded, read-only command
through the same path.

A successful file installation alone is not proof. Do not claim completion
until syntax, permissions, effective policy, and the real execution path have
all been observed.

### 5. Record and maintain the boundary

Document the final rule path, exact scope, owner/mode, validation result, and
security implication in the canonical operational wiki. Never record secret
values. Keep the user-owned candidate as a non-secret source copy if useful.

If a future operator asks to narrow or remove the rule:

1. confirm the exact target and replacement policy;
2. obtain explicit permission before deleting the installed rule;
3. change one policy file at a time;
4. run `visudo -c` and repeat the non-interactive tests;
5. verify that the intended commands still work and unintended access no longer
authorizes.

## Headless Hermes notes

- An interactive parent session can prompt for a masked password and cache it
  for the session.
- Gateway, messaging, and delegated child sessions cannot rely on that prompt.
  They need `NOPASSWD` or a locally configured `SUDO_PASSWORD`.
- Hermes probes local `NOPASSWD` with `sudo -n true` and should not inherit the
  host's sudo state into Docker, SSH, Modal, or other non-local backends.
- Configuration changes to the Hermes `.env` normally require restarting the
  relevant gateway/service; a sudoers rule is read live and does not require a
  Hermes restart.

## Common pitfalls

| Symptom | Likely cause | Safer response |
|---|---|---|
| `sudo -n -v` still asks for a password after `NOPASSWD` | `-v` is refreshing the credential ticket | Test `sudo -n true`, then the real harmless command |
| A gateway or delegated child cannot use sudo | No secure interactive password channel | Provision a local secret or use an explicitly scoped `NOPASSWD` rule |
| A narrow rule unexpectedly grants broad root access | Flexible arguments can invoke an editor, shell, interpreter, or service escape | Replace it with strict argument matching or a validated root-owned wrapper |
| `sudo -n -l` shows both passworded and passwordless entries | Multiple matching sudoers entries and ordering/tags | Inspect the complete policy, use a clear lexical filename, and verify the exact command |
| `visudo` rejects the candidate | Syntax, permissions, or unsupported matching expression | Fix the candidate; never bypass syntax validation |
| The policy works locally but not in a container or SSH backend | Different execution environment and identity | Inspect and provision the target backend separately; never assume host root access crosses the boundary |
| User asks to undo the policy | Removal is a destructive filesystem change | Confirm the exact file and obtain explicit permission before deletion |

## Completion checklist

- [ ] Canonical wiki and live host state were consulted.
- [ ] Exact account, caller type, and backend were identified.
- [ ] Existing sudoers policy was inspected without a password prompt.
- [ ] Least-privilege path was considered before broad access.
- [ ] Any broad `NOPASSWD: ALL` scope was explicitly selected by the operator.
- [ ] No password entered the chat, tool arguments, logs, or skill files.
- [ ] Candidate passed `visudo -cf` before installation.
- [ ] Installed rule has root ownership and mode `0440`.
- [ ] `visudo -c`, `sudo -n true`, effective policy, and real caller path passed.
- [ ] Final scope, risk, and rollback boundary were documented.
