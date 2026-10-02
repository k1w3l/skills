# CSS & Layout — referência completa

Tudo em `frontend/src/styles.css` (~400 linhas, plano, sem pré-processador,
sem Tailwind/styled-components). Tema único, escuro. Antes de inventar uma
classe nova, procure no catálogo abaixo — a maioria dos "novos" cards/grades
que uma feature precisa já tem uma classe parecida.

## Tokens (`:root`)

```css
--bg: #0d1117;      --bg2: #0e1117;     --panel: #161b22;   --panel2: #1c232d;
--border: #232a34;  --text: #e6edf3;    --muted: #9aa4b2;   --accent: #5b8def;
--ok: #3fb950;       --warn: #d29922;    --err: #f85149;
```

Cor de estado é sempre `ok`/`warn`/`err` — não invente um quarto nível sem
necessidade real (exceção documentada: faixas de uso de disco 0-80/81-90/≥91
mapeiam pra esses 3 mesmos tons via `pctLevel()`).

## Ritmo de espaçamento (regra mais importante deste arquivo)

`.section-title` é a unidade de medida de respiro vertical do app inteiro:

```css
.section-title { margin: 22px 0 10px; /* ...resto do estilo visual... */ }
```

**22px antes, 10px depois** — esse é o espaço entre qualquer título de seção
e (a) o que vem antes dele, (b) o card/conteúdo que vem depois. Qualquer
título novo (literal `.section-title` ou um `TitledCard`/cabeçalho de grade
parecido) deve respeitar esse mesmo ritmo — **não invente outro valor de
margem** pra "parecer mais separado" ou "mais colado". Bug real corrigido
nesta sessão: um título com `margin: 0` inline ficou colado tanto no
conteúdo de cima quanto no de baixo — o fix foi mover a margem 22/0/10 pro
container do título, não inventar um valor novo.

Quando dois blocos de grade (`.grid2.inventory`) ficam em sequência sem um
título "pai" entre eles, o gap entre eles também precisa desses 22px — ver
`.grid2.inventory + .grid2.inventory { margin-top: 22px; }`. Generalize esse
raciocínio: **toda transição visual de "bloco" deve valer 22px**, goste ou
não da classe específica usada para chegar lá.

## Catálogo de grades (grid) — qual usar

| Classe | Track | Quando |
|---|---|---|
| `.tiles` | `flex` **nowrap** (não grid no desktop); `flex: 1 1 0; min-width: 0`; padding/fonte compactos | Métricas-resumo no topo (host e detalhe VM/CT). Uma linha no desktop — 8 tiles do host e ~10 do guest. Mobile ≤820 vira grid 2 col. |
| `.grid2` | `repeat(2, 1fr)`, gap 16px, colapsa pra 1 col em <900px | Par de cards/gráficos lado a lado (RX/TX, Processador/Memória). |
| `.machines` / `.net-machines` | `repeat(auto-fill, minmax(220px, 1fr))`, gap 12px | Grade de VMs/LXCs ou de máquinas com NICs — quantas colunas couberem, cresce com 1fr. |
| `.nic-grid` | igual ao acima, minmax(220px,1fr) | Grade de cards de interface de rede. |
| `.chip-grid` | `minmax(170px, 1fr)` | Inventário de dispositivo (PCI/USB/sensor/GPU) — chips pequenos, não tabela. |
| `.disk-tile-grid` | `minmax(300px, 1fr)` | Discos físicos (tile maior que NIC, mais informação). |
| `.kv-grid` | `repeat(2, 1fr)`, gap 8px 16px | Pares chave/valor dentro de um card ou modal. |

Regra: **não crie uma grade nova do zero** pra um caso parecido com algum da
tabela acima — reuse a classe, só ajuste o componente filho.

## Catálogo de cards — qual usar

| Padrão | Componente | Título |
|---|---|---|
| Card simples | `<div className="card">` | nenhum, ou implícito pelo contexto |
| Card com título **fora** | `TitledCard` | fora da caixa, mesmo ritmo de `.section-title`; ver receita abaixo. É o padrão único hoje — `InfoCard` (título dentro da caixa) foi removido em jun/2026 por ficar sem uso depois que Hardware migrou pra `TitledCard`. |
| Tile clicável (abre modal) | `.nic-card`, `.disk-tile` | sem título de card — a identidade é o conteúdo do próprio tile |
| Tile de identidade, sem clique | `.dev-tile` (GPU/PCI/USB), `.sensor-tile` (sensores), `.mem-tile` (módulos de RAM) | mesmo "DNA" do `.disk-tile` (linha de identidade + destaque colorido), mas sem `cursor:pointer`/hover — não abrem modal, não inventam dado que a integração não tem |

### Receita: título fora do card, sem perder alinhamento

Quando um card precisa do título **fora** da borda (em vez de dentro, como
`InfoCard`), o jeito que funciona (validado visualmente com Playwright, ver
seção de verificação abaixo) é envolver título+card num wrapper que estica
junto com a linha do grid:

```css
.titled-card { display: flex; flex-direction: column; }
.titled-card > .card { flex: 1; display: flex; flex-direction: column; justify-content: center; }
```

```jsx
function TitledCard({ title, icon: Icon, children }) {
  return (
    <div className="titled-card">
      <div className="section-title" style={{ margin: "0 0 10px" }}><Icon size={15} /> {title}</div>
      <div className="card">{children}</div>
    </div>
  );
}
```

Por quê: o item de grid (`.titled-card`) estica por padrão (`align-items:
stretch` é o default do CSS Grid) pra acompanhar a altura do vizinho — mas
SÓ o wrapper, não o `.card` lá dentro, que por padrão fica com a altura do
próprio conteúdo. Sem o `flex:1` no `.card`, dois cards vizinhos com
quantidades de conteúdo diferentes ficam com alturas diferentes mesmo
"esticando" o wrapper (sobra espaço vazio invisível). Com `flex:1 +
justify-content:center`, o card mais curto cresce até a altura do vizinho
**e** centraliza o conteúdo dentro do espaço sobrando, em vez de ficar colado
no topo com vão vazio embaixo. Se um card novo tiver esse mesmo problema
(vizinho de altura diferente), use esse padrão — não invente outro.

**Cuidado com o seletor**: `.titled-card > .card` usa filho direto (`>`), de
propósito — se fosse descendente (` .card`), pegaria também cards ANINHADOS
dentro do conteúdo (ex.: `.disk-tile` é `class="card disk-tile"` dentro da
área de Discos físicos) e quebraria o layout interno deles.

### Receita: alinhar 2 cards com os gráficos acima

Quando um par de cards lado a lado precisa ficar com a MESMA largura/gap de
um `.grid2` de gráficos logo acima (pra parecer uma continuação visual —
caso da aba Rede: cards de Interfaces/Configuração alinhados com RX/TX):

```css
.net-cols-head { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 22px 0 10px; }
.net-cols       { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 22px; }
```

Mesmas colunas (`repeat(2, 1fr)`) e mesmo `gap` (16px) que `.grid2` — não
`2fr 1fr` ou outra proporção "que parece melhor", ou a coluna não bate com
o gráfico de cima. Título de cada coluna vai numa grade-cabeçalho separada
(`-head`) com as MESMAS colunas, não dentro do card — replica a ideia do
"Histórico" (`.graphs-head`), que também fica fora do card do gráfico.

### Gotcha: grid aninhado pode "vazar" largura pro pai

Um card que é, ele mesmo, item de uma grade `auto-fill` (ex.: `.net-machine-card`
dentro de `.net-machines`) e que **também** contém uma grade `auto-fill` lá
dentro (ex.: `.nic-grid` com várias NICs) corre risco de o filho "exigir"
mais largura mínima do que o esperado, fazendo o item do grid pai colapsar
pra menos colunas do que deveria (sintoma: "os cards aparecem 1 por linha"
mesmo a grade aceitando vários). Defesa de baixo custo, já aplicada:

```css
.net-machine-card { min-width: 0; }
```

Isso some o "automatic minimum size" baseado em conteúdo que o CSS Grid dá
por padrão a qualquer item (`min-width: auto`). Aplique em qualquer card
novo que seja, ao mesmo tempo, item de grid E container de outro grid/flex
com conteúdo que pode crescer.

## Tiles com valor composto (mais de uma info no mesmo tile)

Quando um `StatTile` precisa mostrar mais que um valor solto (ex.: nome da
interface + velocidade + status, em vez de só um número), NÃO concatene tudo
numa string só (`"enp6s0 · 1 Gb/s · Ativa"`) — fica ilegível e não escala
pra um quarto campo. Em vez disso, passe JSX pro `value` com a info primária
em destaque (herda `.t-v`) e o resto numa sub-linha menor:

```css
.tile-iface { display: flex; flex-direction: column; gap: 5px; }
.tile-iface-sub { display: flex; align-items: center; gap: 7px; font-size: 12px; font-weight: 600; color: var(--muted); }
```

```jsx
<span className="tile-iface">
  <span className="mono">{iface}</span>
  <span className="tile-iface-sub"><span>{speed}</span><span className={`hbadge ${active ? "ok" : "warn"}`}>{status}</span></span>
</span>
```

## Tiles de máquina (`.machine`) — rodapé sempre alinhado no fundo

`.machine` é `display: flex; flex-direction: column` — isso faz todos os tiles
num mesmo row de grid esticarem para a mesma altura. `.m-foot` usa
`margin-top: auto`, o que absorve o espaço sobrante e cola o rodapé **sempre
no fundo do tile**, independente de quantas linhas de conteúdo houver acima
(ex.: tile Docker sem portas vs. com portas — o rodapé fica alinhado nos dois).

Nunca use `margin-top: <valor fixo>` no `.m-foot` — use `auto`.

### `.m-foot` e `.m-actions`

