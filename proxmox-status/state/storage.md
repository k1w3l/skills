# Storage — storages PVE, discos físicos e SMART

**Verificado em:** 2026-08-04

## Storages configurados

| Nome | Tipo | Conteúdo | Total | Usado | Livre | % | Estado |
|---|---|---|---|---|---|---|---|
| **Samsung** | `dir` (NVMe local) | rootdir, images, backup, snippets, import, vztmpl | 458 GB | 340 GB | 95 GB | **79 %** | ativo |
| **Bkp1tb** | `pbs` | backup | 916 GB | 167 GB | 703 GB | 18,2 % | ativo |
| **Backup_VMs** | `cifs` | backup | 13,2 TB | 9,8 TB | 3,4 TB | 74,3 % | ativo |
| **ISOS** | `cifs` | iso | 13,2 TB | 9,8 TB | 3,4 TB | 74,3 % | ativo |
| `local` | `dir` | snippets | — | — | — | — | **desabilitado** |
| `local-lvm` | `lvmthin` | rootdir | — | — | — | — | **desabilitado** |

`Backup_VMs` e `ISOS` são shares diferentes do **mesmo volume** do TrueNAS (por isso números
idênticos).

### `/etc/pve/storage.cfg`

```ini
dir: local
    disable
    path /var/lib/vz
    content snippets
    shared 0

lvmthin: local-lvm
    disable
    thinpool data
    vgname pve
    content rootdir

dir: Samsung
    path /mnt/pve/Samsung
    content rootdir,backup,snippets,import,images,vztmpl
    is_mountpoint 1
    nodes proxmox
    shared 0

pbs: Bkp1tb
    datastore Bkp1tb
    server 192.168.1.42            # ← VM 103, hospedada neste mesmo host
    username root@pam
    fingerprint 9c:98:17:81:cc:f1:9d:03:8d:b6:b1:bf:4c:d5:d6:46:20:35:c0:a3:1e:6b:89:fa:c9:a6:d9:0d:a8:5d:1d:b5
    content backup
    prune-backups keep-all=1

cifs: Backup_VMs
    path /mnt/pve/Backup_VMs
    server 192.168.1.11            # TrueNAS
    share Kiwel
    subdir /Backup VMs
    username kiwel
    content backup
    prune-backups keep-all=1

cifs: ISOS
    path /mnt/pve/ISOS
    server 192.168.1.11
    share Kiwel
    subdir /Tools/Ferramentas/ISOS/Proxmox
    username kiwel
    content iso
    prune-backups keep-all=1
```

Montagens CIFS com SMB **3.1.1**, `rsize/wsize = 4 MiB`, modo `soft`, `actimeo=1`.

## Discos físicos (10)

| Dev | Modelo | Tamanho | Tipo | Horas | SMART | Temp | Uso |
|---|---|---|---|---|---|---|---|
| `sda` | **Crucial CT240BX500SSD1** | 240 GB | SSD SATA | 22.022 h | PASSED | 35 °C | **Sistema PVE** (LVM) — migrado do HGST 320 GB |
| `sdb` | ST1000LM024 HN-M101MBB | 1 TB | HDD 5400 rpm 2.5" | 11.709 h | PASSED | 29 °C | **Passthrough → VM 103** |
| `sdc` | HGST HUS724040ALE641 | 4 TB | HDD 7200 rpm 3.5" | 29.874 h | PASSED | 44 °C | **Passthrough → VM 100** |
| `sdd` | HGST HUS724040ALE641 | 4 TB | HDD 7200 rpm 3.5" | 29.357 h | PASSED | 40 °C | **Passthrough → VM 100** |
| `sde` | HGST HUS724040ALE641 | 4 TB | HDD 7200 rpm 3.5" | 30.525 h | PASSED | 42 °C | **Passthrough → VM 100** |
| `sdf` | HGST HUS724040ALE641 | 4 TB | HDD 7200 rpm 3.5" | 30.528 h | PASSED | 40 °C | **Passthrough → VM 100** |
| `sdg` | HGST HUS724040ALE641 | 4 TB | HDD 7200 rpm 3.5" | 30.031 h | PASSED | 36 °C | **Passthrough → VM 100** |
| `sdh` | HGST HUS724040ALE641 | 4 TB | HDD 7200 rpm 3.5" | 21.250 h | PASSED | 39 °C | **Passthrough → VM 100** |
| `nvme1n1` | Samsung 970 EVO Plus 500 GB | 500 GB | NVMe | 16.471 h | PASSED | **56 °C** | **Storage `Samsung`** |
| `nvme0n1` | Netac NVMe SSD 1 TB | 1 TB | NVMe | 39.529 h | PASSED | 40 °C | **Passthrough → VM 124** |

**Nenhum setor realocado em nenhum disco** (`Reallocated_Sector_Ct = 0` em todos).

