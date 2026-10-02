# Guests — VMs e containers

**Verificado em:** 2026-09-23 para identidade (quem existe, vCPU, RAM provisionada, IP). Uso de RAM e disco ocupado desta página continua o da coleta de 2026-08-17 — não foi remediado.

8 VMs em execução · 17 LXCs em execução · 3 templates parados (VM 1000, VM 2000, CT 115). O CT 107 deixou de ser template: é o OpenBao.

## Alocação agregada

| | vCPU | RAM provisionada |
|---|---|---|
| VMs em execução (8) | 38 | 43.056 MB (~42,0 GiB) |
| LXCs em execução (17) | 25 | 17.664 MB (~17,3 GiB) |
| **Total** | **63** (3,15 : 1 sobre 20 threads) | **~59,3 GiB** |

Uso real de RAM não está nesta soma. A linha antiga (60 vCPU / ~54,8 GiB) era 2026-08-17, com a VM 116 em 2 GB e sem os CTs 107, 113 e 125 na conta.

## VMs (QEMU/KVM)

| VMID | Nome | vCPU | RAM | Uso RAM | Disco boot | IP | SO | onboot | Ordem |
|---|---|---|---|---|---|---|---|---|---|
| **100** | TrueNAS `[critical]` | 4 | 12 GB | 4,34 GiB (36 %) | 32 G | 192.168.1.11 | TrueNAS SCALE (Debian 12, `6.12.15-production+truenas`) | ✅ | **1** |
| **101** | Docker | 6 | 6,05 GB | 4,81 GiB (80 %) | 70,5 G | 192.168.1.40 | Ubuntu 24.04.4 LTS | ✅ | 3 |
| **103** | BackupServer | 4 | 2 GB | 1,79 GiB (90 %) | 32 G | 192.168.1.42 | PBS / Debian 13 (`6.17.2-2-pve`) | ✅ | — |
| **109** | Hassio `[critical]` | 2 | 2 GB | 1,74 GiB (87 %) | 32 G | 192.168.1.47 | Home Assistant OS 17.2 | ✅ | 5 |
| **114** | W11 `[critical]` | **6** | 4 GB | 2,34 GiB (58 %, medição 17/08) | 100 G | 192.168.1.46 | Windows 11 | ✅ | 6 |
| **116** | Jarvis `[critical]` | 4 | 4 GB (balloon 2 GB) | 0,83 GiB (41 %, medição 17/08) | 25,5 G | 192.168.1.6 | Ubuntu 24.04.4 LTS | ✅ | — |
| **124** | Immich | 8 | 8 GB | **7,50 GiB (94 %)** | 49,5 G | 192.168.1.24 | Ubuntu 24.04.3 LTS | ✅ | — |
| **126** | K3s | 4 | 4 GB | 3,54 GiB (88 %) | 15,5 G | 192.168.1.241 | Ubuntu 24.04.4 LTS | ✅ | — |
| 1000 | rockyt **(template)** | 2 | 2 GB (balloon 512) | — | 10 G | — | Rocky Linux, cloud-init | — | — |
| 2000 | ubuntu2204t **(template)** | 1 | 2 GB | — | 3,5 G | — | Ubuntu 22.04, cloud-init | — | — |

> **Balloon:** só a VM 116 tem `balloon` configurado. Nas demais, o campo `mem` de
> `/nodes/*/qemu` reporta `memhost` (memória do host, que só cresce). Use
> `pvesh get /cluster/resources` para o valor real do guest.

### VM 100 — TrueNAS `[critical]`

