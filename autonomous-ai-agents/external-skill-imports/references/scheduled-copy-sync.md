# Scheduled copy synchronization for external skills

Use this pattern when the operator explicitly wants external skills **copied into a durable local cache** rather than linked directly. A local copy remains usable while the external/NAS source is unavailable; the external tree stays authoritative for additions and updates.

## Design

1. Inspect the existing source-to-local mapping before choosing destinations. Directory labels may not match the effective local catalog, and local trees may contain symlinks that make naïve counts misleading.
2. Keep synchronization unidirectional: external source → local skill directories → Hermes category symlinks.
3. Discover only immediate child directories containing a valid `SKILL.md` with YAML frontmatter.
4. Copy the complete skill directory, but normally exclude generated or bulky state such as `.git/`, `node_modules/`, `__pycache__/`, `*.pyc`, and sync-database files. Dependencies should remain reproducible from manifests.
5. Compare content with checksums when correctness matters; mtime and size alone can miss changes copied through other synchronization tools.
6. Do not overwrite a destination symlink, regular file, or Hermes catalog entry that points elsewhere. Report the collision and preserve it.
7. Create a namespaced category symlink for every newly copied skill so Hermes can discover it. Existing expected symlinks are idempotent.
8. Use a non-blocking file lock to prevent overlapping scheduled runs.
9. Make the script idempotent and silent when no files or links changed. Print concise output only for real changes or failures.
10. Do not propagate deletions unless the operator explicitly asks for mirror semantics. Add/update-only behavior avoids turning a transient or partial source tree into local data loss.

## Scheduling with Hermes

A deterministic sync should use a Hermes cron job in `no_agent=True` mode: no model call is needed. A schedule such as `0 */4 * * *` runs six times daily. For gateway delivery, empty stdout means no notification; non-empty stdout can report actual changes, and a non-zero exit produces an error alert.

The cron script may be stored under `~/.hermes/scripts/` and referenced by filename. Verify the finished routine by:

1. Running a dry run and reviewing planned destinations and collisions.
2. Running once for real.
3. Running immediately again and asserting empty stdout.
4. Verifying representative new skills with `skills_list(category=...)` and `skill_view(...)`.
5. Triggering the cron job manually once and confirming status `ok`.

## Pitfalls

- Do not claim newly copied skills are visible merely because files exist; verify Hermes catalog discovery and loadability.
- Do not blindly copy into the root `~/.hermes/skills/`; use source-specific categories to avoid shadowing bundled or hub-installed skills.
- Do not use a symlink-only design when the operator explicitly requests copying or needs skills available during source/NAS outages.
- Existing local skill trees may mix real directories and links to another catalog. Inspect link targets before establishing the mapping.
- Current sessions may need `/reload-skills`; future sessions rescan the catalog automatically.
