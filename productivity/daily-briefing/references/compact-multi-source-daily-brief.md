# Compact multi-source daily brief reference

Use this reference to implement a small, operational morning digest without turning it into a raw dashboard export.

## Recommended contract

```text
DAILY BRIEF — local date

BATTERIES
  only critical / attention / unavailable, with a count
ENERGY — previous civil day
  total or clearly named reference, estimated cost, top consumers, bottom consumers
MAIL — previous civil day
  a few important sender + subject + actionable preview lines
CALENDAR — today
  time + commitment, capped
COMMUNITY / REDDIT — previous civil day
  at most three high-signal links with source and one-line context
```

Set a hard output bound below the destination platform limit (for Telegram, leave margin below 4096 characters). If the result exceeds the bound, truncate at a safe boundary and append an explicit “resumo encurtado” marker.

## Temporal contract

Choose one editorial timezone and calculate the prior-day interval as:

- start: local midnight of yesterday, inclusive;
- end: local midnight of today, exclusive.

Convert those boundaries to UTC only for APIs that require it. Agenda queries should target today's local date. Never use a rolling 24-hour window for a civil-day report.

## Source-specific rules

- Home Assistant battery states: list only values needing attention. Exclude normal readings and non-level battery entities; include unavailable sensors only when their lack of reading is actionable.
- Home Assistant energy: obtain history deltas and convert Wh/kWh/MWh. A device meter often ends in a word such as “total”; determine whether the label describes a device's cumulative counter or the household total before aggregating.
- Stalwart/JMAP mail: query the authoritative mailbox, use the existing importance predicates and feedback, deduplicate by stable message ID, and limit summaries. Do not fall back to Gmail implicitly.
- Stalwart calendar: read today's events only. A briefing must never create, alter, or approve an event.
- Reddit/RSS: collect deterministic candidates, reject undated/out-of-window items, retain canonical URLs, rank by source/relevance/recency, and show only the top few. A cache may be used as a disclosed degradation fallback while preserving the same date filter.

## Scheduling consolidation

Create the new replacement job before pausing old reports. Convert a requested local time to the scheduler timezone and verify `next_run_at` back in local time. Pause only reports that are now represented by the brief; preserve real-time alerts, alarms, reminders, and unrelated newsletters unless the operator explicitly includes them.

Do not manually trigger a job with external delivery merely to test the renderer. Run the renderer directly, validate the output and live source calls, and report that first production delivery remains pending until the scheduled run.

## Verification checklist

1. Run each collector with a bounded live or fixture input.
2. Assert prior-day data is inside the half-open local-date interval.
3. Assert normal batteries and low-signal community items are absent.
4. Assert device-level energy counters are not summed as overlapping household totals.
5. Assert duplicate legacy jobs are paused and required alerts remain enabled.
6. Assert the rendered message length is within the hard bound.
7. Run tests with the project's official interpreter, not an unrelated system Python.
8. Confirm the cron job is enabled, routes to the intended platform, and its next run is the requested local time.
9. Distinguish generated, scheduler-accepted, platform-accepted, and user-confirmed delivery.