### Seriais e caminhos `by-id`

| Dev | Serial | `by-id` |
|---|---|---|
| `sda` | `2225E640CCC3` | `ata-CT240BX500SSD1_2225E640CCC3` |
| `sdb` | `S32HJ9CG901518` | `ata-ST1000LM024_HN-M101MBB_S32HJ9CG901518` |
| `sdc` | `PN1334RA5G2A0Y` | `ata-HGST_HUS724040ALE641_PN1334RA5G2A0Y` |
| `sdd` | `PN2334RA5G29M6` | `ata-HGST_HUS724040ALE641_PN2334RA5G29M6` |
| `sde` | `A11HY3LN` | `ata-HGST_HUS724040ALE641_A11HY3LN` |
| `sdf` | `A11HY4N4` | `ata-HGST_HUS724040ALE641_A11HY4N4` |
| `sdg` | `RA5G2AGS` | `ata-HGST_HUS724040ALE641_RA5G2AGS` |
| `sdh` | `PN1334RA5G29OA` | `ata-HGST_HUS724040ALE641_PN1334RA5G29OA` |
| `nvme1n1` | `S4P2NF0M531127M` | `nvme-Samsung_SSD_970_EVO_Plus_500GB_S4P2NF0M531127M_1` |
| `nvme0n1` | `AA210602901000001566` | `nvme-Netac_NVMe_SSD_1TB_AA210602901000001566` |

### Firmwares

`sda` (BX500) · `sdb` 2BA30002 · `sdc`/`sdd`/`sdh` MFAOAB70 · `sde`/`sdf`/`sdg` MJAOA5F0 ·
Samsung 2B2QEXM7 · Netac U0514A0.

### Desgaste dos SSDs

| SSD | Percentage Used | Vida restante | Total escrito |
|---|---|---|---|
| Samsung 970 EVO Plus 500 GB | **31 %** | 69 % | 228 TB (447.213.180 units) |
| Netac NVMe 1 TB | **42 %** | 58 % | 244 TB (477.050.446 units) |

> O campo `wearout` da API PVE é **vida restante** (69 / 58), o inverso do `Percentage Used` do
> smartctl. Não confundir.

## Layout de partições

```
sda (240 GB Crucial BX500)          → sistema Proxmox (ex-HGST 320 GB HDD)
├─sda1  1007K                       (BIOS boot)
├─sda2  1G     vfat                 (ESP / EFI)
└─sda3  222.6G LVM2_member  → VG "pve"
  ├─pve-swap   8G    swap  → [SWAP]       (~156 MiB em uso em 2026-08-04)
  └─pve-root   214.6G ext4 → /

sdb (1 TB)  └─sdb1 ext4             → passthrough VM 103 (datastore PBS)
sdc..sdh (4 TB cada)
            ├─ X1  2G   linux_raid_member
            └─ X2  3.6T zfs_member  → passthrough VM 100 (pool ZFS do TrueNAS)

nvme1n1 (500 GB) └─p1 ext4          → /mnt/pve/Samsung
nvme0n1 (1 TB)   └─p1 ext4          → passthrough VM 124
```

**As partições `zfs_member` / `linux_raid_member` são visíveis no host mas NÃO estão importadas**
— `zpool list` retorna "no pools available" e `/proc/mdstat` está vazio. Estão sob controle
exclusivo do TrueNAS, como deve ser. Nunca importar no host.

`/etc/fstab` só tem raiz, swap e proc — os storages são montados pelo PVE.

## Templates e ISOs

**Templates LXC** (`Samsung:vztmpl`, 380 M total):
- `alpine-3.22-default_20250617_amd64.tar.xz`
- `debian-12-standard_12.12-1_amd64.tar.zst`
- `debian-13-standard_13.1-2_amd64.tar.zst`
- `ubuntu-24.04-standard_24.04-2_amd64.tar.zst`

**ISOs** (`ISOS`, no TrueNAS):
- `Rocky-10.1-x86_64-dvd1.iso`
- `ubuntu-24.04.3-live-server-amd64.iso`
- `virtio-win-0.1.285.iso`

## Diretórios do storage `Samsung`

| Diretório | Uso |
|---|---|
| `images/` | **340 G** (detalhamento por guest em `guests.md`) |
| `template/` | 380 M |
| `dump/`, `import/`, `private/`, `snippets/` | vazios |
| `lost+found/` | 16 K |

## Capacidade

Ponto mais próximo da saturação é o **`Samsung` a 79 %** (95 GB livres). Como é `dir` sobre ext4
com arquivos `raw`/`qcow2`, não há thin provisioning real de storage — somar discos declarados dos
guests é o limite prático. Criar guest novo ou expandir a VM 114 (74 G) / 124 (49 G) exige
conferir espaço antes.
