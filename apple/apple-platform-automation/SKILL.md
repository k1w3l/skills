---
name: apple-platform-automation
description: "Operate Apple/macOS personal apps and background desktop automation: Notes, Reminders, Messages, Find My, and computer-use workflows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [apple, macos, notes, reminders, imessage, findmy, computer-use, automation]
    related_skills: [obsidian, google-workspace]
---

# Apple Platform Automation

Use this umbrella when a task targets Apple/macOS personal infrastructure: Notes.app, Reminders.app, Messages/iMessage/SMS, Find My, or background desktop UI automation. Prefer this single entry point over separate one-app micro-skills; then follow the relevant subsection.

## Routing

- **Apple Notes**: user wants cross-device notes, folders, search, edits, or exports in Notes.app.
- **Apple Reminders**: user wants iPhone/iPad-synced personal reminders or lists. If the request is an agent alert rather than a phone reminder, use `cronjob` instead or clarify.
- **Messages / iMessage / SMS**: user asks to send or inspect Mac Messages.app chats. Always confirm recipient and exact message before sending.
- **Find My**: user asks where an owned Apple device, AirTag, pet tag, keys, or bag is. Use UI automation + screenshots/vision; Apple exposes no stable CLI/API.
- **macOS computer use**: use `computer_use` when available to drive GUI apps in the background without stealing focus.

## Common macOS safety and permissions

- These workflows require macOS and signed-in Apple apps; do not attempt them on Linux hosts.
- Expect Privacy & Security prompts: Automation, Full Disk Access, Screen Recording, Reminders, or Messages access depending on the app.
- Use `pty=true` for interactive CLIs or permission prompts.
- For any outbound communication or destructive action, confirm exact target and content first.

## Notes.app via `memo`

Prereqs: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`; grant Automation access to Notes.app.

```bash
memo notes                         # list notes
memo notes -f "Folder Name"        # filter by folder
memo notes -s "query"              # fuzzy search
memo notes -a "Note Title"         # quick add
memo notes -e                      # edit selected note
memo notes -d                      # delete selected note
memo notes -m                      # move selected note
memo notes -ex                     # export to HTML/Markdown
```

Use Notes for Apple-device sync; use `memory` for agent-only durable facts and `obsidian` for Markdown-native knowledge work. Notes with attachments/images may not be editable through `memo`.

## Reminders.app via `remindctl`

Prereqs: `brew install steipete/tap/remindctl`; verify or request access with `remindctl status` / `remindctl authorize`.

```bash
remindctl today | tomorrow | week | overdue | all
remindctl list
remindctl list Work --create
remindctl add "Buy milk"
remindctl add --title "Meeting prep" --list Work --due "2026-02-15 09:00"
remindctl complete 1 2 3
remindctl delete 4A83 --force
remindctl today --json
```

`--due` and `--alarm` differ: due time is the task deadline; alarm is the notification trigger. For an early nudge:

```bash
remindctl add --title "Hairdresser" --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
remindctl today --json   # verify dueDate vs alarmDate
```

## Messages.app via `imsg`

Prereqs: `brew install steipete/tap/imsg`; grant Full Disk Access and Messages Automation.

```bash
imsg chats --limit 10 --json
imsg history --chat-id 1 --limit 20 --attachments --json
imsg send --to "+141****1212" --text "Hello" --service auto
imsg send --to "+141****1212" --text "See attached" --file /path/to/image.jpg
imsg watch --chat-id 1 --attachments
```

Rules: confirm recipient and content before sending, verify attachment paths, avoid bulk messaging, and use platform gateways for Telegram/Discord/Slack instead of iMessage.

## Find My via GUI automation

Apple provides no Find My CLI/API. Use AppleScript, `peekaboo`, screenshots, and `vision_analyze`.

```bash
osascript -e 'tell application "FindMy" to activate'
sleep 3
screencapture -w -o /tmp/findmy.png
```

Then analyze `/tmp/findmy.png` with vision. If `peekaboo` is available:

```bash
peekaboo see --app "FindMy" --annotate --path /tmp/findmy-ui.png
peekaboo click --on B3 --app "FindMy"
peekaboo image --app "FindMy" --path /tmp/findmy-detail.png
```

For AirTags, keep the item detail page visible while monitoring; location updates may pause if the page is minimized or not displayed. Respect privacy: only track user-owned devices/items.

## Background macOS computer-use

When `computer_use` is available, prefer element-index actions over coordinates:

```python
computer_use(action="capture", mode="som", app="Safari")
computer_use(action="click", element=7, capture_after=True)
computer_use(action="type", text="example")
computer_use(action="key", keys="cmd+s")
```

Rules:

1. Capture first (`mode="som"` for screenshot + numbered overlays + AX tree).
2. Click/drag by `element=N` whenever possible.
3. Verify after state changes, ideally with `capture_after=True`.
4. Do not set `raise_window=True` unless the user explicitly wants the window brought forward.
5. Scope captures to an app to reduce noise and privacy leakage.
