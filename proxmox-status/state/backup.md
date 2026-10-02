# Backup — jobs, cobertura e histórico

**Verificado em:** 2026-08-31

> ⚠️ **Estado atual: job 1 HABILITADO, job 2 (VM 103) DESABILITADO.** Job 1 reativado após
> 2026-07-28; última execução **2026-08-28 02:00 OK**. Job 2 permanece `enabled 0`.

## Arquitetura — e sua fragilidade

O destino principal é o **PBS `Bkp1tb` em 192.168.1.42**, que é a **VM 103 (BackupServer)**,
hospedada neste mesmo Proxmox, gravando num HDD de 1 TB passado em bloco para ela.

```
Proxmox (192.168.1.5)
  └── VM 103 "BackupServer"  ──passthrough──►  sdb (ST1000LM024 1 TB)
        └── PBS datastore "Bkp1tb"  ◄──── destino dos backups do próprio Proxmox
```

**Consequência:** perder o host físico significa perder o host **e** os backups ao mesmo tempo.
"Restaure do backup" não é saída para falha de hardware do host. Existe um destino secundário
(`Backup_VMs`, CIFS no TrueNAS), mas ele está praticamente sem uso. Ver `issues.md` #3.

## Jobs configurados

**Job 1 — `backup-1e855a39-b2a3`**
```ini
schedule 02:00
all 1                         # todos os guests…
exclude 103                   # …exceto o BackupServer
enabled 1                     # ← REATIVADO (coleta 2026-08-29)
mode snapshot
storage Bkp1tb
prune-backups keep-last=3
fleecing 0
mailnotification always
notification-mode notification-system
notes-template {{guestname}}
node proxmox
```

**Job 2 — `backup-bf54a1d3-0aad`**
```ini
schedule 03:00
vmid 103                      # apenas o BackupServer
enabled 0                     # ← DESABILITADO
mode suspend
compress zstd
storage Bkp1tb
prune-backups keep-last=3
fleecing 0
```

Estado persistido do job 1:
`{"config":{"enabled":"0","schedule":"02:00"},"state":"stopped","msg":"unexpected status"}`

`/etc/vzdump.conf` está vazio (só comentários) — sem bandwidth limit, ionice ou tmpdir globais.

## Última execução — 28/07/2026 02:00 → 12:16 (~10 h)

**Concluídos com sucesso (14):** 101, 102, 104, 105, 106, 107, 108, 109, 110, 111, 112, 114, 116, 117

**Falhas:**

| Guest | Erro |
|---|---|
| **100 TrueNAS** | `command 'qm suspend 100 --skiplock' failed: exit code 4` |
| **118 Filebrowser** | `rsync … failed: interrupted by signal` |
| **120 Pangolin** | `CT is locked (backup)` |
| **121 Pihole** | job travou aqui e não prosseguiu |

**Nunca alcançados nessa execução:** 122, 123, 124, 126, 1000, 2000.

Os locks travados em 120 e 121 foram liberados manualmente em 28/07 (`pct unlock`).

**Diagnóstico:** 10 h de duração para ~22 guests indica contenção severa de I/O — o sistema roda
num HDD 7200 rpm e o storage de origem é o mesmo NVMe para todos os guests. Ver `issues.md` #4 e #7.

## Cobertura por guest (datastore PBS `Bkp1tb`)

| Guest | Último backup | Cópias | Guest | Último backup | Cópias |
|---|---|---|---|---|---|
| 101 Docker | **2026-07-28** | 3 | 100 TrueNAS | 2026-07-26 | 2 |
| 102 Stalwart | **2026-07-28** | 3 | 118 Filebrowser | 2026-07-26 | 2 |
| 104 karakeep | **2026-07-28** | 3 | 120 Pangolin | 2026-07-26 | 2 |
| 105 vaultwarden | **2026-07-28** | 3 | 121 Pihole | 2026-07-26 | 2 |
| 106 gotify | **2026-07-28** | 3 | 122 Authentik | 2026-07-26 | 3 |
| 107 (template) | **2026-07-28** | 3 | 123 Postgres | 2026-07-26 | 3 |
| 108 alpine-mariadb | **2026-07-28** | 3 | 124 Immich | 2026-07-26 | 2 |
| 109 Hassio | **2026-07-28** | 3 | 126 K3s | 2026-07-26 | 3 |
| 110 Uptime-Kuma | **2026-07-28** | 3 | 1000 (template) | 2026-07-26 | 2 |
| 111 Gitea | **2026-07-28** | 3 | 2000 (template) | 2026-07-26 | 2 |
| 112 Web | **2026-07-28** | 3 | | | |
| 114 W11 | **2026-07-28** | 3 | | | |
| 116 Jarvis | **2026-07-28** | 4 | | | |
| 117 nginx | **2026-07-28** | 3 | | | |

**Sem backup no PBS: VM 103 (BackupServer).** Único dump existente está em `Backup_VMs` (CIFS no
TrueNAS): `vzdump-qemu-103-2026_05_15-03_00_01.vma.zst` (5,89 GB), de **15 de maio de 2026**.

## Backups órfãos (guests que não existem mais)

Ocupam espaço e podem ser removidos:

| Grupo | Último backup | Cópias |
|---|---|---|
| `ct/119` | 2026-07-18 | 1 |
| `ct/125` | 2026-07-18 | 1 |
| `ct/126` | 2026-05-17 | 1 (era CT; hoje 126 é VM) |
| `ct/127` | 2026-06-05 | 1 |
| `vm/113` | 2026-07-20 | 1 |
| `vm/115` | 2026-07-20 | 1 |
| `vm/123` | 2026-06-09 | 1 (era VM; hoje 123 é LXC) |

## Retenção

- `prune-backups keep-last=3` nos dois jobs — apenas **3 cópias**, ou seja ~3 dias de histórico com
  backup diário. Sem retenção semanal/mensal.
- Storages `Bkp1tb`, `Backup_VMs` e `ISOS` têm `prune-backups keep-all=1` no nível do storage —
  não podam nada por conta própria.
- Há **703 GB livres** no PBS (18,2 % de uso), então há folga larga para aumentar a retenção.

## Capacidade dos destinos

| Destino | Total | Usado | Livre | % |
|---|---|---|---|---|
| `Bkp1tb` (PBS) | 916 GB | 167 GB | 703 GB | 18,2 % |
| `Backup_VMs` (CIFS/TrueNAS) | 13,2 TB | 9,8 TB | 3,4 TB | 74,3 % |

## Backup das configurações do host

Cron a cada 6 h (00:00, 06:00, 12:00, 18:00):
```
0 0,6,12,18 * * * root /usr/local/sbin/pve-config-backup.sh
```
Destino: `/home/bkp/BKP-Proxmox-Config-*.tar.gz` (retenção 28 tarballs). Restore: `/root/RESTAURACAO.md`.
O NUT precisa de duas permissões extras para restaurar corretamente (ver a memória `bkp-config-proxmox`).

**Alerta Gotify 4×/dia `tar: current/etc/nut/upssched.pipe: socket ignored`:** resolvido em 2026-08-31. `PIPEFN`/`LOCKFN` em `/run/nut/upssched/`; rsync de `/etc` com `--exclude='/nut/upssched.pipe'` e `.lock`. Socket antigo removido do espelho. `tar` de verificação: exit 0, stderr vazio. Ver `issues.md` #25.

## Replicação e HA

- Replicação: `/etc/pve/replication.cfg` vazio.
- HA: `quorum OK`, `fencing standby (CRM watchdog standby)`, sem recursos HA definidos (nó único).
- Nenhum guest possui snapshots.
