---
name: notification-delivery-reliability
description: "Use when jobs can duplicate alerts. Enforce one delivery."
version: 1.0.0
created_by: agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [notifications, idempotency, deduplication, retries, telegram, cron, workers]
---

# Notification Delivery Reliability

Use this class-level skill when several scheduled jobs, collectors, categories, workers, or
channels can surface the same logical event and the operator requires exactly one external
notification per item. It owns delivery idempotency and retry semantics; domain skills own
message classification, source access, and action-specific approval gates.

## Core invariants

1. One logical source item produces at most one user-facing notification in the shared delivery
   scope.
2. The deduplication key is stable and source-derived, preferably a namespace plus the source's
   immutable item ID. Do not use subject text, timestamps, or a per-job state file as the only key.
3. Claim the key atomically in durable storage before sending either a batch header or an item
   payload. Only the claim owner may send.
4. Track delivery state explicitly (`pending`, `sending`, `sent`, and, when useful, a retryable
   failure state). A successful response from the external platform is the transition to `sent`.
5. A duplicate that is already `sent` must suppress both its item notification and any header
   that would announce it. Do not send a header for an empty post-deduplication batch.
6. Mark a worker's local `seen` state only after the item is confirmed sent or the shared ledger
   confirms it was already sent by another worker. Leave failed items eligible for retry.
7. If a notification requires feedback buttons, approval controls, or another actionable UI,
   never fall back to a plain-text rendering of the same item when delivery of that UI fails.
   Emit only a technical error and preserve retryability.

## Delivery protocol

1. Inventory every producer that can emit the logical event; do not assume the job named after
   the event is the only producer.
2. Normalize the source identity and choose one shared namespace. For a source with an immutable
   ID, use a key such as `source-kind:item-id`; share it across category-specific watchers.
3. Register the item metadata without secrets or full sensitive content.
4. Atomically claim delivery before reading configuration for, or sending, the batch header:

```text
BEGIN IMMEDIATE
row = lookup(key)
if row.status == sent: return SKIP_ALREADY_SENT
if row.status == sending and claim_is_fresh: return SKIP_IN_FLIGHT
UPDATE row SET status=sending, claimed_at=now WHERE status=pending OR claim_is_stale
COMMIT
```

5. Build the batch only from successfully claimed items. Send one header, then one actionable
   item notification per claim.
6. On each confirmed item send, set `sent_at`/`status=sent`. On a failed item send, release the
   claim and do not mark the source item seen. Partial batches must retry only the unresolved
   items.
7. Return explicit sets such as `sent_keys`, `skipped_keys`, and `handled_keys` so producer
   state can distinguish delivered, deduplicated, and failed items.

## Concurrency and stale claims

- Use a database transaction or an equivalent compare-and-set primitive; a read followed by a
  write without an atomic condition is racy.
- A fresh `sending` claim must be treated as in flight by concurrent workers. Use a bounded stale
  claim TTL to recover from a crashed worker, and document the duplicate risk of a TTL shorter
  than the platform's possible response time.
- If a platform call succeeds but persisting `sent` fails, do not blindly release the claim:
  the platform side effect is real. Record an operational error and reconcile the ledger before
  allowing a retry.
- A batch header is not a deduplication record. Claim items first; otherwise overlapping workers
  can emit duplicate headers even when item-level deduplication exists.

## Feedback and approval workflows

- If category-specific producers all represent the same class of user importance, use one shared
  feedback namespace so 👍/👎 reactions affect future decisions across categories.
- A separate approval message (for example, create/reject calendar action) may coexist with the
  item's feedback card; the approval control does not replace required feedback controls.
- Keep notification feedback and domain-side mutation separate. A reaction must not move, label,
  delete, or rewrite the source item unless the operator explicitly requested that behavior.

## Schedule and polling changes

When the operator asks for more checks, first distinguish polling frequency from per-query batch
size. Unless they specify otherwise, increase only the requested watcher intervals, preserve the
collector's bounded limit and deduplication scope, and verify unrelated jobs did not change. Do
not manually fire an externally notifying job merely to validate a schedule change.

## Legacy migration

When adding a delivery ledger to an existing system:

1. Back up or transactionally migrate the schema while preserving permissions and secrets.
2. Treat legacy rows as already delivered only when they represent prior notification attempts
   closely enough to prevent a retroactive flood; document this assumption.
3. Do not automatically resend all old plain-text notifications. Identify exact source IDs and
   obtain explicit scope before a selective backfill.
4. Keep new rows distinguishable as `pending` so the first new producer can claim them.

## Verification checklist

- Unit test one producer per stream/category, one failed-send retry, and repeated delivery of the
  same source ID.
- The repeated-delivery test must show one header plus one item on the first call and zero
  external calls on the second call.
- Verify the shared ledger has no repeated source IDs, sent rows have a terminal delivered state,
  and duplicate workers report handled/skipped rather than sending.
- Perform a bounded read-only live probe of the source and scheduler; do not fire a notification
  job solely for evidence.
- Inspect scheduler outputs and platform-acceptance evidence separately. `ok`, empty stdout, or
  a silent sentinel is not proof that a message was delivered.
- Never print credentials, tokens, full secret configuration, or unnecessary sensitive message
  bodies in tests, logs, references, or reports.

## Reference

For a validated Stalwart/J.A.R.V.I.S. implementation, schema migration, overlapping watcher
case, and verification recipe, read `references/stalwart-email-alert-case.md`.

## Related skills

- `hermes-cron-operations` — scheduler diagnosis, safe job mutation, and schedule verification.
- `stalwart-jmap-operations` — Stalwart/JMAP transport, classification, and source-side safety.
