# Atuin self-hosted account recovery

**Summary**: Source-grounded recovery notes for an Atuin 18.13.x server in Docker Compose with PostgreSQL. The pattern preserves encrypted history and must be live-validated on the target before claiming success.

**Sources**: Atuin FAQ; Atuin `account` reference; Atuin v18.13.3 server source and PostgreSQL migration.

**Last updated**: 2026-09-12

---

## Scope and decision tree

This applies to the legacy/self-hosted sync server, not Atuin Hub.

1. **Try the credential vault first.** If the password is in Bitwarden or another approved vault, use it without changing server state.
2. **If the current password is known**, use `atuin account change-password`. The server verifies the current password; this is not a recovery path when it has been forgotten.
3. **If the current password is lost but history must remain**, use an administrative PostgreSQL reset. Do not delete and recreate the account unless loss of the server-side history is explicitly accepted.

The client encryption key is independent of the account password. Preserve the local Atuin key and do not run `atuin register` on an existing client merely to work around a login failure.

## Source-confirmed facts for v18.13.3

- PostgreSQL stores accounts in `users(username, email, password)`; the `password` column is `UNIQUE`.
- The server hashes registrations and password changes with Argon2id (`argon2` crate, default parameters) and verifies the encoded hash on `/login`.
- `ATUIN_OPEN_REGISTRATION=true` permits the registration endpoint. This is a prerequisite for the temporary-registration hash-generation technique below.
- A successful login returns a session token. Discard that response during validation; never log or store the token in the skill.

## Non-destructive administrative pattern

Perform this on the Docker host/guest, not through an exposed Docker TCP socket when SSH or a guest console is available.

1. Confirm the target containers and Compose persistence paths before changing anything.
2. Create a protected `pg_dump` backup of the Atuin database. Keep it outside Git and remove it only after a restore path is known.
3. Prompt for the new password on a private TTY; do not place it in chat, shell history, command arguments, or a file.
4. When open registration is enabled, create a uniquely named temporary Atuin account using the new password. Read its generated Argon2id hash from `users.password` using `psql` inside `atuin-db`.
5. Delete the temporary account **before** updating the target: `users.password` is unique, so updating the target while the temporary row remains can fail with a uniqueness violation. Delete its session row first if there is no foreign-key cascade.
6. Update only `users.password` for the target username using a parameterized `psql` variable. Do not change the PostgreSQL role password, email, username, history, records, store, or encryption key.
7. Validate `POST /login` with the new password while discarding the response body. Treat any status other than the expected success as a failed recovery.
8. On the client, run `atuin login`, then `atuin sync` and `atuin status`. Confirm the same encryption key is still in use and that the history remains readable.
9. Disable open registration afterward if it is not required by the deployment, then verify the Compose/service health.

If open registration is disabled, use a separately reviewed Argon2id hash generator compatible with the exact server version instead of enabling registration casually. Do not substitute MD5, bcrypt, PostgreSQL `crypt()`, or a plain-text value.

## Safe database invocation pattern

Use the PostgreSQL environment already present inside the database container so the database password is not exposed on the command line:

```bash
docker exec -i atuin-db sh -c \
  'exec psql -X -v ON_ERROR_STOP=1 -At -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$@"' \
  db-psql -v target="$TARGET_USERNAME" \
  -c "SELECT count(*) FROM users WHERE username = :'target';"
```

Use `psql` variables with `:'name'` quoting for user-supplied values. Do not interpolate a username or generated hash directly into SQL text.

## Administration access pattern

Prefer the narrowest channel that reaches the Docker guest: existing SSH key, then the guest console. If neither is available, a temporary Ed25519 key may be generated locally and its **public** half added to the guest by an operator through the console. Grant access to the guest service account rather than the Proxmox host root when possible; remove the authorized-key line and the temporary private key after verification. Never reuse an unrelated backup private key merely because it is present on disk.

## Validation boundary

This reference is a source-grounded recipe, not evidence that a particular deployment was successfully changed. A future agent must report the actual backup path, database update result, login status, sync/status output, and cleanup result before claiming completion. If remote access or required credentials are missing, stop at the boundary and ask the operator to execute the procedure; do not fabricate a successful reset.

## Related sources

- https://docs.atuin.sh/main/faq/
- https://docs.atuin.sh/main/reference/account/
- https://github.com/atuinsh/atuin/blob/v18.13.3/crates/atuin-server/src/handlers/user.rs
- https://github.com/atuinsh/atuin/blob/v18.13.3/crates/atuin-server-postgres/migrations/20210425153757_create_users.sql
