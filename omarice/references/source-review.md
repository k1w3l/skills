# Repositórios de inspiração: leitura e limites

Os repositórios são fontes de ideias, não pacotes certificados para uma instalação Omarchy. Antes de reutilizar qualquer exemplo, confira o estado atual do repositório, a licença, a versão suportada do Hyprland, o conteúdo dos arquivos e o destino exato das alterações. Adapte só o trecho necessário em configuração de usuário; não execute scripts de instalação em lote.

## HyDE — `HyDE-Project/HyDE`

- Projeto de ambiente completo com scripts, dotfiles, temas, ferramentas e componentes além do compositor.
- Sua documentação/release atual descreve migração para Lua em Hyprland 0.55/0.56; arquivos antigos `.conf` e caminhos implantados por versões anteriores não são intercambiáveis.
- Pode inspirar paletas, animações e regras específicas. **Não** rodar `install.sh`, copiar `Configs/` ou implantar a sessão/shell sobre Omarchy. Extrair um valor isolado, conferir na wiki oficial da versão atual e inseri-lo no override Lua próprio.
- Cuidado particular com temas e Lua: código carregado pelo compositor é executável, não apenas decoração.

## HyprRice — `DuckyOnQuack-999/HyprRice`

- README descreve uma GUI para Hyprland e outros componentes, incluindo Waybar, Rofi, notificações e temas; anuncia preview e cópias de backup/rollback.
- Os caminhos de exemplo incluem `~/.config/hypr/hyprland.conf`, `~/.config/waybar` e `~/.config/rofi`; isso não corresponde ao formato/layout Lua do Omarchy atual e toca justamente na barra/launcher protegidos.
- Usar como catálogo de ideias para controles e preview, não como escritor automático. Não apontar a ferramenta para o perfil real do Omarchy sem autorização expressa, inspeção dos destinos, backup independente verificado e validação do que foi escrito.

## Awesome Hyprland — `hyprland-community/awesome-hyprland`

- Lista comunitária de apps, plugins, barras/shells, wallpaper managers e utilitários; é índice para investigação, não documentação normativa nem garantia de segurança, manutenção ou compatibilidade.
- Avalie o projeto individualmente: versão recente, compatibilidade com o Hyprland instalado, origem do pacote, permissões, código e impacto em Quickshell/bar/launcher. Não instale a lista em lote.
- Para sintaxe e comportamento do compositor, prevalece a wiki oficial do Hyprland; para o fluxo Omarchy, prevalece a skill `omarchy` e a documentação oficial Omarchy.

## Cozy Hyprland — `mistweaverco/cozy-hyprland`

- README descreve um conjunto minimalista de Waybar/menu para Hyprland com instruções para Manjaro e um `install.sh`.
- A arquitetura standalone de barra/menu diverge do Quickshell do Omarchy e conflita com a restrição de manter barra e launcher intactos. Não executar o instalador nem substituir o shell; usar somente uma referência estética, salvo pedido explícito para migrar esses componentes.

## Regra de precedência

1. Estado real e arquivos que a sessão Omarchy carrega.
2. Documentação oficial atual do Hyprland para API/sintaxe; documentação Omarchy para integração e paths.
3. Wiki pessoal lida para particularidades já descobertas no PCL.
4. Repositórios comunitários somente como inspiração sujeita a revisão.

Uma captura de tela ou demo que “funciona no Hyprland” não demonstra que seja segura para Omarchy, Lua atual, o hardware do patrão ou seus componentes protegidos.

## Fontes

- [HyDE](https://github.com/HyDE-Project/HyDE) e [guia de migração Lua](https://github.com/HyDE-Project/HyDE/blob/master/MIGRATION-LUA.md)
- [HyprRice](https://github.com/DuckyOnQuack-999/HyprRice)
- [Awesome Hyprland](https://github.com/hyprland-community/awesome-hyprland)
- [Cozy Hyprland](https://github.com/mistweaverco/cozy-hyprland)
- [Wiki oficial Hyprland](https://wiki.hypr.land/)
