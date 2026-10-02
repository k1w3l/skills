# Frontend — referência completa

`frontend/src/App.jsx` (~3700 linhas) é o app inteiro: sem React Router, sem
biblioteca de componentes (só ícones `lucide-react`). Tudo roda em
`useState`/`useEffect`/`useCallback` no componente `App` raiz. Antes de criar
um componente/hook/helper novo, procure neste arquivo — quase certamente já
existe algo parecido.

## Navegação (sem router)

Três variáveis de estado decidem o que renderiza:

- `integ` (string) — integração ativa (ex.: `"proxmox"`). Lista vem de
  `[...new Set(entities.map(e => e.integration))]`.
- `sel` (objeto entidade ou `null`) — `null` = home da integração (grade de
  VMs/LXCs); objeto = página de detalhe da entidade.
- `hostTab` (string) — `"overview" | "storage" | "network" | "hardware" | "logs"`,
  reseta para `"overview"` sempre que `integ` muda.

Não introduza `react-router` ou qualquer lib de rotas — não é o padrão e
quebraria a navegação por estado já existente.

## Estado central do `App` (linhas ~1656-1677)

```javascript
const [entities, setEntities] = useState([]);        // todas as entidades (host+VMs+LXCs, todas integ.)
const [alarms, setAlarms] = useState([]);             // alarmes ativos (banner no topo)
const [panels, setPanels] = useState([]);             // painéis de métrica calculados p/ a entidade em foco
const [latestMap, setLatestMap] = useState({});       // snapshot p/ a grade de VMs/LXCs (home)
const [settings, setSettings] = useState({...});      // thresholds globais (cpu/mem/disk)
const [prefs, setPrefs] = useState({});                // preferências por usuário, persistidas no backend
const [iconSet, setIconSet] = useState(null);          // Set de slugs de ícone disponíveis (cache)
```

### Polling (sem WebSocket; SSE só pra alarmes/refresh, não pra métricas)

Dois loops de `setInterval` de 15s, cada um com flag `alive` no cleanup pra
não fazer `setState` depois de desmontar:

```javascript
useEffect(() => {
  if (!focus) { setPanels([]); setUptime(null); return; }
  let alive = true;
  loadPanels(focus, range, diskPref).finally(() => alive && setLoading(false));
  const t = setInterval(() => loadPanels(focus, range, diskPref), 15000);
  return () => { alive = false; clearInterval(t); };
}, [focus?.id, range, loadPanels, prefs.disk]);
```

Esse padrão (`alive` flag + `setInterval`/`clearInterval` no cleanup) é o
padrão do projeto pra qualquer polling — reuse-o ao adicionar uma nova fonte
de dados que precise atualizar periodicamente, não invente outro mecanismo.

Além disso, `subscribe(onEvent)` (SSE, `lib/api.js`) é usado só pra disparar
um `refresh()` (re-busca `entities`+`alarms`) quando o poller do backend
publica um evento — não carrega métricas, é só um gatilho de invalidação.

### Sistema de toast e confirm dialog

O projeto usa um sistema de toast próprio (sem lib externa) com
`ToastContainer` + `ConfirmModal`, ambos em `App.jsx`.

```javascript
// toast global — disponível em qualquer escopo do módulo
toast("mensagem");              // info
toast.ok("mensagem");           // success (verde)
toast.err("mensagem");          // error (vermelho)
toast.warn("mensagem");         // warning (amarelo)

// confirm dialog (retorna Promise<boolean>)
const ok = await confirmDialog("Deseja continuar?");
if (!ok) return;
```

`ToastContainer` usa `createPortal` para `document.body` (mesmo padrão dos
modais — evita deslocamento por transform de ancestral). Toasts aparecem no
**canto superior direito**, auto-dismiss em 4s. Internamente `_toastFn` é um
módulo-level ref que `ToastContainer` popula no mount — isso permite que
funções fora da árvore React (ex.: handlers de ação) usem `toast()` diretamente.

