---
name: bkp-pcl
description: >-
  Sistema de backup/sincronização do setup do Kiwel (host PCL, CachyOS) com o
  NAS TrueNAS via NFS. Use esta skill SEMPRE que a tarefa envolver: ajustar,
  estender ou depurar o backup-sync em ~/git/synk/ (ou o symlink
  ~/.config/backup-sync/); adicionar/remover algo do backup (dotfiles,
  segredos, dados); editar jobs.toml ou a web UI (FastAPI em localhost:8765);
  criar um NOVO job de backup ou replicar esse esquema em outra máquina;
  restaurar o setup após reinstalar o sistema; mexer no repositório yadm, na
  criptografia gpg dos segredos, nas units systemd de sincronização, ou na
  montagem automount do /mnt/NAS. Dispare mesmo quando o usuário só disser
  coisas como "quero adicionar X ao backup", "meu sync com o NAS parou",
  "preciso restaurar minhas configs", "cria um backup do diretório Y", "o yadm
  não está commitando", ou "como faço backup disso pro NAS" — em todos esses
  casos é este o sistema em jogo.
---

# bkp-pcl — Backup/sync do setup com o NAS

Sistema desenhado e implementado para reconstituir rapidamente o setup do Kiwel
após reinstalar o sistema, e proteger os dados pessoais. Separa o problema em
camadas com requisitos distintos em vez de "copiar o home inteiro pro NAS".

**Estado (2026-09-22):** synk **desativado** no `systemd --user` (pedido do
usuário). Timers, `data-watch` e UI (`:8765`) estão `disabled`/`inactive`. O
repo, o symlink `~/.config/backup-sync` e os dados no NAS continuam. Não
desligar `mnt-NAS.automount` nem `ldm-activate.service` ao “desativar o synk”.
Reativar: `bash ~/git/synk/scripts/setup.sh`.

**Antes de mexer, leia `references/design.md`** — ele tem as decisões e o
*porquê* de cada escolha. Não reverta uma decisão sem entender o motivo.

## Ambiente fixo (host PCL)
- Distro: **CachyOS** (Arch). Pacotes via `pacman` (sudo pede senha).
- NAS: **TrueNAS, ZFS com snapshots**, montado por **NFSv4** em `/mnt/NAS`
  (`192.168.1.11:/mnt/tank/Kiwel`), via **automount** (`mnt-NAS.automount`).
- Raiz dos backups no NAS: **`/mnt/NAS/PCL/Backup/`**.
- Init system: `systemd` (units de usuário em `~/.config/systemd/user/`).
- Identidade gpg dos segredos: recipient **`kiwel.01@gmail.com`** (chave privada
  guardada no **Bitwarden** — é o único segredo fora do NAS).

## As 4 camadas

| Camada | O quê | Ferramenta | Destino | Gatilho |
|---|---|---|---|---|
| Config | dotfiles (allowlist) | **yadm** (git) | `dotfiles.git` (bare) | timer diário |
| Segredos | `.ssh`, `.kube` | yadm + **gpg assimétrico** | dentro do repo, cifrado | junto do config |
| Dados | home **não-oculto** | rsync `--backup` | `data/home` | inotify + debounce 5min |
| Estado | `.claude` (histórico/projetos), webapps (`ice`), mídia do LCD (trcc) | rsync `--backup` | `data/state` | timer diário |

Versões substituídas/apagadas → `data-backup/<data>` (retenção 1 dia). Histórico
profundo = snapshots ZFS do NAS.

## Estrutura do projeto — `~/git/synk/`

O projeto vive em **`~/git/synk/`** (git). `~/.config/backup-sync/` é um
**symlink** para `~/git/synk/scripts/` criado pelo `setup.sh`.