```ini
agent: 1,fstrim_cloned_disks=1
boot: order=scsi0;net0
cores: 4                        cpu: host
memory: 12288                   machine: pc-q35-7.1
numa: 0                         onboot: 1
startup: order=1,up=0,down=0    ostype: l26
net0: virtio=66:A0:BA:7B:79:51,bridge=vmbr0
scsihw: virtio-scsi-pci
smbios1: uuid=71208f35-2c87-4cec-a96c-36e4b2e46b74
tags: critical

scsi0: Samsung:100/vm-100-disk-0.qcow2,cache=writeback,discard=on,size=32G,ssd=1

# 6 discos físicos em passthrough (by-id, backup=0, ~21,8 TiB brutos)
scsi1: /dev/disk/by-id/ata-HGST_HUS724040ALE641_A11HY4N4        serial=A11HY4N4
scsi2: /dev/disk/by-id/ata-HGST_HUS724040ALE641_RA5G2AGS        serial=RA5G2AGS
scsi3: /dev/disk/by-id/ata-HGST_HUS724040ALE641_PN1334RA5G29OA  serial=PN1334RA5G29OA
scsi4: /dev/disk/by-id/ata-HGST_HUS724040ALE641_A11HY3LN        serial=A11HY3LN
scsi5: /dev/disk/by-id/ata-HGST_HUS724040ALE641_PN1334RA5G2A0Y  serial=PN1334RA5G2A0Y
scsi6: /dev/disk/by-id/ata-HGST_HUS724040ALE641_PN2334RA5G29M6  serial=PN2334RA5G29M6
```

Passthrough é **por disco (`by-id`), não por HBA** — o TrueNAS não vê SMART nativo nem controle
real de energia dos discos. Rede Docker interna: `172.16.0.1`. Falhou no backup de 28/07 com
`qm suspend 100 --skiplock` exit 4.

### VM 101 — Docker

```ini
agent: 1        cores: 6        cpu: host       memory: 6192
machine: q35    numa: 0         onboot: 1       startup: order=3,up=20,down=0
scsi0: Samsung:101/vm-101-disk-0.qcow2,discard=on,iothread=1,size=72192M,ssd=1
scsihw: virtio-scsi-single
net0: virtio=BC:24:11:BC:28:90,bridge=vmbr0
ciuser: kiwel   ipconfig0: ip=dhcp      nameserver: 192.168.1.1
```

Melhor config de I/O do parque (`virtio-scsi-single` + `iothread` + `discard`).
Rede Docker interna `192.168.128.1`. Tráfego acumulado 12,8 GB in / 46,7 GB out.

### VM 103 — BackupServer (Proxmox Backup Server)

```ini
agent: 1,fstrim_cloned_disks=1   cores: 4      cpu: host    memory: 2048
numa: 0                          onboot: 1
net0: virtio=EA:A2:EA:42:EB:8B,bridge=vmbr0,firewall=1
scsi0: Samsung:103/vm-103-disk-0.qcow2,cache=writeback,discard=on,size=32G,ssd=1
scsi1: /dev/disk/by-id/ata-ST1000LM024_HN-M101MBB_S32HJ9CG901518,backup=0,size=976762584K
scsihw: virtio-scsi-pci
```

**O HDD de 1 TB (`sdb`) passado em bloco hospeda o datastore PBS `Bkp1tb`** — ou seja, o storage
de backup do próprio Proxmox roda dentro desta VM. Sem `startup: order`. 90 % da RAM em uso com
apenas 2 GB.

### VM 109 — Hassio (Home Assistant OS) `[critical]`

```ini
agent: 1        bios: ovmf      machine: q35    cores: 2
cpu: host,flags=+pdpe1gb;+aes                   memory: 2048
onboot: 1       startup: order=5,up=30,down=0   tags: critical
efidisk0: Samsung:109/vm-109-disk-1.qcow2,efitype=4m,ms-cert=2023k,pre-enrolled-keys=1,size=528K
scsi0: Samsung:109/vm-109-disk-0.qcow2,cache=writeback,discard=on,size=32G,ssd=1
net0: virtio=5E:CF:EE:75:07:82,bridge=vmbr0,firewall=1
```

VM mais antiga do parque (`ctime=1651025385`, abril/2022). Rede do supervisor `172.30.32.1`.
Tráfego altíssimo: **127 GB in / 64,7 GB out**.

### VM 114 — Windows 11

