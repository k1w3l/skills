---
name: horus
description: |
  Contexto, arquitetura e convenções do projeto Horus — dashboard de observabilidade
  e controle do home lab (FastAPI + TimescaleDB no backend, React de arquivo único
  no frontend), em /home/kiwel/git/horus. Cobre padrões de CSS/layout (cards, grids,
  ritmo de espaçamento), padrões de componentes/estado do frontend, arquitetura de
  plugins de integração do backend, convenções de API/auth/DB, e estilo de código
  estabelecido (comentários em PT-BR só pro "porquê", sem abstração não pedida).
  USE SEMPRE esta skill ao iniciar qualquer tarefa de desenvolvimento no projeto
  Horus — bugfix, nova feature, ajuste de UI, nova aba/card, nova integração de
  backend, nova rota de API — mesmo que o usuário não diga "Horus" explicitamente,
  contanto que os arquivos/diretório de trabalho estejam sob git/horus. Sem isso,
  é fácil reinventar um padrão que já existe (outro componente de card, outra grade
  CSS, outro jeito de fazer auth) e divergir do resto do projeto.
---

# Horus — contexto do projeto

Dashboard de observabilidade e controle do home lab do Kiwel. Constrói "uma
integração por vez" (fatia 1 = Proxmox; TrueNAS/Docker/k8s vêm depois) atrás de
um modelo canônico que faz qualquer integração nova funcionar com o mesmo
dashboard, alarmes e API sem tocar no core.

```
            ┌─────────── core (fino) ───────────┐
 poller ──▶ │ scheduler · storage · alarmes ·   │ ──▶ Gotify
   │        │ auth (tokens+escopos) · API · SSE │
   ▼        └───────────────────────────────────┘
 integrações (plugins)            ▲ React + uPlot (dashboard vivo)
 ┌──────────┬──────────┬────────┐  │
 │ proxmox  │ truenas  │ docker │  discover/collect/execute
 └──────────┴──────────┴────────┘  + k8s (próxima fatia)
```

Integrações prontas:
- **Proxmox**: VMs/LXCs, inventário, logs, backups, sensores, SSH, UPS
  (o UPS/NUT vira **entidade própria** `type=ups` desde v3.9 — ver seção UPS)
- **TrueNAS**: pools ZFS, discos, interfaces, datasets, snapshots
- **Docker**: host daemon (Remote API TCP:2375), containers com controles (start/pause/stop/restart via `execute()`); log ao vivo no `DockerContainerModal` via `GET /entities/{id}/ctlog` → `get_container_log()` (demux do stream multiplexado em `_demux_log()`, testado, + strip de ANSI)
- **Kubernetes/k3s**: integração completa em `backend/horus/integrations/k8s.py` — nós, deployments, pods com métricas, controles (scale, rollout restart, set_resources), ícone real kubernetes via ALIASES em `icons.js`
- **Uptime-Kuma**: `backend/horus/integrations/uptimekuma.py` — lê o endpoint Prometheus `/metrics` (basic-auth, API key vira senha); entity type `monitor` (ping/http/tcp…), status → `MONITOR_STATE` no front. Aba `UptimeKumaOverviewContent` com `MonitorCard`/`MonitorModal`. Monitores podem ser vinculados a atalhos da Home E a entidades de outras integrações (ver seção "Cards de entidade").

- **Repo**: `/home/kiwel/git/horus` · remotes `gitea` (homelab, `ssh://...222`)
  e `github` (`k1w3l/horus`) — push **nos dois** quando o usuário pedir commit
  (veja a skill `git` para credenciais). Branch única: `main`, sem PRs — o
  usuário trabalha direto nela (ver `prompt`, linha 40: "pode fazer tudo na main").
- **`prompt`** (arquivo na raiz, sem extensão): log cronológico de todas as
  instruções que o usuário já deu, aba por aba. Quando ele disser "continue o
  último prompt" ou pedir algo que pareça já coberto, **leia esse arquivo
  primeiro** — é o backlog/spec viva do projeto, mais confiável que adivinhar.
- **Commits**: mensagens diretas, sem corpo longo. Padrão observado:
  `"Aba X pronta"` ao fechar uma aba inteira, `"feat: ..."` para incrementos
  menores. Sem Conventional Commits estrito.

## Antes de implementar

1. **Leia o `prompt`** (raiz do repo) se a tarefa parecer contínua de algo anterior.
2. Backend: `cd backend && .venv/bin/python -m pytest tests/ -q` — suíte rápida
   (pure functions, parsers; sem mocks de rede/DB). Roda em <1s, sem desculpa
   pra pular.
3. Frontend: `cd frontend && npm run build` — não há lint/typecheck separado
   (sem ESLint/Prettier configurado); o build do Vite É o smoke test. Se ele
   passa mas você tocou em CSS/layout, **isso não prova que ficou visualmente
   certo** — veja a seção de verificação visual abaixo.
4. Não tem `.venv` ativo? `backend/.venv/bin/python` já existe no repo — não
   precisa criar de novo.
5. Mudou CSS/layout sem conseguir abrir a app real (sem Proxmox/DB acessível
   neste ambiente)? Veja **"Verificação visual sem backend"** em
   `references/css-layout.md` — é a técnica usada nesta sessão (Playwright
   headless + um HTML estático reaproveitando `styles.css` direto do repo) pra
   confirmar visualmente um fix de CSS antes de declarar pronto, sem precisar
   de dados reais.
6. Mexeu em **coleta de integração** (o que vai pro banco de métricas)? A suíte
   não cobre isso — ela é só de função pura. O `pytest` passar não prova que o
   número que chega no dashboard mudou. Rode o código da integração dentro do
   pod com as credenciais reais: veja "Verificar integração com credenciais
   reais" na seção da RAM de guest do Proxmox. Vale principalmente onde há
   fallback silencioso (`_get_opt`), que degrada sem log de erro.

## Onde fica o quê

