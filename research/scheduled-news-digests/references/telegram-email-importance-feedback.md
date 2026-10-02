# Telegram feedback for email-importance alerts

Use this reference when a mail-monitoring routine sends Telegram alerts that the operator can classify as important or not important. It complements the newsletter feedback loop without changing mailbox contents.

## Contract

Send one compact Telegram message per selected email with two inline buttons:

- `👍 Importante`
- `👎 Não importante`

Use a stable compact callback identifier derived from the mail kind and stable message ID. Keep callback data within Telegram's limit and never put message bodies, credentials, or tokens in it. The callback must authorize the operator before writing feedback.

Persist enough metadata to learn safely without rereading the mailbox: stable alert ID, mail kind, normalized sender, sender domain, normalized subject tokens, preview if needed for audit, received time, user ID, rating (`1` or `-1`), and update time. SQLite with a unique `(alert_id, user_id)` key is sufficient; enable WAL when the sender and callback can run concurrently.

## Decision rule

Separate a direct operator decision from the softer similarity score:

1. Find the latest explicit rating for the exact normalized sender.
2. A latest `-1` is a reversible veto: do not select future candidates from that sender for the “important” alert stream.
3. A later `+1` re-enables that sender and may promote similar messages.
4. When there is no exact-sender decision, use aggregate signals from sender domain and subject tokens as a soft score. Require a threshold or repeated evidence before suppressing a broader domain/topic.
5. Apply this feedback filter before the ordinary importance predicate, so a negative decision cannot be defeated by a generic keyword such as “document” or “protocolo”.

This rule satisfies an explicit request to stop sending items rated not important while avoiding an irreversible domain-wide ban. If the operator asks for a broader ban, record that scope separately and make it explicit.

## Callback behavior

On a button tap:

1. validate the callback prefix, action, and identifier;
2. authorize the Telegram user;
3. upsert the rating and timestamp;
4. edit only the reply markup so the selected button changes to `✅` and the alternate button remains available;
5. answer the callback promptly with confirmation;
6. log only the stable alert ID, rating, and non-sensitive classification metadata.

A later tap must be able to change the rating. Do not remove the alert row merely because it was classified negatively.

## Delivery and fallback

A direct Telegram API sender is useful when ordinary cron output cannot express per-message keyboards. Register the alert row before or atomically with the item send, and return a result containing sent IDs and per-item errors. Suppress ordinary cron text only after direct delivery succeeds; retain a textual fallback for failed items. State clearly that fallback text cannot carry inline buttons.

Do not run a live test message merely to validate wiring unless the operator explicitly authorizes it. Prefer unit tests with a temporary SQLite database, a callback test with a fake Telegram query, and a read-only/dry-run against the real mail source.

## Verification checklist

- keyboard contains both actions and compact callback IDs;
- positive and negative taps persist and visibly update the keyboard;
- unauthorized users cannot write ratings;
- latest negative exact-sender feedback blocks a future actionable candidate;
- later positive feedback re-enables it;
- domain/subject similarity remains soft unless broader suppression is requested;
- successful direct sends do not produce duplicate cron text;
- failed direct sends produce the documented fallback;
- the mail provider shows no mutation after dry-run verification;
- the scheduler remains enabled and its real script imports the feedback module in a fresh process.

## Privacy and safety

Use Stalwart/JMAP as the mail source when that is the configured system. Keep credentials in the mail service's existing secret store, never in the feedback database, callback data, logs, prompts, or this reference. Feedback changes local alert selection only; it does not delete, move, label, or rewrite email unless the operator separately authorizes such an action.
