---
name: cmdb
description: |
  CMDB do homelab do Kiwel: inventário de configuração de cada máquina e serviço
  (CPU, RAM, disco, IP, MAC, portas, criticidade, risco, janela de mudança e
  monitores do Uptime Kuma). USE esta skill sempre que a tarefa precisar saber
  o que existe na infra, onde roda, qual o IP ou a porta, o que quebra se cair,
  se pode reiniciar, ou se está monitorado — mesmo que o usuário não diga "CMDB",
  "inventário" ou "configuração". Dispara em perguntas sobre homelab, guests do
  Proxmox, Docker da VM 101, apps do k3s, DNS, proxy, backup, e-mail, SSO, NAS,
  Home Assistant, Jarvis/Tiberius, Pangolin, Pi-hole, OpenBao, Vaultwarden e
  Uptime Kuma. ATUALIZE o inventário na mesma sessão em que uma config mudar.
  Para o miolo do Proxmox (passthrough, backup jobs, ACL, NUT, SMART) leia também
  a skill proxmox-status; esta skill é a camada de item de configuração e de
  decisão operacional.
---

# CMDB do homelab

Inventário de configuração para um agente decidir sem redescobrir a rede. A
criticidade e a regra de reinício vieram do `~/cmdb.md` do usuário. CPU, RAM,
disco, IP, MAC e portas foram reconciliados com a coleta ao vivo do Proxmox em
**2026-09-23** e com a skill `proxmox-status`. Os IPs do `~/cmdb.md` conferem
com este inventário desde o ajuste do próprio usuário nessa data. Se um dos
dois mudar e o outro não, atualize os dois na mesma sessão.

Não grave segredo nenhum: token, senha, chave, connection string, conteúdo de
`.env`. Diga só onde a credencial é administrada (OpenBao CT 107, Vaultwarden
CT 105).

## Quando ler o quê

| Precisa de | Arquivo |
|---|---|
| Achar um IP, uma porta, a criticidade ou se pode reiniciar | `inventory/index.md` |
| Config de um guest (CPU/RAM/disco/NIC/serviços no CT) | `inventory/guests.md` |
| Container na VM 101 ou app no k3s | `inventory/services.md` |
| O que o Uptime Kuma checa, e checks com alvo velho | `inventory/monitoring.md` |
| Por que um número mudou | `CHANGELOG.md` |

Abra só o arquivo da pergunta. O índice já responde a maior parte das decisões
de "posso reiniciar?" e "quem depende de quem?".

## Três modos

### Consultar

1. Leia o índice e o arquivo do item. Não responda de memória se o fato estiver
   aqui.
2. Fatos de config (vCPU, disco, IP estático, porta publicada, criticidade)
   envelhecem só quando alguém muda a máquina. Fatos voláteis (uso de RAM,
   disco cheio, monitor up/down, container reiniciado hoje) envelhecem em
   horas: confirme o número específico antes de uma decisão que dependa dele.
3. Estado de saúde agora é do Horus (skill `homelab-monitoring`), não deste
   inventário. O Kuma aqui é a **lista de checks**, não o resultado da última
   sonda.

### Atualizar

Faça isto na mesma sessão em que criar, remover, redimensionar, mudar IP/porta,
criticidade, monitor ou dependência — por sua mão ou porque a coleta mostrou
drift.

1. Substitua o valor no arquivo do item. Não empilhe "antes era X".
2. Se a linha do índice ou uma armadilha deste arquivo mudou, corrija aqui.
3. Uma linha no `CHANGELOG.md` (mais novo no topo) com o motivo.
4. Se a mudança também for fato do Proxmox (vCPU, RAM, disco, NIC, onboot),
   atualize a skill `proxmox-status` no arquivo de `state/` correspondente.
5. Se for conhecimento que a wiki cobre (página de um serviço), atualize a
   página canônica, `wiki/index.md` e `wiki/log.md`. Não duplique o inventário
   inteiro na wiki: a página aponta para cá.

Coleta somente leitura, quando o inventário precisar ser conferido de novo:

```bash
python3 ~/skills/cmdb/scripts/coletar.py
```

