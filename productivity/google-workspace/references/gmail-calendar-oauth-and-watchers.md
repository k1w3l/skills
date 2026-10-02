# Gmail/Calendar OAuth and watcher notes

Session-derived notes from configuring Sr. Kiwel's Gmail + Google Calendar automation.

## OAuth lessons

- For Gmail monitoring plus Calendar creation, start with least privilege:
  - `https://www.googleapis.com/auth/gmail.readonly`
  - `https://www.googleapis.com/auth/calendar.events`
- If the user wants email organization, labels, sending, and full Calendar operations, request:
  - `https://www.googleapis.com/auth/gmail.readonly`
  - `https://www.googleapis.com/auth/gmail.send`
  - `https://www.googleapis.com/auth/gmail.modify`
  - `https://www.googleapis.com/auth/calendar`
- If Google reports the app is in Testing and only developer-approved testers can access it, the fix is to add the user's Google account under Google Cloud Console -> OAuth consent screen / Audience -> Test users.
- If Google redirects to `unknownerror`, generate a fresh OAuth URL. If needed, retry first with narrower scopes, then broaden after the user confirms all scopes were added to the consent screen.
- `http://localhost:1` refusing connection after authorization is expected. The user must paste the full URL from the browser address bar containing `code=`.
- A 403 during a live Calendar check may simply mean the check endpoint requires a broader scope than the one granted. For example, `calendar.events` may not allow listing calendar lists. Verify against the operation actually needed or request broader `calendar` access.
- Prefer the Hermes venv interpreter if system `python3` lacks Google API dependencies: `~/.hermes/hermes-agent/venv/bin/python`.

## Watcher pattern

Use deterministic cron scripts with `no_agent=true` for passive monitoring:

- Keep state in a JSON file under `~/.hermes/` containing seen Gmail message IDs.
- Query Gmail with relevant search terms and a bounded window such as `newer_than:7d` or `newer_than:14d`.
- Print nothing when there are no new matches, so cron delivery stays silent.
- Print a compact alert when new matches appear.
- Do not create Calendar events automatically unless the user has explicitly allowed automation for trusted senders.

## Finance watcher terms

Useful positive terms:
`fatura`, `boleto`, `aluguel`, `vencimento`, `cobrança`, `conta`, `cartão`, `pagamento`, `invoice`, `bill`, `due`.

Useful noise terms:
`promoção`, `oferta`, `newsletter`, `wishlist`, `confirmação de pagamento`, `pagamento confirmado`, `código`, `investimento`, `alerta de segurança`.

## Events / travel / lodging watcher terms

Useful positive terms:
`ingresso`, `ticket`, `convite`, `evento`, `show`, `festival`, `cinema`, `teatro`, `passagem`, `voo`, `embarque`, `check-in`, `reserva`, `hospedagem`, `hotel`, `pousada`, `Airbnb`, `Booking`, `Decolar`, `LATAM`, `Azul`, `Gol`.

Strong senders/domains:
Sympla, Eventbrite, Uhuu, Tickets For Fun, Ingresso.com, Ticketmaster, Booking, Airbnb, Decolar, LATAM, Gol, hotels/pousadas, Uber.

Pitfall: avoid over-broad sender substrings. Matching raw `latam` can falsely match `samsunglatam`; prefer domain-specific patterns such as `latamairlines` or `@latam`.

Useful noise terms:
`promoção`, `oferta`, `newsletter`, `quer viajar`, `dicas de viagem`, `milhas em dobro`, `LinkedIn`, `Google Agenda`, `notificação:`, retail promotions.

## Alert format

Recommended alert shape:

- De: sender
- Assunto: subject
- Data: message date
- Prévia: useful snippet
- ID: Gmail message id

Recommended closing sentence:
"Posso abrir qualquer e-mail listado, extrair data/horário/local e, com sua confirmação, criar o evento no Google Calendar."
