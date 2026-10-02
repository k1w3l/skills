# Chrome/Chromium Wayland UI-stall evidence recipe

Use this reference for tabs, navigation, or repaint freezes on Linux. It is a diagnostic recipe, not permission to change a user's configuration.

## Capture a baseline

Record only non-private operational data:

- browser package/version;
- session and compositor (`XDG_SESSION_TYPE`, Hyprland/Niri/Sway, and display backend);
- GPU/driver and render node;
- browser root and child process arguments;
- memory/swap/disk pressure, OOM, coredumps, GPU reset/page-fault/ring-timeout messages.

Do not read cookies, passwords, tokens, history, authenticated page content, or arbitrary profile databases.

## Safe flag A/B

1. Copy the user flag file to a timestamped backup.
2. Remove or add one experiment only.
3. Fully stop and relaunch the browser through the desktop launcher.
4. Confirm the effective child arguments, not merely the edited file.
5. Test `https://example.com/` and a second public page in separate tabs.
6. Keep the change only if the original symptom disappears over its normal failure interval; otherwise restore the backup or revert the exact lines.

For a native-Wayland test, the expected evidence is an Ozone Wayland argument on the GPU/renderer child and a mapped application in the compositor. Absence of an X11-only screenshot is a control-tool limitation when the app is Wayland-native.

## Useful read-only checks

```bash
ps -C chrome -o pid=,ppid=,stat=,args=
hyprctl clients -j
journalctl -b --since '5 minutes ago' --no-pager
```

Filter compositor JSON to the application class and non-private fields. Avoid copying full command lines when they contain user URLs or profile paths that are not needed for the diagnosis.

## Interpretation guardrails

- An `ERROR` prefix can be a component log level; compare it with the process exit code and coredump state.
- `DEPRECATED_ENDPOINT` from GCM/registration is a remote service warning, not evidence of a browser crash.
- `Frame latency is negative` and VSync failures suggest presentation timing, but are not GPU proof. If the message appears in a GPU-disabled variant, keep the hypothesis at the compositor/presentation layer.
- A short clean restart and a couple of successful tabs demonstrate a passing smoke test only; they do not close an intermittent-freeze investigation.

Record the exact variant, backup path, effective backend, smoke-test interval, and unresolved uncertainty in the canonical operational wiki. Never store secrets in the reference or the wiki.