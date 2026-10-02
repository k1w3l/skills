# Multi-profile Telegram routing for Horus monitoring

Use this recipe when the monitoring profile has its own Telegram bot but Hermes also runs another profile (for example, a default assistant) on the same host.

## 1. Establish ownership and architecture

1. Inventory the profiles and the live gateway before changing jobs:
   ```bash
   hermes profile list
   hermes gateway status
   hermes -p <profile> gateway status
   ```
2. Read only non-secret metadata from each profile's `.env`; validate each `TELEGRAM_BOT_TOKEN` with Telegram `getMe` and record only the bot username/identity. Never print, copy, compare, or persist token values.
3. If the default gateway has `gateway.multiplex_profiles: true`, it is the single inbound process and scheduler. Each served profile must have its own unique Telegram token. Do not start a named profile gateway separately while the multiplexer serves it.
4. If process-level isolation is required instead, use each profile's managed service and obtain approval before changing or restarting an existing gateway. Keep the two architectures separate; do not run a second poller for one token.

## 2. Make cron delivery address the correct bot

1. A cron job with `deliver=telegram` needs a captured origin or a home channel. A script-created job with neither has no delivery target; this is a configuration failure, not a notification.
2. For a secondary profile under a multiplexed gateway, use an explicit target such as `telegram:<chat_id>` and add a matching route in the **default** profile's `gateway.profile_routes`:
   ```bash
   env -u HERMES_HOME hermes config set gateway.profile_routes \
     '[{"name":"<profile>-telegram-owner","platform":"telegram","chat_id":"<chat_id>","profile":"<profile>"}]'
   ```
   Preserve existing routes rather than replacing them. Use the official config writer, then read the setting back with secrets and chat identifiers redacted.
3. Create or edit the jobs in the monitoring profile, not in the default assistant profile:
   ```bash
   hermes -p <profile> cron create 'every 5m' \
     --name 'Horus — watchdog Telegram (5m)' \
     --script horus_watchdog.py --no-agent \
     --deliver 'telegram:<chat_id>'
   ```
4. Keep the target identifier redacted in operator output. Never solve a target problem by copying the other profile's bot token or `.env`.

## 3. Safe cutover order

1. Create the new profile jobs and route first; check `hermes cron doctor` for the profile and verify the scripts exist under that profile's `~/.hermes/scripts/`.
2. Pause the old monitoring jobs in the profile that was delivering as the wrong bot:
   ```bash
   env -u HERMES_HOME hermes cron pause <old_job_id>
   ```
   Do not delete them until the new path has delivered successfully; resuming the paused jobs is the rollback.
3. If the running gateway was started before the new profile/token was configured, restart the **authorized gateway owner** so it re-enumerates profiles. State the expected brief Telegram interruption before doing this.
4. Verify the primary gateway's runtime state, not only a secondary profile's standalone view:
   - `served_profiles` includes the monitoring profile;
   - the primary Telegram state and the profile-specific Telegram state are `connected`;
   - the primary `hermes cron status` has a live ticker;
   - `hermes cron doctor` reports no issues.
5. A private bot cannot send the first DM to a user. Have the user open the new bot and send `/start`; use `/sethome` after that if a home fallback is desired. Only then trigger one monitoring job and inspect `hermes cron list` and `hermes cron runs <job_id>` for `ok` delivery.
6. Remove the paused old jobs only after the new delivery is confirmed and the user has verified the bot identity. If the new path fails, pause it, resume the old jobs, and diagnose the exact target/profile binding.

## 4. Alert and decision semantics

- No-agent cron delivery is a one-way notification. It cannot carry a native decision keyboard; never describe plain text or emoji as an action button.
- For remediation, route the user to an interactive Telegram agent turn and use `clarify`, which renders native inline choices where supported. Include the recommended safe action, an alternative, and defer/no action; require explicit approval before disruptive control.
- Verify delivery through the scheduler's result and gateway state, but do not claim that a person read a message unless the user confirms it. Keep bot tokens, passwords, session tokens, raw API responses, and authentication logs out of skill files, state files, and reports.
