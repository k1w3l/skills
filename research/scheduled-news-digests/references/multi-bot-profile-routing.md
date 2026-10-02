# Routing scheduled Telegram newsletters across multiple Hermes bots

Use this reference when different scheduled newsletters must be sent by different Telegram bot identities.

## Capability and routing model

Hermes supports multiple profiles. Each profile has its own Hermes home, `.env`, cron jobs, gateway state, and Telegram credentials. A Telegram bot identity is therefore selected by the profile that runs the job, not by an argument to the newsletter-card tool. The `send_newsletter_cards` interface has no per-call bot selector; its Telegram API calls resolve the current profile's scoped credentials and routing configuration.

A single default gateway can serve several profiles when the default profile enables:

```yaml
gateway:
  multiplex_profiles: true
  multiplex_profile_allowlist:
    - newsletter
    - status-r
```

The default profile is always served. Telegram/Discord/Slack-style polling platforms work in multiplex mode as long as every profile has a different bot token. Hermes rejects reuse of the same `(platform, token)` across profiles. The alternative is one independent gateway process/service per profile, which gives stronger process isolation but requires managing each service separately.

## Safe migration pattern

1. Inventory the exact existing job with `cronjob(action="list")` or `hermes cron list --all`; preserve its schedule, collector script, prompt, toolsets, and editorial rules.
2. Create named profiles such as `newsletter` and `status-r`. If cloning configuration, replace the copied Telegram token before starting or multiplexing the profiles; never leave the original token duplicated.
3. Configure each profile's Telegram token and target chat locally through that profile's setup or `.env`. Never put tokens in prompts, job definitions, logs, or chat messages. The bot must have been started in a DM or added to the target group.
4. Recreate or move each newsletter job under the profile whose bot should send it. With the CLI, target the profile explicitly (`hermes -p newsletter cron ...` or its profile alias). Do not leave the original default-profile job active after the replacement is validated, or the edition may be sent twice.
5. For card-based newsletters, keep ordinary cron delivery as `local`/suppressed. The direct card tool sends the Telegram messages; changing `deliver` to ordinary `telegram` delivery can create a duplicate plain-text edition or route it through the wrong identity.
6. Enable either the default-profile multiplexer or separate profile gateways, but do not start secondary profile gateways while the multiplexer is serving them.
7. Verify profile-specific cron state, gateway health, collector output, the fresh-process card-tool result, and Telegram delivery. Test a feedback callback only after the cards are confirmed sent.

## Operational distinction

- **Profile routing** chooses which bot token sends the edition.
- **Chat routing** chooses which Telegram chat receives it; both bots may use the same chat ID if the user has started both bots, or they may use different chats.
- `profile_routes` is for routing inbound messages to profiles, especially when one bot is shared; it is not a substitute for giving each profile its own Telegram token.

For scheduler safety and job mutation evidence, also follow `hermes-cron-operations`.