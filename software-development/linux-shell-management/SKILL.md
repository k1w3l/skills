---
name: linux-shell-management
description: >-
  Use for Linux login-shell changes and verification.
---

# Linux shell management

Manage the login shell recorded for a Linux account. This is distinct from
choosing a shell for one terminal emulator, editing shell startup files, or
changing a desktop's terminal preference.

## Scope and default interpretation

- Interpret “make X the default shell” as changing the current user's login
  shell unless the user explicitly asks to change every account or a system-wide
  policy.
- Existing terminals and already-running processes do not change. The new shell
  is used by new login sessions; reopening the terminal may be enough for a
  desktop session, while SSH/TTY login should be tested separately when
  relevant.
- Do not edit `/etc/passwd` by hand. Do not confuse a login shell with
  `$SHELL` inherited by an already-running process.

## Required workflow

1. **Identify the target account.** For the current user, use `id -un` and read
   `getent passwd "$(id -un)"`; preserve the account name exactly. For another
   account, require an unambiguous username and the necessary administrator
   privileges.
2. **Resolve and validate the shell.** Use `command -v <shell>` to obtain the
   executable path. Confirm it is executable and that the exact path appears in
   `/etc/shells`. Keep the resolved path literal; do not add arguments such as
   `fish -l` to the passwd field. If the shell is not listed, stop and explain
   that an administrator must review `/etc/shells` first rather than silently
   editing it.
3. **Read the current value before changing it.** Extract the seventh field of
   the passwd record and report whether a change is actually needed.
4. **Change only the intended account.** For the current user, run:

   ```bash
   chsh -s /absolute/path/to/shell
   ```

   Use the resolved absolute path from step 2. Do not prefix this with `sudo`
   for the current user: doing so can target root or change the authentication
   context unnecessarily. Changes for another account require an explicit,
   administrator-approved command with that username.
5. **Handle authentication safely.** `chsh` may request the account password.
   Never ask for, receive, or type a password in chat, tool arguments, logs, or
   scripts. If the execution channel cannot accept secure interactive input,
   stop that attempt and give the user the exact command to run in a normal
   terminal. Do not keep a password-prompting process alive or repeatedly poll
   it as if the change succeeded.
6. **Verify the external state.** Read the account record again and compare the
   seventh field with the requested absolute path. A successful command message
   alone is not sufficient. If verification fails, report the actual value and
   do not claim completion.
7. **Explain activation and rollback.** Tell the user to start a new login
   session. To restore Bash, use the same procedure with the previously recorded
   Bash path, for example `chsh -s /usr/bin/bash`, after validating that path.

## Fish-specific recipe

For Fish, use the resolved path rather than assuming `/usr/bin/fish` or
`/bin/fish`:

```bash
fish_path="$(command -v fish)" || exit 1
# Confirm "$fish_path" is listed in /etc/shells before continuing.
chsh -s "$fish_path"
```

Fish syntax is intentionally not POSIX shell syntax. Keep Bash/POSIX scripts
running under their declared interpreter (`#!/usr/bin/env bash`, `sh`, etc.);
changing the interactive login shell must not be treated as a script-portability
migration.

## Terminal-emulator handoff

Changing the account's login shell and reopening only a child process are separate concerns. A desktop session can retain the old `SHELL` value, and a terminal emulator may follow that value instead of rereading the account record. If one emulator still launches the old shell, inspect its user configuration before changing global files.

For Alacritty 0.17+, set the shell explicitly in the user-owned `~/.config/alacritty/alacritty.toml` with the current table:

```toml
[terminal.shell]
program = "/absolute/path/to/shell"
```

Use the path resolved by `command -v`, preserve the rest of the configuration, back up before editing, validate with the installed Alacritty binary, and close/reopen the affected terminal. The version-specific validation recipe and legacy-key warning are in [`references/terminal-emulator-shell.md`](references/terminal-emulator-shell.md).

## Graphical UWSM environment is separate

A login-shell change and a graphical session's environment are different state boundaries. Hyprland/Quickshell/UWSM may retain the environment captured when the session started, so `$SHELL` or `command -v` in an interactive terminal does not prove that a notification, desktop action, or user service can resolve the same executable.

For a user-installed CLI that must be launched by graphical actions:

1. Keep the command selection separate from the delivery mechanism; a desktop integration may intentionally open a new CLI session rather than inject into an already-open GUI conversation.
2. Use a user-owned fragment under `~/.config/uwsm/env.d/` to add the required user bin directory. Do not edit package-owned `/usr/share/omarchy/` files.
3. Update/restart the relevant user daemon when safe, and require a new graphical login when the compositor/session environment itself must be rebuilt.
4. Verify both `systemctl --user show-environment` and the target daemon's environment, then inspect the user journal for the actual launched command.

The copy-ready UWSM fragment and verification recipe are in [`references/uwsm-graphical-environment.md`](references/uwsm-graphical-environment.md).

## Common pitfalls

- Checking only `$SHELL` after changing the account: it may be inherited from the
  old session and is not a reliable read-back of `/etc/passwd`.
- Using `sudo chsh -s ...` without naming the target: this can change root's
  shell instead of the user's.
- Setting a shell path that is absent from `/etc/shells`, or adding a shell to
  that file without explicit administrative intent.
- Trying to change the shell by editing dotfiles or terminal-emulator config;
  those do not change the account's login-shell field.
- Claiming success from a command that is still waiting at `Password:` or from
  a background process whose exit status has not been observed.

## Supporting detail

- Fish-specific, copy-ready verification and authentication-boundary notes:
  [`references/fish-login-shell.md`](references/fish-login-shell.md)

## Completion checklist

- [ ] Target username is unambiguous.
- [ ] Shell executable was resolved and is executable.
- [ ] Exact shell path is allowed by `/etc/shells`.
- [ ] Current login-shell field was read before the change.
- [ ] No password was exposed to the agent or command history.
- [ ] The passwd record was read back and matches the requested path.
- [ ] User knows that a new login session is required.
