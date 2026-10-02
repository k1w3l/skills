# Passthrough de hardware e nobreak (NUT)

**Verificado em:** 2026-08-31

## Tabela consolidada de passthrough

| # | Dispositivo | Tipo | Identificador | Destino | Configuração |
|---|---|---|---|---|---|
| 1 | **Intel UHD Graphics** (AlderLake-S GT1) | PCIe / GPU | `0000:00:02.0` (`8086:4680`) | **VM 124 — Immich** | `hostpci0: 0000:00:02,rombar=0,pcie=1` · driver `vfio-pci` · IOMMU grupo 0 (isolado) |
| 2 | **Netac NVMe SSD 1 TB** | Bloco NVMe | `nvme-Netac_NVMe_SSD_1TB_AA210602901000001566` | **VM 124 — Immich** | `scsi1`, `discard=on`, `iothread=1`, `ssd=1`, `backup=0` |
| 3 | **HGST HUS724040ALE641 4 TB ×6** | Bloco SATA | `A11HY4N4`, `RA5G2AGS`, `PN1334RA5G29OA`, `A11HY3LN`, `PN1334RA5G2A0Y`, `PN2334RA5G29M6` | **VM 100 — TrueNAS** | `scsi1`–`scsi6`, `backup=0`, `serial=` preservado |
| 4 | **Seagate ST1000LM024 1 TB** | Bloco SATA | `ata-ST1000LM024_HN-M101MBB_S32HJ9CG901518` | **VM 103 — BackupServer** | `scsi1`, `backup=0` — hospeda o datastore PBS `Bkp1tb` |
| 5 | **`/dev/net/tun`** | Char device | major 10, minor 200 | **CT 117 — nginx/NPM** | `lxc.cgroup2.devices.allow: c 10:200 rwm` + `lxc.mount.entry` |
| 6 | **Bind mount NFS** `/net/192.168.1.11/mnt/tank/Kiwel` | Filesystem | autofs do host | **CT 118 — Filebrowser** | `mp0: …,mp=/mnt/nas` |

**Não há nenhum passthrough USB** (`usb0`…`usbN`) configurado em VM alguma.

### Por que o passthrough da iGPU funciona limpo

O grupo IOMMU 0 contém **apenas** a iGPU — sem ACS override, sem `pcie_acs_override` no cmdline,
sem softdep de vfio em `modprobe.d`. O PVE liga `vfio-pci` ao dispositivo no start da VM 124.
`rombar=0` + `pcie=1` é a combinação correta para iGPU em máquina q35 com OVMF.

Consequência: **enquanto a VM 124 estiver ligada, a iGPU não está disponível para o host.** O
console de vídeo do host usa a Quadro K600.

### Cuidados ao mexer nos discos passados

Os discos vão por `/dev/disk/by-id/...` com `serial=` explícito — isso é o que permite ao ZFS do
TrueNAS identificá-los de forma estável mesmo se a ordem de `/dev/sdX` mudar. **Preserve o
`serial=` ao editar qualquer um desses `scsiN`.** Trocar por `/dev/sdX` quebraria o pool na
primeira mudança de enumeração.

Todos têm `backup=0`, então o vzdump só copia o disco raiz das VMs — correto e proposital.

## Nobreak (UPS) — não é passthrough

> **O nobreak NÃO é passado para nenhuma VM ou container.** É gerenciado **pelo host**, via NUT
> em modo servidor de rede. Se alguém perguntar "qual VM tem a porta USB do nobreak", a resposta
> é: nenhuma. O 4539 alimenta **PCL + Proxmox**. Equipamentos de **rede** (hAP ac2, switch 8p,
> Deco X60, Echo Dot, relógio) estão noutro nobreak, medido por `sensor.smart_plug_8_potencia`
> (HA: “Nobreak Rede”). Esse circuito não entra no NUT.

Dispositivos USB presentes no host (é tudo o que existe no barramento):

```
Bus 001 Device 001: ID 1d6b:0002  Linux Foundation 2.0 root hub
Bus 001 Device 002: ID 0483:5740  STMicroelectronics Virtual COM Port   ← o nobreak
Bus 002 Device 001: ID 1d6b:0003  Linux Foundation 3.0 root hub
```

O nobreak se apresenta como conversor serial STM32 (classe CDC-ACM, driver `cdc_acm`) e aparece
como **`/dev/ttyACM0`**. O NUT fala protocolo serial (`blazer_ser`), não HID USB — por isso passar
como dispositivo USB para uma VM não faria sentido. O acesso é distribuído pela rede: `upsd`
escuta em `0.0.0.0:3493` e qualquer host da LAN pode consultar como cliente NUT.

### Modelo e estado

