# Hermes newsletter recovery and same-day manual editions

Use this reference when a scheduled newsletter stops arriving after a Hermes/core/plugin update, or when the operator explicitly requests an edition covering the current day immediately.

## Recovery checklist

1. Inspect `~/.hermes/logs/errors.log` and `agent.log` for the exact scheduler error. Do not infer failure from `last_status: error` alone.
2. Compare a fresh-process import of the current registry and plugin with the error. If the error names a symbol that exists in the current source, the long-lived gateway likely retained an old imported module after an update.
3. Restart the gateway or use a fresh Hermes process before editing prompts, collectors, schedules, or plugin code.
4. Verify all three layers:
   - `hermes tools list` exposes `newsletter_cards`;
   - a fresh `model_tools` import exposes `send_newsletter_cards`;
   - no new matching import/scheduler errors appear after the reload.
5. Run each collector through its interpreter, not by assuming the script has an executable bit. Confirm parseable JSON, non-zero candidate count when expected, date bounds, real URLs, source diversity, and fetch errors.
6. Keep direct-card cron jobs on `deliver: local`. The card tool sends the Telegram messages; ordinary cron delivery is suppressed to prevent a duplicate plain-text edition.
7. Treat pre-reload errors as historical. Wait for the next scheduled run unless the operator explicitly authorizes an immediate send.

## One-off current-day edition

The recurring Status R contract can remain “previous civil day only” while a manual request temporarily covers today:

1. Resolve the editorial timezone and current time with a live system lookup.
2. Build a half-open interval `[today's local midnight, now)` and convert bounds to UTC for comparison. Reject undated entries and never use a rolling 24-hour window or future timestamps.
3. Reuse the aggregate multi-community Reddit Atom/RSS request and existing relevance/deduplication rules, but apply the one-off current-day bounds in memory. Do not modify the recurring collector or cron schedule.
4. Curate only sufficiently substantive, factual candidates. Send fewer cards rather than padding with jokes, generic questions, shopping posts, or weakly relevant material.
5. After explicit authorization, call `send_newsletter_cards` directly instead of triggering the entire cron job when that would create a duplicate run. Omit the `why` field for Sr. Kiwel's newsletters and use concise factual summaries.
6. Verify the tool result (`sent` count and `errors` list), then query the feedback store to confirm rows for the selected URLs. Report Telegram/API acceptance separately from user-confirmed receipt.

The same-day override is a delivery exception only; the next scheduled edition must return to the normal previous-day contract.
