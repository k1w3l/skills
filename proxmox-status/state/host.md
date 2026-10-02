# Host — hardware, plataforma e sistema

**Verificado em:** 2026-08-17

## Identificação

| | |
|---|---|
| Hostname | `proxmox` / `proxmox.kiwel.home` |
| IP | 192.168.1.5 |
| Versão | Proxmox VE 9.2.5 (`pve-manager/9.2.5/20242970da7fbcef`), `proxmox-ve 9.2.0` |
| Kernel | `7.0.14-6-pve` (PMX, 2026-07-20) · alternativo instalado: `7.0.2-6-pve` |
| Base | Debian 13 "trixie" |
| Boot | UEFI, **Secure Boot desabilitado** |
| Cluster | **Nó único** — `/etc/pve/corosync.conf` não existe, `corosync` inativo |
| Subscrição | Nenhuma. Server ID `B1F18ABBE9F44B8D8A3D03D8C646E8E8` |
| DNS | `192.168.1.1`, search domain `kiwel.home` |
| `datacenter.cfg` | apenas `keyboard: pt-br` |

## Plataforma

| Componente | Especificação |
|---|---|
| Fabricante / Sistema | Micro-Star International (MSI) — MS-7E02 |
| Placa-mãe | **MSI PRO B760M-P DDR4** (MS-7E02) rev 1.0 |
| Serial da placa | `07E0210_O41B076649` |
| BIOS | AMI **1.E0**, 16/06/2025, ROM 32 MB, revisão 5.32 |
| UUID do sistema | `6b3565cb-a7e8-7f19-ae3e-d843aea08a5a` |
| Chipset | Intel B760 |

## CPU

| Item | Valor |
|---|---|
| Modelo | **Intel Core i5-13500T** (Raptor Lake, 13ª geração, TDP 35 W) |
| Topologia | 1 socket · 14 cores (6 P + 8 E) · **20 threads** |
| Clock | 800 MHz – 1600 MHz base (turbo até 4,6 GHz) |
| Cache | L1d 544 KiB · L1i 704 KiB · L2 11,5 MiB · **L3 24 MiB** |
| NUMA | 1 nó (CPUs 0–19) |
| Virtualização | VT-x + VT-d, EPT, VPID, `ept_ad` |
| Microcode | `intel-microcode 3.20251111.1~deb13u1`; módulo `microcode` blacklistado |

Mitigações todas ativas (eIBRS + BHI_DIS_S, SSB por prctl, RFDS, VMscape). Nenhuma
vulnerabilidade em estado "Vulnerable".

**Temperatura ociosa:** package ~34 °C (high 80 °C, crit 100 °C).

## Memória

**64 GB — 4 × 16 GB Kingston DDR4**, sem ECC, dual-rank, dual-channel.

| Slot | Módulo | Nominal | **Real** |
|---|---|---|---|
| Controller0-DIMMA1 | Kingston `KHX3200C15/16G` | 3200 MT/s | **2400 MT/s** |
| Controller0-DIMMA2 | Kingston `KHX3200C15/16G` | 3200 MT/s | **2400 MT/s** |
| Controller1-DIMMB1 | Kingston `KHX3200C15/16G` | 3200 MT/s | **2400 MT/s** |
| Controller1-DIMMB2 | Kingston `KHX3200C15/16G` | 3200 MT/s | **2400 MT/s** |

> Módulos HyperX 3200 CL15 rodando no JEDEC base porque o XMP está desligado no BIOS.
> Habilitar recupera ~33 % de banda sem custo. Ver `issues.md` #9.

**Uso em 2026-08-04:** 62 GiB total · ~39 GiB usados · ~7 GiB livres · ~16 GiB cache ·
~22 GiB disponíveis. **Swap 8 GiB (LVM no SSD BX500), ~156 MiB em uso.**

**Comprometimento:** ~54,8 GiB alocados a guests (40,0 GiB VMs + 14,8 GiB LXCs) = **~88 %** da RAM
física. Uso real somado é bem menor (~33 GiB), mas sem balloon o host não reaproveita a diferença.

## Vídeo

