# Restoring a hardware-pinned OpenRGB rc2 on Omarchy

## When this applies

Use this procedure when a machine's RGB controller requires OpenRGB 1.0rc2, while the
current Arch/Omarchy repository offers a newer release that changes the controller's
zone layout. For the PCL, the affected controller is the Gigabyte X870E AORUS PRO ICE
IT5711; its saved profile expects `ARGB_V2_2` with 40 LEDs.

Do not silently replace the pinned version with `openrgb-git` or the repository's latest
`openrgb`. A `-git` package follows development and is not equivalent to the known-good
rc2 layout.

## Preferred installation path

Use the official Arch packaging tag `1.0rc2-6`, but rebuild it locally against the
compatibility library used by the current system. The historical PKGBUILD names the old
`mbedtls` package; current systems that retain the rc2 ABI use `mbedtls3`, which provides
`libmbedtls.so.21`.

```fish
sudo pacman -S --needed base-devel qt5-tools qt5-base libusb hidapi mbedtls3
mkdir -p ~/build
git clone --depth 1 --branch 1.0rc2-6 \
  https://gitlab.archlinux.org/archlinux/packaging/packages/openrgb.git \
  ~/build/openrgb-rc2
cd ~/build/openrgb-rc2
sed -i "s/'mbedtls'/'mbedtls3'/" PKGBUILD
makepkg -si
```

Run `makepkg` as the regular user, never as root. Review the PKGBUILD and the package
transaction before accepting them. The resulting local package is expected to be
`openrgb 1.0rc2-6`; the release suffix is less important than the rc2 code and the
resolved ABI.

The Arch Archive copy can be useful for inspection or recovery, but its historic package
metadata declares `mbedtls`. Do not make `pacman -U --nodeps` the default workaround.
If the exact CachyOS package `openrgb-1.0rc2-6.1` is available in a trusted backup, verify
its detached signature and checksum before installing it with `sudo pacman -U`.

## Pin and verify

Immediately after installing the working version, add this under `[options]` in
`/etc/pacman.conf`:

```ini
IgnorePkg = openrgb
```

Read back the package and dynamic dependencies before enabling autostart:

```fish
pacman -Q openrgb
ldd /usr/bin/openrgb
```

`ldd` must resolve `libmbedtls.so.21` and contain no `not found`. Once the restored profile
is present, the PCL autostart command is:

```fish
openrgb --startminimized --profile Def
```

If a future upgrade is intentionally tested, remove the pin only for that operation,
set `ARGB_V2_2` back to 40 LEDs in the GUI, save the `Def` profile again, and verify the
headers before leaving the newer version installed. Otherwise, never use
`sudo pacman -S openrgb` for this pinned setup: it selects the current repository release.

## Sources

- Arch packaging repository, tag `1.0rc2-6`:
  `https://gitlab.archlinux.org/archlinux/packaging/packages/openrgb/-/tree/1.0rc2-6`
- Arch package archive:
  `https://archive.archlinux.org/packages/o/openrgb/openrgb-1.0rc2-6-x86_64.pkg.tar.zst`
- Hardware-specific rationale: `references/openrgb-rgb.md` in this skill.
