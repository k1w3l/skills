---
name: hermes-skill-operations
description: Install, verify, update, and manage Hermes Agent skills through the CLI, especially hub/official skills that prompt for confirmation.
version: 1.0.0
author: J.A.R.V.I.S.
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, skills, cli, hub, official-skills, skill-library]
    related_skills: [hermes-agent, hermes-agent-skill-authoring]
---

# Hermes Skill Operations

Use this skill when the user asks to install, update, uninstall, inspect, verify, or otherwise manage Hermes Agent skills from the skill hub or local skill library.

This skill is about operating the skill library. For general Hermes configuration or troubleshooting, also load `hermes-agent` first and treat the live Hermes docs as authoritative.

## Standard workflow

1. Load `hermes-agent` when the task involves Hermes itself.
2. Run the requested Hermes skill command exactly, unless the user’s wording clearly implies a safer preview such as `hermes skills inspect`.
3. If `hermes skills install ...` prompts for confirmation and the user already explicitly requested installation, answer the prompt non-interactively:

```bash
printf 'y\n' | hermes skills install <skill-id>
```

4. Verify the result after installation:

```bash
hermes skills list | grep -i '<skill-name-or-keyword>'
```

5. Report the installed skill ID/category/name and whether it is enabled.
6. Briefly mention scanner verdicts when shown by the CLI, especially `CAUTION` or `DANGEROUS`, but do not over-explain if the skill is official/builtin and the install succeeded.

## Official skill install pattern

For official hub skills such as:

```bash
hermes skills install official/devops/docker-management
hermes skills install official/mlops/whisper
hermes skills install official/software-development/code-wiki
```

Prefer:

```bash
printf 'y\n' | hermes skills install official/<category>/<skill>
hermes skills list | grep -i '<skill>'
```

The first bare install may cancel if the CLI prompt receives no input. If that happens, retry with `printf 'y\n' | ...` rather than treating it as a failure.

## Scanner verdict handling

Hermes may quarantine and scan official skills before installation.

- `SAFE`: mention success only, unless the user asks for details.
- `CAUTION`: say the scanner warned about expected setup or dependency operations.
- `DANGEROUS`: say the scanner warned because the skill discusses privileged or host-affecting operations; if the source is official/builtin and the CLI says `Decision: ALLOWED`, installation may proceed when the user explicitly requested it.

Do not persist broad negative claims such as “this skill is dangerous to use.” Preserve the nuance: the scanner is flagging capabilities or command examples, not necessarily a failed or malicious install.

## Pitfalls

- Do not stop after an interactive prompt cancels. If the user requested installation, retry non-interactively.
- Do not claim a skill is installed until `hermes skills list` or equivalent verification confirms it.
- Do not edit hub-installed or bundled skills when curating lessons; create or update an agent-owned umbrella skill instead.
- Do not store transient scanner output as memory. Scanner details belong in the task reply or, if reusable, in this operational skill.