```ini
agent: 1        bios: ovmf      ostype: win11   machine: pc-q35-9.2+pve1
cores: 6        cpu: host       memory: 4096    onboot: 1   startup: order=6,up=50
efidisk0: Samsung:114/vm-114-disk-1.qcow2,efitype=4m,ms-cert=2023k,pre-enrolled-keys=1,size=528K
tpmstate0: Samsung:114/vm-114-disk-2.raw,size=4M,version=v2.0     # TPM 2.0
scsi0: Samsung:114/vm-114-disk-0.qcow2,cache=writeback,discard=on,iothread=1,size=100G,ssd=1
scsihw: virtio-scsi-single
boot: order=scsi0
net0: virtio=E6:7E:44:5D:C1:3B,bridge=vmbr0,firewall=1
```

**vCPUs: 6.** Disco migrado para **VirtIO SCSI + `iothread`** em 2026-08-17 (issue #10 resolvida).
Maior consumidora de disco (74 GB).
**Tráfego de rede extraordinário: 2,64 TB in / 2,65 TB out** — origem não
investigada. Em 2026-09-23 o guest agent respondeu IPv4 `192.168.1.46`. A NIC não tem mais `firewall=1`. Tag `critical`.

### VM 116 — Jarvis

```ini
agent: 1        cores: 4        memory: 4096    balloon: 2048
machine: q35    numa: 0         onboot: 1       tags: critical
# SEM startup order
# SEM cpu: host — usa kvm64, perde flags de CPU
scsi0: Samsung:116/vm-116-disk-0.raw,size=26112M
scsihw: virtio-scsi-pci
net0: virtio=BC:24:11:DC:49:4D,bridge=vmbr0
ciuser: kiwel   ipconfig0: ip=dhcp
```

Única VM com `balloon` explícito.

### VM 124 — Immich

```ini
agent: 1        bios: ovmf      machine: q35    cores: 8
cpu: host       memory: 8192    onboot: 1       numa: 0
efidisk0: Samsung:124/vm-124-disk-1.qcow2,efitype=4m,ms-cert=2023k,pre-enrolled-keys=1,size=528K

hostpci0: 0000:00:02,rombar=0,pcie=1      # iGPU Intel — grupo IOMMU 0, isolado

scsi0: Samsung:124/vm-124-disk-0.raw,size=50688M
scsi1: /dev/disk/by-id/nvme-Netac_NVMe_SSD_1TB_AA210602901000001566,backup=0,discard=on,iothread=1,size=1000204632K,ssd=1
scsihw: virtio-scsi-single
```

**Dois passthroughs:** iGPU (transcode/ML de fotos) + NVMe de 1 TB inteiro (biblioteca).
`rombar=0` + `pcie=1` é a config correta para iGPU em q35 + OVMF. Maior alocação de vCPU do
parque (8 de 20 threads) e RAM a 94 %. Rede Docker interna `172.18.0.1`.

### VM 126 — K3s

```ini
agent: 1        cores: 4        memory: 4096    machine: q35
numa: 0         onboot: 1
# SEM cpu: host — usa kvm64
scsi0: Samsung:126/vm-126-disk-0.raw,size=15872M
ide2: Samsung:126/vm-126-cloudinit.qcow2,media=cdrom,size=4M
scsihw: virtio-scsi-pci
net0: virtio=BC:24:11:89:06:8F,bridge=vmbr0
```

Rede de pods `10.42.0.0/16` (flannel padrão do k3s). Disco de 15,5 GB é apertado para um cluster
com imagens — 11 G já ocupados.

### Templates de VM

| VMID | Nome | vCPU | RAM | Disco | Observação |
|---|---|---|---|---|---|
| 1000 | rockyt | 2 | 2 GB (balloon 512) | 10 G qcow2 | cloud-init completo, `cpu: host` |
| 2000 | ubuntu2204t | 1 | 2 GB | 3,5 G raw | cloud-init, sem `cpu: host` |

Ambos com `ciuser: kiwel`, `ipconfig0: ip=dhcp`, `nameserver: 192.168.1.1` e duas chaves SSH
(uma FIDO `sk-ecdsa` do Termius, uma ECDSA).

## Containers LXC

| CTID | Hostname | Cores | RAM | Swap | Uso RAM | Disco | Disco usado | IP | SO | onboot | Ordem | Priv. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **102** | Stalwart | 2 | 2048 M | 1024 M | 763 M (37 %) | 20 G + 10 G | 3,28 G (17 %) | .13 | Ubuntu 24.04.4 | ✅ | — | unpriv |
| **104** | karakeep | 2 | 2048 M | 512 M | 461 M (22 %) | 10 G | 5,72 G (59 %) | .16 | Debian 13 | ✅ | — | unpriv |
| **105** | vaultwarden `[critical]` | 1 | **128 M** | 128 M | 24 M (19 %) | 5 G | 500 M (10 %) | .17 | Alpine 3.23 | ✅ | **7** | unpriv |
| **106** | gotify | 1 | **128 M** | 128 M | 27 M (21 %) | 10 G | 989 M (10 %) | .21 | Debian 12 | ✅ | — | unpriv |
| **107** | openbao | 1 | 1024 M | 512 M | — | 15 G | — | .14 | Ubuntu | ✅ | — | unpriv |
| **115** | Ubuntu **(template)** | 1 | 1024 M | 512 M | — | 10 G | — | dhcp | Ubuntu | — | — | unpriv |
| **108** | alpine-mariadb | 1 | 256 M | 128 M | 24 M (9 %) | 1 G | 422 M (43 %) | .18 | Alpine 3.23 | ✅ | — | unpriv |
| **110** | Uptime-Kuma | 2 | 1024 M | 512 M | 336 M (33 %) | 18 G | 6,86 G (39 %) | .25 | Ubuntu 24.04.3 | ✅ | — | unpriv |
| **111** | Gitea | 2 | **1536 M** | 512 M | não remediado | 15 G | 2,95 G (20 %) | .34 | Ubuntu 24.04.4 | ✅ | — | unpriv |
| **112** | Web | 1 | 256 M | 256 M | 65 M (25 %) | 8 G | 1,22 G (16 %) | .10 | Ubuntu 24.04.3 | ✅ | — | unpriv |
| **113** | Nexterm | 1 | 1024 M | 512 M | — | 20 G | — | .12 | Ubuntu | ✅ | — | unpriv |
| **117** | nginx (NPM) | 1 | 512 M | 512 M | 115 M (22 %) | 8 G | 2,25 G (29 %) | .23 | Debian 13 | ✅ | **4** | unpriv |
| **118** | Filebrowser | 2 | 1024 M | 512 M | 426 M (42 %) | 20 G | 5,88 G (30 %) | .26 | Ubuntu 24.04.3 | ✅ | — | unpriv |
| **120** | Pangolin | 1 | 512 M | 512 M | 136 M (27 %) | 10 G | 3,11 G (32 %) | .28 | Ubuntu 24.04.3 | ✅ | — | unpriv |
| **121** | Pihole `[critical]` | 2 | 1024 M | 512 M | 184 M (18 %) | 10 G | 2,85 G (29 %) | .9 | Debian 12 | ✅ | **3** | unpriv |
| **122** | Authentik | 2 | 2048 M | 512 M | 913 M (45 %) | 10 G | 5,96 G (61 %) | .22 | Ubuntu 24.04.3 | ✅ | — | **PRIVILEGIADO** |
| **123** | Postgres | 2 | 2048 M | 2048 M | 92 M (4,5 %) | 20 G | 7,31 G (37 %) | .20 | Ubuntu 24.04.4 | ✅ | — | unpriv |
| **125** | vikunja | 1 | 1024 M | 512 M | — | 20 G | — | .19 | Ubuntu (clone 115) | ✅ | — | unpriv |

Todos os LXCs em execução têm IP **estático** (`ip=192.168.1.X/24`, `gw=192.168.1.1`). O template 115 fica em dhcp. O CT 107 é o OpenBao em `192.168.1.14`, não template.
Padrão geral: `features: keyctl=1,nesting=1`, `arch: amd64`, `nameserver: 192.168.1.1`.

### Configs especiais

**CT 102 — Stalwart (e-mail)**
```ini
rootfs: Samsung:102/vm-102-disk-0.raw,replicate=0,size=20G
mp0:    Samsung:102/vm-102-disk-1.raw,mp=/mail,size=10G    # volume dedicado do maildir
```
Tráfego 7,0 GB in / 217 MB out.

**CT 117 — nginx / Nginx Proxy Manager** — passthrough de `/dev/net/tun` (túnel VPN):
```ini
startup: order=4,up=0,down=0        timezone: America/Sao_Paulo
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file
```

**CT 118 — Filebrowser** — bind mount do NAS:
```ini
mp0: /net/192.168.1.11/mnt/tank/Kiwel,mp=/mnt/nas
```
Bind de um caminho autofs/NFS do host. O vzdump exclui `/mnt/nas`, mas o container ainda falhou no
backup de 28/07 (rsync interrompido). Tráfego 537 MB in / **17,5 GB out**.

**CT 122 — Authentik** — ⚠️ privilegiado e sem confinamento:
```ini
features: nesting=1
# SEM "unprivileged: 1"  →  container PRIVILEGIADO
lxc.apparmor.profile: unconfined     # AppArmor desativado
lxc.cap.drop:                        # nenhuma capability removida
lxc.mount.auto: proc:rw sys:rw       # /proc e /sys em leitura-escrita
```
Equivale na prática a root no host — e é o provedor de SSO. Ver `issues.md` #5.

**CT 105 / 106 / 108** — perfis mínimos (128–256 MB) rodando a 9–21 %. Referência de
dimensionamento enxuto.

### Origem via Community Scripts

CTs **104, 105, 106, 108 e 117** têm o cabeçalho HTML dos
[Proxmox VE Helper-Scripts](https://github.com/community-scripts/ProxmoxVE) no `.conf`.

## Consumo por guest no storage `Samsung`

| Guest | Espaço | Guest | Espaço | Guest | Espaço |
|---|---|---|---|---|---|
| 114 W11 | **74 G** | 116 Jarvis | 16 G | 121 Pihole | 4,6 G |
| 124 Immich | **49 G** | 103 BackupServer | 15 G | 117 nginx | 3,8 G |
| 101 Docker | 34 G | 102 Stalwart | 14 G | 120 Pangolin | 3,7 G |
| 100 TrueNAS | 32 G | 126 K3s | 11 G | 111 Gitea | 3,6 G |
| 109 Hassio | 23 G | 123 Postgres | 8,6 G | 112 Web | 2,0 G |
| 118 Filebrowser | 19 G | 104 karakeep | 8,5 G | 2000 (tpl) | 1,8 G |
| 122 Authentik | 8,3 G | 110 Uptime-Kuma | 8,0 G | 107 (tpl) | 1,5 G |
| 106 gotify | 1,5 G | 1000 (tpl) | 1,2 G | 105 vaultwarden | 716 M |
| 108 alpine-mariadb | 335 M | | | | |

## Pressão de memória

**Apertados (> 85 % do teto):** VM 124 Immich 94 % · VM 103 BackupServer 90 % ·
VM 126 K3s 88 % · VM 109 Hassio 87 %.

**Folgados (< 25 %), candidatos a redução:** CT 123 Postgres 4,5 % (~1,5 GB recuperáveis) ·
CT 108 9 % · CT 111 Gitea 12 % (~1,5 GB) · CT 121 Pihole 18 % (~700 MB) · CT 105 19 % ·
CT 106 21 % · CT 104 karakeep 22 % (~1,2 GB) · CT 117 nginx 22 % (~250 MB).

> Em LXC o `memory` é **teto de cgroup, não reserva** — reduzir não devolve RAM ao host
> automaticamente, mas impede que um container consuma folga alheia. Em VM (`balloon`) a redução
> é que efetivamente libera memória.

## Snapshots

**Nenhum guest possuía snapshots em 2026-08-17.** Não recontado em 2026-09-23.
