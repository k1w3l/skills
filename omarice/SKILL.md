---
name: omarice
description: Use when customizing or troubleshooting Omarchy/Hyprland appearance, animations, decorations, gaps, borders, blur, opacity, window rules, monitors, input, themes, or community rice/dotfiles such as HyDE, HyprRice, cozy-hyprland, and awesome-hyprland.
---

# omarice — personalização segura de Omarchy/Hyprland

Personalize o compositor sem substituir a arquitetura do Omarchy. O critério principal é preservar uma sessão utilizável e fazer alterações pequenas, reversíveis e verificadas.

## Acione e consulte

Use esta skill antes de qualquer personalização Hyprland/Omarchy, mesmo que pareça simples. **Carregue também a skill `omarchy`**: omarice acrescenta os limites abaixo, não substitui seus procedimentos. Siga `wiki-pcl`: consulte `wiki/index.md` antes de fontes externas; leia a página local pertinente, sobretudo `[[omarchy-hyprland-keybinds]]` e `[[omarchy-wallpapers-monitores]]` quando aplicáveis. Consulte a documentação oficial atual do Hyprland para a sintaxe exata da alteração; a sintaxe de regras e opções muda entre versões. Se faltar documentação técnica atual, use Context7 (`/hyprwm/hyprland-wiki`) e depois a wiki oficial.

## Limites de escopo

- O padrão é personalizar **somente o Hyprland** em arquivos do usuário em `~/.config/hypr/`. Nunca altere a barra do Omarchy nem o launcher/menu: não edite `~/.config/omarchy/shell.json`, extensões/menus, plugins Quickshell, widgets ou configurações de launcher, salvo pedido explícito do patrão para esse componente.
- Não aplique um tema global do Omarchy por padrão: `colors.toml` e `omarchy theme set` podem recolorir a barra, menu, notificações e OSD. Para uma aparência apenas do compositor, use um override Hyprland em vez de mudar a paleta global.
- Nunca edite arquivos do pacote em `/usr/share/omarchy/` nem arquivos gerados em `~/.local/state/omarchy/current/`. Leia-os se necessário; escreva apenas em overrides do usuário que a configuração ativa realmente carrega.
- Não execute instaladores ou scripts de rice (`install.sh`, `curl | sh`), não substitua dotfiles em lote e não instale pacotes, plugins, shaders ou componentes de login/autostart como efeito colateral de uma mudança visual. Só faça isso quando o pedido os incluir explicitamente e após revisar escopo, código e compatibilidade.
- Mudanças ordinárias dentro do escopo estão autorizadas sem confirmação por etapa; se forem tocar barra/launcher, ou qualquer componente fora do escopo solicitado, pare e obtenha pedido explícito.

## Fluxo seguro

1. **Identifique o estado real.** Leia a configuração de entrada e os arquivos atuais em `~/.config/hypr/`; confirme `hyprctl version`, `hyprctl configerrors` e, para trabalho de monitor, `hyprctl monitors all`. Registre o estado de erros antes da edição. Se já houver erros, não empilhe outra mudança: identifique a causa ou informe o bloqueio primeiro.
2. **Confirme o formato.** Omarchy mantém overrides Lua, em geral `hyprland.lua`, `looknfeel.lua`, `bindings.lua`, `monitors.lua`, `input.lua` e `autostart.lua`; confirme os includes em uso no sistema real. A documentação atual do Hyprland marca `hyprlang` como obsoleto desde 0.55 em favor de Lua. Não cole trechos antigos `.conf` em arquivos Lua nem suponha que exemplos de outro rice correspondam à versão instalada.
3. **Escolha o menor ponto de edição.** Aparência/decoração/animações: normalmente `looknfeel.lua`; binds: `bindings.lua`; monitor: `monitors.lua`; input: `input.lua`; regras específicas de janela: o módulo Lua já carregado que as contém. Preserve o conteúdo existente e a ordem de carregamento. Para reatribuir tecla, liste primeiro `omarchy menu keybindings --print`; use `hl.unbind(...)` antes do novo `o.bind(...)` quando houver conflito. Para regras de janelas, valide a sintaxe e os seletores na documentação oficial atual.
4. **Faça backup antes de cada gravação.** Copie cada alvo existente, preservando metadados, para `~/.local/state/omarice/backups/YYYYMMDD-HHMMSS/` com o caminho relativo original; se o mesmo arquivo receber outra gravação posterior, faça outro backup antes dela. Registre no manifesto os caminhos, hashes e arquivos que ainda não existiam. Verifique que a cópia está presente e legível. Se não conseguir criar e verificar o backup, não edite. Não faça retenção/prune automático dos backups.
5. **Aplique uma alteração pequena de cada vez.** Prefira valores nativos `hl.config(...)`, `hl.animation(...)`, `hl.curve(...)` e regras Lua atuais; não invente APIs nem transplante configurações de outra distribuição. Evite alterar simultaneamente compositor, drivers, variáveis globais e apps.
6. **Valide imediatamente.** Execute `hyprctl reload` e depois `hyprctl configerrors`; confirme também por IPC/estado real a configuração que mudou e faça uma checagem visual/funcional proporcional ao pedido. Não use `hyprctl reload full-reset` como atalho. Se a validação não ficar limpa, não continue para outra personalização.

