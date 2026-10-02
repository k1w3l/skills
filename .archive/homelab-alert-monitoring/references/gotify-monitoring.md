# Gotify monitoring notes

Use this reference when the operator asks for a report on what alarmed most in Gotify or whether alert rules should be adjusted.

## Observed durable pattern

Gotify can have configured applications with recent `lastUsed` timestamps while the message listing endpoint returns no retained messages. In that case, the correct response is not a retrospective trend report; start a live monitoring window and base the report on captured messages.

## Useful API calls

- `GET /version` — confirms Gotify is reachable and returns version/build.
- `GET /application` with Basic auth — lists applications, default priorities, and last-used timestamps.
- `GET /client` with Basic auth — lists clients.
- `POST /client {"name":"JARVIS Gotify Monitor"}` with Basic auth — creates a monitoring client.
- `GET /message?limit=200&since=<id>` with `X-Gotify-Key: <client token>` — lists messages available to that client.

## Security notes

- Mask application tokens when displaying application lists.
- Keep client tokens in a chmod 0600 temp/cache file if a background monitor needs them.
- Never include the operator's Gotify password or tokens in the final report.

## Analysis categories

Common homelab alert categories:

- `falha/indisponibilidade`: down, offline, unreachable, timeout, failed, error, critical, alert.
- `recuperação/normalização`: up, online, resolved, recovered, success, ok.
- `backup/manutenção`: backup, PBS, prune, garbage collection, GC.
- `mudança/atualização`: update, upgrade, change-detection events.
- `recurso/infraestrutura`: disk, ZFS, pool, SMART, memory, CPU, temperature.

## Recommendation heuristics

- Many failure/recovery pairs close together: likely flapping; suggest debounce, more retries, or a longer confirmation window in the source system.
- High-priority success/maintenance events: suggest lowering priority if no human action is required.
- One source dominates alert volume: tune that source first.
- Empty capture window: recommend a longer monitoring window or review Gotify retention/history settings.