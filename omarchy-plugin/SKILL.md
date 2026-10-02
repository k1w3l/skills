---
name: omarchy-plugin
description: >
  REQUIRED for developing, cloning, validating, packaging, or publishing an
  Omarchy Quattro shell plugin (Quickshell/QML). Use whenever the user wants
  to create a plugin, customize a built-in by cloning it, write manifest.json,
  BarWidget.qml, Panel.qml, Overlay.qml, Menu.qml, Service.qml or Bar.qml,
  run omarchy plugin clone/validate/add/enable, list a plugin on
  plugins.omarchy.org / omarchyplugins.com, or submit to the marketplace.
  Also trigger for "plugin do Omarchy", "desenvolver plugin", "publicar
  plugin", "marketplace de plugins", or any custom bar widget / overlay /
  menu / service for omarchy-shell. Do not use for ordinary Hyprland or
  shell.json tweaks — that is the omarchy skill. Do not use for Omarchy
  core source (`omarchy dev link`, migrations).
---

# Omarchy plugin development

Build and publish third-party plugins for `omarchy-shell` (Omarchy Quattro).
End-user bar/theme tweaks stay in the `omarchy` skill. This skill is the
workflow for **authoring** plugins.

Official walkthroughs:

- Develop: https://plugins.omarchy.org/develop.html
- Publish: https://plugins.omarchy.org/publish.html
- Manual: https://omarchy.org/manual/shell-plugins/
- Runtime contract: `$OMARCHY_PATH/shell/README.md` (usually `/usr/share/omarchy/shell/README.md`)
- First-party catalogue: `$OMARCHY_PATH/shell/plugins/README.md`

Read [`references/develop.md`](references/develop.md) when implementing QML.
Read [`references/publish.md`](references/publish.md) before listing on the marketplace.
Read [`references/first-party.md`](references/first-party.md) to pick a built-in to clone.

## Safety

Plugins share the long-running `omarchy-shell` process. They run **unsandboxed**
with the user's permissions. Review every dependency and command. Never start a
second Quickshell process for a plugin (`quickshell -p ...` is wrong).

The installer never runs plugin code, install hooks, or sudo — it clones files,
validates the manifest, and flips enabled state over IPC. Anything a plugin
needs at runtime it must do itself after it is loaded.

Do not edit `$OMARCHY_PATH/shell/plugins/` (packaged). Work under
`~/.config/omarchy/plugins/<id>/`.

Third-party IDs cannot use the reserved `omarchy.*` namespace. Plugin folders
cannot contain symlinks (`omarchy plugin validate` rejects them).

Omarchy 4 strips `__sourceDir` from third-party manifests. Resolve plugin-local
files with `Qt.resolvedUrl(".")` (or an equivalent relative URL), not
`manifest.__sourceDir`.

## Workflow

1. **Match a built-in.** Clone a first-party plugin with the same `kind` and
   interaction pattern. Do not design a new component from scratch until you
   have a working clone.
2. **Keep the clone ID while developing.** Use the exact ID printed by
   `omarchy plugin clone` (typically `<username>.clock`).
3. **Edit the contract.** `manifest.json` + the QML named in `entryPoints`.
4. **Validate without running.** Manifest layout, then `qmllint`.
5. **Inspect in the live shell.** Enable, summon, hide, click, Escape, disable,
   re-enable, restart shell, remove.
6. **Publish.** Permanent namespaced ID, drop `omarchy.clonedFrom`, public
   GitHub repo, README + LICENSE, then marketplace submission.

Saved files under `~/.config/omarchy/plugins/` hot-reload. Force discovery with
`omarchy-shell shell rescanPlugins`. Code in a `keepLoaded` service or overlay
only takes effect after `omarchy restart shell`.

## Plugin kinds

| Kind | `entryPoints` key | Typical file | Use it for |
|------|-------------------|--------------|------------|
| `bar-widget` | `barWidget` | `BarWidget.qml` | Item in the active bar |
| `panel` | `panel` | `Panel.qml` | Floating surface |
| `overlay` | `overlay` | `Overlay.qml` | Fullscreen surface |
| `menu` | `menu` | `Menu.qml` | Summoned menu |
| `service` | `service` | `Service.qml` | Headless singleton |
| `bar` | `bar` | `Bar.qml` | Full bar replacement |

A plugin may declare several kinds (e.g. `service` + `bar-widget`). Only one
`bar` is active at a time.

A details popout loaded from a bar widget is **not** a second kind. Keep
`kinds: ["bar-widget"]` and `Loader` the panel from `BarWidget.qml`. Declare
`panel` only for a standalone floating surface. Fullscreen HUDs use `overlay`,
not `panel`.

