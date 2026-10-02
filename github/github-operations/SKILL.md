---
name: github-operations
description: "Operate GitHub repositories end-to-end with gh and git: authentication, repo setup, issues, PRs, code review, CI, releases, and codebase inspection."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, gh, git, pull-requests, issues, code-review, repositories, ci]
    related_skills: [coding-agent-orchestration, requesting-code-review]
prerequisites:
  commands: [git, gh]
---

# GitHub Operations

Use this umbrella for GitHub work that crosses repository management, authentication, issues, pull requests, reviews, CI, releases, and codebase inspection. Keep the workflow evidence-backed: use `gh`/`git`, inspect current state, and verify every side effect.

## Universal prerequisites

```bash
gh auth status
git status --short
git remote -v
gh repo view --json nameWithOwner,defaultBranchRef,url
```

If auth fails, run `gh auth login` or set an appropriate token. For HTTPS token use, check credential helpers before rewriting remotes. For SSH, verify keys and `ssh -T git@github.com`.

## Repo management

```bash
gh repo clone OWNER/REPO
gh repo create OWNER/REPO --private --source=. --remote=origin --push
gh repo fork OWNER/REPO --clone
gh release list
gh release create v1.2.3 dist/* --notes-file RELEASE.md
```

Rules: preserve existing remotes unless the user asked to change them; check default branch; avoid force pushes without explicit confirmation.

## Issues

```bash
gh issue list --state open --json number,title,labels,assignees,url
gh issue view 123 --comments
gh issue create --title '...' --body-file issue.md --label bug
gh issue edit 123 --add-label triage --assign @me
gh issue comment 123 --body-file reply.md
```

Use issue templates when available. Include reproduction steps, expected/actual behavior, environment, and verification evidence for bugs.

## Pull request lifecycle

```bash
git checkout -b feature/name
git add -A && git commit -m 'feat: concise summary'
git push -u origin feature/name
gh pr create --fill --base main --head feature/name
gh pr view --json number,url,headRefName,baseRefName,mergeStateStatus,statusCheckRollup
gh pr checks --watch
gh pr merge --squash --delete-branch
```

Use conventional commits when appropriate. Before opening or updating a PR, run relevant tests and include the real outputs in the PR body or final report.

## Code review

Review current facts, not assumptions:

```bash
gh pr checkout 42
git diff origin/main...HEAD
gh pr diff 42
gh pr view 42 --comments --json files,commits,reviews,comments,statusCheckRollup
```

Prioritize correctness, security, data loss, compatibility, and test coverage. For inline comments, use `gh api` or REST only after forming precise file/line comments. Keep review output actionable and avoid style-only noise unless requested.

## CI troubleshooting

```bash
gh run list --branch <branch> --limit 10
gh run view <run-id> --log-failed
gh pr checks <number>
```

Compare local reproduction with CI logs. Do not claim CI passed until `gh pr checks` or run status confirms it.

## Codebase inspection

Use lightweight repository metrics when asked to characterize a codebase:

```bash
pygount --format=summary .
git ls-files | wc -l
```

Report language mix, generated/vendor exclusions, notable directories, test locations, and risks. Do not use line counts as quality measures without context.

## Side-effect verification checklist

- For created issues/PRs/releases/comments, report the URL returned by `gh` and fetch/view it once.
- For merges or pushes, show branch/remote state after the operation.
- For reviews, include exact files/lines or a clear summary of blockers and non-blockers.
- Keep local worktree clean or explicitly state remaining uncommitted changes.
