# Omarchy/Fcitx5 Wayland case

## What was found

The active Quickshell history under `~/.local/state/omarchy/notifications/history/`
retained only the newest ten entries. The remembered Fcitx alert was instead present in
the legacy notification-center archive:

`~/.local/state/omarchy-notification-center/archive.jsonl`

The archive contained 12 records from 2026-09-12 05:04:11 through 2026-09-16
12:52:26 (America/Sao_Paulo), with `app=Fcitx` and `summary=Wayland Diagnose`.

## Exact notification body

> Detect GTK_IM_MODULE being set and Wayland Input method frontend is working. It is recommended to unset GTK_IM_MODULE and use Wayland input method frontend instead.

The wording matters: it confirms that the native Wayland input-method frontend is
working. It is therefore an advisory configuration recommendation, not proof that
Fcitx5 or Wayland is failing.

## Independent checks used

- `omarchy-fcitx5.service` was active and running.
- There was one Fcitx5 process and `fcitx5-remote -n` returned `keyboard-us-intl`.
- The Fcitx5 journal showed native Wayland protocol use and no runtime warning/error.
- `fcitx5-diagnose` exited 0; Qt5/Qt6/GTK3/GTK4 support was present, while Qt4/GTK2
  probe absence was legacy compatibility noise.
- `GTK_IM_MODULE=fcitx` was set by the user's environment override intentionally used
  for GTK support.

## Safe conclusion and authorized A/B test

Do not remove `GTK_IM_MODULE` merely to silence the notification. First classify the
message as advisory and establish that the native Wayland frontend is healthy. If the
operator explicitly authorizes the test, the controlled change for this case is:

1. remove only `GTK_IM_MODULE=fcitx` from
   `~/.config/environment.d/91-input-method.conf`;
2. preserve `QT_IM_MODULE`, `XMODIFIERS`, `SDL_IM_MODULE`, and `GLFW_IM_MODULE`;
3. do not force a logout; let the operator choose a safe time for a fresh login;
4. after login, verify the variable is absent, the `Wayland Diagnose` alert is gone,
   and text entry works in the operator's real GTK, Qt, Electron, and XWayland apps;
5. test the US-International dead-key path and `´c` → `ç`;
6. restore the one removed line if any input workflow regresses.

Do not call a daemon status check or a successful `fcitx5-diagnose` a successful A/B
result. A state-changing `fcitx5-remote` option is never a substitute for focused
text-entry validation.

No credentials, tokens, cookies, or private keys belong in this reference.