| Camada | Arquivo | Observação |
|---|---|---|
| Toda a UI | `frontend/src/App.jsx` | **~5000 linhas, um arquivo só.** Sem React Router — navegação via `useState` (`sel`, `integ`, `hostTab`; `integ === "home"` é a view especial da Home). Não proponha quebrar em múltiplos arquivos a menos que pedido; é assim de propósito (projeto pequeno, 1 dev). |
| Estilo | `frontend/src/styles.css` | Vars CSS em `:root`, sem framework (Tailwind/styled-components). Ver `references/css-layout.md`. |
| Cliente API | `frontend/src/lib/api.js` | Um `req()` central, token no `localStorage`, todo erro tem `.status`. |
| Ícones | `frontend/src/lib/icons.js` | Matching de ícone por nome (dashboardicons.com), com cache. |
| Gráficos | `frontend/src/components/Chart.jsx` | Wrapper fino de uPlot, não React-native. |
| App FastAPI | `backend/horus/main.py` | `lifespan`: init DB → bootstrap → `hydrate_config()` → `poller.setup()/start()`. |
| Modelos | `backend/horus/models.py` | SQLAlchemy 2.0 async, `Mapped[]`/`mapped_column()`. Migrations leves (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`) ficam em `db.py` (`_MIGRATIONS`), pois `create_all` não altera tabela existente. |
| Rotas | `backend/horus/api/routes.py` | Tudo sob prefixo `/api`, auth via `Depends(require(scope))`. |
| Plugins | `backend/horus/integrations/*.py` | Um arquivo por integração; `proxmox.py` é a referência. |
| Núcleo | `backend/horus/core/*.py` | `canonical.py` (vocabulário), `alarms.py`, `auth.py`, `poller.py`, `registry.py`, `icons.py`, `notify.py`, `events.py`, `secrets.py` (cofre Fernet), `config_schema.py` (schema das conexões), `appconfig.py` (config no banco). |

Para o catálogo completo de componentes/classes CSS/rotas, veja os arquivos
em `references/` — carregue o que for relevante pra tarefa, não precisa ler
os três de uma vez:

- **`references/frontend.md`** — catálogo de componentes compartilhados
  (`StatTile`, `TitledCard`, `NicCard`/`NicModal`, `MachineCard`,
  `DockerContainerCard`, `DockerOverviewContent`, `DiskTile`, `DeviceTile`,
  `GuestInfoCard`, `LogTile`/`LogModal`, `BackupTile`/`BackupModal`, `Modal`,
  `ToastContainer`, `ConfirmModal`, `LinkModal`, `IfaceSpeedModal`,
  `K8sNodeCard`, `K8sDeployCard`, `K8sPodCard`, `K8sOverviewContent`,
  `K8sNodeModal`, `K8sDeployModal`, `K8sScaleModal`, `K8sResourcesModal`,
  `K8sOpStrip`, `HomeView`, `ShortcutModal`, `ShortcutIcon`, `IconPicker`),
  helpers de UI (`statusPill`, `EntityTabs`), `runAction` vs `runContainerAction`,
  sistema de toast/confirm, arquitetura de estado do `App`, métodos do
  `api.js`, formatters (`bytes`, `pctFmt`, `durationFmt`, `storagePctLevel`,
  `logPriLabel`...), padrão de polling, página de detalhe VM/LXC, log paginado.
- **`references/backend.md`** — contrato `Integration` (ABC), dataclasses
  `DiscoveredEntity`/`Sample`, registro/poller, schema de tabelas, rotas por
  grupo, auth/escopos, sistema de alarmes (state machine), env vars.
- **`references/css-layout.md`** — tokens de design, catálogo de classes
  por propósito (shells, cards, grids, tiles, badges, modais), receitas de
  layout (título fora do card, cards da mesma altura, grade alinhada com
  gráficos vizinhos, gotcha de grid aninhado), padrão de tile com
  `flex-direction:column` + `m-foot { margin-top:auto }` para rodapé sempre
  alinhado no fundo, classes Docker (`.ct-ports`/`.ct-port`), `.hbadge.status-pill`,
  `.icon-btn.danger` + técnica de verificação visual sem backend.

## Sistema de alarmes (estado atual — página completa desde v3.8)

- **Motor unificado**: `backend/horus/core/alarms.py` — state machine `ok → pending → firing → resolved`, dirigido pela tabela `AlarmRule`. Quatro famílias de `metric`:
  - `resource_pct` → limite dinâmico CPU/RAM/disco (usa `Entity.threshold_cpu/mem/disk` ou o global `Setting["threshold_{res}"]`); foca o recurso mais acima do próprio limite.
  - `connectivity` → host inalcançável (binário; `evaluate_connectivity`).
  - `health` → achados do Diag (v3.15): **sem estado pending** — 1 `AlarmEvent` por finding, firing direto, resolved quando o achado some no check seguinte (ver seção Diag).
  - qualquer outra métrica → regra **genérica** (operador/threshold/`for_seconds`).
- **Escopo da regra** (`_matches`): se `AlarmRule.entity_id` estiver setado, casa **só** aquela entidade (ignora integração/tipo); senão casa por `integration` + `entity_type` (None em qualquer um = "qualquer"). Coluna `entity_id` adicionada via migration em `db.py`.
- **Mute global**: `Setting["alarms_muted"]="true"/"false"` — pula todo o ciclo. **Mute por entidade**: `Entity.alarms_muted`. **Disable por recurso**: `Entity.alarm_disabled_cpu/mem/disk`. **Thresholds por entidade**: `Entity.threshold_cpu/mem/disk` (None = herda global).
- **UI — página completa** (`AlarmsView`, `integ === "alarms"`, item da sidebar **navega**, NÃO é mais modal). Sub-abas (`.seg.alarm-tabs`):
  - **Ativos** (`AlarmsActiveTab`): `GET /alarms/active`, com confirmar (ack) / silenciar entidade / excluir.
  - **Regras** (`AlarmsRulesTab` + `RuleModal`): só regras **genéricas** (filtra `resource_pct`/`connectivity`). CRUD completo; métrica por lista curada (`RULE_METRICS`, inclui os `ups.*`), operador, limite, `for_seconds`, severidade **info/warning/critical** (`SEVERITIES`), escopo por tipo **ou** por entidade específica (`EntitySelect`). `.rule-card`/`.rule-list`.
  - **Mensagem custom** (v3.9): `AlarmRule.message` (nullable) — template com placeholders `{entity}`/`{resource}`/`{value}`/`{threshold}`, renderizado por `_render_msg` no disparo (senão a mensagem padrão). Campo "Mensagem do alerta" no `RuleModal`, default `DEFAULT_ALARM_MSG` editável.
  - **Histórico** (`AlarmsHistoryTab`): filtros de tempo/status + excluir (era o antigo `AlarmsModal`, removido).
  - **Limites** (`AlarmsLimitsTab`): globais CPU/RAM/disco (`GET/PUT /settings`, botão abre `ThresholdsModal`) + toggle de conectividade + lista read-only das entidades com ajuste próprio.
  - Sino de **mute global** (`BellOff/Bell`) segue na sidebar, ao lado de "Alarmes".
- **API**: `GET/POST /alarms/rules` · `PUT /alarms/rules/{id}` · `DELETE /alarms/rules/{id}` (admin; PUT/DELETE **com guarda** — `SPECIAL_ALARM_METRICS = {"resource_pct", "connectivity", "health"}` recusa mudar condição/escopo ou excluir essas regras) · `GET /alarms/active` · `GET /alarms/history` · `POST /alarms/{event_id}/ack` · `DELETE /alarms/{event_id}` · `PATCH /entities/{id}/mute` · `PATCH /entities/{id}/threshold` · `GET/PUT /settings` (limites globais).
- **Design doc**: `docs/superpowers/specs/2026-07-17-alarms-page-design.md`.

## UPS (NUT) — entidade própria (desde v3.9)

- **Coleta**: `node_ssh.parse_ups` (saída do `upsc`, config `settings.nut_ups`) já existia,
  anexada ao host em `attributes.ups`. Agora o **Proxmox também emite uma entidade**
  `type=ups` (`proxmox/{node}/ups`) no `discover()` (status via `_ups_status`: `OB`→degraded
  "na bateria" · `LB`→error "bateria baixa" · `OL`→running) e **samples** no `collect()`
  reaproveitando `self._ssh_extras["ups"]`: `ups.charge_pct`, `ups.load_pct`,
  `ups.runtime_seconds`, `ups.input/output/battery_voltage`, `ups.realpower_w`,
  **`ups.temp`** (celsius; NUT `ups.temperature`, fallback `battery.temperature` /
  `ambient.temperature` — o 4539 `blazer_ser` reporta `ups.temperature`),
  **`ups.input_frequency`** (Hz; desde v3.28) e **`ups.on_battery`** (1/0).
  `EntityType.ups` no `canonical.py`. O `blazer_ser` **não** reporta autonomia/
  `ups.realpower` — `—` na UI é esperado.
- **Alarme on-battery** = regra genérica normal `ups.on_battery > 0` (sem código especial).
  `ups.charge_pct < 30` (bateria baixa) e `ups.runtime_seconds < 300` (autonomia) idem.
- **Frontend**: `UPS_STATE` (status→cls/label); **item na sidebar** (abre o detalhe via
  `setInteg+setSel`) — **não** tem card na overview (o `UpsEntityCard` e a prop `upsEntity`
  do `OverviewTabContent` foram removidos na v3.22, ver seção própria);
  **detalhe** (`UpsDetail`, branch `sel.type==="ups"`):
  tiles + **reusa o `UpsCard` rico** (o mesmo do `HardwareTabContent`, montando o dict do
  `latestMap`) + gráficos `UpsMetricChart` (carga%/load%/temp). `NEED["proxmox/ups"]=[]` (o detalhe
  não usa `panels`). Labels/formatters dos `ups.*` em `METRIC_LABEL`/`metricFmt`.

## Renomear entidade + trocar ícone (desde v3.10)

- **Nome custom**: coluna `Entity.display_name` (nullable) — **fora do `set_` do upsert**
  (`poller._persist`), então **sobrevive ao discover** (mesmo padrão de `icon`/`service_url`).
  `PATCH /entities/{id}/name` (admin, vazio→NULL volta ao descoberto); `api.setEntityName`.
- **Exibição**: helper `entName(e)` = `display_name || (host: INTEG_LABEL) || name`, usado em
  **cards, títulos e sidebar** (todo lugar que mostra nome).
- **UI**: `EntityEditModal` (nome + ícone, reusa o `IconPicker` como o `ItemModal`). Gatilho =
  **lápis** (`.nav-edit`/`.title-edit`, só admin) no hover dos itens da sidebar (hosts + UPS)
  e ao lado dos `h1` (detalhe e overview do host). O ícone já existia (`Entity.icon` +
  `PATCH /entities/{id}/icon` + `IconPicker`), agora exposto junto do rename.

## Aba Logs ampliada + filesystems + pills (desde v3.11)

Nasceu de um diagnóstico real de quedas do Proxmox (backup vzdump em `mode suspend`
enchia o `/` de 28 GB via `/var/tmp` → plano de gerência morria sem log). As três frentes:

- **Aba Logs (host Proxmox)** — `LogsTabContent`, novas fontes em `LOG_SOURCES`:
  - **Kernel** (`source="kernel"`): `node_ssh.get_kernel_log` = `journalctl -k -p warning -o json`
    (OOM killer, panics, hung tasks, MCE), mesclado no feed de `get_cluster_log` com
    `logfile = "kernel (journalctl -k)"`.
  - **Boots** (`source="boots"`, buscado sob demanda): `node_ssh.get_boots` = `journalctl
    --list-boots -o json` → `parse_boots` (puro, **testado**, µs→s). `ProxmoxIntegration.get_boots`
    calcula `gap_seconds` (fim de um boot → início do próximo); a UI destaca gap > 120s como
    freeze/reboot sujo (`log-tile-bad`). Rota `GET /entities/{id}/boots`; `api.boots`.
  - **Log de task inline**: no `LogModal`, entrada com `upid` ganha botão "Ver log completo da
    tarefa" → `api.taskLog` (texto cru, reusa `GET /tasks/{upid}/log`) exibido em `.task-log-raw`.
    Foi o log-chave do diagnóstico (vzdump guest a guest). `LogModal` agora recebe `entityId`.
  - **Profundidade**: `api.logs` puxa 250 linhas (era 100); teto da rota subiu p/ `le=500`.
- **Entidades `filesystem`** (`EntityType.filesystem`) — cada mount real do host (`df`, via
  `parse_mounts`, que já existia) vira entidade `proxmox/{node}/fs/{slug}` no `discover()`
  (slug: `/`→`root`, `/boot/efi`→`boot-efi`), emitindo `disk_used/total_bytes` no `collect()`.
  **Alerta de graça**: reusa as métricas de disco → a regra `resource_pct` já alerta cada FS
  (inclusive o `/`) sem código novo no motor. **Não** entram na sidebar/Home/overview — só na
  aba **Armazenamento** (card "Sistema de arquivos", reusa `StorageUsageRow` com `onPin`
  agora opcional) + no `EntitySelect` de regras. Inclui mounts de rede (CIFS/NFS).
- **Pills da sidebar** (`nav-item`):
  - **Posição**: `.nav-item > span:not(.status-pill)` com `flex:1`+ellipsis → o nome trunca e o
    pill fica ancorado à direita, independente do tamanho do título.
  - **UPS**: pill da sidebar vira **coleta**, não estado OL/OB — `connPill(upsCollected(status))`
    (`running/degraded/error` = tem dado do upsc = Conectado; `unknown` = Desconectado). O estado
    rico OL/OB continua no `UpsCard`/detalhe/alarmes.
  - **Uptime-Kuma**: host `uptimekuma/host` sempre `Status.running` quando o scrape do `/metrics`
    deu certo (chegar ao `discover` já prova); monitor caído = atributo `monitors_down`, não
    rebaixa o host (antes era `degraded if down` → sidebar mostrava "Desconectado" indevidamente).

## Diag — health check do host Proxmox (v3.15; contrato v2 desde v3.16; v3.17 = status info + checks de guests; v3.19 = categoria GPU)

Tile **Diag** na Overview do Proxmox → modal "Diagnóstico do Sistema" com health
check completo em **11 categorias** (10 espelhadas do ProxMenux — cpu, memory,
storage, disks, network, vms, services, logs, updates, security — mais **gpu**,
v3.19), rodando 1x/dia ou sob demanda. Design doc (v1):
`docs/superpowers/specs/2026-07-22-diag-health-check-design.md`.

**Adicionar categoria nova é declarativo**: entrada em `CATEGORIES`
(`proxmox_health.py`) + a mesma em `DIAG_CATEGORIES` (`App.jsx`) + seções no
`_SECTIONS` + um `check_*` chamado no `run_health`. Colapsar, contadores,
ligar/desligar, lápis de limite e alarme saem de graça do contrato v2.

- **Contrato v2 — items como fonte de verdade**: cada `check_*` devolve
  `{status, items, findings}`. **Item** = `{key, label, value, unit, limit_warn,
  limit_crit, below, thr_key, status: ok|info|warning|critical, message,
  detail?}` — **todos os testes aparecem, mesmo OK**. Os **findings** (o que
  vira alarme) são **derivados** em `_result(items)` dos items warning/critical,
  carregando `value`/`limit` numéricos → modal e alarme nunca divergem.
  **Status `info` (v3.17, azul)** = informativo: pinta a categoria mas **não
  vira finding/alarme** — usado por updates pendentes e reboot pendente
  (`THRESHOLDS[...]["sev"] = "info"` faz `_grade` devolver info no degrau warn;
  `_bin_item(severity="info")` pro binário). Item binário via `_bin_item` (sem
  limites); numérico via `_num_item` + `_grade(value, thr)`. Ordem de pior
  status: `_STATUS_ORDER` (ok < info < warning < critical). `key` truncada em
  64 chars (detecção de colisão em `evaluate_health`).
- **Limites configuráveis por CLASSE de item** (`thr_key`: `cpu:temp`,
  `storage:fs` vale pra todos os mounts, `logs:oom`…): defaults no registry
  `THRESHOLDS` (28 classes; `below: True` = limite mínimo, ex. dias de
  certificado; `sev: "info"` = degrau warn vira azul); overrides em
  `settings["health:proxmox:thresholds"]` (`THRESHOLDS_KEY`), mesclados por
  `effective_thresholds(overrides)`. Checks recebem `thr` como parâmetro
  (continuam puros). **Unidades honestas**: itens de contagem usam
  `eventos`/`pacotes`/`IPs`, nunca `%`.
- **Temperatura do CPU — só chip de CPU** (fix v3.19; antes o Diag mostrava a
  temperatura da **GPU**): a seção `cpu.sensors` roda `sensors **-j**` (sem o
  `-j` o `parse_sensors` falha calado e cai no fallback), e o fallback
  `cpu.hwmon` emite `<nome do chip> <millidegrees>` por hwmon — `parse_hwmon_temp`
  só aceita chips de `CPU_TEMP_CHIPS` (`coretemp/k10temp/zenpower/k8temp/cpu_thermal`,
  em `node_ssh.py`). Pegar "a maior leitura de qualquer hwmon" elegia o `nouveau`
  (GPU a 84°C num host cujo CPU estava a 33°C). `cpu_package_temp` casa o chip por
  **prefixo** pelo mesmo motivo — antes exigia `coretemp-isa-0000` exato e num host
  AMD (`k10temp-pci-00c3`) simplesmente não havia temperatura.
- **Checks adicionados na v3.17**: `cpu:usage` (duas leituras de `/proc/stat`
  com `sleep 1` na seção `cpu.stat` → `_cpu_usage_pct`); o item
  `cpu:temp` **sempre aparece** (bin "sem leitura" se nada disponível); swap
  sempre presente ("Sem swap configurado" quando SwapTotal=0);
  **`storage:guest:*`** = uso de disco dos guests (CT via `pct exec df -PB1 /`,
  VM via `qm agent get-fsinfo` — pega o fs mais cheio, VM sem agente não gera
  item; seção `storage.guestdf`, marcadores `===HCGUEST:<KIND>:<id>`,
  `_parse_guest_blocks`/`_guest_disk_items`). Dois acertos de v3.19/v3.20 nesse
  check, os dois achados **rodando no pod, não no pytest**: (a) ignora
  `erofs/squashfs/iso9660/udf/ramfs` e `zram*` — o `/` do **HAOS é erofs**, uma
  imagem read-only eternamente em 100%, e era ela que o "fs mais cheio" elegia
  na VM 109; deduplica **bind mount** pelo device (o `/` do k3s aparecia com o
  caminho gigante de volume do kubelet); (b) a seção virou **paralela** (cada
  probe num arquivo do `mktemp -d`, `wait`, `cat`): em série ~20 guests passavam
  dos 30s do `_bounded` e a seção era **cortada no meio** — os VMs, que vêm
  depois dos CTs, sumiam inteiros do resultado (30s+ → 8s);
  **`vms:ctstart/oom/qmp/vmstart`** = problemas de guests no journal
  (`_VM_ISSUE_PATTERNS` sobre a seção `vms.issues`: startup de CT/VM, OOM em
  guest via `/lxc/<id>` ou processo kvm, falha QMP; contagem + amostra).
- **Backend**: `backend/horus/integrations/proxmox_health.py`, testes em
  `tests/test_health.py`. Coleta = 1 script SSH em lote (`build_script`,
  marcadores `===HC:<nome>`/`===HCDISK:<dev>`, `_bounded` = timeout 30s por
  seção); categoria desativada nem entra no script. Journal agora coletado como
  **linhas** (`-o short-iso`, `tail -100`), não `grep -c`: o parser conta e
  guarda até 5 linhas como `detail` (OOM mostra o processo morto via regex
  `Killed process`). **df parseado por regex `_DF_LINE` ancorada na coluna
  `NN%`** — source com espaço (CIFS `//nas/My Share`) não desloca colunas (era
  bug real); mensagem com bytes humanizados (`_human_bytes`, base 1024).
  `run_health(ssh, disabled, thr_overrides)` → `assemble(...)` →
  `{ran_at, duration_s, overall, categories[{key,label,status,items,findings}]}`;
  falha SSH = `overall:"error"` + `error`, nunca levanta.
- **Categoria `gpu` (v3.19)** — três seções, porque **nenhuma fonte sozinha
  cobre os dois casos**: `gpu.pci` (`lspci -Dmmnn`, formato de campos entre
  aspas; o Python filtra as classes `0300/0301/0302/0380` e tira o `[10de]` do
  nome) vê a placa **mesmo sem driver**, que é como a GPU em **passthrough**
  aparece; `gpu.sys` (loop pelos `/sys/bus/pci/devices/*` de classe `0x03*`) vê
  só quem tem driver — que é justamente quem tem métrica: `driver`, hwmon
  (`temp1_input/max/crit`, `fan1_input`) e, no amdgpu, `gpu_busy_percent` +
  `mem_info_vram_used/total`; `gpu.nvsmi` (`nvidia-smi --query-gpu=...`, só roda
  se o binário existir) é o **único** caminho de uso/VRAM em placa NVIDIA.
  Parsers `parse_gpu_pci`/`parse_gpu_sys`/`parse_nvsmi` (normaliza o bus id de 8
  dígitos `00000000:01:00.0` pro de 4 do sysfs) fundidos por endereço PCI em
  `check_gpu`. Items por placa: `:info` (binário sempre ok — fabricante, modelo
  comercial via `_short_model`, driver ou "em passthrough (vfio-pci), sem
  métricas no host"; `detail` com PCI, limites do fabricante e RPM da ventoinha),
  `:temp`, `:usage`, `:vram` — **item ausente quando o dado não existe**, igual a
  "VM sem qemu-agent". Limites: `gpu:temp` 90/100 e `gpu:vram` 90/97;
  **`gpu:usage` nasce sem limite** (`warn`/`crit` None) porque GPU a 100%
  transcodificando é uso normal, não defeito — quem quiser alarme põe o dele
  pelo lápis. **Armadilha**: `nouveau` **não expõe uso nem VRAM** em lugar
  nenhum (nem no debugfs, que só tem `pstate`) — nessas placas só saem
  identidade + temperatura, e isso é o teto do driver, não bug do Horus.
- **Persistência**: último resultado em `settings` — `RESULT_KEY =
  "health:proxmox"`, `DISABLED_KEY`, `THRESHOLDS_KEY`. `run_and_store` com
  `asyncio.Lock` (concorrente espera e recebe o estado); `get_state()` →
  `{result, disabled, thresholds (efetivos), running}`. Agendamento diário:
  `maybe_schedule` no loop do poller (sonda DB a cada 10 min; roda se >24h);
  `shutdown()` cancela a task de fundo no stop do poller.
- **Alarmes** (métrica `health`, regra semeada "Diagnóstico do sistema"):
  `evaluate_health` — 1 `AlarmEvent` por finding (match `resource`=key), sem
  pending; **`value`/`threshold` do evento preenchidos com o valor/limite reais
  do item** (desde v3.16; antes 0/0). Push Gotify **agregado** por execução.
  Coluna `alarm_events.message` = texto humano — exibida nas abas Ativos/
  Histórico **e no banner do topo do `.main`** (o banner era o 3º ponto de
  render esquecido na v3.15: mostrava "X acima do limite de 0% — valor 0%").
  `evaluate_health` comita; `resolve_health_category` não (chamador comita).
- **API**: `GET /entities/{id}/health` · `POST .../health/run` (admin, síncrono
  ~10-60s) · `PUT .../health/config` (admin) com body `{disabled?: [...],
  threshold?: {key, warn, crit}, excluded_guests?: ["qemu/N","lxc/N"]}` —
  `disabled` resolve alarmes da categoria desativada; `excluded_guests` é
  lista de exclusão (vazia = todas as VMs/CTs entram no disco de guest e no
  onboot; guest nova entra sozinha); ao **acrescentar** um ID, resolve
  `storage:guest:vm-N`/`ct-N` e `vms:N` na hora. `threshold` mescla no
  override da classe (400 se key fora do registry; `null` limpa o degrau).
  `api.health` / `api.runHealth` / `api.setHealthConfig(id, disabled)` /
  `api.setHealthThreshold(id, key, warn, crit)` / `api.setHealthExcluded(id, excluded_guests)`.
  Persistência: `EXCLUDED_KEY = "health:proxmox:excluded_guests"`. O script
  `storage.guestdf` dá `continue` nos IDs excluídos (não gasta o timeout de 5s).
- **Frontend** (`App.jsx`): tile "Diag" (`Stethoscope`) via `extra` do `Tiles`
  (aceita `icon`/`onClick`); `diagTile(health)` agrega valor+cor. `DiagModal`
  ("Diagnóstico do Sistema", **sem pill de status geral no topo** — removida na
  v3.17, fica só o transPill "Executando" durante o run): **cabeçalho-resumo**
  (`diagSummary`) com **contadores grandes e centralizados** (`.diag-count`:
  críticos/atenção/**info azul**/OK, separados da lista por divisor; desde v3.19
  o número vai num `<b>` de 22px dentro do pill, com o rótulo em 13px ao lado, e
  a faixa usa `justify-content: center`) + lista de falhas clicável
  ordenada crítico>atenção>info (badges alinhados `min-width`) que expande e
  rola até a categoria (`jumpTo` + `catRefs`); **categorias colapsáveis**
  (chevron, `expanded: Set`, teclado Enter/espaço); `DiagItemRow` = dot
  colorido + label + `valor — Limite X · crítico Y` (`diagVal`/
  `diagLimitLabel`) + pill Normal/Info/Atenção/Crítico + mensagem + `detail`
  em mono (`.diag-detail`); **lápis (admin) nos itens com `thr_key`** abre
  `DiagThrEdit` inline (warn/crit, vazio = desativado; salvo via
  `setHealthThreshold` — vale a partir da próxima execução). Resultado antigo
  sem `items` → aviso "execute novamente" + fallback na lista de findings.
  Azul: `.hbadge.info` e `.diag-dot.info` (par de `.badge.sev-info`). CSS
  `.diag-summary/.diag-count/.diag-item/.diag-dot/.diag-thr-edit/.diag-detail`;
  no mobile `.diag-item-val` desce pra linha própria (bloco ≤820px).
  `AlarmsRulesTab` filtra `health` do CRUD.
  **VMs/CTs no diagnóstico (v3.26)**: card `DiagGuestsCard` na Configurações
  (não no modal) — lista vm/ct do inventário Proxmox, checkbox marcado = entra;
  `todas`/`nenhuma`; CSS `.diag-guest-*`. Journal de OOM/QMP **não** filtra por guest.
