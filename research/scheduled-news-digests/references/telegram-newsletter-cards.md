# Telegram newsletter cards and feedback loops

Use this pattern when a scheduled digest must look like a professional Telegram newsletter rather than a plain-text cron delivery.

## Architecture

Keep four responsibilities separate:

1. **Collector:** fetch and normalize RSS/Atom/JSON candidates.
2. **Curator agent:** select items and write concise title, summary, and personalized relevance.
3. **Card delivery tool:** send one Telegram photo message per article with caption and inline keyboard.
4. **Feedback store:** persist per-article ratings and expose aggregate signals to the next collector run.

Cron's ordinary final-response delivery is suitable for text, but it cannot express a multi-card newsletter with one image and one keyboard per article. For a card-only job whose empty runs are intentionally silent, set cron delivery to local/suppressed and let a dedicated plugin tool perform the Telegram sends. If the editorial contract requires a no-highlights notice, retain an explicit `telegram:<chat_id>` target (and an explicit failure target when supported): the successful-card branch may return `[SILENT]`, while the empty and failed branches must use ordinary cron delivery. After confirmed tool success, the agent may return the silence sentinel solely to prevent a duplicate plain-text delivery.

## Card contract

Each selected article should carry:

- stable ID derived from the canonical URL;
- translated/editorial title;
- original source;
- a factual summary sized to the editorial contract;
- canonical article URL;
- optional explicit thumbnail URL;
- optional personalized relevance only when the operator explicitly wants a separate block.

For Sr. Kiwel's technology newsletter and Status R, use about three contextualized sentences (roughly 60–90 words when evidence permits), omit personalized relevance and the `why` field, and never pad sparse source data with inference.

Send a short edition header, then one card per article. A good card uses:

- 16:9 image (for example 1280×720);
- source badge and article number;
- readable title overlay with dark contrast gradient;
- concise HTML caption below the image;
- first keyboard row: `👍 Gostei` and `👎 Não é para mim`;
- second row: `🔗 Ler matéria completa` URL button;
- short closing message explaining that ratings improve future editions.

Telegram photo captions are limited, so keep them compact and escape HTML entities. Prefer actual source imagery discovered from RSS media fields or `og:image`/`twitter:image`. If retrieval fails, generate a branded fallback image; every card should still have a thumbnail.

## Persistent feedback

Use SQLite (WAL mode) or an equivalent durable store with two tables:

- `articles`: ID, URL, title, source, summary, relevance, thumbnail, sent timestamp;
- `feedback`: article ID, user ID, rating (`1` or `-1`), updated timestamp, unique per article/user.

Callback data must stay within Telegram's limit; a compact shape such as `nf:l:<12-char-id>` and `nf:d:<12-char-id>` is sufficient. Authorize the callback user before writing. On a tap:

1. upsert the rating;
2. edit only the message keyboard so the selected button becomes `✅`;
3. answer the callback promptly with confirmation;
4. keep the article link button intact.

A click is explicit feedback and may immediately apply a **soft** ranking adjustment. Repeated likes/dislikes across a source or topic should carry more weight than one click. Do not turn one dislike into a permanent ban unless the user explicitly asks.

At collection time, inject compact feedback context:

- source-level likes, dislikes, and net score;
- recent rated titles/topics;
- optionally decayed historical scores.

The curator should favor liked patterns, reduce rejected patterns, and retain some diversity/exploration.

## Hermes plugin pattern

Implement this as a user plugin under `~/.hermes/plugins/<name>/`:

- register a dedicated tool such as `send_newsletter_cards`;
- keep the Telegram token in Hermes' existing secret environment, never in plugin files or prompts;
- resolve the token through `agent.secret_scope.get_secret("TELEGRAM_BOT_TOKEN")`; cron workers may not inherit `.env` into `os.environ`, so a non-multiplexed plugin should call the canonical `load_hermes_dotenv(hermes_home=get_hermes_home())` before retrying the scoped lookup, while multiplexed workers must use only the active profile scope or `build_profile_secret_scope(get_hermes_home())` and never borrow another profile's environment;
- keep non-secret routing/authorization configuration in a plugin config file or `config.yaml`;
- use the Telegram Bot API `sendPhoto` with `reply_markup` for each card.

Hermes' Telegram adapter handles known callback prefixes. If there is no generic callback hook for a custom prefix, a user plugin can narrowly wrap the adapter callback method: intercept only its own prefix and delegate every other callback unchanged to the original method. Make the patch idempotent and apply it at plugin registration. This avoids editing protected/bundled core files, though it should be regression-tested after Hermes upgrades because it couples to an adapter method.

On Hermes versions with lazily loaded, namespaced platform plugins, do not import `plugins.platforms.telegram.adapter` directly: that may create and patch a second class object while the gateway runs `hermes_plugins.telegram_platform.adapter.TelegramAdapter`. Resolve Telegram through `gateway.platform_registry.platform_registry.get("telegram")`, import `entry.adapter_factory.__module__`, and patch the class from that runtime module. Add a regression test asserting the patched class is the same class used by the resolved adapter factory, then restart the gateway.

Enable the plugin and restart the gateway. Tool availability is static per process/session: an already-running CLI agent may not see a newly enabled tool even after the gateway restarts. Verify through a fresh Hermes process or the restarted gateway—the same execution path scheduled cron will use.

## End-to-end verification

Do not stop at “cron succeeded.” Verify all layers:

1. Plugin is enabled and its toolset appears in `hermes tools list`.
2. Gateway restarts cleanly and loads the plugin.
3. Collector returns real candidates and feedback context.
4. A fresh-process cron run calls the card tool.
5. Tool result reports the number of cards sent and any per-item errors.
6. Feedback database contains the sent article rows.
7. A callback test records a rating, edits the keyboard, and answers the query.
8. Ideally, ask the user to tap one real button and confirm the production database changed.

When a tool was enabled during the current conversation, distinguish a stale current-session failure from a real scheduled-gateway failure before changing the design.
