---
name: wiki
description: >-
  A wiki pessoal unificada do usuário em
  /mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/ é a fonte de verdade dele:
  conhecimento técnico curado (Docker, Kubernetes, Proxmox, TrueNAS, home-lab,
  self-hosting, Linux, Ansible, Terraform, IaC, automação de rede, Git, CI/CD,
  DevSecOps, segurança, Python, FastAPI, monitoramento, logging, backups,
  reverse proxy, DNS, n8n, LLMs locais, Claude Code, MCP, agentic coding, AI
  SaaS) e o estado real do ambiente (o que foi implantado, rotinas do
  J.A.R.V.I.S., decisões, projetos e procedimentos). SEMPRE CONSULTE A WIKI
  PRIMEIRO — antes de memórias auxiliares, web ou treino — sempre que o usuário
  perguntar, explicar, comparar, recomendar, depurar, brainstorm, diagnosticar,
  planejar ou implantar nesses temas. Para documentação de libs/frameworks/SDKs/
  APIs/CLIs/cloud: se a wiki não cobrir ou estiver desatualizada, use Context7
  MCP. E REGISTRE de volta: criar algo novo, adquirir conhecimento, mudar
  rotina ou receber orientação durável → criar/atualizar página + index.md +
  log.md. Diretrizes: sobre-a-wiki.md na raiz do vault.
---

# Wiki-first: consultar e devolver

Um único vault Obsidian no NAS. A skill serve para **ler antes de responder** e
**escrever depois de aprender**. É isso que faz o conhecimento compor ao longo
do tempo em vez de se perder no fim da conversa.

## Vault padrão

| | |
|---|---|
| **Raiz do vault** | `/mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/` |
| **Páginas** | `.../wiki/wiki/*.md` |
| **Índice** | `.../wiki/wiki/index.md` |
| **Log** | `.../wiki/wiki/log.md` |
| **Fontes** | `.../wiki/raw/` (imutável) |
| **Diretrizes** | `.../wiki/sobre-a-wiki.md` |

## Ordem obrigatória de consulta

1. **Wiki primeiro.** Abra `wiki/index.md` e as páginas relevantes **antes** de
   qualquer outra fonte (memórias auxiliares, web, treino). Se a página certa
   não for óbvia, use Grep em `wiki/*.md`.
2. **Leia de verdade.** Siga os `[[links]]` internos. Nunca resuma uma página
   "de cabeça" sem abrir o arquivo.
3. **Documentação externa via Context7.** Para biblioteca, framework, SDK, API,
   CLI ou serviço de nuvem: se a wiki não tiver o assunto, ou estiver
   desatualizada/incompleta, use o MCP **Context7** (`resolve-library-id` →
   `query-docs`). Só então web ou treino. Vale também para confirmar detalhes
   de API que mudam rápido mesmo quando a página existe.
4. **Retrato datado.** Páginas com "estado conferido em <data>" não são estado
   ao vivo — confirme na máquina antes de decidir algo operacional.
5. **Cite** como `(wiki: nome-da-pagina)`. Só cite página que você leu.
6. **Se cobrir só em parte:** diga ("a wiki tem X mas não Y") e complete com
   Context7/outras fontes, separando o que é dele do que é externo.
7. **NAS desmontado:** avise. Nunca finja ter consultado.
8. **Fora do domínio:** responda normalmente, sem forçar.

## Registro obrigatório

Sempre que na conversa você **criar algo novo**, **adquirir um conhecimento
durável**, **mudar alguma rotina**, ou **receber uma orientação** do usuário
que valha para o futuro — crie documentação na wiki ou atualize a página
canônica se já existir, **antes do fim da tarefa**.

Também registre: problema não trivial resolvido, decisão de arquitetura ou
ferramenta, implantação concluída, pegadinha descoberta, procedimento que
funcionou.

**Não vale registrar** tentativa-e-erro sem conclusão, progresso efêmero, log
rotineiro ou saída bruta sem curadoria. **Nunca** senha, token, chave privada
ou cookie — registre só onde a credencial é administrada, jamais o valor.

1. **Crie ou atualize a página canônica** no formato de `sobre-a-wiki.md`
   (título, `**Summary**`, `**Sources**`, `**Last updated**`, `---`, conteúdo,
   `## Related pages`). Prefira atualizar a página existente a fragmentar.
   Ligue com `[[wiki-links]]`.
2. **Atualize `wiki/index.md`** — página nova entra com uma linha de descrição.
3. **Append em `wiki/log.md`** com a data e o que mudou.

**Crie e edite sem pedir permissão.** Qualquer agente já está autorizado
(2026-09-22) a criar página nova e a atualizar as existentes sempre que for
preciso. Não pergunte antes. Reportar o que mudou. Exclusão de arquivo,
recurso ou dado continua exigindo permissão explícita. `raw/` permanece
imutável.

## Comando `raw`

Quando o usuário enviar somente `raw`, ative esta skill e verifique `raw/` de
forma incremental: só fontes novas ou alteradas são ingeridas; inalteradas são
ignoradas sem releitura; originais permanecem imutáveis. Atualize `index.md` e
`log.md` quando houver mudanças. Peça esclarecimento só diante de ambiguidade
material, conteúdo delicado ou risco de registrar segredos.

## Limites

- `raw/` é imutável. Nunca altere nada ali.
- Nomes de página em minúsculas com hífen.
- Siga `sobre-a-wiki.md` para formato, ingestão e lint.
