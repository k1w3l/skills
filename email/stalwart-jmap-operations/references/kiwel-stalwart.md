# Ambiente Stalwart/JMAP do Sr. Kiwel

Use estes dados para localizar componentes; reconfirme o estado ao vivo antes de qualquer
mudança. Nunca registre App Password, token, cookie ou conteúdo de mensagens.

## Topologia

- Administração root direta: `root@192.168.1.13` por SSH com chave; não usar o Proxmox como salto para a manutenção normal.
- Proxmox: `root@192.168.1.5`; referência apenas para a camada do hipervisor.
- LXC do Stalwart: CT `102`, IP `192.168.1.13`.
- Acesso operacional sem privilégio: `mailagent@192.168.1.13`.
- Cliente remoto: `/home/mailagent/mail-agent/mailctl.py`.
- Configuração: `/home/mailagent/mail-agent/agent.env`.
- Conta JMAP operacional: `arquivo@mail.kiwel.uk`.
- Bridge do Hermes: `~/.hermes/scripts/stalwart_email_routines.py`.
- Publicação externa: `https://mail.kiwel.uk` via Pangolin.
- Endpoint direto LAN: `http://192.168.1.13:8080`.

Sem porta explícita, `http://192.168.1.13/` usa 80 e não equivale ao listener 8080.

## Estado efetivo verificado em 2026-08-18

`JMAP_BASE_URL` usa `http://192.168.1.13:8080` e `JMAP_IMPORT_ROOT` usa
`Importados/Gmail/INBOX`. O arquivo de ambiente é root-owned e legível pelo grupo `mailagent`;
não deve se tornar gravável pelo agente.

O Stalwart responde à descoberta LAN, mas seu objeto de sessão anuncia o endpoint público
`https://mail.kiwel.uk/jmap/`. Por isso, trocar somente `JMAP_BASE_URL` permitia que `health`
passasse, enquanto a chamada de caixas ainda retornava ao proxy público e falhava.

O `mailctl.py` foi ajustado para manter scheme/host/port da base configurada e aproveitar apenas
path/query do `apiUrl` anunciado:

```python
advertised_api_url = urllib.parse.urlsplit(self.session["apiUrl"])
api_path = advertised_api_url.path or "/jmap/"
if advertised_api_url.query:
    api_path = f"{api_path}?{advertised_api_url.query}"
self.api_url = f"{base}{api_path}"
```

Não altere a URL pública anunciada globalmente pelo Stalwart apenas para atender o agente LAN;
isso pode afetar clientes externos. Prefira o override limitado ao cliente.

A importação é executada por `stalwart-imapsync.timer` no CT 102. O Compose em
`/root/stalwart/docker-compose.yml` deve manter `--noresyncflags`: sem essa opção, o padrão
`--resyncflags` do Imapsync remove a keyword `agent-processed` que existe apenas no destino e
faz o organizador reprocessar a Inbox.

A unidade chama `/usr/local/sbin/stalwart-imapsync-run`. Esse wrapper usa o lock
`/run/stalwart-imapsync.lock`, recusa qualquer container ativo com o label
`com.docker.compose.service=imapsync`, cria o container com o nome fixo
`stalwart-imapsync-job` e remove o container gerenciado ao receber `TERM`/`INT`. O timer usa
`OnUnitInactiveSec=30min`, contando o intervalo depois do fim da passagem anterior. Disparos
manuais devem usar `systemctl start stalwart-imapsync.service`, nunca um `docker compose run`
paralelo.

## Acesso administrativo para arquivos protegidos

O usuário `mailagent` não possui sudo e não deve receber privilégios amplos. Quando uma mudança
root-owned for explicitamente autorizada, conecte diretamente ao LXC:

```bash
ssh root@192.168.1.13 'COMANDO'
```

Não use `root@192.168.1.5` seguido de `pct exec 102` para a manutenção normal do Stalwart; o
Proxmox permanece apenas como camada de hipervisor.

Antes de editar:

1. leia somente a chave não secreta necessária e metadados do arquivo;
2. crie backup timestamped no mesmo diretório;
3. aplique substituição direcionada, recusando chave ausente ou duplicada;
4. valide a sintaxe antes da troca;
5. preserve dono, grupo e modo do arquivo ativo;
6. mantenha backups restritos e nunca exponha seu conteúdo.

## Verificação mínima obrigatória

`health` isolado não é prova fim a fim neste cliente: ele pode apenas descobrir a sessão e
construir o objeto. O resultado correto exige três camadas:

1. CLI remoto:

```bash
python3 /home/mailagent/mail-agent/mailctl.py health
```

O `apiUrl` efetivo deve permanecer em `http://192.168.1.13:8080/jmap/`.

2. Uma chamada JMAP Mail real e não destrutiva:

```bash
python3 /home/mailagent/mail-agent/mailctl.py mailboxes
```

Resuma a saída; não despeje mensagens ou metadados pessoais.

3. Uma consulta pequena pelo bridge usado pelas rotinas:

`~/.hermes/scripts/stalwart_email_routines.py`

Use `recent`/equivalente com limite mínimo e reporte apenas status/contagem. Isso comprova que o
scheduler importa o cliente corrigido e alcança o endpoint LAN.

## Contrato de integridade

Os comandos operacionais conhecidos são `health`, `mailboxes`, `pending`, `read`,
`ensure-mailbox` e `classify`. A automação deve preservar `Importados/*`, adicionar
`Categorias/*` e aplicar `agent-processed`; não deve apagar mensagens nem remover associações
originais sem autorização explícita.

## Wiki canônica

Vault: `/mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/`

- `wiki/agente-email-jmap.md`
- `wiki/stalwart-mail-stack.md`
- `wiki/runbook-stalwart.md`
- `wiki/seguranca-e-operacao-stalwart.md`
- `wiki/rotinas-automatizadas-jarvis.md`

Leia `sobre-a-wiki.md`, atualize a página canônica e `wiki/log.md` após uma mudança confirmada;
nunca edite `raw/`.
