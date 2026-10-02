# Horus API reference

## Connection and authentication

- Base URL: `http://horus.kiwel.home/`.
- Resolve `infra/horus user` and `infra/horus password` from OpenBao with `OPENBAO_ENV=/home/kiwel/.config/openbao/tiberius.env` and `openbao-get`; capture both values in process memory only for `/api/login`, then discard them and use the returned session token.
- The base URL is plain HTTP. Prefer an HTTPS endpoint if one is available; otherwise use it only on the trusted homelab network and treat the login/session credentials as observable to anyone able to inspect that network path.
- A successful HTML response from `/` only proves the web service is reachable. API authentication must be checked separately with `POST /api/login` followed by `GET /api/me`; require the response to identify the expected normal user before monitoring reads. Missing OpenBao fields fail closed and require the operator to create the secret without sending its value in chat.

## Read-only bootstrap

Run these requests before making a health claim:

```bash
HORUS_BASE='http://horus.kiwel.home'

tmpdir=$(mktemp -d)
umask 077
curl --fail-with-body --silent --show-error --max-time 20 \
  -H "Authorization: Bearer ${HORUS_SESSION_TOKEN}" -H 'Accept: application/json' \
  "${HORUS_BASE}/api/me" -o "${tmpdir}/me.json"
curl --fail-with-body --silent --show-error --max-time 20 \
  -H "Authorization: Bearer ${HORUS_SESSION_TOKEN}" -H 'Accept: application/json' \
  "${HORUS_BASE}/api/entities" -o "${tmpdir}/entities.json"
curl --fail-with-body --silent --show-error --max-time 20 \
  -H "Authorization: Bearer ${HORUS_SESSION_TOKEN}" -H 'Accept: application/json' \
  "${HORUS_BASE}/api/alarms/active" -o "${tmpdir}/alarms.json"
```

Use Python or another JSON parser to summarize the files; do not print the authorization header or dump the full inventory into chat. At minimum, validate the response status and report:

- total entities;
- counts by `status`;
- active alarm count;
- all entities whose status is not `running`, including `id`, `integration`, `type`, `name`/`display_name`, `parent_id`, and `last_seen`.

The `/api/me` response is an authentication check. Do not echo token-like fields even if a future deployment adds them.

## Endpoint map

| Endpoint | Method | Use | Boundary |
|---|---:|---|---|
| `/api/login` | POST | Authenticate the dedicated normal Horus user using OpenBao fields | Credentials only from `infra/horus user/password`; never log or echo them |
| `/api/me` | GET | Validate the authenticated normal user | Read-only; require the normal user identity |
| `/api/entities` | GET | List inventory; append a path/filter only when documented by the running UI | Read-only |
| `/api/entities/{id}` | GET | Entity details | Read-only |
| `/api/entities/{id}/latest` | GET | Latest collected state | Read-only |
| `/api/entities/{id}/health` | GET | Last health result | Read-only |
| `/api/entities/{id}/health/run` | POST | Run a Proxmox/system diagnostic and return the result | Diagnostic collection; verify the new `result.ran_at` afterward |
| `/api/entities/{id}/health/config` | PUT | Change diagnostic exclusions or thresholds | **Permission required**; preserve intentional template exclusions |
| `/api/entities/{id}/metrics/{metric}?range={range}` | GET | Time-series metric | Read-only |
| `/api/entities/{id}/logs?since_days={n}&limit={n}` | GET | Entity logs | Read-only |
| `/api/entities/{id}/podlog?tail={n}` | GET | Kubernetes pod log | Read-only, but may expose application secrets; redact before reporting |
| `/api/entities/{id}/ctlog?tail={n}` | GET | Proxmox container log | Read-only, but may expose application secrets; redact before reporting |
| `/api/entities/{id}/boots` | GET | Boot history | Read-only |
| `/api/entities/{id}/backups?since_days={n}&limit={n}` | GET | Backup history | Read-only |
| `/api/alarms/active` | GET | Current alarms | Read-only |
| `/api/alarms/history?range={range}&status={status}` | GET | Alarm history | Read-only |
| `/api/alarms/rules` | GET | List alarm rules | Read-only |
| `/api/alarms/rules` | POST | Create an alarm rule | Standing Horus monitoring authority in this homelab; audit first and verify |
| `/api/alarms/rules/{id}` | PUT | Update an alarm rule | Standing Horus monitoring authority in this homelab; avoid duplicate coverage and verify |
| `/api/alarms/rules/{id}` | DELETE | Delete an alarm rule | **Permission required** unless replacing it atomically with equivalent verified coverage |
| `/api/events/ticket` | POST | Obtain an events ticket for the UI/event stream | Ask if the deployment treats ticket issuance as a stateful operation |
| `/api/entities/{id}/actions` | POST | Submit a control verb with `{ "verb": "...", "params": { ... } }` | **Permission required**; exact verb and target must be approved |
| `/api/entities/{id}/tasks/{task}/status` | GET | Verify an asynchronous task | Read-only verification |
| `/api/entities/{id}/rollout` | POST | Roll out/update an entity | **Permission required**; potentially disruptive |
| `/api/entities/{id}/threshold` | PATCH | Change thresholds | **Permission required** |
| `/api/entities/{id}/mute` | PATCH | Mute/unmute monitoring | **Permission required** |
| `/api/alarms/{id}/ack` | POST | Acknowledge an alarm | **Permission required**; acknowledgement is not remediation |
| `/api/me/prefs` | GET/PUT | Read or save the authenticated user's Home layout/preferences | Normal user session required; verify the readback |