```
~/git/synk/
  jobs.toml            # ⭐ FONTE ÚNICA DE VERDADE — toda config fica aqui
  toml_helper.py       # bridge bash→TOML (export/get/list)
  .venv/               # venv Python da UI (FastAPI)

  scripts/
    config.sh          # eval "$(toml_helper.py export)" + nas_ready()
    dotfiles-sync.sh   # lê paths via toml_helper
    data-sync.sh       # lê excludes via toml_helper
    data-state-sync.sh # lê STATE_PATHS via toml_helper
    data-watch.sh      # lê debounce via toml_helper
    data-prune.sh      # lê retention_days via toml_helper
    setup.sh           # bootstrap: symlink, venv, units, enable serviços

  ui/
    main.py            # FastAPI: dashboard, editor, API REST, SSE logs
    templates/         # Jinja2: base.html, index.html, job.html
    static/app.css     # dark theme

  systemd/
    user/              # units do usuário (copiadas p/ ~/.config/systemd/user/)
      backup-ui.service
      data-watch.service
      dotfiles-sync.{service,timer}
      data-state-sync.{service,timer}
      data-prune.{service,timer}
    system/
      mnt-NAS.mount
      mnt-NAS.automount
```

Mais: `~/.config/yadm/encrypt` (lista do que é cifrado pelo yadm).

**Repos:** Gitea `192.168.1.34:3000/kiwel/synk` (SSH porta 222) · GitHub `github.com/k1w3l/synk`

## jobs.toml — a config central

Toda configuração que antes ficava espalhada em `config.sh`, `yadm-allowlist.txt`,
`data-excludes.txt` e no array `STATE_PATHS` do script, agora está em `jobs.toml`:

```toml
[global]
backup_root = "/mnt/NAS/PCL/Backup"
nas_mount   = "/mnt/NAS"
gpg_recipient = "kiwel.01@gmail.com"
retention_days = 1

[jobs.dotfiles]     # type = "yadm"      → paths[] = allowlist do yadm
[jobs.data_home]    # type = "rsync_home" → excludes[] = padrões rsync
[jobs.state]        # type = "rsync_paths" → paths[] = STATE_PATHS
```

Edite via **UI web** (`http://localhost:8765`) ou diretamente no arquivo.
Após editar o arquivo, **não é necessário reiniciar** nada — `toml_helper.py`
relê na próxima execução.

## Web UI — `http://localhost:8765`

Servida pelo `backup-ui.service` (systemd user).

- **Dashboard**: status NAS, estado de cada job (active/idle), último run, próximo timer
- **"Executar agora"**: roda o script e faz stream do output em tempo real (SSE)
- **"Logs"**: abre SSE do `journalctl --user -u <serviço>` ao vivo
- **"Editar"**: gerencia paths/excludes/parâmetros e salva direto no `jobs.toml`

Stack: FastAPI + Jinja2 + CSS vanilla. Sem build step. Starlette 1.x.

## Tarefas comuns

### Adicionar um app/config ao backup (camada config)

**Via UI**: `http://localhost:8765` → Dotfiles → Editar → "+ Adicionar" → Salvar.

**Manual**: edite `jobs.toml`, seção `[jobs.dotfiles]`, array `paths`. Para itens
grandes/com estado, liste só os arquivos de config, não o diretório inteiro
(ex.: noctalia entra como `settings.json`/`colorschemes`, NÃO `plugins/`). Depois:
```bash
~/.config/backup-sync/dotfiles-sync.sh   # captura, commita e dá push
```

### Adicionar um segredo (cifrado)
Acrescente o caminho em `~/.config/yadm/encrypt`, então:
```bash
yadm encrypt && yadm add ~/.local/share/yadm/archive && yadm commit -m "novo segredo" && yadm push
```
A cifragem usa só a **chave pública** (sem passphrase) — por isso o job diário
re-cifra sozinho. A passphrase/chave privada só é necessária no `yadm decrypt`
(restauração). GoodSync: não ponhas `.config/goodsync-etc` em `jobs.dotfiles.paths`
(iria em plaintext); o snapshot é feito no `dotfiles-sync.sh` e só entra via encrypt.
O mesmo vale para `.config/cursor-telegram` (token do bot).

