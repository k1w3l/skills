# Terminal emulator shell handoff

**Use when** the account's login shell is correct but a desktop terminal emulator still starts the previous shell.

## Diagnosis

The account record and the current desktop environment are different sources of truth:

```bash
getent passwd "$(id -un)" | cut -d: -f7
printf '%s\n' "${SHELL:-unset}"
command -v fish
```

After `chsh`, an existing graphical session can keep exporting the old `SHELL` value. A terminal that follows `$SHELL` may therefore continue launching Bash until a full logout/login. If only one terminal is affected, an explicit terminal setting is the narrower fix.

## Alacritty 0.17+

The default user configuration is `~/.config/alacritty/alacritty.toml`. Set the executable under the current table:

```toml
[terminal.shell]
program = "/usr/bin/fish"
```

Resolve the path first with `command -v fish`; do not assume `/usr/bin/fish` when the machine may install it elsewhere. Alacritty 0.17 accepts the older top-level `[shell]` table as legacy input but emits a deprecation warning; use `[terminal.shell]` for new edits.

Before editing, make a timestamped backup. Do not edit `/usr/share/omarchy/` or other packaged defaults. Keep the change in the user-owned config and preserve existing imports, theme settings, and keyboard bindings.

## Validation

Use Alacritty itself to parse the configuration and its imports without opening an initial window:

```bash
timeout 3s alacritty \
  --config-file "$HOME/.config/alacritty/alacritty.toml" \
  --daemon -vv
```

A timeout is expected because the daemon remains alive; the useful result is that the configured file and its imports are reported as loaded and no configuration warning is emitted. This validates parsing and imports, not the child shell itself.

The shell setting applies to a new terminal process. Close and reopen the affected Alacritty window, then verify inside it with one of:

```bash
printf '%s\n' "$0"
ps -p $$ -o comm=
```

If all applications should inherit the new `SHELL`, perform a full logout/login instead of adding per-application overrides everywhere. Use `omarchy restart terminal` only when restarting existing terminal windows is safe for their running processes.
