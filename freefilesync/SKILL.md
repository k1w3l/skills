---
name: freefilesync
description: Referência do FreeFileSync no PCL (host CachyOS do Kiwel) — onde está instalado, onde ficam os jobs e logs, como agendar via cron, e como diagnosticar erros de permissão, falhas de sincronização e lentidão. Use SEMPRE que a tarefa envolver FreeFileSync, RealTimeSync, arquivos .ffs_batch/.ffs_gui/.ffs_real, sincronização entre /mnt/NAS e /mnt/NAS_BKP, ou o job NAS_K8s — mesmo que o usuário não cite "FreeFileSync" pelo nome. Dispare também em sintomas genéricos como "erro de permissão ao sincronizar", "não consigo criar pasta no NAS_BKP", "Cannot create directory ... EACCES", "meu backup pra HD externo falhou", "o sync agendado não rodou", "a sincronização está lenta demais", ou quando algo de sync quebrar depois de atualizar o app. Esta máquina tem DUAS instalações coexistindo (nativa + Flatpak) com configs e logs separados, e o volume de destino é NTFS — duas armadilhas que fazem o diagnóstico óbvio dar errado.
---

# FreeFileSync no PCL

Sincronização do NAS (NFS) para um HD local NTFS. Duas particularidades deste
host quebram o diagnóstico ingênuo: existem **duas instalações** com estado
separado, e o destino é **NTFS via ntfs3**, que traduz atributos do Windows em
permissões POSIX de um jeito surpreendente.

## Inventário

Confirme o estado real antes de agir — o usuário migrou entre as instalações e
isso pode mudar de novo:

```bash
ls -la /opt/FreeFileSync/ /usr/bin/FreeFileSync 2>&1   # nativa
flatpak info org.freefilesync.FreeFileSync 2>&1        # flatpak
ls -lat ~/.config/FreeFileSync/Logs/ ~/.var/app/org.freefilesync.FreeFileSync/config/FreeFileSync/Logs/ 2>&1
```

O `Logs/` com mtime mais recente indica qual instalação está realmente em uso.

| | Nativa (tarball) | Flatpak |
|---|---|---|
| Binário | `/opt/FreeFileSync/FreeFileSync` | `flatpak run org.freefilesync.FreeFileSync` |
| Symlinks | `/usr/bin/FreeFileSync`, `/usr/bin/RealTimeSync` | `/var/lib/flatpak/exports/bin/org.freefilesync.FreeFileSync` |
| Config | `~/.config/FreeFileSync/` | `~/.var/app/org.freefilesync.FreeFileSync/config/FreeFileSync/` |
| Logs | `~/.config/FreeFileSync/Logs/` | `.../config/FreeFileSync/Logs/` |
| Desinstalar | `/opt/FreeFileSync/uninstall.sh` | `flatpak uninstall org.freefilesync.FreeFileSync` |

**Jobs (comum às duas):** `~/Documents/FFS/` — hoje `NAS_K8s.ffs_batch` (para
cron) e `NAS_K8s.ffs_gui` (para a GUI). São XML; dá para ler e editar direto com
Read/Edit, o que costuma ser mais rápido e preciso que descrever cliques.

**Os dois arquivos não são a mesma coisa.** Apesar do nome idêntico, em
2026-07-27 eles divergiam na semântica mais perigosa que existe:

| | Direção | Apaga no destino? |
|---|---|---|
| `NAS_K8s.ffs_gui` | `RightOnly="right"` (Mirror) | **Sim** |
| `NAS_K8s.ffs_batch` | `Delete="none"` | Não |

Ou seja: rodar pela GUI espelha com deleção, rodar pelo cron só acrescenta.
Antes de responder qualquer coisa sobre "o que o job faz", **leia o arquivo
específico em questão** — não assuma que um reflete o outro.

**A armadilha:** cada instalação tem `GlobalSettings.xml` e `Logs/` próprios.
Se o cron chama a nativa e o usuário abre a Flatpak, os logs que ele vê na GUI
**não são** os do job agendado. Ao investigar "o sync não rodou", confirme
primeiro qual binário o cron invoca e leia o log daquela instalação.

Para o binário nativo, use `/opt/FreeFileSync/FreeFileSync` (o launcher estático
que o manual oficial documenta), não `/opt/FreeFileSync/Bin/FreeFileSync`. O
`Bin/` é detalhe interno de como o launcher resolve a arquitetura.

## Diagnóstico de erros de permissão

O sintoma mais comum neste host, e o mais enganoso:

```
Cannot create directory "/mnt/NAS_BKP/.../_gsdata_".
EACCES: Permission denied [mkdir]
```

