# Changelog do ambiente Proxmox

Histórico datado de mudanças reais no ambiente — não da skill em si. Mais recente no topo.
Registre o **motivo**, não só o valor: o valor já está em `state/`.

Formato:

```markdown
## AAAA-MM-DD
- **Escopo (guest/área)** — o que mudou. Motivo: por quê.
```

---

## 2026-09-23
- **Identidade dos guests** — CT 107 é OpenBao (`192.168.1.14`), não template. CT 113 Nexterm em `.12`. VM 114 respondeu o guest agent em `192.168.1.46` e está tag `critical`. VM 116 passou a 4 GB / balloon 2 GB / `onboot`. CT 111 está em 1536 MB. Motivo: o estado de agosto contradizia a coleta ao vivo usada para criar a skill `cmdb`. Uso de RAM da tabela não foi remediado.

## 2026-08-31
- **NUT / backup de config** — `PIPEFN`/`LOCKFN` de `/etc/nut/` → `/run/nut/upssched/`
  (tmpfiles Debian). `pve-config-backup.sh` exclui o pipe/lock. Motivo: o `tar` avisava
  `socket ignored` e o cron virava Gotify 4×/dia; o UPS não tinha falha. `issues.md` #25
  resolvido. `nut-monitor` reiniciado; status `OL`.

## 2026-08-29
- **NUT** — teste rápido automático 4×/dia (`nut-battery-test.timer` 00:15/06:15/
  12:15/18:15 → `/etc/nut/battery-test.sh`). Motivo: Q1 zera load após reboot/USB
  e o banco 50 Ah precisa de exercício curto. Pula se já estiver `OB` (e LB/FSD/CAL).
  Não dispara na instalação (stamp tocado). Próximo slot: 18:15.
- **NUT / 4539** — host down 15:29–16:51 (troca de banco + chave 220 V). USB agora
  `usb 1-9` / `ttyACM0`. Comunicação `OL`. `ups.load` 0 + `output.voltage` 112 V
  após o boot era Q1 congelado (como em 25/08 e 27/08). Teste rápido 17:13:
  load **0 → 48 %**; `output.voltage` do NUT **continua 112 V**. Verdade das
  tomadas HA: **~215 V** (chave 220 V pegou). Banco 2×50 Ah no circuito: sag
  27,6 → 24,0 V em 12 s (antes 22,2 V só com 7 Ah). `nut-monitor` reiniciado em `OL`.

## 2026-08-27
- **NUT** — host desligou 17:22 após troca do cabo USB. Não foi o timer de 25 min.
  USB `1-1` disconnect 17:22:04 → `status read failed` → FSD em 8 s porque o `upsmon`
  ainda tinha estado **calibrating** do teste rápido de 25/08 no mesmo boot.
  `SHUTDOWNCMD` / `shutdown -h +0`. Reboot 17:28, status `OL`.
- **NUT** — teste rápido 17:39 para recapturar load (0 → **45 %**). `nut-monitor`
  reiniciado em `OL` para não deixar CAL preso. Host não desligou.
- **NUT** — **nunca mais desliga o nobreak** (`sdorder=-1`, `allow_killpower=0`,
  killpower desativado). Halt só por timer 25 min ou `LOWBATT`, via
  `pvesh … --command shutdown` (VMs/CTs pelo `pve-guests`). FSD de USB/CAL só loga
  (`ignore-fsd.sh`). `qm shutdown 100` (TrueNAS) voltou **antes** do `pvesh` do nó,
  espera até 180 s (ZFS lento).

## 2026-08-25
- **NUT** — após troca da porta USB (enumerou 22:20 neste boot, `ttyACM0` / `usb-0:1:1.0`).
  Comunicação OK (`OL`, 224 V in, 112 V out, 27,4 V batt). `ups.load: 0` era o Q1 cru
  `(… 000 …)` — o aparelho enviava carga 0. Teste rápido `test.battery.start.quick` (23:35):
  ~12 s em `OB CAL`, load 42–44 %, depois `OL`; Q1 `044`. Host não desligou (ONLINE cancelou
  o timer). Carga em **44 %**: PCL (`sensor.nobreak_mesa_potencia` 282 W) + Proxmox
  (`sensor.servidor_potencia` 107 W) no mesmo 4539 ≈ 389 W. 2×50 Ah VRLA aguardam
  cabo 24 V; até lá só as 2×7 Ah internas.

## 2026-08-24
- **CT 125 vikunja** — clone full do template Ubuntu **CT 115**, IP `192.168.1.19`, 1 vCPU / 1 GB / 20 G, Docker nested. Motivo: app de tarefas self-hosted. Banco no Postgres CT 123 (`vikunja`). LAN `:3456` ao vivo; Pangolin `task.kiwel.uk` pendente.

## 2026-08-19
- **NUT / nobreak** — timer `shutdown_onbatt` de **120 s (2 min) → 1500 s (25 min)** em
  `/etc/nut/upssched.conf`. `LOWBATT` continua imediato; `ONLINE` continua cancelando o timer.
  Motivo: aproveitar a autonomia do TS Shara 4539 (~45 min em ~150 W) em vez de desligar o host
  aos 2 min. `nut-monitor` reiniciado; UPS em `OL`, carga 6 %, bateria 100 %.
- **NUT `shutdown.sh`** — deixa de dar SSH `shutdown` na VM 103 (PBS, `192.168.1.42`).
  Agora desliga primeiro a **VM 100 (TrueNAS)** com `qm shutdown` e espera até 180 s
  (90 s em `LOWBATT`) para o ZFS exportar, depois o host. SSH para o TrueNAS no host
  falha `Host key verification`; por isso o caminho é `qm`, não SSH.

