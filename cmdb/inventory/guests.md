# Guests e host — configuração

**Verificado em:** 2026-09-23, via `qm config` / `pct config`, guest agent (IPv4) e `ss`/`docker ps` dentro dos CTs.
Política de cada item: `inventory/index.md`. Passthrough com serial, SMART e jobs de backup: skill `proxmox-status`.

Todos os LXCs em execução têm IP estático `192.168.1.X/24`, gateway `192.168.1.1`. Login: LXC `root`, VM `kiwel`.

Ordem de boot no host: 1 TrueNAS (100) → 3 Pi-hole (121) e Docker (101, `up=20`) → 4 nginx (117) → 5 Hassio (109, `up=30`) → 6 W11 (114, `up=50`) → 7 Vaultwarden (105). Filebrowser tem `startup: order=8` sem delay. Jarvis sobe com `onboot` e sem ordem.

## Host — Proxmox

- **Papel:** hypervisor de toda a infra. Se cai, cai tudo.
- **Criticidade:** muito crítico. Só reinicia ou muda com autorização e horário marcado.
- **Endereço:** `192.168.1.5/24` em `vmbr0` (`lan0` 2,5 GbE). UI `https://192.168.1.5:8006`. SSH 22. NUT em `0.0.0.0:3493` — o nobreak não é USB passthrough de VM.
- **Plataforma:** PVE 9.2.5, nó único, i5-13500T, 64 GB. Confirme a versão se for atualizar o host; o número é o da skill `proxmox-status` / mapa de setembro.
- **Kuma:** grupo Proxmox, porta `192.168.1.5:8006`; HTTP `proxmox.kiwel.uk`.

## VM 100 — TrueNAS

- **Papel:** NAS. Serviço core de arquivos.
- **Criticidade:** crítico. Tag PVE `critical`. Startup order 1. `onboot`. `cpu: host`.
- **Compute:** 4 vCPU, 12288 MB, sem balloon.
- **Disco:** boot `scsi0` 32 G qcow2 no storage `Samsung`. Seis HDDs de 4 TB em passthrough por `by-id` (`scsi1`–`scsi6`, `backup=0`). O TrueNAS não vê SMART nativo desses discos.
- **Rede:** `192.168.1.11` (`enp6s18`), MAC `66:A0:BA:7B:79:51`. Docker interno `172.16.0.1`.
- **Kuma:** HTTP `http://192.168.1.11/`.
- **Pool:** `tank` é assunto da `truenas-skill`. Boot pool `freenas-boot` degradado é incidente conhecido, não um fato de disco deste inventário.

## VM 101 — Docker

- **Papel:** host Compose. Nenhum serviço crítico de negócio aqui.
- **Criticidade:** médio. `onboot`, startup order 3 `up=20`. `cpu: host`.
- **Compute:** 6 vCPU, 6192 MB.
- **Disco:** `scsi0` 72192 M qcow2, `iothread`, `discard`.
- **Rede:** `192.168.1.40` (`enp6s18`), MAC `BC:24:11:BC:28:90`, cloud-init DHCP. API Docker TCP 2375 com filtro nftables (origem k3s e localhost).
- **Workloads:** `inventory/services.md`.

## CT 102 — Stalwart

- **Papel:** e-mail e calendário para o Jarvis monitorar, organizar e alertar.
- **Criticidade:** média. Pode reiniciar.
- **Compute:** 2 vCPU, 2048 MB, swap 1024 MB, unprivileged, `nesting`.
- **Disco:** rootfs 20 G + `mp0` 10 G em `/mail`.
- **Rede:** `192.168.1.13/24`, MAC `BC:24:11:62:8D:F0`.
- **Docker:** `stalwartlabs/stalwart:v0.16` publica só `192.168.1.13:8080`. Portas 25, 110, 143, 443, 465, 587, 993, 995 e 4190 ficam dentro da rede do container, sem bind no IP do CT. Roundcube `192.168.1.13:8081`, AgenDAV `192.168.1.13:8082`.
- **Kuma:** grupo Stalwart nas três portas; HTTP `mail.kiwel.uk`, `webmail.kiwel.uk`, `calendar.kiwel.uk`.
- **Nota:** em 2026-09-21 o `imapsync` estourou o cgroup. O timer segue desabilitado; o perfil Compose `sync` tem teto de 768 MiB. Não reative o sync por conta desta ficha.

