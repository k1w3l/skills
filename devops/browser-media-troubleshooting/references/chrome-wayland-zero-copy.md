# Chromium video-only stalls on native Wayland

Reusable notes for Chromium-family browsers on Linux when **audio continues but the image freezes**.

## Diagnostic signal

Treat this symptom as a video-frame pipeline problem until evidence says otherwise. The useful split is:

- `chrome://media-internals`: `pipeline_state`, `kVideoDecoderName`, `kIsPlatformVideoDecoder`, resolution, `kVideoFramesDecoded`, `kVideoFramesDropped`, buffer/underflow events, and decoder errors.
- `chrome://gpu`: GPU process, compositor, video decode, GL backend, and problems detected.
- Browser stderr/journal: Viz/Wayland/ANGLE messages such as `Frame latency is negative`, `eglCreateImage failed`, `Unable to initialize binding from pixmap`, or `OzoneImageBacking` failures.
- YouTube/HTML5 statistics: codec, current resolution, buffer health, dropped frames.

A clean `vainfo` result proves that VA-API can initialize; it does **not** prove that Chromium can import decoded DMA-BUF frames into its GL presentation path.

## Tight A/B recipe

1. Record the exact site, codec, resolution, fullscreen state, monitor, and whether audio continues.
2. Capture the media-internals player during a reproduction.
3. Use a foreground `requestVideoFrameCallback` probe that records callback gaps and `getVideoPlaybackQuality()`. Reload between variants and keep quality fixed. Do not open `chrome://gpu` or `chrome://media-internals` in the measured tab; backgrounding or auto-quality changes can create false results.
4. Compare one variable at a time:
   - default native Wayland;
   - software video decode with `--disable-accelerated-video-decode`;
   - zero-copy import bypass below;
   - only then XWayland with `--ozone-platform=x11`.
5. Run each variant through the normal failure interval. A 45-second clean run is a useful smoke test, not proof for a multi-minute intermittent stall.

## Zero-copy presentation workaround

When logs and media data point at the Chromium EGLImage/DMA-BUF video-frame path, test:

```text
--disable-features=AcceleratedVideoDecodeLinuxZeroCopyGL
```

On Chromium versions that support this feature, it bypasses the zero-copy import while keeping ordinary GPU compositing and platform video decode. After a full restart, verify all three conditions:

1. the flag appears in the actual GPU-process command line;
2. the expected DRM render node is still used;
3. `chrome://media-internals` still reports `VaapiVideoDecoder` (or another platform decoder) and the VCN/decoder activity remains non-zero during playback.

This is a candidate workaround, not a universal guarantee. Roll it back if it does not change the original symptom before testing another backend.

## Backend pitfalls

Do not add a collection of historical Chromium flags. In particular, test `--use-gl=egl` and `--use-gl=desktop` only with explicit verification of `chrome://gpu` and the GPU-process command line; on modern native Wayland builds either can result in disabled or unstable GPU acceleration. `--use-angle=gl` is a separate backend experiment and must be measured independently.

For Arch's Google Chrome package, `/usr/bin/google-chrome-stable` reads `~/.config/chrome-flags.conf` and passes its non-comment lines to the internal binary. Starting `/opt/google/chrome/google-chrome` directly bypasses that wrapper, so a config-file A/B must use the wrapper or inspect the child command line.

## Evidence pattern from a real investigation

A 4K30 YouTube stream selected AV1 and `VaapiVideoDecoder`; Opus audio continued while the visual symptom persisted. The AMD render node and VA-API profiles were healthy, and no amdgpu reset/ring-timeout was found. An isolated local AV1 4K file was stable with both VA-API and `Dav1dVideoDecoder`, so the conclusion was not “AV1 or VA-API is universally broken.” A Chrome `Frame latency is negative` message, together with the native Wayland/ANGLE path, justified testing the zero-copy import workaround, while the final user-facing result still required playback validation over the normal failure interval.

## Source notes

- Omarchy discussion [#4055](https://github.com/basecamp/omarchy/discussions/4055): reports Chromium video presentation problems after Mesa/Wayland changes and includes `AcceleratedVideoDecodeLinuxZeroCopyGL` as a workaround for some Chrome 152/Mesa 26.2/Hyprland configurations.
- Omarchy discussion [#6275](https://github.com/basecamp/omarchy/discussions/6275): documents ANGLE → EGLImage → DMA-BUF presentation failures and the trade-off of `--use-gl=desktop`.
- Chromium issue [40165010](https://issues.chromium.org/issues/40165010): documents a related case where audio continues while a video frame freezes and later catches up.

Do not save credentials, cookies, signed media URLs, or complete private browser histories in this reference.
