---
name: git
description: >-
  Referência de configuração Git do Kiwel: endereços, usuários, tokens e
  procedimentos para Gitea (homelab) e GitHub. Use esta skill SEMPRE que a
  tarefa envolver criar repositórios, configurar remotes, fazer push/clone,
  autenticar ou resolver erros de acesso no Gitea ou GitHub — mesmo que o
  usuário só mencione "gitea", "github", "repo novo", "push pro servidor",
  "criar repositório", "remote" ou qualquer variação. Inclua esta skill
  proativamente sempre que Gitea ou GitHub aparecerem na conversa.
---

# Git — Gitea & GitHub do Kiwel

## Gitea (homelab)

| Campo | Valor |
|---|---|
| HTTP | `http://192.168.1.34:3000` |
| SSH | `ssh://git@192.168.1.34:222` (porta **222**, não 22) |
| Usuário | `kiwel` |
| Settings/Tokens | `http://192.168.1.34:3000/user/settings/applications` |

### Tokens

| Escopo | Serve para |
|---|---|
| `write:repository` | push, clone, operações no repo |
| `write:user` + `write:repository` | **criar repos via API** (obrigatório) |

Tokens com escopo insuficiente retornam `"token does not have at least one of required scope(s)"`.
Gere um token com ambos os escopos em `http://192.168.1.34:3000/user/settings/applications`.

**Token salvo** (escopos `write:user` + `write:repository` — cria repos e faz push):

```
90f4ec6c56d0d065b52b8fea795c1b61f8189782
```

### Criar repo via API

```bash
curl -s -X POST "http://192.168.1.34:3000/api/v1/user/repos" \
  -H "Authorization: token <TOKEN_WRITE_USER>" \
  -H "Content-Type: application/json" \
  -d '{"name":"<nome>","description":"...","private":false,"auto_init":false}'
```

`auto_init: false` é essencial quando o repo vai receber um push imediato — evita conflito de histórico.

### Remote SSH (formato correto)

```bash
git remote add gitea ssh://git@192.168.1.34:222/kiwel/<repo>.git
git push gitea master
```

### Repos existentes (exemplos de formato)

```
ssh://git@192.168.1.34:222/kiwel/synk.git
ssh://git@192.168.1.34:222/kiwel/Kartrack.git
http://192.168.1.34:3000/kiwel/bills-organizer.git
```

---

## GitHub

| Campo | Valor |
|---|---|
| Usuário | `k1w3l` (diferente do Gitea: sem vogal) |
| Protocolo | **HTTPS** (SSH não funciona — `ssh-askpass` não instalado) |
| Auth | `gh` CLI como credential helper |

### Configuração do credential helper (`~/.config/git/config`)

```ini
[credential "https://github.com"]
    helper =
    helper = !/usr/bin/gh auth git-credential
```

### Criar repo

```bash
gh repo create <nome> --private --description "..."
# retorna a URL: https://github.com/k1w3l/<nome>
```

### Remote HTTPS (formato correto)

```bash
git remote add github https://github.com/k1w3l/<repo>.git
git push github master
```

**Nunca use SSH para GitHub** (`git@github.com:...`) — falha com
`ssh_askpass: exec(/usr/lib/ssh/ssh-askpass): No such file or directory`.

---

## Push para os dois (fluxo padrão)

```bash
# 1. Criar repos
curl ... gitea API ...
gh repo create <nome> --private

# 2. Adicionar remotes
git remote add gitea ssh://git@192.168.1.34:222/kiwel/<repo>.git
git remote add github https://github.com/k1w3l/<repo>.git

# 3. Push
git push gitea master
git push github master
```

---

## Armadilhas conhecidas

- **SSH no GitHub falha** — use HTTPS + `gh` como credential helper.
- **Porta SSH do Gitea é 222**, não 22 — `ssh://git@192.168.1.34:222/...`.
- **Token `write:repository`** não cria repos — precisa de `write:user` também.
- **`auto_init: false`** ao criar repo via API — `true` gera conflito no primeiro push.
- **Usuário GitHub é `k1w3l`** (com "1" no lugar do "i") — diferente de `kiwel` no Gitea.
