---
name: agenda
description: "Use for Stalwart calendar operations and Telegram-approved event creation."
version: 1.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agenda, stalwart, calendar, telegram-approval]
---

# Agenda (Stalwart)

Fonte da verdade: Stalwart. Nunca grave a App Password. Nunca fale com Google para criar evento.

Comando operacional: `python3 ~/.hermes/scripts/calendar_ssh.py <args>`

- Hoje: `today`
- Semana: `week`
- Livre?: `freebusy --start 2026-08-22T14:00:00 --end 2026-08-22T15:00:00`
- Criar por solicitação explícita do operador: `create --title '…' --start LDT --end LDT`
- Alterar/cancelar: `update ID …` / `delete ID`
- Timezone: America/Sao_Paulo. LDT sem Z.

## Gate de aprovação

Toda criação automática derivada de e-mail ou outra rotina deve ser aprovada pelo operador no Telegram antes de chamar `create`. Use a fila em `~/.hermes/scripts/jarvis_calendar_approval.py`; ela envia os botões `✅ Criar evento` e `❌ Não criar`, e somente o callback autorizado `ca:y:<id>` chama `calendar_ssh.py create`. Ausência de aprovação, rejeição, falha de Telegram ou conflito não cria nada.

Não use Google Calendar como origem, não invente eventos e não mova mensagens do Stalwart para confirmar uma proposta.

Se stdout tiver `"error":"conflict"`, ofereça outro horário com os `busy` retornados.
Se SSH falhar, diga que o Stalwart/mailagent está inacessível; não invente a agenda.
