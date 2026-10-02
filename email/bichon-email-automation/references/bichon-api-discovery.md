# Bichon API Discovery Notes

These notes capture the initial verified workflow for Eduardo Kiwel Teixeira's self-hosted Bichon email manager. They are implementation notes for future email automation tasks, not a place for secrets.

## Instance and credentials

- Base URL: `http://bichon.kiwel.home`
- Local credential file: `/home/kiwel/.hermes/secrets/bichon.env`
- Expected variables: `BICHON_URL`, `BICHON_API_KEY`
- Auth header: `Authorization: Bearer *** key>`
- Do not print the key. Read it from the env file for scripts and cron jobs.

## Verified endpoints

- `GET /api/v1/current-user`
  - Verified HTTP 200 with Bearer token.
  - Returns authenticated user, email, permissions, and account access mapping.

- `GET /api/v1/minimal-account-list`
  - Returns account records with `id` and `email`.
  - Initially observed accounts:
    - `kiwel01@gmail.com`
    - `eduardo.kiwel@live.com`

- `GET /api/v1/list-mailboxes/{account_id}`
  - Returns mailbox records. Use discovered `account_id`, not `1`.
  - Initially observed for the Gmail account:
    - `INBOX`
    - `[Gmail]/E-mails enviados`

- `GET /api/v1/list-messages/{account_id}?mailbox_id={mailbox_id}&page=1&page_size=5`
  - Returns paginated messages with keys such as `current_page`, `items`, `page_size`, `total_items`, and `total_pages`.
  - Message items may include `account_email`, `account_id`, `attachments`, `bcc`, `cc`, `date`, `from`, `id`, `internal_date`, `mailbox_id`, `mailbox_name`, `message_id`, `size`, `subject`, `tags`, `text`, `thread_id`, `to`, and `uid`.

- `GET /api/v1/message-content/{account_id}/{message_id}`
- `GET /api/v1/get-thread-messages/{account_id}?thread_id={thread_id}&page={n}&page_size={n}`
- `GET /api/v1/download-message/{account_id}/{message_id}`
- `GET /api/v1/download-attachment/{account_id}/{message_id}?name={filename}`
- `POST /api/v1/delete-messages`
- `POST /api/v1/restore-messages/{account_id}` with body containing `message_ids`

## API docs workaround

The `/api-docs`, `/openapi.json`, `/swagger.json`, and `/api-docs.json` paths may return the Bichon SPA HTML rather than a JSON OpenAPI spec. When this happens:

1. Fetch `/api-docs` and locate the JS asset, for example `/assets/index-....js`.
2. Search the asset and lazy chunks for `/api/v1/` strings.
3. Confirm any candidate endpoint with authenticated requests before relying on it.

Useful frontend-discovered chunks in the initial session included chunks exposing account, mailbox, and message calls. The reliable lesson is the discovery method, not the exact chunk filename, because filenames are build hashes and may change.

## Destructive operations

Deleting messages through Bichon is possible. Treat delete operations as destructive:

- Generate a candidate list first.
- Ask the user for approval unless a standing rule explicitly authorizes the operation.
- After deletion or restoration, re-query the mailbox/message state to verify the result.
