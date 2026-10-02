---
name: aorus-x870e
description: 'Referência de hardware do PCL (Gigabyte X870E AORUS PRO ICE, CachyOS) — controle de fans pelo driver it87, RGB/ARGB pelo OpenRGB, Bluetooth do módulo onboard WCN7850, e POST lento de DDR5 (treino AGESA). Use SEMPRE que a tarefa envolver hardware desta máquina — fans, PWM, curvas de ventoinha, CoolerControl, lm-sensors, hwmon, temperaturas, Super I/O, RGB, ARGB, OpenRGB, iluminação da placa, Bluetooth, pareamento, mouse ou teclado sem fio, boot lento na tela de memórias, POST, EXPO, ou drivers de placa-mãe — mesmo que o usuário não cite "Aorus", "X870E" nem o nome do chip. Dispare também em sintomas genéricos como "minhas fans sumiram", "não consigo controlar a ventoinha do CPU", "o RGB apagou depois de atualizar", "o mouse não pareia", "o boot ficou testando as memórias", ou quando algo desses subsistemas quebrar após atualização de kernel ou de pacote. Esta placa tem armadilhas específicas que já custaram horas de diagnóstico e são fáceis de repetir sem esta skill.'
---

# Hardware do PCL — Gigabyte X870E AORUS PRO ICE

Referência da máquina `PCL`: CachyOS, AMD AM5, placa **Gigabyte X870E AORUS PRO ICE**.
Cobre os subsistemas da placa que exigiram diagnóstico não-óbvio: **fans**, **RGB**, **Bluetooth**, e o **POST lento de DDR5** (tela de treino de memórias).

O valor desta skill não é a lista de comandos — é o conjunto de becos sem saída já mapeados.
Cada seção abaixo registra não só o que funciona, mas o que *parece* certo e está errado.

## Inventário dos chips

Saber qual chip faz o quê evita o erro mais comum aqui: tratar RGB e fans como o mesmo problema.
São chips ITE diferentes, com drivers diferentes, que não se afetam.

| Subsistema | Chip | Endereço / bus | Controlado por |
|---|---|---|---|
| Fans/temps (principal) | **IT8696E** rev 0 | ISA `0xa40`, MMIO `0xfe100000` | driver `it87` (DKMS) |
| Fans/temps (secundário) | **IT87952E** rev 1 | ISA `0xa60`, MMIO `0xfe110000` | driver `it87` (DKMS) |
| RGB / ARGB | **IT5711** | USB/SMBus | OpenRGB (fixado no rc2) |
| Wi-Fi / Bluetooth | **Qualcomm WCN7850** (QCNCM865) | USB `0489:e10d` | `btusb` + BlueZ |

BIOS de referência: **FB1a** (2026-03-11).

As fans **Lian-Li do gabinete não passam por nenhum desses chips** — vão por controlador
próprio (`lianli-linux-git`, USB Winbond/Luminary) e **não** pelo `it87`. Quando o usuário
disser "as Lian-Li funcionam mas a do CPU não", isso não é pista de que a placa está boa:
são caminhos totalmente independentes. O daemon Lian-Li **pode** morrer sozinho depois de
um Syu se o FFmpeg mudar de SONAME (FFmpeg 9 no 2026-09-10 → falta `libavutil.so.60`);
ver `references/lianli.md`. O OpenRGB pinado em rc2 tem a mesma classe de falha com
`mbedtls` 4 — ver `references/openrgb-rgb.md`.

## Antes de responder: confira o estado real

As informações aqui são de 2026-07-15 e descrevem uma máquina viva. Kernel, BIOS e pacotes mudam.
Confirme o estado atual antes de afirmar qualquer coisa como fato — leva segundos:

```bash
sensors                                    # o que o kernel expõe hoje
journalctl -k -b | grep -i it87            # quais chips o driver achou neste boot
dkms status | grep it87                    # o DKMS sobreviveu ao último kernel?
uname -r
```

Boa parte dos comandos de diagnóstico e toda correção exigem **root, e o `sudo` aqui pede senha**
(não é NOPASSWD). Você não consegue rodá-los sozinho. Peça ao usuário para colar o comando com o
prefixo `!`, que executa na sessão e traz a saída pra conversa. Monte um one-liner só, não uma
lista de cinco passos que ele vai ter que rodar um por um.

O shell padrão é **fish**. A ferramenta Bash roda `bash`, mas comandos entregues ao usuário caem no
fish — evite heredoc e `for ... done`; prefira formas neutras que funcionam nos dois.

## Onde ir

Leia o arquivo do subsistema em questão — cada um tem o histórico completo e as armadilhas:

- **`references/fans-it87.md`** — fans, PWM, curvas, CoolerControl, lm-sensors, hwmon, temperaturas,
  Super I/O, `it87-dkms-git`. Leia também quando o sintoma for "o CoolerControl não mostra minhas fans":
  o CoolerControl quase nunca é o culpado.
- **`references/openrgb-rgb.md`** — RGB, ARGB, iluminação da placa, zonas, perfis, e por que o
  OpenRGB está pinado. Leia antes de sugerir `pacman -Syu` sem ressalva. Se o RGB da placa
  apagou **e** o journal do autostart mostra `libmbed*.so` missing, é mbedtls 4 — não rc3.
- **`references/lianli.md`** — daemon `lianli-linux-git` (fans/RGB/LCD do gabinete). Se
  crash-loop 127 com `libavutil.so.*` missing, rebuild do AUR; não misturar com `it87`.
- **`references/bluetooth.md`** — Bluetooth, pareamento, mouse/teclado sem fio, quedas de conexão.
- **`references/boot-memory.md`** — POST parado em “teste de memórias”: treino AGESA DDR5, não o Linux. Medir com `systemd-analyze` (campo `firmware`). Wiki: `pcl-boot-am5-memory-training`.

## O princípio que resolveu os dois casos difíceis

Tanto o caso das fans quanto o do RGB foram resolvidos pela mesma pergunta:
**a camada que o usuário está olhando está apenas refletindo uma camada abaixo?**

O CoolerControl não "perde" fans — ele exibe o que o kernel expõe via hwmon. Se um header não
aparece nele, o problema está no driver, e mexer no CoolerControl é perder tempo. O mesmo vale
pro OpenRGB e as zonas do IT5711.

Então, diante de qualquer sintoma aqui: desça uma camada antes de propor conserto. Vá do software
de controle → sysfs/hwmon → log do kernel → driver. A causa raiz esteve no driver nas duas vezes.

## Armadilha que atravessa todos os subsistemas

**Nomes de chip ITE são traiçoeiramente parecidos.** A documentação do kernel lista o `IT8689E`
como suportado; esta placa tem o **IT8696E**, que é outro chip. Essa diferença de um dígito já
descarrilou um diagnóstico nesta máquina — levou à conclusão errada de que o driver mainline
serviria. Sempre leia o ID do chip da saída real (`journalctl -k -b | grep -i it87`) em vez de
deduzir da documentação ou da memória.
