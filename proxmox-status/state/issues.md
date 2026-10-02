# Pendências abertas

**Verificado em:** 2026-08-31

Lista rastreada de problemas e melhorias identificados. Os números são estáveis — outros arquivos
de estado referenciam `issues.md #N`. Ao resolver uma pendência, mude o status para
`✅ resolvido em AAAA-MM-DD` (não apague a linha) e registre no `CHANGELOG.md`. Ao descobrir algo
novo, use o próximo número livre.

| Status | Significado |
|---|---|
| 🔴 | aberto, prioridade alta |
| 🟠 | aberto, prioridade média |
| 🟡 | aberto, prioridade baixa |
| ✅ | resolvido |

---

## Prioridade alta

### 🟠 #1 — Job de backup da VM 103 ainda desabilitado
Job 1 (`backup-1e855a39`, todos exceto 103) **reativado** — última execução 2026-08-28 02:00 OK.
Job 2 (VM 103 dedicado) permanece `enabled 0`.
**Ação:** reativar job 2 com destino `Backup_VMs`.
**Ref:** `backup.md`

### 🔴 #2 — VM 103 sem backup desde 15/05/2026
Está no `exclude` do job 1, e o job 2 (dedicado a ela) está desabilitado. Único dump existente é de
15 de maio, em `Backup_VMs`.
**Ação:** reativar o job 2. O destino precisa ser `Backup_VMs` (CIFS/TrueNAS), **não** `Bkp1tb` —
a VM 103 *é* o `Bkp1tb`.
**Ref:** `backup.md`

### 🔴 #3 — Dependência circular de backup
O datastore PBS `Bkp1tb` roda dentro da VM 103, hospedada neste host, num disco passado para ela.
Perder o host = perder host e backups juntos.
**Ação:** espelhar o datastore para fora (o TrueNAS já é destino CIFS) ou configurar um `sync-job`
do PBS para um alvo externo.
**Ref:** `backup.md`, `passthrough.md`

### 🔴 #4 — Job de backup leva 10 h e falha em cascata
Execução de 28/07: 10 h de duração, com falhas em 100 (`qm suspend` exit 4), 118 (rsync
interrompido) e 120 (locked); travou em 121 e nunca alcançou 122, 123, 124, 126 e templates.
**Ação:** dividir em jobs (críticos diários / resto alternado), avaliar `fleecing`, limitar
bandwidth. A falha da VM 100 precisa de diagnóstico próprio — provável timeout do agent sob I/O
saturado. Relacionado a #7.
**Ref:** `backup.md`

### 🔴 #5 — CT 122 (Authentik) privilegiado e sem confinamento
Privilegiado + `lxc.apparmor.profile: unconfined` + `lxc.cap.drop:` vazio + `proc:rw sys:rw`.
Equivale a root no host — e é o provedor de SSO do parque.
**Ação:** migrar para unprivileged; se alguma dependência exigir, mover o Authentik para uma VM.
**Ref:** `guests.md`

### 🔴 #6 — Tokens de API com Administrator
`@api-users` (horus, homarr) e `@hass-users` têm ACL `Administrator` em `/`, sobrepondo as roles
restritas definidas.
**Ação:** remover esses grupos do ACL `Administrator` e deixar valer as roles. Para o Horus, criar
os dois tokens separados (read / control) que o projeto prevê, e enxugar a role (`Permissions.Modify`,
`User.Modify`, `Realm.Allocate` não têm relação com observabilidade).
**Ref:** `access.md`

---

## Prioridade média

### ✅ #7 — Sistema em HDD de notebook
Resolvido em 2026-08-04: `/` e swap migrados para **Crucial CT240BX500SSD1 240 GB**. Swap em uso
na coleta: ~156 MiB (antes 3–5 GiB).
**Ref:** `storage.md`, `CHANGELOG.md`

### ✅ #8 — Quadro K600 a 84–85 °C com fan em 0 RPM
Resolvido em **2026-08-17**: placa **removida fisicamente**. `lspci` sem NVIDIA; UPS carga caiu
14 % → 6 %; potência HA mínima 137,9 W pós-reboot.
**Ref:** `host.md`, relatório energia 2026-08-17

### 🟠 #9 — RAM a 2400 em vez de 3200 MT/s
Módulos Kingston HyperX 3200 CL15 rodando no JEDEC base porque o XMP está desligado.
**Ação:** habilitar XMP no BIOS. Recupera ~33 % de banda, sem custo.
**Ref:** `host.md`

### ✅ #10 — Disco da VM 114 (W11) em SATA emulado
Resolvido em **2026-08-17**: boot em **`scsi0` VirtIO** com `iothread=1`, `boot: order=scsi0`.
**Ref:** `guests.md`

