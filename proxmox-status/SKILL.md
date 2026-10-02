---
name: proxmox-status
description: |
  Estado real e documentado do Proxmox VE do Kiwel (nó `proxmox`, 192.168.1.5): hardware do
  host, todas as VMs e LXCs com suas configs, discos físicos e SMART, storages, passthrough
  de hardware (iGPU, NVMe, HDDs, /dev/net/tun), nobreak via NUT, rede e mapa de IPs, jobs e
  cobertura de backup, usuários/tokens/ACLs, serviços e pendências abertas.
  CONSULTE esta skill ANTES de qualquer tarefa que toque o Proxmox do usuário — diagnóstico,
  mudança de config, criação/remoção/redimensionamento de VM ou LXC, mexer em backup, storage,
  rede, passthrough, permissões ou nobreak — e também antes de responder qualquer pergunta
  sobre "meu proxmox", "minhas VMs", "meus containers", "meu servidor", "meu home lab" ou
  "meu NAS/TrueNAS/PBS", mesmo que o usuário não diga "Proxmox" explicitamente. Ela evita
  redescobrir por SSH o que já está documentado e evita decisões erradas por desconhecer
  armadilhas do ambiente (backup circular dentro da VM 103, tokens de API com Administrator,
  CT 122 privilegiado, sistema em SSD BX500). ATUALIZE esta skill sempre que uma mudança
  for feita no Proxmox. Ao pedir "relatório do Proxmox" / "relatório atualizado", gere a
  partir do estado aqui e reconcilie com uma coleta ao vivo.
---

# Estado do Proxmox do Kiwel

Esta skill é a **memória viva** do ambiente Proxmox do usuário. Ela existe porque redescobrir
o parque inteiro por SSH a cada sessão é caro e, pior, porque decisões tomadas sem conhecer as
armadilhas deste ambiente específico já custaram retrabalho — por exemplo, sugerir "restaure do
backup" sem saber que o servidor de backup roda *dentro* de uma VM deste mesmo host.

Complementa a skill `proxmox` (referência genérica do produto: comandos, conceitos,
troubleshooting). Quando a pergunta for **"como o Proxmox funciona"** → `proxmox`. Quando for
**"como *este* Proxmox está"** → esta skill.

## Cartão de referência rápida

| | |
|---|---|
| Nó | `proxmox` / `proxmox.kiwel.home` · **192.168.1.5** · SSH por chave como `root` |
| Versão | PVE 9.2.5 · kernel 7.0.14-6-pve · Debian 13 · nó único (sem cluster) |
| Hardware | MSI PRO B760M-P DDR4 · i5-13500T (14C/20T) · 64 GB DDR4 · 10 discos |
| Guests | 8 VMs + 17 LXCs ativos + 3 templates (CT 115, VM 1000, VM 2000) |
| Storage principal | `Samsung` (NVMe 500 GB, dir/ext4) — **84 % cheio** |
| Backup | PBS `Bkp1tb` em **192.168.1.42 = VM 103**, hospedada neste mesmo host |
| Interface | https://192.168.1.5:8006 · SSO via Authentik (CT 122) |
| Login nos guests | **LXC: `root`** · **VMs: `kiwel`** |

**Ordem de boot:** 1 TrueNAS(100) → 3 Pihole(121) / Docker(101) → 4 nginx(117) → 5 Hassio(109)
→ 6 W11(114) → 7 vaultwarden(105). Guests marcados `[critical]`: 100, 105, 109, 121.

### Armadilhas deste ambiente (leia antes de agir)

Estas não são opiniões — são coisas que mudam qual é a resposta certa:

1. **O backup é circular.** O datastore PBS `Bkp1tb` roda dentro da **VM 103**, que é hospedada
   neste host, num HDD passado para ela. "Restaure do backup" não é uma saída se o host morrer.
   A VM 103 em si quase não tem backup (o job dela está desabilitado desde 28/07/2026).
2. **`mem` vs `memhost`.** Só a VM 116 tem `balloon` configurado. Nas demais, `/nodes/*/qemu`
   reporta memória do *host*, que só cresce — uma VM "a 100 % de RAM" quase sempre é artefato
   de medição. Use `pvesh get /cluster/resources`, que traz o `mem` correto.
3. **Todo token de API é Administrator.** Os grupos `api-users` e `hass-users` têm ACL
   `Administrator` em `/`, sobrepondo as roles restritas. Não presuma que o token do Horus é
   somente-leitura — ele é root.
4. **O sistema roda num SSD Crucial BX500 240 GB** (migrado do HDD HGST 320 GB). I/O do root
   melhorou, mas backups/restore ainda saturam por causa dos HDDs do TrueNAS/PBS e da
   controladora Marvell. O job de backup de 28/07 levou 10 h e falhou em cascata.
