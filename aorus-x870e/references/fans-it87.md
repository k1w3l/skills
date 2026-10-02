# Fans e temperaturas — driver it87

## Resumo

O controle de fans desta placa **depende do pacote `it87-dkms-git`** (chaotic-aur, fork do
frankcrawford). Sem ele o CPU_FAN não existe pro sistema. Instalado em 2026-07-15.

Se as fans do CPU sumirem, a primeira hipótese é sempre: **o DKMS caiu**.

## Por que o driver mainline não serve

A placa tem dois chips Super I/O, ambos acessados por **MMIO** (memória mapeada), não por porta ISA:

```
it87: Found IT8696E chip at 0xa40 [MMIO at 0x00000000fe100000], revision 0
it87: Found IT87952E chip at 0xa60 [MMIO at 0x00000000fe110000], revision 1
```

O driver `it87` **mainline** falha por dois motivos somados: não conhece o `IT8696E`, e não faz
acesso MMIO. Resultado: ele enumera só o `IT87952E` secundário — cujos três headers estão vazios,
todos em 0 RPM — e o CPU_FAN simplesmente não aparece em lugar nenhum. O fork do frankcrawford
faz MMIO e conhece o chip.

> **Não confunda:** a doc do kernel lista o `IT8689E` como suportado. Esta placa tem o **IT8696E**.
> Chips diferentes. Essa confusão já levou à conclusão errada de que o mainline bastaria.

## Mapa dos headers

Chip `it8696` (o que importa), confirmado por RPM real com as fans girando:

| sysfs | Header físico | Observado |
|---|---|---|
| `fan1` / `pwm1` | **CPU_FAN** | 884 RPM @ 30% |
| `fan4` / `pwm4` | ocupado | 1061 RPM |
| `fan5` / `pwm5` | **CPU_OPT** — bomba do water cooler | 2647 RPM @ 80% |

Também expõe `temp1`–`temp6`. O chip `it87952` tem `fan1-3`/`pwm1-3`/`temp1-3`, todos headers
vazios — ver 0 RPM neles é normal, não é defeito.

**A bomba (CPU_OPT/`pwm5`) quer velocidade fixa e alta, não curva de temperatura.** Curvas vão
no CPU_FAN (`pwm1`). Tratar bomba de water cooler como ventoinha é erro comum e prejudica a
refrigeração.

## Instalação / correção

```
sudo pacman -S --needed linux-headers it87-dkms-git && sudo systemctl stop coolercontrold && sudo modprobe -r it87 && sudo modprobe it87 && sensors
```

Detalhes que evitam passos desnecessários:

- No **Omarchy** o pacote é AUR (`it87-dkms-git`). Sem `linux-headers` o hook DKMS corre
  vazio, o kernel carrega o **mainline** e só aparece o `IT87952E`. Conferir
  `modinfo it87 | grep filename` → tem de ser `updates/dkms/`, não
  `kernel/drivers/hwmon/`.
- Instala em `/lib/modules/<kernel>/updates/dkms/it87.ko.zst`, que tem **precedência sobre o
  in-tree**. **Não precisa blacklist do `it87` nem reboot** — basta descarregar e recarregar.
- Descarregar o módulo é seguro: os PWMs mantêm o último valor, as fans continuam girando.
- Depois: `sudo systemctl start coolercontrold` — ele re-detecta sozinho.
- Versão no Omarchy (2026-09-12): `it87/354.a904dd8`. CoolerControl `coolercontrol-bin` **5.0.0**.
- Labels: `/etc/sensors.d/gigabyte-it8696.conf` (`CPU_FAN`/`SYS_FAN`/`CPU_OPT`). Perfis do
  daemon em `/etc/coolercontrol` — **não** no yadm. `sudo coolercontrold backup`.
  Wiki: `pcl-coolercontrol-it87`.

## Conflito de ACPI — já resolvido, não persiga

`acpi_enforce_resources=lax` **já estava no cmdline** do CachyOS. No Omarchy 4
o parâmetro **não** veio no Limine — drop-in
`/etc/limine-entry-tool.d/acpi-smbus.conf` + `limine-update` (wiki
`pcl-lianli-openrgb`). Sem isso o `i2c-piix4` não cria o SMBus e o OpenRGB
perde a DRAM RGB; as fans `it87` não dependem deste parâmetro.

A alternativa equivalente seria a opção de módulo `ignore_resource_conflict=1`.

Antes de mexer em cmdline: no Omarchy o bootloader é **Limine**
(`/etc/limine-entry-tool.d/` + `limine-update`). Não é GRUB. Não usar
`omarchy-refresh-limine` (apaga a entrada do Windows).

**Red herring:** o log mostra conflitos de ACPI em `0xB00`/`0xB20` (`\GSA1.SMBI`, `\GSA1.SMG0`).
Isso é do **`piix4_smbus`**, não tem nada a ver com fans. Ignore.

## Atualização de kernel

Headers dos dois kernels instalados (`linux-cachyos-headers`, `linux-cachyos-lts-headers`), então
o DKMS recompila sozinho. Estado esperado:

```
it87/332.20f2f2f, 7.1.3-1-cachyos, x86_64: installed (Original modules exist)
it87/332.20f2f2f, 6.18.38-1-cachyos-lts, x86_64: installed (Original modules exist)
```

Se as fans sumirem depois de um update, o primeiro comando é `dkms status | grep it87`, e conferir
se o módulo em uso é o certo: `modinfo it87 | grep filename` deve apontar pra `updates/dkms/`, não
pra `kernel/drivers/hwmon/`.

## Técnicas de diagnóstico que valeram

**A assinatura de "header não enumerado": fan girando fisicamente + 0 RPM no sysfs.** Foi o que
quebrou o caso. Se o usuário confirma que a ventoinha gira e o `fanN_input` marca 0, aquele canal
não é o header dela — não é problema de leitura de tacômetro. Sempre pergunte onde as fans estão
plugadas fisicamente e se estão girando; isso separa "não enumerado" de "sem leitura".

**O mainline descarta chip desconhecido em silêncio** (via `pr_debug`, invisível por padrão). Para
ver o que ele está rejeitando:

```
sudo modprobe -r it87; sudo modprobe it87 dyndbg=+p; sudo dmesg | grep -i it87
```

**Cuidado com grep poluído no journal:** filtrar por `resource` traz centenas de linhas de
`ACPI: ... New power resource` e enterra o que importa. Filtre por `it87` direto.

**`/proc/ioports` mascara endereços como `0000-0000` sem root** — não conclua que não há nada ali.

## Limitação conhecida

Pela issue #70 do `frankcrawford/it87`, nesta família de placa os **SYS_FAN4-6 podem não aparecer**
mesmo com o DKMS. Não é regressão nem erro de configuração. O que importa (CPU_FAN, CPU_OPT) funciona.

Links: [frankcrawford/it87](https://github.com/frankcrawford/it87) ·
[issue #70](https://github.com/frankcrawford/it87/issues/70) ·
[doc do kernel](https://docs.kernel.org/hwmon/it87.html)