`ConfirmModal` é baseado em Promise: `confirmDialog(msg)` seta um estado
`_confirmFn` que renderiza o modal e resolve a promise no clique de OK/Cancelar.

**Use `toast.err()` para erros de UX** em vez de `alert()`. `401` continua
virando `setAuthed(false)` (relogin), nunca toast.

### Modais de edição inline

| Modal | Props | Uso |
|---|---|---|
| `EntityEditModal` | `entity, iconSet, monitors?, onClose, onSaved` | Renomear, ícone e monitor UK (glyph no card). URL de serviço **não** — só atalhos da Home. |
| `IfaceSpeedModal` | `nic, onClose, onSave` | Editar velocidade (Mb/s) de interface de rede. Validação > 0, "Remover" zera. |

Ambos usam `Modal` (via `createPortal`) e são disparados por botões inline
(`Link2` e `Settings` respectivamente).

## Cliente API (`lib/api.js`)

- Token: `localStorage["horus_token"]`, helpers `getToken()`/`setToken()`.
- `req()` central — todo método de `api` passa por ele; erro lançado tem
  `.status` (HTTP) e `.message`. 204 vira `null`.
- Convenção de nomes: `api.entities()`, `api.metric(id, metric, range)`,
  `api.latest(id)`, `api.action(id, verb, params)`, `api.setEntityIcon(id, icon)`,
  `api.setEntityLink(id, url)`, `api.setIfaceSpeed(id, iface, mbps)`,
  `api.getPrefs()`/`api.putPrefs(prefs)`, `api.settings()`/`api.putSettings(thr)`.
- Upload de arquivo: `FormData`, **sem** header `Content-Type` manual (deixa
  o browser setar o boundary) — ver `api.uploadEntityIcon(id, file)`.
- `subscribe(onEvent)` pede `POST /api/events/ticket` e abre `EventSource` só
  com o ticket (SSE não manda Authorization). Token de sessão não vai na query.

Ao adicionar uma rota nova no backend, adicione o método correspondente em
`api.js` seguindo esse mesmo padrão de nomes (verbo+substantivo, sem prefixo
redundante) — não crie um cliente HTTP paralelo.

## Catálogo de componentes compartilhados

Tabela de qual usar pra cada situação nova. Todos vivem em `App.jsx`.