Keep the same `moduleName` (the plugin id) in every QML root.

## Clone a built-in

```fish
omarchy plugin clone omarchy.clock --edit
```

On success the command prints the new id, creates the folder, enables the copy,
and replaces the built-in in the bar:

```
~/.config/omarchy/plugins/<username>.clock/
├── manifest.json
├── BarWidget.qml
├── Panel.qml
└── Model.js
```

Calls to the original built-in id are routed to the enabled clone. Removing the
clone restores the built-in. Keep `omarchy.clonedFrom` in the manifest while
that restore path matters.

Browse first-party examples before inventing a new shape — see
[`references/first-party.md`](references/first-party.md).

## Manifest

Required for load/validate: `schemaVersion`, `id`, `name`, `version`, `kinds`,
`entryPoints`. Required for marketplace listing: also `author` and
`description`. `version` may be up to 64 characters on the marketplace.

Development clone (keep `clonedFrom`):

```json
{
  "schemaVersion": 1,
  "id": "yourname.clock",
  "name": "Custom Clock",
  "version": "1.0.0",
  "author": "Your name",
  "license": "MIT",
  "description": "A small clock with a details panel for the Omarchy bar.",
  "kinds": ["bar-widget"],
  "entryPoints": { "barWidget": "BarWidget.qml" },
  "barWidget": {
    "displayName": "Custom Clock",
    "category": "Time",
    "allowMultiple": false,
    "defaultSection": "center"
  },
  "omarchy": { "clonedFrom": "omarchy.clock" }
}
```

`barWidget` extras: `displayName`, `category`, `allowMultiple`, optional
`defaultSection`, optional `defaults` + `schema` for inline settings in
`shell.json`. Most widgets set `allowMultiple` to `false`; spacers/indicators
set `true`.

Kind and entry point must agree (`bar-widget` → `entryPoints.barWidget`).
Every referenced file must exist as a **safe relative path**.

Permanent published id: drop `omarchy.clonedFrom` and switch to a globally
unique lowercase namespace such as `io.github.yourname.custom-clock`. IDs are
permanent marketplace identifiers; retired IDs cannot be reused.

## Implement

`BarWidget.qml` is the manifest entry point for a bar widget. Forward the
panel lifecycle that Quattro uses for clicks and shell commands:

- properties: `opened`, `popoutSwitchClosing`
- functions: `open()`, `close()`, `toggle()`, `closeForPopoutSwitch()`
- inject `bar`, `anchorItem`, and `hostWidget` into the loaded panel

`Panel` base provides open state and controller. `KeyboardPanel` anchors to
the bar button. Escape closes through `PanelKeyCatcher`.

Copy-ready QML for the official clock tutorial lives in
[`references/develop.md`](references/develop.md). Prefer cloning the real
built-in (`omarchy.clock` includes `Model.js`, format cycling, calendar) and
editing that, rather than pasting the tutorial over it unless the user asked
for the tutorial tree.

For overlays/services, match `omarchy.image-picker` / `omarchy.media` instead.
Custom IPC (`IpcHandler`) belongs on a `service` that stays loaded; an overlay
that is not `keepLoaded` is missing until `summon`.

## Validate

```fish
set PLUGIN_ID yourname.clock
set PLUGIN_DIR $HOME/.config/omarchy/plugins/$PLUGIN_ID
omarchy plugin validate $PLUGIN_DIR
set qmlint /usr/lib/qt6/bin/qmllint
if not test -x $qmlint
    set qmlint (command -v qmllint)
end
$qmlint -I $OMARCHY_PATH/shell \
    $PLUGIN_DIR/BarWidget.qml $PLUGIN_DIR/Panel.qml
```

`$OMARCHY_PATH` is `/usr/share/omarchy` when unset. System `qmllint` often
lives at `/usr/lib/qt6/bin/qmllint` (not on PATH). Warnings on `qs.*` imports
are expected; the command should still exit 0. A broken mapping looks like:

```
entry point file not found: 'BarWidget.qml'
```

Validate checks: JSON parses; required fields; kind/entry-point agreement;
files exist; id is not `omarchy.*`; no symlinks in the folder.

## Run and inspect

```fish
set PLUGIN_ID yourname.clock
omarchy plugin list --json | jq --arg id $PLUGIN_ID '.[] | select(.id == $id)'
omarchy-shell shell summon $PLUGIN_ID '{}'
omarchy-shell shell hide $PLUGIN_ID
```