The UI also exposes administrative endpoints for users, tokens, integrations, configuration, and entity metadata. Treat all of them as privileged writes and require explicit approval.

## Parsing and triage notes

- Preserve Horus entity IDs exactly; do not normalize slashes, case, or punctuation.
- Use `last_seen` to distinguish a fresh state from stale inventory. A fresh `stopped` state is different from an entity that has not reported recently.
- Group Kubernetes pods by namespace/workload and inspect owner/job metadata before escalating. Reindex jobs and their historical pods can legitimately be `stopped` or `error` after completion.
- A degraded Kubernetes system pod can represent a readiness or dependency issue even when the container is alive. Drill into health and logs before restarting it.
- An Uptime Kuma monitor in `error` identifies a failed monitor target/check; use the corresponding service/entity data to determine cause.
- Keep a pre-action snapshot of the exact target and a post-action readback. Compare both rather than relying on HTTP 2xx.

## Diagnostics, alarm rules, and Home preferences

- For a Proxmox host, read `/health` and use `result.ran_at`, `result.overall`, `result.categories[*].findings`, `excluded_guests`, and `running`. When a result is stale or requires confirmation, POST `/health/run`, then GET `/health` again; verify the new timestamp and report findings without clearing them.
- Before creating or updating an alarm, read `/api/alarms/rules` and recent `/api/alarms/history`; reuse or widen coverage only when it avoids duplicate firing. For Uptime Kuma, prefer one generic availability rule plus deliberately scoped exceptions; calibrate latency thresholds from observed response-time distribution and duration, not a convenient round number.
- After every rule write, read the exact rule/list and `/api/alarms/active`. The evaluator may retain old firing records until its next cycle; wait for one bounded cycle and re-fetch before acknowledging or deleting anything. Preserve history and fix the rule rather than hiding noise.
- `PUT /api/me/prefs` stores per-user `homeItems`, `homeGroups`, `homeGroupOrder`, and `homeChartRange`; use current `/latest` metric keys for charts/gauges and verify the preference readback. Authenticate through `/api/login` with the OpenBao `infra/horus user` and `infra/horus password` fields; verify the preference readback.

## Service-update diagnostic pattern

When a monitored Python service shows a missing-symbol `ImportError` after an in-place code update:

1. Compare the process start time with the code/update time.
2. Reproduce the import in a fresh process using the service's interpreter.
3. If the fresh import succeeds but the long-lived process fails, suspect stale in-memory modules (`sys.modules`) and mixed code generations.
4. Restart only the affected service after approval; do not patch a correctly updated source file to accommodate an old process.
5. Verify the new process start time, service health, endpoint response, and post-restart logs. Check sibling services separately before restarting them.