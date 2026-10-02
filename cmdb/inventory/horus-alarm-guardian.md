# Horus Alarm Guardian — CI e estado operacional

**Verificado em:** 2026-09-25 (readback Hermes Cron, manifesto de exportação e script de sincronização). Horus/guest state permanece baseado na coleta de 2026-09-24 abaixo; não foi recolhido nesta correção.

## Identificação e dependências

- **Job Hermes Cron:** `85ee74c01df3` — `Tiberius — guardião de alarmes persistentes`.
- **Agenda/estado:** `every 5m`, ativo no perfil Tiberius; gateway Cron compartilhado.
- **Monitor:** `~/.hermes/profiles/tiberius/scripts/horus_alarm_guardian.py`.
- **Estado persistente:** `~/.hermes/profiles/tiberius/monitoring/horus-alarm-guardian.sqlite3`; SQLite local com permissões restritas pelo script.
- **Fontes Horus:** snapshot somente leitura com `/api/alarms/active`, condições `material` e `health.findings` quando o diagnóstico tem timestamp válido e idade de até 12 h.
- **Entrega/aprovação:** Telegram via gateway; planos que propõem mudança state-changing têm botões `Aprovar execução` e `Adiar`. A aprovação vale 30 min, vinculada ao alvo/plano/fingerprint, e não executa mudança por si só. Diagnóstico read-only e handoff entre agentes não exigem callback; o usuário pré-autorizou qualquer delegação interagentes.
- **Documentação/dependências:** `~/skills/cmdb/inventory/index.md`, CI/dependências afetados, `~/skills/proxmox-status/state/` e wiki canônica do Horus/domínio.

## Contrato de operação

- Cada condição elegível deve aparecer em **dois snapshots consecutivos**. Flap antes do segundo ciclo é encerrado sem plano; a saída inalterada do monitor não acorda o agente.
- `source=active`: alarme ativo do Horus. `source=material`: condição material de entidade/recurso. `source=health`: finding de diagnóstico Proxmox fresco.
- Snapshot de health ausente, timestamp inválido, futuro implausível ou com mais de 12 h é stale: não abre incidente e não resolve incidentes de health já acompanhados. O status passa a ser avaliado novamente quando houver coleta fresca.
- Pods K3s `Running` e `Ready` cujo único sinal é `restart_count` cumulativo não geram plano. Outros pods fora de readiness/health são agrupados em uma única condição por cluster, reduzindo ruído sem ocultar falhas reais.
- Condição material do boot pool TrueNAS vira finding crítico específico quando `healthy=false` ou o pool não está `ONLINE`/`HEALTHY`; o preflight deve confirmar a condição atual. Incidente conhecido #25 permanece sem remediação até autorização explícita.
- O plano deve conter evidência, diagnóstico, solução, execução, impacto, rollback e validação. Diagnóstico read-only e coleta de evidências podem avançar sem callback, inclusive por agente delegado; o delegado herda o mesmo escopo. Ação state-changing exige aprovação explícita, preflight somente leitura e registro atômico do início, exceto quando coberta por autorização prévia específica.
- Erro de coleta não é ausência de condição: o monitor preserva os estados quando Horus falha e não marca incidents como resolvidos por falta de dados.

## Frescor dos reports

- `horus_status.py` lê primeiro o snapshot persistido; se ausente/inválido ou com mais de 12 h, chama `snapshot(..., run_health=True)` para renovar antes de renderizar.
- Se a renovação falhar ou o Horus continuar retornando snapshot stale, o report rotula a coleta como desatualizada, informa timestamp/contagem, exclui findings antigos da contagem de condições atuais e não gera ações com base neles.
- `horus_daily.py` solicita a coleta noturna e aplica a mesma marcação de frescor. O erro da coleta é mostrado; o resultado antigo não é apresentado como estado atual.

## Correção de resolução de skills — 2026-09-25

