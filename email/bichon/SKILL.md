---
name: bichon
description: Operate Eduardo Kiwel's self-hosted Bichon email archive/manager API for email search, filtering, tagging, mailbox inspection, message retrieval, restore/delete workflows, API-token usage, Bichon configuration, storage, migration, SMTP ingest, and bichonctl imports. Use this whenever the user mentions Bichon, email automation through Bichon instead of Gmail, mail filters/rotinas, archived emails, API tokens, tags/labels, mailboxes, Bichon wiki/docs, or avoiding Google OAuth credential expiry.
---

# Bichon email operations

Use this skill to work with Bichon as the primary email automation layer. For Sr. Kiwel, Bichon replaces direct Gmail/Google API access for email consultation, classification and routines, because Bichon API tokens avoid Google OAuth expiry issues.

## Local connection profile

- Base URL: `http://bichon.kiwel.home`
- Secrets file: `/home/kiwel/.hermes/secrets/bichon.env`
- The file contains `BICHON_URL` and `BICHON_API_KEY`.
- Never print, persist in memory, or include the API key in reports/logs.
- For shell/Python scripts, source/parse the env file and send `Authorization: Bearer <token...v>`.

Use this safe shell pattern; it expands the key from the env file without printing it:

```bash
set -a
. /home/kiwel/.hermes/secrets/bichon.env
set +a
curl -fsS \
  -H "Authorization: Bearer ***" \
  -H 'Accept: application/json' \
  "$BICHON_URL/api/v1/current-user"
```

Prefer Python for non-trivial workflows so secrets stay out of command history and output. A helper is bundled at `scripts/bichon_client.py`.

## Known local account IDs

Verified on Sr. Kiwel's Bichon instance:

- `kiwel01@gmail.com` → account ID `7501643334909347`
  - `INBOX` → mailbox ID `3716229963652770`
  - `[Gmail]/E-mails enviados` → mailbox ID `4807165465470919`
- `eduardo.kiwel@live.com` → account ID `1931859330768072`
  - no mailboxes observed at the time of verification

Always rediscover account/mailbox IDs with the API before destructive or scheduled work; they can change if the instance is rebuilt.

## Core API endpoints observed

Authentication is via Bearer token.

Read/discovery:

- `GET /api/v1/current-user`
- `GET /api/v1/minimal-account-list`
- `GET /api/v1/list-mailboxes/{account_id}?remote=false`
- `GET /api/v1/list-messages/{account_id}?mailbox_id={mailbox_id}&page=1&page_size=30`
- `GET /api/v1/get-thread-messages/{account_id}?thread_id={thread_id}&page=1&page_size=30`
- `GET /api/v1/message-content/{account_id}/{message_id}`
- `GET /api/v1/download-message/{account_id}/{message_id}`
- `GET /api/v1/download-attachment/{account_id}/{message_id}?name={filename}`
- `GET /api/v1/all-tags`

Search and metadata:

- `POST /api/v1/search-messages`
- `POST /api/v1/update-tags`

Dangerous/side-effect endpoints:

- `POST /api/v1/delete-messages`
- `POST /api/v1/restore-messages/{account_id}`
- `DELETE /api/v1/delete-mailbox/{account_id}/{mailbox_id}`

OAuth/account/admin endpoints exist too: `/api/v1/account`, `/api/v1/accounts`, `/api/v1/account-state/{id}`, `/api/v1/oauth2*`, `/api/v1/access-token*`, `/api/v1/users*`, `/api/v1/roles*`. Consult the running UI/API docs before using them.

## Search API shape

Use `POST /api/v1/search-messages` with:

```json
{
  "filter": {
    "text": "invoice",
    "from": "sender@example.com",
    "to": "recipient@example.com",
    "cc": "copy@example.com",
    "bcc": "hidden@example.com",
    "has_attachment": true,
    "attachment_name": "pdf",
    "since": 1767225600000,
    "before": 1769817600000,
    "account_id": 7501643334909347,
    "mailbox_id": 3716229963652770,
    "message_id": "<abc@example.com>",
    "tags": ["compras"],
    "min_size": 2097152,
    "max_size": 10485760
  },
  "page": 1,
  "page_size": 30,
  "sort_by": "DATE",
  "desc": true
}
```

Notes:

