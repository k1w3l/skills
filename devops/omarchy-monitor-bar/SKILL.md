---
name: omarchy-monitor-bar
description: Use when hiding the Omarchy bar on chosen monitors.
version: "1.0.0"
author: Alfred
license: UNLICENSED
metadata:
  hermes:
    tags: [omarchy, linux, quickshell]
    related_skills: [omarchy]
---

# Omarchy bar visibility per monitor

## When to Use

- The user wants the Omarchy Quickshell status bar hidden on selected output(s) while it remains on other monitors.

## Procedure

1. Load the `omarchy` skill and consult the wiki first. Inspect the current active monitor names with `hyprctl monitors -j`, the current `~/.config/omarchy/shell.json`, and the installed bar documentation/source under `$OMARCHY_PATH/shell/plugins/bar/`. Check whether the installed release now provides a native output filter before customizing.
2. Never edit `/usr/share/omarchy/`. The Omarchy 4.0.4 stock bar creates one `BarPanel` per `Quickshell.screens` entry and its `shell.json` schema has no output-exclusion setting.
3. Back up `~/.config/omarchy/shell.json`, then clone the built-in full bar with `omarchy plugin clone omarchy.bar`. This creates a user-owned clone and selects it while preserving the existing bar layout/widgets.
4. In the clone's `Bar.qml`, pass the screen name from the `Variants` delegate into a plain property on the bar panel:

   ```qml
   BarPanel {
     required property var modelData
     screen: modelData
     monitorName: modelData.name
   }
   ```

   Declare `property string monitorName: ""` on `BarPanel`, then keep its remap guard and add the target-output check:

   ```qml
   visible: !remapGuard.remapping && monitorName !== "HDMI-A-1"
   ```

   Replace `HDMI-A-1` only with the exact connector the user requested. Do not reference `PanelWindow.screen` from this `visible` binding; in the tested Quickshell build that produced a binding loop. The delegate's `modelData.name` works as the output connector name.
5. Apply with `omarchy restart shell` if the file watcher/rescan does not update the active full-bar clone. Verify `omarchy-shell shell ping` returns `ok`; inspect `hyprctl layers` to confirm `omarchy-bar` is absent only on the target and remains on the other outputs; inspect `hyprctl monitors -j` to confirm the target has no bar reservation; check recent Quickshell logs for a `visible` binding loop or QML load failure.
6. To revert the active bar without deleting the clone, use the documented bar-selection command to reselect `omarchy.bar`. Never delete the clone or backup without explicit user permission.

## Scope note

The no-filter finding is specific to Omarchy 4.0.4; re-check the installed version/schema before applying this workaround on a later release. Record each completed system-specific change in the canonical wiki page, index, and log.