O script não reescreve o inventário. Ele imprime guests, portas, Docker, k3s e
monitores para você reconciliar. Política de reinício e texto de risco não
saem da coleta — isso só muda quando o usuário mudar a regra.

### O que não fazer

- Não reinicie nem altere um item fora da janela descrita no índice. "Pode
  reiniciar" no inventário autoriza a janela, não substitui o pedido desta
  conversa quando a orientação exige autorização.
- Não trate template parado (CT 115, VM 1000, VM 2000) como incidente.
- Não use o campo `url` de um monitor `port` do Kuma como alvo do probe. O alvo
  é hostname + porta. Vários `url` apontam para outro serviço.
- Não copie serial de disco, hash ou token para cá. Passthrough detalhado fica
  em `proxmox-status`.

## Cartão

| | |
|---|---|
| Host | `proxmox` · `192.168.1.5` · PVE 9.2.5 · só reinicia com autorização e horário marcado |
| LAN | `192.168.1.0/24` · gw `192.168.1.1` (MikroTik) · DNS local Pi-hole `192.168.1.9` |
| Guests | 8 VMs em execução · 17 LXCs em execução · 3 templates parados |
| Login | LXC `root` · VM `kiwel` · Compose de CT em `/root/<app>/` |
| Monitoramento | Uptime Kuma CT 110 `192.168.1.25:3001` · saúde ao vivo no Horus |
| Segredos de agente | OpenBao CT 107 `192.168.1.14:8200` |
| Segredos humanos | Vaultwarden CT 105 `192.168.1.17:8000` |

Itens que **só reiniciam com autorização**: o host Proxmox, TrueNAS (100),
Vaultwarden (105), Pi-hole (121), Home Assistant (109), Windows 11 (114),
Jarvis (116) e Immich (124).

Itens críticos com janela curta, sem precisar marcar horário: Pangolin (120).
Backup (103) pode reiniciar fora de 02h–04h.

## Armadilhas que mudam a decisão

1. **Backup circular.** O datastore PBS `Bkp1tb` vive na VM 103, neste mesmo
   host. Cair o Proxmox leva o backup junto. Detalhe em `proxmox-status`.
2. **CT 122 Authentik é privilegiado** (`unconfined`, `cap.drop` vazio). A
   criticidade de negócio é baixa (SSO); a superfície no host é alta. Não
   "endurecer" sem pedido.
3. **Stalwart não publica SMTP/IMAP no IP do CT.** O Docker só faz bind de
   `:8080` (admin), `:8081` (Roundcube) e `:8082` (AgenDAV). As portas 25/143/993
   existem dentro do container.
4. **Kartrack e RomsDB no Kuma ainda sondam `192.168.1.29:5173`.** A produção
   está no Ingress do k3s, `192.168.1.241`. O `.29` não é guest.
5. **CT 105 Vaultwarden está com `lock: backup`.** Isso bloqueia stop/start até
   `pct unlock 105`. Não é um pedido para destravar.
6. **VM 116 Jarvis e VM 126 K3s não usam `cpu: host`** (kvm64). A 116 tem
   `onboot: 1`, 4 GB de RAM e balloon de 2 GB.
7. **Pi-hole fora não derruba a internet.** O MikroTik troca o DNS para
   `8.8.8.8`. Cai resolução local, adblock e DNS recursivo.
8. **Docker da VM 101 escuta a API em `2375`.** nftables restringe a origem;
   confirme na skill/wiki de Docker antes de tratar como fechado ou aberto.
9. **Login.** Não crie usuário `kiwel` num CT para "ficar igual à VM".

## Relação com as outras skills

- `proxmox-status` — camada PVE: hardware, passthrough, storage, backup, ACL, NUT.
- `homelab-monitoring` / `horus` — saúde agora e alarmes. Não duplique isso aqui.
- `truenas-skill` — pools e datasets da VM 100. Aqui só cabe o guest.
- `wiki` — narrativa e runbooks. O inventário canônico de CI é esta skill.
- `openbao` — como ler segredo. O item de config do cofre está em `guests.md`.
