# Portable Skills-Only Hermes Backups

Use this reference when the operator wants to move skills between Hermes installations without sharing the rest of a profile.

## Scope and archive layout

Stage only the active profile's `skills/` tree. Do not use a full profile export for this narrow purpose: `hermes profile export default` can include configuration, persona files, memories, sessions, plugins, and cron data even though `auth.json` and `.env` are excluded.

Create an archive with exactly one top-level directory, for example:

```text
hermes-skills-<timestamp>/
├── README.md
├── manifest.json
└── skills/
    ├── <category>/
    │   └── <skill>/SKILL.md
    └── <root-level-skill>/SKILL.md
```

Preserve each skill's support files (`references/`, `templates/`, `scripts/`, and assets), not just `SKILL.md`. Keep the archive outside a source checkout when possible.

## Filtering rules

At the root of the source `skills/` tree, omit Hermes bookkeeping and curator state such as:

- `.usage.json` and its lock file
- `.curator*`
- `.archive/`
- `.hub/`
- `.bundled_manifest`

At any depth, omit credential/profile-data names such as `auth.json`, `.env`, `sessions/`, `memories/`, `state.db*`, `logs/`, `workspace/`, and `plans/`. Do not remove `.env.example` solely because it contains the substring `.env`; redact its contents instead.

Run Hermes' secret redactor on text-like files before writing the manifest. A skills-only archive may still contain personal prose or operational details, so inspect it before sharing it.

## Symlink handling

Normal external imports should prefer directory symlinks, because the external source remains authoritative. A portable backup is different: materialize every symlink into regular files/directories while staging. Otherwise the archive can contain absolute links back to `~/.agents/skills` or `~/.claude/skills`, which will be broken on the destination machine.

The staging copier should:

1. resolve symlink files and directories;
2. copy their targets as regular content;
3. detect broken links and fail rather than silently omitting them;
4. detect cycles before recursive traversal; and
5. verify that the final tarball contains no symlink members.

## Manifest and counts

Record at least:

- archive format/version and generation time;
- Hermes version used to create it;
- source profile and source tree (without secret paths);
- whether symlinks were materialized;
- skill path, frontmatter `name`, byte size, and SHA-256 for each `SKILL.md`;
- category counts; and
- filesystem-instance count versus unique frontmatter-name count.

Those counts intentionally differ when the library contains duplicate names, symlinked imports, or platform-specific skills that are not enabled on the current host.

## Validation and restore

Before delivery, validate all of the following:

```bash
sha256sum -c <archive>.sha256
tar -tzf <archive>
```

Also inspect the tar members programmatically: require exactly one top-level directory, `skills/` plus `README.md` and `manifest.json` beneath it, no symlinks, and no forbidden profile entries.

Smoke-test the public import path in an isolated temporary environment, not the user's real profile:

```bash
set tmp (mktemp -d)
env HOME=$tmp HERMES_HOME=$tmp/.hermes hermes profile import <archive> --name skills-smoke
env HOME=$tmp HERMES_HOME=$tmp/.hermes hermes -p skills-smoke skills list --enabled-only
```

Compare the imported `SKILL.md` count with the manifest and report the catalog's enabled count separately. The importer creates a separate profile; it does not merge into an existing default profile.

For a merge, extract the archive, copy only its `skills/` directory into the target Hermes home, inspect duplicate-name collisions, and start a new Hermes session so skill discovery is refreshed.