- Dates are JavaScript/Unix epoch milliseconds.
- UI size presets map to: `tiny` max 15 KiB; `small` max 2 MiB; `medium` 2–10 MiB; `large` 10–20 MiB; `huge` min 20 MiB.
- Return shape is paginated: `items`, `current_page`, `page_size`, `total_items`, `total_pages`.
- Message items include fields such as `id`, `account_id`, `account_email`, `mailbox_id`, `mailbox_name`, `from`, `to`, `cc`, `bcc`, `subject`, `date`, `internal_date`, `thread_id`, `message_id`, `tags`, `attachments`, `text`, `size`, `uid`.

## Tagging/classification workflow

For mail routines, prefer tags over destructive mailbox changes unless the user explicitly asks for deletion or restore.

1. Search narrowly enough to avoid accidental tagging.
2. Show a sample/count when the operation is broad.
3. Apply tags with `POST /api/v1/update-tags`.

Observed update payload from the UI:

```json
{
  "updates": {
    "7501643334909347": [6948171769895232]
  },
  "tags": ["compras", "e-commerce"]
}
```

The `updates` object maps account IDs to arrays of message IDs. Tags are lower-case strings in the UI. Preserve existing tags by reading the message first when replacing tag sets could remove useful context.

Sr. Kiwel's classification conventions:

- Shopee/AliExpress: e-commerce/compras
- Hotmart/Udemy: cursos/estudos
- Ollama: IA/tecnologia
- Correio do Povo: notícias
- Laçador/Samsung/voeazul-news: propaganda/promoções
- KM de Vantagens: cashback/benefícios
- Google Agenda: eventos
- LinkedIn/Facebook/Instagram/X: redes sociais
- Claro: contas
- Ticketmaster: ingressos/eventos
- Pichau RMA: important/actionable

## Destructive actions discipline

Deletion, mailbox deletion, and restore-to-IMAP have lasting side effects. Before calling them:

- Rediscover IDs from the live API.
- Search and count affected messages.
- Provide a concise preview: account, mailbox, count, example subjects/senders.
- Obtain explicit user approval unless the user has already preauthorized the exact operation.
- After execution, verify by re-querying Bichon.

For scheduled routines, encode the exact criteria and keep deletion disabled unless explicitly requested.

## Bichon documentation summary

The source wiki is `https://github.com/rustmailer/bichon/wiki`. A distilled reference is bundled at `references/wiki-summary.md`; observed local API details are in `references/api-observed.md`.

Key wiki facts:

- Bichon is a lightweight Rust email backup/archive solution with its own storage and search stack.
- It uses Tantivy indexes for metadata/full-text search and Fjall keyspaces for raw message/attachment blobs in v1.x.
- `BICHON_ENCRYPT_PASSWORD` protects sensitive account/app/OAuth/IMAP credentials, not archived email contents. Set it before first use; changing it later makes encrypted metadata unreadable.
- Root directory contains sensitive encrypted account/system data; index/data directories are not encrypted and must be backed up separately.
- Multi-user RBAC uses global roles (`Admin`, `Manager`, `Member`) and account roles (`AccountManager`, `AccountViewer`). API tokens are user-managed and intended for programmatic access.
- Bichon WebUI tokens expire server-side, but API tokens are separately user-managed.
- By default, only INBOX and Sent are synced when adding an account; additional folders are selected via Accounts → Actions → Sync Folders.
- `bichonctl` imports EML/MBOX data into NoSync accounts using a service URL and API token.
- SMTP ingest in v1.0 is receive-only, can accept STARTTLS/SMTPS and AUTH PLAIN/LOGIN using Bichon API tokens, max one recipient per transaction, max message size 50 MB.
- Migration from v0.3.7 to v1.0 uses `bichon-admin`, is non-destructive, and should be done with the old server stopped.

## Helper script examples

List accounts:

```bash
python3 ~/.hermes/skills/email/bichon/scripts/bichon_client.py accounts
```

List mailboxes:

```bash
python3 ~/.hermes/skills/email/bichon/scripts/bichon_client.py mailboxes 7501643334909347
```

Search messages:

```bash
python3 ~/.hermes/skills/email/bichon/scripts/bichon_client.py search \
  --text invoice --account-id 7501643334909347 --page-size 10
```

Get message content:

```bash
python3 ~/.hermes/skills/email/bichon/scripts/bichon_client.py content \
  7501643334909347 6948171769895232
```

Tag messages:

```bash
python3 ~/.hermes/skills/email/bichon/scripts/bichon_client.py tag \
  7501643334909347 compras,e-commerce 6948171769895232
```

When writing one-off scripts, import or copy the helper's `BichonClient` class rather than rebuilding auth/error handling from scratch.