A discovered bar-widget looks like `{"id":"...","kinds":["bar-widget"],"enabled":true}`.

`summon` / `hide` route to `open()` / `close()` on the bar entry point. Before
sharing, test click, Escape, shell open/close, disable, re-enable, shell
restart, and removal.

Useful IPC (the wrapper talks to the already-running shell; it does not start
one):

```fish
omarchy-shell shell ping
omarchy-shell shell toggle $PLUGIN_ID '{}'
omarchy-shell shell listPlugins
omarchy-shell shell rescanPlugins
omarchy restart shell
```

Agents/scripts: `omarchy plugin add <url-or-path> --enable --yes` skips
prompts. Without a TTY the commands refuse rather than guess.

Place a bar widget after enable:

```fish
omarchy bar move $PLUGIN_ID --section center
```

## Enablement (shell.json)

Third-party plugin is enabled **iff** its id appears in
`~/.config/omarchy/shell.json` — bar layout entry, `plugins[]`, or `bar.id`.
First-party non-widgets are on unless listed in `disabledPlugins[]`. A full
bar has no off state; you replace it by enabling another `kind: "bar"`.

Settings are inline on the layout/plugin entry. No separate per-plugin config
file.

## Local gotchas

These are easy to miss and have already bitten real plugins here:

- **One shell.** Never `quickshell -p` a plugin. Summon through `omarchy-shell`.
- **Nested panel ≠ `panel` kind.** Bar popouts stay inside `bar-widget`.
- **`keepLoaded`.** Overlay/service code changes need `omarchy restart shell`.
- **No `__sourceDir`.** Third-party manifests lose it; use `Qt.resolvedUrl(".")`.
- **`plugin add` does not create `.desktop` or menu entries.** Add
  `~/.config/omarchy/extensions/omarchy-menu.jsonc` (and a `.desktop`) yourself
  if the plugin needs a launcher.
- **Helper scripts + fish.** `config.fish` may run `fastfetch`. Invoke helpers
  with `fish --no-config` so plugin-spawned scripts stay quiet and keep PATH.
- **QML helpers from PATH.** Reconstitute PATH in those scripts; login PATH is
  not guaranteed.
- **Clones vs git repos.** Develop in `~/.config/omarchy/plugins/<id>/` (hot
  reload). Keep a canonical git repo (e.g. `~/git/<name>`) and install with
  `omarchy plugin add ~/git/<name> --yes` when you want a git-managed checkout.
- **Updates.** `omarchy plugin update` is a fast-forward of the git checkout.
  Local patches (Displaywright-style) vanish on update.

Wiki examples: `omarchy-alfred` (service + overlay + bar-widget),
`omarchy-wallpapers-monitores` (`__sourceDir` hole), `omarchy-notificacoes`
(clone of `omarchy.notifications`).

## Publish

Distribution is a **public GitHub repository** with `manifest.json` at the
root. Anyone installs with:

```fish
omarchy plugin add https://github.com/yourname/custom-clock.git --enable
```

Marketplace listing is separate: it validates the repo, not plugin security.
You remain responsible for code, assets, docs, and license.

Before submit: permanent id, no `clonedFrom`, README with Install / Usage /
Configure / Remove, LICENSE (keep upstream copyright if the QML came from an
Omarchy clone), optional `preview.png` (or jpg/jpeg/webp/avif) at the repo
root. Document every external binary, service, and privilege the plugin uses.

Then follow [`references/publish.md`](references/publish.md). Do **not** open
the marketplace issue until the owner has approved the exact title and body.

## Troubleshooting

| Symptom | What to check |
|---------|----------------|
| Folder not found | Exact clone id under `~/.config/omarchy/plugins/` |
| Entry point missing | `entryPoints` filename and capitalization match disk |
| Validates but not listed | `omarchy-shell shell rescanPlugins`, then `omarchy plugin list --json` |
| Listed but invisible | Enable it; confirm kind; `qs log -p $OMARCHY_PATH/shell --tail 100` |
| Panel opens once, not again | Forward `opened`, `open()`, `close()` from bar entry to the loaded panel |
| IPC `Target not found` | Custom target lives on a loaded `service`; overlay-only is gone when hidden |
| QML runs old service code | `keepLoaded` — `omarchy restart shell` |
| Process `QList("/foo.sh")` | `__sourceDir` was empty; resolve the plugin directory from QML |

## Out of scope

- Editing Hyprland / themes / hooks as an end user → `omarchy` skill
- Editing Omarchy package sources, migrations, `omarchy dev ...`
- Security review of third-party plugins (marketplace listing is not one)
