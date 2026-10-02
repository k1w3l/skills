# Índice de itens de configuração

**Verificado em:** 2026-09-23 (config de guest, portas publicadas, Docker, k3s e lista do Kuma).
Plataforma do host (PVE 9.2.5, i5-13500T, 64 GB) vem da skill `proxmox-status` e do mapa de 2026-09-17; não foi remedida nesta coleta.

Uso de disco e RAM **ocupados** não estão nesta tabela — são voláteis. A coluna Disco é o tamanho provisionado.

Criticidade e a coluna Mudança são a política do usuário (`~/cmdb.md`), não um palpite. "Autorização" significa não reiniciar nem alterar sem pedido explícito e, no host, com horário marcado.

## Máquinas

| ID | Nome | IP | vCPU | RAM | Disco | Portas de serviço | Criticidade | Mudança |
|---|---|---|---|---|---|---|---|---|
| host | Proxmox | 192.168.1.5 | 14C/20T | 64 GB | Samsung NVMe (dir) | 8006 UI, 22 SSH, 3493 NUT | muito crítico | só com autorização e agendamento |
| 100 | TrueNAS | 192.168.1.11 | 4 | 12 GB | 32 G + 6× HDD 4 TB | 80/443 UI, NFS/SMB | crítico | só com autorização |
| 101 | Docker | 192.168.1.40 | 6 | 6192 MB | 70,5 G | ver `services.md`; API 2375 | médio | livre |
| 102 | Stalwart | 192.168.1.13 | 2 | 2 GB | 20 G + 10 G `/mail` | 8080 admin, 8081 webmail, 8082 calendário | média | livre |
| 103 | BackupServer | 192.168.1.42 | 4 | 2 GB | 32 G + HDD 1 TB PBS | 8007 PBS | médio | livre, fora de 02h–04h |
| 104 | karakeep | 192.168.1.16 | 2 | 2 GB | 10 G | 3000 | baixa | livre |
| 105 | vaultwarden | 192.168.1.17 | 1 | 128 MB | 5 G | 8000 | crítico | com autorização |
| 106 | gotify | 192.168.1.21 | 1 | 128 MB | 10 G | 80 | média | livre, downtime curto |
| 107 | openbao | 192.168.1.14 | 1 | 1 GB | 15 G | 8200 | alta | livre, downtime curto |
| 108 | alpine-mariadb | 192.168.1.18 | 1 | 256 MB | 1 G | 3306 | média | livre, downtime curto |
| 109 | Hassio | 192.168.1.47 | 2 | 2 GB | 32 G | 8123 | crítico | só com autorização |
| 110 | Uptime-Kuma | 192.168.1.25 | 2 | 1 GB | 18 G | 3001 | alta | livre, downtime curto |
| 111 | Gitea | 192.168.1.34 | 2 | 1536 MB | 15 G | 3000 HTTP, 222 SSH | baixa | livre |
| 112 | Web | 192.168.1.10 | 1 | 256 MB | 8 G | 80, 443 | baixa | livre |
| 113 | Nexterm | 192.168.1.12 | 1 | 1 GB | 20 G | 6989 | baixa | livre |
| 114 | W11 | 192.168.1.46 | 6 | 4 GB | 100 G | 32400 Plex | crítico | só com autorização |
| 116 | Jarvis | 192.168.1.6 | 4 | 4 GB (balloon 2 GB) | 25,5 G | 9119 dashboard Hermes | crítico | só com autorização |
| 117 | nginx (NPM) | 192.168.1.23 | 1 | 512 MB | 8 G | 80, 443, 40081 admin | alta | livre, downtime curto |
| 118 | Filebrowser | 192.168.1.26 | 2 | 1 GB | 20 G | 8087 | baixa | livre, downtime curto |
| 120 | Pangolin | 192.168.1.28 | 1 | 512 MB | 10 G | newt (sem porta LAN de app) | crítico | livre, downtime bem curto |
| 121 | Pihole | 192.168.1.9 | 2 | 1 GB | 10 G | 53 DNS, 8080 admin, 443 | crítico | com autorização |
| 122 | Authentik | 192.168.1.22 | 2 | 2 GB | 10 G | 7000 HTTP, 7443 HTTPS | baixa | livre |
| 123 | Postgres | 192.168.1.20 | 2 | 2 GB | 20 G | 5432 | média | livre, downtime curto |
| 124 | Immich | 192.168.1.24 | 8 | 8 GB | 49,5 G + NVMe 1 TB | 2283 | crítico | só com autorização |
| 125 | vikunja | 192.168.1.19 | 1 | 1 GB | 20 G | 3456 | baixa | livre |
| 126 | K3s | 192.168.1.241 | 4 | 4 GB | 15,5 G | 6443 API; Ingress 80/443 | alta | livre, downtime curto |
| pcl | PCL (esta estação) | 192.168.1.7 | — | — | — | GoodSync 33556 (wiki) | — | fora do Proxmox |

