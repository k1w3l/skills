---
name: home-assistant-control
description: "Control Sr. Kiwel's Home Assistant devices through the local REST API: discover entities, call services, handle tokens safely, and verify resulting state."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [smart-home, home-assistant, lights, rest-api, homelab]
    created_by: agent
---

# Home Assistant Control

Use this skill when Sr. Kiwel asks to operate smart-home devices through Home Assistant, especially lights, switches, scenes, rooms/areas, or when a request mentions Home Assistant entities.

## Current local endpoint

- Home Assistant endpoint: `http://192.168.1.47:8123`
- Hermes/J.A.R.V.I.S. is expected to run inside Sr. Kiwel's Proxmox homelab, so reach Home Assistant directly on the LAN; do not use VPN unless the homelab network facts change.
- User-specific discovery notes are in `references/sr-kiwel-home-assistant.md`.
- Battery-sensor scheduled monitoring guidance is in `references/battery-sensor-monitoring.md`.
- Energy-consumption report guidance is in `references/energy-consumption-reporting.md`.

## Security posture

- Do not save Home Assistant tokens in memory, skills, or final replies.
- If no token is available in the live environment, ask Sr. Kiwel for a Long-Lived Access Token or for permission to configure one locally.
- It is acceptable to use a token transiently in the shell environment for the immediate action, but avoid printing it. Secret redaction may mask it in tool output; still be careful.
- Prefer Python `urllib.request` or `curl` with headers over ad-hoc browser automation.

## Ownership boundary for recurring reports

J.A.R.V.I.S. may control Home Assistant devices and inspect state when explicitly asked, but recurring Home Assistant battery/energy reports and infrastructure alerts belong to **Tiberius**. Do not create, resume, edit, run, maintain, or deliver those routines from the default J.A.R.V.I.S. workflow. Route requests for them to Tiberius instead. The personal Samsung Galaxy Watch alert remains a J.A.R.V.I.S. responsibility.

### Ownership handoff procedure

When recurring Home Assistant reporting moves from J.A.R.V.I.S. to Tiberius:

1. Inventory enabled and paused jobs with `hermes cron list --all`, and match exact names/scripts before touching anything; never infer a job ID.
2. Pause only the active J.A.R.V.I.S. jobs with `hermes cron pause <exact-id>`; preserve execution history and reusable scripts unless deletion is explicitly requested.
3. Remove Home Assistant collectors and dashboard attachments from aggregate J.A.R.V.I.S. reports, while retaining explicitly personal-device alerts such as the Galaxy Watch.
4. Re-list the jobs and run unit tests/compilation or another non-delivering verification path; do not manually trigger a Telegram-delivering job merely to test the handoff without authorization.
5. Record the final ownership boundary in the relevant workflow documentation so a later session does not recreate the paused jobs.

## Scheduled monitoring workflow (Tiberius-owned)

Use this section only when operating as Tiberius for recurring Home Assistant monitors, such as battery alerts or daily sensor reports.

1. Scheduled jobs must have durable credentials available to the script, not merely a token pasted in the current chat. Prefer `HASS_URL` and `HASS_TOKEN` environment variables, with `HASS_URL` defaulting to the local endpoint. Never print or save token values in memory/skills/final replies.
2. If a token is known only from a past session or was provided interactively, ask for explicit permission before persisting it into a local secure config/environment file for cron use.
3. Create no-agent cron scripts that print only actionable output for alert jobs; silence means no notification. For daily reports, always print the report.
4. Deliver recurring notifications to Telegram by default for Sr. Kiwel, unless he explicitly chooses another target.
5. Verify against the live `/api/states` endpoint before declaring the monitor complete.
6. For battery sensors, use the filtering details in `references/battery-sensor-monitoring.md`.

## Basic REST workflow

1. Check reachability before assuming credentials are wrong:

   ```bash
   curl --connect-timeout 2 --max-time 10 -sS -i http://192.168.1.47:8123/ | head -20
   ```

   A `200 OK` HTML response means the frontend is reachable. `/api/states` returns `401 Unauthorized` without a bearer token.

2. Discover matching entities by friendly name and entity ID before acting. For Portuguese names, search both accented and unaccented forms plus English fallbacks:

   ```python
   terms = ('escritório', 'escritorio', 'office')
   matches = [s for s in states if s['entity_id'].startswith('light.') and any(t in (s['entity_id'] + ' ' + s.get('attributes', {}).get('friendly_name', '')).lower() for t in terms)]
   ```

