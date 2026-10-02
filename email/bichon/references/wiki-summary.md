# Bichon wiki summary

Source: https://github.com/rustmailer/bichon/wiki

## Configuration Reference

Each Bichon setting can be provided by CLI option or environment variable. Major groups:

- Logging/output: `BICHON_LOG_LEVEL`, ANSI logs, file logs, JSON logs, log retention.
- Server/network: `BICHON_HTTP_PORT` default 15630, `BICHON_BIND_IP`, `BICHON_PUBLIC_URL`, CORS options, REST HTTPS.
- Storage: `BICHON_ROOT_DIR`, `BICHON_INDEX_DIR`, `BICHON_DATA_DIR`, cache sizes, `BICHON_ENCRYPT_PASSWORD`.

`BICHON_ROOT_DIR` contains core encrypted account/system information. `BICHON_INDEX_DIR` and `BICHON_DATA_DIR` can be customized and are not encrypted.

## Encryption password

`BICHON_ENCRYPT_PASSWORD` encrypts sensitive values such as user login passwords, OAuth2 client secrets, OAuth2 access/refresh tokens and IMAP account passwords. It does not encrypt archived email contents. It must be changed before first use and cannot be safely changed later without making existing encrypted metadata unreadable.

Bichon also supports `BICHON_ENCRYPT_PASSWORD_FILE`, recommended for production. The file should contain only the password string.

## Storage and backup

Bichon can keep the root directory, metadata index, and email data in separate locations:

- Root directory: app settings, credentials, core DB, encrypted.
- Index directory: Tantivy metadata/search index, unencrypted.
- Data directory: raw email data / archive store, unencrypted.

A full backup must cover all configured locations. The data directory is most critical because it contains the message archive.

## v1.0 storage and migration

Bichon v1.0 separates email indexes from raw blobs:

- `bichon-indices/mail_metadata` — Tantivy metadata/full-text index.
- `bichon-indices/attachment_metadata` — Tantivy attachment metadata.
- `bichon-storage/keyspaces` — Fjall keyspaces for email bodies and attachment blobs.

Migration from v0.3.7 is non-destructive and uses `bichon-admin`; stop the old server before migration and use a recent v1.x release. The migration has metadata and email/blob phases. Batch size controls memory use.

## Deduplication

Bichon computes BLAKE3-256 content hashes for full raw email bytes and attachment bytes. Fjall blob storage skips writes when a content hash already exists. A background Tantivy dedup task runs every 12 hours and removes duplicate documents within the same account/mailbox/content hash, keeping the newest `ingest_at`. Cross-mailbox duplicates are preserved.

## Multi-user and RBAC

Bichon v0.2.0 introduced built-in authentication and RBAC. The default admin account is `admin` / `admin@bichon`; change it. Built-in roles:

- Global: Admin, Manager, Member.
- Account-scoped: AccountManager, AccountViewer.

Important permissions include `system:root`, `user:manage`, `token:manage`, `account:create`, `data:read`, `data:manage`, `data:raw_download`, `data:delete`, `data:export:batch`, `data:import:batch`.

API tokens are user-managed and intended for programmatic access. WebUI tokens are separate, internal, generated at login, stored in localStorage, and expire server-side according to `bichon_webui_token_expiration_hours` (default 168h).

## Folder sync selection

When an email account is added, only INBOX and Sent are synchronized by default. To sync more folders, use Accounts → Actions → Sync Folders, select folders, and save. Unchecking a folder stops future sync but does not automatically delete existing local messages.

## bichonctl import

`bichonctl` imports existing EML/MBOX data and is distributed as a precompiled binary. Create a NoSync account in the Web UI before importing. NoSync accounts do not connect to IMAP and are intended for static imports. `bichonctl` needs a config file with service base URL and API token. Import requires data import permissions.

Docker example from the wiki:

```bash
docker run -it --rm -v $(pwd):/mnt rustmailer/bichon bichonctl
```

Use container paths such as `/mnt/file.mbox` when running in Docker.

## SMTP ingest service

Introduced in v1.0.0. Bichon's SMTP server accepts inbound email deliveries and stores them into the target account's INBOX. It is receive-only and does not relay outbound mail.

Capabilities:

- Receive inbound messages.
- STARTTLS and implicit TLS.
- AUTH PLAIN / AUTH LOGIN.
- Optional unauthenticated mode.
- Max 1 recipient per DATA transaction.
- Max message size 50 MB.

When auth is required, the SMTP password field must be a valid Bichon API access token; username is ignored. Bichon resolves `RCPT TO` to a registered Account and checks permissions.

## External OAuth2 token API

Endpoint documented by the wiki: `POST /store-external-oauth2-token/:account_id` (`store_external_oauth2_token`). It accepts an `ExternalOAuth2Request` containing optional `oauth2_id`, `access_token`, and/or `refresh_token`.

Use modes:

- `access_token` only: external system handles refresh; Bichon stores current token only.
- `oauth2_id` + `refresh_token`: Bichon can refresh automatically if OAuth2 configuration exists.

## Reset admin password

Use the offline `bichon-admin` tool from release archives, not the Docker image. Stop Bichon first, point the tool at the root dir containing `meta.db`, provide the database encryption key, set a new password, then restart Bichon.
