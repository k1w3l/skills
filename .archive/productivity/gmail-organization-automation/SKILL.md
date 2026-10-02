---
name: gmail-organization-automation
description: "Operate and maintain Sr. Kiwel's Gmail organization automations: rule design, reclassification, verification, and safe label corrections."
version: 1.0.0
author: agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [gmail, email, labels, automation, google-workspace]
    related_skills: [google-workspace]
created_by: agent
---

# Gmail Organization Automation

Use this skill when Sr. Kiwel asks to organize Gmail, adjust email classification rules, audit already-organized messages, or fix messages that landed under the wrong label.

## Core principles

1. **Do not delete mail.** Organization means adding the correct label and removing Inbox/category labels when appropriate.
2. **Ask approval before broad cleanup or new Gmail modifications** unless the user explicitly directs the correction in the same message.
3. **Prefer exact sender/domain and brand-specific rules over broad keyword rules.** Broad words in snippets, footers, and legal/privacy text can misroute large volumes of mail.
4. **Preserve priority ordering.** Exact brand/sender rules should run before broad categories such as security, finance, newsletters, or social.
5. **Verify after changing labels.** Run a distribution/count check by target brand or sender and confirm there are no remaining messages in wrong organization labels.
6. **Report concise results only:** total moved, key label destinations, failures, and verification status.

## Known classification preferences for Sr. Kiwel

- Shopee, AliExpress → `Compras e Entregas`
- Globoplay, Paramountplus/Paramount+ → `Streaming e Assinaturas`
- NiceHash → `Crypto` (create the label first if missing)
- LinkedIn, Facebook, Instagram, X/Twitter → `Redes Sociais`
- Samsung, voeazul-news, Laçador de Ofertas → `Promoções e Marketing`
- Hotmart, Udemy → `Cursos e Carreira`
- Ollama → `IA`
- Correio do Povo → `Notícias e Newsletters`
- KM de Vantagens → `Cashback e Benefícios`
- Claro → `Financeiro e Contas`
- Google Agenda, Ticketmaster → `Viagens e Eventos`

## Safe workflow for correcting already-organized mail

1. Load Google credentials through the existing Hermes Google token; refresh if expired.
2. List current Gmail labels and map label names to IDs.
3. Define organization labels centrally. Avoid duplicating rule lists across scripts without updating all copies. Ensure new destination labels (for example `Crypto`) are created before the first reclassification run.
4. For each exact sender/domain rule, query messages under every *wrong* organization label.
5. Use `batchModify` to add the target label and remove only the wrong organization label.
6. Do **not** remove unrelated labels, system labels, or all labels globally.
7. After modification, run a verification count per brand/domain across all organization labels.
8. Re-run the exact correction script; it should return `total_modified: 0`.

## Pitfalls

- **Do not classify by raw brand words alone** when the word may appear in ads, news, job posts, or snippets. Example: a Veduca job-post email mentioning Shopee is not necessarily Shopee e-commerce.
- **Do not use broad priority rules for global reclassification.** Applying “first matching category wins” to already-organized mail can move tens of thousands of messages incorrectly because old newsletters and snippets contain many generic category words.
- **Do not let footer text dominate.** Many marketing emails contain “redes sociais”, app-store badges, privacy notices, unsubscribe links, login/security boilerplate, or payment words.
- **If a bulk correction goes wrong, use Gmail History immediately** to identify labelAdded/labelRemoved pairs and reverse only those recent changes.

## References

- `references/reclassification-pitfalls.md` — detailed lessons from correcting misclassified already-organized Gmail messages.
