---
name: ajuste-cedilha
description: Diagnosa e corrige o problema do cedilha (ç) aparecendo como ć ou outro caractere errado em sistemas Linux. Use esta skill sempre que o usuário reportar que a tecla cedilha não funciona corretamente, que ç aparece como ć, que caracteres especiais do português (PT-BR) não estão sendo interpretados certo, ou quando houver problemas de layout de teclado para português brasileiro no Linux — especialmente em sessões Wayland (Niri, Sway, Hyprland) com teclados configurados via QMK/VIA ou com layout us-international. Aplica-se também a problemas similares com outros caracteres com dead keys no Linux.
---

# Ajuste de Cedilha no Linux (PT-BR)

## Contexto do problema

O layout `us intl` (US Internacional) mapeia `dead_acute + c` → `ć` (U+0107, c com agudo), **não** `ç` (U+00E7, cedilha). Isso afeta qualquer teclado — físico, QMK/VIA, ou virtual — que envie essa sequência de tecla morta. É o comportamento padrão do XKB e não um bug.

## Diagnóstico inicial

Execute para entender o estado atual:

```bash
# Layout XKB ativo
localectl status

# Verificar se input method está rodando
pgrep -a fcitx5; pgrep -a ibus

# Variáveis de input method na sessão atual
echo "GTK: $GTK_IM_MODULE | QT: $QT_IM_MODULE | XMOD: $XMODIFIERS"

# Override XCompose do usuário
cat ~/.XCompose 2>/dev/null || echo "não existe"
```

**Confirma o problema quando**:
- Layout XKB é `us` com variante `intl`
- `GTK_IM_MODULE`, `QT_IM_MODULE`, `XMODIFIERS` não estão definidas
- `~/.XCompose` não existe ou não tem regra para cedilha

> **Dica**: `echo $GTK_IM_MODULE` só mostra o valor no shell atual. Para ver se as variáveis carregaram na sessão systemd (afeta apps lançados pelo compositor), use:
> ```bash
> systemctl --user show-environment | grep -E "GTK_IM|QT_IM|XMODIFIERS"
> ```

## Correção 1 — XCompose override (resolve para a maioria dos apps)

Criar ou editar `~/.XCompose`:

```
include "%L"

<dead_acute> <c>  : "ç"  ccedilla
<dead_acute> <C>  : "Ç"  Ccedilla
```

**Por que funciona**: libxkbcommon (usado por Niri, Sway, Hyprland, apps GTK4, Qt6, terminais) lê `~/.XCompose`. A linha `include "%L"` herda todas as outras sequências do locale e apenas sobrescreve o cedilha.

**Nota**: muda o comportamento de todos os teclados da sessão para `dead_acute + c` → `ç`. Para usuários PT-BR que nunca precisam de `ć`, é o comportamento desejado.

## Correção 2 — Variáveis de ambiente para input method

Necessário para apps Electron (VS Code, Discord), Qt5, SDL e outros que não usam libxkbcommon diretamente.

Criar `~/.config/environment.d/91-input-method.conf`:

**Para Fcitx5:**
```ini
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
SDL_IM_MODULE=fcitx
GLFW_IM_MODULE=ibus
```

**Para IBus:**
```ini
GTK_IM_MODULE=ibus
QT_IM_MODULE=ibus
XMODIFIERS=@im=ibus
```

Arquivos em `environment.d/` são carregados pelo `pam_env` no início de cada sessão — **requer logout e login** para ter efeito.

**Sem precisar fazer logout** (injetar na sessão atual para novos apps):
```bash
systemctl --user set-environment \
  GTK_IM_MODULE=fcitx \
  QT_IM_MODULE=fcitx \
  XMODIFIERS=@im=fcitx \
  SDL_IM_MODULE=fcitx
```
Apps já abertos não são afetados; apenas os que forem lançados depois.

## Correção 3 — Autostart do input method no compositor

Se Fcitx5/IBus não estiver no autostart, as correções 1 e 2 podem falhar em partes da sessão.

### Niri (`~/.config/niri/cfg/autostart.kdl`):
```kdl
spawn-at-startup "fcitx5" "-d" "--replace"
```

### Sway (`~/.config/sway/config`):
```
exec fcitx5 -d --replace
```

### Hyprland (`~/.config/hypr/hyprland.conf`):
```
exec-once = fcitx5 -d --replace
```

### Omarchy (Hyprland + unit systemd)

O Omarchy **já** sobe o IME com `omarchy-fcitx5.service` (`fcitx5 --disable notificationitem`). **Não** adicionar `exec-once` / `o.launch_on_start` do fcitx5 — duplicar instâncias reescreve `~/.config/fcitx5/profile` no boot.

Layout da sessão: `~/.config/hypr/input.lua` (o default lê `/etc/vconsole.conf` e vem `us` **sem** `intl`):

```lua
hl.config({
  input = {
    kb_layout = "us",
    kb_variant = "intl",
    kb_options = "compose:caps,shift:both_capslock_cancel",
  },
})
```

`~/.XCompose` do Omarchy já inclui o ficheiro empacotado (emoji + `include "%L"`). Acrescentar as regras de cedilha **depois** desse include. Aplicar com `omarchy-restart-xcompose`, não com um segundo fcitx.

Manter `~/.config/autostart/org.fcitx.Fcitx5.desktop` com `Hidden=true`. Completar `GTK_IM_MODULE` em `~/.config/environment.d/91-input-method.conf` — o `10-omarchy-fcitx.conf` empacotado não define GTK.

