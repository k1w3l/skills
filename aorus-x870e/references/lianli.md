# Lian-Li — daemon `lianli-linux-git`

## Resumo

As fans/RGB/LCD do gabinete Lian-Li **não** passam pelos chips ITE da placa.
Pacote AUR `lianli-linux-git` (`lianli-daemon` + `lianli-gui`), serviço de
**usuário** `lianli-daemon.service`. Hardware USB típico neste PCL: Winbond
`0416:8040`/`0416:8041` (SLV3TX/RX) e Luminary `1cbe:0005`.

O AUR **não** habilita o unit. GUI vazia (“No devices found / Is the daemon
running?”) depois de um restore é quase sempre o daemon `disabled`/`inactive`,
não USB e não a versão. Conferir com `systemctl --user status lianli-daemon`.

No Omarchy (2026-09-12) o pacote é **0.9.1** (já ligado ao FFmpeg 9). Não
voltar para 0.4.8 só por causa da GUI vazia — no CachyOS o 0.4.8 morreu por
SONAME (`libavutil.so.60`), não porque a versão em si falhasse em achar o
hardware. Correção no restore:

```fish
systemctl --user enable --now lianli-daemon.service
```

## Depois de um Syu: FFmpeg 9 (2026-09-10)

O binário de 2026-04-25 (`0.4.8-1`) ligava contra FFmpeg 8 (`libavutil.so.60`,
`libswscale.so.9`, `libavcodec.so.62`). O Syu subiu `ffmpeg` para 9.0.1
(`libavutil.so.61`). Não existe pacote `ffmpeg8` nos repos. Sintoma: crash-loop
do unit user, **127**, `error while loading shared libraries: libavutil.so.60`.

`evdi-dkms` (dependência para LCD) recompilou no mesmo update e **não** é a causa.

Correção: rebuild do AUR.

```fish
yay -S --rebuild lianli-linux-git
systemctl --user start lianli-daemon.service
```

Wiki: `pcl-lianli-openrgb`.

## Não misturar

`it87` / CoolerControl = headers da placa (CPU_FAN etc.). OpenRGB = IT5711 da
placa. Lian-Li = este daemon. Um Syu pode quebrar os dois daemons de userspace
ao mesmo tempo por libs diferentes; ainda assim são bugs independentes.