### 🟠 #11 — Storage `Samsung` a 79 %
95 GB livres de 458 GB. Pouca margem para novos guests ou crescimento da VM 114 (74 G) e 124 (49 G).
**Ação:** podar órfãos (#12) e planejar expansão antes de criar guest novo.
**Ref:** `storage.md`

### 🟠 #12 — Backups órfãos no PBS
Grupos de guests que não existem mais: `ct/119`, `ct/125`, `ct/126`, `ct/127`, `vm/113`, `vm/115`,
`vm/123`.
**Ação:** remover os grupos e rodar GC no PBS.
**Ref:** `backup.md`

### 🟠 #13 — Retenção de apenas 3 cópias
`keep-last=3` = ~3 dias de histórico com backup diário. Há 703 GB livres no PBS.
**Ação:** avaliar `keep-daily=7, keep-weekly=4, keep-monthly=3`.
**Ref:** `backup.md`

### 🟠 #14 — VM 116 (Jarvis) sem `onboot`
Não sobe sozinha após reboot do host.
**Ação:** adicionar `onboot: 1` e um `startup: order` se o agente deve subir automaticamente.
**Ref:** `guests.md`

---

## Prioridade baixa

### 🟡 #15 — `VM.Monitor` nas roles
Privilégio removido no PVE 9, ainda referenciado por `PulseMonitor`, `homarr` e `horus`. Gera
`user config - ignore invalid privilege 'VM.Monitor'` em todo comando `qm`/`pct`/`pvesh`.
**Ação:** editar as três roles e remover o privilégio.
**Ref:** `access.md`

### 🟡 #16 — Firewall ativo sem regras
`pve-firewall` ativo, nenhum ruleset definido. VMs 103, 109 e 114 têm `firewall=1` na NIC, criando
bridges `fwbr*` que não filtram nada.
**Ação:** definir rulesets reais ou remover a flag.
**Ref:** `network.md`

### 🟡 #17 — Senhas padrão no NUT
`upsadmin` e `upsuser` com senha `nut`, e `upsd` escutando em `0.0.0.0:3493`.
**Ação:** trocar as senhas e restringir o `LISTEN` às sub-redes necessárias.
**Ref:** `passthrough.md`

### 🟡 #18 — `rpcbind` em `0.0.0.0:111`
Sem uso aparente de NFS server no host.
**Ação:** avaliar desabilitar.
**Ref:** `network.md`

### 🟡 #19 — VMs 116 e 126 sem `cpu: host`
Usam `kvm64`, perdendo AES-NI e demais extensões.
**Ação:** trocar para `cpu: host`. Ganho gratuito.
**Ref:** `guests.md`

### 🟡 #20 — `enp4s0` (1 GbE) ociosa
Segunda NIC sem cabo, disponível para bond LACP ou rede de storage dedicada.
**Ref:** `network.md`

### 🟡 #21 — HDDs com ~30 mil horas
Os 6 HGST de 4 TB estão entre 21.250 h e 30.528 h. Sem falha em curso (0 setores realocados), mas
na faixa em que a taxa de falha anual sobe.
**Ação:** planejar substituição escalonada.
**Ref:** `storage.md`

### 🟡 #22 — `zfs_arc_max` no host sem efeito
`/etc/modprobe.d/zfs.conf` define 6,25 GiB, mas não há pool ZFS no host. Inócuo, porém pode
confundir diagnóstico futuro.
**Ref:** `host.md`

### 🟡 #23 — Tráfego de rede inexplicado na VM 114 (W11)
2,64 TB in / 2,65 TB out acumulados — desproporcional ao resto do parque, origem não investigada.
**Ação:** investigar o que gera o volume.
**Ref:** `network.md`

### 🟡 #24 — Notificações só pelo Gotify
`sendmail` desabilitado; tudo vai para `https://push.kiwel.uk`. Se o Gotify (CT 106) cair, não há
canal de alerta alternativo.
**Ação:** avaliar reativar o e-mail como fallback.
**Ref:** `services.md`

### ✅ #25 — Alerta Gotify `tar: upssched.pipe: socket ignored` (falso positivo do NUT)
Resolvido em **2026-08-31**: `PIPEFN`/`LOCKFN` em `/run/nut/upssched/`; rsync do
`pve-config-backup.sh` exclui o pipe e o lock; socket antigo removido de `/etc/nut` e do
espelho. `tar` no `current/`: exit 0, stderr vazio. `nut-monitor` reiniciado; UPS `OL`.
**Ref:** `backup.md`, `passthrough.md`
