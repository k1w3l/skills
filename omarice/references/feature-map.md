# Matriz de personalização Hyprland no Omarchy

Esta matriz delimita opções comuns e riscos; não é substituto da documentação da versão instalada. Confirme o arquivo que o Hyprland realmente carrega, a versão (`hyprctl version`) e os nomes de monitor/janela ao vivo.

## Áreas adequadas para ajustes isolados

| Área | Ponto Omarchy habitual | O que pode ser personalizado | Risco/validação |
|---|---|---|---|
| Espaçamento e borda | `~/.config/hypr/looknfeel.lua` | `general.gaps_in`, `gaps_out`, `border_size`, cores/gradientes | Baixo; confirme sintaxe Lua, recarregue e veja tiled/floating/fullscreen. |
| Aparência de janelas | `looknfeel.lua` | `decoration.rounding`, opacity, shadow, blur e efeitos nativos | Baixo a moderado; blur/sombras custosos podem piorar renderização. Prefira valores modestos e teste sem empilhar efeitos. |
| Animações | `looknfeel.lua` | folhas `windows`, `workspaces`, `fade`, `layers` e outras folhas aceitas pela versão; curvas Bezier/spring e estilos | Moderado; confira a árvore/estilos atuais. Faça uma família por vez. Não use `loop` contínuo para ângulos de borda/sombra/glow como padrão. |
| Regras de janela | módulo Lua efetivamente carregado, muitas vezes `hyprland.lua` | corresponder classe/título/workspace e aplicar opacity, border, rounding, blur, animação ou comportamento documentado | Moderado; ordem de regras importa. Use `hyprctl clients` para descobrir classe/título reais; valide regex e efeitos atuais na wiki oficial. |
| Atalhos | `bindings.lua` | binds do Hyprland/Omarchy sem substituir o conjunto inteiro | Moderado; imprima binds existentes e desfaça colisão antes de criar outro. Não mexa no atalho/launcher Omarchy salvo solicitação explícita. |
| Teclado e mouse | `input.lua` | layout, opções XKB, sensibilidade, aceleração e dispositivo | Moderado; preserve um atalho/terminal de recuperação, confira layout e dispositivo reais. |
| Monitores | `monitors.lua` | saída, modo suportado, posição, escala, transformação, mirror e campos documentados | Alto; use `hyprctl monitors all` e modos suportados. Saída desativada remove-a do layout e desloca janelas/workspaces. Evite modelines experimentais. |
| Layout/workspaces | regras/workflows Lua que a instalação já carrega | layout, gaps ou destino do workspace via regras atuais | Moderado; diferenças de seletores e semântica entre versões podem mover janelas ou espaços de trabalho. |
| Autostart | `autostart.lua` | aplicações que o usuário pediu para iniciar com a sessão | Alto; não inclua daemon, script de terceiros ou comando que troca a sessão sem pedido expresso. |

## Temas, fundos e cores

- Um overlay Hyprland pode ajustar as cores/decoração do compositor sem mudar o restante do ambiente. Preserve o tema Omarchy atual e confirme qual arquivo de tema gerado é carregado antes de escolher o ponto de override.
- O `colors.toml`/`omarchy theme set` é tema **global** do Omarchy; pode regenerar cores do shell, barra, menu, notificações e OSD. Não o use para uma personalização Hyprland-only. Só aplique tema global se o patrão pedir explicitamente mudança dos componentes que serão afetados.
- Wallpapers padrão e seleção de fundos pertencem ao shell Omarchy, não ao conjunto de configurações cosméticas do compositor. Não instale outro daemon, plugin ou picker nem edite a barra/launcher para obter fundo sem pedido explícito. A wiki local registra que o fundo stock é global e que opções por monitor requerem integração adicional: `(wiki: omarchy-wallpapers-monitores)`.
- Cores de borda podem usar gradiente quando suportado pela API atual. Não transplantar diretamente sintaxe antiga de `hyprland.conf` nem código Lua completo vindo de tema externo.

## Itens fora do padrão seguro

Exigem pedido explícito, análise específica de compatibilidade, backup de todos os arquivos envolvidos e estratégia de recuperação: plugins `.so`, shaders, mudanças de driver/kernel/GPU, `allow_tearing`, VRR/HDR/ICC, modelines, alterações de `autostart`, sessão/greeter/SDDM, novos daemons de wallpaper, ou instalação de pacote. Um efeito “visual” não é justificativa para alterar o sistema inteiro.

## Checagem pós-mudança

1. `hyprctl reload`
2. `hyprctl configerrors`
3. Readback da propriedade/regra/monitor afetado via IPC apropriada e observação do comportamento pedido.
4. Compare com o baseline. Qualquer erro novo ou regressão: rollback antes de mais experimentos.

A documentação oficial viva para sintaxe e avisos:

- [Configuração avançada / Lua](https://wiki.hypr.land/configuring/core/advanced-configuration/)
- [Opções de configuração](https://wiki.hypr.land/configuring/core/config-options/)
- [Animações](https://wiki.hypr.land/configuring/core/animations/)
- [Window rules](https://wiki.hypr.land/configuring/core/rules/window-rules/)
- [Monitores](https://wiki.hypr.land/configuring/core/monitors/)
- [Posicionamento de monitores](https://wiki.hypr.land/configuring/core/monitors/positioning/)
- [Performance](https://wiki.hypr.land/configuring/advanced-and-cool/performance/)
- [Uso de plugins](https://wiki.hypr.land/Plugins/Using-Plugins/)
- [Crashes and Bugs](https://wiki.hypr.land/Crashes-and-Bugs/)
- [Manual Omarchy: dotfiles](https://omarchy.org/manual/dotfiles/)
- [Manual Omarchy: criar tema](https://omarchy.org/manual/making-your-own-theme/)
- [Manual Omarchy: common tweaks](https://omarchy.org/manual/common-tweaks)
