# Telegram gateway update notes

Session-derived operational details for Sr. Kiwel's Hermes gateway.

## Observed pattern

- Active env path was resolved with `hermes config env-path` to `/home/kiwel/.hermes/.env` in the default profile.
- Telegram token key used by Hermes gateway: `TELEGRAM_BOT_TOKEN`.
- Token validation via Telegram `getMe` returned a valid bot:
  - Username: `kiwel_bot`
  - Bot ID: `7921784280`
  - Can join groups: `true`

## Runtime note

`hermes gateway restart` reported that the user service could not be restarted because linger was not enabled for user `kiwel`. In that situation, Hermes can run the gateway manually as a temporary fallback, but the durable service fix is:

```bash
sudo loginctl enable-linger kiwel
hermes gateway install
hermes gateway restart
hermes gateway status
```

Do not store Telegram bot tokens in this reference; validate public bot metadata only.
