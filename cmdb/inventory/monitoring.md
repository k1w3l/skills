# Uptime Kuma — monitores

**Verificado em:** 2026-09-23, leitura somente do SQLite `/root/kuma/kuma.db` no CT 110.
**Instância:** CT 110 `Uptime-Kuma`, `192.168.1.25:3001`, imagem `louislam/uptime-kuma:2`.
**Contagem:** 136 monitores, 134 ativos. Horus lê o endpoint Prometheus `/metrics` desta instância; o inventário abaixo é a lista de checks, não o estado up/down do momento.

O campo `url` do Kuma muitas vezes guarda um nome amigável que não é o alvo do probe. Para tipo `port`, `ping` e `postgres`, o alvo real é `hostname` + `port`. A coluna Alvo abaixo já faz essa escolha.

| ID | Nome | Tipo | Alvo | Grupo (parent id) | Ativo | Intervalo |
|---|---|---|---|---|---|---|
| 45 | Agregarr | port | `192.168.1.40:7171` | 91 | sim | 60s |
| 37 | Apache | port | `192.168.1.10:80` | 55 | sim | 60s |
| 121 | Audiomass | group | `—` | — | sim | 60s |
| 122 | Audiomass | port | `192.168.1.40:8084` | 121 | sim | 60s |
| 108 | auth.kiwel.uk | http | `https://auth.kiwel.uk` | 107 | sim | 60s |
| 106 | Authentik | port | `192.168.1.22:7000` | 107 | sim | 60s |
| 107 | Authentik | group | `—` | — | sim | 60s |
| 24 | Bazarr | port | `192.168.1.40:6767` | 91 | sim | 60s |
| 125 | BentoPDF | group | `—` | — | sim | 60s |
| 115 | Bentopdf | port | `192.168.1.40:3005` | 125 | sim | 60s |
| 114 | Bichon | port | `192.168.1.40:15630` | — | sim | 60s |
| 177 | Bytestash | group | `—` | — | sim | 60s |
| 178 | Bytestash | port | `192.168.1.40:5000` | 177 | sim | 60s |
| 170 | calendar.kiwel.uk | http | `https://calendar.kiwel.uk/` | 151 | sim | 60s |
| 136 | Claro 5G | ping | `8.8.8.8` | 141 | sim | 60s |
| 144 | Claro 5G - Router | ping | `192.168.3.1` | 141 | sim | 60s |
| 135 | Claro Fibra | ping | `1.1.1.1` | 141 | sim | 60s |
| 143 | Claro Fibra - Router | ping | `192.168.0.1` | 141 | sim | 60s |
| 147 | Comprovantes | http | `http://comprovantes.kiwel.home` | — | sim | 60s |
| 59 | Copyparty | port | `192.168.1.40:3923` | — | sim | 60s |
| 109 | dash.kiwel.uk | http | `https://dash.kiwel.uk` | 102 | não | 60s |
| 31 | docker.kiwel.uk | http | `https://docker.kiwel.uk/` | 124 | sim | 60s |
| 124 | Dockhand | group | `—` | — | sim | 60s |
| 95 | Dockhand | port | `192.168.1.40:10000` | 124 | sim | 60s |
| 165 | fast-sync.kiwel.uk | http | `https://fast-sync.kiwel.uk` | 163 | sim | 60s |
| 118 | Filebrowser | port | `192.168.1.26:8087` | 58 | sim | 60s |
| 58 | Filebrowser | group | `—` | — | sim | 60s |
| 51 | Flaresolverr | port | `192.168.1.40:8191` | 91 | sim | 60s |
| 60 | Freshrss | group | `—` | — | sim | 60s |
| 61 | Freshrss | port | `192.168.1.40:8089` | 60 | sim | 60s |
| 1 | Fundação | http | `https://fundacao.sicredi.com.br` | 40 | sim | 60s |
| 6 | Fundação Org | http | `https://fundacaosicredi.org.br` | 40 | sim | 60s |
| 176 | Gitea | port | `192.168.1.34:3000` | — | sim | 60s |
| 62 | Gotify | group | `—` | — | sim | 60s |
| 63 | Gotify | port | `192.168.1.21:80` | 62 | sim | 60s |
| 10 | hass.kiwel.uk | http | `https://hass.kiwel.uk/` | 66 | sim | 60s |
| 66 | Home Assistant | group | `—` | — | sim | 60s |
| 67 | Home Assistant | port | `192.168.1.47:8123` | 66 | sim | 60s |
| 140 | Horus | group | `—` | — | sim | 60s |
| 138 | horus.kiwel.home | http | `http://horus.kiwel.home` | 140 | sim | 60s |
| 139 | horus.kiwel.uk | http | `https://horus.kiwel.uk` | 140 | sim | 60s |
| 46 | Huntarr | port | `192.168.1.40:9705` | 91 | sim | 60s |
| 2 | IBPF | http | `https://ibpf.sicredi.com.br` | 40 | sim | 60s |
| 3 | IBPJ | http | `https://ibpj.sicredi.com.br` | 40 | sim | 60s |
| 80 | Immich | group | `—` | — | sim | 60s |
| 84 | Immich | port | `192.168.1.24:2283` | 80 | sim | 60s |
| 148 | Jarvis | ping | `192.168.1.6` | 172 | sim | 60s |
| 172 | Jarvis | group | `—` | — | sim | 60s |
| 173 | jarvis.kiwel.uk | http | `https://jarvis.kiwel.uk/` | 172 | sim | 60s |
| 68 | Karakeep | group | `—` | — | sim | 60s |
| 69 | Karakeep | port | `192.168.1.16:3000` | 68 | sim | 60s |
| 132 | Kartrack | group | `—` | — | sim | 60s |
| 133 | Kartrack | http | `http://kartrack.kiwel.home` | 132 | sim | 60s |
| 134 | kartrack.kiwel.uk | http | `https://kartrack.kiwel.uk/` | 132 | sim | 60s |
| 9 | keys.kiwel.uk | http | `https://keys.kiwel.uk/` | 85 | sim | 60s |
| 183 | Kifipe | http | `http://kifipe.kiwel.home` | 184 | sim | 60s |
| 184 | Kifipe | group | `—` | — | sim | 60s |
| 185 | kifipe.kiwel.uk | http | `https://kifipe.kiwel.uk` | 184 | sim | 60s |
| 38 | kiwel.uk | http | `https://kiwel.uk` | 55 | sim | 60s |
| 103 | Kuma-Mieru | port | `192.168.1.40:3883` | 102 | não | 60s |
| 154 | mail.kiwel.uk | http | `https://mail.kiwel.uk/` | 151 | sim | 60s |
| 36 | Mariadb | port | `192.168.1.18:3306` | 55 | sim | 60s |
| 21 | media.kiwel.uk | http | `https://media.kiwel.uk/` | 78 | sim | 60s |
| 70 | Metube | group | `—` | — | sim | 60s |
| 71 | Metube | port | `192.168.1.40:8081` | 70 | sim | 60s |
| 15 | metube.kiwel.uk | http | `https://metube.kiwel.uk/` | 70 | sim | 60s |
| 180 | Microbin | port | `192.168.1.40:8083` | — | sim | 60s |
| 142 | Mikrotik | ping | `192.168.1.1` | 141 | sim | 60s |
| 7 | Mobi | ping | `sicmobi.sicredi.com.br` | 40 | sim | 60s |
| 8 | Mobi 2 | ping | `sicmobi2.sicredi.com.br` | 40 | sim | 60s |
| 123 | mp3.kiwel.uk | http | `https://mp3.kiwel.uk` | 121 | sim | 60s |
| 12 | nas.kiwel.uk | http | `https://nas.kiwel.uk/` | 58 | sim | 60s |
| 141 | Network | group | `—` | — | sim | 60s |
| 160 | Nexterm | group | `—` | — | sim | 60s |
| 161 | Nexterm | port | `192.168.1.12:6989` | 160 | sim | 60s |
| 162 | nexterm.kiwel.uk | http | `https://nexterm.kiwel.uk/` | 160 | sim | 60s |
| 74 | Nginx | group | `—` | — | sim | 60s |
| 75 | Nginx | port | `192.168.1.23:80` | 74 | sim | 60s |
| 33 | nginx.kiwel.uk | http | `https://nginx.kiwel.uk/` | 74 | sim | 60s |
| 163 | Obsidian-sync | group | `—` | — | sim | 60s |
| 164 | Obsidian-sync | http | `http://192.168.1.40:9000` | 163 | sim | 60s |
| 171 | Open Speed Test | port | `192.168.1.40:30000` | — | sim | 60s |
| 182 | Openbao | port | `192.168.1.14:8200` | — | sim | 60s |
| 181 | Pairdrop | port | `192.168.1.40:3006` | — | sim | 60s |
| 127 | Pangolin | group | `—` | — | sim | 300s |
| 49 | Pangolin | ping | `192.168.1.28` | 127 | sim | 60s |
| 128 | pangolin.kiwel.uk | http | `https://pangolin.kiwel.uk` | 127 | sim | 300s |
| 29 | PBS | ping | `192.168.1.42` | — | sim | 60s |
| 126 | pdf.kiwel.uk | http | `https://pdf.kiwel.uk` | 125 | sim | 60s |
| 11 | photos.kiwel.uk | http | `https://photos.kiwel.uk/` | 80 | sim | 60s |
| 30 | Pihole | port | `192.168.1.9:8080` | — | sim | 60s |
| 96 | Plex | group | `—` | — | sim | 60s |
| 97 | Plex | port | `192.168.1.46:32400` | 96 | sim | 60s |
| 20 | plex.kiwel.uk | http | `https://plex.kiwel.uk/web/index.html#!/` | 96 | sim | 60s |
| 19 | pocket.kiwel.uk | http | `https://karakeep.kiwel.uk/` | 68 | sim | 60s |
| 137 | Postgres | postgres | `—` | 140 | sim | 60s |
| 105 | Profilarr | port | `192.168.1.40:6868` | 91 | sim | 60s |
| 25 | Prowlarr | port | `192.168.1.40:9696` | 91 | sim | 60s |
| 98 | Proxmox | group | `—` | — | sim | 60s |
| 99 | Proxmox | port | `192.168.1.5:8006` | 98 | sim | 60s |
| 28 | proxmox.kiwel.uk | http | `https://proxmox.kiwel.uk` | 98 | sim | 60s |
| 150 | Prunemate | port | `192.168.1.40:7676` | — | sim | 60s |
| 5 | PUFV | http | `https://auniaofazavida.com.br` | 40 | sim | 60s |
| 35 | push.kiwel.uk | http | `https://push.kiwel.uk/` | 62 | sim | 60s |
| 27 | qBittorrent | http | `http://192.168.1.40:8080/` | — | sim | 60s |
| 22 | Radarr | port | `192.168.1.40:7878` | 91 | sim | 60s |
| 157 | RomsDB | group | `—` | — | sim | 60s |
| 158 | RomsDB | http | `http://romsdb.kiwel.home` | 157 | sim | 60s |
| 159 | romsdb.kiwel.uk | http | `https://romsdb.kiwel.uk/` | 157 | sim | 60s |
| 91 | RRs | group | `—` | — | sim | 60s |
| 18 | rss.kiwel.uk | http | `https://rss.kiwel.uk/` | 60 | sim | 60s |
| 26 | Sabnzbd | http | `http://192.168.1.40:8085/sabnzbd/` | — | sim | 60s |
| 116 | Scanopy | port | `192.168.1.40:60072` | — | sim | 60s |
| 78 | Seerr | group | `—` | — | sim | 60s |
| 79 | Seerr | port | `192.168.1.40:5055` | 78 | sim | 60s |
| 40 | Sicredi | group | `—` | — | sim | 60s |
| 156 | Site | http | `https://sicredi.com.br` | 40 | sim | 60s |
| 55 | Site | group | `—` | — | sim | 60s |
| 179 | snip.kiwel.uk | http | `https://snip.kiwel.uk` | 177 | sim | 60s |
| 23 | Sonarr | port | `192.168.1.40:8989` | 91 | sim | 60s |
| 151 | Stalwart | group | `—` | — | sim | 60s |
| 152 | Stalwart | port | `192.168.1.13:8080` | 151 | sim | 60s |
| 169 | Stalwart - Calendar | port | `192.168.1.13:8082` | 151 | sim | 60s |
| 153 | Stalwart - Webmail | port | `192.168.1.13:8081` | 151 | sim | 60s |
| 146 | Switch 2.5G | ping | `192.168.1.4` | 141 | sim | 60s |
| 168 | task.kiwel.uk | http | `https://task.kiwel.uk/` | 174 | sim | 60s |
| 32 | Truenas | http | `http://192.168.1.11/` | — | sim | 60s |
| 102 | Uptime Kuma | group | `—` | — | sim | 60s |
| 90 | Uptime Kuma | port | `192.168.1.25:3001` | 102 | sim | 60s |
| 104 | uptime.kiwel.uk | http | `https://uptime.kiwel.uk` | 102 | sim | 60s |
| 85 | Vaultwarden | group | `—` | — | sim | 60s |
| 86 | Vaultwarden | port | `192.168.1.17:8000` | 85 | sim | 60s |
| 174 | Vikunja | group | `—` | — | sim | 60s |
| 175 | Vikunja | port | `192.168.1.19:3456` | 174 | sim | 60s |
| 155 | webmail.kiwel.uk | http | `https://webmail.kiwel.uk/` | 151 | sim | 60s |
| 145 | X60 | ping | `192.168.1.2` | 141 | sim | 60s |

