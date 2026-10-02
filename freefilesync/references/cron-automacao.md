# Agendamento e execução desatendida

## Índice

- [Estado atual](#estado-atual)
- [Linha de comando](#linha-de-comando)
- [Exit codes](#exit-codes)
- [Preparar o job para rodar sem interface](#preparar-o-job-para-rodar-sem-interface)
- [Dependência de montagem](#dependência-de-montagem)
- [Logging](#logging)
- [Diagnóstico: "o sync agendado não rodou"](#diagnóstico-o-sync-agendado-não-rodou)
- [RealTimeSync](#realtimesync)

## Estado atual

```
# 0 */2 * * * /usr/bin/FreeFileSync "/home/kiwel/Documents/FFS/NAS_K8s.ffs_batch"
```

**A linha está comentada** — o agendamento não está ativo. Sempre confirme com
`crontab -l` antes de investigar qualquer outra hipótese; é a explicação mais
provável para "o backup automático parou" e a mais fácil de não enxergar.

Não existe systemd timer para FreeFileSync neste host. Os timers `nas-backup-sync`,
`dotfiles-sync` e `data-state-sync` pertencem a **outro** sistema (`~/git/synk/`,
skill `bkp-pcl`) e não têm relação com este app.

## Linha de comando

O manual oficial documenta a invocação como caminho do binário + caminho do
`.ffs_batch`:

```bash
/opt/FreeFileSync/FreeFileSync "/home/kiwel/Documents/FFS/NAS_K8s.ffs_batch"
```

Use `/opt/FreeFileSync/FreeFileSync` (launcher estático, o que o manual
documenta). O `/usr/bin/FreeFileSync` é symlink para `/opt/FreeFileSync/Bin/FreeFileSync`
— funciona, mas passa por dentro do detalhe de implementação em vez do ponto de
entrada suportado. Prefira o caminho canônico em automação.

Pela Flatpak, o equivalente é:

```bash
flatpak run org.freefilesync.FreeFileSync "/home/kiwel/Documents/FFS/NAS_K8s.ffs_batch"
```

Rodar Flatpak por cron traz complicação extra (precisa de `DBUS_SESSION_BUS_ADDRESS`
e `XDG_RUNTIME_DIR` no ambiente, que o cron não fornece) e ainda esbarra no
sandbox para chegar em `/mnt`. **Para agendamento, prefira a instalação nativa.**

Aspas nos caminhos são obrigatórias: tanto `~/Documents/FFS/` quanto os pares de
pastas do job contêm nomes com espaço (`Backup Telefone`, `Backup VMs`).

## Exit codes

Do manual oficial:

| Código | Significado |
|---|---|
| 0 | Concluído com sucesso |
| 1 | Concluído com avisos |
| 2 | Concluído com erros |
| 3 | Abortado |

Qualquer coisa diferente de 0 merece atenção. Um wrapper mínimo que notifica em
caso de falha:

```bash
#!/usr/bin/env bash
LOG=~/Documents/FFS/cron.log
/opt/FreeFileSync/FreeFileSync "/home/kiwel/Documents/FFS/NAS_K8s.ffs_batch" >>"$LOG" 2>&1
rc=$?
if [ $rc -ne 0 ]; then
    notify-send -u critical "FreeFileSync" "Job NAS_K8s falhou (exit $rc)"
    echo "$(date -Is) exit=$rc" >>"$LOG"
fi
exit $rc
```

`notify-send` a partir do cron precisa de `DBUS_SESSION_BUS_ADDRESS`. Se a
notificação não aparecer, o log ainda registra — não é motivo para o job falhar.

## Preparar o job para rodar sem interface

O manual é explícito: ao salvar como batch, habilite **Run minimized** e
**Auto-Close**, e configure **Handle errors** como *Ignore errors* ou *Cancel*.

O `NAS_K8s.ffs_batch` atual tem:

```xml
<Batch>
    <ProgressDialog Minimized="true" AutoClose="true"/>
    <ErrorDialog>Show</ErrorDialog>     <!-- PROBLEMA -->
    <PostSyncAction>None</PostSyncAction>
</Batch>
```

`ProgressDialog` está correto, mas **`ErrorDialog=Show` é incompatível com
execução desatendida**: ao primeiro erro o job abre um diálogo e fica esperando
input humano que nunca chega. Sob cron — sem `DISPLAY` numa sessão Wayland — ele
simplesmente trava ou morre sem completar.

Isso não é hipotético. O log `NAS_K8s 2026-07-27 193429.964 [Stopped].html`
mostra a execução morrendo no 4º par (`Games`), logo depois de tocar em arquivos
`_gsdata_` — os mesmos diretórios do erro de permissão do NTFS. Os 8 pares
seguintes (`Backup Telefone`, `Backup VMs`, `Tools`, `Sync`, `PCL`, `Downloads`,
`Temp`, `K8s`) **não chegaram a ser sincronizados**.

É esse o risco real: um erro pontual em um diretório não degrada o backup
parcialmente — ele aborta tudo o que vinha depois, e de forma silenciosa se
ninguém abrir o log. Um `[Stopped]` no nome do arquivo é sempre sinal disso.

Para agendamento, troque para:

```xml
<ErrorDialog>Cancel</ErrorDialog>
```

Ou, se preferir que o job siga adiante e reporte no final em vez de abortar no
primeiro erro:

```xml
<Errors Ignore="true" Retry="2" Delay="5"/>
```

`Retry` merece atenção aqui: a origem é NFS com opção `soft`, então falhas
transitórias de rede voltam como erro de I/O em vez de bloquear. O `Retry="0"`
atual não dá nenhuma chance de recuperação. `Retry="2" Delay="5"` absorve
oscilações curtas sem mascarar problema real.

Edite o XML direto (é mais preciso que descrever cliques), mas lembre que a GUI
sobrescreve o arquivo ao salvar — se o usuário reabrir e salvar o job, as
mudanças manuais se perdem. Avise quando fizer edição manual.

## Dependência de montagem

`/mnt/NAS` é automount do systemd. Um job que dispara antes da montagem
materializar enxerga um **diretório vazio**, não um erro.

Isso é perigoso conforme a direção do job. O `NAS_K8s` hoje está configurado
como espelho sem deleção:

```xml
<Left Create="right" Update="right" Delete="none"/>
<Right Create="none" Update="none" Delete="none"/>
```

Com `Delete="none"`, uma origem vazia não apaga nada no destino — o job só não
faz nada. **Se alguém habilitar deleção, isso vira perda de dados**: origem
vazia + deleção ativa = destino esvaziado. Sinalize esse risco sempre que a
conversa envolver ligar deleção neste job.

Proteção: force a montagem e verifique antes de sincronizar.

```bash
#!/usr/bin/env bash
# dispara o automount e confirma que montou de verdade
ls /mnt/NAS >/dev/null 2>&1
if ! mountpoint -q /mnt/NAS; then
    echo "$(date -Is) /mnt/NAS não montado — abortando" >>~/Documents/FFS/cron.log
    exit 1
fi
# sentinela: um arquivo/pasta que só existe se o conteúdo real estiver visível
[ -d /mnt/NAS/Media ] || { echo "$(date -Is) /mnt/NAS montado mas vazio" >>~/Documents/FFS/cron.log; exit 1; }

/opt/FreeFileSync/FreeFileSync "/home/kiwel/Documents/FFS/NAS_K8s.ffs_batch"
```

O mesmo vale para `/mnt/NAS_BKP` — se o HD não estiver conectado, o ponto de
montagem existe mas está vazio.

Para rodar após o boot, o manual sugere dar folga ao sistema:

```
@reboot sleep 60; /opt/FreeFileSync/FreeFileSync "/home/kiwel/Documents/FFS/NAS_K8s.ffs_batch"
```

## Logging

São dois canais distintos, e confundi-los atrasa o diagnóstico:

**Logs do app (HTML, detalhados, por execução)** — contêm a lista de arquivos,
erros por item e o resumo. É onde está a resposta na maioria dos casos:

```
~/.config/FreeFileSync/Logs/                                    # nativa
~/.var/app/org.freefilesync.FreeFileSync/config/FreeFileSync/Logs/   # flatpak
```

Nomeados `<Job> <data> <hora>.html`, com sufixo `[Stopped]` quando a execução foi
interrompida — sinal direto de que o job não completou. O elemento `<LogFolder/>`
vazio no `.ffs_batch` significa "usar o local padrão"; preencha para centralizar.

Ler um log HTML no terminal:

```bash
# o log mais recente
ls -lat ~/.config/FreeFileSync/Logs/ | head

# só as linhas de erro, sem as tags
sed -e 's/<[^>]*>/ /g' "$(ls -t ~/.config/FreeFileSync/Logs/*.html | head -1)" \
  | grep -iE "error|warning|cannot|denied" | head -40
```

Os logs podem passar de 300 KB (o de 2026-07-26 tem 369 KB) porque listam cada
arquivo processado. Filtre em vez de ler inteiro — jogar o HTML todo no contexto
desperdiça espaço e enterra a informação útil.

**Saída do cron (stdout/stderr)** — captura o que acontece *antes* do app subir:
binário não encontrado, permissão negada, variável de ambiente ausente. Se o job
nem chega a criar log HTML, a resposta está aqui:

```
0 */2 * * * /opt/FreeFileSync/FreeFileSync "/home/kiwel/Documents/FFS/NAS_K8s.ffs_batch" >> /home/kiwel/Documents/FFS/cron.log 2>&1
```

## Diagnóstico: "o sync agendado não rodou"

Nesta ordem, porque vai do mais provável e barato ao mais caro:

1. **`crontab -l`** — a linha está comentada? (é o estado atual conhecido)
2. **O binário existe?** `ls -la /opt/FreeFileSync/FreeFileSync`. Uma
   reinstalação ou remoção pode deixar `/usr/bin/FreeFileSync` como symlink
   quebrado; `which` ignora symlinks quebrados e some com o comando, o que dá a
   falsa impressão de que o app não está instalado.
3. **O cron está rodando?** `systemctl status cronie` (CachyOS usa `cronie`).
4. **Existe log HTML da execução?** Se não, o app nunca subiu — investigue o log
   do cron. Se sim, ele rodou e falhou por dentro — leia o HTML.
5. **Sufixo `[Stopped]` no log?** O job foi interrompido. Verifique
   `ErrorDialog`, e leia o final do HTML para achar o item que travou.
6. **As montagens estavam disponíveis no horário?** `journalctl --since "<hora>"
   -u "mnt-NAS.mount"`.

## RealTimeSync

`RealTimeSync` (`/usr/bin/RealTimeSync`, config `LastRun.ffs_real` em
`~/.config/FreeFileSync/`) monitora pastas e dispara um comando quando algo muda
— alternativa ao cron para sincronização contínua.

Ele expõe `$change_action` e `$change_path` para o comando disparado, o que
permite logar o que mudou:

```bash
echo $change_action $change_path >> ~/Documents/FFS/changes.log
```

Não é usado neste host hoje (existe um `LastRun.ffs_real`, mas nenhum job
`.ffs_real` salvo em `~/Documents/FFS/`). Vale considerar se o usuário pedir sync
contínuo em vez de a cada 2h — mas atenção: monitorar `/mnt/NAS` via NFS é caro e
pouco confiável, porque o `inotify` não enxerga mudanças feitas por outros
clientes do servidor. Para NFS, cron continua sendo a escolha mais previsível.
