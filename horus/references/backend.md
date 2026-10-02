# Backend — referência completa

FastAPI async + SQLAlchemy 2.0 async + PostgreSQL/TimescaleDB. Python ≥3.12.
Sem requirements.txt — tudo em `backend/pyproject.toml`, instalado com
`pip install -e '.[dev]'`.

## Arranque (`horus/main.py`)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()                    # cria schema + hypertable Timescale
    await ensure_bootstrap_token()      # token admin via HORUS_BOOTSTRAP_TOKEN (1x)
    await ensure_bootstrap_user()       # user admin via HORUS_BOOTSTRAP_USER/PASSWORD (1x)
    await ensure_defaults()             # regra de alarme + thresholds default
    poller.setup()                      # instancia integrações configuradas
    await poller.start()
    yield
    await poller.stop()
```

`GET /health` retorna `{"status": "ok", "integrations": [...]}`. CORS aberto
(`allow_origins=["*"]`) — ambiente de lab, não endurecer sem pedido explícito.

## Banco de dados (`horus/db.py`)

- `AsyncEngine` (`create_async_engine`, `pool_pre_ping=True`) +
  `async_sessionmaker(expire_on_commit=False)`.
- **TimescaleDB**: tabela `samples` é hypertable (`create_hypertable(...,
  if_not_exists=>TRUE)`); continuous aggregate `samples_5m` (bucket de 5min,
  avg/max/min/last) sem expiração; **retenção de 7 dias** nos dados brutos —
  é o "downsample após 1 dia" mencionado no README.
- Migrações são **idempotentes inline** em `init_db()` (sem Alembic) — ex.:
  adicionar coluna de threshold por recurso, coluna de preferências, coluna
  `net_speed_overrides`. Ao adicionar uma coluna nova, siga esse padrão
  (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...` dentro de `init_db()`), não
  introduza Alembic sem que o usuário peça.

## Modelos (`horus/models.py`)

SQLAlchemy 2.0 declarativo, `Mapped[]` + `mapped_column()`. Tabelas:

| Tabela | Chave | Campos notáveis |
|---|---|---|
| `Entity` | `id` (str hierárquico, ex. `proxmox/pve1/qemu/101`) | `attributes` (JSONB, dados específicos da integração), `threshold_cpu/mem/disk` (override por entidade, `None` = herda global), `icon`, `service_url`, `kuma_monitor_id` (monitor UK vinculado; mostra saúde no card), `net_speed_overrides` (JSONB `{iface: mbps}`) |
| `Sample` | composta `(ts, entity_id, metric)` | hypertable; `value`, `unit`, `labels` (JSONB) |
| `AlarmRule` | `id` | `metric`, `operator`, `threshold`, `for_seconds`, `severity`, `enabled` |
| `AlarmState` | composta `(rule_id, entity_id)` | state machine `ok\|pending\|firing` |
| `AlarmEvent` | `id` autoincrement | histórico; `resource` (label legível, ex. "Uso de CPU"), `status`, `acknowledged` |
| `Setting` | `key` (str) | `value` JSONB — thresholds globais, `alarms_muted`, e **config de conexões** (`conn:{integração}` → `{campo: valor}`, secrets cifrados) |
| `User` | `id`/`username` único | `password_hash` (PBKDF2), `scopes` (JSONB list), `preferences` (JSONB) |
| `Token` | `id` | `token_hash` (SHA-256), `scopes` (lista persistida), `preferences` (JSONB — Home do agente) |
| `AuditLog` | `id` | toda ação de escrita via API, com `verb`/`params`/`result` |

## Padrão de plugin de integração (`horus/integrations/base.py`)

Contrato que **toda integração nova** (TrueNAS, Docker, k8s) implementa:

```python
class Integration(ABC):
    name: str  # único, ex. "proxmox"

    @abstractmethod
    async def discover(self) -> list[DiscoveredEntity]: ...   # inventário (read-only)
    @abstractmethod
    async def collect(self) -> list[Sample]: ...               # métricas do ciclo (read-only)
    def actions(self) -> list[ActionSpec]: return []            # verbos suportados (opcional)
    async def execute(self, entity_id: str, verb: str, params: dict) -> dict: ...  # ação de escrita
    async def aclose(self) -> None: ...                         # cleanup (opcional)
    @staticmethod
    async def test_connection(cfg: dict) -> None: ...           # testa conexão (aba Config); default levanta
```

```python
@dataclass
class DiscoveredEntity:
    id: str; type: EntityType; name: str; status: Status
    parent_id: str | None = None
    attributes: dict = field(default_factory=dict)

@dataclass
class Sample:
    entity_id: str; metric: str; value: float
    unit: str = ""; labels: dict = field(default_factory=dict)
```

