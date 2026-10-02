# Sr. Kiwel Home Assistant notes

These notes capture current, user-specific Home Assistant control details for future smart-home actions.

## Endpoint and network

- Endpoint: `http://192.168.1.47:8123`
- Hermes runs inside the Proxmox homelab VM environment, so Home Assistant should be reachable directly on the LAN.
- `/` returned Home Assistant HTML with `HTTP 200 OK`.
- `/api/states` without bearer auth returned `401 Unauthorized`, as expected.

## Office lights discovery

A scan of authenticated `/api/states` for light entities containing `escritório`, `escritorio`, or `office` returned:

- `light.luzes_escritorio` — friendly name `Luzes Escritório`
- `light.luz_escritorio` — friendly name `Luz Escritório`
- `light.luz_escritorio_2` — friendly name `Luz Escritório 2`

Both `light.turn_on` and `light.turn_off` service calls succeeded with `HTTP 200`, and state verification confirmed `on`/`off` afterward.

## Token handling

Sr. Kiwel may provide a Long-Lived Access Token interactively. Use it only for the immediate request unless he explicitly asks to configure persistent credentials. Never store or echo it in memory, skills, or final replies.
