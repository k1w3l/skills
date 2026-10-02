# Self-hosted client endpoint preflight

Use this reference when a client for a self-hosted service cannot register, log in, sync, or reach its configured server.

## Read-only checks

```bash
# Client-side, non-secret state
<client> --version
<client> config show

# Replace <host> with the configured hostname
getent ahosts <host>
resolvectl query <host> 2>/dev/null || true
```

Sanitize configuration output before reporting it. URLs and account identifiers may be personal data; passwords, API credentials, tokens, cookies, encryption keys, and returned item contents are secrets.

## Decision tree

1. **Client configuration is missing or invalid**: use the installed client's documented key names and supported package/setup flow. Verify the saved scheme and hostname.
2. **Hostname resolves**: continue with the supported interactive registration/login flow. Use a native pinentry or a private user-controlled TTY; never place secrets in arguments, environment variables, shell history, logs, or agent input calls.
3. **Hostname does not resolve, but a harmless control hostname does**: stop before authentication. Do not guess a new domain, use a raw IP for HTTPS, add an `/etc/hosts` override, or change TLS verification.
4. **The service is on the homelab**: hand DNS, ingress, reverse-proxy, and service checks to the designated infrastructure operator. Do not administer the remote host directly when the operating policy requires delegation.
5. **Endpoint is confirmed**: repeat registration/login, then verify sync and the client's unlocked/session state. A successful local config write or process start is not sufficient evidence.

## Completion evidence

Report only what was observed:

- sanitized client configuration points to the intended endpoint;
- DNS resolution succeeds for the exact configured hostname;
- registration/login exits successfully when required;
- sync completes;
- client session/unlock state is confirmed without exposing secrets;
- remote diagnostics or changes have a verifiable operator result and no secret data was copied into the report.
