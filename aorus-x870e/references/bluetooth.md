# Bluetooth — Qualcomm WCN7850 (onboard da X870E)

## Hardware

Adaptador Wi-Fi/BT onboard da placa: **Qualcomm WCN7850** (módulo QCNCM865).
USB `0489:e10d`, em `/sys/bus/usb/devices/1-6`.

## Ajustes já aplicados (2026-06-11)

Não são defaults — foram aplicados de propósito para estabilizar conexões. Confira se ainda estão
lá antes de concluir que "o BT está no padrão":

- `/etc/modprobe.d/btusb.conf`: `enable_autosuspend=0`
  (o autosuspend do `btusb` derrubava periféricos ociosos)
- `/etc/bluetooth/main.conf`:
  - `FastConnectable=true`
  - `JustWorksRepairing=always`
  - `ReconnectAttempts=10`
  - `ReconnectIntervals` explícitos

## Pegadinha: Attack Shark X11 troca de MAC ao parear

O mouse **Attack Shark X11** (aparece como `X11mouse2`) **anuncia com outro endereço MAC quando
entra em modo de pareamento** — mudou de `...:0C:CA:10` para `...:0D:CA:10`.

Consequência prática: parear pelo endereço que você já conhecia **falha**, e parece que o mouse
está com defeito. O certo é **escanear de novo com o mouse já em modo de pareamento**, pegar o
endereço recém-descoberto, e **manter o scan ativo durante o pair**.

Se o usuário disser "meu mouse não pareia" ou "o endereço sumiu", é quase certo que é isto.

## Sinal fraco

O sinal do X11 chegava fraco: **−73 dBm**. Se a instabilidade voltar, antes de mexer em software,
**confira a antena externa Wi-Fi/BT da placa** — conexão frouxa ou antena mal posicionada explica
quedas que nenhum ajuste de BlueZ resolve.
