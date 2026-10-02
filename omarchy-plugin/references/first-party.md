# First-party plugins to clone

Source: `$OMARCHY_PATH/shell/plugins/README.md`.

Match **kind** and **interaction** (bar chip + popout, fullscreen overlay,
headless service, summoned menu). Cloning copies the whole directory,
including extra kinds and local JS.

| Goal | Clone this | id | kinds |
|------|------------|----|-------|
| Bar chip + details panel | Clock | `omarchy.clock` | `bar-widget` |
| Bar chip + rich popup (audio/bt/net/…) | matching panel | `omarchy.audio` etc. | `bar-widget` |
| Fullscreen overlay (picker/HUD) | Image picker | `omarchy.image-picker` | `overlay` |
| Overlay (emoji / clipboard / reminders) | same family | `omarchy.emojis` / `clipboard` / `reminders` | `overlay` |
| Summoned menu | Omarchy menu | `omarchy.menu` | `menu`, `bar-widget` |
| Headless singleton | Battery / idle / night light | `omarchy.battery` etc. | `service` |
| Service + bar chip | Media | `omarchy.media` | `service`, `bar-widget` |
| Session lock / polkit | Lock / polkit | `omarchy.lock` / `omarchy.polkit` | `service` |
| Floating OSD | OSD | `omarchy.osd` | `panel` |
| Full bar replacement | Bar | `omarchy.bar` | `bar` |
| Notifications daemon | Notifications | `omarchy.notifications` | `service` |

Workspaces and other bar-only widgets may live as `*.manifest.json` next to
QML under `bar/widgets/` rather than a full plugin directory. Clone via
`omarchy plugin clone omarchy.workspaces` when that id exists on the machine.

Local examples already on this system:

- `kiwel.alfred` — `service` + `overlay` + `bar-widget` (wiki: omarchy-alfred)
- `kiwel.notifications` — clone of `omarchy.notifications`
- `kiwel.workspaces` — clone of `omarchy.workspaces`
