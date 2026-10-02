# Bichon API observed from Sr. Kiwel's instance

Base URL: `http://bichon.kiwel.home`

Authentication: `Authorization: Bearer *** from `/home/kiwel/.hermes/secrets/bichon.env`.

Do not print the API key. Use Python/urllib or the bundled helper script to keep secrets out of command history and logs.

## Verified endpoints

- `GET /api/v1/current-user` — returns authenticated user, global/account permissions and roles.
- `GET /api/v1/minimal-account-list` — returns `[{id, email}]`.
- `GET /api/v1/list-mailboxes/{account_id}?remote=false` — returns local/synced mailboxes. UI function accepts `remote` boolean.
- `GET /api/v1/list-messages/{account_id}?mailbox_id={mailbox_id}&page={n}&page_size={n}` — paginated mailbox messages.
- `GET /api/v1/get-thread-messages/{account_id}?thread_id={thread_id}&page={n}&page_size={n}` — paginated messages in a thread.
- `GET /api/v1/message-content/{account_id}/{message_id}` — body/content details.
- `GET /api/v1/download-message/{account_id}/{message_id}` — raw EML blob.
- `GET /api/v1/download-attachment/{account_id}/{message_id}?name={filename}` — attachment blob.
- `POST /api/v1/search-messages` — full-text/filtered search.
- `GET /api/v1/all-tags` — list tag facets.
- `POST /api/v1/update-tags` — apply tag set to messages.
- `POST /api/v1/delete-messages` — delete selected messages. Dangerous.
- `POST /api/v1/restore-messages/{account_id}` with `{"message_ids": [...]}` — restore messages to IMAP. Dangerous.
- `DELETE /api/v1/delete-mailbox/{account_id}/{mailbox_id}` — delete mailbox. Dangerous.

## Search payload

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

## Tag payload

```json
{
  "updates": {
    "7501643334909347": [6948171769895232]
  },
  "tags": ["compras", "e-commerce"]
}
```

`updates` maps account ID strings to arrays of message IDs. The UI lowercases new tags.

## Known local IDs at last verification

- `kiwel01@gmail.com`: account `7501643334909347`
  - `INBOX`: mailbox `3716229963652770`
  - `[Gmail]/E-mails enviados`: mailbox `4807165465470919`
- `eduardo.kiwel@live.com`: account `1931859330768072` with no mailboxes observed.

Rediscover IDs before destructive operations or long-lived scheduled routines.