### Adicionar dados ou estado
- **Dados não-ocultos** do home já entram automaticamente no `data-sync`.
- **Estado/ocultos/pesados**: edite `jobs.toml` → `[jobs.state]` → `paths[]`
  (ou use a UI: Estado Pesado → Editar).

### Excluir algo do backup de dados (re-baixável / pesado)
Edite `jobs.toml` → `[jobs.data_home]` → `excludes[]` (padrões rsync, relativos
a `$HOME`, `/` ancora na raiz). Já excluídos: **Zephyr SDK** e **`/zmk/`**.
Critério: re-baixável/re-gerável NÃO entra. Ao excluir algo já copiado, limpe na
mão no NAS (`rm -rf /mnt/NAS/PCL/Backup/data/home/<isso>`) — `--delete` não
remove excludes do destino.
⚠️ Antes de excluir um workspace/projeto inteiro, confira se há trabalho local
sem remote git (ex.: `zmk-wing`/`zmk-def` não têm remote).

### Criar um NOVO job de backup
1. Adicione uma seção `[jobs.<id>]` no `jobs.toml` com os campos necessários
   (`name`, `type`, `description`, `enabled`, `systemd_service`, `paths` ou `excludes`)
2. Crie o script em `scripts/<id>-sync.sh` seguindo o padrão existente:
   source `config.sh`, cheque `nas_ready`, leia paths/excludes via `toml_helper.py`
3. Adicione a entrada `script_map` em `ui/main.py` para o botão "Executar agora"
4. Crie a dupla `.service`+`.timer` em `systemd/user/`
5. Rode `setup.sh` para instalar

### Restaurar em máquina nova
```bash
# 1. Clonar o repo (Gitea LAN; GitHub é espelho)
git clone ssh://git@192.168.1.34:222/kiwel/synk.git ~/git/synk
# 2. Instalar automount NFS (as DUAS units) + LDM do NAS_BKP + deps
sudo cp ~/git/synk/systemd/system/mnt-NAS.mount ~/git/synk/systemd/system/mnt-NAS.automount ~/git/synk/systemd/system/ldm-activate.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mnt-NAS.automount
sudo systemctl enable --now ldm-activate.service
sudo mkdir -p /mnt/NAS_BKP && sudo mount /mnt/NAS_BKP
# 3. gpg --import da chave privada (Bitwarden, recipient kiwel.01@gmail.com)
# 4. Configs + segredos + GoodSync; opcional --data / --state / --all
bash ~/git/synk/scripts/restore.sh --all
# 5. Ativar timers/UI
bash ~/git/synk/scripts/setup.sh
```
`restore.sh` faz: `yadm clone` do bare no NAS → `yadm decrypt` (`.ssh`, `.kube`, `.config/goodsync-etc`, `.config/cursor-telegram`) → devolve GoodSync a `/etc/goodsync` + unit systemd → rsync reverso de `data/home` e `data/state` se pedido.

### Desativar (parar timers/UI/watch, sem desmontar o NAS)

Não toca em `mnt-NAS.automount`, `mnt-NAS.mount`, `ldm-activate.service` nem
GoodSync. Os jobs em `jobs.toml` podem já estar `enabled = false`; o systemd
ainda corre se as units estiverem enabled.

```fish
systemctl --user disable --now backup-ui.service data-watch.service \
  dotfiles-sync.timer data-state-sync.timer data-prune.timer nas-backup-sync.timer
systemctl --user stop dotfiles-sync.service data-state-sync.service \
  data-prune.service nas-backup-sync.service
```

Reativar: `bash ~/git/synk/scripts/setup.sh`.

### Operar / depurar
```bash
systemctl --user list-timers 'data-*' 'dotfiles-*'    # quando rodam
journalctl --user -u data-watch.service -f             # log do watch reativo
~/.config/backup-sync/dotfiles-sync.sh                 # forçar sync de config
python3 ~/git/synk/toml_helper.py export               # verificar vars lidas
python3 ~/git/synk/toml_helper.py list jobs.state.paths  # inspecionar lista
# UI:
systemctl --user status backup-ui.service
journalctl --user -u backup-ui.service -f
```

