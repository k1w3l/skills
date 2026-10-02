---
name: coding-agent-orchestration
description: "Delegate software work to external coding-agent CLIs such as Claude Code, Codex, and OpenCode; choose modes, run safely, monitor, and verify outputs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding-agent, autonomous-agents, claude-code, codex, opencode, delegation, pty, process]
    related_skills: [hermes-agent, github-operations, systematic-debugging]
---

# Coding Agent Orchestration

Use this umbrella when the user wants an external autonomous coding worker to implement, refactor, review, or debug code. Pick the agent from availability, requested vendor, and task shape; keep Hermes responsible for scope, verification, git hygiene, and final reporting.

## Universal workflow

1. Confirm or infer a narrow workdir and check git status before letting an agent write.
2. Prefer bounded one-shot modes for clear tasks; use interactive/background sessions only when follow-up steering is valuable.
3. For long tasks use `background=true` and normally `notify_on_complete=true`, then inspect logs/diffs/tests yourself.
4. Never report success from an agent self-report alone: verify files, diffs, tests, build output, PR URLs, or command status.
5. Keep prompts scoped: exact goal, relevant files, constraints, tests to run, and commit/PR policy.
6. Review `git diff` and run targeted tests before committing or handing off.

## Choosing an agent

- **Claude Code**: best when user explicitly asks for Claude, needs strong autonomous implementation, structured print-mode analysis, or Claude-specific slash/plugin/MCP features.
- **Codex CLI**: best when the current environment is already authenticated for Codex/OpenAI, for OpenAI-specific coding-agent behavior, or when Hermes itself runs through the `openai-codex` provider.
- **OpenCode**: best when a provider-agnostic/open-source TUI is requested, when selecting arbitrary providers/models, or when resuming named OpenCode sessions.

## Claude Code quick sheet

Install/auth/check:

```bash
npm install -g @anthropic-ai/claude-code
claude auth status --text
claude doctor
claude --version
```

Legacy/virtualized CPU pitfall: newer Claude Code native builds can hang silently on KVM/older CPUs without AVX even for `--version`. Diagnose with `lscpu` flags and, if the native `bin/claude.exe` path hangs, install the last JS CLI build instead:

```bash
npm install -g @anthropic-ai/claude-code@2.1.112
claude --version
```

If npm's global prefix is under Hermes (for example `~/.hermes/node`), ensure `~/.hermes/node/bin` is on PATH for both interactive and login shells before concluding installation failed.

Prefer print mode for bounded tasks because it exits cleanly and skips workspace/permission dialogs:

```bash
claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10
claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5
```

Use tmux for multi-turn interactive work. Handle first-run trust with Enter; if using `--dangerously-skip-permissions`, the warning defaults to **No**, so send Down then Enter. Capture panes to monitor, and exit with `/exit` when done.

## Codex CLI quick sheet

Install/auth/check:

```bash
npm install -g @openai/codex
codex --version
```

Codex normally needs a git repo and PTY. A missing `OPENAI_API_KEY` is not proof auth is absent because CLI OAuth may live under `~/.codex/auth.json`.

```bash
codex exec 'Add dark mode toggle to settings'          # one-shot
codex exec --full-auto 'Refactor the auth module'      # auto-approve workspace edits
codex exec --sandbox danger-full-access '<task>'       # gateway/service contexts where sandboxing breaks
```

In Hermes gateway/service contexts, Codex sandboxing can fail with bubblewrap/user-namespace errors; use `--sandbox danger-full-access` only with a narrow workdir, clean git status, diff review, and tests as the safety boundary.

## OpenCode quick sheet

Install/auth/check:

```bash
npm i -g opencode-ai@latest    # or: brew install anomalyco/tap/opencode
opencode --version
opencode auth list
which -a opencode              # diagnose binary resolution differences
```

Bounded task:

```bash
opencode run 'Add retry logic to API calls and update tests'
opencode run 'Review this config for security issues' -f config.yaml -f .env.example
opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4
```

Interactive/background session:

```python
terminal(command="opencode", workdir="/path/to/project", background=True, pty=True)
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow and add tests")
process(action="poll", session_id="<id>")
process(action="write", session_id="<id>", data="\x03")  # exit; /exit is not valid OpenCode
```

## Parallelization patterns

- Use separate git worktrees for independent issue fixes or reviews.
- Give each agent an isolated branch/workdir and an explicit output contract.
- Monitor with `process(action="poll"|"log"|"wait")` rather than blind sleeps.
- Merge results manually after tests pass; agents should not be trusted to reconcile conflicting changes without review.

## Verification checklist

- `git status --short` and `git diff` inspected.
- Tests/lints/builds relevant to the change executed by Hermes, not merely claimed by the child agent.
- Any PR/issue/comment side effect has a verifiable URL/ID and was fetched or checked.
- Final answer distinguishes completed work, verification output, and remaining risks.