**Registro**: `@register` (decorator) + `load_integrations()` em
`core/registry.py` faz scan de módulos em `horus/integrations/*` no boot —
uma integração nova é só um arquivo novo nessa pasta com a classe decorada,
**sem tocar no core**.

**Ciclo do poller** (`core/poller.py`), uma vez por integração por ciclo:

```python
entities = await inst.discover()
samples = await inst.collect()
async with SessionLocal() as session:
    await self._persist(session, name, entities, samples)   # upsert (ON CONFLICT DO UPDATE)
    await alarms.evaluate(session, name, entities, samples)
await bus.publish({"type": "update", "integration": name, "entities": len(entities)})
```

Erro em uma integração não derruba o ciclo das outras (`try/except` por
integração, log + `continue`).

`_persist()` também **deleta entidades que sumiram do discover** (pod removido
num scale-down, VM deletada) — senão viram fantasma na UI. Guarda: se o discover
veio **vazio** (soluço da API), não apaga nada, pra não perder ícones/limites
configurados de todas as entidades da integração.

## Vocabulário canônico (`horus/core/canonical.py`)

```python
class CanonicalMetric(str, Enum):
    cpu_pct = "cpu_pct"; mem_used_bytes = "mem_used_bytes"; mem_total_bytes = "mem_total_bytes"
    disk_used_bytes = "disk_used_bytes"; disk_total_bytes = "disk_total_bytes"
    net_rx_bytes = "net_rx_bytes"; net_tx_bytes = "net_tx_bytes"
    disk_read_bytes = "disk_read_bytes"; disk_write_bytes = "disk_write_bytes"
    uptime_seconds = "uptime_seconds"
```

Métrica que **não** é universal entre integrações usa namespace:
`proxmox.io_delay_pct`, `truenas.smart_temp_c` — o frontend ignora o que não
reconhece, e os gráficos/tiles genéricos (Overview) só usam as canônicas. Ao
adicionar uma métrica nova específica de uma integração, **sempre namespace**
(`<integração>.<nome>`) — nunca solte um nome novo direto no vocabulário
canônico sem que ele faça sentido pra qualquer integração futura.

`EntityType`: `vm | ct | host | pool | disk | container | pod | node | deployment | monitor | ups | filesystem`.
(`filesystem` = ponto de montagem do host Proxmox via `df`, entidade `proxmox/{node}/fs/{slug}`,
emite `disk_used/total_bytes` → alertável por `resource_pct`; desde v3.11.)
`Status`: `running | stopped | paused | degraded | error | unknown`.

## Testes (`backend/tests/`)

`pytest` + `pytest-asyncio`. Foco em **funções puras**. Arquivos de teste ativos:

| Arquivo | O que testa |
|---|---|
| `test_core.py` | registro de integrações, vocabulário canônico |
| `test_node_ssh.py` | parsers SSH: netcfg, nicsys, ups, lscpu, board, bios, RAM, disk links |
| `test_proxmox_smart.py` | `_smart_num`, `_parse_smart_text`, `_disk_link_info` |
| `test_proxmox_resources.py` | `_disk_spec`, `_guest_resources`, `_vm_nic` (model), `_parse_backup_vmtype/vmid` |

Total: 42 testes (Junho 2026). Ao adicionar parser puro novo em proxmox.py, adicione caso em `test_proxmox_resources.py`.

## Integração de referência: Proxmox (`integrations/proxmox.py`)

- IDs: host `proxmox/<node>`, VM `proxmox/<node>/qemu/<vmid>`, LXC
  `proxmox/<node>/lxc/<ctid>`.
- **Privilege separation**: token de leitura (`PROXMOX_TOKEN_ID/SECRET`) pra
  `discover()`/`collect()`; token de controle separado, opcional
  (`PROXMOX_CONTROL_TOKEN_ID/SECRET`) pra `execute()` — sem ele, a integração
  fica read-only.
- Cache de inventário com TTL (`PROXMOX_INVENTORY_TTL`, default 300s) — a API
  do Proxmox é cara pra chamar todo ciclo de 15s.
- **RAM de guest vem de `_guest_mem()`, não da lista por nó** (v3.18). O
  `/nodes/{node}/qemu` devolve `memhost` no campo `mem`; só o
  `/cluster/resources?type=vm` traz o valor do balloon. O mapa é keyed por
  `{kind}/{vmid}` (formato do campo `id` de lá) e o `collect()` usa
  `guest_mem.get(chave, g.get("mem", 0))` — o valor da lista fica de fallback.
  Contexto completo e a pegadinha de por que isso é invisível sem balloon: seção
  "RAM de guest do Proxmox" no `SKILL.md`.