Detalhe do PCL: wiki `teclado-us-intl-cedilha`.

### GNOME / KDE Wayland:
Geralmente não precisa de configuração manual — usar Gerenciador de Entrada do sistema.

## Configuração QMK/VIA

Se as correções de sistema não resolverem, o QMK pode estar enviando a sequência errada.

No layout `us intl`:
- `dead_acute + c` = `ć` — **errado para PT-BR**
- `dead_cedilla + c` = `ç` — **correto**
- `AltGr + ,` = `dead_cedilla` (via XKB)

Em QMK, para produzir `ç` corretamente com `us intl` no OS:
- Macro: `RALT(KC_COMM)` seguido de `KC_C`
- Ou Unicode mode: `UC(0x00E7)` (requer configuração de Unicode no QMK)

## Macro VIA (usevia.app) — modo Unicode Windows não funciona no Linux

**Sintoma**: ao pressionar o atalho configurado no VIA, aparecem os dígitos literais `0199` (ou outro código) no lugar do caractere especial.

**Causa**: o modo Unicode padrão do QMK/VIA usa o método Windows (`Alt + código decimal`). No Windows, `Alt+0199` = Ç, mas no Linux esse método não existe — o sistema interpreta os Alt+numpad como caracteres normais e os dígitos aparecem na tela.

**Não confundir codepoints**:
- Ç = **U+00C7** (hex `C7` = decimal 199)
- Windows usa decimal → `Alt+0199` → Ç
- Linux GTK usa hex → `Ctrl+Shift+U` + `00c7` + Enter → Ç
- **U+0199** (hex `0199`) = ƙ (Latin Small Letter K with Hook) — caractere completamente diferente

### Correção: reconfigurar o macro no VIA para o método Linux

No [usevia.app](https://usevia.app), edite o macro e substitua pela sequência:

| Passo | Ação |
|-------|------|
| 1 | `Down` → Left Ctrl |
| 2 | `Down` → Left Shift |
| 3 | `Tap` → U |
| 4 | `Up` → Left Shift |
| 5 | `Up` → Left Ctrl |
| 6 | `Tap` → 0 |
| 7 | `Tap` → 0 |
| 8 | `Tap` → C |
| 9 | `Tap` → 7 |
| 10 | `Tap` → Enter |

Isso envia `Ctrl+Shift+U` → digita `00c7` → Enter — o método de entrada Unicode do Linux (GTK/IBus).

**Para ç minúsculo** (U+00E7): mesma lógica, digitar `00e7` nos passos 6–9 (0, 0, e, 7).

## Checklist de verificação

```
[ ] ~/.XCompose criado com as regras de cedilha
[ ] ~/.config/environment.d/91-input-method.conf criado
[ ] Input method (fcitx5/ibus) no autostart do compositor
[ ] Logout e login realizados
[ ] Testado em: terminal, navegador, editor de texto
```

## Solução de problemas

**Ainda `ć` após relog**:
```bash
pgrep fcitx5          # confirmar que está rodando
echo $GTK_IM_MODULE   # confirmar que a variável carregou
```

**Funciona no terminal mas não no navegador**:
- Chromium/Electron no Wayland usa o protocolo `text-input` do compositor — geralmente funciona se o input method estiver rodando
- Tentar: `chromium --gtk-version=4`

**XCompose sem efeito em app específico**:
- Apps GTK2 ou X11 clássicos podem não respeitar `~/.XCompose` via libxkbcommon
- Garantir que Fcitx5/IBus esteja configurado como input method (variáveis `GTK_IM_MODULE` etc.)

## Cedilha intermitente após reboot (caso PCL, 2026-07-08)

**Sintoma**: após reiniciar, o cedilha às vezes funciona, às vezes não — mesmo com XCompose, variáveis e fcitx5 corretos.

**Causas encontradas (duas somadas)**:

1. **Fcitx5 duplicado no boot**: o Niri (`spawn-at-startup fcitx5 -d --replace`) e o autostart XDG (`/etc/xdg/autostart/org.fcitx.Fcitx5.desktop`) subiam duas instâncias em paralelo; o `--replace` fazia uma matar a outra e ambas reescreviam `~/.config/fcitx5/profile` ao sair — o estado salvo variava por boot.
2. **`keyboard-br` como DefaultIM no fcitx5**: o atalho padrão Ctrl+Space (usado por editores pra autocomplete) trocava pro layout br sem o usuário perceber; no br, o apóstrofo vira dead_tilde e o ç some. O estado ficava salvo e era restaurado no boot seguinte.

**Diagnóstico**:
```bash
fcitx5-remote -n                      # IM ativo agora (keyboard-br = problema)
cat ~/.config/fcitx5/profile          # DefaultIM e lista de IMs do grupo
journalctl --user -b | grep -i fcitx  # duas instâncias subindo no boot?
```

**Correção aplicada**:
- `~/.config/autostart/org.fcitx.Fcitx5.desktop` com `Hidden=true` (fica só o spawn do Niri);
- `~/.config/fcitx5/profile` com um único IM `keyboard-us-intl` (mesma variante do Niri: `us intl`), sem `keyboard-br` — editar o profile SEMPRE com o fcitx5 parado, senão ele sobrescreve ao sair;
- Pra re-adicionar o layout br um dia: `fcitx5-configtool`.
