---
name: knowledge-base-operations
description: >-
  Operar e manter bases de conhecimento pessoais ou técnicas como fonte de verdade:
  consultar antes de responder, verificar estado operacional volátil, atualizar páginas
  canônicas, registrar mudanças, reconciliar edições concorrentes e preservar proveniência.
  Use sempre que uma tarefa consultar ou modificar wiki, vault Obsidian, runbook,
  documentação operacional, índice, changelog/log de conhecimento ou segundo cérebro —
  inclusive quando a documentação não for citada explicitamente, mas a resposta depender
  do estado documentado do ambiente.
---

# Knowledge Base Operations

Use a base como memória curada, não como depósito de transcrições. O objetivo é fazer o
conhecimento compor entre sessões sem transformar retratos antigos em falsas certezas.

Ao responder ou agir usando a wiki pessoal do Sr. Kiwel, leia `wiki/index.md`
primeiro para localizar a página canônica — nunca comece por web, memória ou
treino. Leia em seguida as páginas pertinentes; consulte `sobre-a-wiki.md` e
`references/kiwel-wiki.md` para regras e caminhos sem deslocar o índice do primeiro
passo. Se o NAS não estiver acessível, declare que a wiki não foi consultada.
A diretriz canônica do próprio vault prevalece sobre esta skill.

Para as skills deste usuário, consulte exclusivamente `~/skills/` como diretório canônico.
Trate outros catálogos registrados como integrações, não como fontes independentes de busca.
Se o nome simples for ambíguo, selecione a entrada categorizada correspondente ao conteúdo
canônico; não adivinhe.

> **Cuidado com skills legadas sobrepostas:** o catálogo ainda pode expor a skill externa
> `wiki`, que descreve os antigos vaults separados `Wiki-Devops` e `Wiki-Jarvis`, e a skill
> manual `wiki-jarvis`, que também aponta para o vault aposentado. Esses caminhos foram
> substituídos pelo vault unificado. Não siga nem propague aquela topologia antiga; use
> `references/kiwel-wiki.md` e, sobretudo, o `sobre-a-wiki.md` do vault atual. Se uma dessas
> skills for carregada por engano, trate seus caminhos como desatualizados e prossiga com esta
> skill de operações de base de conhecimento.

## Consulta antes de responder

1. Consulte `wiki/index.md` primeiro para localizar a página canônica; não comece por web,
   memória ou treino.
2. Leia as páginas pertinentes, sintetize apenas o que estiver efetivamente documentado e
   cite-as como `(wiki: nome-da-página)`.
3. Confirme ao vivo qualquer estado operacional ou informação volátil; páginas datadas são
   retratos históricos, não garantias do estado presente.
4. Se a wiki não cobrir o assunto ou estiver desatualizada, consulte Context7 primeiro para
   bibliotecas, APIs, CLIs e serviços; depois use fontes oficiais na web.
5. Registre conhecimento, configuração, decisão, mudança de rotina ou nova orientação antes
   de concluir: atualize/crie a página canônica, adicione links internos e atualize o índice e
   o log.
6. Nunca modifique `raw/` nem registre senhas, tokens, chaves ou outros segredos.
7. Se o NAS estiver indisponível, declare que não conseguiu consultar a wiki; jamais finja.

## Estado operacional volátil

IP, estado de VM/container, portas, jobs, capacidade, versões e saúde de serviços envelhecem
rapidamente. Para esses fatos:

1. Use a wiki para localizar a entidade e a fonte autoritativa.
2. Consulte o sistema ao vivo por uma interface de leitura apropriada.
3. Diferencie endereço LAN do host, bridge/rede interna e IP de container/pod.
4. Responda com o valor confirmado e identifique o escopo.
5. Se a confirmação acrescentar ou corrigir conhecimento, atualize a página canônica com
   fonte, data e aviso de volatilidade.

Não atualize a data de verificação de um documento inteiro quando apenas um campo foi
confirmado; anote a verificação junto ao campo para não sugerir que todo o inventário foi
revalidado.

## Registro obrigatório

Quando a tarefa criar algo, adquirir conhecimento, mudar uma rotina ou receber uma orientação:

1. Pesquise antes para evitar duplicatas.
2. Atualize a página canônica existente; crie uma nova somente se não houver local adequado.
3. Registre estado final, motivo, procedimento, implicações e proveniência úteis no futuro.
4. Não grave tentativa e erro sem conclusão, logs rotineiros, saída bruta ou progresso efêmero.
5. Nunca grave segredos; registre somente onde a credencial é administrada.
6. Atualize índice e log conforme a diretriz da base.
7. Considere a documentação parte do critério de conclusão, não uma oferta opcional posterior.

## Escrita concorrente

Vaults sincronizados podem mudar entre leitura e patch por ação de outro agente, editor ou
processo de sincronização.

1. Releia o trecho-alvo imediatamente antes de cada edição.
2. Se o arquivo mudou, reconcilie a versão nova com a alteração pretendida; não force o texto
   antigo por cima.
3. Procure se outro processo já criou a seção, entrada de índice ou log pretendida.
4. Mescle conteúdo complementar e remova duplicações sem perder informação mais recente.
5. Corrija atribuições imprecisas: não diga “confirmado pelo usuário” quando a evidência veio
   de uma consulta ao vivo, por exemplo.
6. Depois da escrita, releia os trechos modificados e confirme consistência entre página,
   índice e log.

## Critérios de qualidade

- Uma entidade tem uma página canônica reconhecível.
- Fatos operacionais indicam fonte, escopo e data de confirmação.
- Retratos datados não são apresentados como estado atual sem verificação.
- Índice descreve a página atual, não uma versão antiga.
- Log é append-only e não contém entradas duplicadas para a mesma operação.
- Links internos conectam conceito e implementação sem copiar indiscriminadamente.
- A resposta ao usuário permanece direta; a manutenção da wiki ocorre nos bastidores.

## Pitfalls

- Não confunda IP do host com IP de bridge Docker, pod ou container.
- Não crie uma segunda seção só porque o título existente usa outra redação.
- Não use memória persistente como prova do estado atual.
- Não sobrescreva edição concorrente com um patch preparado sobre conteúdo antigo.
- Não declare toda a base “verificada hoje” após checar apenas um dado.
- Não encerre uma mudança relevante com “posso documentar se desejar”.
