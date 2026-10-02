# Serviços dentro das VMs

**Verificado em:** 2026-09-23. Docker via `qm guest exec 101`. Kubernetes via `kubectl get deploy,svc,ingress -A` na VM 126.
O guest em si (CPU, RAM, disco, IP) está em `guests.md`.

## Docker — VM 101 (`192.168.1.40`)

30 containers em execução nesta coleta. Imagem sem tag legível (ID curto) fica em branco na coluna Imagem: o nome do container é o identificador estável.

| Container | Imagem | Porta na LAN | Kuma |
|---|---|---|---|
| agregarr | `agregarr/agregarr:latest` | 7171 | porta 7171, grupo RRs |
| atuin | `ghcr.io/atuinsh/atuin` | 8888 | — |
| atuin-db | `postgres:18` | só rede interna 5432 | — |
| audiomass | `nginx:alpine` | 8084 | porta 8084, grupo Audiomass; HTTP `mp3.kiwel.uk` |
| bazarr | `linuxserver/bazarr` | 6767 | porta 6767, grupo RRs |
| bentopdf | `bentopdf/bentopdf-simple` | 3005 | porta 3005, grupo BentoPDF; HTTP `pdf.kiwel.uk` |
| bichon | (imagem local) | 15630 | porta 15630 |
| bytestash | `ghcr.io/jordan-dalby/bytestash` | 5000 | porta 5000, grupo Bytestash; HTTP `snip.kiwel.uk` |
| copyparty | `copyparty/ac` | 3923 | porta 3923 |
| dockhand | (imagem local) | 10000 | porta 10000, grupo Dockhand; HTTP `docker.kiwel.uk` |
| fast-note-sync-service | `haierkeys/fast-note-sync-service` | 9000 (9001 interno) | HTTP `http://192.168.1.40:9000`, grupo Obsidian-sync; HTTP `fast-sync.kiwel.uk` |
| flaresolverr | `ghcr.io/flaresolverr/flaresolverr` | 8191 | porta 8191, grupo RRs |
| freshrss | `freshrss/freshrss` | 8089 | porta 8089, grupo Freshrss; HTTP `rss.kiwel.uk` |
| freshrss-db | `postgres:16` | só rede interna | — |
| huntarr | `huntarr/huntarr` | 9705 | porta 9705, grupo RRs |
| metube | `ghcr.io/alexta69/metube` | 8081 | porta 8081, grupo Metube; HTTP `metube.kiwel.uk` |
| microbin | `danielszabo99/microbin` | 8083 | porta 8083 |
| openspeedtest | `openspeedtest/latest` | 30000 e 30001 | porta 30000 |
| pairdrop | `linuxserver/pairdrop` | 3006 | porta 3006 |
| profilarr | `santiagosayshey/profilarr` | 6868 | porta 6868, grupo RRs |
| prowlarr | `linuxserver/prowlarr` | 9696 | porta 9696, grupo RRs |
| prunemate | `anoniemerd/prunemate` | 7676 | porta 7676 (o `url` desse monitor é uma CGI do NUT; o probe é `.40:7676`) |
| qbittorrent | `linuxserver/qbittorrent` | 8080 TCP, 6881 TCP/UDP | HTTP `http://192.168.1.40:8080/` |
| radarr | `linuxserver/radarr` | 7878 | porta 7878, grupo RRs |
| sabnzbd | `linuxserver/sabnzbd` | 8085 | HTTP `:8085`; o hostname gravado no monitor diz `:8585` — ver `monitoring.md` |
| scanopy-daemon | `ghcr.io/scanopy/scanopy/daemon` | rede do host, sem publish | — |
| scanopy-db | `postgres:17-alpine` | só rede interna | — |
| scanopy-server | `ghcr.io/scanopy/scanopy/server` | 60072 | porta 60072 |
| seerr | `ghcr.io/seerr-team/seerr` | 5055 | porta 5055, grupo Seerr; HTTP `media.kiwel.uk` |
| sonarr | `linuxserver/sonarr` | 8989 | porta 8989, grupo RRs |

Stacks históricas e YAMLs sanitizados continuam na wiki `docker-operacoes-devops`. Aquela página ainda descreve o snapshot de 19 containers de agosto; a tabela acima é a lista viva de 2026-09-23. Persistência no homelab é bind mount, não volume nomeado.

O grupo Kuma **RRs** (id 91) junta Sonarr, Radarr, Bazarr, Prowlarr, Flaresolverr, Huntarr, Profilarr e Agregarr.

## Kubernetes — VM 126

Cluster de um nó. Ingress Nginx no LoadBalancer `192.168.1.241` (80 e 443). TLS termina fora do cluster; o Ingress é HTTP de propósito.

| Namespace | Deployment | Service | Porta interna | Ingress |
|---|---|---|---|---|
| comprovantes | sistema-comprovante 1/1 | ClusterIP | 8000 | `comprovantes.kiwel.home` |
| horus | horus 1/1 | ClusterIP | 8420 | `horus.kiwel.home`, `horus.kiwel.uk` |
| kartrack | kartrack 1/1 | ClusterIP | 8000 | `kartrack.kiwel.home`, `kartrack.kiwel.uk` |
| kifipe | kifipe 1/1 | ClusterIP | 8000 | `kifipe.kiwel.home`, `kifipe.kiwel.uk` |
| romsdb | romsdb 1/1 | ClusterIP | 80 | `romsdb.kiwel.home`, `romsdb.kiwel.uk` |
| ingress-nginx | controller 1/1 | LoadBalancer 192.168.1.241 | 80, 443 | — |
| kube-system | coredns, local-path-provisioner, metrics-server | ClusterIP | 53, 443 | — |
| metallb-system | controller 1/1 | webhook 443 | — | — |
| nfs-provisioner | nfs-subdir-external-provisioner 1/1 | — | — | — |

Banco do Kartrack: MariaDB CT 108, não um Postgres do cluster. Banco do Horus: Postgres CT 123. Imagem do Kifipe em produção na data da wiki de 2026-09-23: `kiwel/kifipe:v1.1`. Imagem do VikunjaX não está neste cluster — roda no CT 125.

### Kuma desses apps

| App | Check que descreve a produção | Check com alvo velho |
|---|---|---|
| Horus | HTTP `horus.kiwel.home`, `horus.kiwel.uk`; grupo Horus | — |
| Kartrack | HTTP `kartrack.kiwel.uk` | id 133 → `192.168.1.29:5173` |
| Kifipe | HTTP `kifipe.kiwel.home`, `kifipe.kiwel.uk` | — |
| RomsDB | HTTP `romsdb.kiwel.uk` | id 158 → `192.168.1.29:5173` |
| Comprovantes | HTTP `http://comprovantes.kiwel.home` | — |

Jobs antigos `romsdb-reindex` em Error não são Deployment. Não entram como serviço deste inventário.