- **Banner de alarmes agrupado** (topo do `.main`, desde v3.17): com >1 alarme
  ativo mostra só o primeiro + botão **`.alarm-more`** com `+N`; clicar expande
  todos (vira `ChevronUp` pra recolher). State `alarmsExpanded` no `App`.
- **Verificação visual sem backend**: os mocks desta feature foram validados
  com a técnica de `references/css-layout.md` (HTML estático + Playwright do
  cache do npx: `createRequire("/home/kiwel/.npm/_npx/<hash>/node_modules/")`).

## RAM de guest do Proxmox — de onde vem o número (v3.18)

A API do PVE tem **dois `mem` diferentes** pro mesmo guest, e o endpoint mais
óbvio é o errado. `/nodes/{node}/qemu` (a lista por nó) devolve em `mem` a
memória do processo KVM no host — o `memhost` —, que só cresce: página que o
guest tocou uma vez nunca volta pro host, e o page cache dele conta junto. O
valor sobe até a alocação total e trava lá pra sempre.

- **Fonte certa** = `/cluster/resources?type=vm`, lido por `_guest_mem()` em
  `proxmox.py`. Uma chamada só cobre qemu **e** lxc de todos os nós, traz todos
  os contadores que a lista por nó tem (`cpu`, `maxmem`, `disk`, `maxdisk`,
  `netin`, `netout`, `diskread`, `diskwrite`, `uptime`, `status`) e ainda expõe
  `memhost` como campo separado. A chave `id` já vem no formato `qemu/124` /
  `lxc/102`, que é exatamente o sufixo do `eid` — por isso o mapa é keyed por
  `f"{kind}/{vmid}"` e não precisa remontar nada.
