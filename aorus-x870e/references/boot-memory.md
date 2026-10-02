# POST / treino de DDR5 no PCL

Quando o utilizador disser que o boot “ficou parado a testar as memórias”, isso é **AGESA no firmware**, antes do rEFInd. Não é o Linux, não é memtest da ESP, não é o HDD.

Detalhe medido e o padrão da semana: wiki `pcl-boot-am5-memory-training`.

## Confirme no host (não precisa de root)

```fish
systemd-analyze
```

O campo `firmware` é o POST. Referência neste kit:

- **~22 s** — Memory Context Restore aproveitado (reboot quente, alguns cold boots)
- **~1,5–3 min** — treino completo DDR5 EXPO 6000 (cold boot longo, 5VSB cortado, MCR Auto falhou)

## Kit

- 2×16 GiB TeamGroup UD5-6000 nos DIMM 1 (canais A/B), 6000 MT/s
- BIOS FB1a (2026-03-11)
- Sem ECC; MCE/EDAC limpos no boot de 2026-09-08

## Não “consertar” no Linux

Kernel, initramfs e unidades systemd não encurtam essa tela. Se o `firmware` estiver em ~22 s e o resto lento, aí sim é bootloader/disco/userspace.

## BIOS (só se o utilizador quiser cold boot mais curto)

Tweaker / AMD CBS: **Memory Context Restore = Enabled** (não Auto). Fast Boot. Não cortar PSU/UPS se quiser persistir o contexto. Não baixar EXPO só por um POST longo depois de dias desligado.