## Armadilhas conhecidas (não repita)

- **🚨 NUNCA ponha `After/Wants=network-online.target` no `.automount`.** Isso
  derrubou a rede inteira num boot (jun/2026). Ciclo `local-fs → automount →
  network-online → NetworkManager → … → local-fs` faz o systemd apagar o job do
  NetworkManager. Dependência de rede fica **só no `mnt-NAS.mount`**. Valide com
  `systemd-analyze verify ~/git/synk/systemd/system/mnt-NAS.*`.
- **As DUAS units precisam existir** (`mnt-NAS.mount` define o NFS, `.automount`
  aciona). Ambas em `systemd/system/`. Numa máquina nova, só o `.automount` não
  monta nada.
- **NAS_BKP no boot precisa de `ldm-activate.service` instalada e enabled.** O
  fstab tem `nofail` + `x-systemd.requires=ldm-activate.service`. Sem a unit no
  `/etc/systemd/system/`, o systemd descarta o job (`Unnecessary job was removed
  for /dev/disk/by-uuid/60D60944D6091BC2`) e o volume LDM nem é criado. Não uses
  a `ldmtool.service` do pacote (`Type=simple` — o `ldmtool create all` sai e o
  serviço fica morto). Depois do `ldmtool create all` a unit faz `udevadm settle`
  para o UUID existir antes do mount.
- **`start-limit-hit` no mount/automount**: `sudo systemctl reset-failed mnt-NAS.mount mnt-NAS.automount`.
- **automount recusa iniciar se `/mnt/NAS` já está montado** — `setup.sh` trata isso.
- **Segredos só `.ssh`, `.kube`, `.config/goodsync-etc` e `.config/cursor-telegram`**
  (snapshot de `/etc/goodsync` sem logs, feito no `dotfiles-sync.sh` antes do
  `yadm encrypt`; token do bot Telegram nunca na allowlist). Não ponhas estes
  paths em `jobs.dotfiles.paths`.
  `.gnupg` fica FORA (circular). `.atuin` e `.credentials.json` do Claude também
  ficam fora (re-loga na máquina nova). `.goodsync` no `$HOME` é perfil vazio do
  CLI — o perfil real do servidor é `/etc/goodsync`. `~/.config/gh/hosts.yml` tem
  oauth token — também fica fora.
- **`.claude` é quase tudo estado**: config vai no yadm; churn (`history.jsonl`,
  `projects/`, etc.) vai na camada estado (rsync), não no git.
- **`ice/` (~10G)** = perfis de browser dos webapps; camada estado (timer diário),
  nunca inotify reativo.
- **gh já é o credential helper** do git (não há mais `git_token.txt`).
- **Symmetric vs assimétrico**: gpg **assimétrico** de propósito (cifra sem senha
  no job automático). Não troque sem resolver como o timer obteria a passphrase.
- **Starlette 1.x mudou `TemplateResponse`**: não passe `request` no dict de
  contexto — use `request=` como kwarg separado:
  ```python
  # ✓ correto (Starlette 1.x)
  templates.TemplateResponse(request=request, name="index.html", context={...})
  # ✗ quebra com TypeError unhashable no cache do Jinja2
  templates.TemplateResponse("index.html", {"request": request, ...})
  ```
- **Python no CachyOS é "externally managed"** — não use `pip install` global.
  A UI usa o venv em `~/git/synk/.venv/`. Para adicionar dependências:
  `~/git/synk/.venv/bin/pip install <pkg>`.
- **Token do Gitea com escopo `write:repository`** não consegue criar repos via
  API (requer `write:user`). Use um token com ambos os escopos para operações
  de criação. Gere em `http://192.168.1.34:3000/user/settings/applications`.

## Detalhes e racional completos
Ver `references/design.md`.