- `.../qemu/{vmid}/status/current` também traz o valor certo, mas custa **N
  chamadas por ciclo**. Foi por isso que ficou de fora.
- `_guest_mem()` usa `_get_opt`: se a chamada falhar, devolve `{}` e o `collect()`
  cai no valor da lista em vez de quebrar a coleta inteira. O custo desse
  fallback é ser **silencioso** — se o token perder permissão, o número volta a
  ficar errado sem nenhum erro no log. É o que a verificação abaixo cobre.

**Não dá pra testar isso sem o balloon do lado do Proxmox.** Sem o device
virtio-balloon na VM (`balloon: 0` no config), `mem == memhost` nos dois
endpoints e os dois concordam — o defeito fica invisível. Só aparece em VM com
balloon ativo. Detalhes do lado do PVE (incluindo que o `qm set --delete balloon`
cai em `[PENDING]` e exige stop/start completo) estão na skill `proxmox`,
seção "VM Memory Reported at ~100%".

Ao ler os números corrigidos: o balloon reporta `total_mem - free_mem` e conta
page cache do guest como usado. É um teto honesto, não o `used` do `free -m` —
VM com ZFS (ARC) ou banco de dados ocupado continua alta, e está certa.

### Verificar integração com credenciais reais (sem mexer em segredo)