### Inventário de guests (VM/LXC)

`_inventory()` chama `_guest_inventory(node, kind, vmid, running)` por guest:

```python
inv[eid] = await self._guest_inventory(name, kind, g["vmid"], running)
# retorna {"net": [...], "resources": {...}}
```

**`_guest_inventory`** busca `/nodes/{node}/{kind}/{vmid}/config` UMA vez e deriva:
- `"net"`: lista de NICs com `{iface, mac, bridge, tag, ip, model, type, active, _hostif}`.
  `_vm_nic` inclui `"model"` (chave PVE: "virtio"/"e1000"/etc.). Para VM rodando, chama
  `_vm_agent_ips()` que retorna `(ips: dict, ok: bool)` — `ok=True` se o agente respondeu,
  usado para preencher `agent_active` nos recursos.
- `"resources"`: resultado de `_guest_resources(kind, cfg, agent_active)` (função pura,
  testável). Para qemu: sockets/cores/vcpus/cpu_type/numa/memory_mb/agent_enabled/agent_active/
  bios/machine/ostype/scsihw/disks. Para lxc: cores/memory_mb/swap_mb/ostype/arch/unprivileged/disks.

**`_disk_spec(spec)`** — parser de spec de disco (`"storage:volume,size=32G,mp=/data"`):
```python
{"storage": "local-lvm", "volume": "vm-100-disk-0", "size": "32G", "mountpoint": ""}
```
Filtra `media=cdrom` (drives CD-ROM vazios) antes de passar por `_guest_resources`.

**Regexes auxiliares:**
- `_QEMU_DISK_RE = re.compile(r"^(ide|sata|scsi|virtio)\d+$")` — slots de disco de VM
- `_LXC_MOUNT_RE = re.compile(r"^mp\d+$")` — pontos de montagem extras de CT
- `_UPID_RE` — parse de UPID embutido no `msg` de entradas TASK no cluster log
- `_BACKUP_CT_RE` / `_BACKUP_VMID_RE` — determina vm vs ct e vmid a partir do volid

### Logs e backups

**`get_cluster_log`** — usa `/cluster/log?max=500`, filtra por período no cliente.
Entradas com `tag="TASK"` têm um UPID embutido no `msg` — parseado via `_UPID_RE`
para enriquecer com: `type` (qmstart/vzdump/etc.), `vmid`, `user`, `upid`, `duration`
(endtime−starttime_do_UPID), `status` ("OK"/"ERRO..."). Entradas sem UPID têm
esses campos como strings vazias / `None`.

**`get_backups`** — usa `/nodes/{node}/storage/{s}/content?content=backup` em cada
storage com `content` incluindo `"backup"` (não tasks/vzdump). Retorna:
```python
{
  "total": int,
  "ok": int,                  # len(items) — arquivo presente = sucesso
  "failed": 0,
  "storages_info": [           # uso REAL do disco de backup (não soma de arquivos)
    {"name": "Bkp1tb", "type": "dir", "used": 523*GB, "total": 1*TB, "avail": ..., "pct": 52.3}
  ],
  "items": [
    {"volid": "...", "storage": "Bkp1tb", "storage_type": "dir",
     "size": 2.3*GB, "ctime": 1234567890, "vmid": "112", "vmtype": "ct"}
  ]
}
```
`storage_type="pbs"` → frontend mostra pill "PBS" (accent); outros → pill "Local" (muted).
`storages_info` alimenta um `StatTile` por storage na aba Logs (label = nome do storage, valor = usado/total).

- **SSH como complemento, nunca obrigatório** (`integrations/node_ssh.py`):
  coleta o que a API do PVE não expõe (sensores, UPS via NUT, velocidade real
  de interface via sysfs, PCI/USB, LVM, mounts, DNS, `lscpu -J`/`dmidecode`
  p/ CPU flags+L3/motherboard/BIOS/RAM, `smartctl -i`/sysfs PCIe p/ versão
  SATA e link speed NVMe). Um script remoto único por ciclo, parseado depois.
  **Resiliente por design**: sem `asyncssh` instalado, sem host ou sem
  credencial → `gather()` devolve `{}` e o ciclo segue normal.

## Alarmes (`core/alarms.py`)

State machine por par `(rule, entity)`: `ok → pending → firing → resolved → ok`.
`pending → firing` exige a condição sustentada por `rule.for_seconds`
(evita flapping). Notificação (Gotify) só nas **transições** (firing/resolved),
nunca em estado sustentado — não notifique a cada ciclo.

