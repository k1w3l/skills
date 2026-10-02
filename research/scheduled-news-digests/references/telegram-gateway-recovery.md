# Telegram gateway recovery and delivery verification

Use this reference when a Telegram-based digest or direct message stops arriving, especially when the bot appears configured but the user cannot obtain a normal agent reply.

## Diagnostic distinction

A Telegram transport connection and a functioning agent run are separate stages:

1. `gateway status` / service state proves the process exists.
2. Gateway logs showing `telegram connected` prove polling is established.
3. An `inbound message` followed by `Agent error` proves Telegram received the message but the agent path failed.
4. A `Sending response` line is useful evidence of an attempted outbound response, but the Telegram API acceptance must still be checked when delivery is in doubt.

Do not rotate a token merely because replies stopped. First inspect logs and isolate transport versus agent execution.

## Proven recovery sequence

1. Inspect without exposing secrets:

   ```bash
   hermes gateway status
   hermes status --all
   hermes config env-path
   systemctl --user status hermes-gateway --no-pager
   ```

   Read only recent gateway lines matching Telegram, inbound, agent error, exception, failed send, polling, or connection.

2. If an inbound message is followed by an agent import/runtime error, test the installed code in a fresh interpreter using the gateway venv. A fresh import that succeeds while the long-lived gateway keeps failing is evidence of stale/inconsistent process state, not proof that the Telegram token is invalid.

3. Restart the gateway after code, plugin, or tool changes. A long-lived gateway may retain old module state, and a newly enabled plugin/tool is not necessarily visible to already-running agent workers.

   ```bash
   hermes gateway restart
   ```

   If the command is rejected because it is being invoked from inside the gateway process, do not repeatedly retry from that same process. Open a genuinely separate shell/session outside the gateway and run the restart there. The verified fallback is an interactive shell started independently, followed by:

   ```bash
   systemctl --user restart hermes-gateway.service
   ```

4. Verify after the restart, not just the exit code:

   - service is `active (running)`;
   - logs show `Connected to Telegram (polling mode)` and `telegram connected`;
   - there are no new `Agent error`, `ImportError`, `Traceback`, or `failed to send` lines after the restart boundary;
   - the bot identity endpoint `getMe` returns `ok: true` without printing the token;
   - if an outbound test is authorized, send one natural recovery message through `sendMessage` and check the API result is `ok: true`.

5. Ask the operator to send a short inbound message after recovery. Confirm its new inbound log entry and successful agent response before declaring the complete round trip verified.

## Safe evidence handling

- Never print, persist, or repeat `TELEGRAM_BOT_TOKEN`.
- Do not call `getUpdates` as a casual verification step while the gateway is polling; it can compete with the gateway or consume queued updates.
- A direct `sendMessage` test verifies outbound API acceptance only; it does not prove inbound agent processing.
- Historical errors must be separated from post-restart errors using an explicit timestamp/process boundary.
- Telegram fallback-IP warnings may indicate a degraded network path; treat them as transport evidence, but do not confuse them with an agent import/runtime failure.

## Operator-facing report

State separately what is proven: gateway active, Telegram polling connected, API accepted an outbound message, agent errors absent after restart, and inbound round trip confirmed or still awaiting the operator's reply. Avoid claiming full recovery from service status alone.