O análogo backend da "verificação visual sem backend": rodar código da integração
**dentro do pod**, que já tem a config hidratada do banco e o token decifrado.
Evita ter que extrair credencial do Secret pra testar, e prova o caminho de ponta
a ponta em produção — inclusive se o `_get_opt` está caindo em fallback.

```bash
POD=$(kubectl get pod -n horus -o jsonpath='{.items[0].metadata.name}')
kubectl cp verify.py horus/$POD:/tmp/verify.py
kubectl exec -n horus $POD -- python /tmp/verify.py
kubectl exec -n horus $POD -- rm -f /tmp/verify.py
```

O script precisa de `await init_db()` e `await appconfig.hydrate()` antes de
instanciar a integração — sem o hydrate, `settings` fica com o que veio do `.env`
e não com a config do banco, que é a fonte de verdade.

## Tiles de IO delay e Swap na Overview do Proxmox (v3.21; swap no gráfico de RAM desde v3.25)

- **IO delay** = `st["wait"]` do `/nodes/{node}/status`, que vem como **fração**
  igual ao `cpu` (0.0614 = 6.1%) — é o mesmo número do resumo do PVE. Sample
  `proxmox.io_delay_pct` (×100), na chamada que o `collect()` já fazia: **zero
  requisição extra**. O `rrddata` também tem `iowait`, mas é média do bucket de
  1 min e o `wait` é instantâneo — por isso o status ganhou.
- **Swap** já era coletado desde antes (`proxmox.swap_used_bytes`/`_total_bytes`,
  só emitidos quando `swap.total` > 0). Desde v3.25 **não há painel/tile
  próprio**: a % de swap é a **2ª série** do painel Memória (mesmo padrão do
  load no CPU — tile `X% · swap Y%`, head com bytes).
- **Frontend**: métricas no `NEED["proxmox/host"]` + painel host-only
  `iodelay` depois do CPU/temp. Overview filtra tiles com
  `OVERVIEW_TILE_KEYS` (cpu/cputemp/iodelay/mem/net/disk) — Disco I/O e PSI
  ficam **só nos gráficos**.
- **Nome `io_delay_pct`, não `io_delay`**, de propósito: `metricFmt`/`metricUnit`
  casam por regex `/pct|percent/` — com o sufixo, formatação em % e gauge 0-100
  saem sozinhos. Ambas entraram em `METRIC_LABEL` + `RULE_METRICS` (regra de
  alarme genérica e gauge/gráfico da Home).
- **Sem `alert` nos tiles**: o `Tiles` só pinta alerta a partir dos limites de
  cpu/mem/disco (`PANEL_RES` + `thr`) — limite fixo pra IO delay/swap seria
  chute, quem quiser alarme cria a regra.

## Disk IO + Pressure Stall (PSI) — overview e detalhe VM/LXC (v3.23; fix fish v3.25)

Métricas de **Pressure Stall Information** do PVE 9 e Disco I/O do host na
UI, no mesmo padrão dos tiles/painéis da v3.21.

- **Host overview** (`OverviewTabContent` Graphs): além de CPU/Mem, filtra
  `diskio`, `psicpu`, `psiio`, `psimem`. Tiles desses painéis **não** aparecem
  na overview (só gráficos).
- **Página dedicada VM/LXC**: `Graphs panels={panels}` — entram os 3 painéis
  PSI; Disco I/O do guest já existia (`disk_read/write_bytes`).
- **PSI**: samples namespaced `proxmox.pressure.{cpu,io,mem}_{some,full}_pct`.
  Host lê o **último ponto do RRD** (`/nodes/{node}/rrddata`) — o `/status`
  do nó **não** traz `pressure*`. Guest lê a lista `qemu`/`lxc` (campos
  `pressurecpusome`…). Nó RRD **não tem** `pressurecpufull`. PVE &lt;9 → sem
  sample (`.get` opcional). Helper `_pressure_samples` + testes.
- **Disk IO do host**: RRD do nó **não tem** diskread/write — taxas via SSH
  `/proc/diskstats` (`parse_diskstats` só discos inteiros, `_disk_rates` entre
  ciclos) → `proxmox.disk_read_rate` / `disk_write_rate`. **Armadilhas**
  (sintoma: taxas sempre 0):
  1. `@@diskstats@@` **antes** do `disklink` (smartctl em cada `sd*` estoura
     o timeout 15s).
  2. **Login shell do root no Proxmox = fish** — `sshd` roda `fish -c <script>`
     e qualquer `var=value` bash dá exit 127 com stdout vazio (o `gather()`
     inteiro morre). `NodeSSH._run` força `/bin/bash -c …`; o Diag
     (`proxmox_health.run_health`) reusa `_run`. `_disk_rates({})` **não**
     emite 0 nem envenena o prev.
  Primeiro ciclo SSH bom não emite taxa (só arma o prev).
- **Disk IO de VM**: a lista `/nodes/.../qemu` manda `diskread`/`diskwrite` =
  `null`; a fonte certa é `/cluster/resources?type=vm` (mesmo endpoint do
  balloon). `_guest_runtime` / `_guest_runtime_map` traz mem + I/O numa chamada;
  LXC já vinha certo na lista, mas usa a mesma fonte.
- **UI**: `pushPsiPanel` (Some amarelo / Full vermelho); `NEED`, `METRIC_LABEL`,
  `RULE_METRICS` (some de cpu/io/mem).

## Overview Docker espelha a VM Proxmox (v3.25)

- Casa host Docker ↔ VM/CT Proxmox pelo **nome descoberto** (`docker/Docker` ↔
  VM `Docker` / vmid 101).
- `loadPanels` busca `DOCKER_VM_NEED` (disk_used/total + PSI) na entidade
  Proxmox; `buildDockerPanels(raw, vmRaw)` monta painéis `disk` + PSI.
- Tiles: CPU, Memória, Disco (além de Rodando/Parados/Imagens…).
- Gráficos: cpu, mem, disk, diskio, psicpu, psiio, psimem, net.

## A poda do inventário apagava UPS e filesystem (v3.22)

Sintoma relatado como "renomear a UPS não salva no banco, salva local". **O
salvamento nunca foi o problema**: o `PATCH /entities/{id}/name` grava e o
`_persist` já preserva `display_name`/`icon`. Quem apagava era a **poda de
inventário** do `poller._persist`.

- **Causa**: o `discover()` do Proxmox é **metade API, metade SSH** —
  `node_ssh.gather()` devolve `{}` em **qualquer** falha de SSH (timeout, host
  ocupado, primeiro ciclo depois de um restart). Nesse ciclo `ups` e
  `filesystem` somem do resultado, mas host/vm/ct continuam vindo da API. A
  guarda que existia só perguntava "o discover veio vazio?" — não veio, então a
  poda rodava e **deletava a linha da UPS e de todos os FS**. O ciclo seguinte
  recriava tudo em branco, levando junto `display_name`, `icon`, `service_url`,
  `kuma_monitor_id`, thresholds por entidade e `alarms_muted`. Some sem log de
  erro (o `gather` loga só um warning de SSH) e o intervalo entre renomear e
  perder pode ser de horas — daí parecer "armazenamento local".
- **Fix**: poda **por tipo** — só apaga entidades cujo `type` apareceu naquele
  discover (`Entity.type.in_(types)`). Se nenhuma `ups` veio, nenhuma `ups` é
  apagada. Preço: remover o **último** item de um tipo deixa fantasma até voltar
  algum irmão — mesmo trade-off da guarda de "discover vazio".
- **Lição de diagnóstico**: o log de acesso do **ingress-nginx** é a prova
  barata de que o front mandou a requisição e ela deu 200
  (`kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller |
  grep "PATCH /api/entities"`). Com isso o dedo sai do front/rota e vai pro que
  reescreve a linha depois. O outro atalho: rodar o PATCH real de dentro do pod
  (ver "Verificar integração com credenciais reais").

### Seções de `ups`/`filesystem` na overview (mesmo release)

`machines` (no `App`) filtrava só `e.type !== "host"`, então `ups` e
`filesystem` caíam no fallback `e.type` do `dispGroup` e viravam **seções de
cards de máquina** na overview da integração. Agora existe
`NON_MACHINE_TYPES = {host, ups, filesystem}`. A UPS mora na sidebar, os
filesystems na aba Armazenamento. Removido junto o `UpsEntityCard` e a prop
`upsEntity` do `OverviewTabContent`, que já eram código morto.

## Integração Kubernetes (estado atual)

