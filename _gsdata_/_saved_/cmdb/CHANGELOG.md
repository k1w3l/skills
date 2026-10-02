# Changelog do CMDB

Mudança real de configuração ou de política. O valor novo fica no inventário; aqui fica o motivo.

## 2026-09-23

- **`~/cmdb.md`** — o usuário corrigiu os IPs. Conferidos um a um contra `inventory/index.md`: batem. O aviso de que o rascunho repetia `192.168.1.13` saiu da skill. Motivo: o aviso passou a contradizer o arquivo.
- **Skill criada** a partir de `~/cmdb.md` (criticidade, risco, janela de mudança) reconciliado com `qm`/`pct` ao vivo, guest agent, portas dos CTs, `docker ps` da VM 101, Ingress do k3s e o SQLite do Uptime Kuma. Motivo: o rascunho repetia `192.168.1.13` em quase todos os CTs e não tinha CPU, disco, porta nem monitor.
- **CT 107** registrado como OpenBao em `192.168.1.14:8200`, não como template.
- **CT 113 Nexterm** em `192.168.1.12:6989` e **VM 114** em `192.168.1.46` entraram no mapa. O guest agent do Windows respondeu.
- **CT 111** com 1536 MB, como ampliado em 2026-09-22.
- **VM 116** com 4096 MB, balloon 2048, `onboot: 1` e tag `critical`.
