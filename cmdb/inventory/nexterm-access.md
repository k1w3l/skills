# Nexterm — validação de acesso às entradas

**Summary**: Snapshot somente leitura da conectividade autenticada das entradas configuradas no Nexterm. Em 2026-09-24, 27 de 28 entradas tiveram sessão/handshake de protocolo via Nexterm confirmados; a entrada SSH `Home Assistant` não foi confirmada em duas tentativas.

**Last updated**: 2026-09-24

---

## Escopo e critério

- CI pai: CT 113 `Nexterm` (`192.168.1.12:6989`), publicado como `http://nexterm.kiwel.home`; versão observada `v1.2.2-BETA`, revisão `d631c47931ed379a9ef66f1623985a768627b4df`.
- O token de API é administrado no OpenBao em `secret/infra/nexterm/api-token`; forma do helper: `openbao-get infra/nexterm api-token`. Valor: `[REDACTED]`.
- A API autenticada respondeu HTTP 200 em `/api/accounts/me` e `/api/entries/list`. Foram enumeradas 28 entradas (IDs 1–29, sem ID 4); cada entrada tinha uma identidade associada e endereço/porta configurados. Protocolos: 27 SSH e 1 RDP.
- HTTP 201 ao criar uma sessão não foi tratado como prova suficiente. A sessão/handshake SSH ou RDP foi considerada confirmada somente quando a sessão Nexterm permaneceu disponível após a janela de conexão (36 s para SSH; 52 s para RDP). Isso confirma estabelecimento autenticado da sessão no Nexterm, não I/O de shell nem saúde da aplicação remota.
- Ao fim de cada tentativa, um DELETE foi enviado quando a sessão ainda estava presente; GET 404 confirmou ausência. Em falha de handshake, a sessão podia desaparecer por si só antes do DELETE. Nenhum comando foi enviado às máquinas, nenhuma entrada/configuração foi alterada e nenhuma interação RDP foi feita. As tentativas ficam registradas no audit log do Nexterm.

## Resultado por entrada — 2026-09-24

| ID | Entrada | Protocolo | Resultado |
|---:|---|---|---|
| 1 | Nexterm | SSH | Sessão/handshake confirmado |
| 2 | W11 | RDP | Sessão/handshake confirmado |
| 3 | Vaultwarden | SSH | Sessão/handshake confirmado |
| 5 | Immich | SSH | Sessão/handshake confirmado |
| 6 | Jarvis | SSH | Sessão/handshake confirmado |
| 7 | Docker | SSH | Sessão/handshake confirmado |
| 8 | Proxmox | SSH | Sessão/handshake confirmado |
| 9 | Postgres | SSH | Sessão/handshake confirmado |
| 10 | Stalwart | SSH | Sessão/handshake confirmado |
| 11 | Mariadb | SSH | Sessão/handshake confirmado |
| 12 | Pangolin - Racknerd | SSH | Sessão/handshake confirmado |
| 13 | Kuma - Racknerd | SSH | Sessão/handshake confirmado |
| 14 | Gitea | SSH | Sessão/handshake confirmado |
| 15 | FilebrowserQ | SSH | Sessão/handshake confirmado |
| 16 | PBS | SSH | Sessão/handshake confirmado |
| 17 | Truenas | SSH | Sessão/handshake confirmado |
| 18 | Nginx | SSH | Sessão/handshake confirmado |
| 19 | Pangolin | SSH | Sessão/handshake confirmado |
| 20 | Uptime-Kuma | SSH | Sessão/handshake confirmado |
| 21 | Authentik | SSH | Sessão/handshake confirmado |
| 22 | Pi-hole | SSH | Sessão/handshake confirmado |
| 23 | Web | SSH | Sessão/handshake confirmado |
| 24 | Home Assistant | SSH | **Não confirmado — `connection_failed` em duas tentativas** |
| 25 | Karakeep | SSH | Sessão/handshake confirmado |
| 26 | Gotify | SSH | Sessão/handshake confirmado |
| 27 | K3s | SSH | Sessão/handshake confirmado |
| 28 | Vikunja | SSH | Sessão/handshake confirmado |
| 29 | Openbao | SSH | Sessão/handshake confirmado |

**Resumo:** 27/28 sessões/handshakes autenticados confirmados: 26 SSH e 1 RDP. A sessão da entrada `Home Assistant` desapareceu durante a janela de conexão em duas tentativas; isso prova apenas que o estabelecimento da sessão SSH via Nexterm não foi confirmado, não que a VM ou o serviço Home Assistant estejam indisponíveis.

## Limpeza e pendência

- Todos os IDs de sessão criados pelos testes foram confirmados ausentes após a tentativa; DELETE foi enviado às sessões que ainda estavam ativas, e GET 404 confirmou ausência. As sessões das duas falhas já haviam desaparecido antes da limpeza. O readback final mostrou zero sessões visíveis/residuais.
- Dois resíduos de uma tentativa anterior interrompida (entradas `Mariadb` e `Pangolin - Racknerd`) foram identificados pela combinação exata de entrada e timestamp do próprio lote de teste, removidos e verificados por readback.
- A VM 109/Home Assistant estava `running` no Proxmox às 06:57 UTC, após a última tentativa de conexão. O log Nexterm na janela da primeira falha registrou apenas um erro SSH/conexão genérico; não foi possível distinguir falha de autenticação, listener SSH ou rede. Nenhuma correção foi aplicada. Investigar esse único acesso exige diagnóstico separado, ainda somente leitura; habilitar add-on SSH, trocar identidade ou alterar a VM requer autorização explícita.

## Related pages

- CMDB: `inventory/index.md`, guest 109 em `inventory/guests.md`, Nexterm em `inventory/guests.md`.
- Wiki: [[nexterm-ssh-auth]], [[openbao-homelab]].
