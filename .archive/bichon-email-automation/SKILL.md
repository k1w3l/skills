---
name: bichon-email-automation
description: Use this skill only when the user explicitly asks to inspect or operate the legacy self-hosted Bichon service. The user's active email consultation, classification, filtering, alerts, and cron routines use Stalwart/JMAP through the restricted SSH mail agent; do not choose Bichon as the default backend.
---

# Legacy Bichon Email Automation

This skill documents the user's legacy self-hosted Bichon instance. Use it only for explicit Bichon requests, historical diagnosis, or a deliberate rollback. The active email backend is Stalwart/JMAP through `mailagent@192.168.1.13`; active routines must not read Bichon credentials or mutate Bichon state.

If the request concerns Stalwart, JMAP, `mailctl.py`, the current mail agent, endpoint health,
URL changes, or active email routines, stop using this skill and load
`stalwart-jmap-operations`. Do not apply Bichon endpoints or credential files to the active
backend merely because this legacy skill was loaded first.

## Safety and credential handling

- Read credentials from `/home/kiwel/.hermes/secrets/bichon.env` when available.
- The file should define `BICHON_URL` and `BICHON_API_KEY`.
- Never print, log, store in memory, or include the API key in final responses.
- Use `Authorization: Bearer *** key from env file>` in scripts, but never echo the value.
- Keep any credential file mode at `600` and parent directory at `700`.
- If a cron job needs email access, source or parse this env file inside the job/script rather than embedding the key in the cron prompt.

## Standard connection check

Before applying filters or routines, verify the API is reachable and authenticated:

1. Load `BICHON_URL` and `BICHON_API_KEY` from the local env file.
2. GET `$BICHON_URL/api/v1/current-user` with the Bearer token.
3. Confirm HTTP 200 and expected authenticated user/email.
4. GET `$BICHON_URL/api/v1/minimal-account-list` to discover account IDs.
5. GET `$BICHON_URL/api/v1/list-mailboxes/{account_id}` to discover mailbox IDs.

Do not guess account IDs or mailbox IDs. Discover them from the API on each new automation unless the task explicitly supplies them.

## Common endpoints

Use these endpoints as the known-good starting set:

- `GET /api/v1/current-user` — validate authentication and permissions.
- `GET /api/v1/minimal-account-list` — list accounts with IDs and emails.
- `GET /api/v1/list-mailboxes/{account_id}` — list mailboxes for an account.
- `GET /api/v1/list-messages/{account_id}?mailbox_id={mailbox_id}&page={n}&page_size={n}` — page through messages.
- `GET /api/v1/message-content/{account_id}/{message_id}` — fetch full content when list results are insufficient.
- `GET /api/v1/get-thread-messages/{account_id}?thread_id={thread_id}&page={n}&page_size={n}` — fetch thread messages.
- `GET /api/v1/download-message/{account_id}/{message_id}` — download `.eml`.
- `GET /api/v1/download-attachment/{account_id}/{message_id}?name={filename}` — download attachment.
- `POST /api/v1/delete-messages` — delete messages; treat as destructive and confirm scope unless preauthorized.
- `POST /api/v1/restore-messages/{account_id}` with `message_ids` — restore messages.

## Workflow for classification and filters

1. Discover accounts and mailboxes.
2. Select the target mailbox, usually `INBOX`, by name rather than hard-coded ID.
3. Page messages in batches.
4. For each candidate message, classify using subject, sender, recipients, date, tags, snippet/text, and full content when needed.
5. Respect the user's existing email classification preferences. Shopee/AliExpress are purchases/e-commerce; Hotmart/Udemy are courses; Ollama is AI/technology; Correio do Povo is news; Laçador/Samsung/voeazul are promos; KM is benefits; Google Agenda is events; social networks are social; Claro is bills; Ticketmaster is events/tickets.
6. For destructive cleanup, prepare a candidate list and ask approval unless the user has explicitly preauthorized that class of cleanup.
7. Verify effects by re-querying counts or message state after applying a routine.

## Tag mutations and scheduled routines

Classification output is not proof that tags were applied. After every tag mutation, re-query the affected messages and verify the expected tags in Bichon's returned state. For bulk work, establish the endpoint contract with one reversible message first.

Do not trust Hermes Cron's `last_status=ok` alone when a wrapper catches exceptions. A `no_agent=true` routine should stay silent on success/no findings, print actionable output when needed, and return non-zero on operational failure so the scheduler cannot record a false success.

Do not migrate or reactivate the user's current Gmail/email routines on Bichon. For any active
monitoring, classification, alerts, or cron repair, load `stalwart-jmap-operations` and use its
`references/inbox-automation-hardening.md` workflow. Only update a Bichon job when the user has
explicitly requested a legacy Bichon operation or deliberate rollback; in that narrow case,
update job names/prompts, reconcile the schedule, trigger one controlled run, and verify both
delivery and Bichon's remote state.

Read `references/tag-and-cron-validation.md` before implementing or repairing Bichon tag updates or cron-driven email routines. It contains the minimal mutation test, the `FacetParseError` contract pitfall, and end-to-end verification steps.

## Documentation pitfall

The user's Bichon `/api-docs` path may serve the SPA application rather than an OpenAPI JSON document. If direct documentation URLs such as `/openapi.json` or `/swagger.json` return HTML, inspect the frontend asset references and search built JavaScript chunks for `/api/v1/` endpoints, then confirm candidate endpoints with authenticated requests.

See `references/bichon-api-discovery.md` for the session-specific endpoint discovery notes.

## Reporting style

In final responses, report what was actually verified: endpoint, HTTP status, authenticated account, discovered accounts/mailboxes, and any changes made. Do not reveal API keys. Keep the report concise and suitable for the terminal.
