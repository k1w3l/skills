---
name: stalwart-jmap-operations
description: >-
  Operar, diagnosticar e alterar com segurança integrações de e-mail Stalwart via JMAP,
  incluindo descoberta de sessão, cliente remoto por SSH, URL base, autenticação com App
  Password, listagem e classificação não destrutiva, health checks e falhas de proxy.
  Use quando houver menção a Stalwart, JMAP, .well-known/jmap, mailagent, mailctl.py,
  automações ativas de e-mail, Categorias/Importados, erro 502/401/timeout no endpoint de
  e-mail ou troca entre DNS público e IP LAN. Não use Bichon ou Gmail como fallback implícito.
---

# Operações Stalwart/JMAP

Esta skill governa a camada ativa de consulta, classificação e automação de e-mail via JMAP.
O objetivo é separar corretamente transporte SSH, descoberta JMAP, autenticação, operações de
mail e proxy reverso; mudar configuração somente após validar o endpoint candidato; e comprovar
o resultado com uma operação real não destrutiva.

Para detalhes do ambiente do Sr. Kiwel, leia `references/kiwel-stalwart.md`. Trate endereços,
portas e caminhos ali como estado documentado que deve ser reconfirmado antes de uma mudança.
Para importação por Imapsync, reativação de cron, wrappers de dry-run, deduplicação e redução de
falsos positivos, leia `references/inbox-automation-hardening.md`.

## Princípios de segurança

- Credenciais JMAP permanecem no servidor de e-mail; nunca as copie para o agente, wiki, log
  ou resposta.
- Ao inspecionar um arquivo de ambiente, leia somente a chave não secreta necessária, como
  `JMAP_BASE_URL`; não imprima o arquivo inteiro.
- Use App Password da conta de e-mail para JMAP Mail. Não presuma que API key administrativa
  substitui autenticação de usuário.
- Prefira operações de leitura para diagnóstico: `health`, `mailboxes`, consultas limitadas e
  leitura de metadados.
- Não apague mensagens, remova associações originais, mova e-mails para fora de `Importados/*`
  nem altere conteúdo sem autorização explícita e escopo confirmado.
- Se uma execução remota ou elevação de privilégio for negada pelo controle de segurança, não
  contorne, reformule ou tente outra via; informe que nada mudou e aguarde nova autorização.

## Diagnóstico em camadas

Teste cada camada separadamente para não confundir “SSH funciona” com “JMAP funciona”.

### 1. Transporte SSH

Confirme autenticação não interativa e disponibilidade do utilitário remoto. Um shell que
responde não prova acesso ao correio; ele prova apenas transporte.

Exemplo:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 USUARIO@HOST \
  'python3 /caminho/mailctl.py --help'
```

### 2. Descoberta e saúde declarada

Use o comando canônico do cliente para exercitar carregamento seguro do ambiente e descoberta
em `/.well-known/jmap`:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 USUARIO@HOST \
  'python3 /caminho/mailctl.py health'
```

Leia a implementação antes de chamar esse teste de “fim a fim”. Alguns clientes constroem a
sessão e imprimem `status: ok` sem fazer um POST em `apiUrl`; nesse caso, `health` comprova apenas
descoberta, autenticação da sessão e seleção de conta. Registre também o `apiUrl` efetivo que o
cliente informa. Um `curl` público isolado continua não sendo prova de capacidade JMAP Mail.

### 3. Operação de leitura obrigatória

Depois de `health`, execute uma listagem de caixas ou consulta pequena pelo mesmo cliente. Esta
é a prova de que o endpoint efetivo aceita uma chamada JMAP Mail:

```bash
ssh -o BatchMode=yes USUARIO@HOST \
  'python3 /caminho/mailctl.py mailboxes'
```

Se a saída contiver dados pessoais, resuma apenas contagens e nomes necessários; não despeje
mensagens na resposta. Quando houver bridge ou wrapper do scheduler, repita uma consulta curta
por esse caminho também — sucesso do CLI não garante que a automação use a mesma resolução de
URL.

### 4. Pitfall: `apiUrl` anunciado pode voltar ao DNS público

A descoberta JMAP retorna um objeto de sessão com `apiUrl`. Alterar somente
`JMAP_BASE_URL` pode mudar `/.well-known/jmap`, mas o cliente ainda pode seguir o `apiUrl`
absoluto anunciado pelo servidor e voltar ao domínio público/proxy. O padrão de falha é:

1. o endpoint LAN de descoberta responde;
2. `health` mostra `status: ok`;
3. o `apiUrl` exibido continua no DNS público;
4. `mailboxes` ou outra chamada POST falha no proxy, frequentemente com 502.

Para um agente LAN que deve permanecer no endpoint configurado, preserve apenas path e query do
`apiUrl` anunciado e substitua scheme/host/port pela base configurada:

```python
advertised = urllib.parse.urlsplit(session["apiUrl"])
api_path = advertised.path or "/jmap/"
if advertised.query:
    api_path = f"{api_path}?{advertised.query}"
effective_api_url = f"{configured_base.rstrip('/')}{api_path}"
```

Prefira esse override no cliente específico a alterar a URL pública anunciada globalmente pelo
Stalwart, pois a mudança global pode quebrar clientes externos. Faça backup do cliente antes do
patch, valide sintaxe e preserve dono, grupo e modo do arquivo ativo.

## Interpretação de falhas

- Falha SSH/DNS/timeout antes do comando: transporte ou rede até o host remoto.
- `401`/`403` no cliente autenticado: credencial, conta, permissão ou contrato de autenticação.
- `404` em `/.well-known/jmap`: URL base, roteamento ou publicação incorreta.
- `502`/`503` no endereço publicado: o proxy respondeu, mas o upstream JMAP não ficou
  disponível; investigue proxy, porta de destino e saúde do serviço antes de trocar senha.
