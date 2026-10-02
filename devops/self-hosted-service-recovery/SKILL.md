---
name: self-hosted-service-recovery
description: Use when recovering service access. Back up and verify.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [self-hosting, recovery, credentials, docker, postgres, security]
    category: devops
    requires_toolsets: [terminal]
---

# Self-hosted Service Recovery

Recover access to self-hosted applications while preserving application data, encryption keys, and a reversible rollback path. This is a class-level runbook: use the application-specific notes in `references/` for schema, hash format, and provider behavior.

## When to use

- A user has lost an application password or authentication session.
- A service runs in Docker/Compose and its identity data lives in PostgreSQL, SQLite, or another persistent store.
- The normal password-reset flow is absent, broken, or requires the forgotten credential.
- Remote administration needs to reach a Docker guest without exposing a management socket.
- A self-hosted client is configured but cannot reach or authenticate against its service endpoint.

Do not use this skill for guessing credentials, cracking password hashes, bypassing access controls on systems without explicit authorization, or deleting data to make a login problem disappear.

## Core rules

1. **Preserve the data authority.** Identify the database, volume, encryption key, and configuration that actually own the account and history.
2. **Prefer supported recovery.** Use the application’s native password-change or reset flow when it can complete safely.
3. **Back up before mutation.** Take a logical database dump or application-consistent backup before changing authentication state. Do not use `docker compose down -v` as a recovery step.
4. **Keep secrets out of logs and arguments.** Prompt on a private TTY or use protected input; do not put passwords, hashes, tokens, or database passwords in chat, Git, shell history, process arguments, or the skill library.
5. **Change the smallest possible field.** Update only the account credential column. Do not alter encryption keys, history, records, email, database-role passwords, or service volumes unless the recovery plan explicitly requires it.
6. **Verify from the outside.** A successful SQL update is not proof of recovery. Test the real login endpoint, then the client sync/read path.
7. **Report the boundary honestly.** If access or a required secret is missing, stop and ask the operator to run the prepared procedure. Never claim a reset, login, sync, or cleanup that was not observed.

## Endpoint preflight before interactive authentication

Before entering a master password, API key, recovery code, or other credential into a self-hosted client:

1. Read the client configuration without copying secrets into context or logs.
2. Verify the exact hostname and scheme the client is configured to use.
3. Check hostname resolution locally with `getent ahosts <host>` or `resolvectl query <host>` and compare only with a harmless control hostname when diagnosing DNS.
4. If the configured host fails to resolve while unrelated names resolve, stop before authentication. Do not guess a replacement domain, substitute a raw IP for an HTTPS service, edit `/etc/hosts`, weaken TLS, or treat the error as a bad password.
5. Delegate DNS, ingress, reverse-proxy, and service checks to the responsible infrastructure operator. Remote changes require the operator's normal verification and rollback process.
6. Resume the supported registration/login flow only after the endpoint is confirmed.

Keep client setup and server recovery separate: a successful local config write does not prove endpoint reachability, authentication, or sync. Interactive secrets belong in a user-controlled TTY or native pinentry; never inject them through agent tools, process arguments, environment variables, or shell history.

### When the operator corrects the hostname

If the operator supplies an authoritative replacement hostname after a reachability failure, treat the correction as the new source of truth instead of continuing to diagnose the obsolete name:

1. Preserve the exact hostname and scheme supplied; update only the client endpoint field.
2. Re-check resolution with `getent ahosts` or `resolvectl query`.
3. Re-run a non-interactive sync and record its exit status before attempting authentication.
4. If a read-path check is authorized, discard output (for example, `rbw list >/dev/null`) so item names and values do not enter logs or chat.
5. Report separately whether endpoint reachability, sync, read access, login, and unlock were each verified; a successful sync/read path is not proof that an interactive login was just completed.
6. Update durable documentation to make the corrected hostname current while retaining the obsolete hostname only as historical diagnostic context.

