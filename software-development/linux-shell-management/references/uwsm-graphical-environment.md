# Graphical UWSM environment verification

Use this when a user-installed executable works in a terminal but is invoked by a Hyprland/Omarchy notification, desktop launcher, or user service.

## Why the distinction matters

`$SHELL`, the interactive shell's `PATH`, and an already-running compositor are separate from the environment inherited by UWSM, Quickshell, `systemd --user`, and `uwsm-app-daemon`. Always inspect the environment of the process that actually launches the action.

## Persistent user configuration

Use a user-owned UWSM environment fragment. Keep it POSIX-shell-compatible because the fragment is sourced during session preparation:

```sh
# ~/.config/uwsm/env.d/20-user-cli
case ":${PATH:-}:" in
  *":$HOME/.local/bin:"*) ;;
  *) PATH="$HOME/.local/bin${PATH:+:$PATH}" ;;
esac
export PATH
```

Do not modify `/usr/share/omarchy/`; package updates own that tree.

## Apply and verify

- For a safe current-session update, set the user manager environment and restart only the affected daemon when appropriate.
- If the compositor or shell still has the old environment, start a fresh graphical login rather than claiming the current session was rebuilt.
- Read back the manager environment:

```bash
systemctl --user show-environment
```

- For a named daemon, inspect its environment through `/proc/<pid>/environ`, printing only non-sensitive keys such as `PATH`, `HOME`, and `SHELL`.
- Correlate the action with the journal:

```bash
journalctl --user -b -g 'agent|xdg-terminal|hermes|omarchy'
```

A journal entry proving `xdg-terminal-exec` received a command proves launch routing, not that a model answered or that an existing desktop chat received the prompt.

## Omarchy agent handoff

The stock Omarchy crash-notification action resolves the selected agent using `omarchy default agent`. For Hermes it opens a separate terminal/TUI command similar to:

```text
env -u HERMES_SESSION_SOURCE hermes chat --yolo --tui --query=<prompt>
```

Use `omarchy default agent` and the agent-specific check command to confirm selection and installation. Do not assume that “Hermes CLI was launched” means the prompt was inserted into the currently open Hermes Desktop conversation.
