# Stalwart email-alert feedback contract

Use this reference when an operator reports an important email alert missing the Telegram feedback keyboard.

## Reproduction and diagnosis

1. Inventory every active Stalwart watcher. Do not inspect only the job named `important`: finance, event/travel, and direct/actionable watchers can all surface potentially important mail.
2. Read the latest cron output and scheduler/gateway logs. A successful/no-agent run with `silent (empty output)` or `[SILENT]` is not proof that a feedback card was delivered.
3. Read recent mail through the Stalwart bridge (`health` plus a bounded `recent` query), never Gmail. Compare each matching message with `~/.hermes/plugins/newsletter-cards/feedback.db`:
   - a row in `email_alerts` means the feedback sender registered the alert;
   - a row without `email_feedback` means no reaction has been recorded yet, not necessarily that the keyboard was absent;
   - a matching message with no `email_alerts` row likely passed through a legacy plain-text route.
4. Inspect the alert implementation, not only job status. The live path is `stalwart_email_routines.py` → `jarvis_email_feedback.send_email_alerts` → Telegram `sendMessage` with `reply_markup`.

## Required implementation

- Every potentially important stream (`finance`, `events`, and `important`) calls `send_email_alerts(..., kind="important")`.
- Each mail item is sent with `email_keyboard(alert_id)`, whose callbacks are `em:p:<id>` and `em:n:<id>`.
- Shared `kind="important"` lets reactions adapt future importance across category boundaries by exact sender, domain, and subject tokens.
- Event/calendar approval may send a separate `ca:y`/`ca:n` message, but it does not replace the email feedback card.
- Never fall back to `format_matches` or another plain-text rendering of email contents during a live alert run. On failure, expose only a technical error; do not silently send an unbuttoned email.
- Persist watcher `seen_ids` only after `send_email_alerts` reports the corresponding `sent_alert_ids`. Keep partial failures eligible for retry.

## Safe verification

Use mocks for Telegram in unit tests and include one test per stream plus a failed-send retry test. A read-only live probe should verify Stalwart `health`, a small JMAP `recent` result, active job state, and the feedback DB without modifying mail or firing a job manually. Do not automatically re-send legacy alerts: old watcher state may have marked an entire window as seen, so first identify the exact messages and get explicit scope before any backfill.
