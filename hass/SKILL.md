---
name: hass
description: >
  Home Assistant access for the homelab instance. Use whenever collecting state,
  calling services, inspecting entities/automations, or performing any action
  against Home Assistant / HA / hass. Always load this skill before API calls.
  Triggers: home assistant, hass, ha, entities, automations, lights, sensors,
  climate, switches, REST API, long-lived token, 192.168.1.47, :8123.
---

# Home Assistant (hass)

**Load this skill before any Home Assistant access** — info gathering or actions.

## Connection

| Field | Value |
|-------|-------|
| Base URL | `http://192.168.1.47:8123` |
| Auth | Long-lived access token (Bearer) |

```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzZmFlNjNiM2QzYzM0Y2M2ODhkN2Y1NmRhNzhmYWMzNyIsImlhdCI6MTc4NTg5NzA3MCwiZXhwIjoyMTAxMjU3MDcwfQ.iN5C9P8GXYwElxqaZn4FRrL7ecURq1phYZk8RX8Dlq8
```

Do not invent or substitute credentials. Do not print the full token in user-facing replies unless the user asks for it.

## Auth header

```
Authorization: Bearer <token>
Content-Type: application/json
```

## Quick API (curl)

Prefer fish-compatible one-liners when showing commands to the user.

```fish
set -x HASS_URL http://192.168.1.47:8123
set -x HASS_TOKEN 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzZmFlNjNiM2QzYzM0Y2M2ODhkN2Y1NmRhNzhmYWMzNyIsImlhdCI6MTc4NTg5NzA3MCwiZXhwIjoyMTAxMjU3MDcwfQ.iN5C9P8GXYwElxqaZn4FRrL7ecURq1phYZk8RX8Dlq8'

# API OK?
curl -sS -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/"

# All states
curl -sS -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states"

# One entity
curl -sS -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states/light.sala"

# Call a service
curl -sS -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"light.sala"}' \
  "$HASS_URL/api/services/light/turn_on"
```

## Common endpoints

| Method | Path | Use |
|--------|------|-----|
| GET | `/api/` | Connectivity check |
| GET | `/api/config` | Instance config |
| GET | `/api/states` | All entity states |
| GET | `/api/states/<entity_id>` | One entity |
| POST | `/api/states/<entity_id>` | Set state (usually prefer services) |
| POST | `/api/services/<domain>/<service>` | Call service (body JSON) |
| GET | `/api/services` | List services |
| GET | `/api/events` | List events |
| GET | `/api/error_log` | Error log |
| GET | `/api/history/period/<timestamp>` | History |
| GET | `/api/calendars` | Calendars |
| GET | `/api/template` | Render template (POST with `{"template":"..."}`) |

## Agent workflow

1. Read this skill (credentials + base URL).
2. Prefer REST API via `curl` against `http://192.168.1.47:8123`.
3. For destructive or broad changes (many entities, restarts, deletions), confirm with the user first.
4. Summarize results in plain language; keep the token out of normal chat output.

## Notes

- Instance is LAN-only at `192.168.1.47:8123` (HTTP).
- Token is a Home Assistant long-lived access token.
- If auth fails (401/403), ask the user to rotate/create a new token in HA → Profile → Long-lived access tokens, then update this skill.
