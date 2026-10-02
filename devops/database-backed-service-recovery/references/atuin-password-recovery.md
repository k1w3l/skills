# Atuin self-hosted password recovery notes

**Scope**: Legacy/self-hosted Atuin sync server backed by PostgreSQL in Docker Compose. Validated against the local stack on 2026-09-12 with server 18.13.3 and client 18.16.0.

## Authoritative facts

- The legacy server does not provide a password-reset flow that works without the current password. `atuin account change-password` verifies the current password.
- In Atuin 18.13.3, the server handler generates Argon2id hashes. PostgreSQL stores them in `users.password`; the schema defines `username varchar(32)` and a unique constraint on `password`.
- The account password is separate from the client encryption key. Preserve the existing key (normally `~/.local/share/atuin/key`) so encrypted history remains readable.
- Deleting/re-registering an account removes remote history; it is not the data-preserving recovery path.

Sources:

- [Atuin FAQ](https://docs.atuin.sh/main/faq/)
- [Atuin account reference](https://docs.atuin.sh/main/reference/account/)
- [Atuin 18.13.3 password handler](https://github.com/atuinsh/atuin/blob/v18.13.3/crates/atuin-server/src/handlers/user.rs)
- [Atuin 18.13.3 PostgreSQL users schema](https://github.com/atuinsh/atuin/blob/v18.13.3/crates/atuin-server-postgres/migrations/20210425153757_create_users.sql)

## Validated recovery sequence

1. Establish key-only SSH access to the Docker VM. First bootstrap a dedicated public key with `ssh-copy-id -i KEY.pub -o PubkeyAuthentication=no -o PreferredAuthentications=keyboard-interactive`; then persist `IdentityFile` and `IdentitiesOnly yes` in SSH config and verify with `BatchMode=yes`.
2. Confirm `atuin` and `atuin-db` are running and create a protected `pg_dump` before any write.
3. Ask for the new password only in a writable user terminal. Do not use a Hermes background-process terminal mirror for the prompt.
4. With open registration intentionally enabled, create a short temporary Atuin account using the desired password. Read its Argon2id hash from PostgreSQL.
5. Remove the temporary account before assigning the hash to the target, because `users.password` is unique. Keep the target's history and encryption key untouched.
6. Feed SQL to `psql` through stdin with `\\set` when required by the installed client. In the validated PostgreSQL 18 image, variable expansion in the `-c` form did not work as expected, while stdin did.
7. Do not compare `UPDATE ... RETURNING` output to one line: `psql` can emit the returned username and a separate `UPDATE 1` command tag. Verify the stored hash separately and then test the actual login.
8. Remove the helper account/files, keep the backup until validation, and disable open registration if it was temporary.

## Failure lessons

- An overlong helper username caused HTTP 400 and a server log entry `value too long for type character varying(32)` before any target change. The corrected helper name used only a short epoch/PID suffix.
- The first database-update script reported a false failure after the update had already succeeded because it treated `RETURNING` output as a single line. The target hash was compared against the pre-change dump without printing either hash; the comparison confirmed that the password hash changed.
- The final application-level check is still required: run `atuin login`, then `atuin sync` and `atuin status` on the client that owns the original encryption key.

## Safe verification shape

For a PostgreSQL-backed service, keep credentials and hashes out of arguments and output. Use a protected dump before the write, an SQL boolean comparison for the target row, and a real login/sync check. A successful SQL statement alone is not sufficient.
