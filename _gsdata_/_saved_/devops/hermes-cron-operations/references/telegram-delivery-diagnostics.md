# Telegram delivery diagnostics

Use this reference when a Hermes cron job appears to stop delivering to Telegram or reports a platform error.

## Evidence order

1. List the exact profile's jobs, including disabled jobs, and record job ID, script, `no_agent`, delivery target, last status, failure streak, next run, and last error.
2. Read the newest saved output for the job and the matching scheduler, agent, gateway, and error-log entries. Keep collection/generation, script-side Bot API calls, Hermes adapter delivery, and fallback delivery as separate stages.
3. Check the gateway service with `systemctl --user is-active hermes-gateway.service` and a full status view. A running service only proves the process exists; it does not prove platform acceptance.
4. For Telegram, inspect recent logs for content rejection (`too long`, parse/entity errors), transport failure (`ConnectTimeout`, `ConnectError`, `Bad Gateway`, degraded polling, reconnect), and authentication/target failure (`401`, `403`, `Chat not found`).
5. Perform a bounded no-token network probe without sending a message:

```text
curl -4 -sS -o /dev/null --connect-timeout 5 --max-time 15 \
  -w 'http=%{http_code} remote=%{remote_ip} total=%{time_total}s\n' \
  https://api.telegram.org/
curl -6 -sS -o /dev/null --connect-timeout 5 --max-time 15 \
  -w 'http=%{http_code} remote=%{remote_ip} total=%{time_total}s\n' \
  https://api.telegram.org/
```

An HTTP response from the endpoint demonstrates reachability only; it is not proof that the bot token, chat target, or `sendMessage` call succeeded. Compare it with the gateway timestamps because intermittent paths can pass a probe while the adapter is reconnecting.

## Payload and fallback checks

- When the producer supports dry-run, enable it and direct any state/cache path to a temporary file. Capture the exact post-rendering body and count characters/bytes without displaying the body in the report.
- Measure after HTML/Markdown escaping because entity expansion changes the size and malformed markup can cause a second failure in the fallback path.
- Chunk long messages on semantic/newline boundaries below the platform limit; validate each chunk's markup independently. Put inline keyboards or feedback controls on the final chunk unless the interaction contract explicitly requires otherwise.
- If a job both sends through its script and declares `deliver=telegram`, map both paths before modifying either one. Do not manually run the job merely to test delivery, because the direct script or scheduler fallback may send an unrequested duplicate.
- A timeout after a platform call is ambiguous: preserve retryability, but reconcile whether the platform accepted the request before blindly retrying.

## Reporting standard

State separately what was collected, generated, script-sent, adapter-sent, platform-accepted, and user-confirmed. Never call a job delivered solely because the gateway is active, the script exited zero, stdout was non-empty, or the scheduler says `ok`. Delete temporary payload/state files after the probe and never print tokens, full secret configuration, or unnecessary message bodies.
