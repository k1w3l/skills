# Telegram report delivery

Use this reference when a Tiberius report is delivered directly through the Telegram Bot API or when a scheduled report has a size/delivery failure.

## Contract

- Render the report completely before measuring it. Count the final HTML payload in UTF-16 code units because Telegram's text cap is 4,096 units, not Python code points.
- Keep a conservative per-body budget below the platform cap to reserve continuation labels and formatting overhead. The current Tiberius delivery path uses 3,900 units before adding a part label.
- Split at semantic line or block boundaries first; split an individual long line only as a last resort. Every resulting payload must be independently valid HTML and must pass the hard limit check before any network call.
- Send one logical report as ordered chunks. Attach feedback controls only to the final chunk so a multi-part report still produces one feedback decision.
- Keep scheduled-report formatting separate from remediation controls: feedback evaluates presentation and never authorizes infrastructure changes.

## Procedure

1. Inspect scheduler state with `hermes -p tiberius cron list`, `cron status`, and `cron doctor`. Read the target job's last status/error and distinguish a historical failure from a new run.
2. Test the shared renderer, not each producer separately. All producers should call the common delivery helper; do not add ad-hoc truncation to a daily report, watchdog, or Home Assistant report.
3. Validate the final rendered payload with a mocked transport or silent dry run. Assert the chunk count, UTF-16 length of every chunk, valid markup, ordered parts, and feedback markup only on the final chunk.
4. Run the focused regression tests and Python compilation for the shared helper plus its report producers. Keep credentials and real chat identifiers out of fixtures and output.
5. Do not clear scheduler history or send a real full-status test merely to make `cron doctor` green. After changing the renderer, wait for the next scheduled run and verify provider acceptance (`ok` and `message_id`) plus the job readback.
6. Report validation honestly: code/tests prove the renderer; a successful provider response proves delivery; a stale scheduler error remains historical until a new run replaces it.

## Tiberius validation pattern

From the report script directory, use the focused suite and compilation checks:

```bash
PYTHONPATH=/home/kiwel/.hermes/profiles/tiberius/scripts \
  python3 -m unittest test_report_delivery.py test_horus_monitoring.py
python3 -m py_compile tiberius_report_delivery.py horus_common.py horus_status.py horus_daily.py horus_recurrence.py horus_watchdog.py
```

For local size fixtures, exercise both many-line reports and a single overlong line. A passing fixture has no payload above 4,096 UTF-16 units. Do not substitute a real Telegram send for this test.

## Alarm controls in Telegram reports

- Pass sanitized active-alarm rows to the common delivery helper; it derives stable short control IDs and persists only operational metadata in the shared `newsletter-cards` SQLite database.
- Put `🔕 Silenciar` and `⚙️ Threshold` on the final chunk only. Preserve these rows whenever a feedback callback rebuilds the report markup.
- Guard callbacks by authorized user and chat, accept only a short hexadecimal control ID, and validate every threshold value against server-generated options. Never place credentials or arbitrary infrastructure identifiers in `callback_data`.
- Mute is entity-scoped (`PATCH /api/entities/{entity_id}/mute`) and must be read back. Resource thresholds use `PATCH /api/entities/{entity_id}/threshold`; generic rules use a full `PUT /api/alarms/rules/{rule_id}` payload; health thresholds use `PUT /api/entities/{entity_id}/health/config`. Read back the exact target after every write.
- Do not show threshold controls for binary/connectivity alarms. Treat the gateway restart needed to load callback code as a separate availability change requiring an explicit window.

## Pitfalls

- Measure after escaping and markup conversion; source Markdown length underestimates the payload because HTML tags and entities add characters.
- Measure UTF-16 units; emoji and other astral characters cost two units even when Python's `len()` reports one.
- Do not put feedback keyboards on every chunk; that duplicates the user decision surface.
- Do not infer successful delivery from empty stdout, a successful script exit, or a scheduler dispatch. Read the provider response and exact job state back.
- Do not change the Horus endpoint while fixing message size. Verify the operational base URL independently and keep externally published Pangolin URLs distinct from the internal collection URL.