| GPU | Endereço | Driver | Destino |
|---|---|---|---|
| **Intel UHD (AlderLake-S GT1)** `8086:4680` | `0000:00:02.0` | `vfio-pci` | **Passthrough → VM 124** |
| ~~NVIDIA Quadro K600~~ | — | — | **Removida em 2026-08-17** (issue #8) |

`nvidiafb` blacklistado (padrão PVE). Sem GPU dedicada no host — console apenas via SSH/IPMI se necessário.

> Após remoção da K600: UPS carga **6 %** (era 14 %); potência HA mínima **137,9 W** pós-reboot.
> Piso elétrico continua dominado pelos **7 HDDs** + RAM + guests.

## IOMMU

Habilitado por padrão do kernel 7.0 — **não há `intel_iommu=on` no cmdline**:

```
BOOT_IMAGE=/boot/vmlinuz-7.0.14-6-pve root=/dev/mapper/pve-root ro quiet
```

Grupos relevantes:

| Grupo | Dispositivos |
|---|---|
| **0** | **iGPU Intel `00:02.0` — isolada**, por isso o passthrough para a VM 124 é limpo (sem ACS override) |
| 7 | USB xHCI `00:14.0` + PCH Shared SRAM `00:14.2` |
| 9 | SATA AHCI Intel `00:17.0` |
| **16** | Quadro K600 `01:00.0` + seu áudio `01:00.1` |
| 17 | NVMe Silicon Motion (Netac) `02:00.0` |
| 18 | Realtek RTL8111 `04:00.0` |
| 19 | NVMe Samsung `05:00.0` |
| 20 | Realtek RTL8125 `06:00.0` |
| **21** | SATA Marvell 88SE9215 `07:00.0` |

## Controladoras de armazenamento

| Controladora | PCI | Observação |
|---|---|---|
| Intel Raptor Lake SATA AHCI | `0000:00:17.0` | — |
| **Marvell 88SE9215 PCIe 2.0 x1, 4 portas SATA 6 Gb/s** | `0000:07:00.0` | **Gargalo** — x1 Gen2 ≈ 500 MB/s compartilhados entre as 4 portas |
| Samsung NVMe SM981/PM981 | `0000:05:00.0` | storage `Samsung` |
| Silicon Motion SM2263 (Netac) | `0000:02:00.0` | passthrough VM 124 |

## Rede física

| Interface | Controlador | PCI | Driver | Estado |
|---|---|---|---|---|
| `enp6s0` | **Realtek RTL8125 2.5GbE** `10ec:8125` | `0000:06:00.0` | `r8169` (fw `rtl8125b-2_0.0.2`) | **UP — 2500 Mb/s Full** |
| `enp4s0` | Realtek RTL8111/8168 GbE `10ec:8168` | `0000:04:00.0` | `r8169` | DOWN, sem cabo, **ociosa** |

PHY do RTL8125 a 54,5 °C.

## Módulos e blacklists

```ini
# /etc/modprobe.d/zfs.conf
options zfs zfs_arc_max=6707740672     # 6,25 GiB — sem efeito, não há pool ZFS no host

# /etc/modprobe.d/pve-blacklist.conf
blacklist nvidiafb

# /etc/modprobe.d/intel-microcode-blacklist.conf
blacklist microcode
```

## Repositórios APT

| Repositório | Suíte | Estado |
|---|---|---|
| `download.proxmox.com/debian/pve` — `pve-no-subscription` | trixie | ✅ ativo |
| `deb.debian.org/debian` — main, contrib, non-free-firmware | trixie, trixie-updates | ✅ ativo |
| `security.debian.org/debian-security` | trixie-security | ✅ ativo |
| `enterprise.proxmox.com/debian/pve` | trixie | ❌ `.disabled` |
| `enterprise.proxmox.com/debian/ceph-squid` | trixie | ❌ `Enabled: false` |

## Versões de pacotes-chave

| Pacote | Versão |
|---|---|
| `pve-qemu-kvm` | 11.0.2-2 |
| `qemu-server` | 9.2.1 |
| `pve-container` | 6.1.12 |
| `lxc-pve` / `lxcfs` | 7.0.0-2 / 7.0.0-pve1 |
| `zfsutils-linux` | 2.4.3-pve1 |
| `proxmox-backup-client` | 4.2.3-1 |
| `pve-firewall` / `proxmox-firewall` | 6.0.5 / 1.2.3 |
| `pve-edk2-firmware` (OVMF) | 4.2025.05-2 |
| `swtpm` | 0.8.0+pve3 |
| `ksm-control-daemon` | 1.5-1 |
| `smartmontools` | 7.5-pve2 |
| `corosync` | 3.1.10-pve3 (instalado, inativo) |