## 2026-08-17
- **Quadro K600 removida** — `lspci` sem NVIDIA; sensor `nouveau` ausente; UPS carga **14 % → 6 %**.
  Potência HA mínima 24 h: **137,9 W** (pós-reboot manutenção). → `host.md`, `issues.md` #8
- **VM 114 (W11)** — disco migrado **`sata0` → `scsi0` VirtIO** com `iothread=1`; `boot: order=scsi0`.
  → `guests.md`, issue #10 resolvida
- **Rede `lan0`/`lan1`** — confirmada operacional após reboot (prep. 05/08). → `network.md`
- **Relatório consumo energia** em
  `/mnt/NAS/Sync/Agentes/Reports/relatorio-consumo-energia-proxmox-2026-08-17.md`

## 2026-08-05
- **Rede — nomes estáveis por MAC (pré-remoção K600)** — criados
  `/etc/systemd/network/10-lan0.link` (MAC `90:de:80:b7:7e:12` → `lan0`, RTL8125)
  e `11-lan1.link` (MAC `d8:43:ae:a0:8a:5a` → `lan1`, RTL8111).
  `/etc/network/interfaces` passou a usar `bridge-ports lan0`; backup em
  `interfaces.bak-*`. `pve-power-tune.sh` atualizado (`enp4s0` → `lan1`).
  Motivo: remover a Quadro K600 sem risco de `enp6s0` mudar de nome e perder SSH.
  **Reboot de validação pendente** (K600 ainda instalada). → `network.md`

- **Energia — passo 1 do plano** — governor `performance` → **`powersave`**, EPP →
  **`balance_power`** em todos os 20 threads; `enp4s0` (RTL8111 sem link) forçada **DOWN**.
  Persistência: `pve-power-tune.service` + `/usr/local/sbin/pve-power-tune.sh` (enable on boot).
  Motivo: checklist de eficiência (meta 152–156 W). Baseline HA antes: 163,5 W.
  `no_turbo=1` mantido. Bridge/`enp6s0` intactos.

## 2026-08-04
- **Disco de sistema migrado** — `/` e swap saíram do HGST HTS725032A7E630 320 GB (HDD) para
  **Crucial CT240BX500SSD1 240 GB** (`sda`). Motivo: eliminar o gargalo de I/O do root/swap no
  HDD 7200 rpm (issue #7). Swap em uso caiu de ~3–5 GiB para ~156 MiB na coleta. → `storage.md`,
  `host.md`, `issues.md` #7
- **VM 114 (W11)** — vCPUs 4 → **6**. Observado em `qm config` durante relatório de eficiência
  energética. → `guests.md`
- **Relatório de eficiência energética** salvo em
  `/mnt/NAS/Sync/Agentes/Reports/relatorio-eficiencia-energetica-proxmox-2026-08-04.md`.
  Potência HA idle ~158 W / pico histórico 254 W; RAPL package ~7 W.

## 2026-07-29
- **Skill `proxmox-status` criada** — estado completo documentado a partir da coleta de
  2026-07-28 23:30. Motivo: evitar redescobrir o parque inteiro por SSH a cada sessão e não
  repetir decisões ruins por desconhecer as armadilhas do ambiente.

## 2026-07-28
- **Jobs de backup desabilitados** (`enabled 0` nos dois, `jobs.cfg` às 23:18). Motivo: a execução
  das 02:00 levou ~10 h, falhou em cascata (VM 100, CT 118, CT 120) e deixou o host lento o dia
  inteiro. Decisão de pausar até redesenhar a estratégia. → `issues.md` #1
- **Locks de backup liberados nos CTs 120 (Pangolin) e 121 (Pihole)** via `pct unlock`. Motivo:
  ficaram travados após a falha do job das 02:00, bloqueando shutdown/start dos containers.
- **`ksmtuned` reconfigurado** — `KSM_THRES_COEF` de 20 % para 30 % (limiar de 12,8 GB → 19,2 GB),
  daemon reiniciado. Motivo: KSM nunca ativava porque a memória livre não chegava a cair abaixo do
  limiar antigo. Após a mudança, KSM ativou e deduplicou ~494 MiB. Backup do config original
  preservado. → `services.md`
- **VM 116 (Jarvis) e VM 100 (TrueNAS) reiniciadas** (~23:14–23:17). Contexto: sessão de
  diagnóstico de memória.

## 2026-07-26
- **Última execução de backup completa** — cobriu todos os guests. As execuções de 27 e 28/07 foram
  parciais.

## 2026-05-15
- **Último backup da VM 103 (BackupServer)** — `vzdump-qemu-103-2026_05_15-03_00_01.vma.zst` em
  `Backup_VMs`. Desde então o job dedicado a ela está desabilitado. → `issues.md` #2

---

### Antes de 2026-07-28

O histórico anterior não foi reconstruído. Datas conhecidas por artefatos:

- **2022-04-26** — VM 109 (Hassio) criada (`ctime=1651025385`). É a VM mais antiga do parque.
- **2025-10-15** — VM 114 (W11) criada (`ctime=1760568242`).
- **2025-10-28** — template VM 1000 (rockyt) criado (`ctime=1761618469`).
- **2025-12-12** — VMs 101 (Docker), 116 (Jarvis), 124 (Immich), 126 (K3s) e template 2000 criados
  (`ctime=1765545438` — mesmo timestamp, provavelmente uma leva de provisionamento).
- Guests removidos em algum momento (só restam backups órfãos): CT 119, CT 125, CT 127, VM 113,
  VM 115, e os IDs 123 e 126 foram reaproveitados trocando de tipo (VM→LXC e CT→VM).
