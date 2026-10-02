# Publish an Omarchy plugin

Sources:

- https://plugins.omarchy.org/publish.html (updated 20 Aug 2026)
- https://github.com/omacom/omarchy-plugin-marketplace
- [SUBMISSION.md](https://github.com/omacom/omarchy-plugin-marketplace/blob/main/SUBMISSION.md)

The marketplace validates listings (layout + Quattro compatibility + a static
baseline). It is **not** a security review. Plugins run unsandboxed. You remain
responsible for code, assets, documentation, and license.

Browse https://plugins.omarchy.org/ (also https://omarchyplugins.com/) before
writing something that already exists.

## Prepare the repository

One public GitHub repository **per plugin**, files at the **repository root**:

- Valid `manifest.json`
- README with installation **and** removal
- License file; document external dependencies
- Safe install and removal (do not overwrite user config without consent)
- Globally unique id **outside** `omarchy.*`
- Optional one root preview: `preview.png`, `preview.jpg`, `preview.jpeg`,
  `preview.webp`, or `preview.avif` (max 50 MB / 40 megapixels). The
  marketplace generates card/detail images; no need to hand-optimize.

Create and validate before submit:

```fish
omarchy plugin clone omarchy.clock   # or start from your existing tree
omarchy plugin validate ~/git/your-plugin
```

Minimal marketplace-shaped manifest (kind must match the real plugin):

```json
{
  "schemaVersion": 1,
  "id": "yourname.plugin",
  "name": "Plugin name",
  "version": "1.0.0",
  "author": "Your name",
  "description": "What the plugin does.",
  "kinds": ["overlay"],
  "entryPoints": {
    "overlay": "Plugin.qml"
  }
}
```

Prefer `io.github.yourname.plugin-name`. Search the marketplace for the id
first. Changing it later means updating every install command and the README.

### Manifest fields (all required for listing)

| Field | Purpose |
|-------|---------|
| `schemaVersion` | Omarchy manifest contract version |
| `id` | Unique namespaced plugin identifier |
| `name` | Human-readable name |
| `version` | Current version (up to 64 characters on the marketplace) |
| `author` | Shown in the marketplace |
| `description` | Short marketplace summary |
| `kinds` | Capabilities exposed to Omarchy |
| `entryPoints` | QML file for each kind |

## Listing metadata

One category (exact spelling, case-sensitive):

`Appearance`, `Desktop`, `Developer Tools`, `Hardware`, `Kids`,
`Productivity`, `System`, `Widgets`, `Other`

One to three tags. The GitHub **form** dropdown uses title case (`AI`, `Bar`,
…). The **CLI/AI body** in SUBMISSION.md uses lowercase:

`ai`, `bar`, `education`, `games`, `hyprland`, `kids`, `launcher`, `media`,
`power-management`, `quickshell`, `security`, `system`, `workspaces`

Optional: suggest one missing reusable tag. Reviewers decide.

## Submit

Human form (preferred when the owner is at the keyboard):

https://github.com/omacom/omarchy-plugin-marketplace/issues/new?template=submit-plugin.yml

Automated validation checks the current commit; a maintainer must then apply
`approved-and-verified`. New listings are not published on the legacy
`approved-for-listing` label.

### CLI / agent body

Preserve **every heading, order, and checklist wording**. Replace placeholders.
Show the completed title and body to the owner. Create the issue **only after
explicit approval**.

```fish
# write /tmp/omarchy-plugin-submission.md with the six headings below,
# then:
gh issue create \
    --repo omacom/omarchy-plugin-marketplace \
    --title "[Plugin]: Plugin Name" \
    --body-file /tmp/omarchy-plugin-submission.md
```

Body template:

```markdown
### Repository URL

https://github.com/your_github_name/your_plugin_repository

### Category

Widgets

### Tags

bar, quickshell

### Suggest a missing tag

_No response_

### Maintainer notes

_No response_

### Submission checklist

- [x] The repository is public and contains installation and removal instructions.
- [x] I have documented the plugin license and any external dependencies.
- [x] I confirm that I own or have permission to submit this plugin and its preview assets.
- [x] The plugin does not overwrite user configuration without explicit consent.
- [x] I understand that approval is for listing and is not a security review.
```

Rules:

- Repository URL is the GitHub **root**, no trailing slash, no `/tree/main`
- Category matches the list exactly, no backticks
- One to three allowed tags
- All five checklist items true and checked
- Title starts with `[Plugin]: `

Agent steps from SUBMISSION.md:

1. Read root `manifest.json`, README, and license.
2. Pick one category and one to three tags from the allowed lists.
3. Keep headings/order/checklist text exact.
4. Ask the owner to confirm ownership and every checklist item.
5. Show title and body before creating the issue.
6. Create the issue only after the owner approves.

## After the issue opens

The bot keeps one validation comment and one Automated Security Baseline
comment. Baseline is static (does not execute plugin code) and reports
`passed`, `review-required`, or `needs-fixes`. Publication requires
`approved-and-verified` plus a fresh exact-commit scan.

The baseline looks for a small set of patterns (download-to-shell, unpinned
external git execution, passwordless sudoers, privileged process control from
shared temp). It is not a full audit.

On failure: fix the **existing** repo or issue. Do not open a duplicate.
Editing the issue re-runs detection.

If no bot comment appears, check: title starts with `[Plugin]:`, six headings
in order, exact category, all five boxes checked.

## Update or verify a listing

https://github.com/omacom/omarchy-plugin-marketplace/issues/new?template=verify-plugin.yml

- **Verify and publish a newer upstream commit** — existing plugin id, repo
  root URL, full 40-character SHA of current HEAD. Id set must not change.
- **Verify the currently listed snapshot** — id, repo, and exact
  `listingValidatedCommit`.

A later HEAD that is not the approved snapshot shows as `Update unverified`.
Marketplace install/update still clones mutable upstream HEAD and is not
verification-bound. Users who care should pin the reviewed commit themselves.

Private security reports:

https://github.com/omacom/omarchy-plugin-marketplace/security/advisories/new
