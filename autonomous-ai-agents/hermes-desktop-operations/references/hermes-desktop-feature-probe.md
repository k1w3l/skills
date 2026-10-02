# Hermes Desktop feature probe

This reference keeps the detailed evidence pattern for Desktop launch/window
questions out of the main skill while preserving a reusable example.

## Compact probe matrix

| Question | Read-only evidence |
|---|---|
| Which build is running? | `hermes --version` |
| Does the launcher expose it? | `hermes desktop --help` |
| Is there a config section/key? | `hermes config get desktop` and `hermes config get desktop.<candidate>` |
| Is the state persistent? | Local source: store initialization, restore path, state-file writes, tests |
| Is the setting only compositor behavior? | Official Desktop docs plus Electron/native windowing code |
| Is the manual action supported? | Official docs and the visible Desktop command/shortcut |

When a plausible key is missing, combine all rows before concluding. Never write
an unrecognized key as an experiment.

## Verified example: always opening in HUD

**Checked**: 2026-09-13, Hermes Agent `v0.21.0 (2026.8.31)` on Linux/Omarchy.

**Surface**: native Hermes Desktop, not the CLI/TUI or web dashboard.

**Evidence**:

- `hermes desktop --help` lists build and launch controls, but no option for
  starting in HUD.
- `hermes config get desktop` exposes Desktop/Electron settings, including
  `ozone_platform_hint`, but no HUD startup preference. Read-only queries for
  `desktop.hud`, `desktop.start_in_hud`, and `desktop.hud_on_startup` were unset.
- The local source `apps/desktop/src/store/hud.ts` explicitly describes `$hudActive` as
  deliberately not persisted; it is live window state.
- Official Desktop documentation says HUD is toggled with **Ctrl/Cmd+Shift+H**
  or the titlebar button, and the same shortcut exits it.
- `desktop.ozone_platform_hint` changes Wayland/XWayland window behavior and
  pinning; it does not choose HUD at launch.

**Scoped conclusion**: the checked build has no native persistent "always start
in HUD" setting. Starting normally and pressing Ctrl/Cmd+Shift+H is the supported
path. A wrapper/autostart action that sends the shortcut after the app is ready
would be an external workaround with compositor/readiness dependencies, not a
Hermes configuration key.

**Authoritative source**: Hermes Desktop guide,
https://hermes-agent.nousresearch.com/docs/user-guide/desktop (HUD mode).
The official source was also retrieved through Context7 library
`/nousresearch/hermes-agent`; the local source was used to scope the result to
the installed build.
