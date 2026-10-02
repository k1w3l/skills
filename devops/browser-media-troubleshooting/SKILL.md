---
name: browser-media-troubleshooting
description: Use when browser media, tabs, or repaint stall on Linux. Triage the failing layer.
---

# Browser media troubleshooting

Diagnose short pauses, dropped frames, buffer stalls, and brief audio/video interruptions in Chromium-family browsers on Linux. Use evidence and controlled A/B tests; do not apply random GPU flags or declare a fix from a single clean restart.

## When to use

Use for Chrome/Chromium/Brave/Edge playback that pauses for roughly a second and resumes, especially on Wayland, AMD graphics, PipeWire, or Bluetooth audio. It covers streaming and local browser playback, but not a complete diagnosis of a broken display driver or an ISP outage.

## Operating principles

- Separate **what stopped**: video only, audio only, both, one tab, or every application.
- Separate **where it stopped**: network/buffer, media decoder, GPU/render path, browser renderer, compositor, or audio transport.
- Establish a baseline before changing settings and keep a short before/after record.
- Prefer a reversible A/B test over a speculative configuration change.
- Do not add legacy Chrome GPU flags merely because the symptom sounds graphical. On modern native Wayland Chrome, flags such as `--use-gl=egl`, `--enable-zero-copy`, and `--ignore-gpu-blocklist` can create new failure modes; inspect the live configuration first.
- Never delete a browser profile, cache, or system state as a first-line fix. Ask before deletion when it is actually required.
- For this user, announce any investigation that would open, automate, or navigate a browser and obtain explicit permission first. Prefer terminal, package metadata, logs, and compositor state before touching the user's browser; a direct HTTP/API lookup that does not open the user's browser is a separate path, but say so clearly.

## Evidence-first workflow

### 1. Characterize the interruption

Record the site, stream type, resolution, whether the audio pauses with the image, frequency, fullscreen state, monitor/output, and whether the pause happens in another tab or a local video. Test the same stream with:

1. the current audio output;
2. a wired/USB/HDMI output when available;
3. an incognito/private window with extensions absent or minimized;
4. a second browser only if the first three tests do not isolate the layer.

The most valuable first split is **audio pauses too** versus **only video pauses**.

### 2. Inspect the browser without changing it

- Read the browser's actual version and process command line. Check user-level flag files and `chrome://version` rather than assuming defaults.
- Inspect `chrome://gpu`: GPU process status, compositing, WebGL, video decode, and any reset/crash messages.
- Inspect `chrome://media-internals` or DevTools' Media panel during a reproduction: pipeline state, decoder, buffer/underflow events, timestamps, and errors.
- On YouTube-like sites, use Stats for Nerds to record codec, dropped frames, and buffer health.
- Check `chrome://flags` only for non-default experiments that could affect media; do not change several flags at once.
- For current Chrome on native Wayland, expect the browser to use the native Wayland path and hardware decode when the driver exposes it. Validate this; do not force a legacy GL path preemptively.

### 3. Check the system paths in parallel

**GPU and decode**

- Confirm the render node and hardware decode capabilities with the distribution's VA-API tool (on Arch, commonly `vainfo`).
- Inspect the kernel journal for `amdgpu`, GPU reset, ring timeout, page fault, or display-engine errors around the reproduction.
- Check GPU process crashes or hangs, not merely high utilization. High utilization alone is not a root cause.

**Audio**

- Use `pw-top` while reproducing. A changing non-zero `ERR` counter is evidence of xruns or stream errors; note the stream and node.
- Inspect the user journal for `xrun`, `underrun`, `overrun`, `RTKit`, `bluez`, `Bluetooth audio transport`, PipeWire, and WirePlumber errors.
- Check the active sink and its transport. A Bluetooth sink entering an error state while the browser stream is active strongly prioritizes the audio path.
- Check real-time scheduling support. On Arch, verify whether the official `rtkit` package is present and whether `rtkit-daemon.service` is active; RTKit is normally used on demand, so enabled-at-boot status is not itself a failure.

**Network and resources**

- Check the wired/Wi-Fi link, local gateway latency and loss, DNS only when name resolution is implicated, and the stream's buffer health.
- Check memory pressure and the kernel journal for OOM events. Also check CPU pressure if software decode or a saturated compositor is plausible.

### 4. Use the symptom matrix

