---
name: database-backed-service-recovery
description: Use when recovering DB-backed services. Back up and verify.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [recovery, credentials, docker, compose, postgresql, self-hosting, ssh]
    category: devops
    requires_toolsets: [terminal]
---

# Database-backed service recovery

Recover access to a self-hosted container service without destroying application data. This is a class-level runbook: adapt the schema, hashing format, and service commands to the exact application version before making a write.

## Use this for

- A self-hosted service whose account data lives in PostgreSQL or another database.
- Credential recovery where the application has no usable reset flow.
- Container stacks administered on a remote VM or host.
- Recovery work that must preserve encrypted application data, independent keys, or existing records.

Do not use this as a generic password-cracking procedure. The operator must own or be explicitly authorized to administer the service and its database.

## Non-negotiable rules

1. **Back up before writing.** Make a protected, restorable database backup and keep it until the user-facing login and data validation succeed.
2. **Prefer supported application operations.** If the current password/session is available, use the application's change-password command. If it is not, inspect the exact server version and schema before an administrative update.
3. **Preserve independent encryption material.** An account password and a data-encryption key are often different. Never replace or regenerate the latter as part of password recovery.
4. **Never put plaintext secrets in chat, shell history, process arguments, logs, or wiki pages.** Let the user type the new secret in a real writable TTY.
5. **Verify the effect, not just the command.** A successful SQL exit code, a misleading command-tag parser, or a successful helper-account registration is not end-to-end validation.
6. **Do not delete and re-register an account** unless remote-data loss is explicitly accepted and a recoverable local copy is confirmed.

## Workflow

### 1. Establish an administration path

Identify the actual Docker host, container names, bind mounts, database type, and service version. For remote Docker, prefer SSH to the host over an exposed Docker TCP socket.

For a dedicated key whose public half is being bootstrapped with the existing account password, use an interactive first copy and then switch to key-only verification:

```bash
ssh-copy-id \
  -i ~/.ssh/id_ed25519_service.pub \
  -o PubkeyAuthentication=no \
  -o PreferredAuthentications=keyboard-interactive \
  USER@DOCKER_HOST
```

Persist non-default key selection in `~/.ssh/config`:

```sshconfig
Host service-docker DOCKER_HOST
    HostName DOCKER_HOST
    User USER
    IdentityFile ~/.ssh/id_ed25519_service
    IdentitiesOnly yes
    PreferredAuthentications publickey
    PasswordAuthentication no
    KbdInteractiveAuthentication no
```

Prove key-only access before an administrative command:

```bash
ssh -o BatchMode=yes service-docker hostname
```

A command that succeeds while silently falling back to a password is not a valid access check.

### 2. Inspect before changing

- Confirm the service and database containers are running.
- Read the exact image/server version and relevant Compose configuration, without printing database passwords or secret environment values.
- Confirm the user exists and identify the account/password columns and foreign-key relationships.
- Determine whether the application has a supported reset/change-password endpoint and whether it requires the old password.
- Locate the independent encryption key and protect it from accidental replacement.

### 3. Create a protected backup

Use the database container's local credentials/environment rather than putting a database password on the command line. For PostgreSQL:

```bash
umask 077
docker exec DB_CONTAINER sh -c \
  'exec pg_dump -Fc -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  > service-db-before-password-reset-UTC.dump
```

Check that the dump is non-empty and retain it until the final application check. Do not put the dump, its contents, or credential hashes in a wiki or chat transcript.

### 4. Generate a compatible password hash

Use the application's own hasher or a documented compatible implementation. Confirm the algorithm and parameters from the exact server source/version; do not substitute MD5, database `crypt()`, bcrypt, or a generic hash merely because it is available.

If the application has open registration and its registration handler is the only available in-stack hasher, a uniquely named temporary account can be used as a hash-generation bridge only when all of these are true:

- registration is intentionally enabled and its side effects are understood;
- the temporary username is valid and within the schema length limit;
- the temporary account is removed after the hash is read;
- the temporary row is removed **before** assigning its hash to the target if the password column is unique;
- the target update and final login are independently verified.

Prefer a local helper using the application's library when that avoids creating a temporary account.

### 5. Make the minimal database update

Keep SQL values out of process arguments and history. When using `psql` client variables, feed SQL through stdin if the installed client does not expand variables in `-c` strings:

```bash
db_psql() {
    docker exec -i DB_CONTAINER sh -c \
      'exec psql -X -v ON_ERROR_STOP=1 -At -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
}
```

Validate identifiers before interpolation and use the database client's safe variable/literal mechanism for values. Update only the password field for the intended row. Do not change account IDs, sessions, history, records, encryption keys, or database-user credentials unless the inspected recovery plan specifically requires it.

Do not parse an `UPDATE ... RETURNING` capture as if it must contain one line: `psql` may emit returned rows plus a separate command tag such as `UPDATE 1`. Suppress command output and verify the stored value separately, for example with a boolean comparison that never prints the hash.

### 6. Validate and clean up

Use all applicable checks:

1. Database row exists and the stored hash has the expected algorithm/format.
2. The hash differs from the pre-change value when a backup comparison is available.
3. The real service login succeeds with the new password.
4. Existing sessions behave as expected.
5. Application sync/data decryption succeeds with the original encryption key.
6. Temporary helper accounts and files are removed; the protected backup remains until sign-off.
7. Disable open registration if it was enabled only for recovery.

If the script reports a failure after a write, first determine whether the write already succeeded from the database/backup state. Do not blindly repeat the reset.

## Interactive terminal discipline

Hermes `terminal(background=true)` processes are mirrored in a read-only terminal tab. Never launch a password prompt there and then tell the user to type into it. Run the interactive command in the user's normal terminal application or another genuinely writable TTY. The agent must not type or request plaintext passwords in chat.

Give the user the shortest actionable command and say exactly where the secret is entered. For noninteractive verification, use key-only SSH or a status code and discard response bodies containing tokens.

## Common pitfalls

| Symptom | Root cause | Correct response |
|---|---|---|
| SSH command works but still prompts for a password | Non-default key is not selected, or the command fell back to keyboard-interactive | Add `IdentityFile`/`IdentitiesOnly`, then test with `BatchMode=yes` and password methods disabled |
| Temporary registration returns HTTP 400 | Invalid request, registration disabled, duplicate data, or a schema limit | Read the application log and response body; do not retry blindly |
| Temporary username is rejected | Helper name exceeds the application's column length | Generate a short valid name and check the schema limit first |
| Target update appears to fail after `RETURNING` | Output contains both returned data and a command tag | Verify the stored hash separately, then test the real login |
| User cannot type into the recovery prompt | Prompt was launched in a read-only background terminal mirror | Stop it and rerun from a normal writable terminal |
| Login works but history is empty/garbled | Wrong or replaced encryption key | Restore the original key; do not register a new account |

## Reference notes

The validated Atuin case study, including its Argon2id/schema details and exact failure lessons, is in `references/atuin-password-recovery.md`.