| Componente | Usa quando | Notas |
|---|---|---|
| `StatTile` | Métrica avulsa no topo de uma aba (`.tiles`) | `value` pode ser string OU JSX (ver `tile-iface` no CSS p/ layout de 2 linhas dentro do tile) |
| `TitledCard` | **Qualquer** card novo com título — é o padrão único hoje | Título **fora** da caixa, ritmo de `.section-title`. Usado em Rede/Armazenamento/Hardware. Estica (`flex:1`) e centraliza conteúdo verticalmente se o card vizinho for mais alto — ver `references/css-layout.md`. (`InfoCard`, com título *dentro* da caixa, existiu até jun/2026 mas foi removido por falta de uso — não recrie esse padrão sem necessidade real.) |
| `NicCard` | Qualquer interface de rede clicável (física, virtual, de VM/LXC) | Abre `NicModal` no click; reusado em 3 lugares (host, `net-cols`, `net-machines`, `GuestInfoCard`). `NicModal` mostra `Controlador` condicionalmente se `nic.model` presente (VMs têm; físicas/LXC não têm). |
| `MachineCard` | Tile de VM/LXC na grade da Overview (`.machines`) | 3 linhas de `.m-stat`: CPU (azul) · Mem (roxo) · Disco (rosa `#f778ba`). `disk` incluído no cálculo de `over` (alerta vermelho). Rodapé: IP à esq + `m-actions` à dir (RotateCw, Power/danger). **Sem** botões de link — URLs só nos atalhos da Home. |
| `DockerContainerCard` | Tile de container Docker (mesmo grid `.machines`) | 2 linhas de `.m-stat`: CPU + Mem (sem disco). Rodapé `.m-foot`: portas publicadas no host (`.ct-ports` / `.ct-port`, só `PublicPort`) + `m-actions` (Play, Pause, RotateCw, Square/danger). **Sem** botão de link — URLs só nos atalhos da Home. Square (parar) é o último — à direita, com `danger` = hover vermelho. Sem `runAction`/confirm — usa `runContainerAction` diretamente. |
| `DockerOverviewContent` | Aba Overview do host Docker | Tiles de métricas + gráficos + grade de `DockerContainerCard`. Recebe `onAction={runContainerAction}`. |
| `GuestInfoCard` | Card de informações completas de VM/LXC (abaixo dos gráficos no detalhe) | Renderiza com `TitledCard` + `className="block-gap"`. VM: vCPU/RAM/CPU/NUMA/agente/BIOS/máquina/scsihw. LXC: núcleos/RAM/swap/ostype/arch/unprivileged. Discos via `DeviceTile` em `.dev-tile-grid`. Rede via `NicCard`/`NicModal` com estado `modalNic` local. Retorna `null` se `entity.attributes.resources` vazio. |
| `LogTile` | Tile clicável de log do sistema na aba Logs | `.log-tile` card: head com `hbadge` tipo + `dev-tile-badge` origem + timestamp (right). Body clamped 3 linhas (`-webkit-line-clamp:3`). Cor de borda esquerda via `.log-tile-bad`/`.log-tile-warn`. |
| `LogModal` | Modal de detalhe de log | Linha msg + pill OK/ERRO (`log-modal-msg`). kv-grid: Tipo, Nó, Usuário, VM/CT ID, Duração, Data. UPID em mono break-all no rodapé. |
| `BackupTile` | Tile clicável de backup na aba Logs | Head: `type-pill vm/ct` + `dev-tile-badge accent` "PBS" ou `dev-tile-badge` "Local" + `hbadge ok` tamanho (sempre verde). Body flex-column: storage name / data+hora. |
| `BackupModal` | Modal de detalhe de backup | Pills row + kv-grid (Storage, Tamanho, Data, VM/CT ID) + Volume ID em mono break-all. |
| `DiagModal` | Modal "Diagnóstico do Sistema" (tile "Diag" da Overview Proxmox; v3.15, v2 na v3.16, info+guests na v3.17) | Cabeçalho-resumo (`diagSummary`: contadores grandes `.diag-count` críticos/atenção/**info azul**/OK + lista de falhas clicável ordenada que expande/rola até a categoria), 10 categorias colapsáveis, `DiagItemRow` (valor — limite — pill Normal/Info/Atenção/Crítico + mensagem + detail de journal em mono), toggle por categoria e lápis de limites (`DiagThrEdit` inline, admin) e "Executar agora". Status `info` = informativo (updates/reboot), azul via `.hbadge.info`/`.diag-dot.info`, não alarma. Estado `health` vive no `OverviewTabContent`; `diagTile(health)` agrega em valor+cor pro tile. CSS `.diag-*`. |
| Banner de alarmes agrupado | Topo do `.main` (desde v3.17) | Com >1 alarme ativo, renderiza só o primeiro + botão `.alarm-more` com `+N`; clique expande todos (`ChevronUp` recolhe). State `alarmsExpanded` no `App`. Fallback de mensagem: `a.message` → "Conexão" → template resource/threshold. |
| `DiskTile` | Tile de disco físico clicável (`.disk-tile-grid`) | Abre `DiskSmartModal`. Tem 3ª linha opcional com versão/velocidade de link (SATA/NVMe) via `diskLinkLabel()`. |
| `DeviceTile` | Identidade de dispositivo SEM clique/modal (GPU, PCI, USB, discos anexados de VM/LXC) | Mesmo "DNA" visual do `DiskTile` (`.dev-tile*`) mas sem cursor/hover. Badge à direita pra categoria/destaque. Usado também em `GuestInfoCard` para discos anexados. |
| `SensorTile` | 1 leitura de sensor de temperatura, dentro de um grupo | Cor por `sensorTempColor(group, valor)` — CPU tolera mais que disco; "Discos"/"NVMe" reusam `diskTempColor` da aba Armazenamento (mesma peça física, tem que concordar). |
| `ToastContainer` | Notificações (canto sup. dir.) | Usa `createPortal`. Não renderize outro — só existe um, no root de `App`. |
| `ConfirmModal` | Dialog de confirmação Promise-based | Idem. Acesse via `confirmDialog(msg)` — não renderize outro. |
| `Modal` | Qualquer modal | **Sempre** via `createPortal(..., document.body)` — ver gotcha abaixo. |
| `Bar` | Barra de progresso/uso (%, com cor por faixa) | `thick` prop pra versão mais grossa (usada em Armazenamento). |
| `EntityIcon` | Ícone de qualquer entidade (com fallback Lucide) | `onEdit` prop abre o `IconPicker` se passado. |
| `HBadge` | Pílula de saúde/status (`ok`/`warn`/`bad`) | Cor por `healthClass()`. |

