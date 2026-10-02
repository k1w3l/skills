# Otimização e ajuste dos jobs

Baseado no manual oficial (freefilesync.org/manual.php), aplicado à topologia
deste host: origem NFS na rede, destino NTFS local.

## Índice

- [Variantes de comparação](#variantes-de-comparação)
- [Paralelismo](#paralelismo)
- [Política de exclusão e versionamento](#política-de-exclusão-e-versionamento)
- [Filtros](#filtros)
- [Config atual do NAS_K8s](#config-atual-do-nas_k8s)

## Variantes de comparação

Escolher errado aqui é a diferença entre um sync de minutos e um de horas.

| Variante | Critério | Quando usar | Custo |
|---|---|---|---|
| **File time and size** | Data de modificação **e** tamanho batem | Sincronizar com um destino de backup. É o padrão e o certo para este host. | Baixo — só metadados |
| **File content** | Conteúdo bit a bit idêntico | Verificação de consistência; fallback quando a data de modificação não é confiável (celulares, FTP antigo) | Altíssimo — lê os dois lados inteiros |
| **File size** | Só o tamanho | Quando a data não existe ou é inútil (MTP, FTP) e comparar conteúdo é lento demais | Baixo, mas **arquivos de mesmo tamanho e conteúdo diferente passam como iguais** |

O job usa `TimeAndSize`, que é a recomendação oficial para backup. Só troque para
`Content` em uma verificação pontual de integridade — nunca no job agendado, já
que ele leria dezenas de GB pela rede a cada duas horas.

Se aparecerem "conflitos" de mesma data e tamanho diferente, ou arquivos
reportados como alterados sem terem mudado, a suspeita é resolução de timestamp
entre filesystems (NTFS e NFS não guardam mtime com a mesma granularidade). O
`IgnoreTimeShift` do job existe para isso — útil também para horário de verão.

## Números medidos neste host (2026-07-27)

Base para decidir se vale mexer em alguma coisa, em vez de chutar:

| Medição | Valor | Implicação |
|---|---|---|
| Link de rede | 2,5 GbE (`enp16s0`) | teto teórico ~312 MB/s |
| Leitura NFS (`/mnt/NAS`) | **225 MB/s** | origem **não** é o gargalo |
| Destino | 4 HDs mecânicos, LDM **spanned** | ~150–180 MB/s por stream |
| Dados | 10 TB origem / 9,9 TB destino | delta pequeno, não é cópia do zero |

**Cuidado ao medir escrita em `/mnt/NAS_BKP`:** o `ntfs3` não honra
`fsync`/`fdatasync`/`sync` para os dados do arquivo. Escrever 3 GB resultou em
**28 KB** chegando aos discos físicos — o resto ficou em page cache. Qualquer
`dd` vai reportar números fictícios (medi 3,3 GB/s em 4 HDs mecânicos). O
volume também rejeita `O_DIRECT` (`Operation not supported`), então esse escape
não existe.

Para medir a taxa real, olhe os discos físicos, não o `dd`:

```bash
awk '$3=="sda"||$3=="sdb"||$3=="sdc"||$3=="sdd"{s+=$10} END{print s*512/1024/1024" MB"}' /proc/diskstats
```

Amostre antes e depois de um intervalo **durante um sync de verdade**. É a única
leitura confiável de vazão de escrita neste volume.

Consequência prática para jobs grandes: os primeiros GB parecem instantâneos
(cache), e a velocidade despenca quando o cache satura. Não conclua nada sobre
desempenho pelos primeiros minutos de um sync.

## Paralelismo

O manual descreve o modelo com precisão, e ele não é intuitivo:

- O número de operações paralelas é configurado **por dispositivo**, não por par
  de pastas (diálogo *Comparison Settings*).
- **Na comparação**, as pastas são agrupadas pela raiz do dispositivo. Vários
  pares que compartilham a mesma raiz dividem o mesmo limite — não somam.
- **Na sincronização**, cada par usa o **máximo** entre os dois lados:
  `max(origem, destino)`.

Exemplo do manual: com `C:\` = 1, `D:\` = 2, `E:\` = 3, os pares `C:\Source↔D:\Target`
e `C:\Source2↔E:\Target` sincronizam com 2 e 3 operações respectivamente, e
`C:\Source`/`C:\Source2` compartilham 1 operação na fase de comparação.

Aplicando aqui — os 12 pares do `NAS_K8s` têm só **duas** raízes de dispositivo:

- `/mnt/NAS` — NFS. Latência de rede domina. Paralelismo **ajuda muito**: enquanto
  uma operação espera a rede, outra progride. Vale testar 4–8.
- `/mnt/NAS_BKP` — NTFS local, e aqui o caso é particular: são **4 HDs mecânicos**
  (`sda`–`sdd`) unidos em um volume LDM spanned de 14,6 TB. Em um único disco
  mecânico a regra seria manter paralelismo baixo (1–2), porque operações
  concorrentes viram seek. Com 4 fusos, o volume tolera mais concorrência —
  desde que os arquivos caiam em discos diferentes, o que num volume spanned
  depende de onde o LDM alocou. Vale testar 3–4 e medir, sem assumir ganho.

Como os 12 pares compartilham as mesmas duas raízes, `Threads="2"` não significa
24 operações — significa 2 por grupo de dispositivo na comparação.

### Quebrar em vários jobs não aumenta paralelismo

Pergunta recorrente: "e se eu criar um job por diretório?" Pelo modelo do
manual, **não ajuda** — o limite é por raiz de dispositivo, e 12 jobs continuam
disputando as mesmas duas raízes (`/mnt/NAS` e `/mnt/NAS_BKP`).

- **Em série:** trabalho total idêntico, só com overhead de 12 inicializações.
- **Em paralelo:** pior. 12 processos concorrendo pelos mesmos 4 fusos mecânicos
  viram thrashing de seek, e você perde a coordenação por dispositivo que o
  próprio FreeFileSync faz — cada processo só enxerga o próprio limite.

A alavanca certa é o número de operações paralelas, não o número de jobs.
Quebrar em jobs só faz sentido por outros motivos: agendar frequências
diferentes por diretório (ex.: `Sync` de hora em hora, `Media` uma vez por
semana), ou isolar um diretório problemático para não derrubar o resto.

### O detalhe que inverte a intuição

Como a sincronização usa `max(origem, destino)`, **não dá para configurar
"origem rápida, destino lento"**. Subir `/mnt/NAS` para 16 pensando em acelerar
a leitura via NFS faz a fase de sync martelar o volume mecânico com 16 operações
concorrentes — exatamente o que você queria evitar.

O ajuste tem que ser escolhido pensando na fase de sincronização, que é a que
manda. Um valor moderado igual dos dois lados (4–6) acelera a comparação em
relação a 2 sem estourar o destino. Suba um degrau por vez e compare o tempo
total no rodapé do log HTML.

Confirme a natureza dos discos antes de recomendar número (`ROTA=1` é mecânico):

```bash
lsblk -o NAME,ROTA,SIZE,MODEL,MOUNTPOINT | grep -B4 NAS_BKP
```

Meça antes e depois em vez de chutar: o tempo total está no rodapé do log HTML de
cada execução.

## Política de exclusão e versionamento

O job usa `DeletionPolicy=RecycleBin`. Como as três direções estão com
`Delete="none"`, isso hoje não tem efeito prático — mas a lixeira é frágil em
volumes não-nativos (NTFS montado no Linux, NFS): pode falhar ou espalhar
`.Trash-1000` pelo destino. Note que o filtro do job já exclui `*/.Trash-*/` e
`*/.recycle/`, o que sugere que isso já incomodou antes.

Se a deleção for habilitada algum dia, **versionamento é mais seguro que lixeira**
neste ambiente. Do manual:

```
Deletion Handling: Versioning
Naming Convention: Time stamp [File]
```

Resulta em cópias datadas, preservando a estrutura de pastas:

```
D:\Revisions\Folder\File.txt 2020-12-11 111111.txt
D:\Revisions\Folder\File.txt 2020-12-12 122222.txt
```

O estilo `Replace` (o do job atual) guarda só a última versão. `TimeStamp` guarda
histórico, ao custo de espaço — vale combinar com uma limpeza periódica da pasta
de versões.

## Filtros

Filtros reduzem trabalho antes de qualquer I/O, então são a otimização mais
barata que existe. Exclusões atuais:

```xml
<Item>*/.Trash-*/</Item>
<Item>*/.recycle/</Item>
```

Candidatos que costumam valer a pena numa árvore com backup de perfil Windows e
VMs:

```
*/_gsdata_/          # metadados do GoodSync (o dir do erro de permissão de 2026-07-27)
*/System Volume Information/
*/$RECYCLE.BIN/
*/Thumbs.db
*/desktop.ini
*/.DS_Store
*/lost+found/
```

Cuidado com arquivos de VM (`/mnt/NAS/VMs`, `/mnt/NAS/Backup VMs`): discos
grandes que mudam por inteiro a cada execução. Se o sync estiver lento, esses
pares são os primeiros suspeitos — o FreeFileSync copia o arquivo completo, sem
delta. Se o objetivo for backup de VM, `rsync` ou snapshot no lado do NAS podem
ser mais adequados que sincronizar imagens inteiras a cada 2h. Vale levantar isso
com o usuário em vez de tentar acelerar o inacelerável.

## Config atual do NAS_K8s

Registro do estado em 2026-07-27, para comparação futura:

```xml
<Compare>
    <Variant>TimeAndSize</Variant>
    <Symlinks>Exclude</Symlinks>
</Compare>
<Synchronize>
    <Changes>
        <Left Create="right" Update="right" Delete="none"/>
        <Right Create="none" Update="none" Delete="none"/>
    </Changes>
    <DeletionPolicy>RecycleBin</DeletionPolicy>
    <VersioningFolder Style="Replace"/>
</Synchronize>
<Errors Ignore="false" Retry="0" Delay="5"/>
```

Leitura: cópia unidirecional `/mnt/NAS` → `/mnt/NAS_BKP`, cria e atualiza no
destino, **nunca apaga**. Conservador e adequado para backup — o destino acumula
arquivos que sumiram da origem, mas nada é perdido por engano.

O `NAS_K8s.ffs_gui` do mesmo dia, porém, é **Mirror com deleção**:

```xml
<Differences LeftOnly="right" LeftNewer="right" RightNewer="right" RightOnly="right"/>
```

`RightOnly="right"` significa que arquivo existente só no destino é **apagado**.
Rodar o job pela GUI e pelo cron produz resultados diferentes. Sempre verifique
qual arquivo está em jogo antes de afirmar o que o sync vai fazer, e trate a
variante Mirror com o cuidado extra que ela merece — combinada com a origem em
automount, uma montagem que não materializou vira esvaziamento do destino.

12 pares: `Media`, `VMs`, `Viagens`, `Games`, `Backup Telefone`, `Backup VMs`,
`Tools`, `Sync`, `PCL`, `Downloads`, `Temp`, `K8s`.

Dois pontos de atenção já identificados:

- `Retry="0"` não tolera oscilação transitória do NFS. Considere `Retry="2" Delay="5"`.
- `ErrorDialog=Show` (bloco `<Batch>`) trava execução desatendida — ver
  `cron-automacao.md`.