Templates parados, de propósito: CT 115 Ubuntu, VM 1000 rockyt, VM 2000 ubuntu2204t.

## O que quebra

Texto de risco do usuário, ligado ao IP real.

| Cai | Efeito |
|---|---|
| Host Proxmox | A infra inteira para. |
| 100 TrueNAS | Some o NAS. Arquivo de rede, binds do Filebrowser e storage CIFS do PVE. |
| 101 Docker | Param os containers da VM. Nada crítico de negócio roda lá hoje (mídia, utilitários, Dockhand, Scanopy). |
| 102 Stalwart | Jarvis deixa de ler/organizar e-mail e de mandar alerta por e-mail. |
| 103 PBS | Backup das VMs/CTs fica parado ou desatualizado. O datastore está no mesmo host. |
| 104 karakeep | Só perde acesso ao que foi salvo para ler depois. |
| 105 Vaultwarden | Dispositivos já logados seguem com cache. Aparelho novo não conecta. |
| 106 Gotify | Alarmes deixam de chegar. |
| 107 OpenBao | Agentes podem ficar sem credencial e as rotinas param. |
| 108 MariaDB | Site web e Kartrack ficam sem banco. |
| 109 Home Assistant | Automações e a coleta de consumo das tomadas param. |
| 110 Uptime Kuma | Perde o monitoramento de sistemas e domínios. O Horus também deixa de ver esses checks. |
| 111 Gitea | Sem push/pull no Git interno. |
| 112 Web | `kiwel.uk` e sites PHP sem importância. |
| 113 Nexterm | Perde um caminho de terminal/RDP. |
| 114 W11 | GoodSync para de atualizar o OneDrive e os syncs; Plex sai do ar. |
| 116 Jarvis | Perfis Jarvis e Tiberius param. Rotinas e automações deles param. |
| 117 nginx | Proxy dos sistemas do Kubernetes e dos proxies internos. Domínios que passam por ele caem. |
| 118 Filebrowser | Perde um acesso web ao NAS. O NAS em si continua. |
| 120 Pangolin | Cai a VPN e os domínios externos deixam de alcançar os serviços. |
| 121 Pi-hole | Internet segue (MikroTik cai para 8.8.8.8). Perde adblock, DNS recursivo e nomes locais. |
| 122 Authentik | Perde SSO em alguns serviços. O container é privilegiado no host. |
| 123 Postgres | Horus e VikunjaX ficam sem banco. |
| 124 Immich | Backup/streaming de fotos e vídeos da família para. |
| 125 Vikunja | Perde a lista de tarefas. O banco está no CT 123. |
| 126 K3s | Param Kartrack, Horus, RomsDB, Kifipe e comprovantes. |

## Fora do Proxmox, vistos pelo Kuma ou pela wiki

| IP / nome | O que é | Fonte |
|---|---|---|
| 192.168.1.1 | Gateway MikroTik. Failover de DNS para 8.8.8.8 se o Pi-hole cair. | Kuma ping + política do Pi-hole |
| 192.168.1.2 | Aparelho "X60" (só ping no Kuma) | Kuma |
| 192.168.1.4 | Switch 2.5G (só ping no Kuma) | Kuma |
| 192.168.1.7 | PCL, estação Omarchy. GoodSync Server em `:33556` | esta coleta de rota + wiki |
| 192.168.1.29 | Alvo velho do Kuma para Kartrack/RomsDB `:5173`. Não é guest. | Kuma |
| 216.45.53.24 | VPS do Pangolin (CrowdSec/Traefik) | wiki `crowdsec-pangolin-vps` |
| 192.168.0.1 / 192.168.3.1 | Roteadores Claro Fibra / Claro 5G (ping) | Kuma |

Rede plana: uma bridge `vmbr0`, sem VLAN. Detalhe de NIC, firewall vazio e MACs de todos os guests em `guests.md` e, para o host, em `proxmox-status` `state/network.md`.

## Dependências que importam na hora de mexer

- Publicação externa: Pangolin (120) na frente, NPM (117) no `80/443` da LAN, Ingress do k3s em `192.168.1.241`.
- Kartrack usa MariaDB (108) e também roda no k3s (126). VikunjaX (125) usa Postgres (123).
- Horus (k3s) usa Postgres (123) e lê Proxmox, Docker, TrueNAS, k3s e Kuma.
- Filebrowser (118) monta `/net/192.168.1.11/mnt/tank/Kiwel` do TrueNAS.
- Agentes no Jarvis (116) leem segredo no OpenBao (107) e e-mail no Stalwart (102).
- Alertas de infra vão para o Gotify (106), publicado em `https://push.kiwel.uk`.
