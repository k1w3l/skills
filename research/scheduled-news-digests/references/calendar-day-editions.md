# Closed calendar-day newsletter editions

Use this pattern when an edition must cover a named civil date such as “yesterday,” rather than a rolling freshness interval.

## Temporal contract

1. Choose the editorial timezone explicitly (for example, `America/Sao_Paulo`).
2. Compute the previous local date from a timezone-aware `now`.
3. Construct local midnight at the start of that date and local midnight at the start of the following date.
4. Convert both boundaries to UTC for source comparison.
5. Accept only timestamps in the half-open interval `start_utc <= published < end_utc`.
6. Reject undated entries: they cannot be proven to belong to the requested date.
7. Emit the contract with the collector output, preferably as:
   - `coverage_timezone`
   - `covered_date`
   - `window_start_utc`
   - `window_end_utc_exclusive`
8. Repeat the strict window rule in the curation prompt. Prohibit widening, extra discovery, and substitution from other dates.

Do not implement “yesterday” as `now - 24 hours`. A rolling interval crosses two civil dates and behaves incorrectly around timezone offsets and daylight-saving transitions.

## Scheduler timezone

Hermes cron expressions follow the scheduler host timezone. If the desired editorial time is local but the host runs UTC:

- convert the desired local hour to the host timezone when writing the cron expression;
- inspect the saved `next_run_at` value;
- convert `next_run_at` back to the editorial timezone and assert that its local hour matches the request.

Avoid changing the host timezone merely to accommodate one newsletter, since that affects unrelated jobs.

## Reddit collection for a prior-day edition

A once-daily run against a busy multi-subreddit `/new` feed may expose only the most recent entries and omit much of the prior day. A resilient low-request pattern is:

- make one multi-subreddit Atom/RSS request to `top/.rss?t=week&limit=100`;
- apply relevance filtering and then the exact local-calendar-day bounds;
- keep a short normalized cache as a degradation fallback;
- deduplicate only after combining live/cache candidates;
- use one aggregate request where anonymous Reddit rate limits reject bursts of grouped requests.

The wider upstream query is only a collection mechanism. The delivered edition remains strict because every candidate is filtered through the closed `covered_date` interval before curation.

## Verification without an unwanted extra edition

For direct rich-card jobs, a manual cron run may send a real newsletter immediately. Unless the operator requested a demonstration delivery:

1. compile/lint the collectors;
2. run each collector directly;
3. parse its JSON and assert every candidate is inside the emitted half-open window;
4. verify a non-error live fetch or an explicitly disclosed cache fallback;
5. inspect the stored cron expression, prompt guards, enabled state, and `next_run_at` converted to local time;
6. do not trigger the full card-sending job merely for verification; report that delivery was intentionally deferred to the next scheduled edition.

A manual end-to-end run remains appropriate when the user explicitly asks for a test edition or authorizes an immediate send.