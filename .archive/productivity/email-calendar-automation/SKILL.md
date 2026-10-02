---
name: email-calendar-automation
description: Build and operate automations that read email for bills/faturas/boletos, tickets, travel, lodging, notify the user, and create calendar events after confirmation.
version: 1.0.0
author: J.A.R.V.I.S.
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [email, gmail, calendar, oauth, cron, bills, finance, notifications, travel, events, lodging]
    related_skills: [google-workspace, himalaya]
---

# Email → Calendar Automation

Bulk Gmail organization guidance is in `references/gmail-inbox-organization.md`: approved label taxonomy, no-assistant-name label preference, ignored-sender review workflow, and batchModify patterns for Inbox/category tabs.

Reference added from the Gmail/Calendar setup session: `references/gmail-calendar-oauth-and-watchers.md` documents OAuth scope handling, Google test-user/unknownerror pitfalls, and watcher patterns for bills, events, travel, and lodging.

For Gmail Inbox organization by labels, use `references/gmail-inbox-organization.md`; it captures the approved label set, the sender-ignore workflow, the no-`JARVIS/` label naming correction, and the high-volume `batchModify` pattern for tens of thousands of messages.

Use this skill when Sr. Kiwel wants J.A.R.V.I.S. to monitor incoming emails for important financial items — faturas, boletos, aluguel, contas, cartão, cobrança, vencimentos — and create or suggest Google Calendar events, or to organize Gmail messages into labels by subject/sender.

Use this skill when Sr. Kiwel wants J.A.R.V.I.S. to monitor incoming emails for important financial items — faturas, boletos, aluguel, contas, cartão, cobrança, vencimentos — and create or suggest Google Calendar events. Also use it when he asks to organize Gmail, create labels from subjects/senders, archive/move Inbox messages into labels, or maintain ignored/noise sender lists.

For Gmail/Google Calendar access, load `google-workspace` first. That bundled skill remains the authority for normal OAuth and API usage, but this skill adds the practical automation workflow and local pitfalls discovered while setting up user-specific monitoring.

## Safety policy

1. Reading emails for classification is acceptable once OAuth is configured.
2. Never create, delete, or alter calendar events without explicit user confirmation unless the user has already approved a specific automatic rule/source.
3. Start with “notify + ask confirmation”; only later promote trusted senders to automatic event creation.
4. Do not expose tokens, client secrets, authorization codes, or pasted redirect URLs beyond the immediate OAuth exchange.
5. Prefer narrow scopes first. If the user explicitly authorizes broader access, request the larger Gmail/Calendar scopes.

## Gmail + Calendar OAuth approach

Recommended initial scopes:

- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/calendar.events`

Broader scopes when the user asks for them:

- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.modify`
- `https://www.googleapis.com/auth/calendar`

See `references/google-oauth-gmail-calendar.md` for details on generating authorization URLs, exchanging redirect URLs, and handling scope/check-live quirks.

## Standard workflow

1. Check whether Google auth is already configured:

```bash
/home/kiwel/.hermes/hermes-agent/venv/bin/python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
```

2. If not authenticated, guide the user through OAuth client creation using the `google-workspace` skill.
3. Ask for the downloaded OAuth Desktop JSON path and register it with `setup.py --client-secret`.
4. Generate an OAuth URL using the smallest suitable scope set.
5. Ask the user to paste the full `http://localhost:1/?...code=...` redirect URL.
6. Exchange the URL with `setup.py --auth-code '<full-url>'`.
7. Verify Gmail with a harmless search, e.g. recent messages.
8. For Calendar verification, use an operation compatible with the granted scope; `calendar.events` may not allow listing calendar lists.
9. Build or update a watcher script under `~/.hermes/scripts/` and schedule it with a cron job.

## Watcher design

A good watcher should:

- Search recent Gmail for likely billing keywords.
- Maintain a local seen-ID state file so notifications are not repeated.
- Print nothing when nothing new is found; this keeps script-only cron jobs silent.
- Filter obvious noise: newsletters, promotions, wishlist/sale emails, investment marketing, Google Agenda summaries, security alerts, and payment confirmations already completed.
- Include sender, subject, date, snippet, and Gmail message ID in alerts.
- Invite the user to approve event creation rather than creating events silently.

## Gmail inbox organization workflow

Use this when Sr. Kiwel asks to organize the inbox by labels/markers:

1. Treat inbox cleanup as a two-phase operation. Phase 1 is read-only analysis; Phase 2 is modification.
2. Phase 1 may read a representative `in:inbox` sample, group messages by sender/subject, propose labels, and propose ignore/newsletter senders.
3. Before Phase 2, show the concrete plan: label names, counts, example senders/subjects, and the full list of senders to ignore. Do not apply changes until Sr. Kiwel explicitly approves that concrete plan.
4. Prefer user labels under a clear namespace such as `JARVIS/<category>` so automated organization is reversible and easy to audit.
5. To "move" a Gmail message into a marker, add the target label and remove `INBOX`; do not delete messages.
6. Never put known marketing/newsletter senders into transactional categories just because keywords match. Example: `noreply@voeazul-news.com.br` is Azul propaganda/newsletter, not proof of purchased airfare.
7. Keep an approved ignore-sender list in the watcher/config script where the classification logic uses it, and normalize display senders like `Name <email@domain>` before matching.

