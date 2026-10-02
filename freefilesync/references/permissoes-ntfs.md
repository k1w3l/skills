# Erros de permissão em sincronizações

Guia de diagnóstico para `EACCES`, `EPERM` e falhas de escrita. Ordenado da
causa mais provável neste host para a menos provável.

## Índice

- [Fluxo de triagem](#fluxo-de-triagem)
- [Causa 1 — atributo READONLY do NTFS (ntfs3)](#causa-1--atributo-readonly-do-ntfs-ntfs3)
- [Causa 2 — sandbox do Flatpak](#causa-2--sandbox-do-flatpak)
- [Causa 3 — NFS](#causa-3--nfs)
- [Causa 4 — volume NTFS em modo somente leitura](#causa-4--volume-ntfs-em-modo-somente-leitura)

## Fluxo de triagem

O erro do FreeFileSync diz **qual** operação falhou e **em qual caminho**. Use os
dois para separar as camadas antes de formular hipótese.

**Passo 1 — reproduza fora do app.** Isso decide se o problema é do
FreeFileSync ou do filesystem, e custa um comando:

```bash
mkdir "/caminho/exato/do/erro/__teste__" && rmdir "/caminho/exato/do/erro/__teste__"
```

Falhou também? O app está apenas reportando. Siga para o passo 2. Funcionou? Aí
sim investigue o app — provavelmente sandbox (causa 2).

**Passo 2 — encontre o elo quebrado na cadeia.** `namei -l` mostra a permissão de
cada componente do caminho, o que revela na hora qual diretório é o culpado:

```bash
namei -l "/caminho/exato/do/erro"
```

Procure por um diretório sem `w` para o dono. Exemplo real deste host:

```
drwxr-xr-x kiwel kiwel Kiwel
dr-xr-xr-x kiwel kiwel Desktop     ← o culpado: 555, sem escrita
```

**Passo 3 — identifique o filesystem**, porque a explicação depende dele:

```bash
findmnt -T "/caminho/exato/do/erro"
```

`ntfs3` → causa 1. `nfs4` → causa 3. Funcionou fora do app mas falha dentro →
causa 2.

## Causa 1 — atributo READONLY do NTFS (ntfs3)

**A causa de 100% dos casos observados neste host.** Vale conhecer em detalhe.

### Sintoma

Diretório em `/mnt/NAS_BKP` com modo `dr-xr-xr-x` (555), pertencente ao próprio
usuário, dentro de pais `755` perfeitamente graváveis. `mkdir` retorna `EACCES`
mesmo sendo você o dono. A montagem tem `dmask=0022`, que deveria produzir `755`
em todo diretório — mas este ficou `555`.

### Por que acontece

O NTFS guarda o atributo `FILE_ATTRIBUTE_READONLY` (`0x01`) por arquivo. Em
diretórios, **o Windows ignora esse bit** — lá ele serve só como marcador de
"pasta customizada", usado junto com `desktop.ini`. Por isso as pastas especiais
de um perfil Windows (`Desktop`, `Documents`, `Downloads`, `Music`, `Pictures`,
`Videos`, `Saved Games`, `Screenshots`, `Camera Roll`…) quase sempre o carregam.

O driver `ntfs3` do Linux, por outro lado, **honra o bit literalmente** e remove
o bit de escrita do modo POSIX. O `dmask` da montagem não sobrepõe isso. Você
fica dono de um diretório em que não pode escrever.

### Confirmação

```bash
getfattr -n system.dos_attrib "/caminho/do/diretorio"
```

`0sAQ==` é base64 de `0x01` = READONLY. Confirmado.

Para ver a extensão do problema numa árvore inteira:

```bash
find /mnt/NAS_BKP -type d ! -perm -u=w
```

### Correção

`chmod u+w` — no `ntfs3` isso limpa o atributo READONLY na origem, não só o modo
POSIX (verificável: `system.dos_attrib` passa de `0sAQ==` para `0sAA==`):

```bash
# um diretório
chmod u+w "/caminho/do/diretorio"

# a árvore toda de uma vez (nomes com espaço são comuns aqui — use -print0)
find /mnt/NAS_BKP -type d ! -perm -u=w -print0 | xargs -0 -r chmod u+w
```

Verifique que zerou:

```bash
find /mnt/NAS_BKP -type d ! -perm -u=w | wc -l   # esperado: 0
```

Só o bit de escrita do dono muda. Conteúdo, timestamps e donos ficam intactos.
Reverter é `chmod u-w`.

### Precedente

Em 2026-07-27, o job `NAS_K8s` falhou com `Cannot create directory
".../Users/Kiwel/Desktop/_gsdata_"`. Eram 14 diretórios de 1472 na árvore
`Games/Emudesk/Backup/` — todos, sem exceção, pastas especiais de um perfil
Windows restaurado, todas com `dos_attrib=0x01`. `chmod u+w` resolveu.

### Prevenção

O atributo viaja junto com o arquivo. Se o usuário recopiar um perfil Windows
para o volume NTFS, o problema volta. O `find | xargs chmod u+w` acima é o
remendo padrão — vale rodá-lo depois de qualquer restauração desse tipo, ou como
`PostSyncCommand` se virar rotina.

Não há opção de montagem do `ntfs3` que desligue esse mapeamento. Remontar sem
`acl` não resolve, porque o READONLY é tratado antes do `dmask`.

## Causa 2 — sandbox do Flatpak

Relevante só se a instalação Flatpak estiver em uso, e o sintoma é específico:
**funciona no terminal, falha dentro do app**.

O Flatpak só enxerga os caminhos que suas permissões liberam. `/mnt` não é
exposto por padrão em muitos manifests.

```bash
flatpak info --show-permissions org.freefilesync.FreeFileSync
flatpak override --user --show org.freefilesync.FreeFileSync
```

Procure por `filesystems=`. Sem `host` ou um `/mnt` explícito, o app não alcança
nem `/mnt/NAS` nem `/mnt/NAS_BKP`.

Concessão (preferindo o mínimo necessário ao invés de `host`):

```bash
flatpak override --user --filesystem=/mnt/NAS \
                        --filesystem=/mnt/NAS_BKP \
                        org.freefilesync.FreeFileSync
```

Cuidado com `/mnt/NAS`: é automount. O Flatpak pode montar o caminho no sandbox
antes de o automount materializar, e o app vê um diretório vazio. Se o job usa
deleção, isso é destrutivo — veja a seção de dependência de montagem em
`cron-automacao.md`.

Nota de diagnóstico: `flatpak info --show-permissions <id>` sem a branch pode
falhar com `not installed`. Use `<id>//stable` ou leia o `metadata` do deploy.
Um erro aqui **não** significa que o app não está instalado.

## Causa 3 — NFS

Vale quando o caminho que falhou está em `/mnt/NAS` (o lado de origem).

O export é `192.168.1.11:/mnt/tank/Kiwel` com `sec=sys`, ou seja, o servidor
confia no UID/GID que o cliente envia. Erros de permissão aqui normalmente são:

- **UID/GID divergente** entre o PCL e o TrueNAS. Compare `id -u`/`id -g` local
  com o dono real no NAS (`ls -lan /mnt/NAS/...`). Números diferentes = sem
  acesso, mesmo com nomes de usuário iguais.
- **Root squash** — acesso como root vira `nobody`. Não roda o FreeFileSync com
  `sudo` esperando mais permissão; no NFS costuma dar menos.
- **Permissão do dataset no TrueNAS** (ACL do lado do servidor). Investigue no
  NAS, não no cliente. A skill `truenas-skill` cobre isso.

A montagem usa `soft` e `x-systemd.mount-timeout=10s`: sob falha de rede as
operações **retornam erro** em vez de travar. Bom para não pendurar o job, mas
significa que instabilidade de rede aparece como erro de I/O no meio do sync.

## Causa 4 — volume NTFS em modo somente leitura

Distinga pelo `errno`: somente-leitura dá `EROFS` (`Read-only file system`), não
`EACCES`. Se o erro for `EACCES`, **não é isso** — volte para a causa 1.

Quando for `EROFS`, quase sempre é o NTFS marcado como sujo (dirty) — Windows
desligado com fast startup, hibernação, ou desmontagem suja. O `ntfs3` remonta
como somente leitura para se proteger.

```bash
findmnt -T /mnt/NAS_BKP -o TARGET,SOURCE,FSTYPE,OPTIONS
dmesg | grep -i ntfs3 | tail -20
```

Correção (requer o volume desmontado, e `ntfsfix` é do pacote `ntfs-3g`):

```bash
sudo umount /mnt/NAS_BKP
sudo ntfsfix /dev/mapper/ldm_vol_PC-Dg0_Volume1
sudo mount /mnt/NAS_BKP
```

Para corrupção real, `ntfsfix` não basta — só o `chkdsk` do Windows resolve.
Nesse caso, avise o usuário em vez de insistir em ferramentas do Linux.
