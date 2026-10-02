---
name: drakaris
description: >
  Pipeline global de release disparado pela palavra drakaris. Sempre incrementa
  a tag da imagem (v1.0 → v1.1 → v1.2) salvo pin na mensagem (drakaris v1.5 /
  drakaris versão 2.0). Padrão Docker Hub + k3s; variante Compose no CT.
  Use ao ouvir drakaris, bump de tag Docker, VERSION, ou next_version.py.
---

# `drakaris` — release com bump de tag

A palavra `drakaris` dispara o pipeline completo do **projeto atual**, pré-autorizado. Wiki: `comando-drakaris`. Skill do projeto (ex. `horus`, `vikunja`) + esta skill.

**Build e push da imagem estão sempre autorizados** (orientação 2026-08-31): não perguntar para `docker build` nem para `docker push` no Hub. Tag de versão + `latest` quando for o padrão do projeto.

## Versão da imagem (obrigatório)

Cada `drakaris` gera a **próxima** tag (`v1.0` → `v1.1` → `v1.2`). `latest` continua tag extra; o deploy aponta para a versão numerada. Listas do tipo `exemplo: v1.0, v1.1` **não** pinam.

Pin só se a mensagem pedir: `drakaris v1.5` ou `drakaris versão 2.0`. Sem histórico, o primeiro release é `v1.0`.

Antes do build:

```fish
python3 ~/skills/drakaris/next_version.py --repo . --message "<mensagem do usuário>" --write
```

Se o repo não tem `VERSION` nem `image: kiwel/…:vX.Y`, passe a tag ao vivo da skill/wiki:

```fish
python3 ~/skills/drakaris/next_version.py --repo . --message "<mensagem>" --current v1.0 --write
```

O script lê `VERSION` (ou a maior tag `vX.Y` nos YAML `image:` de imagens `kiwel/`, ignorando `.github/`) e grava a nova tag em `VERSION`. Use essa tag no `docker build`, Hub, manifests e compose.

Testes: `python3 -m unittest discover -s ~/skills/drakaris/tests -v`

## Pipeline k3s (padrão)

1. Resolver a tag (acima).
2. Build da imagem Docker (nome já usado no repo).
3. Push Hub (versão + `latest` se for o padrão).
4. Atualizar manifestos k3s com a tag nova.
5. `kubectl apply` + `kubectl rollout status`.
6. Commit e push nos dois remotes (skill `git`; nunca SSH no GitHub).
7. Atualizar a skill do projeto.

## Pipeline Docker/CT (Compose no LXC, sem k3s)

Vikunja / CT 125 — skill `vikunja`. Sem `kubectl`.

1. Resolver a tag.
2. Build + push Hub.
3. No CT: tag no compose, `docker compose pull && docker compose up -d`.
4. Commit e push nos dois remotes.
5. Atualizar skill + wiki da stack.

## Não dispara

- "deploy" sozinho ou o antigo `deploy:`.
- Sem Docker e sem Compose no CT: dizer o que falta; não improvisar infra.
