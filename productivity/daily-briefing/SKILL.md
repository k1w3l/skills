---
name: daily-briefing
description: "Use for compact multi-source daily briefs."
version: 0.1.0
created_by: agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [daily-briefing, digest, telegram, home-assistant, email, calendar, reddit, cron]
    related_skills: [scheduled-news-digests, home-assistant-control, hermes-cron-operations, stalwart-jmap-operations]
---

# Multi-source Daily Briefing

Build one concise, actionable morning briefing from several independent data sources. Use this skill when an operator wants to replace multiple daily reports with a single digest containing operational metrics, exceptions, schedule commitments, messages, and a small number of curated highlights.

## When to use

- A daily morning summary must combine Home Assistant, e-mail, calendar, RSS/Reddit, or similar sources.
- Existing reports are too verbose, list every normal device, or create duplicate notifications.
- The operator requests a fixed local delivery time and a readable message rather than raw tables.

Do not use this skill to replace time-sensitive alerts, incident notifications, low-battery alarms, calendar reminders, or security watchdogs unless the operator explicitly asks for that consolidation too.

## Editorial contract

Before implementation, record:

- name and delivery destination;
- editorial timezone and local delivery time;
- which sections are required and their order;
- time window for each section (`today`, previous civil day, or another explicit range);
- maximum items per section;
- hard message-size limit;
- behavior when a source is empty or unavailable;
- which existing jobs are redundant and which alerts must remain active.

Prefer fewer actionable items over a complete inventory. A good brief answers “what deserves attention today?” rather than “what exists in the system?”.

## Source collection

Keep each source adapter independent and failure-isolated:

1. **Operational state** — query the authoritative local API or service directly, using credentials already available to the scheduler. Never copy secrets into prompts, logs, skills, or the final message.
2. **Historical metrics** — compute deltas from the source history for the requested period. Do not substitute a current cumulative counter for a daily value.
3. **Mail** — use the configured authoritative mailbox source, deduplicate by stable message ID, and summarize only messages matching the established importance rules.
4. **Calendar** — query the source-of-truth calendar for the requested local date. Do not create or modify events as part of a briefing.
5. **Community/news feeds** — use deterministic RSS/Atom/JSON collection, strict date filtering, canonical URLs, and a bounded ranked candidate list before formatting.

If a source fails, preserve the other sections and show a short visible “indisponível” note. Return a non-zero script status when a source failure should be observable by the scheduler; do not silently present a partial brief as complete.

## Time and timezone rules

- Convert the requested local delivery time to the scheduler's timezone rather than changing the host timezone.
- Verify the persisted `next_run_at` after creating or editing the job by converting it back to the editorial timezone.
- Interpret “yesterday” as the previous civil day: local midnight inclusive through the next local midnight exclusive. Never implement it as `now - 24 hours`.
- Keep the agenda on the current local date while energy, mail, and community sections use their explicitly declared historical window.

## Selection and concise presentation

- Batteries: show only critical, attention, or unavailable sensors; omit normal devices and include a count.
- Energy: show total/reference, estimated cost when configured, and only highest/lowest device-level consumers. Distinguish true household totals from device counters whose names happen to contain “total”.
- Mail: show a small number of sender/subject/preview summaries; do not dump message bodies or internal IDs.
- Calendar: show time and title for today's commitments, capped to a readable number.
- Reddit/news: show only the top few technically relevant items with source, concise summary, and canonical link.
- Use plain, scannable headings and one-line bullets. Strip scheduler metadata, debug output, credentials, and unnecessary identifiers.
- Enforce a hard character limit below the platform limit and truncate gracefully with an explicit marker if the source data exceeds it.

See `references/compact-multi-source-daily-brief.md` for a reusable section contract and verification checklist.

## Scheduling and consolidation

1. Validate the renderer locally before changing production schedules.
2. Create the replacement job with an explicit platform target and `no_agent=true` when the script can render the final text deterministically.
3. Pause only the redundant daily report jobs after the replacement job exists and has a valid next run.
4. Leave immediate alerts and reminders active unless explicitly included in the new brief.
5. Do not manually fire an external-delivery job merely to test it unless the operator authorized an immediate test send. Run the renderer directly for content validation.
6. Record which jobs were paused, which were preserved, and whether delivery was generated, scheduler-accepted, platform-accepted, or user-confirmed.

## Verification checklist

- [ ] Each source adapter was exercised with a bounded live or fixture query.
- [ ] Historical sections use strict local civil-day boundaries.
- [ ] Normal devices and low-value items are omitted.
- [ ] Device-level totals are not mistaken for a household total.
- [ ] Deduplication prevents the old report and new brief from both delivering.
- [ ] The final message stays within the hard size limit.
- [ ] A source failure remains visible and affects script status as designed.
- [ ] The cron job is enabled, has an explicit destination, and its next run converts to the requested local time.
- [ ] Existing alert jobs remain enabled and unchanged unless explicitly consolidated.
- [ ] No external test message was sent without authorization.

## Pitfalls

- Treating `last_status: ok` as proof that useful content was generated or delivered.
- Listing every normal sensor or every energy entity in a morning brief.
- Summing several overlapping “total” meters and reporting a false household total.
- Using a rolling 24-hour window for a civil-day report.
- Pausing alerts together with reports and creating an observability gap.
- Running the production delivery job manually during verification and sending a duplicate edition.
- Including raw e-mail bodies, internal IDs, tokens, or scheduler diagnostics in Telegram output.
- Returning a giant partial report when one source is unavailable instead of preserving the compact contract.
