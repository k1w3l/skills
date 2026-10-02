# Serviços, agendamentos, notificações e monitoramento

**Verificado em:** 2026-08-29

## Daemons

| Serviço | Estado |
|---|---|
| `pvedaemon`, `pveproxy`, `pvestatd`, `pve-cluster`, `pve-firewall`, `pvescheduler` | ✅ ativos |
| `ksmtuned` | ✅ ativo |
| `nut-server`, `nut-monitor` | ✅ ativos |
| `smartd` | ✅ ativo |
| `pve-power-tune` | ✅ ativo (oneshot, enabled) — governor `powersave` + EPP `balance_power` + `enp4s0` down |
| `corosync` | ⏹ inativo (nó único — correto) |

**Unidades falhadas: nenhuma** (`systemctl --failed` vazio).

## Cron

```cron
# Backup das configurações do PVE — 4× ao dia
0 0,6,12,18 * * *  root  /usr/local/sbin/pve-config-backup.sh

# ZFS (herdados do pacote zfs-linux; sem efeito — não há pool ZFS no host)
24 0 1-7  * *  root  [se domingo] /usr/lib/zfs-linux/trim
24 0 8-14 * *  root  [se domingo] /usr/lib/zfs-linux/scrub

# ext4/xfs scrub
10 3 * * *     root  test -e /run/systemd/system || SERVICE_MODE=1 /sbin/e2scrub_all -A -r
30 3 * * 0     root  test -e /run/systemd/system || SERVICE_MODE=1 e2scrub_all_cron
```

`crontab -l` do root está vazio — tudo vem de `/etc/cron.d/`.

## Timers systemd

| Timer | Frequência | Ativa |
|---|---|---|
| `dpkg-db-backup.timer` | diário 00:00 | backup do banco dpkg |
| `logrotate.timer` | diário ~00:28 | rotação de logs |
| `systemd-tmpfiles-clean.timer` | diário ~04:40 | limpeza de tmp |
| `pve-daily-update.timer` | diário ~05:28 | verificação de atualizações PVE |
| `apt-daily-upgrade.timer` | diário ~06:44 | upgrade APT |
| `man-db.timer` | diário ~06:46 | índice do man |
| `apt-daily.timer` | diário ~07:38 | update APT |
| `xfs_scrub_all.timer` | semanal (dom 03:10) | scrub XFS |
| `e2scrub_all.timer` | semanal (dom 03:10) | scrub ext4 |
| `fstrim.timer` | semanal (segunda) | TRIM dos SSDs |
| **`nut-battery-test.timer`** | **00:15, 06:15, 12:15, 18:15** | teste rápido 4539; pula se já em bateria |

## Notificações

**`/etc/pve/notifications.cfg`**
```ini
gotify: Proxmox
    server https://push.kiwel.uk          # Gotify exposto publicamente (CT 106)

matcher: default-matcher
    comment Route all notifications to gotify
    match-field exact:type=vzdump
    match-field exact:hostname=proxmox
    match-field exact:type=fencing
    match-severity info
    mode any                              # qualquer condição casando dispara
    target Proxmox

sendmail: mail-to-root
    comment Send mails to root@pam's email address
    mailto-user root@pam
    disable true                          # e-mail DESABILITADO
```

O token do Gotify fica em `/etc/pve/priv/notifications.cfg` (não replicado aqui).

**Todas as notificações vão para o Gotify em `https://push.kiwel.uk`.** Notificação por e-mail
está desligada — se o Gotify cair, o usuário fica sem alertas do Proxmox.

## KSM (deduplicação de memória)

Estado em 2026-07-28 23:xx:

```
run: 0                        # ksmtuned desligou — pressão de memória caiu
pages_shared:    53.814
pages_sharing:  126.511       # ≈ 494 MiB ainda deduplicados
pages_unshared: 2.196.689
full_scans: 5
```

**`/etc/ksmtuned.conf`:** `KSM_THRES_COEF=30` (era 20; alterado em 2026-07-28 para ativar KSM com
mais folga — 30 % de 64 GB = 19,2 GB de limiar). Backup do original preservado.

Comportamento a saber: o `ksmtuned` monitora a cada 60 s e **desliga o KSM quando a memória livre
sobe acima do limiar**, mantendo as páginas já mescladas. `run: 0` com `pages_sharing > 0` é
estado normal, não falha.

## Monitoramento externo

Cinco sistemas consomem este Proxmox:

| Sistema | Usuário / Token | Onde roda |
|---|---|---|
| **Horus** (observabilidade própria) | `horus@pve!horus` | `~/git/horus` no PCL |
| **Homarr** (dashboard) | `homarr@pve!homarr` | — |
| **Pulse** | `pulse-monitor@pam` (3 tokens) | inclusive instância remota `pulse-kiwel-uk` |
| **Home Assistant** | `hass@pve!hass` | VM 109 |
| **Uptime-Kuma** | — (checagens de rede) | CT 110 (`192.168.1.25:3001`) |

## Serviços hospedados no parque (visão funcional)

| Função | Onde |
|---|---|
| Armazenamento / NAS | VM 100 TrueNAS |
| Backup | VM 103 PBS |
| Automação residencial | VM 109 Home Assistant |
| Fotos | VM 124 Immich |
| Kubernetes | VM 126 k3s |
| Docker geral | VM 101 |
| Agente pessoal de IA | VM 116 Jarvis |
| Desktop Windows | VM 114 |
| DNS / ad-block | CT 121 Pi-hole |
| SSO / identidade | CT 122 Authentik |
| Gerenciador de senhas | CT 105 Vaultwarden |
| E-mail | CT 102 Stalwart |
| Git | CT 111 Gitea |
| Reverse proxy | CT 117 Nginx Proxy Manager |
| Túnel externo | CT 120 Pangolin |
| Notificações | CT 106 Gotify |
| Monitoramento | CT 110 Uptime-Kuma |
| Arquivos web | CT 118 Filebrowser |
| Bookmarks | CT 104 karakeep |
| Bancos de dados | CT 123 PostgreSQL · CT 108 MariaDB |
| Site | CT 112 Web |
