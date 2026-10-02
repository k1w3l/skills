---
name: hermes-dashboard-operations
description: "Use for Hermes dashboard lifecycle and auth operations."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, dashboard, web-ui, authentication, security, operations]
    related_skills: [hermes-agent]
    created_by: agent
---

# Hermes Dashboard Operations

Operate the Hermes web dashboard as a security-sensitive backend service. This
skill covers lifecycle management, local versus remote exposure, authentication
providers, password rotation, and evidence-based verification. It complements
the broader `hermes-agent` skill, which is protected and covers the full Hermes
CLI/configuration surface.

Use this skill whenever the operator asks to start, stop, inspect, expose,
secure, connect to, or change credentials for `hermes dashboard`, or when Hermes
Desktop must connect to a remote Hermes backend.

The password-rotation recipe, including a hidden-input shell sequence and the
session-invalidation option, lives in
`references/basic-auth-rotation.md`.

## Security model

1. **Loopback is the default safe bind.** Keep the dashboard on `127.0.0.1`
   unless remote access is required; use an SSH tunnel or a trusted VPN when
   practical.
2. **Non-loopback binds require authentication.** Current Hermes hardening
   engages the auth gate for a public/LAN bind. `--insecure` is deprecated and
   does not bypass this gate. A missing provider should fail closed rather than
   be worked around by disabling authentication.
3. **Choose the provider for the exposure.** Use OAuth (Nous Portal) or a
   properly configured OIDC provider for internet-facing deployments. The
   bundled username/password provider is intended for a trusted LAN or VPN,
   not direct public-internet exposure.
4. **Separate the password from the token-signing secret.**
   `dashboard.basic_auth.password_hash` authenticates new logins;
   `dashboard.basic_auth.secret` signs stateless session tokens. Changing the
   password hash alone does not revoke already-issued sessions.
5. **Never expose credentials in evidence.** Check only whether an env key is
   present; never print `.env`, raw passwords, hashes, signing secrets, cookies,
   authorization headers, or process environments containing them.

## Discovery before mutation

Run the minimum read-only checks needed to identify the active instance,
profile, bind, port, and provider:

```bash
hermes dashboard --status
hermes config path
hermes config env-path
curl -s http://127.0.0.1:9119/api/status
```

From the status response, retain only non-secret fields such as
`auth_required`, `auth_providers`, and `version`. If a named profile is in use,
apply the profile consistently to every CLI invocation (for example,
`hermes --profile NAME dashboard --status` and the corresponding config paths).

Determine precedence before changing credentials:

- `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` overrides
  `dashboard.basic_auth.username`.
- `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` overrides a configured hash because it
  is hashed in memory at load time.
- `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` overrides the configured hash.
- A password/hash in `.env` therefore wins over a value written with
  `hermes config set`; update the higher-precedence source or remove the stale
  override deliberately.

## Lifecycle operations

Use the CLI rather than killing a process by PID:

```bash
hermes dashboard --status
hermes dashboard --stop
hermes dashboard --host 127.0.0.1 --port 9119 --no-open
```

For a trusted remote/LAN backend, bind to the required non-loopback address
and configure an auth provider first:

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open --skip-build
```

`--skip-build` is appropriate only when the existing web bundle is already
built. If a service manager, container, or supervisor owns the dashboard, use
that manager for the restart after changing configuration; do not leave a
second dashboard process competing for the same port.

## Username/password configuration and rotation

The bundled basic provider activates only when a username and either a
`password_hash` or a plaintext `password` are configured. Prefer the scrypt
hash form:

```yaml
dashboard:
  basic_auth:
    username: admin
    password_hash: "scrypt$..."
    password: ""                  # do not keep plaintext here
    secret: "<stable signing secret>"
```

Use the hidden-input recipe in the reference to generate a new scrypt hash,
then write it with the supported config command:

```bash
hermes config set dashboard.basic_auth.password_hash "$HASH"
unset HASH
```

After changing `config.yaml` or `.env`, restart the dashboard. Config is read
when the server/plugins are loaded; changing the file does not change the
already-running provider.

If the operator wants a full credential cutover, rotate the signing secret as
well, then restart:

```bash
hermes config set dashboard.basic_auth.secret "$(openssl rand -base64 32)"
```

Rotating `secret` invalidates existing stateless access and refresh tokens. Do
not rotate it merely to change a password when preserving active sessions is
intended.

## OAuth and OIDC

For a public or broadly reachable dashboard, prefer OAuth/OIDC instead of the
shared basic credential:

- Nous Portal: `hermes dashboard register`, then verify the configured OAuth
  client ID without printing it.
- Self-hosted OIDC: configure the issuer and public PKCE client ID; keep the
  identity provider responsible for user accounts, MFA, and password policy.

Never claim an OAuth setup is complete from a written config value alone:
verify the provider appears in `/api/status` and complete an actual browser
login/callback when the task requires end-to-end proof.

## Verification checklist

After lifecycle or auth changes:

1. Confirm exactly one intended dashboard process is listening and the expected
   bind/port are in use.
2. Query the public status endpoint and confirm the intended gate/provider:

   ```bash
   curl -s http://127.0.0.1:9119/api/status \
     | jq '{auth_required, auth_providers, version}'
   ```

3. For basic auth, test the login through the browser or the supported login
   flow; do not put the password in a command-line argument or URL.
4. Confirm an old session behaves according to the intended policy: it should
   remain valid when only the hash changed, and fail after the signing secret
   was intentionally rotated.
5. Report provider, bind, port, restart result, and verification outcome;
   report only secret presence/absence, never secret values.

## Pitfalls

- **Editing the wrong layer:** env overrides beat `config.yaml`; inspect key
  presence and precedence before declaring a password change effective.
- **Changing the file but not the process:** restart the dashboard or its owning
  service after auth/config changes.
- **Assuming password rotation logs everyone out:** basic sessions are stateless
  HMAC tokens; rotate `secret` when immediate invalidation is required.
- **Using `--insecure` on a public bind:** it is no longer an auth bypass.
- **Using basic auth on the public internet:** use OAuth/OIDC for external
  exposure; basic is a shared credential with no MFA or per-user identity.
- **Printing hashes as harmless diagnostics:** a password hash is still a
  credential-bearing secret and must stay out of logs, transcripts, and reports.
- **Starting a second instance blindly:** inspect `--status` and use the owning
  supervisor to avoid port conflicts and inconsistent configuration.

## Completion report

Give a concise evidence-backed report containing:

- the selected profile and dashboard bind/port;
- the active auth provider and whether the gate is required;
- the configuration source changed (`config.yaml` or `.env`) without values;
- restart/service result;
- verification output reduced to non-secret fields;
- whether existing sessions were intentionally preserved or invalidated.