Regra especial `resource_pct`: dinâmica, dispara quando CPU%, mem% **ou**
disco% passam do limite — usa o limite por-entidade se setado
(`Entity.threshold_cpu` etc., `None` = herda `Setting[threshold_cpu]` global).

## Auth (`core/auth.py`)

- Token: `"horus_" + secrets.token_urlsafe(32)`; só o hash SHA-256 fica no
  banco.
- Senha: PBKDF2-SHA256, 200k iterações, formato `pbkdf2$iter$salt$digest`.
- Escopos: `"read"` | `"control:<integração>"` | `"control:*"` | `"admin"`.
  `admin` permite tudo; `control:*` permite qualquer `control:X`; ter
  qualquer escopo de controle já implica `read`.
- Login emite **1 token por usuário** (login novo revoga o anterior).

## Rotas (`api/routes.py`, tudo sob `/api`)

Auth via `Depends(require(scope))` (factory em `api/deps.py`, lê header
`Authorization: Bearer <token>`). Grupos principais:

- **Inventário/métricas**: `GET /entities`, `GET /entities/{id}/metrics/{metric}`
  (ranges `day|week|month|year`, resample automático), `GET /latest`,
  `GET /entities/{id}/latest`.
- **Alarmes**: `GET /alarms/active`, `GET /alarms/history`,
  `POST /alarms/{id}/ack`, `DELETE /alarms/{id}` (eventos); regras =
  `GET/POST /alarms/rules`, `PUT/DELETE /alarms/rules/{id}` (admin; PUT/DELETE
  com guarda `SPECIAL_ALARM_METRICS` — não deixa mexer na condição/escopo nem
  excluir as regras `resource_pct`/`connectivity`). `AlarmRule.entity_id`
  (nullable) mira uma entidade só; `GET/PUT /settings` = limites globais.
- **Controle** (Proxmox): `POST /entities/{id}/actions` (`{verb, params}`,
  exige `control:<integração>`, sempre logado em `AuditLog`), além de
  `/logs` (agora inclui fonte `kernel` = `journalctl -k`; `limit` até 500),
  `/boots` (histórico de boots com `gap_seconds`, desde v3.11), `/backups`,
  `/notifications`, `/tasks/{upid}/log` (download **e** exibição inline via `api.taskLog`).
- **Diag / health check** (v3.15, contrato v2 na v3.16; ver seção Diag no SKILL.md):
  `GET /entities/{id}/health` (read) → `{result, disabled, thresholds, excluded_guests, running}` ·
  `POST /entities/{id}/health/run` (admin, síncrono ~10-60s) ·
  `PUT /entities/{id}/health/config` (admin, `{disabled?: [...], threshold?:
  {key, warn, crit}, excluded_guests?: ["qemu/N","lxc/N"]}` — desativar categoria
  resolve os alarmes abertos dela via `alarms.resolve_health_category`;
  `excluded_guests` (v3.26) é lista de exclusão de VMs/CTs (disco + onboot;
  vazia = todas; ao acrescentar um ID resolve `storage:guest:*` e `vms:N` via
  `alarms.resolve_health_resources`); `threshold` mescla o override da classe em
  `settings["health:proxmox:thresholds"]`, 400 se key fora de `THRESHOLDS`).
  Implementação em `integrations/proxmox_health.py`; resultado (só o último) em
  JSONB na tabela `settings` (`health:proxmox` / `:disabled` / `:thresholds` /
  `:excluded_guests`).
  11 categorias desde a v3.19 (`gpu` entrou entre `memory` e `storage`) — a lista
  é `CATEGORIES` no backend e `DIAG_CATEGORIES` no `App.jsx`, e as duas precisam
  bater; `check_gpu` funde `lspci` (inventário, pega placa em passthrough),
  `/sys/bus/pci/devices` (métricas de quem tem driver) e `nvidia-smi` por
  endereço PCI.
- **Ícones**: `GET /icons`, `GET /icons/{slug}.svg`, `GET /icons/upload/{name}`,
  `POST /entities/{id}/icon/upload` (multipart, admin).
- **Renomear/ícone da entidade** (admin): `PATCH /entities/{id}/icon` (`Entity.icon`),
  `PATCH /entities/{id}/name` (`Entity.display_name`, vazio→NULL). Ambas as colunas são
  **preservadas no discover** (fora do `set_` do upsert em `poller._persist`).
