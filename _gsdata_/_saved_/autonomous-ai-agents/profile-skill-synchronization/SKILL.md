---
name: profile-skill-synchronization
description: "Synchronize skills between isolated Hermes profiles safely."
version: 0.1.0
author: Eduardo Kiwel Teixeira, Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes, profiles, skills, synchronization, symlink]
    related_skills: [cross-profile-skill-access]
---

# Profile Skill Synchronization

Use this skill when one Hermes profile must expose another profile's skills through an automatic, auditable routine. Keep profiles isolated: the source remains authoritative, the destination receives a namespaced catalog, and existing destination entries are never silently replaced.

## Procedure

1. Resolve both profiles from Hermes metadata and `$HERMES_HOME`; treat the default profile as the Hermes home root when it has no `profiles/<name>` directory.
2. Define direction and ownership before editing. Use the source profile's skill tree as authoritative and never infer ownership from a display name, hostname, or an already-imported category.
3. Inventory source entries recursively, retaining category and frontmatter name. Exclude hidden directories, hub/cache state, and foreign catalogs already imported from another profile.
4. Audit candidate text for concrete credential fingerprints before exposing it. Skip or quarantine a contaminated skill, but treat clearly redacted or placeholder documentation as non-secret.
5. Create a flat destination namespace containing one directory symlink per skill. Do not use `namespace/category/skill`: Hermes may interpret the extra level as another category, shadow duplicate names, and make loader results misleading.
6. Preserve collisions. Count an identical expected symlink as already present; skip any other object without overwriting it. Do not prune removed source entries automatically.
7. Schedule the operation as an idempotent `no_agent` job owned by the source profile. Keep stdout empty when nothing changed; deliver only material changes and failures to the user's configured Telegram target.
8. Verify the real loader, not only filesystem links: run the destination profile's `skills list`, check a representative non-filtered skill with `skill_view`, and distinguish linked, already-present, skipped, blocked, and loader-visible counts.
9. State that existing conversations may need a new session or authorized gateway restart before they rebuild their skill registry. Never claim a long-lived conversation loaded a newly exposed skill without that verification.

## Safety and rollback

This workflow changes only the destination skill catalog and scheduler. Do not restart gateways, copy secrets, overwrite destination skills, or delete stale links as part of routine synchronization. Roll back by pausing the synchronization job; the namespaced symlinks leave pre-existing destination skills untouched.

## References

- `references/flat-namespace-and-verification.md` — loader behavior, collision accounting, and verification checklist.
