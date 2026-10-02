---
name: desktop-idle-display-diagnostics
description: Use for desktop idle/DPMS/screensaver diagnosis.
---

# Desktop idle, display power, and screensaver diagnostics

Diagnose Linux desktop inactivity behavior without guessing whether the fault
belongs to the idle scheduler, the fullscreen inhibitor, the lock screen, or
monitor power routing. Use this skill for Hyprland/Wayland and analogous desktop
stacks; read the platform-specific reference only when that stack is present.

## Always-on rules

- Start with read-only collection and the user's canonical documentation. Do not
  change display, lock, compositor, or shell configuration until the failing
  layer and a narrow correction are identified.
- Preserve the user's active work: do not force logout, reboot, lock, DPMS, or a
  disruptive monitor cycle merely to obtain a nicer test. If a physical cycle
  would interrupt the session, validate the effective IPC/configuration and mark
  the physical transition for the next natural idle cycle.
- Never edit package-owned desktop files such as `/usr/share/omarchy/`; place
  user overrides under `~/.config/` and keep the stock implementation read-only.
- Before persistent edits, create a timestamped backup beside every changed
  configuration file. Do not delete backups or runtime state without explicit
  permission.
- Apply only the user's requested scope. Do not alter global monitor scale,
  GPU flags, browser profiles, or unrelated window rules while fixing idle or
  display routing.
- Treat fullscreen playback inhibition as a window-state rule, not as a reason
  to disable the entire idle system. Prefer `idle_inhibit = "fullscreen"` for
  the specific application class instead of an always-on inhibitor.
- Report the distinction between configured monitor selection and observed
  physical DPMS state. A selector showing the intended monitor is not proof that
  a lock cycle has physically switched outputs.

## Procedure

### 1. Establish the current stack and the expected behavior

- Read the relevant wiki/runbook and the platform skill before touching the
  system.
- Record the exact expected result: which connector stays visible, which
  connectors go dark, the screensaver delay, the lock delay, and whether
  fullscreen playback should inhibit idle.
- Determine whether the user means an inactivity interval or a wall-clock
  schedule. Do not interpret a duration field as a time-of-day schedule.

### 2. Identify the active idle and lock mechanisms

Collect the live state without opening a browser or reading private content:

```bash
hyprctl monitors -j
hyprctl clients -j
systemctl --user list-units --all --no-pager --plain
systemctl --user list-timers --all --no-pager --plain
ps -eo pid=,ppid=,etimes=,comm=,args=
systemd-inhibit --list --no-pager
```

Filter the results for `idle`, `dpms`, `screensaver`, `lock`, `hypridle`,
`swayidle`, `niri-idle`, and the desktop shell. Read the actual user
configuration and the package implementation to determine which mechanism is
active; do not assume a legacy service is still in use.

### 3. Separate scheduler, inhibitor, and output routing

Treat these as independent checks:

1. **Scheduler:** what starts the screensaver and lock, and what units/IPC
   report their delays and timers?
2. **Inhibitor:** does the fullscreen client report that it inhibits idle?
   Inspect the client fields for `fullscreen`, `xwayland`, and
   `inhibitingIdle`; a fullscreen window with `inhibitingIdle=false` is a
   separate fault from monitor selection.
3. **Routing:** which monitor is designated as the input/keep monitor, and does
   the lock implementation invoke a selective output script or a global DPMS
   command? A global `dpms off` cannot express “all except this connector”.

Do not fix one layer by changing another. For example, increasing the timeout
will not make fullscreen playback inhibit idle, and changing a monitor mode
will not repair an absent lock selector.

### 4. Verify effective state through the desktop IPC

Use the stack's read-only status endpoints. For Omarchy/Quickshell, use:

```bash
omarchy-shell idle status
omarchy-shell lock monitors
omarchy-shell lock status
```

Interpret duration values according to the implementation (Omarchy's
`shell.json` values are seconds). After restarting a shell, an immediate IPC
`not responding` result can be a startup race: wait briefly, then retry once and
inspect the new process/journal before declaring failure.

### 5. Make the smallest targeted correction

For a user-owned Hyprland/Omarchy setup:

- Add an explicit keep/input monitor to the lock plugin configuration when the
  absence of that field falls back to `all`. Use the real connector name (for
  example `DP-3`), not a display mode or a monitor profile that reconfigures
  the keep output.
- Add a class-scoped fullscreen idle-inhibit window rule when the current
  fullscreen application lacks inhibition. Preserve existing rules, especially
  webapp tiling rules, and use the exact observed class.
- Set screensaver/lock durations explicitly in the active shell configuration;
  record them in seconds and state their human-readable values.
- Back up before edits, then reload the compositor and restart the shell only as
  required by the implementation. Never copy a stale Niri idle service into a
  Hyprland/Omarchy session without live evidence.

### 6. Verify every layer after the edit

Run all applicable checks again:

```bash
hyprctl reload
hyprctl configerrors
omarchy restart shell
omarchy-shell idle status
omarchy-shell lock monitors
omarchy-shell lock status
hyprctl monitors -j
hyprctl clients -j
```

Confirm that:

- the compositor reloads with no config errors;
- the shell IPC is responsive after its restart;
- the effective selector names only the intended keep monitor;
- the configured delays match the requested intervals;
- the current fullscreen client reports `inhibitingIdle=true`;
- the current physical monitor state is described accurately, including when
  all outputs remain on because the session is active and unlocked.

If a real lock/DPMS cycle is not safe to force, state that the physical
transition remains deferred and provide the exact evidence already validated.

## Common pitfalls

- **Assuming the legacy idle service is active:** inspect processes, user units,
  and shell IPC first because a migrated desktop may use an integrated shell
  service instead.
- **Calling a duration a clock schedule:** read the schema and status output;
  inactivity seconds do not specify a time of day.
- **Relying on a missing monitor field:** inspect the implementation's default;
  an absent `inputMonitor` may mean `all`, which bypasses the selective-output
  script.
- **Using global DPMS for selective output behavior:** global DPMS cannot keep
  one connector reliably on and may be re-enabled by keyboard/mouse activity;
  use the lock flow's selective output mechanism.
- **Adding a rule by replacing the existing rule block:** verify the diff keeps
  every prior behavior, because a targeted replacement can silently remove a
  webapp tiling or other window rule.
- **Treating a transient shell IPC race as a configuration failure:** wait for
  the new shell process and retry the read-only IPC once before changing more
  files.
- **Claiming physical validation from configuration alone:** distinguish the
  IPC selector, compositor syntax validation, and actual monitor DPMS state.

## Completion report

Report the diagnosed layer, the files changed and backups created, the exact
configured delays, the effective keep monitor, the fullscreen inhibitor result,
compositor/shell validation, and whether a physical lock/DPMS cycle was
observed or deliberately deferred.
