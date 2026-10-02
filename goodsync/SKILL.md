---
name: goodsync
description: >-
  Use whenever the user installs, configures, authenticates, licenses,
  operates, or troubleshoots GoodSync Server/GoodServer or the GoodSync Job
  Server on Arch Linux, Omarchy, or another Linux host. Trigger for GoodSync,
  gs-server, gsync, the self-extracting .run installer, users.tix, settings.tix,
  GsAcct.tic, the local Web UI on port 11000, FileServer on 33333, Job Server
  on 33556, account enrollment, license activation, login failures, TLS
  certificate warnings, or the error Account Not Configured. Keep local
  GoodSync users separate from the GoodSync Account used by the Job Server.
compatibility: >-
  Linux with systemd; Arch/Omarchy package management; a visible terminal for
  the interactive installer and account/password prompts; sudo only when the
  installer requests privileged operations.
---

# GoodSync Server e Job Server no Linux

Use this skill as the operational runbook for the GoodSync installation on the
PCL/Omarchy host. It is based on the validated installation and the local wiki;
confirm live state before claiming that a service, listener, account, or login
works.

The PCL installation was validated with GoodServer for Unix/Linux `12.11.5.5`
and Arch package `libxcrypt-compat 4.5.2-1`. The downloaded self-extracting
installer identified itself as Makeself `2.2.0`; its metadata/check/list modes
are useful for inspection but do not replace a real installation check.

## Segurança e regra de credenciais

- Nunca leia, copie, imprima, registre ou versione senhas, hashes, tokens,
  cookies, chaves TLS ou o conteúdo completo de `users.tix`, `GsAcct.tic` e
  arquivos equivalentes.
- Em documentação, logs de trabalho e respostas, represente qualquer valor
  sensível por `[REDACTED]`. Não substitua esse marcador por um valor real.
- O usuário deve digitar a senha diretamente no instalador, na Web UI ou em um
  terminal visível. Nunca passe senha em prompt do agente, argumento de
  ferramenta, script, histórico do shell ou comando de background.
- Não automatize a confirmação de certificado como se fosse uma prova de
  identidade. O certificado local é autoassinado; use a exceção apenas para o
  host confiável e prefira um certificado confiável quando o serviço for
  publicado fora da LAN.
- O serviço roda como `kiwel`; trate `/etc/goodsync` como estado operacional
  sensível. Não coloque seus arquivos de conta em Git plano.

## Modelo de contas — não misturar identidades

Há quatro conceitos distintos:

| Identidade | Onde é administrada | Uso |
|---|---|---|
| Usuário Linux `kiwel` | `/etc/passwd` e PAM | Dono do processo/arquivos; não é automaticamente uma senha GoodSync |
| Usuário local GoodSync | `/etc/goodsync/server/users.tix` | Login e autorização do GoodSync Server local |
| Conta GoodSync | perfil `GsAcct.tic` | Conta online/associada usada pelo GoodSync e pelo Job Server |
| Conta do Job Server | `/etc/goodsync/gsweb/GsAcct.tic` | Perfil GoodSync que habilita a autenticação do Job Server |

O `UserID` local GoodSync pode se parecer com `kiwel` ou com uma versão
normalizada do endereço da conta, mas não se deve adivinhar o identificador.
Use o `UserID` mostrado na Web UI/arquivo de forma sanitizada e não confunda
`kiwel`, `-local-kiwel` e a conta GoodSync externa.

## Instalação correta no Arch/Omarchy

### Pré-requisitos

1. Confirme que o sistema é Arch/Omarchy, que `systemd` está disponível e que
   a sessão possui um terminal visível.
2. Use o instalador oficial `.run` baixado localmente. No PCL, o arquivo
   observado foi `~/Downloads/goodsync-linux-x86_64-release.run`.
3. Inspecione o instalador sem executá-lo para instalação:

```bash
/home/kiwel/Downloads/goodsync-linux-x86_64-release.run --info
/home/kiwel/Downloads/goodsync-linux-x86_64-release.run --check
/home/kiwel/Downloads/goodsync-linux-x86_64-release.run --list
```

4. Se o loader informar `libcrypt.so.1: cannot open shared object file`, a
   compatibilidade necessária no Arch é `core/libxcrypt-compat`:

```bash
sudo pacman -S --needed libxcrypt-compat
ldd /usr/bin/gsync
ldd /usr/bin/gs-server
```

Prossiga somente quando não houver biblioteca necessária marcada como `not
found`. Não interprete esse erro como incompatibilidade de arquitetura.

### Regra essencial: instalação interativa pelo usuário

Execute o script como o usuário que administrará o servidor, em um terminal
visível, seguindo todas as perguntas do próprio instalador:

```bash
cd ~/Downloads
chmod +x ./goodsync-linux-x86_64-release.run
./goodsync-linux-x86_64-release.run
```

Não execute o instalador inteiro com `sudo` e não pré-carregue variáveis de
conta, usuário ou senha antes de iniciá-lo. Não passe credenciais como
argumentos e não injete respostas por pipe. Essa instalação interativa é
importante porque o script cadastra corretamente o usuário e a senha local do
GoodSync em `/etc/goodsync/server/users.tix`. O instalador solicitará elevação
quando precisar escrever em caminhos do sistema; digite a senha local somente
no prompt visível.

Se o GoodSync já estiver instalado, altere o usuário/senha local pela Web UI,
na área **Account**, ou pelo procedimento local documentado pela versão
instalada. Faça a alteração em um terminal visível e reinicie o serviço depois;
nunca tente editar senhas no arquivo com `sed`, `awk`, editor não seguro ou
texto salvo em histórico.

### Avisos conhecidos do instalador

- `service: command not found` pode aparecer quando o instalador tenta chamar a
  interface SysV antiga. No Omarchy, isso não é fatal se a unit systemd for
  criada e o serviço ficar ativo.
- A mensagem de `GsAcct.tic` ausente no perfil temporário do instalador pode
  aparecer durante a instalação. Ela não substitui o cadastro posterior da
  conta do Job Server.
- Depois da instalação, confirme o resultado real; o código de saída do
  instalador sozinho não prova que o daemon está operando.

## Arquivos e processos importantes

| Item | Função |
|---|---|
| `/usr/bin/gs-server` | GoodSync Server/GoodServer local |
| `/usr/bin/gsync` | Cliente GoodSync e processo do Job Server |
| `/usr/share/goodsync-server` | Recursos da Web UI |
| `/etc/goodsync/server/users.tix` | Usuários e autenticação local GoodSync |
| `/etc/goodsync/server/settings.tix` | Configurações operacionais do servidor local |
| `/etc/goodsync/gsweb/GsAcct.tic` | Conta GoodSync do perfil do Job Server |
| `/etc/goodsync/gsweb/jobs-groups-options.tix` | Estado/opções de jobs e grupos do Job Server |
| `/etc/systemd/system/goodsync-server.service` | Unit systemd do GoodServer |
| `/var/log/goodsync-server` | Logs; não copie credenciais deles |

A unit validada no PCL usa:

```ini
Environment="GS_OS_SERVER_PROFILE=/etc/goodsync"
ExecStart=/usr/bin/gs-server /profile=/etc/goodsync/server /resources=/usr/share/goodsync-server
User=kiwel
Restart=on-failure
```

O perfil do CLI em `~/.goodsync` é separado do perfil operacional do daemon em
`/etc/goodsync`. Não altere um supondo que o outro será atualizado.

## Portas e URLs

| Serviço | Endereço validado | Observação |
|---|---|---|
| GoodSync Server Web UI | `https://127.0.0.1:11000/` | No PCL, o listener também respondeu em HTTP; `http://127.0.0.1:11000/` retornou 303 para o fluxo da UI |
| FileServer local | `127.0.0.1:33333` | Listener local do GoodSync Server |
| Job Server | `https://192.168.1.7:33556/web-ui` | Porta correta para o acesso remoto na LAN |

Não omita `:33556` no endereço remoto. `https://192.168.1.7/web-ui` não é o
endpoint do Job Server validado. A Web UI remota respondeu HTTP 200 no PCL.