- `.m-foot` — `display:flex; justify-content:space-between; align-items:center`.
  Sempre dois filhos: algo à esquerda (`.m-ip` com IP, ou `<span />` vazio como
  placeholder) + `.m-actions` à direita.
- `.m-actions` — `display:flex; align-items:center; gap:4px`. **Não adicione
  `flex-wrap` nem `justify-content` globalmente** — isso quebra os tiles do
  Proxmox. Se precisar de overflow, trate no componente filho (inline style).

### Status pill (`.hbadge.status-pill`)

```css
.hbadge.status-pill { text-transform: none; letter-spacing: 0; font-size: 10px; }
```

Sobrescreve o `text-transform:uppercase` do `.hbadge` base — **só** para pills
de status (os outros badges, como tipo NIC ou alarme, continuam em uppercase).
Use sempre `statusPill(status, type)` helper em vez de construir manualmente.

### Classes Docker-específicas (não alteram tiles Proxmox)

```css
/* porta publicada no host — no rodapé do tile (à esquerda das ações) */
.ct-ports { display:flex; flex-wrap:wrap; gap:6px; align-items:center;
            min-width:0; flex:1; }
.ct-ports-block { display:flex; flex-wrap:wrap; gap:8px; align-items:center; }
.ct-port  { font-size:13px; font-weight:700; font-family:ui-monospace,monospace;
            color:var(--text); background: color-mix(in srgb, var(--accent) 16%, transparent);
            border:1px solid color-mix(in srgb, var(--accent) 40%, var(--border));
            border-radius:6px; padding:2px 8px; white-space:nowrap; }
```

Portas vêm só como bind no host (`8080/tcp`), sem a porta interna do container.
Ficam no `.m-foot` à esquerda (no lugar do IP das VMs).

## Catálogo rápido de utilitários

- `.mono` — fonte monoespaçada (IP, MAC, hostname, serial).
- `.muted` — `color: var(--muted)`, texto secundário.
- `.ell` — `max-width: 160px` + ellipsis (truncar nome longo); combine com
  `min-width: 0` no próprio elemento se ele estiver num flex/grid item, ou o
  truncamento não funciona.
- `.hbadge` (`ok|warn|bad`) — pílula pequena de status textual (SMART,
  ativo/inativo). `.badge` é o primo maior (alarmes: firing/acknowledged/resolved).
- `.hbadge.status-pill` — variante de status de entidade: `text-transform:none`,
  `font-size:10px`. Gerada via `statusPill(status, type)` — nunca construa manualmente.
- `.section-title` — título de seção com ícone, sempre `22px 0 10px` salvo
  override explícito justificado (ver receitas acima).
- `.icon-btn.danger` — botão de ação destrutiva; `:hover` fica vermelho
  (`color: var(--err)`). Usado em Power (VMs) e Square/parar (Docker).

## Verificação visual sem backend

Este ambiente normalmente **não tem** um Proxmox real nem o backend rodando
(sem dado real pra olhar a app de verdade). A técnica usada nesta sessão pra
confirmar uma mudança de CSS/layout sem isso:

1. Escreva um HTML estático mínimo num scratchpad, com `<link rel="stylesheet"
   href="/home/kiwel/git/horus/frontend/src/styles.css">` apontando **direto
   pro arquivo do repo** (não copie o CSS — assim qualquer edição que você
   fizer no styles.css real já aparece no próximo screenshot, sem passo de
   sync) e o HTML reproduzindo só a árvore de classes relevante (ex.: as
   classes do card que você está ajustando, com 2-3 itens de conteúdo
   fake — o suficiente pra disparar o bug, não a app inteira).
2. Tire screenshot com o Playwright CLI via `npx` (já tem Chromium em cache
   neste ambiente, não precisa instalar nada):
   ```bash
   npx --yes playwright screenshot --viewport-size "1600,900" --full-page \
     "file:///caminho/pro/repro.html" out.png
   ```
3. Leia o PNG com a tool de leitura de imagem e compare antes/depois. Pra
   medir altura/largura exata de um elemento em vez de confiar no olho,
   `page.$$eval(seletor, els => els.map(e => e.getBoundingClientRect()))`
   via um script `.cjs` chamando `playwright` (`chromium.launch()`) dá
   números exatos — útil quando a diferença é sutil (alguns px de
   alinhamento).
4. Pra comparar duas variantes de CSS rapidamente, gere uma cópia do
   `styles.css` com `sed` trocando só a regra em teste (ex.:
   `sed 's/align-items: start/align-items: stretch/'`) e aponte um segundo
   HTML pra essa cópia — não precisa editar o arquivo real até decidir qual
   versão ficou melhor.

Isso substitui (parcialmente) abrir a app de verdade no browser — não
dispensa rodar `npm run build` no final, mas permite confirmar
visualmente um fix de alinhamento/espaçamento **antes** de gastar tempo
descrevendo "deveria estar certo agora" sem ter olhado.
