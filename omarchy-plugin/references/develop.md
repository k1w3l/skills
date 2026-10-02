# Develop a custom plugin

Source: https://plugins.omarchy.org/develop.html (updated 13 Aug 2026).
Runtime truth: `$OMARCHY_PATH/shell/README.md`.

This is the official `bar-widget` + details panel tutorial. Clone
`omarchy.clock` and keep the printed id (`yourname.clock` below) until
publishing. Then switch to a permanent namespaced id and drop
`omarchy.clonedFrom`.

Do not copy the id, repository URL, author, or description unchanged.
Document every external dependency, setup step, privilege, service,
installer, or remote build.

## Clone

```fish
omarchy plugin clone omarchy.clock --edit
```

```
~/.config/omarchy/plugins/yourname.clock/
├── manifest.json
├── BarWidget.qml
├── Panel.qml
└── Model.js
```

The real built-in also has format cycling, a calendar, and `Model.js`. The
tutorial below is the Marketplace’s simplified contract (clock + details
panel). Prefer editing the clone; use these files when starting from the
tutorial tree or when the user asked to match develop.html exactly.

Force discovery only when hot-reload misses:

```fish
omarchy-shell shell rescanPlugins
```

## Development manifest

Keep `kinds: ["bar-widget"]` and `entryPoints.barWidget: "BarWidget.qml"`.
The entry point loads `Panel.qml` internally — do not declare a separate
`panel` kind.

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

## BarWidget.qml

Displays the clock, loads `Panel.qml`, and forwards the panel lifecycle
Quattro uses for clicks and shell commands.

```qml
import QtQuick
import Quickshell
import qs.Ui

BarWidget {
  id: root
  moduleName: "yourname.clock"

  readonly property bool opened: panelLoader.item
    ? panelLoader.item.opened === true
    : false
  readonly property bool popoutSwitchClosing: panelLoader.item
    ? panelLoader.item.popoutSwitchClosing === true
    : false

  function open() {
    if (panelLoader.item) panelLoader.item.open()
  }

  function close() {
    if (panelLoader.item) panelLoader.item.close()
  }

  function toggle() {
    if (panelLoader.item) panelLoader.item.toggle()
  }

  function closeForPopoutSwitch() {
    if (panelLoader.item) panelLoader.item.closeForPopoutSwitch()
  }

  function injectPanel() {
    if (!panelLoader.item) return
    panelLoader.item.bar = root.bar
    panelLoader.item.anchorItem = button
    panelLoader.item.hostWidget = root
  }

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  onBarChanged: injectPanel()

  SystemClock {
    id: clock
    precision: SystemClock.Minutes
  }

  Loader {
    id: panelLoader
    active: true
    source: Qt.resolvedUrl("Panel.qml")
    visible: false
    onLoaded: {
      root.injectPanel()
      Qt.callLater(root.injectPanel)
    }
  }

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: Qt.formatTime(clock.date, "HH:mm")
    tooltipText: "Open Custom Clock"
    onPressed: function(buttonCode) {
      if (buttonCode === Qt.LeftButton) root.toggle()
    }
  }
}
```

## Panel.qml

`Panel` provides open state and controller. `KeyboardPanel` anchors to the
bar button. Escape closes through `PanelKeyCatcher`.

```qml
import QtQuick
import Quickshell
import qs.Commons
import qs.Ui

Panel {
  id: root
  moduleName: "yourname.clock"
  manageIpc: false

  property var anchorItem: null
  property var hostWidget: null

  function open() {
    root.controller.show()
  }

  function close() {
    root.controller.hide()
  }

  function switchPanel(direction) {
    if (root.bar && typeof root.bar.switchPanelFrom === "function")
      return root.bar.switchPanelFrom(root.hostWidget || root, direction)
    return false
  }

  SystemClock {
    id: clock
    precision: SystemClock.Minutes
  }

  KeyboardPanel {
    id: panel
    anchorItem: root.anchorItem
    owner: root.hostWidget || root
    bar: root.bar
    open: root.opened
    focusTarget: keyCatcher
    contentWidth: panel.fittedContentWidth(Style.space(240))
    contentHeight: panel.fittedContentHeight(content.implicitHeight)

    PanelKeyCatcher {
      id: keyCatcher
      anchors.fill: parent
      onCloseRequested: root.close()
      onTabRequested: function(direction) { root.switchPanel(direction) }

      Column {
        id: content
        width: parent.width
        spacing: Style.space(8)

        Text {
          width: parent.width
          text: Qt.formatDateTime(clock.date, "dddd, d MMMM yyyy")
          color: root.barForeground
          font.family: root.bar ? root.bar.fontFamily : Style.font.family
          font.pixelSize: Style.font.subtitle
          font.bold: true
          wrapMode: Text.WordWrap
        }

        Text {
          width: parent.width
          text: Qt.formatTime(clock.date, "HH:mm")
          color: root.barForeground
          font.family: root.bar ? root.bar.fontFamily : Style.font.family
          font.pixelSize: Style.font.displayLarge
        }
      }
    }
  }
}
```

Same `moduleName` in both files.

## Validate and inspect

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

omarchy plugin list --json | jq --arg id $PLUGIN_ID '.[] | select(.id == $id)'
omarchy-shell shell summon $PLUGIN_ID '{}'
omarchy-shell shell hide $PLUGIN_ID
```

Before sharing: click, Escape, shell open/close, disable, re-enable, shell
restart, removal.

## Finished example (publish tree)

Replace the clone id with a permanent namespaced id and remove
`omarchy.clonedFrom`. Optional `preview.png` sits beside these files.

### manifest.json

```json
{
  "schemaVersion": 1,
  "id": "io.github.yourname.custom-clock",
  "name": "Custom Clock",
  "version": "1.0.0",
  "author": "Your name",
  "license": "MIT",
  "description": "A small clock with a details panel for the Omarchy bar.",
  "kinds": ["bar-widget"],
  "entryPoints": {
    "barWidget": "BarWidget.qml"
  },
  "barWidget": {
    "displayName": "Custom Clock",
    "category": "Time",
    "allowMultiple": false,
    "defaultSection": "center"
  }
}
```

`BarWidget.qml` / `Panel.qml` are the same as above with
`moduleName: "io.github.yourname.custom-clock"`.

### README.md

Include Install / Usage / Configure / Remove. Install command:

`omarchy plugin add https://github.com/yourname/custom-clock.git --enable`

Configure: `omarchy bar move io.github.yourname.custom-clock --section center`

Remove: `omarchy plugin remove io.github.yourname.custom-clock`

Usage: click the clock to open or close the details panel; Escape closes it.

### LICENSE

If the QML started as an Omarchy clone, keep the upstream copyright and add
the author’s:

```
MIT License

Copyright (c) David Heinemeier Hansson
Copyright (c) 2026 Your name
```

Then the standard MIT permission/warranty paragraphs.
