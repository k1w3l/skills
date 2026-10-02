# Home Assistant lights fallback

Use this when the user asks to control lights and OpenHue is unavailable or the user's current setup routes smart-home actions through Home Assistant.

## Endpoint and auth

- Prefer the Home Assistant endpoint remembered for the user or provided in the current conversation.
- First verify reachability without credentials:
  - `curl --connect-timeout 2 --max-time 10 -sS -i "$HA_URL/"`
  - `curl --connect-timeout 2 --max-time 10 -sS -i "$HA_URL/api/"`
- Authenticated API calls require:
  - `Authorization: Bearer <LONG_...EN>`
  - `Content-Type: application/json`
- If `/api/states` returns `401 Unauthorized`, ask for a Long-Lived Access Token or a preconfigured local credential.
- Do not save Home Assistant tokens to memory or skills.

## Discover light entities

After auth, list light entities and search for the room/area named by the user:

```bash
curl -sS -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/states" \
| jq -r '.[] | select(.entity_id | startswith("light.")) | [.entity_id, .attributes.friendly_name, .state] | @tsv'
```

If the requested location is ambiguous, prefer matching by friendly name, entity_id, area/group name, or ask a short clarification.

## Turn on a light or group

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"light.office"}' \
  "$HA_URL/api/services/light/turn_on"
```

For several entities:

```json
{"entity_id":["light.office_ceiling","light.office_desk"]}
```

Optional brightness payload:

```json
{"entity_id":"light.office","brightness_pct":100}
```

## Verify

Read back state after the service call:

```bash
curl -sS -H "Authorization: Bearer ***" \
  "$HA_URL/api/states/light.office"
```

Report the actual API result or blocker to the user; never claim the light changed unless the service call or readback confirms it.