- **Auth/usuário**: `POST /login`, `GET /me`, `POST /me/password`
  (só sessão `user:…`), `GET|PUT /me/prefs` (preferências persistidas —
  nunca no frontend). Sessão de login usa `users.preferences`. Token de API:
  GET lê `tokens.preferences` se não-vazio, senão a Home do 1º `User` (semente);
  PUT grava no próprio token. `authenticate()` une os escopos do 1º usuário
  aos do token (só em memória). `GET /me` devolve `has_password` (true só em
  `user:…`) e `username` do dono da instância para o agente. `prefs_owner()`
  em `core/auth.py`.
- **Admin**: `/users` (CRUD), `/tokens` (criar — token aparece **uma vez só**
  na resposta).
- **Thresholds**: `GET|PUT /settings` (global), `PATCH /entities/{id}/threshold`
  (por entidade), `PATCH /entities/{id}/net/{iface}/speed` (override manual
  de velocidade de interface virtual).
- **SSE**: `POST /events/ticket` (Bearer, ticket ~60s um uso) →
  `GET /events?ticket=...`. O token de sessão **não** vai na query (cai em
  access log do ingress).
- **Login**: `POST /login` tem janela de 5 falhas / 5 min por IP (429).

Rota nova: siga o padrão de prefixo `/api`, dependency `require(<scope>)`
explícita, e se for ação de escrita, registre em `AuditLog`.

## Configuração (`horus/config.py`)

`pydantic-settings`, lê `.env`. Convenção de nome: `<INTEGRAÇÃO>_<CAMPO>`
(`PROXMOX_URL`, `PROXMOX_TOKEN_ID`, `PROXMOX_SSH_HOST`, `NUT_UPS`). Ver
`.env.example` na raiz pro catálogo completo. Variável ausente/vazia em
recurso opcional (SSH, Gotify, controle) deve **desabilitar a feature
silenciosamente**, nunca lançar erro no boot — é o padrão estabelecido
(`ssh_enabled()`, checagem de token de controle, etc.).

`HORUS_SECRET_KEY` (Fernet, base64 32 bytes) alimenta a config no banco (abaixo).
O `settings` é **mutado em runtime** por `appconfig.hydrate()` (boot) e por
`appconfig.save()` — não é mais só leitura do `.env`.

## Config de conexões no banco (jul/2026)

Conexões das integrações editáveis pela UI e persistidas no banco; o `.env`/
Secret só semeia no 1º boot. Módulos:

- **`core/config_schema.py`** — `SCHEMA`: fonte única (integração → campos
  `{name, label, type, secret, required}`). Nomes = atributos de `config.py`.
- **`core/secrets.py`** — cofre baseado em `HORUS_SECRET_KEY`; sem a chave, os
  campos marcados como sensíveis não são persistidos (`SecretKeyMissing`).
- **`core/appconfig.py`** — `hydrate()` (semeia + sobrepõe no `settings`),
  `get_all()` (mascara os campos sensíveis na resposta), `save()` (persiste +
  atualiza `settings` + `poller.request_reload`), `resolve_stored()` (pro teste).
  Transformações puras testadas em `tests/`.
- **Reload ao vivo**: `poller.request_reload(nome)` → `_drain_reloads()` no topo
  de cada ciclo re-instancia só aquela integração (fecha o client antigo). As
  integrações seguem lendo `settings.*` no `__init__`.
- **Teste de conexão**: `Integration.test_connection(cfg)` staticmethod (default
  levanta; cada integração faz uma chamada barata). Gotify → `notify.test_connection`.
- **Rotas** (admin): `GET/PUT /config`, `POST /config/{integ}/test`.
- Coluna nova (ex.: `kuma_monitor_id`) entra em `db.py::_MIGRATIONS` como
  `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (idempotente).

## Ícones (`core/icons.py`)

Backend faz **proxy com cache em disco** do CDN dashboardicons.com
(`/data/icons/svg/`), nunca o frontend busca direto — índice revalidado a
cada 24h, com fallback pro cache velho se o CDN cair. Upload de usuário fica
em `/data/icons/uploads/`, referenciado na entidade como `upload:<nome>`.


## Deploy

`docker-compose.yml` na raiz: `db` (TimescaleDB 2.17/PG16, healthcheck
`pg_isready`) → `backend` (porta 8420, espera `db` saudável) → `frontend`
(porta 8421, Nginx servindo o build do Vite com fallback de SPA). Backend
Dockerfile: `python:3.12-slim`, `pip install .` a partir do `pyproject.toml`
local (sem requirements.txt separado). Dep de runtime `cryptography` (config no
banco). Em produção (k3s) `HORUS_SECRET_KEY` vai no Secret; imagem
`kiwel/horus:vX.Y` no Docker Hub, versão referenciada em `deploy/app/02-app.yaml`.