## VM 103 — BackupServer (PBS)

- **Papel:** backup do Proxmox. O datastore `Bkp1tb` está no HDD de 1 TB passado para esta VM (`scsi1`, `backup=0`). O backup mora no mesmo host que protege.
- **Criticidade:** médio. Pode reiniciar fora da janela 02h–04h. Sem `startup` order. `cpu: host`. `firewall=1` na NIC, sem ruleset no cluster.
- **Compute:** 4 vCPU, 2048 MB.
- **Disco:** boot 32 G qcow2 + HDD ~1 TB.
- **Rede:** `192.168.1.42` (`ens18`), MAC `EA:A2:EA:42:EB:8B`.
- **Kuma:** ping `192.168.1.42` (o monitor cita a UI `:8007` na URL).

## CT 104 — karakeep

- **Papel:** guardar links e arquivos para ler depois.
- **Criticidade:** baixa.
- **Compute:** 2 vCPU, 2048 MB, swap 512 MB, unprivileged, Debian.
- **Disco:** rootfs 10 G.
- **Rede:** `192.168.1.16/24`, MAC `BC:24:11:9F:56:E9`.
- **Portas:** app `*:3000`. Meilisearch só em `127.0.0.1:7700`.
- **Kuma:** grupo Karakeep, porta 3000; HTTP `pocket.kiwel.uk` (o monitor de URL aponta para `karakeep.kiwel.uk`).

## CT 105 — vaultwarden

- **Papel:** cofre humano (senhas, tokens, MFA, passkeys). Não é o cofre dos agentes.
- **Criticidade:** crítico. Tag `critical`. Startup order 7. Alpine. Pode reiniciar só com autorização.
- **Compute:** 1 vCPU, 128 MB, swap 128 MB, unprivileged.
- **Disco:** rootfs 5 G.
- **Rede:** `192.168.1.17/24`, MAC `BC:24:11:6F:36:A3`.
- **Porta:** `0.0.0.0:8000`.
- **Estado:** `lock: backup` na config. Stop/start falha até `pct unlock 105`. Não destravar sem pedido.
- **Kuma:** grupo Vaultwarden, porta 8000; HTTP `keys.kiwel.uk`.

## CT 106 — gotify

- **Papel:** notificações e alarmes.
- **Criticidade:** média. Downtime curto.
- **Compute:** 1 vCPU, 128 MB, swap 128 MB, unprivileged, Debian.
- **Disco:** rootfs 10 G.
- **Rede:** `192.168.1.21/24`, MAC `BC:24:11:9D:B5:3C`.
- **Porta:** `*:80`.
- **Kuma:** grupo Gotify, porta 80; HTTP `push.kiwel.uk`.

## CT 107 — openbao

- **Papel:** cofre de segredos dos agentes e sistemas. Não é mais template.
- **Criticidade:** alta. Downtime curto — agentes ficam sem credencial.
- **Compute:** 1 vCPU, 1024 MB, swap 512 MB, unprivileged, Ubuntu, `nesting`.
- **Disco:** rootfs 15 G.
- **Rede:** `192.168.1.14/24`, MAC `BC:24:11:53:93:91`.
- **Porta:** `192.168.1.14:8200`. LAN only, sem Pangolin.
- **Kuma:** porta 8200. O `url` desse monitor é `push.kiwel.uk`; ignore, o probe é a porta 8200.

## CT 108 — alpine-mariadb

- **Papel:** MariaDB do site e do Kartrack.
- **Criticidade:** média. Downtime curto.
- **Compute:** 1 vCPU, 256 MB, swap 128 MB, unprivileged, Alpine.
- **Disco:** rootfs 1 G. Apertado para crescer dado.
- **Rede:** `192.168.1.18/24`, MAC `BC:24:11:9B:41:8F`.
- **Porta:** `0.0.0.0:3306`.
- **Kuma:** porta 3306, grupo Site.

## VM 109 — Hassio

