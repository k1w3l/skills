---
name: hermes-desktop-operations
description: "Use when checking Hermes Desktop startup or window modes."
version: 1.0.0
created_by: agent
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, desktop, electron, hud, startup, windowing, configuration]
    related_skills: [hermes-agent, inspecting-hermes-desktop-dom]
---

# Hermes Desktop Operations

Operate and troubleshoot the native Hermes Desktop application as a desktop
surface, not as the CLI/TUI or the web dashboard. This skill covers launch
behavior, window modes, startup preferences, desktop configuration, compositor
compatibility, and evidence-based answers about whether a GUI feature is
persistent.

## When to use

Use this skill when the user asks about:

- starting Hermes Desktop in a particular mode;
- HUD, quick entry, pop-out, focus, or always-on-top behavior;
- persistent window/layout preferences;
- `hermes desktop` flags or Desktop-specific configuration;
- Linux Wayland/XWayland, Hyprland/Omarchy, or other compositor behavior;
- whether a visible Desktop action has a supported config key, startup flag, or
  only an external automation workaround.

Do not use this skill for:

- general Hermes provider, gateway, skill, cron, or agent-core administration
  (use `hermes-agent`);
- CSS/DOM inspection while developing the Desktop renderer (use
  `inspecting-hermes-desktop-dom`);
- the separate web dashboard, whose lifecycle and plugins are different.

## Operating invariants

1. **Name the surface first.** Confirm that the question concerns native
   `hermes desktop`, not `hermes --tui`, the classic CLI, `hermes dashboard`,
   or a Quick Entry overlay. Similar names do not imply shared configuration.
2. **Installed build wins for local behavior.** Record `hermes --version` and
   inspect the installed build before relying on latest upstream documentation.
   State version differences explicitly.
3. **Read before write.** Inspect `hermes desktop --help`, the resolved
   `desktop` config section, and plausible candidate keys in read-only mode.
   Never add a speculative key merely to see whether the app accepts it.
4. **Classify state ownership.** A setting may belong to persistent YAML, a
   session/renderer store, native window geometry, a state file, or the desktop
   compositor. A persisted position or size does not prove that the selected
   window mode is persisted.
5. **No fabricated knobs.** If the supported surface has a shortcut or menu
   action but no config key or launch flag, say that it is not natively
   configurable in the checked version. Keep external wrappers/autostart and
   simulated hotkeys clearly separate from supported Hermes configuration.
6. **Treat negative findings as scoped evidence.** "No startup-HUD setting was
   found in version X" is valid; "Hermes can never start in HUD" is not, unless
   the product explicitly guarantees that across versions.
7. **Keep compositor settings separate.** Ozone/backend hints can alter
   pinning, click-through, floating, or rendering, but they do not automatically
   select a renderer/window mode.

## Verification workflow

### 1. Consult the local knowledge base

Follow the active wiki policy before external research. Search for the canonical
Hermes Desktop page and any Omarchy/compositor notes. Read the actual pages and
record the date of any state snapshot; do not treat a dated page as live state.

### 2. Identify the supported entry points

Run the non-mutating probes appropriate to the installed build:

```bash
hermes --version
hermes desktop --help
hermes config get desktop
hermes config path
```

For a suspected option, query it directly:

```bash
hermes config get desktop.<candidate>
```

A missing-key response is evidence to combine with help/source inspection, not
permission to invent or write the key.

### 3. Reconcile documentation and implementation

For a technical product question, resolve the official Hermes documentation in
Context7 and query the exact feature. Also consult the official Desktop
reference when needed. If the local source checkout is available, inspect the
feature's entry/exit functions and persistence calls with targeted file search.
Look specifically for:

- the command-line flag or IPC/menu action that enters the mode;
- whether the mode atom/store is restored at boot;
- geometry persistence, which is often a separate concern;
- native window creation and compositor-specific branches;
- explicit comments or tests that state whether the mode is persisted.

Use `references/hermes-desktop-feature-probe.md` for a compact probe matrix and
the verified HUD case.

### 4. Classify the answer

Report one of these outcomes:

- **Supported persistent setting** — provide the exact key/flag and restart or
  reload requirement.
- **Supported transient action** — provide the shortcut/menu action and explain
  that it must be repeated after relaunch.
- **External workaround** — describe only a validated wrapper/autostart path,
  with readiness, focus, compositor, and failure-recovery caveats.
- **Unresolved** — say what evidence is missing instead of guessing.

### 5. If the user requests a change

Before editing configuration, state the exact file/key and scope. Make the
smallest change, preserve unrelated values, restart the relevant Desktop
process, and verify the resulting behavior. For native Desktop state, avoid
claiming success from a config write alone: confirm the window mode after a
fresh launch. Do not relaunch or manipulate the user's live window merely to
answer a read-only question.

## External notification boundaries

A notification created by Omarchy/Quickshell/libnotify is not automatically a Hermes Desktop notification. Before debugging a no-op click, classify the owner and trace sender metadata, persistence, click handler, and target separately. An external notification has no renderer-owned Hermes session binding unless an explicit supported bridge provides one.

For an external notification that should open diagnosis, prefer a fixed allow-listed notification class and an absolute user-owned launcher. Pass the alert body as one argv element, treat it as untrusted data, and keep the diagnostic prompt read-only. Do not replay arbitrary `execArgv` from notification history or claim that a launcher opened the current Desktop conversation when it actually starts a separate CLI/TUI session.

Background launch contexts can differ from an interactive terminal. Validate command resolution in the launcher's environment, use explicit paths for the known action, reload the relevant shell/Desktop component, and verify the actual click separately from parser/configuration success. Keep the UI workaround clearly labeled as external to the native Desktop protocol.

See [`references/notification-bridge-boundary.md`](references/notification-bridge-boundary.md) for the reusable source-to-handler checklist and safe argv pattern.

## Common distinctions

| Surface or setting | What it controls | What it does not prove |
|---|---|---|
| `display.interface` | CLI interface selection such as CLI/TUI | Native Desktop startup mode |
| Desktop HUD toggle | Runtime floating HUD window | Persistent HUD preference |
| Window state file | Position and size recovery | Which window mode opens |
| `desktop.ozone_platform_hint` | Electron Wayland/XWayland behavior | Selecting HUD at startup |
| Quick Entry shortcut | Separate global composer | Main Desktop/HUD state |
| Web dashboard theme/layout | Browser dashboard presentation | Native Electron Desktop layout |

## Completion checklist

- [ ] Native Desktop was distinguished from CLI/TUI/dashboard.
- [ ] Installed version and relevant live help were checked.
- [ ] Candidate configuration keys were queried read-only.
- [ ] Persistent config, runtime state, geometry, and compositor behavior were
      considered separately.
- [ ] Official current documentation was consulted when the question was
      version-sensitive.
- [ ] Negative findings are scoped to a version/build and backed by evidence.
- [ ] Any workaround is labeled external and its limitations are stated.
- [ ] A requested change was verified after the relevant restart.
- [ ] No secrets or speculative settings were written.

## Related skills

- `hermes-agent` — general Hermes setup, configuration, gateway, and CLI.
- `inspecting-hermes-desktop-dom` — live Desktop DOM/CSS and renderer facts.
- `omarchy` — end-user compositor and desktop customization.
