# Reference: triagem AUR no restore Omarchy/PCL

**Snapshot**: verificação ao vivo em 2026-09-12, no Omarchy 4.0.3. Estes
números são um retrato da sessão; repetir a busca antes de instalar porque o
AUR e os repositórios são mutáveis.

## Mapeamento verificado

| Pedido original | Fonte/estado verificado | Tratamento |
|---|---|---|
| `it87-dkms-git` | AUR, `301.8dd7f65-1` | instalar com `yay`; requer `dkms` |
| `lianli-linux-git` | AUR, `0.8.5.r0.ga56f6bf-1` | instalar com `yay`; requer headers/DKMS para dependências de módulo |
| `coolercontrol` | AUR, `4.3.1-2`, marcado desactualizado | preferir `coolercontrol-bin`, `5.0.0-1` |
| `openlogi` | nome exacto não retornou pacote AUR | usar `openlogi-bin`, `v0.8.3-1`, que declara `provides: openlogi` |
| `linux-headers` | repositório oficial, `7.2.3.arch1-3` | corresponde ao pacote `linux` instalado e ao kernel em execução |
| `openrgb` | repositório `extra`, `1.0rc3-3` | não incluir no restore genérico: o PCL precisa da rc2 pinada |

## Comandos separados validados para o plano

```fish
# Repositório oficial; o kernel em execução é o linux padrão
sudo pacman -S --needed linux-headers dkms

# AUR; executar como utilizador normal, nunca com sudo yay
yay -S --needed it87-dkms-git coolercontrol-bin lianli-linux-git openlogi-bin
```

A chamada original misturava os seis nomes num único `pacman -S`. Os quatro
nomes não disponíveis no sync database (`it87-dkms-git`, `coolercontrol`,
`lianli-linux-git` e `openlogi`) fizeram a transacção ser rejeitada antes da
instalação dos alvos válidos. Confirmar com `pacman -Q` após executar os
comandos; não presumir que `openrgb` ou os headers foram instalados.

## Regra especial do OpenRGB

O repositório actual oferece rc3, mas a configuração do PCL documenta rc2 para
não apagar as zonas ARGB do IT5711. Restaurar o pacote exacto da rc2 a partir do
backup/cache da instalação anterior e manter o pin; seguir o runbook
[[pcl-lianli-openrgb]] para a biblioteca compatível (`mbedtls3`) e para a
verificação com `ldd`. Não substituir este pin por `sudo pacman -S openrgb`.

## Fontes consultadas

- `/etc/os-release`, `uname -r`, `pacman -Ss`, `pacman -Q` e `yay -Ss` locais.
- Metadados RPC do AUR para `it87-dkms-git`, `coolercontrol`,
  `coolercontrol-bin`, `lianli-linux-git`, `openlogi-bin` e
  `coolercontrold-bin`.
- [[omarchy-dual-boot-pcl]] e [[pcl-lianli-openrgb]].