- **Papel:** Home Assistant. Automação da casa e coleta de consumo.
- **Criticidade:** crítico. Tag `critical`. Startup order 5 `up=30`. `cpu: host` com flags `pdpe1gb` e `aes`. OVMF.
- **Compute:** 2 vCPU, 2048 MB.
- **Disco:** `scsi0` 32 G qcow2 + efidisk.
- **Rede:** `192.168.1.47`, MAC `5E:CF:EE:75:07:82`, `firewall=1` sem ruleset. Supervisor `172.30.32.1`.
- **Porta:** 8123 (alvo do Kuma; não foi listada por `ss` porque é VM).
- **Kuma:** grupo Home Assistant, porta 8123; HTTP `hass.kiwel.uk`.

## CT 110 — Uptime-Kuma

- **Papel:** checagens de disponibilidade e domínios. A lista está em `monitoring.md`.
- **Criticidade:** alta. Downtime curto.
- **Compute:** 2 vCPU, 1024 MB, swap 512 MB, unprivileged, Ubuntu, `nesting`.
- **Disco:** rootfs 18 G. Dados em `/root/kuma` → `/app/data` do container.
- **Rede:** `192.168.1.25/24`, MAC `BC:24:11:3A:31:6B`.
- **Docker:** `louislam/uptime-kuma:2` em `0.0.0.0:3001`. Há `*:2376` (API Docker do CT), não é o Kuma.
- **Kuma:** grupo Uptime Kuma, porta 3001; HTTP `uptime.kiwel.uk`. `dash.kiwel.uk` está inativo.

## CT 111 — Gitea

- **Papel:** Git interno e CI. Espelho dos repos; o GitHub continua remoto.
- **Criticidade:** baixa.
- **Compute:** 2 vCPU, **1536 MB** (ampliado de 1024 em 2026-09-22), swap 512 MB, unprivileged.
- **Disco:** rootfs 15 G.
- **Rede:** `192.168.1.34/24`, MAC `BC:24:11:ED:55:D5`.
- **Docker:** `gitea` em `:3000` e SSH git em `:222`. MySQL 8 só na rede do Compose. SSH do SO continua na 22.
- **Kuma:** porta 3000. O `url` do monitor é `push.kiwel.uk`; o probe é `.34:3000`.

## CT 112 — Web

- **Papel:** Apache/PHP. `kiwel.uk` e sites sem importância operacional.
- **Criticidade:** baixa.
- **Compute:** 1 vCPU, 256 MB, swap 256 MB, unprivileged. `features: nesting=1` sem keyctl.
- **Disco:** rootfs 8 G.
- **Rede:** `192.168.1.10/24`, MAC `BC:24:11:82:16:06`.
- **Portas:** 80 e 443.
- **Kuma:** grupo Site, porta 80; HTTP `kiwel.uk`.

## CT 113 — Nexterm

- **Papel:** terminal e RDP no browser. Um caminho a mais, não o único.
- **Criticidade:** baixa.
- **Compute:** 1 vCPU, 1024 MB, swap 512 MB, unprivileged, Ubuntu, `nesting`.
- **Disco:** rootfs 20 G.
- **Rede:** `192.168.1.12/24`, MAC `BC:24:11:99:A8:53`.
- **Docker:** `nexterm/aio` em `0.0.0.0:6989`.
- **Kuma:** grupo Nexterm, porta 6989; HTTP `nexterm.kiwel.uk`.

## VM 114 — W11

- **Papel:** Plex e GoodSync (sync para OneDrive e backups de sistemas).
- **Criticidade:** crítico. Tag `critical`. Startup order 6 `up=50`. `cpu: host`. OVMF, TPM 2.0, `ostype: win11`.
- **Compute:** 6 vCPU, 4096 MB.
- **Disco:** `scsi0` 100 G qcow2, VirtIO SCSI + `iothread`.
- **Rede:** `192.168.1.46` (guest agent, interface `Ethernet`), MAC `E6:7E:44:5D:C1:3B`. Sem `firewall=1` na NIC nesta coleta.
- **Porta:** Plex 32400.
- **Kuma:** grupo Plex, porta 32400; HTTP `plex.kiwel.uk`.

## CT 115 — Ubuntu (template)

Parado de propósito. 1 vCPU, 1024 MB, disco 10 G, IP dhcp, `template: 1`. Não é incidente.