Antes de suspeitar do sandbox do Flatpak ou do NFS, **reproduza fora do app** —
isso separa "problema do FreeFileSync" de "problema do filesystem" em um comando:

```bash
mkdir /caminho/que/falhou/__teste__ && rmdir /caminho/que/falhou/__teste__
```

Se falhar aqui também, o FreeFileSync é só o mensageiro. Siga para
`references/permissoes-ntfs.md` — cobre o caso do atributo READONLY do NTFS, que
já explicou 100% das ocorrências neste host, além de NFS e sandbox do Flatpak.

O atalho, quando o destino é `/mnt/NAS_BKP` (NTFS): diretórios vindos de um
perfil Windows carregam `FILE_ATTRIBUTE_READONLY`, o `ntfs3` honra isso removendo
o bit de escrita, e `chmod u+w` limpa o atributo na origem.

## Automação via cron

O job roda por cron, não por systemd timer. Estado atual do crontab:

```
# 0 */2 * * * /usr/bin/FreeFileSync "/home/kiwel/Documents/FFS/NAS_K8s.ffs_batch"
```

Repare que **está comentado** — se o usuário disser que o sync automático parou,
verifique isso primeiro com `crontab -l`. É a causa mais provável e a mais fácil
de passar batido.

Exit codes (do manual oficial), úteis para wrapper scripts e alertas:

| Código | Significado |
|---|---|
| 0 | Concluído com sucesso |
| 1 | Concluído com avisos |
| 2 | Concluído com erros |
| 3 | Abortado |

Detalhes de agendamento, redirecionamento de log, `@reboot`, dependência de
montagem e o ajuste crítico de `ErrorDialog` para execução desatendida estão em
`references/cron-automacao.md`. Leia antes de mexer no crontab — a config atual
do `NAS_K8s.ffs_batch` tem uma opção que **trava o job esperando input** quando
roda sem interface.

## Otimização e ajuste dos jobs

O job `NAS_K8s` espelha 12 pares de pastas de `/mnt/NAS` (NFS) para
`/mnt/NAS_BKP` (NTFS local), com `Threads="2"` por par e variante de comparação
`TimeAndSize`.

Antes de sugerir mudanças, entenda que os dois lados têm gargalos diferentes:
NFS sofre com latência de rede (paralelismo ajuda), NTFS local sofre com I/O de
metadados (paralelismo demais atrapalha). Consulte
`references/otimizacao.md` para as variantes de comparação, como o FreeFileSync
agrupa threads por dispositivo, versionamento e política de exclusão.

## Referências

Leia sob demanda — não carregue tudo de uma vez:

- `references/permissoes-ntfs.md` — erros EACCES, atributo READONLY do ntfs3,
  NFS e sandbox do Flatpak. **O arquivo mais útil deste skill.**
- `references/cron-automacao.md` — cron, exit codes, logging, execução
  desatendida, dependência de montagem, RealTimeSync.
- `references/otimizacao.md` — variantes de comparação, paralelismo por
  dispositivo, versionamento, filtros e desempenho.

## Contexto do ambiente

Coisas que mudam a resposta certa e não são óbvias olhando só para o app:

- `/mnt/NAS` é **NFS** (`192.168.1.11:/mnt/tank/Kiwel`), montado por **automount
  do systemd** com `x-systemd.mount-timeout=10s` e opção `soft`. Um job que roda
  antes da montagem materializar vê diretórios vazios — o que, num sync com
  deleção habilitada, é destrutivo. Veja a seção de dependência de montagem em
  `references/cron-automacao.md`.
- `/mnt/NAS_BKP` **não é o NAS**, apesar do nome. É armazenamento local NTFS
  montado com `ntfs3`, `uid=1000,gid=1000,dmask=0022,acl` — um volume dinâmico
  LDM de 14,6 TB (`/dev/mapper/ldm_vol_PC-Dg0_Volume1`) **distribuído por 4 HDs
  mecânicos** (`sda`–`sdd`, 3,6 TB cada). Perder qualquer um dos quatro
  provavelmente derruba o volume inteiro: LDM spanned não tem redundância. Se a
  conversa virar "confiabilidade do backup", esse é o ponto a levantar.
- A sessão é **Niri/Wayland**. Apps gráficos disparados de contexto não
  interativo (cron, systemd) não têm `DISPLAY`/`WAYLAND_DISPLAY` — mais um motivo
  para o batch nunca depender de diálogo.
- Existe um sistema de backup separado e independente deste (`~/git/synk/`, com
  systemd timers). Não confunda os dois: se a pergunta for sobre dotfiles,
  segredos ou yadm, é a skill `bkp-pcl`, não esta.
