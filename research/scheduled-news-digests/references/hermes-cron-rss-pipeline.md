# Hermes cron + RSS newsletter pipeline

This reference captures a reusable implementation pattern for Hermes scheduled digests. Adapt paths, sources, and destinations to the active profile; do not copy user IDs or secrets between environments.

## Recommended architecture

```text
RSS/Atom/JSON sources
        |
        v
pre-run collector script
(normalize, filter, dedupe)
        |
        v
compact JSON injected into cron prompt
        |
        v
agent ranks and writes final digest
        |
        v
explicit platform delivery target
        |
        v
saved cron output + delivery status
```

Hermes cron jobs can attach a script whose stdout is injected as context before the agent runs. Use agent mode (`no_agent=false`) when editorial ranking and summarization are required. Use no-agent mode only when the script itself emits the exact final message.

## Collector output contract

Emit one compact JSON object:

```json
{
  "edition": "Morning",
  "generated_at": "ISO-8601 timestamp",
  "window_hours": 14,
  "candidate_count": 2,
  "fetch_errors": [],
  "candidates": [
    {
      "source": "Project blog",
      "title": "Release title",
      "url": "https://example.org/original-item",
      "published": "ISO-8601 timestamp",
      "summary": "Feed-provided factual excerpt",
      "weight": 2.0
    }
  ]
}
```

Keep stdout comfortably below context and tool-output limits. Truncate summaries, cap candidates, and sort before emission.

## RSS/Atom parsing notes

- Identify XML elements by local name (`tag.rsplit('}', 1)[-1]`) to tolerate namespaces.
- RSS normally uses `item`, `pubDate`, and text links; Atom uses `entry`, `updated`/`published`, and `link href`.
- Parse RFC 2822 and ISO-8601 timestamps; convert them to UTC for comparison.
- Strip HTML from feed excerpts and decode entities.
- Canonicalize or compare URLs before deduplication.
- Community aggregate feeds may expose the originating community in a `category` element; preserve it for attribution.

## Deduplication against delivered outputs

For a pragmatic Hermes implementation:

1. Read recent files under the job's cron output directory.
2. Examine only the `## Response` section.
3. Ignore outputs containing the silence sentinel.
4. Extract URLs from actual responses.
5. Exclude those URLs from the next candidate set.

This is superior to marking every collected item as seen because only selected items count as delivered. A more advanced implementation can store selected IDs in a dedicated state file after confirmed delivery.

## Prompt clauses that prevent silent newsletters

Include equivalent requirements:

- Every scheduled edition must return content.
- Never return the silence sentinel for a newsletter.
- Widen the search window from the primary interval to 24 hours, then 48 hours, if necessary.
- If no candidate is verifiable, return a short no-highlights edition.
- Manual runs use a labelled demonstration edition and a 24–48 hour window.
- Use only facts and URLs supplied by the collector unless another tool independently verifies them.

## Troubleshooting “cron says OK but nothing arrived”

Check in this order:

1. List the job and note `last_status`, `last_delivery_error`, and delivery target.
2. Open the newest file in `~/.hermes/cron/output/<job-id>/`.
3. Inspect `## Response`:
   - silence sentinel → delivery was intentionally suppressed;
   - empty response → generation failed or returned nothing;
   - real content → continue to delivery diagnostics.
4. Ensure the route identifies the intended platform/chat/thread.
5. Inspect current gateway/cron error logs for delivery fallback or platform errors.
6. Run the collector directly and validate its JSON.
7. Trigger the job manually and repeat steps 2–5.

Do not tell the user “it was sent” until a real response exists and delivery has no reported error. Phrase uncertainty accurately when only scheduler state is available.

## Rate-limit resilience

- Avoid firing one request per community simultaneously.
- Use supported aggregate feeds to reduce request count.
- Split oversized aggregates into a small number of topical groups only when needed.
- Space grouped requests modestly and continue if one group fails.
- Retain independent technical feeds so partial community-feed failure does not empty the digest.
- Do not encode a transient HTTP error as a permanent assertion that a source is unusable.

## End-to-end acceptance criteria

A newsletter change is complete only when:

- the collector executes successfully;
- its output contains verifiable candidates or an explicit, factual empty result;
- a manual cron run creates a saved output file;
- the saved response is non-empty and not suppressed;
- the destination is explicit;
- no delivery error is recorded;
- ideally, the user confirms receipt.