## VM 116 — Jarvis

- **Papel:** agentes Hermes, perfis Jarvis (pessoal) e Tiberius (infra), no mesmo host.
- **Criticidade:** crítico. Tag `critical`. `onboot: 1`. Sem startup order. **Sem `cpu: host`** — o tipo efetivo é kvm64.
- **Compute:** 4 vCPU, 4096 MB, balloon 2048 MB.
- **Disco:** `scsi0` 26112 M raw (~25,5 G).
- **Rede:** `192.168.1.6` (`eth0`), MAC `BC:24:11:DC:49:4D`, cloud-init DHCP. Docker interno `172.17.0.1`.
- **Porta:** dashboard Hermes `192.168.1.6:9119` (wiki; não reaberta nesta coleta).
- **Kuma:** grupo Jarvis, ping `192.168.1.6`; HTTP `jarvis.kiwel.uk`.

## CT 117 — nginx (Nginx Proxy Manager)

- **Papel:** proxy reverso da LAN, inclusive o que publica o cluster e os proxies internos.
- **Criticidade:** alta. Startup order 4. Downtime curto. Debian, unprivileged.
- **Compute:** 1 vCPU, 512 MB, swap 512 MB.
- **Disco:** rootfs 8 G.
- **Rede:** `192.168.1.23/24`, MAC `BC:24:11:3C:A7:19`. Passthrough de `/dev/net/tun`.
- **Portas:** 80, 443 e admin **40081** (não é a 81 padrão do NPM). Também `*:3000` no CT — não confundir com o Gitea.
- **Kuma:** grupo Nginx, porta 80; HTTP `nginx.kiwel.uk`.

## CT 118 — Filebrowser

- **Papel:** browser de arquivos em cima do NAS. O dado mora no TrueNAS.
- **Criticidade:** baixa. Startup order 8.
- **Compute:** 2 vCPU, 1024 MB, swap 512 MB, unprivileged, `nesting`.
- **Disco:** rootfs 20 G. Bind `mp0: /net/192.168.1.11/mnt/tank/Kiwel` → `/mnt/nas`.
- **Rede:** `192.168.1.26/24`, MAC `BC:24:11:04:70:B9`.
- **Docker:** `gtstef/filebrowser` em `0.0.0.0:8087`. O CT também escuta `rpcbind` na 111.
- **Kuma:** grupo Filebrowser, porta 8087; HTTP `nas.kiwel.uk`.

## CT 120 — Pangolin

- **Papel:** agente de túnel (`fosrl/newt`). Domínios externos e VPN dependem dele.
- **Criticidade:** crítico. Pode reiniciar se o downtime for bem curto.
- **Compute:** 1 vCPU, 512 MB, swap 512 MB, unprivileged, `nesting`.
- **Disco:** rootfs 10 G.
- **Rede:** `192.168.1.28/24`, MAC `BC:24:11:E3:3C:EA`.
- **Docker:** `newt` com 2112/tcp só dentro da rede do container. O CT escuta `*:2376` (API Docker), não uma porta de app na LAN.
- **Kuma:** grupo Pangolin, ping `192.168.1.28` a cada 300 s; HTTP `pangolin.kiwel.uk` no mesmo intervalo.
- **VPS:** `216.45.53.24` (wiki). Não abrir túnel novo daqui.

## CT 121 — Pihole

- **Papel:** DNS da LAN e adblock. Core de nome local.
- **Criticidade:** crítico. Tag `critical`. Startup order 3. Pode reiniciar só com autorização.
- **Compute:** 2 vCPU, 1024 MB, swap 512 MB, unprivileged, Debian 12.
- **Disco:** rootfs 10 G.
- **Rede:** `192.168.1.9/24`, MAC `BC:24:11:0C:F3:ED`.
- **Portas:** DNS `0.0.0.0:53`, admin `0.0.0.0:8080`, `0.0.0.0:443`.
- **Kuma:** porta 8080 (`/admin/login`).
- **Falha:** o MikroTik (`192.168.1.1`) aponta a LAN para `8.8.8.8` se não alcançar o Pi-hole. A internet segue; os nomes `*.kiwel.home` não.