O certificado apresentado pelo servidor é autoassinado/não validado
(`ssl_verify=20` nas verificações com `curl`). Um navegador pode exibir uma
página de erro de certificado ou `chrome-error://chromewebdata/`; isso não
prova falha de autenticação. No navegador real, confirme a exceção para o host
local confiável. Para diagnóstico não interativo, use somente:

```bash
curl -k -sS -o /dev/null -w 'http=%{http_code} remote=%{remote_ip} ssl=%{ssl_verify_result}\n' \
  https://192.168.1.7:33556/web-ui
```

## Fluxo operacional após instalar

Siga esta ordem para não deixar o GoodServer local e o Job Server em estados de
conta diferentes:

1. Acesse `https://127.0.0.1:11000/`. Se a variante HTTPS não abrir por causa
   do listener/certificado, teste `http://127.0.0.1:11000/`; no PCL ela
   respondeu HTTP 303.
2. Entre com o usuário local GoodSync cadastrado pelo instalador. A senha é a
   senha GoodSync local, não necessariamente a senha Linux.
3. Abra a aba **Account** e altere/vincule o servidor à **conta GoodSync**. Não
   confunda essa etapa com a edição da conta local em `users.tix`.
4. Reinicie o serviço para que o perfil e o processo filho sejam recarregados:

```bash
sudo systemctl restart goodsync-server.service
```

