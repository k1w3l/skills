# Sr. Kiwel — tecnologia geral, exclusões e entrega

Use esta referência para newsletters de tecnologia geral do Sr. Kiwel e para diagnósticos de uma edição que terminou `ok` mas não apareceu.

## Preferências editoriais

- Não envie atualizações rotineiras do kernel Linux, incluindo version bumps, prepatches, merge windows, manutenção comum e mudanças genéricas de drivers.
- Preserve somente exceções materiais: CVE/segurança crítica, regressão comprovada, risco de perda de dados ou quebra/impacto explícito em Proxmox/KVM, ZFS/storage, rede, containers ou servidores self-hosted.
- Uma edição de tecnologia deve cobrir tecnologia geral — software/aplicativos, web/navegadores, hardware, ferramentas de desenvolvimento, open source, segurança, IA, cloud/infra, redes, mobilidade e consumo — sem deixar homelab/Linux dominar.
- Na seleção final, limite a dois itens por assunto central e dois por fonte; prefira pelo menos quatro áreas e quatro fontes quando houver qualidade suficiente. Envie menos itens em vez de preencher por repetição.

## Implementação recomendada

1. Faça a exclusão de assuntos recorrentes no coletor determinístico, não apenas no prompt do modelo.
2. Reaplique exatamente o mesmo predicado a itens RSS/Atom frescos e a itens vindos do cache antes da janela temporal, deduplicação e curadoria.
3. Reduza o peso de fontes que dominam a edição e mantenha uma piscina de fontes gerais com pesos equilibrados.
4. Repita os limites no prompt persistente e, quando possível, valide a seleção no sender antes de qualquer `sendMessage`/`sendPhoto`.
5. Teste a diferença entre ruído de kernel e exceção crítica; um termo genérico como `driver`, `Proxmox` ou `storage` sozinho não é exceção.

## Diagnóstico de ausência

- `last_status: ok` só prova que o job terminou; não prova geração nem entrega.
- Leia o output salvo e os logs. `candidate_count` baixo, `tool_turns=0` e resposta `[SILENT]` significam que a curadoria não selecionou nada, não falha do Telegram.
- Se o operador espera confirmação diária, use `deliver=telegram` e um aviso curto de “nenhum destaque verificado” quando não houver candidatos. Para jobs que enviam cartões diretamente, mantenha `deliver=local` e use `[SILENT]` somente depois de o sender confirmar sucesso.
- Não dispare manualmente um job de cartões só para testar o caminho vazio sem autorização explícita; valide o coletor, o prompt, o roteamento e o próximo horário.
- Verifique separadamente: coleta (contagem/erros/fontes), geração (tool call ou `[SILENT]`) e entrega (sent count/erro da plataforma).
