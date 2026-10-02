# RGB / ARGB — OpenRGB e o controlador IT5711

## Resumo

O OpenRGB está **deliberadamente fixado em `1.0rc2-6.1`** no PCL, via `IgnorePkg` em
`/etc/pacman.conf`. Isso é intencional — **não é pacote desatualizado por descuido.**

Se aparecer um "openrgb: ignorando atualização" durante um `pacman -Syu`, está correto.
Não sugira remover o pin sem antes ler o motivo abaixo.

## Por que o pin existe

O upgrade pro `1.0rc3` (2026-07-08) **mudou o layout de zonas do controlador IT5711** da placa:
de 4 zonas para 6 — `LED_C` foi dividido em `LED_C` + `I/O Cover` + `Chipset Accent`.

Essa mudança invalida o `sizes.ors` e **zera os tamanhos das zonas ARGB**. Com as zonas em
tamanho 0, o usuário perde o controle dos headers endereçáveis — na prática o RGB dos
periféricos ligados nos headers ARGB morre. O rollback pro rc2 restaurou os **40 LEDs** do
`ARGB_V2_2` automaticamente, via o `sizes.ors` antigo.

## Estado configurado

- Pacote: `openrgb` **1.0rc2-6.1**, em `IgnorePkg` no `/etc/pacman.conf`
  (junto de `nvidia-dkms` e `refind` — ver a memória `bootloader-refind`).
- Autostart: `openrgb --startminimized --profile Def`
- `ARGB_V2_2` = **40 LEDs**

## Se um dia for atualizar pro rc3+

Não é impossível, só exige reconfiguração manual — o pin existe pra evitar a surpresa, não porque
o rc3 seja quebrado:

1. Atualizar o pacote (tirar do `IgnorePkg`).
2. Redimensionar as zonas ARGB na GUI: **`ARGB_V2_2` = 40 LEDs**.
3. **Salvar o perfil `Def` de novo** — senão o autostart carrega o perfil velho e as zonas voltam a zerar.

Depois de qualquer mudança, confira que o perfil `Def` ainda carrega certo no boot, já que é o que
o autostart usa.

## Depois de um Syu: mbedtls 4 (2026-09-10)

O pin **não** impede o binário rc2 de quebrar quando a lib TLS muda de SONAME.
No update de 2026-09-10, `mbedtls` 3.6.5 → 4.2.0. O OpenRGB rc2 precisa de
`libmbedx509.so.7` / `libmbedtls.so.21` / `libmbedcrypto.so.16`. O daemon de autostart
sai com **127** (`error while loading shared libraries`). O IT5711 continua no USB
(`048d:5711`). Isso **não** é o bug do rc3.

Correção que preserva o pin: `sudo pacman -S mbedtls3` (Provides exatamente esses SONAMEs;
não conflita com mbedtls 4). **Não** `pacman -S openrgb`. Depois:
`openrgb --startminimized --profile Def`.

Wiki: `pcl-lianli-openrgb`.

## Restore no Omarchy: DRAM some (SMBus)

O perfil `Def.orp` espera duas barras **ENE DRAM** (Adata `AUDA0-E6K5-0101`) em
`I2C: /dev/i2c-11` (endereços `0x71` e `0x73`). A placa reserva `0x0b00`/`0x0b20`
em ACPI (`PNP0C02`); sem `acpi_enforce_resources=lax` o `i2c-piix4` carrega mas
**não cria adaptador**, o OpenRGB só vê o IT5711 (HID) e o G703, e avisa
“I2C or SMBus interfaces failed to initialize”.

No CachyOS o parâmetro já ia no cmdline. No Omarchy 4 (Limine/UKI) ele **não**
vem de fábrica. Drop-in que restaura o comportamento:

`/etc/limine-entry-tool.d/acpi-smbus.conf`

```
KERNEL_CMDLINE[default]+=" acpi_enforce_resources=lax"
```

Depois `limine-update` (não `omarchy-refresh-limine` — esse apaga o Windows) e
**reboot**. Confirmar `i2cdetect -l` com uma linha `SMBus PIIX4` e `/dev/i2c-11`.
O grupo `i2c` + udev `uaccess` cobrem permissão; o HID do IT5711 nunca precisou
disso.

Não atualizar para rc3 para “achar mais dispositivos”. rc3 só muda o layout de
zonas do IT5711.

Wiki: `pcl-lianli-openrgb`.

## Não confunda com as fans

O **IT5711** (RGB) e o **IT8696E**/**IT87952E** (fans) são chips ITE diferentes, com drivers e
softwares diferentes, na mesma placa. Nomes parecidos, problemas independentes: mexer no `it87`
não afeta o RGB, e o OpenRGB não tem nada a ver com o CPU_FAN não aparecer no CoolerControl.

O RGB das fans **Lian-Li** também não passa pelo OpenRGB desta placa — elas têm controlador próprio
e software de terceiro.