| Campo | Valor |
|---|---|
| Fabricante / Modelo | **TS Shara** — `TS -222 231016` / `Senoid 18` (TSSHARA 1800) |
| Tipo | Offline / line-interactive |
| Firmware | `V010101058` |
| Conexão | USB → CDC-ACM → **`/dev/ttyACM0`** (`by-id` `usb-STMicroelectronics_STM32_Virtual_ComPort_00000000001A-if00`, path **`usb-0:9:1.0`** neste boot) |
| Driver NUT | `blazer_ser` (v2.8.1, protocolo interno 1.60) |
| **Status (2026-08-29 17:14)** | **`OL` — em rede, comunicação OK** |
| Carga da bateria | 100 % · 26,0 V logo após teste (antes do teste 27,60 V; nominal 24 V) |
| Entrada | 222,0 V @ 60,0 Hz |
| Saída NUT (`output.voltage`) | **112 V** — mentira do Q1. Tomadas HA: **~215 V** (`sensor.nobreak_mesa_voltagem` 214,8 V, `sensor.servidor_voltagem` 214,6 V). Chave **220 V** aplicada. |
| **Carga do nobreak (`ups.load`)** | **48 %** após `test.battery.start.quick` (antes do teste, pós-reboot: **0** / Q1 `QQQ=000`). HA: mesa **276 W** + servidor **114 W** ≈ **390 W**. Banco **2×50 Ah VRLA ligado** (cabo 24 V). No teste de 12 s a bateria sagou 27,6 → **24,0 V** (antes, só internas: 27,6 → 22,2 V). |
| Temperatura | 21,0 °C · Beeper habilitado |

### Configuração NUT

**`/etc/nut/nut.conf`** — `MODE=netserver` (o host é o servidor NUT da LAN)

**`/etc/nut/ups.conf`**
```ini
pollinterval = 1
maxretry = 1
offdelay = 120
ondelay = 240

[shara]
driver = blazer_ser
port = /dev/ttyACM0
desc = "TSSHARA 1800"
sdorder = -1
allow_killpower = 0
synchronous = auto
```

**`/etc/nut/upsd.conf`** — `LISTEN 0.0.0.0 3493`

**`/etc/nut/upsd.users`** — contas `upsadmin` (master, `SET`/`FSD`, `instcmds ALL`) e `upsuser`
(slave). ⚠️ **ambas com a senha padrão `nut`**, e o `upsd` escuta em toda a rede. Ver `issues.md` #17.

**`/etc/nut/upsmon.conf`** (pontos-chave)
```
RUN_AS_USER root
MONITOR shara@localhost 1 upsadmin <senha> master
SHUTDOWNCMD "/etc/nut/ignore-fsd.sh"   # FSD (USB/CAL) NÃO desliga o host nem o UPS
NOTIFYCMD  /usr/sbin/upssched
# POWERDOWNFLAG /etc/killpower  — desativado; flag inerte em /etc/nut/no-killpower
POLLFREQ 4        POLLFREQALERT 2
DEADTIME 24       HOSTSYNC 15
FINALDELAY 5
```

### Política de desligamento

**Só duas condições** chamam halt, e **só do Proxmox** (nunca do nobreak):

1. **25 min em bateria** (`START-TIMER shutdown_onbatt 1500`)
2. **`LOWBATT`**

Comando: primeiro `qm shutdown 100` (TrueNAS) com espera até **180 s** (export ZFS lento; `startup down=0` no guest não dá folga no halt do nó). Depois `pvesh create /nodes/localhost/status --command shutdown` (`/etc/nut/pve-node-shutdown.sh`) — Shutdown do nó na UI: `pve-guests` para o restante das VMs/CTs. **Não** há `/sbin/shutdown` genérico nem `upsdrvctl shutdown` / `load.off` / killpower (`sdorder = -1`, `allow_killpower = 0`).

O nobreak **permanece ligado** para o PCL e o resto da carga.

**`/etc/nut/upssched.conf`** — ONBATT timer 1500 s; ONLINE cancela; LOWBATT → `shutdown_lowbatt`.

`PIPEFN /run/nut/upssched/upssched.pipe` · `LOCKFN /run/nut/upssched/upssched.lock` (tmpfiles Debian `d /run/nut/upssched`). Movidos de `/etc/nut/` em 2026-08-31 para o backup de config não empacotar o socket. Rsync de `/etc` exclui `nut/upssched.pipe` e `.lock`. `issues.md` #25 resolvido.

Arquivos: `shutdown.sh`, `pve-node-shutdown.sh`, `ignore-fsd.sh` (`0755`).

**Pegadinha USB + CAL:** em 27/08/2026 ~17:22 a troca do cabo USB desconectou `usb 1-1`. Em **~8 s** o `upsmon` fez FSD (`Executing automatic power-fail shutdown`) porque o estado ainda era **calibrating** (teste rápido de 25/08 no **mesmo** boot; o daemon não esqueceu o CAL). **Não** foi o timer de 25 min nem o `shutdown.sh`. `SHUTDOWNCMD` desligou o host. Depois do reboot o status voltou `OL` sem CAL. Não desconectar a USB do 4539 com o NUT no ar, sobretudo após `test.battery.*`. Após teste de bateria: **reiniciar `nut-monitor`** com o status já `OL`, para o CAL não ficar preso.

Teste rápido 27/08 17:39 (pós-reboot): `ups.load` 0 → **45 %**, depois `OL`; `nut-monitor` reiniciado. Host não desligou.

**Timer 4×/dia:** `nut-battery-test.timer` → `/etc/nut/battery-test.sh` às **00:15 / 06:15 / 12:15 / 18:15**. `test.battery.start.quick` só se estiver `OL`. Se já estiver em bateria (`OB`), o script sai sem testar (também `LB`/`FSD`/`CAL`/NUT mudo). Após `OL`, reinicia `nut-monitor`. `Persistent=true` (catch-up após downtime; no primeiro enable o stamp foi tocado para não disparar na hora).
