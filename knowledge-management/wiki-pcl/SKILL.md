---
name: wiki-pcl
description: >-
  Use this skill for every user request, consulting the user's unified PCL wiki
  first as the primary source. For environment, projects, systems, procedures,
  decisions, preferences, operational state, or durable knowledge, if the wiki
  does not contain the answer or is stale, use Context7 for current
  library/framework/API/CLI documentation when applicable, and only then use
  other external sources. After anything is created, changed, configured,
  answered through a durable procedure, fixed, decided, or added to memory,
  document the durable result in the wiki so all agents remain aligned. Trigger
  even when the user does not explicitly mention the wiki.
---

# Wiki PCL: fonte principal e alinhamento entre agentes

A wiki unificada do PCL é a fonte de verdade compartilhada entre os agentes.
Este fluxo combina a skill `wiki` e o antigo alias `wiki-jarvis`; não trate os
antigos vaults separados como bases ativas.

## Localização canônica

```text
vault:   /mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/
policy:  /mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/sobre-a-wiki.md
pages:   /mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/wiki/
index:   /mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/wiki/index.md
log:     /mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/wiki/log.md
raw:     /mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/raw/
```

## Ordem obrigatória de consulta e ação

Antes de responder ou agir, siga esta ordem:

1. **Índice primeiro.** Leia `wiki/index.md` para localizar a página canônica
   relevante; nunca comece pela web, memória ou treino.
2. **Páginas pertinentes.** Leia as páginas relevantes e sintetize apenas o que
   estiver efetivamente documentado; cite-as como `(wiki: nome-da-página)`.
3. **Estado ao vivo.** Confirme ao vivo qualquer estado operacional ou
   informação volátil. Uma página datada é retrato histórico, não garantia do
   estado atual.
4. **Documentação técnica.** Se a wiki não cobrir o assunto ou estiver
   desatualizada, consulte Context7 primeiro para documentação de bibliotecas,
   APIs, CLIs e serviços; depois, fontes oficiais na web.
5. **Registro durável.** Quando a tarefa produzir conhecimento, configuração,
   decisão, mudança de rotina ou orientação nova, registre antes de concluir:
   atualize a página canônica ou crie uma, adicione links internos e atualize
   `wiki/index.md` e `wiki/log.md`.
6. **Segurança da base.** Nunca modifique `raw/`, nem registre senhas, tokens,
   chaves ou outros segredos.
7. **NAS indisponível.** Declare que não foi possível consultar a wiki; jamais
   finja que foi consultada.

Depois, separe na resposta o que veio da wiki, do Context7 e de outras fontes,
explique conflitos em vez de escolher silenciosamente uma versão e cite páginas
lidas como `(wiki: nome-da-pagina)`. Fora do domínio da wiki, não force uma
consulta vazia; preserve as demais regras aplicáveis.

### Gates operacionais complementares

- Consulte skills pessoais somente no catálogo canônico `~/skills/`; resolva nomes ambíguos com entrada categorizada, sem adivinhar.
- Em projeto existente, localize a raiz antes de ler ou editar; em projeto novo, crie a pasta e inicialize Git antes do scaffold.
- Antes de ações em Proxmox, guests, servidor, NAS, PBS ou homelab, consulte `proxmox-status` e a CMDB, além de confirmar o estado ao vivo.

### Casos específicos

- Skill nova: conteúdo em `~/skills/<nome>/`, com
  symlinks nos catálogos Claude, Cursor, Hermes e `~/.agents/skills`.
- A palavra `drakaris` dispara o pipeline completo de release/deploy, sem pedir
  confirmação a cada etapa; siga a skill e a página do projeto, não faça
  force-push e pare diante de falha bloqueante.
- Qualquer agente já está autorizado (2026-09-22) a criar página nova da wiki
  e a editar as existentes sem pedir permissão. Reportar o que mudou. A pasta
  `raw/` continua imutável.
- Exclusão de arquivo, recurso ou dado exige permissão explícita do usuário.

## Registro obrigatório de mudanças e conhecimento

Registre na wiki, antes de concluir a tarefa, qualquer resultado durável de:

- criação, ajuste, configuração, instalação ou implantação;
- atendimento de solicitação que produza uma orientação ou procedimento
  reutilizável;
- diagnóstico, correção, resolução ou descoberta de uma falha;
- decisão, alteração de rotina, convenção ou estado operacional relevante;
- nova memória persistente criada para o usuário ou para o ambiente;
- documentação externa consultada que seja importante para decisões futuras.

O objetivo é que todos os agentes possam consumir o mesmo estado, e não manter
informações importantes apenas na memória desta conversa.

### Como registrar

1. Pesquise antes para evitar duplicatas.
2. Atualize a página canônica existente quando ela já cobrir o assunto. Crie uma
   nova página somente quando não houver página adequada; use nomes em minúsculas
   com hífens.
3. Registre o estado final, motivo, procedimento validado, limitações e
   implicações futuras. Não copie tentativa e erro, saída bruta ou progresso
   efêmero.
4. Atualize `wiki/index.md` quando criar página nova ou quando a navegação ficar
   obsoleta.
5. Adicione uma entrada datada em `wiki/log.md`, preservando seu caráter
   append-only.
6. Releia os trechos alterados e valide links, datas, consistência e ausência de
   segredos antes de finalizar.

A documentação é parte do critério de conclusão: não ofereça “documentar depois”.
Se a ação não produziu conhecimento durável, não crie ruído artificial; ainda
assim, qualquer nova memória persistente deve sempre ter registro correspondente.

## Formato e segurança

Ao criar página, prefira:

```markdown
# Título

**Summary**: Síntese curta.

**Sources**: Fontes usadas.

**Last updated**: YYYY-MM-DD

---

Conteúdo com headings claros e [[wiki-links]].

## Related pages

- [[pagina-relacionada]]
```

- Leia e siga a política canônica em `sobre-a-wiki.md` se houver qualquer dúvida.
- Nunca modifique `raw/`; fontes originais são imutáveis.
- Nunca registre senhas, tokens, chaves privadas, cookies ou outros segredos;
  registre apenas onde a credencial é administrada.
- Não escreva nos antigos caminhos `Wiki-Jarvis/` ou `Wiki-Devops/`.
- O comando isolado `raw` significa ingestão incremental: processe apenas fontes
  novas ou alteradas sob `raw/`, preserve-as e atualize páginas, índice e log
  quando houver mudanças.

## Relação com outras skills

- `wiki` contém a política operacional detalhada e deve ser seguida como
  referência complementar.
- `wiki-jarvis` é apenas um alias de compatibilidade para a wiki unificada.
- `context7-mcp` define o procedimento de resolução e consulta no Context7.