### Por que `Modal` usa `createPortal`

```javascript
// portal direto no <body>: um ancestral com transform (mesmo "encerrado",
// ex.: a animação .fade de entrada da view) cria containing block p/
// position:fixed e desloca o modal — independente disso, ele sempre fica
// relativo à viewport.
function Modal({ title, onClose, children, wide }) {
  return createPortal(<div className="modal-bg" onClick={onClose}>...</div>, document.body);
}
```

Isso foi um bug real (modal de NIC abrindo deslocado por causa de uma
animação CSS no ancestral) — qualquer modal NOVO deve seguir esse padrão,
nunca renderizar inline dentro da árvore da aba.

## Helpers de UI reutilizáveis

### `statusPill(status, type)`

Retorna um `<span className="hbadge status-pill {ok|warn|bad|off}">` com texto
em PT-BR. Primeira letra maiúscula, resto minúsculo (CSS `text-transform:none`
na classe `status-pill`). Para VMs (`type === "vm"`) usa formas femininas
(`"Parada"`, `"Pausada"`, etc.). Use **sempre** este helper — não construa a
pílula manualmente:

```javascript
const STATUS_LABEL    = { running:"Rodando", stopped:"Parado", paused:"Pausado", ... };
const STATUS_LABEL_VM = { stopped:"Parada", paused:"Pausada", degraded:"Degradada", ... };
const STATUS_CLS      = { running:"ok", paused:"warn", error:"bad", ... }; // default: "off"
const statusPill = (status, type) => { ... };
```

Aparece em: header da entity detail (VM/LXC/container). **Nos cards** de
vm/ct/container/pod a pill de texto foi **substituída pelo glifo de estado**
(`stateGlyph`, ver abaixo); **nos hosts** (menu lateral e título) usa-se
`connPill`.

### `connPill(status)`, `stateGlyph(cls, label)` / `stateGlyphFor(status,type)`, `monitorGlyph(km)`

- **`connPill`** — pill de conectividade do **host**: `"Conectado"` (status
  `running`) verde / `"Desconectado"` (resto) vermelho. Usada no item de sidebar
  e no título da integração.
- **`stateGlyph`/`stateGlyphFor`** — glifo `CirclePlay` colorido por
  `.m-state.{ok|bad|warn|off}` (hover = label), no `.m-badges` dos cards de
  vm/ct/container/pod. `stateGlyphFor(status,type)` deriva cls+label do status;
  o `K8sPodCard` calcula cls/label à mão pra cobrir transitórios.
- **`monitorGlyph(km)`** — glifo `Activity` colorido pelo estado do monitor UK
  vinculado; `km` vem de `monitorFor(ent)` no `App` (resolve `kuma_monitor_id` →
  `monitorState`), passado por prop até o card. `null` = não renderiza.

### `EntityTabs`

Wrapper de abas que **retorna `null` se `tabs.length <= 1`** — evita mostrar
uma única aba sem sentido. Hosts Docker têm só "overview", então a barra de
abas some automaticamente.

### `runAction` vs `runContainerAction`