See `references/self-hosted-client-preflight.md` for the reusable decision tree and completion evidence.

## Procedure

### 1. Discover the deployment

Collect read-only facts first:

- service URL and whether it is local, LAN-only, or behind a proxy;
- container names, image/version, Compose file, restart policy, and health;
- persistent bind mounts/volumes and the database container;
- account username and the application encryption key location, without printing values;
- current login/session state on each relevant client;
- supported recovery commands and the exact server version.

For a Docker host in a VM, run Docker commands on the guest. Prefer SSH or the guest console over an exposed Docker TCP API; firewalling `2375` is not a reason to weaken the firewall.

### 2. Choose the least destructive path

Use this order:

1. Retrieve the credential from the approved password vault, without changing server state.
2. Use the application’s supported password-change flow if the current credential is known.
3. If the current credential is lost, use a documented administrative database reset that preserves the application’s data and encryption key.
4. Delete/recreate the account only after explicitly accepting the application’s documented data loss and re-encryption consequences.

Do not assume that a new account can decrypt old records. Account password and application encryption key may be independent, but the account identifier, key wrapping, or server-side history lifecycle may still matter.

### 3. Make the change reversible

- Create a protected, timestamped dump before the change and record its path outside Git.
- If a temporary account is needed to obtain an application-generated hash, make its username unique, give it no data, and arrange cleanup with a trap or equivalent.
- Check unique constraints before reusing a generated hash. Remove the temporary row only after the hash has been read and before assigning it to the target when the credential column is unique.
- Use parameterized SQL variables (`psql -v` or the database driver’s bind parameters), not string interpolation.
- If any precondition fails, abort before mutating the target account and clean up the temporary row.

### 4. Verify and close out

Verify in this order:

1. Database update affected exactly the intended account.
2. Login endpoint returns the expected success status with the new credential; discard the response body if it contains a session token.
3. Application client can log in without replacing the encryption key.
4. Sync completes and previously encrypted data is readable.
5. Containers remain healthy and logs show no new authentication/database errors.
6. Temporary account, temporary key authorization, and unnecessary open-registration settings are removed.
7. Keep the backup until rollback is no longer needed, then dispose of it according to the backup policy.

## Remote access without broadening privileges

When the existing SSH path is unavailable, use the narrowest operator-approved route:

- guest console first when practical;
- otherwise a short-lived Ed25519 key whose public half is added to the service user on the guest;
- avoid adding a recovery key to the Proxmox host root account when guest access is sufficient;
- do not reuse an unrelated backup private key merely because it is present on disk;
- remove the authorized-key line and local private key after verification.

Never paste a private key into chat or into a wiki. Public keys may be transferred through the operator’s console, but access still needs explicit scope and cleanup.

## Common pitfalls

| Symptom | Likely cause | Safer response |
|---|---|---|
| Native password change returns unauthorized | It validates the current password | Use the approved vault or an administrative reset; do not loop guesses |
| New password works but history is unreadable | Encryption key was replaced or a new account was registered | Restore the original key and stop destructive account recreation |
| SQL update fails with a uniqueness error | Temporary and target rows have the same generated hash | Delete the temporary row first, then update the target |
| Containers disappear or history is gone | `compose down -v` or volume deletion | Restore from backup; never use volume deletion as a reset |
| Login appears successful but client remains empty | Session/config points elsewhere or key is wrong | Check address, username, key identity, sync status, and server version |
| Remote Docker commands fail | Local socket/permissions or guest boundary | Use the guest’s SSH/console; do not open an unauthenticated Docker API |

## Reference index

- `references/atuin-account-recovery.md` — Atuin legacy/self-hosted PostgreSQL behavior, Argon2id reset pattern, and validation boundary.
- `references/self-hosted-client-preflight.md` — endpoint, DNS, interactive-authentication, delegation, and verification checklist for self-hosted clients.