- **Backend**: `backend/horus/integrations/k8s.py` — descobre nós, deployments, pods; coleta CPU/mem; executa `scale`, `rollout_restart`, `set_resources`
- **Config**: `K8S_API_URL`, `K8S_TOKEN`, `K8S_VERIFY_TLS`, `K8S_CLUSTER_NAME` em `.env`
- **UI**: `K8sOverviewContent` no `App.jsx` com 5 `StatTile` (CPU cluster, Memória, Nós prontos, Pods rodando, Deployments) + grids de cards `K8sNodeCard/K8sDeployCard/K8sPodCard`
- **Modais**: `K8sNodeModal` (info do nó + métricas live), `K8sDeployModal` (deployment info + botões ação), `K8sScaleModal` (réplicas), `K8sResourcesModal` (cpu/mem req/lim por container), `K8sPodModal` com log ao vivo (polling + seletor de container)
- **Logs de pod**: `get_pod_log()` no backend (equivale a `kubectl logs --tail`; sem container informado, descobre via spec e usa o primeiro) → `GET /entities/{id}/podlog?tail=&container=` → `api.podLog(id, container)`
- **Rollout status**: `get_rollout_status()` → `GET /entities/{id}/rollout` (réplicas desired/updated/ready/available + `done`) — usado pelo `ProgressModal` no `App.jsx` pra acompanhar ações ao vivo; o análogo Proxmox é `get_task_status(upid)` → `GET /entities/{id}/tasks/{upid}/status` (node extraído do próprio UPID) → `api.taskStatus(id, upid)`
- **Ícone**: ALIASES em `icons.js` mapeiam `k8s → "kubernetes"` e `k3s → "kubernetes"` para o dashboardicons.com
- **Label**: `INTEG_LABEL["k8s"] = "Kubernetes"` e `INTEG_ICON["k8s"] = Boxes`
- **Identificação**: integração = `"k8s"`, entity types: `node`, `deployment`, `pod`; host entity tem `type = "host"`, `integration = "k8s"`
- **Estados transitórios de pod**: attributes `terminating` (via `metadata.deletionTimestamp` —
  a phase da API continua "Running" durante graceful shutdown) e `waiting_reason` (1º container
  travado: ContainerCreating, CrashLoopBackOff, ImagePullBackOff…). O `K8sPodCard` deriva o visual:
  `.machine.k8s-terminating` (esmaece em ciclo, keyframe `term-fade`) · `.machine.k8s-starting`
  (âmbar pulsante, `pulse-warn`) · reason com `BackOff|Err|Invalid` vira card `alert` com o reason
  como pill. Pills transitórias usam o helper `transPill(label, cls)` (spinner embutido, `.status-pill.trans`).
- **Status de ação nos cards**: `runK8sAction` alimenta o mapa `k8sOps` (state do `App`, keyed por
  entity.id: `{verb, phase, detail, error}`) → `K8sOpStrip` renderiza faixa no card (azul executando
  com progresso do rollout, verde ok some em 6s, vermelho erro fica 20s). Deploy convergindo
  (`ready < total`) mostra pill "Atualizando" e barra listrada animada (`Bar` com prop `busy`,
  classe `.bar span.busy` + keyframe `bar-stripes`).

## Home (estado atual)

- **View**: `HomeView` no `App.jsx`, ativa quando `integ === "home"` (default de landing,
  item fixo no topo da sidebar). Focada em **atalhos de serviços** — não renderiza cards
  de VMs/containers/pods (isso fica em cada integração).
- **Tiles**: um por integração presente (Proxmox/Docker/K8s com contagem ▶ rodando / ■ parado
  via helper `countsFor`; TrueNAS com espaço livre somado de `host.attributes.pools[].free`),
  depois "RAM em uso" (mem do host Proxmox via `latestMap`), UPS (mesma lógica
  `upsStatusLabel`/`upsClass` da Overview Proxmox) e Alarmes ativos. Ícones dos tiles de
  integração = `IntegIcon` (mesmo do menu), adaptado ao prop `icon` do `StatTile` pelo
  helper `integIcon(name)`.
- **Itens**: persistidos em `prefs.homeItems` = `[{id, type, group?, x/y/w/h, ...}]`, com
  `type ∈ shortcut|chart|tile|gauge`. Migração preguiçosa do legado (`prefs.shortcuts`/
  `homeCharts`) via `migrateHome` — as chaves antigas ficam **intocadas** (rollback-safe).
  `ItemModal` cria/edita; cada card tem lápis (editar) e `Copy` (**duplicar** → `cloneItem`,
  id novo, uma linha abaixo, mesmo grupo).
- **Layout**: `react-grid-layout` por grupo (`GroupGrid`), 12 col no desktop / 2 no toque;
  `x/y/w/h` gravados **só no fim do gesto** (`applyLayout` em onDragStop/onResizeStop) e só
  no layout de 12 col. Alça de arraste = `.sc-grip`.
- **Grupos**: `prefs.homeGroups` = `{[nome]: {icon?, collapsed?}}` + **ordem explícita** em
  `prefs.homeGroupOrder` (array). NÃO derivar a ordem dos itens — senão mover um item de
  grupo reordena os grupos (bug corrigido). `moveGroup` reordena (setas ↑↓ no cabeçalho);
  toda gravação **congela** a ordem atual em `homeGroupOrder`. `+` no cabeçalho pré-preenche
  o grupo no `ItemModal`; o campo "Grupo" (input + `datalist`) move o item entre grupos.
  **Não há drag entre grupos** (grades RGL separadas) — usar o campo "Grupo".
- **Vínculos do atalho**: `entity` (vm/ct/container/pod/deployment → pill `scStatus`:
  running=verde · paused/degraded/restarting=âmbar · resto=vermelho · sumiu=cinza) e `kuma`
  (monitor Uptime-Kuma → ícone `Activity`). `icon`: slug do dashboardicons OU data URI
  (upload vira base64 no pref, cap 300 KB); `ShortcutIcon` reconhece `data:`.
- **Persistência = banco**: `savePrefs` → `PUT /api/me/prefs`. Sessão `user:…`
  grava em `users.preferences`. Token de API grava em `tokens.preferences`
  (blob próprio). GET vazio no token lê a Home do 1º usuário como semente —
  o primeiro PUT copia o blob para o token. Sem blob no token e sem usuário,
  GET `{}`; PUT de token autenticado sempre persiste. Senha (`POST /me/password`)
  continua só na sessão de login. Escopos efetivos do agente = união com os do
  1º usuário (em memória; a coluna `tokens.scopes` não muda). `GET /me` traz
  `has_password` (UI de senha) e o username do dono da instância. **Gotcha**: o blob
  carrega os ícones base64, então o ingress precisa de `nginx.ingress.kubernetes.io/proxy-body-size`
  (default 1 MB dava 413 e o save sumia). `savePrefs` mostra toast em qualquer erro de
  persistência. Ver `docs/superpowers/specs` e a memória do projeto.
- **Dados**: a Home carrega `latestAll("")` (sem filtro de integração) no `loadOverview`.

## Configurações — conexões das integrações no banco (estado atual)

Aba **Configurações** (`ConfigView` no `App.jsx`, `integ === "config"`, item de
sidebar só-admin abaixo de "Alarmes"). Permite editar as conexões de todas as
integrações pela UI, guardando as credenciais **cifradas no banco** em vez do
`.env`.

- **Fonte de verdade = banco**; o `.env`/Secret só **semeia** no 1º boot. O
  `settings` (pydantic) segue sendo a config viva em memória: o banco o sobrepõe
  no boot (`appconfig.hydrate()`, chamado no `lifespan` antes do `poller.setup()`)
  e a cada save. **As integrações não mudaram** — continuam lendo `settings.*`.
- **Schema declarativo** em `core/config_schema.py` (`SCHEMA`): fonte única que
  dirige o que é secret (cifrado), a resposta da API, a validação e o formulário
  do front. Campos batem 1:1 com atributos de `config.py`.
- **Cofre** em `core/secrets.py` — Fernet com `settings.horus_secret_key`
  (env `HORUS_SECRET_KEY`, base64 32 bytes; **obrigatória** pra cifrar/semear
  secrets — sem ela só campos não-secretos salvam). **Nunca trocar a chave
  depois de salvar** (o cifrado deixa de decifrar). Nova dep `cryptography`.
- **Armazenamento**: reusa a tabela `settings` (key→JSONB), 1 linha por
  integração `conn:{nome}`, secrets guardados como ciphertext.
- **`core/appconfig.py`**: `hydrate()`, `get_all()` (mascara secrets → manda
  `secretsSet: bool`, nunca o valor), `save()` (cifra, grava, atualiza o
  `settings` em memória, chama `poller.request_reload(nome)`), `resolve_stored()`
  (decifra + patch, pro teste). Funções puras (`mask`/`merge_patch`/`seed_from_settings`/
  `apply_to_settings`) isoladas do DB e **testadas** (`tests/test_appconfig.py`,
  `test_secrets.py`).
- **Reload ao vivo**: `poller.request_reload(nome)` enfileira; `_drain_reloads()`
  roda no início de cada ciclo (na própria task do poller, sem mutar `instances`
  no meio de um ciclo): fecha o cliente antigo e re-instancia — ou remove se
  ficou sem config. Efeito no próximo ciclo (~15s), sem reiniciar o pod.
- **Testar conexão**: `Integration.test_connection(cfg)` (staticmethod, default
  levanta) implementado por integração (chamada barata: `/version`, `/info`…);
  Gotify (que não é Integration) tem `notify.test_connection`.