- **`runAction(entity, verb)`** — para VMs/LXCs. Chama `confirmDialog` antes de
  executar. Mostra toast de resultado.
- **`runContainerAction(container, verb)`** — para containers Docker. Sem confirm
  dialog (operações reversíveis/rápidas). Mostra toast de resultado.

Não use `runAction` para Docker nem vice-versa.

## Formatters (linhas ~14-59 de `App.jsx`)

Reuse, não reinvente:

| Função | Saída | Uso |
|---|---|---|
| `bytes(n)` | `"1.5 GB"` | qualquer tamanho em bytes |
| `pctFmt(v)` | `"75.3%"` | percentuais (1 decimal) |
| `rateFmt(v)` | `"1.2 MB/s"` | taxas de transferência |
| `speedFmt(mbps)` | `"100 Mb/s"` / `"1.5 Gb/s"` | velocidade de interface de rede |
| `loadFmt(v)` | `"0.50"` | load average |
| `uptimeFmt(s)` | `"5d 3h"` | uptime |
| `tempFmt(v)` | `"52.3°C"` | temperatura |
| `powerOnFmt(hours)` | `"10.878h (1a88d)"` | horas ligado de disco, locale pt-BR |
| `countFmt(v)` | `"1.234"` | contadores (separador de milhar) |
| `durationFmt(s)` | `"1m 23s"` / `"2h 5m 3s"` | duração de task Proxmox (segundos → texto) |
| `pctLevel(pct)` | `"ok"\|"warn"\|"bad"` | faixa de uso GLOBAL (≤80/81-90/≥91) — CPU/mem/UPS |
| `storagePctLevel(pct)` | `"ok"\|"warn"\|"bad"` | faixa de uso de **armazenamento** (≤70/71-90/>90) — thresholds mais estritos que CPU/mem |
| `logPriLabel(pri)` | `"INFO"\|"WARN"\|"ERRO"` | prioridade syslog → label PT-BR p/ pill do log |
| `logTaskLabel(type)` | `"Início VM"` etc. | task type do PVE → label humana via `LOG_TASK_LABELS` |
| `backupStorageLabel(t)` | `"PBS"\|"Local"` | `storage_type === "pbs"` → "PBS", qualquer outro → "Local" |
| `backupStoragePill(t)` | classe CSS | "PBS" → `"dev-tile-badge accent"`, "Local" → `"dev-tile-badge"` |
| `isLive(lastSeen)` | bool | "coleta online" (visto há <60s) — alimenta `.live-dot` |

**Importante:** `storagePctLevel` é separado de `pctLevel` de propósito — disco cheio tem impacto maior, alerta começa em 70% enquanto CPU/mem alertam em 80%. Não unifique os dois.

## Padrão de tabs de entidade (Overview/Armazenamento/Rede/Hardware/Logs)

Toda aba de host segue a mesma forma: `<TabXContent>` recebe `entity`/`panels`
(+ specifics) e renderiza, nessa ordem:

1. `.tiles` (métricas-resumo no topo)
2. `<Graphs>` (histórico, se a aba tiver série temporal relevante)
3. Cards de inventário (`.grid2`/`TitledCard`)
4. Grade de VMs/LXCs, se a aba também mostrar isso (Overview e Rede)

Uma aba NOVA deve seguir essa mesma ordem salvo instrução contrária — é o
que o usuário já validou em 5 abas existentes.

## Página de detalhe de VM/LXC (`sel` branch em `App()`)

Quando `sel` não é null (usuário clicou em uma VM/LXC na grade), o layout é:

1. **Topbar**: voltar + ícone + nome + subtítulo + botões de ação
2. **Subtítulo** (`.entity-sub`): pill de tipo + ID em destaque + pill de status
3. **Tiles** (`<Tiles extra={[{label:"IP",...}]}>`) — inclui IP como tile extra via prop `extra`. Desde v3.15 os tiles extras aceitam também `icon` (componente lucide, senão cai em `METRIC_ICON`) e `onClick` (vira clicável com `cursor:pointer`) — é assim que o tile "Diag" da Overview do Proxmox abre o `DiagModal`.
4. **Graphs** — série temporal dos painéis
5. **`<GuestInfoCard entity={selLive} />`** — card de informações completas

