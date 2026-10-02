# Template do relatório de infraestrutura

Estrutura do relatório completo do Proxmox. Salve em `~/relatorio-proxmox-<AAAA-MM-DD>.md`.

Sempre em **português**. Sempre com **números concretos** — "79 % de 458 GB, 95 GB livres" é útil,
"quase cheio" não é. Tabelas para inventário, blocos de código para configs literais.

Quando o usuário pedir só uma área ("relatório dos backups", "como estão os discos"), use apenas as
seções relevantes — não force o relatório inteiro.

**Nunca incluir segredos:** tokens de API, hashes de `cipassword`, senhas do NUT, token do Gotify,
chaves SSH. Redija (`<REDACTED>`) ou omita.

---

## Esqueleto

```markdown
# Relatório de Infraestrutura — Proxmox VE

**Nó:** `proxmox` (`proxmox.kiwel.home`) · **IP:** 192.168.1.5
**Gerado em:** <data e hora, -03>
**Coleta:** SSH direto no nó + API `pvesh`

## Sumário executivo
<tabela com versão, kernel, base, boot, cluster, uptime, load, contagem de guests, subscrição>

### Mudanças desde o último relatório
<Seção obrigatória quando existe relatório anterior. Uma linha por mudança real,
com o valor antigo → novo. Se nada mudou estruturalmente, diga isso explicitamente.
Variação normal de uso (RAM, temperatura, uptime) não entra aqui.>

### Pontos que exigem atenção
<lista numerada, o mais crítico primeiro, vinda de issues.md + o que a coleta nova revelou>

## 1. Hardware do host
1.1 Plataforma · 1.2 CPU · 1.3 Memória · 1.4 Vídeo · 1.5 Rede (hardware)
1.6 Controladoras de armazenamento · 1.7 IOMMU

## 2. Discos físicos
2.1 Inventário completo · 2.2 Seriais e caminhos by-id · 2.3 Desgaste dos SSDs
2.4 Layout de partições

## 3. Storages Proxmox
3.1 Definições · 3.2 Consumo por guest · 3.3 Templates e ISOs

## 4. Máquinas virtuais
4.1 Visão geral (tabela) · 4.2 Configurações detalhadas (uma subseção por VM)

## 5. Containers LXC
5.1 Visão geral (tabela) · 5.2 Configurações especiais

## 6. Hardware passado para guests (passthrough)
6.1 Tabela consolidada · 6.2 Sobre a porta USB do nobreak

## 7. Nobreak (UPS) — NUT
7.1 Modelo e estado atual · 7.2 Configuração · 7.3 Política de desligamento

## 8. Rede
8.1 Topologia · 8.2 Mapa de IPs · 8.3 MACs · 8.4 Firewall · 8.5 Portas em escuta

## 9. Backups
9.1 Jobs · 9.2 Última execução · 9.3 Cobertura por guest · 9.4 Órfãos
9.5 Config do host · 9.6 Retenção

## 10. Usuários, autenticação e permissões
10.1 Usuários · 10.2 Tokens · 10.3 Grupos e ACLs · 10.4 Roles

## 11. Sistema operacional e pacotes
11.1 Versões · 11.2 Repositórios · 11.3 Datacenter · 11.4 Módulos e blacklists

## 12. Serviços, agendamentos e monitoramento
12.1 Daemons · 12.2 Cron · 12.3 Timers · 12.4 Notificações
12.5 Monitoramento externo · 12.6 Snapshots · 12.7 HA e replicação

## 13. Alocação de recursos e capacidade
13.1 vCPU · 13.2 Memória · 13.3 Armazenamento

## 14. Diagnóstico e recomendações priorizadas
<três tabelas — alta / média / baixa — com # da issue, item e ação sugerida>

## Anexo — Comandos de coleta
<referência ao scripts/coletar.sh e aos comandos principais>

---

*Relatório gerado a partir de coleta ao vivo em <data>. Segredos foram omitidos ou redigidos.*
```

---

## Notas de conteúdo

**Sumário executivo** — o usuário lê isso primeiro e muitas vezes só isso. Os "pontos que exigem
atenção" devem ser acionáveis e ordenados por consequência real, não por facilidade de correção.

**Seção de mudanças** — é o que diferencia um relatório atualizado de um relatório novo. Vem da
reconciliação entre `state/` e a coleta ao vivo. Se a coleta anterior estiver guardada,
`diff -r <anterior> <nova>` a produz quase pronta.

**Configurações detalhadas** — cole a config literal do `.conf` em bloco de código e comente ao
lado do que for relevante (`# ← disco em SATA, não SCSI`). Ler a config crua junto do comentário é
mais útil que a prosa sozinha.

**Passthrough e nobreak** — sempre deixar explícito que o nobreak **não** é passthrough USB. É a
confusão mais provável de quem lê o relatório, e já apareceu uma vez.

**Recomendações** — puxe de `state/issues.md` mantendo os números das issues, para que o usuário
consiga rastrear entre relatórios sucessivos qual pendência é qual.