| Observation | First suspect | Confirm with |
|---|---|---|
| Audio and image pause together | audio clock/transport, PipeWire, Bluetooth | wired output A/B; `pw-top`; user journal |
| Image pauses and buffer health falls | network or adaptive stream delivery | Stats for Nerds; gateway/stream test |
| Image pauses, buffer is healthy, dropped frames rise | decoder, GPU upload, compositor | media-internals; `chrome://gpu`; `vainfo`; kernel journal |
| Only one tab pauses | page, renderer, extension, or site-specific codec | incognito; second site; media panel |
| Every app stutters | system scheduling, GPU, compositor, or resource pressure | other media player; kernel/resource checks |
| Bluetooth output alone correlates | Bluetooth profile/transport or real-time scheduling | wired/USB/HDMI A/B; BlueZ/PipeWire journal |

### 5. Apply the smallest evidence-backed repair

1. **Browser configuration:** remove only a confirmed stale or harmful experiment, then fully restart the browser. Preserve the original value for rollback.
2. **Real-time audio support:** if RTKit is absent and the package is available from the official repository, install it with the system package manager (for Arch, `sudo pacman -S --needed rtkit`), confirm the daemon can activate, and restart the user audio session (`pipewire`, `pipewire-pulse`, and `wireplumber`). If a component enters a restart loop, stop making changes and inspect its journal before retrying.
3. **Bluetooth isolation:** compare a non-Bluetooth sink, then inspect the Bluetooth profile, adapter, transport and signal/interference. Do not make a wired sink the permanent default unless that is the user's intent.
4. **Network/codec isolation:** temporarily lower resolution or use another codec only as a test. Do not present the test as a permanent fix without reproducing the original condition.
5. **Extensions/site:** use incognito or disable one extension at a time. Keep browser flags at default unless a specific experiment is supported by evidence.

Avoid blanket GPU disablement, arbitrary `--disable-features` lists, random PipeWire quantum changes, and profile deletion. Those can mask the layer that actually failed.

### 6. Verify the fix

Reproduce the original workload for long enough to cover the normal failure interval. Re-check the same counters and logs, then repeat the most discriminating A/B test. A successful package install or service restart is not proof; proof is the symptom disappearing while the relevant error counters remain clean. If the suspected device was not connected during the final test, label the result as **likely** rather than **confirmed**.

For flaky video-only stalls, a foreground `requestVideoFrameCallback` probe is a useful tight loop: record frame-callback gaps, `videoWidth`/`videoHeight`, and `getVideoPlaybackQuality()` before and after the change. Reload between A/B runs, keep the quality/codec fixed where possible, and do not open diagnostic pages in the same tab while measuring. A backgrounded or auto-quality-switched player can produce a false zero-callback or false-clean result.

Document durable findings in the appropriate system/wiki page, including the evidence, the exact change, the rollback, and what remains unverified. Do not record credentials, tokens, or private stream URLs.

## Wayland browser UI stalls: tabs, navigation, and repaint

Use this branch when a Chromium-family browser keeps its process alive but opening tabs, navigating, or repainting appears stuck, even when the symptom is not video playback.

1. Separate logical progress from presentation. A changed title or URL does not prove that the surface painted; a stale surface does not prove that navigation failed.
2. Record the live browser version, session/compositor, GPU/driver, and effective process arguments without reading private profile data. Check resources, OOM, coredumps, GPU resets/page faults/timeouts, and browser crash counters before changing anything.
3. Treat one variable per A/B run: browser update, native Wayland versus XWayland, GPU/compositing flag, or extensions/profile. Use a fresh temporary profile for profile/extension isolation; never reset or delete the main profile to make a test pass.
4. Before changing a user flag file, create a timestamped backup and edit only the requested lines. Fully restart the browser, then inspect the GPU and renderer child arguments; the root command line alone may not show the effective Ozone backend.
5. If a desktop control tool can inspect X11 but not native Wayland, use compositor state such as `hyprctl clients -j` to confirm the application class, mapped state, and workspace. A missing screenshot in an X11-only driver is not evidence that the Wayland application failed.
6. Exercise safe public pages and ordinary tab operations, then observe the process, mapped window, and journal for a bounded interval. Log severity is not an exit status: an `ERROR` line in a process that exits 0 is not automatically a crash.
7. Keep causal claims proportional. `Frame latency is negative` and VSync warnings are timing/compositor clues; if they also appear with `--disable-gpu`, they do not prove a GPU-only root cause. Report the clean interval and the remaining uncertainty instead of calling an intermittent freeze permanently fixed.

See [references/chrome-wayland-ui-stalls.md](references/chrome-wayland-ui-stalls.md) for a compact evidence recipe and rollback-safe flag procedure.

## Restoring a proven XWayland workaround

If a controlled A/B already showed that native Wayland video freezes while XWayland is stable, and the user explicitly requests the known workaround, treat that direct request as authorization for the configuration edit and browser restart; do not ask again about the same edit. Keep the separate browser-use permission gate: do not open tabs, navigate, or reproduce media for validation unless the user has also authorized browser use.

