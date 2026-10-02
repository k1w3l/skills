# Changelog do CMDB

Mudança real de configuração/política ou inclusão relevante de inventário. O valor novo fica no inventário; aqui fica o motivo.

## 2026-09-25

- **Horus Alarm Guardian — preloads Cron no catálogo canônico** — corrigidos os nomes antigos no array `skills` do job `85ee74c01df3` para `proxmox-status`, `wiki-pcl` e demais nomes/categorias válidos em `~/skills`. O perfil já tinha `skills.create_dir`/`external_dirs` corretos. O script de sync `9d57ccd39d75` passou a ler a allowlist em `~/skills/.tiberius-skill-sync.json`, validar 65 fontes canônicas e gravar apenas no namespace de destino dentro de `~/skills`. Teste isolado com destino scratch/stub de Telegram criou 65 symlinks; Cron doctor encontrou 9 jobs ativos sem problemas. Cinco execuções recentes do guardião não registraram skills ausentes (última `ok`). No destino real, 64 basenames colidem com arquivos vazios, 13 diretórios não colidem e um destino de skill falta; tudo permaneceu intacto e nenhuma execução manual do sincronizador ocorreu. Sem mutação Proxmox/Horus. Motivo: remover a busca explícita de caminhos legados e impedir que rotinas de skill usem árvores de compatibilidade como fonte.

## 2026-09-24

- **Nexterm — snapshot de validação de acesso** — criado `inventory/nexterm-access.md` e apontado pelo índice: 28 entradas enumeradas, 27 sessões/handshakes autenticados confirmados, Home Assistant SSH não confirmado em duas tentativas. Nenhuma configuração de guest/serviço foi alterada; sessões próprias confirmadas ausentes (DELETE enviado quando ainda ativas). Motivo: registrar a verificação solicitada sem confundir disponibilidade do Nexterm com acesso às entradas.
- **Horus Alarm Guardian — inclusão da CI** — criado `inventory/horus-alarm-guardian.md` e adicionado ao índice. Registro inicial do job ativo, dependências e limite de escopo/frescor identificado em leitura somente; nenhuma rotina ou infraestrutura havia sido alterada. Motivo: a página era referenciada pela wiki, mas não existia na CMDB.
- **Horus Alarm Guardian — escopo e frescor corrigidos** — o monitor agora observa alarmes ativos, findings materiais e health fresco, com debounce de dois snapshots; status reports renovam health acima de 12 h e marcam stale em falha. Pods K3s Ready/Running com somente `restart_count` cumulativo não abrem planos; boot pool TrueNAS mantém finding crítico específico. Atualizados prompt/skills do Cron; 35 testes direcionados e 54 testes da suíte total passaram. Em readback às 20:38Z, o evento real do boot pool estava `awaiting_approval`, com message ID e sem execução; plano somente leitura. Nenhuma mutação de infraestrutura. Motivo: relatórios repetiam diagnósticos stale e findings não cobertos pelo caminho de plano/aprovação.
- **Horus Alarm Guardian — fronteira de delegação/aprovação corrigida** — o usuário confirmou pré-autorização para qualquer handoff entre agentes; diagnósticos read-only não aguardam callback, e o agente delegado herda o mesmo escopo. Aprovação continua restrita à ação state-changing quando não houver autorização específica. O filtro Cron que rejeita URL HTTPS com IP privado literal permanece independente e não é contornado. Motivo: não confundir autorização para delegar com autorização de mutação nem com política de rede.


## 2026-09-23

- **`~/cmdb.md`** — o usuário corrigiu os IPs. Conferidos um a um contra `inventory/index.md`: batem. O aviso de que o rascunho repetia `192.168.1.13` saiu da skill. Motivo: o aviso passou a contradizer o arquivo.
- **Skill criada** a partir de `~/cmdb.md` (criticidade, risco, janela de mudança) reconciliado com `qm`/`pct` ao vivo, guest agent, portas dos CTs, `docker ps` da VM 101, Ingress do k3s e o SQLite do Uptime Kuma. Motivo: o rascunho repetia `192.168.1.13` em quase todos os CTs e não tinha CPU, disco, porta nem monitor.
- **CT 107** registrado como OpenBao em `192.168.1.14:8200`, não como template.
- **CT 113 Nexterm** em `192.168.1.12:6989` e **VM 114** em `192.168.1.46` entraram no mapa. O guest agent do Windows respondeu.
- **CT 111** com 1536 MB, como ampliado em 2026-09-22.
- **VM 116** com 4096 MB, balloon 2048, `onboot: 1` e tag `critical`.