5. Deslogue da conta local e entre novamente com a conta GoodSync.
6. Abra **Licence**/**License** e ative uma licença para este PC. Confirme a
   ativação na própria UI; não registre a chave no chat, Git ou wiki.
7. Ative o **Job Server** usando o usuário local, conforme a UI solicitar.
8. Acesse `https://192.168.1.7:33556/web-ui` usando o usuário e a senha da
   conta GoodSync associada ao perfil do Job Server.

## Preparar a conta do Job Server

O GoodSync Server local e o Job Server não compartilham automaticamente a
conta. O perfil do Job Server precisa conter
`/etc/goodsync/gsweb/GsAcct.tic`. Sem esse arquivo, o endpoint de autenticação
pode retornar `Account Not Configured`/HTTP 500, independentemente do usuário
informado na tela.

Para criar ou atualizar o perfil, execute em um terminal visível e informe
interativamente os dados da conta. O endereço abaixo é apenas um marcador; não
registre nem substitua `[REDACTED]` nesta skill:

```bash
/usr/bin/gsync /profile=/etc/goodsync/gsweb \
  /gs-account-enroll='[REDACTED]'
```

O processo solicitará a senha. O valor real deve ser digitado diretamente no
terminal e não deve aparecer na linha de comando, no histórico ou em logs.
Depois, reinicie `goodsync-server.service` e valide a existência do arquivo
somente por metadados. Nunca leia seu conteúdo para diagnóstico:

```bash
sudo systemctl restart goodsync-server.service
stat -c '%A %a %U:%G %n' \
  /etc/goodsync/gsweb \
  /etc/goodsync/gsweb/GsAcct.tic \
  /etc/goodsync/gsweb/jobs-groups-options.tix
```

No estado validado do PCL, o diretório do perfil ficou em modo `700`, e
`GsAcct.tic` e `jobs-groups-options.tix` em modo `600`, pertencentes a `kiwel`.
Preserve essa proteção. Se for necessário ajustar permissões, faça-o sem
expor o conteúdo e confirme o serviço após a mudança:

```bash
chmod 700 /etc/goodsync/gsweb
chmod 600 /etc/goodsync/gsweb/GsAcct.tic \
  /etc/goodsync/gsweb/jobs-groups-options.tix
sudo systemctl restart goodsync-server.service
```

### Quando o terminal não aceita entrada

O instalador e o `gs-account-enroll` precisam de um TTY real para receber a
senha. Uma execução em background, pipe, painel não interativo ou processo
Hermes sem entrada pode ficar aguardando ou produzir:

```text
stty: 'standard input': Inappropriate ioctl for device
```

Pare esse caminho e peça ao usuário para abrir o próprio Alacritty/terminal e
executar o comando localmente. Não tente contornar digitando a senha em chat,
em variável enviada por ferramenta, em argumento ou em processo background.

## Diagnóstico baseado em evidência

Comece por estas leituras sem segredo:

```bash
systemctl show goodsync-server.service \
  -p LoadState -p ActiveState -p SubState -p ExecMainStatus -p User
systemctl is-enabled goodsync-server.service
ss -ltnp
```

Para uma instalação funcional, confirme:

- `/usr/bin/gsync` e `/usr/bin/gs-server` existem;
- `ldd` dos binários não mostra dependência `not found`;
- `goodsync-server.service` está `active/running`, com status principal `0`;
- a porta 11000 está escutando localmente;
- a porta 33333 está escutando localmente;
- a porta 33556 está escutando no endereço LAN esperado;
- a Web UI remota responde HTTP 200 com o certificado explicitamente tratado;
- `GsAcct.tic` existe no perfil `/etc/goodsync/gsweb`;
- a tentativa visual de login usa a identidade correta.

Leia logs sem despejar linhas que possam conter credenciais:

```bash
journalctl -u goodsync-server.service -b --no-pager
```

### Tabela de falhas conhecidas

| Sintoma | Causa provável | Tratamento |
|---|---|---|
| `libcrypt.so.1` ausente | Loader antigo exigido pelo instalador | Instalar `libxcrypt-compat`, verificar `ldd` e repetir o instalador |
| `service: command not found` | Sonda SysV legada | Verificar unit systemd, `is-enabled`, `is-active`, journal e listeners |
| Página sem conexão em `192.168.1.7/web-ui` | Porta do Job Server foi omitida | Usar `https://192.168.1.7:33556/web-ui` |
| `Account Not Configured` | Falta `gsweb/GsAcct.tic` | Fazer enrollment interativo da conta GoodSync e reiniciar o serviço |
| Usuário local não entra no Job Server | Conta local e conta GoodSync são identidades distintas | Usar a conta GoodSync vinculada ao perfil do Job Server |
| Chrome mostra `chrome-error`/aviso TLS | Certificado autoassinado | Aceitar a exceção no host confiável ou diagnosticar com `curl -k`; não desativar TLS permanentemente |
| Senha parece correta mas login falha | Senha Linux/local não é a senha GoodSync externa | Confirmar a conta na aba Account e redefinir a credencial pelo fluxo local, sem exibir a senha |
| Enrollment fica parado ou falha com `stty` | Não há TTY interativo | Executar no terminal real do usuário; não usar pipe/background |
| Serviço não sobe após alteração | Perfil/permissão/configuração inválida | Ler `systemctl status`, journal e permissões; não apagar arquivos nem contas |

## Regras para alterações posteriores

- Prefira a Web UI para editar usuários locais, a conta GoodSync, licença e
  opções do Job Server; confirme cada mudança pela UI e pelo estado do serviço.
- `/etc/goodsync/server/settings.tix` é o arquivo de configurações do servidor.
  Antes de qualquer edição manual, identifique a chave necessária e preserve
  permissões; não faça substituições amplas nem copie o arquivo para locais
  públicos.
- `/etc/goodsync/server/users.tix` é a fonte dos usuários/senhas locais. Não
  trate o nome do arquivo como autorização para expor seu conteúdo. Se a senha
  local precisar ser alterada depois da instalação, use a aba **Account** ou o
  mecanismo local da versão instalada, com entrada interativa segura.
- Não remova arquivos, contas, jobs, licenças ou perfis como tentativa de
  diagnóstico. Faça somente leituras, reinícios e ajustes mínimos autorizados;
  qualquer exclusão exige autorização explícita do patrão.
- Se a configuração for copiada para backup, mantenha-a cifrada e fora de Git
  plano; exclua logs e qualquer credencial dos artefatos públicos.

## Referência rápida de encerramento

Ao concluir uma instalação ou correção, informe apenas:

1. versão/binários confirmados;
2. dependências instaladas e verificadas;
3. unit e listeners confirmados;
4. perfil/arquivo de conta confirmado por metadados;
5. URL correta e estado HTTP/TLS;
6. o que ainda depende de ação visual do usuário, como aceitar o certificado,
   informar senha, concluir login ou ativar licença.

Fontes locais principais: `wiki: omarchy-dual-boot-pcl`, `wiki: sobre-a-wiki` e
o estado vivo do host. Documentação do fornecedor:
`https://www.goodsync.com/for-linux`.