Use this rollback-safe sequence:

1. Read the active flag file and process arguments, then create a timestamped backup before editing.
2. Restore only the proven trio when that is the established workaround for the machine:

   ```text
   --ozone-platform=x11
   --force-device-scale-factor=1.5
   --disable-features=AcceleratedVideoDecodeLinuxZeroCopyGL
   ```

3. Fully stop the existing Chrome process and relaunch it through the desktop's normal launcher (on Omarchy, `omarchy launch browser`); a soft tab restart is not sufficient for command-line flags.
4. Verify the file, root browser command line, GPU-process command line, browser version, and a short clean process interval. Process-only verification is the correct stopping point when browser use is not authorized.
5. Report that the workaround is restored, not that video playback is fixed; leave the user to observe the original workload unless they grant permission for a browser test.

Do not add `--disable-gpu`, `--use-gl=egl`, or unrelated flags while restoring this workaround. Preserve the backup for rollback and document the exact active flags and what was deliberately not tested.

## Wayland video-only freezes: zero-copy presentation branch

When audio remains continuous but the image freezes, rank media presentation above audio transport. Inspect `chrome://media-internals` for the decoder and frame counters, then inspect `chrome://gpu` and the browser log for Viz/Wayland/ANGLE errors such as negative frame latency or EGLImage/native-pixmap import failures. A healthy VA-API capability check alone does not prove that decoded frames can be imported and presented.

If the evidence points to the Chromium zero-copy video-frame path, test the smallest reversible branch first:

```text
--disable-features=AcceleratedVideoDecodeLinuxZeroCopyGL
```

This is intended to bypass zero-copy EGLImage/DMA-BUF import while retaining normal GPU compositing and VA-API decode. Verify after a full browser restart that the flag reached the GPU process, the render node is still in use, and `chrome://media-internals` still reports a platform decoder. It remains a candidate workaround until the original video-only stall disappears over the normal failure interval.

Do not blindly substitute legacy `--use-gl=egl` or `--use-gl=desktop`; verify the resulting GPU backend first because either can disable or destabilize acceleration on a modern native-Wayland installation. If the zero-copy branch does not change the symptom, revert it before testing XWayland (`--ozone-platform=x11`) or another compositor variable.

See [references/chrome-wayland-zero-copy.md](references/chrome-wayland-zero-copy.md) for the evidence pattern, A/B recipe, and source notes.

## Arch/Omarchy AMD stack updates

Treat the graphics stack as coordinated layers, not one monolithic "driver": kernel `amdgpu`, Mesa/radeonsi/RADV, VA-API components, `linux-firmware`/`linux-firmware-amdgpu`, `amd-ucode`, and the running kernel/headers. A newer upstream package is evidence of availability, not evidence that it fixes the browser stall.

1. Collect installed versions and the configured repository candidates read-only. Record `pacman-conf --repo-list`, the mirror/repository URLs, `pacman -Q` for the graphics stack, `pacman -Si` candidates, and `pacman -Qu`.
2. If the configured database is stale, use a complete upgrade path (`pacman -Syu`) only after explicit authorization. Preview the transaction and inspect whether the target Mesa/firmware/kernel packages are actually present before confirming.
3. On Omarchy, distinguish the stable mirror from the public Arch package pages. The stable mirror may intentionally lag the Arch web index; `pacman -Syu` can therefore offer only Omarchy packages while public Arch pages show newer Mesa, firmware, or kernel builds.
4. If the target driver packages are absent and the transaction contains only unrelated Omarchy updates, cancel before confirmation. Do not switch to public Arch mirrors or install a partial Mesa/kernel/firmware set on an Omarchy system merely to chase a browser symptom.
5. Consult the matching Mesa release notes, but state explicitly when they contain only general RADV/radeonsi/video fixes and do not mention the user's GPU, browser, or Wayland path. Do not promise that an update will solve the stall.
6. After an authorized installation, read back exact package versions and kernel/firmware state. If the kernel or firmware changed, obtain separate authorization before rebooting if needed. Validate browser playback only after the browser-use permission gate above has been satisfied.

For the reusable command/evidence pattern and the Omarchy stable-mirror pitfall, see [references/omarchy-amd-stack-updates.md](references/omarchy-amd-stack-updates.md).

## Reference

For the AMD/Wayland/Chrome/PipeWire-Bluetooth evidence pattern and reusable commands, see [references/chrome-amd-wayland-pipewire.md](references/chrome-amd-wayland-pipewire.md).