## CT 122 — Authentik

- **Papel:** SSO. Criticidade de negócio baixa.
- **Superfície:** container **privilegiado**. Sem `unprivileged: 1`, AppArmor `unconfined`, `lxc.cap.drop` vazio, `/proc` e `/sys` rw. Equivale a root no host. Não rebaixar sem pedido e plano.
- **Compute:** 2 vCPU, 2048 MB, swap 512 MB. `features: nesting=1` só.
- **Disco:** rootfs 10 G.
- **Rede:** `192.168.1.22/24`, MAC `BC:24:11:68:C5:E8`.
- **Docker:** server `2025.10.3` em `0.0.0.0:7000`→9000 e `:7443`→9443. Postgres 16 só interno. Worker `root-worker-1`.
- **Kuma:** grupo Authentik, porta 7000; HTTP `auth.kiwel.uk`.

## CT 123 — Postgres

- **Papel:** banco do Horus e do VikunjaX.
- **Criticidade:** média. Downtime curto.
- **Compute:** 2 vCPU, 2048 MB, swap 2048 MB, unprivileged, `nesting`.
- **Disco:** rootfs 20 G.
- **Rede:** `192.168.1.20/24`, MAC `BC:24:11:84:D9:D9`.
- **Porta:** `0.0.0.0:5432`.
- **Kuma:** tipo `postgres`, grupo Horus (parent 140). Sem hostname no registro; o serviço está neste IP.

## VM 124 — Immich

- **Papel:** backup e streaming de fotos e vídeos da família.
- **Criticidade:** crítico. `onboot`. `cpu: host`. OVMF. 8 vCPU é a maior alocação do parque.
- **Compute:** 8 vCPU, 8192 MB.
- **Disco:** boot `scsi0` ~49,5 G raw. `scsi1` NVMe Netac 1 TB inteiro em passthrough (`backup=0`). `hostpci0` é a iGPU Intel (`0000:00:02`, `rombar=0`, `pcie=1`).
- **Rede:** `192.168.1.24` (`enp6s18`), MAC `BC:24:11:85:FA:5F`. Bridge Docker `172.18.0.1`.
- **Porta:** 2283.
- **Kuma:** grupo Immich, porta 2283; HTTP `photos.kiwel.uk`.

## CT 125 — vikunja

- **Papel:** tarefas (VikunjaX, imagem `kiwel/vikunjax:v1.4`). O banco fica no Postgres do CT 123.
- **Criticidade:** baixa. Clone do template 115.
- **Compute:** 1 vCPU, 1024 MB, swap 512 MB, unprivileged, `nesting`.
- **Disco:** rootfs 20 G.
- **Rede:** `192.168.1.19/24`, MAC `BC:24:11:10:08:91`. Searchdomain `kiwel.home`.
- **Docker:** publica `192.168.1.19:3456`.
- **Kuma:** grupo Vikunja, porta 3456; HTTP `task.kiwel.uk`. O `url` do monitor de porta é uma URL do Plex; o probe é `.19:3456`.

## VM 126 — K3s

- **Papel:** cluster Kubernetes. Kartrack, Horus, RomsDB, Kifipe, comprovantes.
- **Criticidade:** alta. Downtime curto. `onboot`. **Sem `cpu: host`.**
- **Compute:** 4 vCPU, 4096 MB.
- **Disco:** `scsi0` 15872 M raw (~15,5 G). Continua justo para imagens.
- **Rede:** `192.168.1.241` (`eth0`), MAC `BC:24:11:89:06:8F`. Pods `10.42.0.0/16` (flannel). Ingress MetalLB no mesmo `192.168.1.241:80` e `:443`. API 6443.
- **Workloads:** `inventory/services.md`.

## Templates de VM

| VMID | Nome | vCPU | RAM | Disco | Notas |
|---|---|---|---|---|---|
| 1000 | rockyt | 2 | 2 GB, balloon 512 | 10 G qcow2 | `cpu: host`, cloud-init, parado |
| 2000 | ubuntu2204t | 1 | 2 GB | 3,5 G raw | sem `cpu: host`, cloud-init, parado |

Os dois têm `ciuser: kiwel` e DHCP. Não clonam segredo para este arquivo.
