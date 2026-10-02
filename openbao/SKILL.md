---
name: openbao
description: >-
  Ler secrets do OpenBao homelab (CT 107, http://192.168.1.14:8200) via AppRole.
  Usar quando um agente precisar de senha, token, API key ou credencial da infra,
  vida pessoal ou PCL. Nunca colar secret_id, root token ou o valor do secret no
  chat, wiki ou commit.
---

# OpenBao — como o agente pede um secret

Cofre de máquina na LAN. Cofre humano continua no Vaultwarden. Sem Pangolin.

O agente **não** usa MCP de Vault. Corre o helper e usa o valor na ferramenta (SSH, API, etc.), depois descarta. A wiki `mcp` manda preferir CLI.

## Quem lê o quê

| Agente | Host | Ficheiro (modo 600) | Paths |
|---|---|---|---|
| Jarvis | `192.168.1.6` | `~/.config/openbao/jarvis.env` | `personal/*` |
| Tiberius | `192.168.1.6` | `~/.config/openbao/tiberius.env` | `infra/*` |
| Alfred | PCL | `~/.config/openbao/alfred.env` | `pcl/*` |
| Cursor / Claude Code | PCL | `~/.config/openbao/cursor.env` ou `claude.env` | policy `agent-read` |

Repo: `~/git/openbao` (Gitea privado `ssh://git@192.168.1.34:222/kiwel/openbao.git`; sem GitHub). Helper: `python3 ~/git/openbao/scripts/openbao-get.py` (no gateway, copiar para `~/.local/bin/openbao-get`).

```fish
set -x OPENBAO_ENV ~/.config/openbao/alfred.env
python3 ~/git/openbao/scripts/openbao-get.py pcl/exemplo password
```

Só o valor vai para stdout. Sem `--key`, lista **nomes** dos campos, não os valores.

## Regras

1. Não echoes o valor. Não grava na wiki, no `log.md`, nem em commit.
2. Não uses o `root_token`. Só AppRole do teu perfil.
3. Não leias o `.env` de outro agente no mesmo host (Jarvis ≠ Tiberius).
4. Se HTTP 403: estás no prefixo errado (Alfred não lê `infra/`).
5. Se HTTP 503 / sealed: o CT 107 está selado — unseal humano, não o agente.
6. Credenciais do AppRole (`BAO_ROLE_ID`, `BAO_SECRET_ID`) nunca entram no transcript.

Wiki: `openbao-homelab`, `agentes-hermes`.
