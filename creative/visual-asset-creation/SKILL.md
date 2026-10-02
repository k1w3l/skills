---
name: visual-asset-creation
description: Use when creating visual assets. Build and verify them.
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, avatar, illustration, svg, icon, artifact, verification]
---

# Visual Asset Creation

Create small, portable visual assets—especially avatars, icons, badges, and simple illustrations—with an actual file as the deliverable, not a prose description.

## Workflow

1. **Interpret the brief**
   - Identify subject, mood, intended use, format, dimensions, and any text.
   - Use an obvious default when the brief is small: generate one polished concept rather than blocking on unnecessary questions.
   - When the brief asks for multiple options, make each variant materially distinct in silhouette, focal expression, and palette; do not produce three near-duplicates.
   - Translate requested personality traits into one immediately legible visual cue per variant (for example, a severe brow, warning color, or watchful eye) rather than relying on a long explanation.
   - Keep the composition legible at avatar/icon scale; avoid details that disappear when reduced.
   - For assistant avatars, default to an adult, restrained, professional visual language: deliberate geometry or editorial illustration, a limited palette, and one strong focal mark; avoid childish cartoon proportions, clip-art styling, decorative clutter, and explanatory slogans unless explicitly requested.

2. **Choose a portable format**
   - Prefer a self-contained SVG for geometric artwork, icons, and avatars: it scales cleanly, embeds its own colors and typography, and avoids dependency failures.
   - Use a raster format only when texture, painting, or platform compatibility specifically requires it.
   - Give the file a descriptive, stable name and write it to the requested working directory.

3. **Build the asset**
   - Define a constrained palette, explicit gradients, strokes, typography, and accessible `title`/`desc` metadata where the format supports them.
   - Use a clear silhouette, strong contrast, and one focal expression or symbol; make the personality legible through posture, gaze, silhouette, and palette before adding text.
   - Keep text short and verify that it remains readable at the intended size.
   - Keep labels and important facial or symbolic details inside a conservative safe margin; circular borders and thumbnail cropping make edge-hugging text look clipped even when the SVG bounds are valid.
   - Do not invent external dependencies or remote image URLs unless explicitly requested.

4. **Verify the artifact**
   - Confirm the source exists and has non-zero size.
   - Open it in an available browser or renderer and inspect the actual rendered result, not only the source markup.
   - Check for clipping, missing elements, illegible text, broken references, unexpected whitespace, and labels colliding with borders.
   - For avatars, rasterize every delivered variant at the intended thumbnail dimensions and inspect the rendered pixels, not only the source markup; a valid SVG can still have poor safe-area composition.
   - If the first renderer cannot inspect the format directly, use a browser to render it or convert it with an installed rasterizer; do not claim visual verification from source inspection alone.

5. **Stage or copy it when requested**
   - Check that the destination exists and is the intended mount/path before writing.
   - Copy with an explicit target filename rather than relying on implicit directory behavior.
   - Verify the resulting target by reading its metadata and comparing a cryptographic hash with the source, for example:
     `sha256sum /path/source.svg /destination/source.svg`
   - Report the exact destination path and verification result.

## Quality Rules

- Prefer original visual language over cloning a branded or copyrighted character/interface.
- Keep the deliverable self-contained and directly usable.
- Preserve the exact requested filename, path, and literal text; do not silently normalize identifiers or wording.
- Use concise final reporting: path, what was created, and what was actually verified.
- If rendering or copying fails, report the concrete blocker and do not substitute an unverified success claim.

## Pitfalls

- Render the asset before calling it complete—the SVG can be syntactically valid while clipped, unreadable, or visually unbalanced.
- Reject a technically valid avatar if the rendered pixels feel childish, generic, or like clip art—visual QA must judge tone and finish as well as geometry because the user evaluates the image, not the markup.
- Check destination mounts before copying—the path may exist as a directory while the intended storage is unavailable or different.
- Compare source and target hashes after copying—successful `cp` only proves the command exited, not that the stored artifact is identical.
- Keep avatar details bold and sparse—fine facial or decorative geometry is lost at thumbnail size.
- Use browser rendering as a fallback for SVG inspection when a vision tool cannot consume SVG directly—the browser exercises the format's real rendering path.
