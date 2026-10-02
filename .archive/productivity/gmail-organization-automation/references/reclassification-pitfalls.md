# Gmail reclassification pitfalls and recovery notes

This reference captures durable lessons from correcting Sr. Kiwel's Gmail labels after messages such as AliExpress and Globoplay were routed to incorrect categories.

## What went wrong

A broad rule set was used for reclassifying already-organized messages. It put high-priority category queries like `Compras e Entregas`, `Streaming`, and `Redes Sociais` before other broad rules, but the queries included loose terms such as `compra`, `oferta`, `LinkedIn`, `Globoplay`, `AliExpress`, `login`, `segurança`, and footer language. Since old messages often contain unrelated snippets, app-store badges, social links, privacy text, and marketing boilerplate, tens of thousands of messages could match a broad category that was not their real sender/source.

## Safer rule design

Use exact sender/domain rules for known sources:

- AliExpress: `from:(aliexpress.com OR selections.aliexpress.com OR notice.aliexpress.com OR mail.aliexpress.com)`
- Shopee: `from:(shopee.com.br OR mail.shopee.com.br)`
- Globoplay: `from:(globoplaymkt.globo.com OR globoplay.com)`
- Paramountplus/Paramount+: `from:(paramountplus.com OR paramount.com)`
- NiceHash: `from:nicehash.com` → label `Crypto` (create the label before moving)
- LinkedIn: `from:linkedin.com`
- Samsung: `from:(samsung.com OR email.samsung.com)`
- voeazul-news: `from:voeazul-news.com.br`
- Hotmart/Udemy: `from:(hotmart.com OR e.udemymail.com OR udemy.com)`
- Ollama: `from:ollama.com`
- Correio do Povo: `from:correiodopovo.com.br`
- Claro: `from:(claro.com.br OR claro.com)`
- Ticketmaster: `from:(ticketmaster.com.br OR email.ticketmaster.com.br)`

Use broad terms only for new Inbox triage, and even then place exact sender rules first.

## Verification pattern

After a correction, count each target brand across every organization label. A clean result should show the target brand under its intended label only, except for legitimate unorganized or unrelated labels.

Example verification shape:

```json
{
  "Globoplay": {"labels": {"Streaming e Assinaturas": 142}},
  "LinkedIn": {"labels": {"Redes Sociais": 1177}},
  "Correio do Povo": {"labels": {"Notícias e Newsletters": 86}}
}
```

Then run the exact reclassification script again. A successful idempotency check returns:

```json
{"total_modified": 0, "failures": []}
```

## Recovery pattern for a bad bulk label move

If a bulk correction misroutes many messages:

1. Get the current Gmail `historyId` before additional label operations when possible.
2. Query Gmail History with `historyTypes=['labelAdded','labelRemoved']` from a recent valid `startHistoryId`.
3. Build per-message recent label change records.
4. Reverse only safe/simple moves: messages with exactly one organization label added and one removed, and whose `(source, destination)` pair matches the bad operation's report.
5. Re-run targeted exact sender/domain reclassification, not a broad global classifier.

Do not encode a stale `historyId` in a reusable script; it is valid only for a limited window.