- Sessão descoberta e `health` positivo, mas `mailboxes` falha: primeiro compare o `apiUrl`
  anunciado com a URL efetiva. Se o cliente voltou ao DNS público, corrija o roteamento do
  cliente; só depois investigue capacidade JMAP Mail, accountId ou permissão da conta.
- Saída de shell genérica após um comando como `help`: teste inválido; use explicitamente o
  utilitário e o subcomando `health`.

Não transforme um incidente transitório em regra permanente. Reexecute o teste canônico após a
correção e registre apenas a causa confirmada.

## Troca segura de `JMAP_BASE_URL`

1. Consulte a documentação operacional e descubra onde o serviço JMAP escuta de fato.
2. Leia somente o valor atual de `JMAP_BASE_URL` e os metadados do arquivo (dono, grupo e modo).
3. Teste o endpoint candidato antes de editar, incluindo `/.well-known/jmap`.
4. Não suponha que um IP sem porta usa a porta correta. Ao bypassar proxy reverso, a porta
   publicada diretamente costuma ser diferente de 80/443.
5. Se o usuário escreveu um endereço exato que não responde, não substitua silenciosamente por
   outro. Mostre o achado e obtenha decisão; se a intenção foi “usar o IP direto funcional”,
   escolha a porta verificada.
6. Crie backup timestamped no mesmo diretório; preserve dono, grupo e permissões do arquivo
   ativo e mantenha o backup ao menos tão restritivo quanto o original.
7. Faça substituição direcionada apenas da chave `JMAP_BASE_URL`; recuse arquivo ambíguo, chave
   ausente ou duplicada.
8. Execute `health` e compare o `apiUrl` anunciado/efetivo com a base desejada.
9. Execute uma operação JMAP Mail real e não destrutiva. Se ela voltar ao domínio público,
   aplique o override de path/query no cliente descrito acima, com novo backup e validação de
   sintaxe.
10. Repita a operação pelo bridge/script realmente usado pelo scheduler.
11. Se qualquer verificação falhar sem uma causa compreendida, restaure o backup e repita os
   testes.
12. Só então atualize jobs, documentação ou estado persistente que dependam da URL.

## Restrições de permissão

Arquivos de ambiente podem ser root-owned e deliberadamente não graváveis pelo usuário SSH.
Isso é uma proteção, não um defeito a contornar.

- Descubra o mecanismo autorizado de alteração: comando restrito, sudo específico, acesso de
  administração ao LXC ou alteração pela plataforma de configuração.
- Não alargue permissões, não adicione o agente a `sudo`/`docker` e não copie segredos para um
  arquivo gravável apenas para concluir a tarefa.
- Se faltar um caminho autorizado, pare antes da escrita e peça autorização ou acesso adequado.

## Verificação de automações

Uma correção de endpoint não termina no `health` se existirem rotinas agendadas:

1. execute uma consulta pequena pelo mesmo bridge/script usado pelo scheduler;
2. valide ao menos um job em modo não destrutivo ou dry-run;
3. confirme que erros continuam produzindo código de saída não zero;
4. evite consumir estado de deduplicação em testes de alerta;
5. não use sucesso do cron como prova se o wrapper captura exceções e retorna zero.

### Imapsync e keywords exclusivas do destino

Imapsync habilita `--resyncflags` por padrão. Em um destino já classificado, isso pode remover
keywords JMAP que existem apenas no Stalwart, como `agent-processed`, a cada sincronização. A
rotina de importação deve usar `--noresyncflags` quando automações gravam flags/keywords no
destino.

Validação obrigatória após essa mudança:

1. processe a Inbox até `pending` ficar vazio e registre os totais;
2. não interrompa uma execução ativa de `docker compose run --rm` apenas para acelerar a prova;
   aguarde a passagem atual terminar e valide a seguinte, pois parar somente o wrapper systemd
   pode deixar o container continuando sem o lock;
3. execute ou acompanhe uma passagem real do Imapsync pela Inbox;
4. compare total, processadas e pendentes antes/depois;
5. aceite pendências novas somente quando corresponderem a mensagens efetivamente copiadas na
   passagem;
6. confirme que a contagem de mensagens já processadas não diminuiu e então processe eventuais
   mensagens novas.

### Imapsync e exclusão mútua entre execuções

Não trate `flock` ao redor de `docker compose run --rm` como proteção suficiente: o processo
Compose pode ser encerrado enquanto o container continua no daemon, liberando o lock e
permitindo outra execução. Investigue unit, timer, containers e journal antes da correção.

O padrão durável combina lock de arquivo, detecção de qualquer container ativo pelo label do
serviço Compose, nome fixo do container, tratamento de `TERM`/`INT` com limpeza e timer baseado
em `OnUnitInactiveSec`. Valide com uma segunda chamada concorrente e com uma unidade transitória
inofensiva que prove a remoção do container após sinal. Não interrompa a passagem real somente
para construir a prova.

No ambiente do Sr. Kiwel, leia `references/kiwel-stalwart.md` para os caminhos e nomes atuais e
administre diretamente por SSH root no LXC, sem salto pelo Proxmox.

## Relato final

Informe de modo conciso:

- camada SSH;
- URL base não secreta configurada e `apiUrl` efetivo utilizado;
- resultado de `health`, deixando claro se ele fez ou não uma chamada JMAP Mail;
- operação de leitura verificada pelo CLI e, quando aplicável, pelo bridge do scheduler;
- arquivo alterado e existência do backup, sem expor seu conteúdo;
- rollback realizado ou pendência de permissão, se houver.

Nunca declare a configuração corrigida apenas porque o arquivo foi editado.
