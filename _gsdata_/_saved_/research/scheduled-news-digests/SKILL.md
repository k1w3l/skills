---
name: scheduled-news-digests
description: "Build, operate, and troubleshoot scheduled newsletters and curated news digests: weighted source lists, RSS/Atom collection, ranking, deduplication, cron delivery, and end-to-end verification. Use when creating recurring news briefings, technology newsletters, feed digests, or when a scheduled digest reports success but no message arrives."
version: 1.1.0
created_by: agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [newsletter, rss, atom, cron, curation, monitoring, telegram]
---

# Scheduled News Digests

Use this skill to build recurring, curated newsletters from preferred sources and to verify that collection, generation, and delivery all work end to end.

## Core principle

A scheduler reporting `ok` proves only that the run completed. A working digest requires three independently verified stages:

1. **Collection:** current, attributable candidates were actually fetched.
2. **Generation:** the final response contains the requested digest rather than an empty response or a silence sentinel.
3. **Delivery:** the destination is concrete and the platform reports no delivery error.

Never claim that a user received a digest merely because the cron run status is `ok`.

## Build workflow

### 1. Capture the editorial contract

Record these explicitly in the job prompt or configuration:

- schedule and timezone;
- maximum items per edition;
- primary topics and exclusion criteria;
- preferred sources and their relative weight;
- freshness window for each edition;
- duplicate/update policy;
- output language and exact item format;
- delivery destination;
- how explicit user feedback changes source weights.

Prefer fewer strong items over padding to a fixed count.

### Closed calendar-day editions

Distinguish a rolling freshness window from a closed civil-date contract. When the user says “only yesterday” or names a calendar date:

- anchor the interval to the editorial timezone, not to `now - 24 hours`;
- calculate local-midnight bounds and compare normalized UTC timestamps with a half-open interval;
- reject undated candidates rather than guessing;
- emit `coverage_timezone`, `covered_date`, `window_start_utc`, and `window_end_utc_exclusive` for the curator;
- explicitly forbid widening the window or substituting items from another date—the general sparse-edition widening rule does not apply;
- if cron runs in a different host timezone, convert the requested local delivery time and verify the saved `next_run_at` back in the editorial timezone.

See `references/calendar-day-editions.md` for collector, Reddit, scheduler, and side-effect-safe verification patterns.

### 2. Separate collection from curation

For durable automation, use a deterministic pre-run collector and let the agent curate its output:

- fetch RSS/Atom or documented JSON endpoints directly;
- normalize source, title, canonical URL, timestamp, and short summary;
- reject malformed entries;
- filter by the edition's freshness window;
- remove URLs already present in prior delivered outputs;
- emit compact JSON for the agent;
- ask the agent to select and summarize only from supplied candidates.

This avoids making the final model discover every source interactively during a short cron run.

### 3. Design resilient source ingestion

- Prefer official RSS/Atom feeds and original project sources.
- Set an honest feed-reader `User-Agent` and finite network timeouts.
- Parse namespaces by local XML tag name so RSS and Atom both work.
- Aggregate compatible community feeds where supported to reduce requests and rate pressure. For Reddit, prefer one multi-subreddit Atom/RSS request over a burst of per-subreddit requests.
- For rate-limited feeds, persist the last successfully normalized batch with a short expiry. A cached batch is only a degradation fallback: still apply the normal freshness window and delivered-URL filter, and disclose cache use to the curator.
- Treat individual source failures as partial degradation; continue with healthy sources.
- Keep a diverse secondary source pool so one outage does not empty the edition.
- When several digests share a delivery plugin, deduplicate against one shared registry of URLs actually delivered—not merely each job's output files. Mark only sent items as delivered; rejected candidates may remain eligible until stale.
- Never fabricate a missing URL, title, date, or fact.

Do not persist a blanket claim that a source or tool is broken. Record the resilient fallback order instead.

### 4. Make silence semantics explicit

Alert/watchdog jobs often should remain silent when nothing changes; newsletters usually should not.

For ordinary rolling-window newsletters, state in the prompt:

- never return the scheduler's silence sentinel unless the editorial contract explicitly permits an empty edition;
- widen the freshness window progressively when the primary window is sparse;
- if no verifiable item exists, send a short “no verified highlights” edition rather than suppressing delivery;
- manual test runs should produce a clearly labelled demonstration edition.

A strict calendar-date contract overrides the widening rule: never pull from another date merely to fill an edition. Follow the operator's chosen empty-edition policy (`[SILENT]` or a no-highlights notice) without fabricating or broadening. Also avoid a manual full-job run when its direct card tool would send an unrequested extra edition; validate the collector and saved schedule instead, unless the operator authorized a demonstration send.

### 5. Use explicit delivery routing