- **Rotas** (admin): `GET /config` (schema + valores mascarados + `hasKey`),
  `PUT /config/{integ}`, `POST /config/{integ}/test`. `api.js`: `getConfig`/
  `putConfig`/`testConfig`.
- **Layout**: `.cfg-grid` usa **colunas (masonry)** — cards pequenos na altura
  natural, os menores empilham na mesma coluna (não esticam à altura do maior).
- **Poço (HUD, v4.5)**: `.cfg-field` input com fundo `--bg`, padding 10–12px,
  radius 8px; texto de ajuda por integração em `CFG_HELP` (não muda o schema).

## Overview/inventário HUD (v4.5)

Não é o System Report navy revertido. Visual Homelab HUD (cobalt). Spec:
`docs/superpowers/specs/2026-09-19-proxmox-overview-inventory-design.md`.

- **`discover()` Proxmox:** host `attributes.firewall` (`GET /cluster/firewall/options`,
  omitido se falhar) e `attributes.services` (SSH `@@services@@` /
  `parse_pve_services`, depois de diskstats e antes de disklink). Guest
  `attributes.maxdisk` da lista PVE. Sem rota nova.
- **Overview Proxmox** (depois dos tiles/gráficos): Uso de CPU + Uso de RAM;
  overcommit vCPU/RAM **só guests `running`**; Maiores consumidores (RAM/CPU/
  Disco/I/O/Rede); inventário lista (default) ou tiles. Coluna de armazenamento
  = **Disco** (`maxdisk`), nunca FS. `guestDiag` usa `resThr`, não o Diag.
- **Docker:** mesmo toggle lista/tiles. Sem overcommit/consumidores.
- **Prefs** (`PUT /me/prefs`): `collapsedCards` (`cpuUsage`, `ramUsage`,
  `vcpuOvercommit`, `ramOvercommit`, `topConsumers`, `proxmoxInventory`,
  `dockerInventory`) e `inventoryView` `"list"` | `"tiles"`. Não reusar
  `prefs.guestInventory`.
- **Rede / Hardware:** `FirewallCard` só leitura (ausente = Indisponível);
  chips `pvedaemon` `pveproxy` `pvestatd` `pve-cluster` `pvescheduler`
  (verde = `active`). Desde v4.6, card **Serviços Host** no `.grid2` ao lado
  (systemd `running`, sem systemd-*/getty/user@/qemu@/lxc@/pve*).
- **v4.6:** tiles desktop nowrap (host e detalhe VM/CT); swap em GB no tile
  e 2ª série no gráfico quando há amostra; alarme `*_bytes` sem `%`; Uso de
  CPU = `proxmox.loadavg` + alocada vs em uso. VM sem `swap`/`maxswap` = `—`.
- **Kuma:** `types_to_prune` em `poller.py` não poda `monitor` se o discover
  do UK veio sem esse tipo. `KumaMonitorSelect` mantém a `<option>` do id
  salvo se sumiu da lista viva; só limpa com "— sem monitor —".
- Tiles desktop: `.tiles` flex nowrap. Desde v4.9 o conteúdo do tile fica
  centrado (`.tile` flex column, padding `8px 10px`). `OverflowTip` põe
  `title` nativo só quando o texto (ou um filho) estoura
  `scrollWidth`/`scrollHeight`; texto que cabe não ganha hover.
  Fora: aba Backup, restyle NIC/storage, tema navy.

## Cards de entidade — glifo de estado + vínculo Uptime-Kuma (estado atual)

Os cards de **vm/ct** (`MachineCard`), **container** (`DockerContainerCard`) e
**pod** (`K8sPodCard`) mostram, no canto sup. direito (`.m-badges`), dois glifos:

- **Estado** (`stateGlyph`/`stateGlyphFor`, ícone `CirclePlay` = "executando"):
  substitui a antiga pill de texto. Cor por `.m-state.{ok|bad|warn|off}`; hover
  = label do status (inclui transitórios do pod: `Terminando`/`Subindo`/reason
  `CrashLoopBackOff`). Não-clicável (ações continuam no rodapé).
- **Monitor Uptime-Kuma** (`monitorGlyph`, ícone `Activity` colorido): só se a
  entidade tiver um monitor vinculado. Resolver `monitorFor(ent)` no `App`
  (reusa `monitorState`/`MONITOR_STATE`), passado via prop pelos containers
  (`MachineGroups`/`DockerOverviewContent`/`K8sOverviewContent`). Hover =
  `Uptime-Kuma: no ar · 12 ms`, igual ao ícone dos atalhos da Home.
- **Vínculo** persistido na coluna **`Entity.kuma_monitor_id`** (migration em
  `db.py`; sobrevive ao discover como `service_url`). Editado no `LinkModal`
  (botão 🔗 do card), que agora tem URL do serviço + `<select>` de monitor;
  salvo via `PATCH /entities/{id}/link` (body `{url, kuma_monitor_id}`),
  `api.setEntityLink(id, url, kuma_monitor_id)`.
- **Pill de conectividade dos hosts** (`connPill`): no menu lateral e no título
  da integração, o status do **host** vira **"Conectado"** (running) / **"Desconectado"**
  (unreachable). VMs/containers/pods mantêm o glifo de estado (rodando/parado).
- **Ícone de backup** (`MachineCard`, Proxmox): o `title` fica num `<span>`
  (`.m-bk-wrap`), não no `<svg>` — em SVG o atributo `title` não vira tooltip.

## Sidebar recolhível (estado atual)

- State `navCollapsed` no `App` (persistido em `localStorage["horus.navCollapsed"]`),
  classe `.app.nav-collapsed`. Botão **«** (`ChevronsLeft`) no `.brand` recolhe;
  **»** (`ChevronsRight`, `.nav-expand`) no `.appbar` reabre.
- No modo recolhido a `.app` vira **coluna única** (`grid-template-columns: 1fr`)
  e a `.sidebar` some (`display:none`) — **não** use `0 1fr`, pois a aside com
  `display:none` sai do grid e o `.main` cairia na faixa de largura zero.
- Só desktop: no bloco mobile (`≤820px`) `.nav-collapse`/`.nav-expand` têm
  `display:none` (lá quem manda é o drawer `navOpen`).

## Deploy / release (estado atual)

- **Imagem única** `kiwel/horus:vX.Y` no Docker Hub (`docker build` na raiz →
  `docker push`), tag `latest` junto. O FastAPI serve o front buildado
  (imagem multi-stage; `cryptography` é dep de runtime desde a config no banco).
