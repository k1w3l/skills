# Cross-profile import workflow

Use this reference after an explicit request to expose one Hermes profile's skills to another. It covers discovery and provenance; it does not authorize editing the source profile or restarting a gateway.

## Decision table

| Situation | Action |
|---|---|
| Need to read one foreign skill | Read the exact source `SKILL.md` directly and report its path; do not import it. |
| Need many skills available in the active profile | Create a namespaced destination directory and one directory symlink per active source entry. |
| Destination entry is the expected symlink | Leave it in place and count it as already present. |
| Destination entry exists but is not that symlink | Skip it and report the collision; never overwrite. |
| Frontmatter name collides with an active skill | Keep both source paths; compare hashes and do not silently change bare-name precedence. |
| A scanner finds a real credential | Do not expose that file; move the secret to a credential store or `.env` owned by the source profile. |
| Only documentation placeholders match a secret pattern | Keep the file, but redact values in reports and do not call them credentials. |
| A long-lived gateway already has a session | Treat the import as available to new sessions; request authorization before `/new`, `/reset`, or gateway restart if continuity matters. |

## Recipe

1. **Resolve both homes.** Identify the active profile's `$HERMES_HOME`. Locate the target profile's `profile.yaml`; the default profile commonly owns the Hermes home root rather than `profiles/default/`. Read identifying metadata only.
2. **Inventory active entries.** Under the source `skills/` tree, include a top-level directory when it contains `SKILL.md` directly or contains active child skill directories. Skip dot-prefixed directories such as archives, hub state, locks, and caches. Parse frontmatter `name` values and retain source paths.
3. **Audit before exposure.** Scan text files for concrete secret formats (provider keys, bot tokens, private-key blocks, bearer literals, and credential-bearing URLs). Emit only relative paths and redacted classifications. Do not dump matching lines or values into chat, logs, or a report.
4. **Create the namespace.** Under the active profile, make `skills/<source>-skills/` and create one directory symlink per selected source entry. For each destination: keep an identical symlink, skip any other existing object, and record the outcome. Do not copy unless the user explicitly requests a local cache and the copy-sync workflow is in place.
5. **Compare collisions.** Group by frontmatter name and compare `sha256` of `SKILL.md` for duplicates. Identical content is already functionally shared; divergent content must remain source-qualified and must not replace the active profile's copy.
6. **Verify the real registry.** Run `hermes -p <active> skills list` and filter the source category. Then call `skills_list(category=<source>-skills)` and `skill_view(name=<unique-skill>)` for at least one direct and one nested skill. A raw `rglob` count is not sufficient because common walkers do not recurse through directory symlinks.
7. **Close accurately.** State exact source and destination paths, linked/already/skipped counts, collision handling, loader-visible count, and whether a new session is required. Do not call a skill "loaded" merely because its directory exists; say "discoverable" until the registry has returned it.

## Reusable verification pattern

```bash
hermes -p <active-profile> skills list
hermes -p <active-profile> skills list | <filter only the source namespace>
```

Use the Hermes `skills_list` and `skill_view` tools for the second-stage check. Keep the source namespace stable so provenance remains visible and future syncs can be audited without comparing opaque copies.