5. **O storage `Samsung` está a 79 %.** Criar guest novo ou expandir disco precisa de conferência
   de espaço antes.
6. **O nobreak NÃO é passthrough USB.** É gerenciado pelo host via NUT em `netserver`
   (`/dev/ttyACM0`, driver `blazer_ser`, porta 3493 aberta na LAN). Não procure `usb0` nas VMs.
7. **CT 122 (Authentik) é privilegiado com AppArmor `unconfined`** e `cap.drop` vazio — acesso
   equivalente a root no host. Tratar como superfície crítica.
8. **Roles com `VM.Monitor`** (privilégio removido no PVE 9) fazem todo comando `qm`/`pct`
   imprimir `user config - ignore invalid privilege 'VM.Monitor'`. É ruído conhecido, não é falha.
9. **Login nos guests:** LXC = `root`; VMs = `kiwel`. Não criar `kiwel` num CT para “ficar
   igual à VM”. Compose de app em LXC vive em `/root/<app>/`.

## Onde está cada coisa

O detalhe fica em `state/`, um arquivo por área. Leia só o que a tarefa exige — abrir tudo
desperdiça contexto.

| Arquivo | Conteúdo | Leia quando |
|---|---|---|
| `state/host.md` | Placa, BIOS, CPU, RAM, GPUs, sensores, IOMMU, kernel, repos | Hardware, temperatura, capacidade, atualização de kernel/BIOS |
| `state/guests.md` | **Config completa de cada VM e LXC**, recursos, IPs, SO, alocação | Qualquer coisa sobre um guest específico |
| `state/storage.md` | Storages PVE, discos físicos, SMART, layout de partições, uso | Espaço, disco novo, saúde de disco, criar/mover volume |
| `state/passthrough.md` | Todo hardware passado a guests + nobreak/NUT completo | Passthrough, GPU, disco físico, nobreak, energia |
| `state/network.md` | Bridge, mapa de IPs, MACs, firewall, portas em escuta | Rede, IP novo, firewall, exposição de serviço |
| `state/backup.md` | Jobs, cobertura por guest, histórico de falhas, retenção | Backup, restore, retenção, agendamento |
| `state/access.md` | Usuários, tokens, grupos, ACLs, roles | Permissões, token novo, integração externa |
| `state/services.md` | Daemons, cron, timers, notificações, KSM, monitoramento | Serviço, agendamento, alerta, KSM |
| `state/issues.md` | **Pendências abertas com status e prioridade** | Antes de propor melhorias — e depois de resolver alguma |
| `CHANGELOG.md` | Histórico datado de mudanças no ambiente | Entender por que algo está como está |

`references/report-template.md` tem a estrutura do relatório completo.
`scripts/coletar.sh` faz a coleta ao vivo.

## Os três modos de uso

### 1. Consultar (antes de administrar)

Leia o cartão de referência acima e o(s) arquivo(s) de `state/` relevantes à tarefa. Isso
normalmente já responde a pergunta ou dá o contexto para agir sem tatear.

**Confie no estado, mas verifique o que for decisivo.** O estado tem uma data de verificação no
topo de cada arquivo. Fatos estruturais (modelo da placa, serial de disco, quem recebe qual
passthrough) envelhecem devagar. Fatos voláteis — espaço livre, uso de RAM, se um job está
habilitado, se um guest está ligado — envelhecem em horas. Antes de tomar uma decisão que
depende de um número volátil, confirme aquele número específico no host; não é preciso recoletar
tudo.

Se encontrar divergência entre o estado e a realidade, **corrija o estado na hora** e registre no
CHANGELOG — foi uma mudança que aconteceu fora daqui.

### 2. Atualizar (depois de qualquer mudança)

Sempre que algo mudar no Proxmox — por sua mão ou por observação — atualize a skill na mesma
sessão. Estado desatualizado é pior que estado nenhum, porque induz confiança falsa.

O que conta como mudança: criar/remover/renomear guest; mudar CPU, RAM, disco, rede ou boot de um
guest; passthrough novo ou removido; mexer em storage; alterar job de backup; mexer em usuário,
token, role ou ACL; trocar hardware; atualizar PVE ou kernel; mudar config do NUT; resolver (ou
descobrir) uma pendência de `issues.md`.

Para cada mudança:

1. Edite o arquivo de `state/` correspondente — **substitua o valor antigo**, não empilhe notas.
2. Atualize a linha `Verificado em:` no topo daquele arquivo.
3. Se a mudança contradiz o cartão de referência ou uma armadilha deste SKILL.md, corrija aqui também.
4. Se resolveu ou criou uma pendência, atualize `state/issues.md`.
5. Acrescente uma linha ao `CHANGELOG.md` no formato:

```markdown
## 2026-08-15
- **VM 124 (Immich)** — RAM 8 GB → 12 GB. Motivo: uso constante em 94 %, ML de rostos travando.
```

O CHANGELOG é cronológico decrescente (mais novo no topo) e existe para responder "por que isso
está assim?" meses depois. Registre o **motivo**, não só o valor — o valor já está no `state/`.

### 3. Gerar relatório

Quando o usuário pedir relatório do Proxmox — atualizado, completo, ou de uma área específica:

1. **Rode a coleta ao vivo:**
   ```bash
   ~/skills/proxmox-status/scripts/coletar.sh \
     ~/.local/share/proxmox-status/coleta-$(date +%F)
   ```
   São ~12 arquivos de texto, um por área, em cerca de um minuto. Não faz nenhuma escrita no host.

2. **Compare com a coleta anterior** — é o atalho que entrega a seção de mudanças quase pronta:
   ```bash
   diff -r ~/.local/share/proxmox-status/ultima \
           ~/.local/share/proxmox-status/coleta-$(date +%F)
   ```
   Depois de gerar o relatório, reaponte o link: `ln -sfn <nova-coleta> ~/.local/share/proxmox-status/ultima`.
   As coletas antigas são pequenas (~130 KB); vale guardar algumas.

3. **Reconcilie com o estado documentado.** Este é o passo que dá valor: o `state/` é a base
   pronta, a coleta é o presente. Compare os dois e classifique cada diferença:
   - **Mudança real** (guest novo, disco trocado, job reativado) → vai para o relatório na seção
     "Mudanças desde o último relatório", *e* atualiza `state/` + `CHANGELOG.md`.
   - **Variação normal** (uso de RAM, temperatura, uptime, espaço livre) → só atualiza o número
     no relatório, sem virar entrada de changelog.
   - **Pendência resolvida ou agravada** → atualiza `state/issues.md` e reflete na seção de
     recomendações.

4. **Escreva o relatório** seguindo `references/report-template.md`. Sempre em português,
   sempre com uma seção de mudanças desde o relatório anterior, sempre com as recomendações
   priorizadas em alta/média/baixa vindas de `issues.md` mais o que a coleta nova revelar.

5. **Atualize a skill** com o que a coleta mostrou de novo, antes de encerrar. Um relatório que
   não realimenta o estado desperdiça a coleta.

6. Salve o relatório em `~/relatorio-proxmox-<AAAA-MM-DD>.md` (é onde o usuário espera achar).

**Nunca inclua segredos no relatório**: tokens de API, senha do Gotify, hashes de `cipassword`,
chaves SSH e senhas do NUT ficam de fora ou redigidos. O estado em `state/` segue a mesma regra.

## Acesso ao host

SSH por chave já configurada: `ssh root@192.168.1.5`. O `coletar.sh` respeita `PVE_HOST` e
`PVE_USER` se o endereço mudar.

Comandos de leitura são seguros. Para escrita — `qm set`, `pct set`, `vzdump`, alteração de
storage, `pvesm`, mudança de ACL — confirme com o usuário antes, exceto quando ele já pediu a
mudança explicitamente nesta conversa. Lembre que a maioria dos guests são serviços em produção
do home lab (DNS, SSO, e-mail, gerenciador de senhas, automação residencial): parar o guest
errado tem efeito imediato e visível.

Mudança de config em VM ligada costuma cair em `[PENDING]` — `qm config` mostra o valor ativo,
então a alteração pode parecer que falhou silenciosamente. Confira `/etc/pve/qemu-server/<id>.conf`
e lembre que mudança de dispositivo exige stop/start completo, não reboot pelo guest.

## Relação com as outras skills

- **`proxmox`** — referência genérica do produto. Use junto quando precisar de sintaxe de comando
  ou troubleshooting conceitual.
- **`truenas-skill`** — a VM 100 é o TrueNAS, com 6 HDDs de 4 TB em passthrough. Perguntas sobre
  pools, datasets, snapshots ou apps do NAS vão para lá; o que está aqui é a camada de
  virtualização abaixo dele.
- **`wiki`** — as wikis pessoais do usuário. Depois de uma mudança relevante de infraestrutura,
  vale registrar a síntese lá também, além do CHANGELOG daqui.
- **`horus`** — o projeto de observabilidade que consome a API deste Proxmox pelo token
  `horus@pve!horus`.
- **`cmdb`** — inventário de configuração e política operacional (IP, porta, criticidade,
  reinício, monitores do Uptime Kuma, apps do Docker e do k3s). Esta skill continua dona
  do miolo PVE: passthrough, storage, backup, ACL, NUT.