- **Bump de versão**: editar `deploy/app/02-app.yaml` (`image: kiwel/horus:vX.Y`)
  e commitar. Versão atual deployada: **v4.9** (v3.8 = página de alarmes + prefs
  da Home; v3.9 = entidade UPS/NUT + alarme on-battery + mensagem custom nas regras;
  v3.10 = renomear entidades + trocar ícone na sidebar/títulos; v3.11 = aba Logs
  ampliada [kernel/boots/log de task inline] + entidades `filesystem` no armazenamento
  + correção dos pills da sidebar; v3.12 = fixes do Uptime-Kuma + card de armazenamento;
  v3.13/v3.14 = mobile/responsividade [login, pills da sidebar, margens, home mobile,
  menus]; v3.15 = **Diag** — health check do host Proxmox; v3.16 = **Diag v2** —
  items detalhados com valor/limite, limites configuráveis, detalhe de journal,
  fix do df com espaço e do banner de alarmes; v3.17 = **Diag v2.1** — status
  info azul [updates sem alarme], uso de CPU + fallback hwmon, disco dos guests,
  checks de startup/OOM/QMP de VMs/CTs, resumo com contadores grandes e banner
  de alarmes agrupado com +N — ver seção própria; v3.18 = **fix da RAM de guest**
  vinda do `/cluster/resources` — ver seção própria; v3.19 = **Diag: categoria
  GPU** + fix da temperatura do CPU que mostrava a GPU + fix do disco de guest
  em erofs/bind mount + contadores do resumo maiores e centralizados; v3.20 =
  seção `storage.guestdf` em paralelo, que em série estourava os 30s e cortava
  os VMs do resultado — as três últimas na seção do Diag; v3.21 = tiles de
  **IO delay** e **Swap** na Overview do Proxmox — ver seção própria; v3.22 =
  **fix da poda do inventário**, que apagava a UPS e os filesystems num soluço de
  SSH e levava junto nome/ícone/limites, + remoção das seções `ups`/`filesystem`
  da overview — ver seção própria; v3.23 = **Disk IO + Pressure Stall (PSI)** na
  overview do host e no detalhe de VM/LXC — ver seção própria; v3.24 = **fix Disk
  IO** — host (diskstats antes do smartctl/timeout SSH) e VMs (I/O via
  `/cluster/resources`, não a lista `/qemu` que manda null); v3.25 = overview
  Proxmox sem tiles Disco I/O/PSI + swap no gráfico de Memória + fix SSH fish
  (`NodeSSH._run` → bash) + overview Docker com tiles CPU/RAM/Disco e gráficos
  Disco/PSI da VM homônima; v3.26 = **Diag: lista de exclusão de VMs/CTs** —
  card na Configurações, vale para disco de guest e onboot, alarme resolve na
  hora; journal agregado no host continua; v3.27 = **temperatura do UPS**
  (`ups.temp`); v3.28 = **varredura segurança + clique** — conectividade que
  levanta, SSE ticket, rate-limit login, SVG sandbox, pod não-root, Alarmes
  clicável na linha, Kuma `null`/grupo, Docker host CPU ÷ NCPU, `ups.input_frequency`,
  Diag “Atualizações”, labels pt-BR / mobile);
  v3.29 = **links só na Home**; portas Docker = bind no host;
  v3.30 = **Homelab HUD UX** — PRODUCT/DESIGN.md (Impeccable), motion rack-blade
  + View Transitions, layout chrome unificado + container queries, distill
  thumb-first ≤820px [appbar sticky, ações ícone-only, gráficos 132px,
  alarm strip rolável], polish [focus-visible, login labels, modal-actions];
  v4.0 = polish de transição (sem VT / sem flash preto), tiles Home restaurados,
  overflow dos cards, shell centrado em telas largas, portas Docker +N, nomes
  por extenso na sidebar;
  v4.1 = chrome host (ações nas abas Proxmox/TrueNAS, sem IP no Proxmox), tiles
  sem ellipsis, Home spacing, sidebar `.nav-label` 1 linha sem wrap;
  v4.2 = sidebar 340px + nomes por extenso sem ellipsis (nowrap + max-content);
  v4.3 = **prefs via token de API** — GET/PUT `/me/prefs` em sessão só-token
  compartilha o blob do 1º usuário; o agente vê a mesma Home da sessão logada;
  v4.4 = **Home do agente + escopos da conta** — `tokens.preferences` próprio
  (GET vazio lê a Home do 1º usuário); `authenticate()` une os escopos do dono
  da instância; `GET /me.has_password` esconde "Alterar senha" no token);
  v4.5 = **overview/inventário HUD** — painéis CPU/RAM, overcommit só guests
  rodando, maiores consumidores, inventário lista/tiles (Disco = `maxdisk`,
  nunca FS), inventário Docker no mesmo toggle, firewall na Rede, chips PVE
  no Hardware, Config em poço, vínculo Kuma estável (`types_to_prune` +
  `KumaMonitorSelect`). Visual cobalt HUD, **não** o System Report navy
  revertido em 2026-09-19. Reusar a tag `v4.5` no Hub exigiu um pull
  `Always` — `IfNotPresent` tinha ficado com o digest navy antigo. Ver
  seção própria;
  v4.6 = **tiles numa linha, swap em GB, CPU em uso, Serviços Host** —
  `.tiles` nowrap no desktop (host e detalhe VM/CT); tile de memória com
  swap em GB; alarme `*_bytes` sem `%`; Uso de CPU lê `proxmox.loadavg` e
  alocada vs em uso (`cpu_pct × vCPUs`); Hardware com Serviços Host ao lado
  dos PVE; swap de guest via `swap`/`maxswap` (VM sem dado = `—`).
  v4.7/v4.8 = boot pool TrueNAS (`truenas.boot_pool_healthy`), na branch
  `tiberius/truenas-boot-pool-v4.8` — `main` ficou em v4.6;
  v4.9 = **tiles de entidade centrados** + hover com o texto inteiro só
  quando não cabe (`OverflowTip`). Imagem `sha256:bfb394ba6e74…`, commit
  `db68051`, na mesma branch (não em `main`). Pod `horus-77f5f86c59-r4jfs`.
  Próxima = v4.10.
- **Ingress** (`deploy/app/03-ingress.yaml`) tem `proxy-body-size: 16m` — necessário
  pro `PUT /me/prefs` (blob de prefs com ícones base64); sem isso, 413.
- **Pod não-root** (v3.28+): Dockerfile `USER 1000`; Deployment `runAsNonRoot` /
  `fsGroup: 1000` / drop ALL. Volume NFS de ícones precisa ser gravável por uid 1000.
- **Conectividade:** UK/Docker/k8s/TrueNAS **levantam** se a chamada essencial
  falhar. `for_seconds<=0` fire no mesmo ciclo. Host Docker/k8s entra no
  `resource_pct` via prefixo `docker.`/`k8s.`.
- **SSE:** `POST /api/events/ticket` + `EventSource?ticket=` — token de sessão
  fora da query.
- **Docker host CPU:** sample `docker.cpu_pct` = soma dos containers ÷ `NCPU`
  (~0–100%). Containers individuais mantêm a escala Docker.
- **Tiles vs gráfico:** tile = último poll; “atual” do gráfico = último bucket
  do dia — lag esperado (wiki `horus-observabilidade`).
- **Bootstrap:** Secret com `horus_`+`token_urlsafe(32)`; restart não troca o
  hash se a tabela `tokens` já tem `bootstrap`. Rotacionado 2026-09-03.
- **Docker 2375:** VM 101 (`192.168.1.40`) — nftables só `127.0.0.1` + k3s
  `192.168.1.241`. Build de imagem no PCL: rsync + `docker build --network=host`
  via SSH em `kiwel@192.168.1.40` (TCP 2375 fechado do PCL).
- **CrowdSec:** `horus.kiwel.uk` = `35-Horus-service` no Pangolin/Traefik.
- **Aplicar no k3s**: `KUBECONFIG=/home/kiwel/.kube/kartrack.yaml kubectl apply
  -f deploy/app/` + `kubectl rollout status deployment/horus -n horus`. Sem esse
  kubeconfig o kubectl cai em `localhost:8080`. Detalhes em `deploy/00-install.md`.
- **`HORUS_SECRET_KEY`** precisa estar no Secret (`deploy/app/01-secret.yaml`,
  gitignored) antes de usar a aba Configurações; gere com
  `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
- **Atalho `drakaris`**: bump da tag (`v4.9` → `v4.10` salvo pin), build/push
  Hub, apply, commit+push nos dois remotes — sem perguntar. Atalhos antigos
  `deploy` / `deploy:` **não** disparam.

## Responsividade / mobile (estado atual)

- **Breakpoint único**: `@media (max-width: 820px)` no fim do `styles.css`.
- **Sidebar vira drawer off-canvas**: state `navOpen` no `App`, classe `.sidebar.open`,
  hambúrguer `.nav-burger` no `.appbar` (display:none no desktop), backdrop `.nav-backdrop`
  fecha ao tocar; `switchInteg` e abrir alarmes fecham o drawer.
- **Fixes globais**: `.app` com `height: 100dvh` (fallback 100vh), `touch-action: manipulation`
  em botões/links/nav, sidebar com `overflow-y: auto`.
- **No bloco mobile**: main com padding 14px + safe-area, entity-name 26px, tabs com scroll
  horizontal próprio, modais 94vw/86dvh, toasts em largura total, `input/select/textarea`
  com fonte 16px (evita zoom automático do iOS no foco).
- Grades de cards já colapsam sozinhas (auto-fill/minmax); `Chart` (uPlot) se redimensiona
  no resize da janela.

## Convenções de código (não negociáveis, vistas em todo o histórico)

- **Comentário só explica o "porquê" não-óbvio**, e em **PT-BR** — nunca o
  "o quê" (nome de variável já faz isso). Ex. real do código:
  `// % de pacotes perdidos/com erro: precisão maior que pctFmt p/ não
  arredondar tudo p/ "0.0%"`. Não adicione comentário explicando o que uma
  linha óbvia faz.
- **Não crie abstração que ninguém pediu.** Se 2-3 lugares repetem um
  padrão pequeno (uma linha de `<div className="kv">`), deixe repetido — só
  vira componente/helper quando o padrão é usado de fato em 3+ lugares E tem
  alguma lógica não-trivial (ver `TitledCard`, criado só quando 5 cards
  precisaram do mesmo tratamento de título-fora-da-caixa).
- **Mudança pedida para UM lugar não deve vazar para outro.** Quando um
  componente compartilhado (`InfoCard`) é usado por várias abas e só uma
  precisa mudar de comportamento visual, crie uma variante nova
  (`TitledCard`) em vez de alterar o componente compartilhado — evita
  quebrar abas que não foram pedidas na tarefa atual.
- **Sem TypeScript, sem testes de frontend.** Não proponha adicionar — não
  é o padrão do projeto e não foi pedido.
- **Backend tem teste só onde vale a pena**: funções puras (parsers SSH,
  SMART, auth/scopes). Não há teste de rota HTTP nem de integração com DB —
  não introduza isso a menos que pedido.
- **Toda a UI é em português (pt-BR)** — labels, mensagens de erro
  (`alert("Falha: " + e)`), nomes de abas. Não traduza nada para inglês.
- **Service age**: este é um projeto solo, sem CI configurado. "Funciona e
  o build passa" é a barra; não inflar com processo (PRs, branches de
  feature, hooks extras) que o usuário não pediu — ele decidiu trabalhar
  direto na `main` (ver `prompt`, linha 40).