When possible, store a concrete platform/chat/thread target instead of relying on an ambiguous default route. Preserve thread IDs on thread-capable platforms. Do not expose tokens or credentials in prompts, logs, or reports.

## Ranking model

A simple explainable score is usually sufficient:

- source preference weight;
- topical relevance;
- recency;
- primary-source bonus;
- practical impact/security/release bonus;
- duplicate, rumor, clickbait, or low-substance penalty;
- diversity adjustment to prevent one source from dominating.

For community posts, consider technical substance and discussion quality, not votes alone.

## Professional presentation and interactive cards

Treat legibility and visual hierarchy as part of the editorial contract, not cosmetic follow-up. When the destination supports rich messages and the user wants a professional newsletter:

- send a compact edition header;
- render each article as its own card rather than one dense text block;
- include a relevant 16:9 thumbnail for every item;
- use the source image when available and a branded fallback when it is not;
- keep title, factual summary, source, and article link visually distinct;
- treat a separate “why it matters” block as optional, never as a universal requirement;
- place per-article feedback controls immediately below that article.

### Sr. Kiwel's newsletter presentation contract

For the technology newsletter and Status R:

- omit the “Por que importa” section entirely and do not require or request a `why` field;
- use a somewhat fuller factual summary: normally three contextualized, scannable sentences and roughly 60–90 words when the supplied candidate contains enough evidence;
- when source data is sparse, shorten the summary instead of inferring or padding;
- preserve the source line, article link, thumbnail, and per-item 👍/👎 controls.

For Telegram, a multi-card newsletter usually needs a dedicated delivery tool: ordinary cron final-response delivery cannot attach one photo and one inline keyboard to every article. The tool should send each card with `sendPhoto`, a concise HTML caption, `👍/👎` callback buttons, and a URL button. Set ordinary cron delivery to local/suppressed only after the direct card tool has confirmed success, so the user does not receive a duplicate plain-text newsletter.

## Feedback adaptation

Only treat explicit feedback as preference evidence. Typed feedback and button taps are both explicit signals. Examples:

- “I liked this source” or `👍` → increase its source/topic weight softly;
- “less content like this” or `👎` → add a topical or source penalty;
- repeated approval of a new source → promote it to the preferred pool.

A single click may influence the next edition immediately, but should remain a soft signal rather than a permanent source ban. Repeated patterns deserve greater weight. Do not infer preference from absence of complaint or incidental mention.

Persist ratings by stable article ID and user, preferably in SQLite. Feed compact source scores and recent rated titles back into the collector/curator on every run. The callback should acknowledge the tap and visibly mark the selected button so the user knows the rating was saved.

## Verification checklist

After creating or changing a digest:

1. Run the collector directly and verify non-empty, parseable output.
2. Confirm candidate count, timestamps, source diversity, real URLs, and injected feedback context.
3. Trigger the scheduled job manually through a fresh process when tools/plugins were enabled during the current session **and an immediate test delivery is authorized**. For direct-card jobs, otherwise validate collector output, prompt guards, schedule, enabled state, and local conversion of `next_run_at` without sending an extra edition.
4. Read the saved cron output and inspect the actual `Response` section and tool-call result.
5. For text delivery, confirm the response is neither empty nor a silence sentinel.
6. For direct rich-card delivery, confirm the card tool reported sent items before allowing a silence sentinel to suppress duplicate text.
7. Check the job's routing and platform errors.
8. Verify sent article rows exist in the feedback store.
9. Exercise a callback: rating persisted, keyboard changed, and callback answered.
10. Report precisely what is proven: generated, tool-sent, platform-accepted, callback-tested, or user-confirmed.

## Common pitfalls

- Treating `last_status: ok` as proof of content or receipt.
- Testing a newsletter with the same narrow window used at scheduled times, yielding no demonstration content.
- Depending on interactive web search during a short cron run when direct feeds are available.
- Assuming a newly enabled plugin tool is visible to an already-running agent process; use a fresh process or restarted gateway.
- Returning a silence sentinel before a direct card-delivery tool confirms success.
- Sending a dense plain-text digest when the requested destination supports thumbnails and per-item actions.
- Creating callback buttons without a registered handler or durable feedback store.
- Marking all fetched candidates as “sent,” which suppresses items the curator never selected.
- Querying many community feeds in a burst and triggering rate limits.
- Omitting source attribution or linking to an aggregator instead of the original item.
- Adding source-learning logic without a durable place to store learned weights.

## Supporting references

- `references/hermes-cron-rss-pipeline.md` — Hermes-oriented collection, cron, and delivery troubleshooting.
- `references/calendar-day-editions.md` — exact prior-day bounds, scheduler timezone conversion, low-request Reddit collection, and verification without an unwanted send.
- `references/telegram-newsletter-cards.md` — professional Telegram cards, thumbnails, plugin delivery, persistent 👍/👎 callbacks, and verification.
