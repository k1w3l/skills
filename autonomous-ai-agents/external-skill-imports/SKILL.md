---
name: external-skill-imports
description: "Import, copy-sync, or expose skills from external agent directories and network storage to Hermes, then verify catalog discovery and loadability."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [skills, hermes, claude, agents, import, symlink]
    related_skills: [hermes-agent]
created_by: "agent"
---

# External Skill Imports

Use this skill when the operator asks to "carregar", import, expose, sync, or make available skills from another local agent directory, especially:

- `~/.agents/skills/`
- `~/.claude/skills/`
- another directory containing subdirectories with `SKILL.md`

This is a Hermes skill-library integration workflow, not a request to read every skill into the current model context.

## Default approach

Prefer symlinking external skill directories into the active Hermes profile's skill library rather than copying them. Symlinks keep the external skill source authoritative and avoid stale duplicated SKILL.md files.

**Copy exception:** when the operator explicitly requests copying, the source is removable/network storage, or local availability during source outages matters, build a unidirectional scheduled local cache instead. Follow `references/scheduled-copy-sync.md` for source mapping, checksum-based updates, collision handling, Hermes category links, idempotent no-agent cron execution, and end-to-end verification.

Use a source-specific category directory under the active profile, for example:

- `~/.hermes/skills/claude-agent-skills/` for `~/.agents/skills`
- `~/.hermes/skills/claude-local-skills/` for `~/.claude/skills`

For named profiles, use that profile's own skill directory instead of the default profile, e.g. `~/.hermes/profiles/<profile>/skills/...`.

## Workflow

1. Locate candidate skills by finding immediate child directories that contain `SKILL.md`.
2. Inspect frontmatter names when possible to detect duplicate skill names already present in Hermes.
3. Create a destination category directory under the active Hermes profile's `skills/` tree.
4. For each candidate, create a directory symlink at `destination/<source-dir-name>` pointing to the source skill directory.
5. If a destination already exists:
   - treat it as already imported only if it is the expected symlink to the same source;
   - otherwise skip it and report the collision rather than overwriting.
6. Verify discovery with `skills_list(category=<category>)`.
7. Verify at least one representative skill with `skill_view(name=<skill-name>)` before claiming success.

## Safe import script pattern

```python
from pathlib import Path
import os

src_root = Path('/home/kiwel/.claude/skills')
dst_root = Path('/home/kiwel/.hermes/skills/claude-local-skills')
dst_root.mkdir(parents=True, exist_ok=True)

created = []
already_present = []
skipped = []

for skill_md in sorted(src_root.glob('*/SKILL.md')):
    src = skill_md.parent.resolve()
    dst = dst_root / src.name
    if dst.exists() or dst.is_symlink():
        if dst.is_symlink() and Path(os.readlink(dst)).resolve() == src:
            already_present.append(src.name)
        else:
            skipped.append((src.name, 'destination exists and is not the expected symlink'))
        continue
    dst.symlink_to(src, target_is_directory=True)
    created.append(src.name)

print('created:', created)
print('already_present:', already_present)
print('skipped:', skipped)
```

## Verification checklist

- The destination import root exists.
- The expected number of symlinks exists under the import root.
- `skills_list(category=...)` shows imported skills.
- `skill_view(name=...)` can load at least one imported skill.
- The final report distinguishes all linked skills from uniquely visible skills, because duplicate names may be deduplicated or shadowed in display.

## Pitfalls

- Do not say skills are "loaded" when they were only made discoverable. Say they are available in the Hermes skill catalog and will be loaded on demand.
- Do not copy secrets from imported skills into the final reply. If a skill contains plaintext credentials, mention the issue generically and recommend moving secrets to `.env` or a credential store.
- Do not overwrite an existing Hermes skill directory when importing. Use a namespaced category directory to avoid collisions.
- Do not attempt to load every imported skill into the current context; large skill directories can overflow context and are better loaded by trigger.
- Do not edit protected Hermes or hub-installed skills just to document this workflow; create or update an agent-authored umbrella instead.
