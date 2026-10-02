# Case reference: AMD Wayland + Chrome + PipeWire/Bluetooth

This is a reusable case note, not a machine-independent assumption. It records the evidence pattern and the split that should be repeated on similar Linux desktop incidents.

## Observed case

- Host: Arch-based Omarchy desktop, native Wayland/Hyprland.
- GPU: AMD Radeon RX 9070 XT; Chrome 153; Mesa 26.2.2; VA-API exposed H.264, HEVC, VP9, and AV1 decode profiles.
- Chrome used the native Wayland GPU path. No user Chrome flag file was present, and no relevant non-default experiments or legacy EGL/zero-copy flags were found.
- The active Chrome stream used the Bluetooth ARCANO sink. The user-visible symptom was a roughly one-second pause followed by recovery.
- The user journal showed WirePlumber/BlueZ transport errors for the Bluetooth output, including a Bluetooth audio transport failure and a sink transition to an error state.
- The audio stack also reported RTKit `ServiceUnknown` before the official `rtkit` package was installed.
- After installing `rtkit` and restarting the audio user services, a clean boot showed PipeWire, PipeWire Pulse, WirePlumber, and RTKit active; WirePlumber had zero restarts and no new xrun, RTKit, BlueZ, PipeWire, or WirePlumber errors in the checked interval.

The repair was **not fully confirmed** for the original symptom because the final clean check had the ARCANO disconnected and another sink active. The correct conclusion is “Bluetooth/PipeWire is the leading hypothesis; retest with ARCANO connected,” not “the issue is proven fixed.”

## Reusable collection commands

Use commands appropriate to the current host and do not assume the render-node number or sink name:

```bash
# Browser/GPU evidence
pgrep -af 'chrome|chromium'
vainfo --display drm --device /dev/dri/renderD128
journalctl -k -b --no-pager -g 'amdgpu|gpu reset|ring timeout|page fault'

# Audio evidence
pw-top
wpctl status
journalctl --user -b --no-pager -g 'xrun|underrun|overrun|RTKit|bluez|Bluetooth audio transport|pipewire|wireplumber'
systemctl is-active rtkit-daemon.service
systemctl --user show wireplumber.service -p ActiveState -p SubState -p MainPID -p NRestarts -p Result

# Resource/network controls
free -h
journalctl -k -b --no-pager -g 'oom|out of memory'
ping -c 20 <local-gateway>
```

Replace `/dev/dri/renderD128` and `<local-gateway>` only after discovering the live values. A non-zero or increasing `ERR` value in `pw-top`, a Bluetooth sink/transport error, and simultaneous audio/video interruption form a stronger causal chain than any one observation alone.

## Documentation notes

- ArchWiki Chromium guidance for current native Wayland builds treats VA-API as a validated capability, not a reason to force old EGL flags; AMD-specific flag experiments should be evidence-led.
- PipeWire real-time scheduling documentation describes RTKit as a fallback/helper for real-time thread permissions. `pw-top` documents `ERR` as an error/xrun-oriented counter useful during reproduction.
- Chrome’s media-internals and DevTools Media panel provide browser-side pipeline and decoder evidence; Stats for Nerds provides codec, dropped-frame, and buffer-health evidence for compatible streaming sites.

These notes complement, rather than replace, the current Arch/Omarchy, hardware, package-management, and wiki skills.