### Subtítulo de VM/LXC

```jsx
<div className="entity-sub">
  <span className={`type-pill ${selLive.type}`}>{selLive.type === "ct" ? "LXC" : "VM"}</span>
  <b className="entity-id">ID {selLive.id.split("/").pop()}</b>
  <span className={`m-status ${selLive.status}`}><span className={`dot ${selLive.status}`} />{selLive.status}</span>
</div>
```

- `type-pill.vm` = azul accent; `type-pill.ct` = roxo `#a371f7`
- ID extraído via `.split("/").pop()` — remove path completo `proxmox/pve/qemu/100` → `"100"`
- Status usa `m-status` **sem** `.entity-head` ancestor → aparece como dot+texto colorido (igual Overview tiles), não como pill com borda

### NEED.default e `buildPanels` para guests

```js
NEED.default = ["cpu_pct", "mem_used_bytes", "mem_total_bytes",
  "disk_used_bytes", "disk_total_bytes",       // adicionados: disco de capacidade
  "net_rx_bytes", "net_tx_bytes", "disk_read_bytes", "disk_write_bytes"]
```

`buildPanels` para `type !== "host"` cria painel "Disco" (% de uso de capacidade) via
`pctSeries(raw.disk_used_bytes, raw.disk_total_bytes)` — cor `#f778ba`, chave `"disk"`.
O host usa fonte diferente (inventário `storages`), não amostras.

### Aba Logs — padrão de tiles paginados

- `LOG_PAGE_SIZE = 5` itens por página
- `page` state reseta ao trocar subtab, período, ou busca
- `search` state filtra `filtered` antes de paginar
- `filtered` usa match case-insensitive em campos relevantes (logs: msg/tag/type/node/user/vmid; backups: storage/vmid/volid; notif: name/type)
- Tile de armazenamento de backup: 1 `StatTile` por entrada em `backups.storages_info`, label = nome do storage (ex. "Bkp1tb"), valor = `used / total` real do storage (não soma de arquivos)

### StorageUsageRow — layout da linha abaixo da barra

```jsx
<div className="store-bottom">
  <b className="store-num" style={{ color:"var(--text)", fontSize:14 }}>{bytes(storage.total)}</b>
  <b className="store-num" style={{ color: barColor, textAlign:"center" }}>{bytes(storage.used)}</b>
  <span className="store-num" style={{ color:"var(--ok)", textAlign:"right" }}>livre {bytes(storage.avail)}</span>
</div>
```

`.store-bottom` é `display:grid; grid-template-columns:1fr auto 1fr` — 3 colunas:
total (branco/negrito, esq) · em uso (cor da barra, centro) · livre (verde, dir).

## Preferências/threshold: sempre persistidas no servidor