## Estabilidade, crashes e rollback

Qualquer erro novo, travamento, artefato visual, regressão de desempenho ou encerramento/crash do compositor após a mudança é sinal para **rollback imediato**, não para tentar vários ajustes especulativos.

1. Restaure com `cp -a <backup> <arquivo-original>` usando o backup desta alteração; verifique o arquivo restaurado.
2. Se Hyprland ainda estiver vivo, rode `hyprctl reload` e `hyprctl configerrors`; confirme que voltou ao estado anterior. Se a sessão caiu ou ficou inutilizável, acesse um TTY (`Ctrl`+`Alt`+`F3`), restaure o backup e só então entre novamente na sessão.
3. Se esta alteração criou um arquivo que não existia, remova somente esse arquivo novo ao executar o rollback autorizado pelo patrão; não remova outros arquivos, backups ou configurações. Se o rollback falhar, pare, preserve os backups e reporte o estado e o caminho de recuperação; não reinicie display manager ou máquina como primeira tentativa.
4. Informe sempre o alvo alterado, o backup disponível, o resultado da validação e, se necessário, o comando exato para restauração. Não apague backups sem autorização explícita.

## Riscos a evitar

- Não use o instalador completo do HyDE nem copie sua árvore de dotfiles para uma instalação Omarchy existente. Projetos de rice podem substituir o compositor, sessão, shell, atalhos e dependências; mudanças entre Hyprland 0.55/0.56 também tornam configs antigas incompatíveis.
- Não trate o HyprRice como editor seguro do Omarchy: ele documenta caminhos para `hyprland.conf`, Waybar e Rofi, enquanto Omarchy usa Lua e protege a barra/launcher. Backup anunciado pelo app não substitui o backup verificado desta skill.
- Não trate `awesome-hyprland` como certificação de compatibilidade: é um catálogo. Avalie cada projeto e versão individualmente.
- Plugins Hyprland são código C++ carregado dentro do compositor; leia a fonte e confirme compatibilidade/ABI com a versão instalada antes de sequer considerar uso. Uma incompatibilidade pode impedir a carga ou provocar crash. Não instale plugin para obter efeitos que a configuração nativa já oferece.
- Não use animação contínua `loop` em ângulos de borda/sombra/glow por padrão: a wiki alerta que pode renderizar continuamente à frequência do monitor, aumentando uso de CPU/GPU e consumo. Blur pesado, wobble, shaders e efeitos empilhados também exigem teste isolado de desempenho.
- Alterações de monitor são de risco maior que cosméticas: confira nome, modos e posição ao vivo; não desative o monitor ativo principal nem use modeline/resolução especulativa. Altere esse domínio apenas se o pedido o exigir e mantenha uma rota de recuperação.

## Referências internas

- Para matriz do que personalizar e seus riscos: [`references/feature-map.md`](references/feature-map.md).
- Para leitura crítica dos repositórios citados: [`references/source-review.md`](references/source-review.md).
- Para procedimentos e experiência local: consulte as páginas wiki lidas e atualize/crie página, `index.md` e `log.md` após conhecimento ou mudança durável. Nunca registre segredos.