Useful Portuguese/English trigger terms:

```text
fatura, boleto, aluguel, vencimento, vence, cobrança, cobranca, conta, cartão, cartao,
pagamento, invoice, bill, due, claro, vivo, tim, oi, nubank, itaú, inter, bradesco,
santander, sicredi, banrisul, caixa, bb, ceee, corsan, dmae, iptu, ipva, seguro,
condomínio
```

Noise terms worth excluding:

```text
promoção, promocao, wishlist, sale, desconto, oferta, newsletter, welcome, bem-vindo,
guarde dinheiro, minhas reservas, google agenda, compromissos diários,
confirmação de pagamento, pagamento confirmado, pagamento realizado, código,
finalizar a compra, marketing, viagem, viajar, tesouro, investimento, alerta de segurança
```

## Gmail inbox organization

When organizing Sr. Kiwel's Inbox, use the detailed workflow in `references/gmail-inbox-organization.md`.

Key rules:

1. First produce a read-only proposal from a sample of Inbox messages; do not modify email during analysis.
2. Show exact label names, message counts, and the candidate ignored/noise senders before applying changes.
3. Do not prefix user-facing Gmail labels with `JARVIS/`; use clean names such as `Financeiro e Contas`, `Compras e Entregas`, and `Viagens e Eventos`.
4. “Move to label” means add the approved Gmail label and remove `INBOX`; do not delete messages.
5. After applying, verify with the Gmail API that all sampled messages have the expected label and no longer have `INBOX`.
6. Keep ignored sender lists explicit and editable. For example, `noreply@voeazul-news.com.br` is Azul marketing/newsletter and should not be treated as a purchased-ticket signal.

## Scheduling pattern

For a script that emits final human-readable alerts itself, use `cronjob` with `no_agent=true`:

```text
schedule: every 30m
script: jarvis_email_finance_watch.py
no_agent: true
```

Cron scripts must live under `~/.hermes/scripts/` and the cron `script` field should be the relative filename, not an absolute path.

### Telegram delivery hygiene for email cron jobs

Sr. Kiwel does not want Telegram notifications to expose internal automation details. Cron/email notification scripts should print only the final user-facing result and should not include job IDs, cron job names, script filenames, internal routine labels, or suggestions such as commands to stop/manage jobs. Keep operational diagnostics in local state/log files instead of Telegram output.

For Gmail organization reports, include a concise summary of what was organized, not just counts. A good report lists totals per mailbox/category plus a few sample sender/subject pairs per label, while still stating that no messages were deleted.

### Known sender classification overrides

Keep explicit sender/domain override lists for watchers and Gmail organization rules so marketing/account/security mail is not misclassified by broad keyword matching:

- Travel/lodging watcher exclusions: `@nomadglobal.com` is account/card mail; `@pichau.com.br` is purchases/delivery/e-commerce.
- Finance/bills watcher exclusions: `@acesso.go.br` is government access/login/security mail, not a bill or invoice.
- Gmail organization rules should route `@nomadglobal.com` to `Financeiro e Contas`, `@pichau.com.br` to `Compras e Entregas`, and `@acesso.go.br` to `Segurança e Acessos`.
- Sr. Kiwel's explicit Gmail routing corrections: Shopee → e-commerce/compras; Hotmart → cursos/estudos; Ollama → IA; Correio do Povo → notícias; Laçador de Ofertas → propaganda/promoções; KM de Vantagens → cashback/benefícios; Google Agenda → eventos; LinkedIn/Facebook/Instagram/X/Twitter → redes sociais; Claro → contas; Ticketmaster → ingressos/eventos.
- When updating scheduled Gmail organization scripts, apply these overrides to every relevant mailbox/category script, not only the Inbox script, and preserve ordering so specific categories like `IA`, `Redes Sociais`, `Cursos`, and `Cashback/Benefícios` run before broader marketing/newsletter rules.

## Pitfalls

- The `google-workspace` setup docs may mention `--services` / `--format`; if the installed bundled script lacks those options, generate the OAuth URL with a small Python snippet using `google_auth_oauthlib.flow.Flow` and save `~/.hermes/google_oauth_pending.json` with `state`, `code_verifier`, `redirect_uri`, and `scopes`.
- On this Hermes install, Google dependencies are available in the Hermes venv. Prefer `/home/kiwel/.hermes/hermes-agent/venv/bin/python` for Google Workspace scripts rather than system `python3`.
- `setup.py --check-live` may fail with 403 after a narrow `calendar.events` grant because it lists calendars via `calendarList.list`, which needs broader Calendar permission. Treat this as a scope mismatch, not failed OAuth, when Gmail calls work and the granted scopes are intentional.
- If Google says the app is in testing and only developer-approved testers can access it, have the user add their own account under Google Cloud Console → OAuth consent/Audience → Test users, then generate a fresh auth URL.
- If the browser ends at `accounts.google.com/info/unknownerror` without `code=`, the exchange cannot proceed. Check consent-screen completeness, test-user status, and scopes, then generate a fresh URL.
