# Progressive battery threshold alerts

Use this reference when one Home Assistant battery entity needs staged alerts such as 30%, 20%, 10%, and 5%.

## Contract

1. Verify the exact entity and current state before creating the watcher. Use a direct authenticated state request when only one entity is needed.
2. Define thresholds explicitly and compare numeric values with `<=` so the exact threshold is included. A sensible polling interval is 10 minutes when the user did not specify one.
3. Persist a small per-entity state file containing the notified thresholds, last value, active-cycle flag, and update time.
4. During a discharge cycle, emit each threshold at most once. If polling skips several thresholds, report the newly reached thresholds together rather than repeating them on every run.
5. When the value rises above the highest threshold, clear the notified-threshold set so the next discharge starts a new cycle. Unknown/unavailable/non-numeric states should be silent and must not reset the cycle.
6. Keep the output Telegram-ready: device name, current percentage, newly reached threshold(s), and one short action recommendation. No cron IDs, file paths, debug details, or credentials.
7. If a generic battery monitor also matches the entity, add an exact exclusion there so the dedicated watcher is the sole owner and does not duplicate the lowest-level alert.

## Verification

- Unit-test one descending sequence, repeated polling at the same value, recharge/reset, malformed state, and generic-monitor exclusion.
- Run the watcher once against the live Home Assistant entity. A healthy value above the first threshold must produce no output and exit zero.
- Do not force a low value in Home Assistant and do not send a real Telegram test unless the operator explicitly authorizes it; test rendering and delivery with mocks.
- Verify the scheduled job is enabled, uses the intended Telegram route, and that only one job targets the entity.

## Example state shape

```json
{
  "entity_id": "sensor.example_battery_level",
  "notified_thresholds": [30, 20],
  "last_value": 18,
  "active": true,
  "updated_at": "<UTC timestamp>"
}
```
