---
name: vikunja
description: >
  Instância pessoal Vikunja (fork em ~/git/vikunjaX, CT 125, Compose, não k3s).
  Use SEMPRE neste repo, ao ouvir drakaris, rebuild/push de kiwel/vikunjax,
  pull/up no LXC, task.kiwel.uk, Split Inspector, ou /root/vikunja/.
  O drakaris daqui é Docker Hub + compose no CT — nunca kubectl.
---

# Vikunja — instância pessoal (Docker/CT)

Clone em `/home/kiwel/git/vikunjaX`. UI/API self-hosted no **CT 125** (`192.168.1.19`), Compose em `/root/vikunja/`, Postgres no CT 123. Público: `https://task.kiwel.uk`. Wiki: `vikunja-tarefas`. Gatilho global: `comando-drakaris`.

Não é o pipeline k3s do Horus/Kartrack. Sem namespace, sem `kubectl`.

## `drakaris` (pré-autorizado)

Mensagem contém `drakaris` **neste projeto**. Sem pedir confirmação por etapa. Parar só se uma etapa falhar de forma bloqueante. **Build e push da imagem estão sempre autorizados** (2026-08-31): não perguntar para `docker build` nem `docker push`.

Antes do build, resolver a tag (skill `drakaris`). Ao vivo hoje é `v1.5`, então o próximo run sem pin é `v1.6`. O repo já tem `VERSION`; não precisa de `--current`.

Ordem:

1. **Build** no PCL, no root do repo (`linux/amd64`, versão do dump = 2.5.0):

```fish
set TAG (python3 ~/skills/drakaris/next_version.py --repo . --message "<mensagem>" --write)
docker build --platform linux/amd64 --build-arg RELEASE_VERSION=2.5.0 \
  -t kiwel/vikunjax:$TAG \
  .
```

Hub exige repositório em minúsculas (`vikunjax`, não `vikunjaX`). `RELEASE_VERSION=2.5.0` é a versão interna do dump, não a tag Docker.

2. **Push Hub** da tag canónica (`$TAG`).

3. **CT 125** — login LXC `root`, stack `/root/vikunja/`. Compose com `image: kiwel/vikunjax:$TAG`. Do PCL o SSH direto a `192.168.1.19` falha host key; usar o Proxmox:

```bash
ssh root@192.168.1.5 'pct exec 125 -- bash -lc "cd /root/vikunja && docker compose pull && docker compose up -d"'
```

Conferir `docker compose ps` e `http://192.168.1.19:3456`.

4. **Commit + push nos dois remotes** (skill `git`; nunca SSH no GitHub).

   - GitHub: `origin` = `https://github.com/k1w3l/vikunjaX.git`
   - Gitea: `gitea` = `ssh://git@192.168.1.34:222/kiwel/vikunjaX.git` — criar remote/repo se faltar
   - Conventional Commits; `PRODUCT.md`, `DESIGN.md` e `.impeccable/` **entram** no repo (orientação 2026-08-28). Não commitar o ficheiro solto `prompt`.
   - Não commitar o ramo temporário de login SPA com token `tk_` a menos que o usuário peça

5. Atualizar **esta skill** + wiki `vikunja-tarefas` (digest e se o CT está na tag nova).

## Fora de `drakaris`

- **Ao vivo 2026-09-24:** CT 125 em `kiwel/vikunjax:v1.5` digest `sha256:71b4ab583ee477c4fd9f1b851a7fe96414ebd9742046140d72bd2e96edebe4c2` (commit `8e85b0e16`). Compose `image: kiwel/vikunjax:v1.5`. LAN `:3456` 200. GitHub `k1w3l/vikunjaX`, Gitea `kiwel/vikunjaX`. `latest` no Hub aponta para o mesmo digest.
- **UI em v1.4:** telemóvel — tab bar Overview | Projects | Upcoming (`MobileTabBar.vue`, blur, ativo cádmio); sem hamburger; logo no header; Projects abre o rail como folha. Tiles: colapsado + toque expande `TaskActionBar` (não abre o inspector da lista). Título do tile no telemóvel é um botão com `color: var(--text)`; a barra tem ícone `pen` para editar o título no tile expandido (Overview e kanban). Sem popup amarelo de update do service worker. **Kanban no telemóvel:** pager de uma coluna (setas + snap, título cádmio); cartão expande in-tile; Add vai para o bucket visível; inspector não abre no toque. Arrasto de cartão no telemóvel desligado (o `.handle` bloqueava scroll/swipe). Pegadilha Sass: a regra do pager tem de ser `.kanban.is-phone-pager .bucket` — o `&` aninhado compilava `.kanban.is-phone-pager .kanban .bucket` (0 matches, colunas ~104px no `v1.2`). Desktop: rail 15rem com PROJECTS/LABELS + `+`; clique no título abre inspector 30rem; kanban continua quadro lado a lado. Modal Add task: só título + barra (sem heading “New task”). Chevron de subtarefa no gutter à esquerda do tile. `DESIGN.md` tem **The One-Column Board Rule**; sidecar alinhado 2026-08-31. Settings: Labels e Teams. `/projects` → overview. Chrome **VikunjaX**.
- **UI em v1.5:** kanban móvel mostra `FancyCheckbox` no cartão (ao lado do título). `TaskActionBar` tem ícone `align-left` (descrição) com textarea + Save, também no modal Add task; o tile expandido mostra a descrição só leitura. Barra guardada 11 ícones, draft 9.
- Frontend dev: `frontend/` + `pnpm dev` (porta 4173). Obrigatório `frontend/.env.local` com `DEV_PROXY=http://192.168.1.19:3456` — senão POST `/api/v1/login` no Vite é 404. `localStorage.API_URL` = `http://192.168.1.19:3456/api/v1` (directo) ou `/api/v1` (via proxy).
- E2E: `mage test:e2e`, nunca `pnpm test:e2e` solto.
- Novas rotas API → `/api/v2` (skills `api-v2-routes` / `crudable` / `migration` no repo).
- Senha do banco, JWT, tokens de API: só no LXC. Nunca na wiki nem nesta skill.

## Related

- Wiki `vikunja-tarefas`, `comando-drakaris`
- Skills `git`, `wiki`, `homelab-k8s-deploy` (este último **não** se aplica ao deploy da app)
