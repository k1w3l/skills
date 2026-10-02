# Omarchy AMD stack update triage

Use this reference when a Chromium-family browser stalls during video playback on an AMD GPU under Omarchy/Wayland and the question is whether a driver update is available.

## Layer model

Do not call the whole stack "the driver". Record each layer separately:

- kernel: `amdgpu`, running kernel, and matching headers;
- userspace graphics: Mesa, radeonsi, RADV, `vulkan-radeon`, and `libdrm`;
- media: VA-API driver and browser platform decoder;
- firmware: `linux-firmware`, `linux-firmware-amdgpu`, `linux-firmware-whence`, and `amd-ucode`;
- compositor/browser: Wayland compositor, Ozone backend, ANGLE/Viz, and browser version.

A release-note match is useful evidence, but an upstream version number alone does not establish causality for a Chrome freeze.

## Read-only collection

```bash
uname -r
pacman-conf --repo-list
pacman -Q mesa vulkan-radeon linux-firmware-amdgpu linux-firmware-whence linux-firmware amd-ucode linux linux-headers
pacman -Si mesa vulkan-radeon linux-firmware-amdgpu amd-ucode linux linux-headers
pacman -Qu
journalctl -k -b --no-pager -g 'amdgpu|drm|ring timeout|page fault|gpu reset'
```

Also record the GPU model and kernel binding with `lspci -k`, and use `vainfo`/Vulkan probes only as read-only capability checks. Do not read browser cookies, passwords, tokens, or private page content.

## Arch versus Omarchy repositories

Compare both sources explicitly:

- configured candidates from `pacman -Si` and `pacman -Qu`;
- public Arch package pages and the matching Mesa release notes.

Omarchy commonly uses a stable mirror such as:

```text
https://stable-mirror.omarchy.org/$repo/os/$arch
```

That mirror can lag the public Arch package index. Seeing a newer Mesa, firmware, or kernel on `archlinux.org` does not mean the package is safely installable from the configured Omarchy repositories.

## Safe transaction rule

On Arch, do not solve stale metadata with standalone `pacman -Sy` or by mixing mirrors. After explicit authorization, use a complete upgrade path:

```bash
sudo pacman -Syu
```

Inspect the transaction before confirmation. If the target graphics packages are absent and only unrelated Omarchy packages are listed, answer `n` and report that the update is blocked by mirror publication. Do not install a partial Mesa/kernel/firmware set or rewrite the mirror list to chase a browser regression.

If a kernel or firmware update later enters an authorized transaction, read back the installed versions and obtain separate authorization before rebooting when a reboot is needed. A package transaction succeeding is not proof that video playback is fixed.

## Browser permission gate

Before opening, automating, or navigating the user's browser, announce the action and obtain explicit permission. First use terminal-only evidence. If browser validation is authorized, preserve the main profile, use public/non-sensitive pages where possible, and validate the original failure interval rather than a single successful restart.

## Session-derived evidence pattern

On 2026-09-18, the PCL reported an AMD Radeon RX 9070 XT/Navi 48 with `amdgpu`, Mesa/RADV `1:26.2.2-1`, AMD firmware and `amd-ucode` `20260810-2`, and kernel `7.2.3.arch1-3`. Public Arch pages showed Mesa/RADV `1:26.2.3-1`, firmware/`amd-ucode` `20260916-1`, and kernel `7.2.6.arch2-1`; Mesa 26.2.3 notes had general RADV/radeonsi/video fixes but no explicit RX 9070 XT/Chrome fix.

The configured Omarchy stable mirror had Arch sync databases dated 2026-09-08. An authorized `pacman -Syu` preview offered only seven Omarchy packages and no Mesa, firmware, or kernel update. The transaction was canceled with `n` before confirmation, so no package changed. This is the expected evidence for "upstream update exists, but it is not yet safely available through the current Omarchy mirror."