- A causa do aviso de skills do job `85ee74c01df3` era seu array explícito `skills`, não a configuração do perfil: o perfil Tiberius já define `skills.create_dir: ~/skills` e `skills.external_dirs: [~/skills]`.
- Readback Hermes Cron: preloads agora são `cmdb`, `proxmox-status`, `wiki-pcl`, `devops/homelab-monitoring`, `devops/infrastructure-state-curation`, `truenas-skill` e `homelab-k8s-deploy`. Prompt, agenda `every 5m`, destino, monitor e enabled state foram preservados; as instruções usam `wiki-pcl` como skill canônica.
- O job de sincronização `9d57ccd39d75` continua `no_agent`; seu script agora lê somente a allowlist `~/skills/.tiberius-skill-sync.json` e valida as 65 fontes relativas contra `~/skills`. A saída é um catálogo flat de symlinks em `~/skills/tiberius-skills/`; conteúdo de skill não é copiado.
- Validação isolada: 65 fontes canônicas aceitas; execução do `main()` contra destino temporário criou 65 symlinks apontando para dentro de `~/skills`; entrega foi stubbed, sem Telegram real e sem execução manual do job.
- No destino de produção, 64 dos 65 basenames de skill colidem com arquivos regulares vazios; 13 diretórios não colidem, há zero symlinks e uma skill ainda não tem entrada. Não sobrescrever/remover; limpeza exige escopo/autorização próprios.
- `hermes -p tiberius cron doctor`: 9 jobs ativos, nenhum problema. As cinco execuções guardiãs mais recentes (00:15–00:39 BRT) não têm aviso de skill ausente; a mais recente terminou `ok`. Nenhuma execução manual do sincronizador nem alteração de infraestrutura Proxmox/Horus ocorreu.

## Reconciliado ao vivo em 2026-09-24

- Job lido de volta pelo Hermes Cron: ativo, a cada 5 min, monitor `horus_alarm_guardian.py`, skills de `cmdb`, `proxmox-status`, wiki, monitoramento, curation, `truenas-skill` e `homelab-k8s-deploy`. O prompt foi atualizado para distinguir `active`/`material`/`health` e exigir preflight por origem. Nenhum reload do gateway foi feito.
- Horus: `0` alarmes ativos; health executado em `2026-09-24T19:30:16Z`, `overall=ok`, `0` findings; `9` desvios materiais.
- Um desvio é o boot pool `freenas-boot` `DEGRADED`/`FAILING_DEV`, único vdev virtual `sda2`, correspondente ao incidente crítico aberto #25. Não foi feita mutação de pool, reinício ou recuperação.
- Os oito pods K3s rotulados `degraded` estão `Running`/`Ready`. Leitura somente por SSH/`kubectl` confirmou para esses pods último término em `2026-08-29T19:56:10Z`, exit `255`, reason `Unknown`; contadores são cumulativos/históricos e não geram plano sozinhos.
- Teste de integração com banco temporário: 2 snapshots reais consecutivos produziram exatamente 1 evento `investigate` crítico `source=material` para `truenas/freenas`; nenhum Telegram foi enviado pelo teste e a base de produção não foi usada por ele.
- Reports/guardian: os módulos direcionados `test_horus_alarm_guardian` + `test_horus_monitoring` passaram com 35 testes; `python3 -m unittest discover -v` passou com 54 testes no total. Readback da base de produção às 20:38Z: finding TrueNAS em `awaiting_approval`, 2 observações, message ID registrado, sem `execution_started_at` nem resultado de execução. O plano é somente diagnóstico read-only (TrueNAS e metadados PVE); nenhuma mutação ocorreu. Callback ainda não exercitado porque não houve clique.
- O health stale anterior de CT 123/Postgres (97%) foi revalidado ao vivo como guest `running`, filesystem em 79%, e nova coleta Horus `overall=ok`, sem findings. Nenhum backup foi removido.

## Delegação e bloqueio de rede — regra confirmada em 2026-09-24

- O usuário pré-autorizou qualquer delegação de tarefa entre agentes. Não pedir aprovação adicional para handoff; diagnósticos read-only não devem ficar `awaiting_approval` só por cruzarem fronteiras de agente.
- A autorização de delegação não autoriza mutação fora do escopo já aprovado e não contorna segurança de rede do Cron. Na tentativa TrueNAS, o job bloqueou a URL HTTPS com IP privado literal; não foi feito bypass. Usar uma via suportada ou reportar o bloqueio.

## Rollback e limites

- Para interromper novas investigações, pausar o job Hermes Cron `85ee74c01df3`; o histórico SQLite permanece para auditoria.
- Para reverter a mudança, restaurar as versões anteriores dos scripts de `horus_status.py`, `horus_daily.py`, `horus_common.py` e `horus_alarm_guardian.py`, e o prompt anterior do job. Manter a base SQLite preserva auditoria; não apagar incidentes como parte do rollback.
- Nenhuma remediação de infraestrutura foi executada nesta alteração. A reconstrução/substituição do boot device TrueNAS continua bloqueada até autorização explícita e janela aprovada.