## Desligados

- **103 Kuma-Mieru** — porta `192.168.1.40:3883`, inativo. Não tratar como incidente.
- **109 dash.kiwel.uk** — HTTP `https://dash.kiwel.uk`, inativo.

## Alvos que não batem com o serviço em produção

Estes checks existem e estão ativos, mas o alvo não é o endpoint que o cluster publica hoje. Não 'corrigir' o Kuma sem pedido explícito; usar o alvo de produção para decidir se o serviço está no ar e tratar o monitor como drift.

- **Kartrack (133)** aponta para `192.168.1.29:5173`. A produção no k3s é o Ingress `kartrack.kiwel.home` / `kartrack.kiwel.uk` em `192.168.1.241:80`. O `.29` não é guest do Proxmox.
- **RomsDB (158)** aponta para `192.168.1.29:5173`. A produção é `romsdb.kiwel.home` / `romsdb.kiwel.uk` em `192.168.1.241:80`.
- **Sabnzbd (26)** é HTTP em `http://192.168.1.40:8085/sabnzbd/`, mas o hostname/porta gravados no monitor são `192.168.1.40:8585`. O container publica `8085`.
- Vários monitores `port` têm `url` de outro serviço (Gitea com URL `push.kiwel.uk`, Vikunja com URL do Plex, OpenBao com URL do Gotify). O probe desses registros é o hostname/porta, não essa URL.

## Grupos

Um `group` não prova que o filho está de pé. O estado de cada check é a linha do filho.

| ID | Grupo |
|---|---|
| 121 | Audiomass |
| 107 | Authentik |
| 125 | BentoPDF |
| 177 | Bytestash |
| 124 | Dockhand |
| 58 | Filebrowser |
| 60 | Freshrss |
| 62 | Gotify |
| 66 | Home Assistant |
| 140 | Horus |
| 80 | Immich |
| 172 | Jarvis |
| 68 | Karakeep |
| 132 | Kartrack |
| 184 | Kifipe |
| 70 | Metube |
| 141 | Network |
| 160 | Nexterm |
| 74 | Nginx |
| 163 | Obsidian-sync |
| 127 | Pangolin |
| 96 | Plex |
| 98 | Proxmox |
| 157 | RomsDB |
| 91 | RRs |
| 78 | Seerr |
| 40 | Sicredi |
| 55 | Site |
| 151 | Stalwart |
| 102 | Uptime Kuma |
| 85 | Vaultwarden |
| 174 | Vikunja |
