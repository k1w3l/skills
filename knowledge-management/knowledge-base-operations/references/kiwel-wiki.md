# Wiki unificada do Sr. Kiwel

## Localização

- Raiz: `/mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/`
- Diretriz canônica: `sobre-a-wiki.md`
- Páginas: `wiki/`
- Índice: `wiki/index.md`
- Log: `wiki/log.md`
- Fontes imutáveis: `raw/`

Leia `sobre-a-wiki.md` a cada tarefa; suas regras prevalecem sobre skills e memórias.

## Caminhos legados aposentados

Os vaults separados abaixo não são mais a topologia canônica:

- `/mnt/NAS/Sync/Documentos/Pessoal/Wiki/Wiki-Devops/`
- `/mnt/NAS/Sync/Documentos/Pessoal/Wiki/Wiki-Jarvis/`

O segmento final `wiki/` faz parte da raiz atual. Assim, a diretriz fica em
`/mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/sobre-a-wiki.md`, enquanto índice e log ficam
um nível abaixo, em `.../wiki/wiki/index.md` e `.../wiki/wiki/log.md`. Não derive caminhos
de memória nem tente manter duas bases em paralelo.

## Sequência operacional

1. Leia `sobre-a-wiki.md` e `wiki/index.md`.
2. Pesquise e leia páginas relevantes.
3. Para dado operacional volátil, consulte a fonte ao vivo antes de responder.
4. Atualize a página canônica se houver conhecimento novo ou confirmação relevante.
5. Atualize o índice quando a descrição ou o conjunto de páginas mudar.
6. Acrescente uma entrada ao log sem reescrever o histórico.
7. Releia os trechos finais e confira duplicatas ou edições concorrentes.

## Exemplo: identificar um host Docker

A página e o inventário indicavam a VM 101 como host Docker em `192.168.1.40`, mas o dado era
datado. A verificação correta consultou o QEMU Guest Agent no Proxmox e confirmou:

- interface LAN `enp6s18`;
- IPv4 `192.168.1.40/24`;
- MAC `BC:24:11:BC:28:90`.

As diversas bridges `172.x` e `192.168.x.1` vistas dentro do guest eram redes Docker internas,
não o endereço LAN pedido pelo usuário. O registro final foi feito na página canônica de
operações Docker, com fonte e data, e o índice/log foram reconciliados.

## Lição de concorrência observada

Durante a atualização, outro processo adicionou uma seção equivalente, alterou o índice e
incluiu uma entrada no log entre a leitura e o patch. O procedimento seguro foi:

1. interromper a tentativa de aplicar texto antigo;
2. reler página, índice e log;
3. combinar a distinção útil entre Docker/Compose e k3s;
4. remover a seção duplicada;
5. substituir a fonte imprecisa “confirmado pelo usuário” pela evidência real do QEMU Guest
   Agent;
6. verificar novamente os trechos finais.

Esse padrão vale para qualquer vault sincronizado ou editado por múltiplos agentes.