`prefs` (disco padrão por host, etc.) e thresholds (global + por-entidade)
**nunca** vão para `localStorage` — só o token de auth fica lá. Qualquer
preferência nova do usuário deve usar `api.getPrefs()`/`api.putPrefs()`
(ver `savePrefs()` em `App.jsx`) — isso foi pedido explicitamente pelo
usuário ("todas as preferências devem ficar salvas em banco por usuário, de
preferência nada no navegador" — `prompt`, linha 35). Sessão `user:…` grava em
`users.preferences`; token de API grava em `tokens.preferences` (GET vazio lê a
Home do 1º usuário como semente). O menu "Alterar senha" usa `me.has_password`.

## Home — atalhos de serviços (`HomeView`, jul/2026)

- `HomeView({ entities, alarms, latestMap, iconSet, prefs, savePrefs })` — view de
  `integ === "home"`. Tiles por integração + grupos de atalhos; **não** renderiza
  cards de entidades.
- `ShortcutModal({ item, initialGroup, groups, entities, onClose, onSave, onRemove })` —
  nome/URL/grupo (datalist dos grupos existentes) + select de vínculo com entidade
  (types em `SC_LINK_TYPES`: vm/ct/container/pod/deployment, optgroup por integração).
  `onSave` recebe objeto `{name, url, group, entity}`.
- `ShortcutIcon({ name, icon, iconSet, size })` — `icon` pode ser slug do dashboardicons
  ou data URI (`data:` usado direto como src); sem icon, matching por nome; fallback Globe.
- Ícone do atalho é um botão → abre `IconPicker` com `onSave`=slug no pref e
  `onUpload`=FileReader→dataURL (cap 300 KB). `IconPicker` esconde "enviar ícone"
  quando `onUpload` não é passado.
- Grupos: seções derivadas de `s.group`, recolhíveis (chevron `.sc-collapse`, estado
  `prefs.scCollapsed[gKey]`, `gKey = g || "_default"`), `+` no cabeçalho pré-preenche
  o grupo via `initialGroup`.
- Pill de disponibilidade: `scStatus(s)` resolve `s.entity` em `entities` →
  `.sc-status` (hbadge pequeno) ok/warn/bad/off.

## K8s — estados transitórios e status de ação (jul/2026)

- Backend expõe em pod attributes: `terminating` (deletionTimestamp) e `waiting_reason`.
- `K8sPodCard`: deriva `terminating`/`failing` (regex `BackOff|Err|Invalid` no reason)/
  `starting` (Pending ou Running sem ready) → classes `.machine.k8s-terminating`/`alert`/
  `.machine.k8s-starting` + pill via `transPill(label, cls)` (spinner embutido).
- `k8sOps` (state do App): mapa entity.id → `{verb, phase: running|ok|error, detail, error}`,
  alimentado por `runK8sAction` (helpers `patchK8sOp`/`clearK8sOp`; ok limpa em 6s, erro em
  20s). Desce por `K8sOverviewContent` → prop `op` dos cards → `K8sOpStrip({ op })`.
- `Bar({ pct, color, thick, busy })` — `busy` liga listras animadas (`.bar span.busy`);
  usado no deploy convergindo e na barra do `ProgressModal`.

## Mobile — drawer da sidebar (jul/2026)

- `navOpen` (state do App) → `.sidebar.open` + `.nav-backdrop`; hambúrguer `.nav-burger`
  no `.appbar` (só aparece ≤820px). `switchInteg()` e o item Alarmes fecham o drawer.
- Bloco responsivo único em `@media (max-width: 820px)` no fim do `styles.css`.

## Configurações, vínculo UK e sidebar recolhível (jul/2026)

- **`ConfigView` + `ConfigSection`** (`integ === "config"`, item de sidebar
  só-admin): carrega `api.getConfig()` (`{schema, values, hasKey}`) e renderiza
  um `TitledCard` por integração com campos do schema. Secret mostra "••••
  definido" (do `secretsSet`) + botão limpar; `buildPatch()` só manda secret se
  digitado/limpo. Botões "testar conexão" (`api.testConfig`) e "salvar"
  (`api.putConfig`). Layout `.cfg-grid` em **colunas (masonry)**.
  Card extra `DiagGuestsCard` (v3.26): lista VMs/CTs do inventário Proxmox com
  checkbox (marcado = entra no Diag); `api.setHealthExcluded`; CSS `.diag-guest-*`.
- **Monitor UK no card**: `EntityEditModal` (lápis) grava `kuma_monitor_id` via
  `api.setEntityLink` (preserva `service_url` legado). URLs de abrir serviço ficam
  **só** nos atalhos da Home — tiles/páginas de VM/CT/Docker sem botão de link.
- **Sidebar recolhível**: `navCollapsed` (state + `localStorage`), `.app.nav-collapsed`;
  botão « (`.nav-collapse` no `.brand`) recolhe, » (`.nav-expand` no `.appbar`)
  reabre. Recolhido = coluna única + `.sidebar { display:none }` (ver SKILL.md
  pro porquê de não usar `0 1fr`). Escondidos no mobile.