3. Call the relevant Home Assistant service with all matched entities when the user's intent is room-level, then verify each state afterward:

   ```python
   import json, os, urllib.request, time

   base = 'http://192.168.1.47:8123'
   token = os.environ['HA_TOKEN']
   headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
   entity_ids = ['light.luzes_escritorio', 'light.luz_escritorio', 'light.luz_escritorio_2']

   data = json.dumps({'entity_id': entity_ids}).encode()
   req = urllib.request.Request(base + '/api/services/light/turn_on', data=data, headers=headers, method='POST')
   with urllib.request.urlopen(req, timeout=10) as r:
       assert r.status == 200
       r.read()

   time.sleep(1)
   for eid in entity_ids:
       req = urllib.request.Request(base + '/api/states/' + eid, headers=headers)
       with urllib.request.urlopen(req, timeout=10) as r:
           print(eid, json.load(r)['state'])
   ```

4. For turning lights off, use `/api/services/light/turn_off` with the same verification step.

## Known office light entities

The office/escritório request matched these Home Assistant light entities:

- `light.luzes_escritorio` — `Luzes Escritório`
- `light.luz_escritorio` — `Luz Escritório`
- `light.luz_escritorio_2` — `Luz Escritório 2`

When Sr. Kiwel says "ligue/desligue as luzes do escritório", target these entities unless discovery shows the entity set changed.

## Scheduled monitoring workflows (Tiberius only)

When Tiberius is operating a durable Home Assistant monitor/alert, prefer a script-only Hermes cron job (`no_agent=True`) that prints only when there is something to notify. Deliver alerts and reports to Telegram by default, per user preference.

J.A.R.V.I.S. must not use these workflows for recurring battery or energy reporting; those jobs are outside its personal-assistant scope.

Telegram notification hygiene: print only the final user-facing alert or report. Do not include internal cron/job identifiers, cron job names, script filenames, “Rotina:” footers, or command suggestions for stopping/managing jobs in Telegram output.

For energy-consumption reports, use `references/energy-consumption-reporting.md`: discover kWh/Wh/MWh energy sensors, compute period consumption from Home Assistant history deltas, split total/general meters from individual meters, estimate cost using the configured tariff, report yesterday daily, and include previous-month closing on the first day of each month.

For physical power attribution on a Proxmox host, use `references/proxmox-power-attribution.md`: correlate the Home Assistant watt sensor with one-minute Proxmox RRD, tasks/journal, disk state and live RAPL; separate baseline hardware draw from workload-driven peaks; report confidence and limitations instead of claiming watts per guest.

For battery monitoring:

1. Use the Home Assistant REST API `/api/states` with `HASS_URL` and `HASS_TOKEN` read from the live environment or `~/.hermes/.env`; never print the token.
2. Match battery entities by `bateria`/`battery` in `entity_id` or `friendly_name`, and also accept `device_class: battery`.
3. Filter out battery-related entities that are not battery level sensors, especially `battery power`, `battery temperature`, `battery state`, `battery health`, `estado da bateria`, and similar non-percentage readings.
4. Maintain an explicit exclusion list for broken/noisy sensors the user names. Current exclusions: any “Temperatura e Umidade Cozinha” battery entity, and any N7 battery entity.
5. Alert only on numeric percentage values at or below the requested threshold. Use a per-entity cooldown/state file so repeated cron checks do not spam while a sensor remains low.
6. Create a separate daily report cron that always prints the current battery table, including unavailable/non-numeric entities in a separate section.
7. Before finalizing, run a real report and a real/`--no-state` alert check against Home Assistant, inspect the output for false positives, then refine filters if needed.

Session-specific implementation notes and the known-good battery monitor shape are in `references/battery-monitoring.md`.

## Reporting format

Keep the final response short and operational:

- Say the action was performed.
- List the verified final state of each affected entity in Portuguese.
- Include the HTTP status only if useful, e.g. `HTTP 200`.
- Do not mention or echo tokens.

## Philips Hue / OpenHue fallback

Prefer Home Assistant for general smart-home requests because it centralizes rooms, scenes, sensors, and verification. Use OpenHue only when the user explicitly asks for Hue/OpenHue or when Home Assistant is unavailable but the Hue bridge is reachable.

Typical OpenHue flow:

```bash
openhue get lights
openhue get rooms
openhue set light <light-id> --on true
openhue set light <light-id> --brightness 80
openhue set room <room-id> --on false
openhue get scenes
openhue activate scene <scene-id>
```

Discovery matters: Hue light/room IDs differ from Home Assistant entity IDs. Verify final state after every command, and if Home Assistant contains Hue-exposed entities, prefer the Home Assistant state as the source of truth. Historical mapping notes can live under `references/home-assistant-lights.md` if needed.

## Pitfalls

- Do not confuse Hue/OpenHue control with Home Assistant control. If the user asks generally for smart-home actions and Home Assistant is configured/reachable, prefer the Home Assistant API.
- A TCP-open port is not enough; verify the Home Assistant frontend and authenticated API separately.
- If a service call fails with `401`, re-check that the exact live token was used; do not persist the token to solve it.
