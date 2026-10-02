---
name: hermes-gateway-operations
description: "Operate Hermes messaging gateway credentials and runtime safely: update platform tokens, validate bots, restart or run the gateway, and report service state."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, gateway, telegram, operations, credentials]
    created_by: agent
---

# Hermes Gateway Operations

Use this skill when Sr. Kiwel asks to update or troubleshoot Hermes gateway messaging platforms such as Telegram, Discord, Slack, or similar adapters.

This complements the protected `hermes-agent` skill. Load `hermes-agent` first for authoritative CLI/config docs, then use this skill for the local operational pattern and safety checks.

## Credential safety

- Platform tokens are secrets. Do not save them in memory or skills.
- Do not print full tokens in final replies. Report only validation results such as bot username/ID.
- Store secrets in the active profile `.env`, not in `config.yaml`, unless Hermes docs for that platform explicitly say otherwise.
- Use `hermes config env-path` to locate the active profile's `.env`; do not assume a path when profiles may be in use.

## Updating a Telegram bot token

Sr. Kiwel-specific Telegram gateway notes are in `references/sr-kiwel-telegram-gateway.md`.

1. Load `hermes-agent` first for current gateway command syntax.
2. Find the active environment file:

   ```bash
   hermes config env-path
   ```

3. Update or add the `TELEGRAM_BOT_TOKEN=` line in that `.env` file. Preserve file permissions when possible; use `0600` for newly created secret files.
4. Validate the token with Telegram without echoing it:

   ```python
   import json, urllib.request
   token = 'read from .env, do not print'
   with urllib.request.urlopen('https://api.telegram.org/bot' + token + '/getMe', timeout=10) as r:
       data = json.load(r)
   print({'ok': data.get('ok'), 'bot_username': data.get('result', {}).get('username'), 'bot_id': data.get('result', {}).get('id')})
   ```

5. Restart the gateway:

   ```bash
   hermes gateway restart
   hermes gateway status
   ```

6. If the user service cannot restart because systemd linger is disabled, report the exact fix and either ask permission to run it or start the gateway manually for the current session:

   ```bash
   sudo loginctl enable-linger "$USER"
   hermes gateway install
   hermes gateway restart
   ```

   Temporary fallback:

   ```bash
   hermes gateway run
   ```

   Run it under Hermes background process management if starting it from an agent turn.

## Reporting format

Report briefly:

- Which env path was updated.
- Whether platform API validation succeeded.
- Public bot/account identifier if available, never the token.
- Gateway state and PID if running.
- Whether it is running as a persistent service or only manually.

## Pitfalls

- Config changes do not always affect a running gateway until restart.
- `hermes gateway restart` can fail on headless servers/VMs if user linger is not enabled; this is a setup state. The durable fix is enabling linger and installing/restarting the gateway service.
- Do not conflate CLI session state with gateway runtime state; always verify with `hermes gateway status` after a restart or manual start.
