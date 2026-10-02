# Home Assistant battery monitoring notes

Use these notes when creating durable battery alerts/reports for Sr. Kiwel's Home Assistant.

## Pattern that worked

Create a script-only Hermes cron (`no_agent=True`) that runs a deterministic script under `~/.hermes/scripts/`:

- Alert job: runs frequently, prints only when an entity is below threshold, and is silent otherwise.
- Report job: runs once daily and always prints the current battery table.
- Delivery: Telegram by default.

The script should read:

- `HASS_URL` from env or `~/.hermes/.env` with fallback to the known local endpoint.
- `HASS_TOKEN` / `HA_TOKEN` / `HOME_ASSISTANT_TOKEN` from env or `~/.hermes/.env`.

Never echo or store the token in memories, final replies, or skills.

## Entity selection

Initial broad matching by name can include false positives. Battery monitoring should include:

- `bateria` or `battery` in `entity_id` or `friendly_name` with `%` unit.
- Home Assistant entities with `attributes.device_class == "battery"`.

Filter out non-level entities whose names indicate:

- battery power
- battery temperature / temp
- battery state
- battery health
- battery voltage/current
- estado da bateria
- saúde da bateria
- temperatura/potência/tensão/corrente da bateria

These are not charge percentage readings and can create false alerts, e.g. `Battery power: 0` is often not a dead battery.

## Verification checklist

Before scheduling:

1. Run the report script against the live Home Assistant API.
2. Inspect the output for false positives such as temperature, power, health, or state sensors.
3. Run alert mode with `--no-state` or equivalent so verification does not consume cooldown state.
4. If real alert mode was used during testing, clear/reset test state before enabling cron, unless you intentionally want to suppress immediate duplicate alerts.
5. Send an immediate Telegram alert if current readings already meet the threshold and the user expects notification now.

## Cron shape

Use wrapper scripts when the scheduler expects paths relative to `~/.hermes/scripts/`:

- `home_assistant_battery_alert.sh` → calls the Python monitor in alert mode.
- `home_assistant_battery_report.sh` → calls the Python monitor in report mode.

For daily reports at 09:00 America/Sao_Paulo when the scheduler is UTC, use `0 12 * * *` unless scheduler timezone semantics change.

## Output shape

Use a professional, structured report format rather than a loose bullet list. Include:

- Title in uppercase, e.g. `⚠️ RELATÓRIO DE ALERTA — BATERIA CRÍTICA` or `🔋 RELATÓRIO DIÁRIO — BATERIA DOS SENSORES`.
- Divider line.
- System name, timestamp in `America/Sao_Paulo`, alert criterion, and status.
- Counts by category directly under the header; do not include a literal `Resumo executivo` title.
- Grouped sections: critical, attention, normal, and unavailable/non-numeric.
- Add visual icons for scanability, e.g. 🏠 system, 🕒 timestamp, 🎯 criterion, 🔴 critical, 🟡 attention, 🟢 normal, ⚫ unavailable, 🔋 level, 🆔 entity, 🛠️ recommended action.
- Numbered entities with aligned fields for `🔋 Nível`, `📌 Status`, and `🆔 Entidade`.
- Alert messages should end with an `🛠️ Ação recomendada` section.
- Test notifications should be sent exactly like a real notification, without adding a `TESTE` title or prefix.

Alert example:

```text
⚠️ RELATÓRIO DE ALERTA — BATERIA CRÍTICA
────────────────────────────────────────
Sistema: Home Assistant
Data/hora: 11/06/2026 19:09:37 (America/Sao_Paulo)
Critério: sensores de bateria com nível menor ou igual a 5%
Status geral: AÇÃO RECOMENDADA

Resumo executivo
• Sensores críticos notificados: 3
• Total de sensores críticos detectados: 3
• Total de sensores monitorados: 22

Sensores em estado crítico
────────────────────────────────────────
01. Porta da frente Bateria
    Nível:   0%
    Status:  CRÍTICO
    Entidade: sensor.porta_da_frente_bateria

Ação recomendada
• Substituir ou recarregar as baterias listadas acima.
• Verificar no Home Assistant se algum sensor crítico está sem comunicação física.
```

Daily report should use the same header style and group sensors into `Sensores críticos`, `Sensores em atenção`, `Sensores em condição normal`, and `Entidades sem leitura numérica`.
