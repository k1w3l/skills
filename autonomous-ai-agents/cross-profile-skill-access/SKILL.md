---
name: cross-profile-skill-access
description: "Use when accessing skills from another Hermes profile."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [hermes, profiles, skills, discovery, provenance, safety]
    category: autonomous-ai-agents
---

# Cross-profile skill access

Use this skill when a task depends on a skill belonging to a different Hermes profile, a default profile, or a slash-skill directory that is not exposed by the active profile's skill registry.

## Procedure

1. **Identify the active profile without changing it.** Resolve the active Hermes home from the runtime's `$HERMES_HOME` (or the session-provided profile path). Treat its `skills/` tree and `profile.yaml` as the current profile. Do not infer the target profile from a hostname, URL, or display name alone.
2. **Resolve the target profile in layers.** Check the configured Hermes profile root for `profiles/<target>/profile.yaml`; if that directory is absent, inspect the Hermes home itself for `profile.yaml` whose `display_name` matches the target, because the default profile may live at the home root rather than under `profiles/`. Only inspect an alternate root when the runtime or user identifies it.
3. **Discover the skill by path, not by the active registry.** `skills_list` and `skill_view(name=...)` are scoped to the active profile and can omit another profile's skills. Enumerate the target's `skills/**/SKILL.md` files, then select the exact name or slash-command path. Use direct file reading for a skill outside the active registry and record that it was read directly.
4. **Follow compatibility aliases.** If the selected skill redirects to another skill, read the canonical target as well and follow the canonical policy. Report both the alias path and the canonical path so the source of each instruction is clear.
5. **Distinguish skill stores.** A file under a target Hermes `skills/` tree is profile-owned Hermes content. A file under `$HOME/.claude/skills/` is a Claude slash skill, not automatically registered in Hermes; it may still be read when the user asks for it, but label it as an external slash skill and do not claim that Hermes activated it through its registry.
6. **Verify before reporting access.** Confirm the file exists and read its contents. Report the exact path, target profile, and whether the skill was registry-loaded or directly read. Do not claim a skill is available based only on a directory name or an alias.
7. **Keep the operation read-only by default.** Accessing another profile means inspecting and applying its instructions, not copying, merging, switching, or editing profiles. Edit only when the user explicitly requests it and the target skill is curator-managed and not bundled, pinned, externally owned, or user-owned.
8. **If editing is authorized, preserve ownership boundaries.** Freshly read the exact `SKILL.md` or support file before patching it, use the skill-management workflow, and prefer a targeted correction over a duplicate addendum. Never modify protected skills or silently import a foreign skill into the active profile.

## Authorized import and exposure

When the user explicitly asks to make another profile's skill library available, hand off the filesystem mechanics to the `external-skill-imports` workflow and apply these gates:

1. Resolve the source profile and active destination from metadata and `$HERMES_HOME`; never infer either from a display name alone.
2. Prefer a namespaced directory of per-entry symlinks (for example, `skills/jarvis-skills/`) over copying or symlinking the entire source root. Link active top-level skill/category directories only; skip hidden archives, hub metadata, and caches.
3. Audit source text for literal credential fingerprints before exposing it. Do not print matches; skip or quarantine real secrets and treat documentation placeholders as non-secrets.
4. Compare frontmatter names and hashes before linking. Keep existing destinations untouched; preserve divergent versions under the source namespace instead of changing bare-name precedence.
5. Verify with Hermes' loader (`hermes -p <profile> skills list`, `skills_list(category=...)`, and a representative `skill_view`), not only a filesystem glob; many directory walkers do not follow symlinked directories.
6. Report linked, already-present, skipped, and loader-visible counts separately. Do not claim a link is loaded into a long-lived gateway conversation until a new session or an authorized restart has rebuilt its skill registry.

See `references/import-workflow.md` for the reusable import recipe and collision table.

## Example: resolving a missing `/wiki`

- Inspect the target profile metadata first.
- Search both the target Hermes skill tree and any explicitly identified slash-skill tree for `wiki/SKILL.md` and `wiki-jarvis/SKILL.md`.
- Read `/wiki/SKILL.md` when it exists; if `wiki-jarvis` only redirects, read the unified canonical wiki policy it names.
- Keep the active profile unchanged and cite the actual source paths in the result.

## Pitfalls

- **Do not conclude that a target profile is absent because `profiles/<name>` is missing** — the default profile may be represented by the Hermes home root and identified only by `profile.yaml`.
- **Do not conclude that a skill is unavailable because `skills_list` omits it** — registry listings are profile-scoped, so inspect the target tree directly.
- **Do not conflate Claude slash skills with Hermes-registered skills** — the same name can exist in both stores while having different activation and ownership rules.
- **Do not copy a foreign skill just to make it visible** — direct read preserves the target's provenance and avoids silently changing the active profile.
- **Do not expose configuration wholesale while locating a profile** — read only identifying metadata because config files can contain credentials, hashes, or tokens.
