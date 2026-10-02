---
name: openbao-tiberius
description: "Use when Tiberius needs secrets. Read OpenBao safely."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [OpenBao, secrets, Tiberius, homelab, infrastructure]
    related_skills: [openbao, homelab-monitoring]
created_by: "agent"
---

# OpenBao — perfil Tiberius

Esta é a skill operacional do perfil `tiberius` para leitura de segredos de infraestrutura. A skill `/openbao` importada é a referência geral; consultar `/openbao` sempre que houver dúvida sobre o cliente, AppRole, permissões ou comportamento do vault.

## Conexão obrigatória

- Arquivo de ambiente do perfil: `/home/kiwel/.config/openbao/tiberius.env`.
- Variável obrigatória: `OPENBAO_ENV=/home/kiwel/.config/openbao/tiberius.env`.
- Cliente operacional: `openbao-get`, atualmente resolvido em `/home/kiwel/.local/bin/openbao-get`.
- O arquivo contém as credenciais AppRole do perfil e deve permanecer protegido; nunca ler, imprimir, copiar, versionar ou registrar seus valores.
- O escopo deste perfil é exclusivamente `infra/*`. Não tentar ler `personal/*`, `pcl/*` ou o arquivo de ambiente de outro agente.
- O padrão de referência é `infra/<entidade> <secret>`, por exemplo `openbao-get infra/exemplo password`.

Uso seguro em Fish:

```fish
set -x OPENBAO_ENV /home/kiwel/.config/openbao/tiberius.env
set user (openbao-get infra/horus user)
set password (openbao-get infra/horus password)
# Usar $user e $password somente no POST /api/login autorizado; não executar echo,
# set sem argumentos, printf, logger ou qualquer outra operação que imprima valores.
unset user password
```

Em Python ou shell, executar o binário com `capture_output`/substituição de comando, `stdin` desconectado e sem shell interpolation do path ou da chave. Capturar o resultado apenas em memória e descartar depois do uso. Nunca executar `openbao-get` de forma que o stdout apareça no chat, no log ou em uma saída de diagnóstico.

## Paths do perfil

| Path e campo | Uso | Estado |
|---|---|---|
| `infra/horus user` | Usuário normal usado no login do monitor Horus | **Verificado no probe real** |
| `infra/horus password` | Senha do usuário normal usado no login do monitor Horus | **Verificado no probe real** |
| `infra/horus token` | Token de sessão/API fornecido pelo Horus após o login, não um segredo de entrada do perfil | **Não utilizado** |
|| `infra/proxmox token` | Token Proxmox, somente se uma tarefa futura exigir explicitamente esse segredo | Consultado por nomes de campo; não existe atualmente |
|| `infra/truenas token` | API key HTTPS de leitura do TrueNAS do homelab | **Verificado nesta sessão; valor nunca exposto** |

Não tratar qualquer token antigo ou variável de ambiente como substituto. O monitor Tiberius resolve cada credencial somente pelo path/campo OpenBao documentado, usa o valor apenas em memória durante a chamada autorizada e o descarta ao terminar. Para Horus, usa `infra/horus user` e `infra/horus password` no login; para TrueNAS, usa `infra/truenas token` na API HTTPS. Nenhum desses valores entra em documentação, logs ou respostas. Nenhuma rotina de monitoramento deve executar remediação automática.

## Quando o segredo não existir

1. Confirmar a ausência consultando apenas os nomes de campos do path, sem solicitar ou exibir valores.
2. Parar a operação dependente da credencial e manter falha fechada; não tentar outro path por adivinhação.
3. Solicitar ao operador a criação do segredo no OpenBao, informando somente o path e o nome do campo. Nunca pedir o valor pelo chat.
4. Depois que o operador confirmar a criação, verificar a presença do campo sem imprimir seu valor e executar apenas a operação originalmente autorizada.

Mensagem padrão: `O segredo OpenBao infra/horus user ou infra/horus password não foi localizado. Crie o campo ausente no vault do perfil Tiberius; não envie valores por chat. Depois da confirmação, farei uma verificação sem exibir as credenciais.`

## Regras de segurança

- Nunca usar `rbw`, Bitwarden, Hermes browser vault, token de entrada não validado, root token ou prompt interativo como fallback. Login e senha só podem vir dos campos OpenBao documentados.
- Nunca imprimir, logar, persistir, testar com valor real, colocar em memória durável ou incluir em relatório o token, `secret_id`, `role_id`, senha ou qualquer conteúdo do arquivo `tiberius.env`.
- Não enviar o valor do segredo a processos que não precisam dele. O `openbao-get` recebe somente o path e o campo, e seu stdout deve ser capturado.
- Não registrar headers `Authorization`, corpos de requisição, stderr do helper ou respostas que possam conter credenciais.
- Em 403, path fora do escopo ou erro de autenticação, parar e reportar apenas o código/estado sanitizado. Em vault selado ou indisponível, solicitar intervenção autorizada; nunca fazer unseal automático.
- Não alterar, revogar ou rotacionar segredos sem permissão explícita e sem plano de recuperação.
- Se um valor tiver quebra de linha, estiver vazio ou vier acompanhado de saída inesperada, rejeitar o resultado em vez de normalizá-lo.

## Integração com Horus

O monitor deve resolver `infra/horus user` e `infra/horus password` no início de cada processo curto, executar `POST /api/login`, validar `GET /api/me` como usuário normal e manter o token de sessão apenas durante as chamadas necessárias. A ausência de qualquer campo é uma falha de autenticação, não uma autorização para usar token antigo ou login alternativo. Nenhuma rotina de monitoramento deve executar remediação automática.
