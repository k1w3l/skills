# Hermes cron watchdog pattern

Session-derived notes for infrastructure/resource monitors implemented as Hermes cron jobs.

## Recommended shape

- Use a deterministic script in `~/.hermes/scripts/`.
- Create the job with `no_agent=true` so the scheduler delivers the script stdout directly.
- Keep the script silent when the system is healthy; empty stdout means no delivery.
- Emit a concise, human-readable alert only when a threshold or condition is met.
- Store minimal local state, if needed, under `~/.hermes/state/` for cooldowns and deduplication.

## Important Hermes cron details

- `script` must be relative to `~/.hermes/scripts/`.
  - Correct: `script="hardware_monitor.py"`
  - Incorrect: `script="/home/kiwel/.hermes/scripts/hardware_monitor.py"`
- Use explicit recurring schedule phrasing.
  - Correct recurring: `schedule="every 5m"`
  - Bare duration: `schedule="5m"` / `"30m"` is interpreted as one-shot unless repeat is set separately.
- For Sr. Kiwel, scheduled alert deliveries should go to Telegram by default: `deliver="telegram"`.
- Verify the created job with `cronjob(action="list")`; check `repeat="forever"`, `deliver`, `script`, and `next_run_at`.

## Hardware monitor script pattern

For CPU/memory/disk threshold alerts:

1. CPU: sample `/proc/stat` twice with a short interval and calculate busy percentage.
2. Memory: use `/proc/meminfo`, preferably `MemAvailable` vs `MemTotal`.
3. Disk: iterate `/proc/mounts`, skip pseudo filesystems, and use `shutil.disk_usage` on real mountpoints.
4. If any metric is above threshold, print one alert with bullet lines.
5. Use cooldown state keyed by alert class (`cpu`, `memory`, `disk`) to avoid repeated notifications while a condition persists.
6. Provide a `--threshold` and `--no-state` option for safe verification without mutating alert state.

## Verification

- Force an alert with a harmless low threshold, e.g. `--threshold 0 --no-state`, to confirm formatting and stdout delivery behavior.
- Run normally once with `--no-state`; healthy systems should produce no output and exit 0.
- Confirm the cron job uses `no_agent=true`; otherwise the LLM may be invoked unnecessarily for a simple threshold alert.
