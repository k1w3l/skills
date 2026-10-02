---
name: homelab-alert-monitoring
description: Monitor and analyze homelab alerting/notification systems such as Gotify, Uptime Kuma, Proxmox/PBS, TrueNAS, and other infrastructure notifiers; produce evidence-backed alarm reports and tuning recommendations.
---

# Homelab alert monitoring

Use this skill when the operator asks to log into, monitor, summarize, or tune alarm/notification systems in the homelab — especially Gotify-backed alerts from Uptime Kuma, Proxmox, PBS, TrueNAS, Pulse, Docker tooling, Node-RED, or media-stack services.

## Principles

1. Route notifications according to the operator's default preference.
   - For Sr. Kiwel, assistant-created notifications and scheduled alert deliveries should go to Telegram by default unless he explicitly requests another destination.
   - When creating Hermes cron alerts, set `deliver="telegram"` rather than relying on the origin conversation.

2. Verify the alerting endpoint before claiming access.
   - Check a harmless version/health endpoint when available.
   - Authenticate with the requested account or token only for the specific requested scope.
   - Never print, persist in plain text, or repeat credentials/tokens in the final response.

2. Prefer real data over retrospective assumptions.
   - First query historical messages if the API supports it.
   - If history is empty or retention is disabled, say so plainly and start live monitoring instead of inventing a report.
   - Report the monitoring window, poll interval, process/session id if started, and evidence files used.

3. Preserve raw evidence in a structured file.
   - JSONL is a good default for live alert capture: one message per line.
   - Include timestamp, app/source, priority, title, body/message, and message id.
   - Keep secrets out of the evidence file.

4. Produce actionable tuning recommendations.
   - Group by source application, priority, category, and repeated title/message pattern.
   - Look for flapping: pairs of failure and recovery events close together.
   - Suggest debounce, retries, confirmation windows, priority downgrades, or filtering only when supported by captured data.
   - Distinguish expected informational events, such as successful backup/maintenance, from human-actionable alerts.

## Hermes cron watchdogs

Use Hermes `cronjob` with `no_agent=true` for simple infrastructure watchdogs where a script itself emits the final alert text.

1. Put the script under `~/.hermes/scripts/`.
2. In `cronjob(action="create")`, pass the script path relative to that directory, e.g. `script="hardware_monitor.py"`; absolute or `~/...` script paths are rejected.
3. Use recurring schedules with explicit `every`, e.g. `schedule="every 5m"`. A bare duration like `"5m"` creates a one-shot job.
4. Make the script silent when there is no alert. With `no_agent=true`, empty stdout means no notification; non-empty stdout is delivered verbatim.
5. Add alert cooldown/state inside the script for noisy conditions so persistent incidents do not spam Telegram.
6. After creation, run `cronjob(action="list")` and verify `repeat="forever"`, the expected `deliver` target, and the next run time.

See `references/hermes-cron-watchdogs.md` for a compact pattern and pitfalls.

## Gotify workflow

1. Probe Gotify without exposing secrets:
   - `GET /version` for version/build information.
   - `GET /application` with Basic auth to discover configured applications and their last-used timestamps.

2. Create or reuse a dedicated client for monitoring when message access requires a client token:
   - `GET /client` with Basic auth.
   - `POST /client {"name":"JARVIS Gotify Monitor"}` if no suitable monitoring client exists.
   - Store the client token in a restricted temporary file, mode 0600, and do not print it.

3. Query messages with the client token:
   - `GET /message?limit=200&since=<last_id>` with `X-Gotify-Key: <client_token>`.
   - Track the highest message id seen to avoid duplicates.
   - If `/message` returns an empty list, state that no retained messages were available and run live monitoring for an explicit interval.

4. When starting live monitoring:
   - Use a bounded background process for a requested or sensible default window.
   - Use notify-on-complete for bounded jobs.
   - Keep a poll interval that is polite to the local service, e.g. 10 seconds unless the operator requests otherwise.

## Report shape

Include:

- Monitoring window and timezone.
- Total alerts captured.
- Top alerting sources.
- Top categories or repeated patterns.
- Priority distribution.
- Last few notable alerts.
- Concrete adjustment recommendations, tied to the observed evidence.

If no alerts were captured, say that directly and recommend either a longer window or checking Gotify retention/history settings.

## Pitfalls

- Do not fabricate historical alarm trends when Gotify returns no retained messages.
- Do not confuse application tokens with client tokens; Gotify message listing may require a client token.
- Do not expose Gotify client/application tokens or user passwords in command output, files, or final reports.
- Do not store credentials in persistent memory. Store only stable endpoint facts and the rule to handle credentials carefully.

## Support files

- `templates/gotify_monitor.py`: starter Python monitor for polling Gotify messages and producing a concise alarm report.
- `references/gotify-monitoring.md`: notes on the Gotify live-monitoring pattern and report interpretation.