---
name: vikunja-task-management
description: "Use for Vikunja task management and Obsidian TODO imports."
version: 1.0.0
author: J.A.R.V.I.S.
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Vikunja, tasks, projects, subtasks, Obsidian, REST]
    related_skills: [obsidian, agenda, document-to-action-items]
---

# Vikunja Task Management

Manage Vikunja through its REST API with project-aware task creation, safe reconciliation, and native parent/subtask relations. Use this skill whenever the operator asks to create, update, complete, move, delete, inspect, or bulk-import tasks in Vikunja, especially from Obsidian TODO notes.

## Operating rules

1. Explicit task requests may be written immediately; suggestions discovered during conversation remain proposals until the operator asks to create them.
2. Never delete unrelated Vikunja tasks. For an undo/re-import, identify the exact import marker or source provenance first and preserve pre-existing records.
3. When importing a note hierarchy, the note title/file stem is the parent task and its open checklist items are subtasks. Do not flatten the children into titles prefixed with the parent.
4. Import unchecked items by default. Ignore completed `[x]` items unless the operator explicitly requests a full status mirror; preserve the source status if doing so.
5. Skip index cards that merely link to a note already represented as a parent task. Skip empty checkboxes and kanban metadata.
6. If a task contains a due date, follow the `agenda` approval gate: prepare a calendar proposal and never create a Stalwart event automatically without explicit Telegram approval.

## Hermes `/task` command

The user-level `task-command` plugin exposes `/task` in Hermes chat. Use one of these forms for an explicit task-creation request:

```text
/task <project> <title>
/task <project> | <title>
/task <project> + <title>
```

The command discovers live projects, chooses the longest matching project prefix when no separator is used, sends the title literally to Vikunja, and verifies the created task. It must not create a calendar event or mutate unrelated tasks. If the project is unknown or ambiguous, report the live project choices instead of guessing.

## Credentials and safe API use

- Keep the base URL and API token in `~/.config/vikunja/credentials.json`, mode `0600`; never place the token in memory, a skill, a source file, command output, or the final response.
- Before writing, validate the credential with `GET /api/v1/user` and report only status, username, and file mode.
- Use a single authenticated helper that returns structured JSON and suppresses secrets in errors/logs.
- Discover live projects with `GET /api/v1/projects`; do not assume project IDs are stable across instances.
- Read tasks with `GET /api/v1/projects/{project_id}/tasks?page={n}&per_page=50`, paginating until a short page or no new IDs is returned.

## Core Vikunja API operations

- Create a task: `PUT /api/v1/projects/{project_id}/tasks` with `{"title": ..., "description": ...}`.
- Read one task: `GET /api/v1/tasks/{task_id}`.
- Delete one task: `DELETE /api/v1/tasks/{task_id}` only after the scope is established.
- Create a parent/subtask relation: `PUT /api/v1/tasks/{child_id}/relations` with `{"other_task_id": parent_id, "relation_kind": "subtask"}`.
- Verify a hierarchy by reading the parent and checking that its `related_tasks.parenttask` contains every child ID. The relation direction is important: the child is the URL/base task and the parent is `other_task_id`.
- A duplicate child title under different parents is not a duplicate record. Deduplicate by source/parent, not by global title alone.

The tested endpoint details and response shapes are in `references/vikunja-api.md`.

## Hierarchical Obsidian import

1. Resolve the concrete note directory and inspect all Markdown notes with the Obsidian skill/file tools.
2. Build a structured collection before any external write: `{project, parent title, source note, child title, source line, description, URL}`.
3. For each note with actionable children, create one parent task. Use the filename stem as the parent title, cleaned of `.md`; use a friendly title for underscore-separated filenames when appropriate.
4. Convert each open checkbox into a child task. Preserve the original text and source path/line in the description. Preserve course or reference URLs in the description.
5. Treat clearly actionable plain bullets in a TODO note as children, but do not convert unmarked wishlist prose or headings into tasks.
6. Convert independent open cards from an index note into top-level tasks, using the index section for project mapping. Resolve Markdown links and wiki-links only for deduplication; do not leave link syntax in task titles.
7. Map to a live project by folder/section and existing project intent. If no defensible project exists, use Inbox as the explicit fallback.
8. Reuse an exact existing independent task when it already exists in the intended project; do not create a duplicate. Repeated subtasks such as `Comprar o Curso` must still be separate children under each parent.
9. Create parent first, then each child, then the child-to-parent `subtask` relation. Throttle bulk requests modestly and keep a list of created IDs.
10. On any failure, remove only relations/tasks created by this run (or use a unique import marker to identify a partial run), then report the blocker. Do not leave a half-imported hierarchy.
11. Verify created task presence, target project, parent/subtask relation completeness, total counts, and absence of temporary probe tasks. Aggregate and count in code rather than manually.

## Safe undo and re-import

- Mark imported descriptions with a unique, human-readable run marker plus `Origem: Obsidian — <path>, linha <n>`.
- Before undoing, list tasks across the relevant projects and select only records carrying that marker/source provenance.
- Delete imported records in a controlled batch, verify zero marked records remain, and confirm unrelated task IDs/titles were preserved.
- Rebuild the hierarchy from the source notes, not from the flattened task titles.

## Project mapping

Project names and IDs are instance-specific. Read the live project list every run. Maintain the operator's current folder/section mapping and exceptions in `references/kiwel-obsidian-project-map.md`; use it as a starting point, then prefer live evidence such as an existing exact task in a project.

## Verification checklist

- [ ] Credential validation succeeded without exposing the token.
- [ ] Live projects were discovered and every destination is justified or Inbox fallback is explicit.
- [ ] Completed source items and index links were handled according to the operator's requested import mode.
- [ ] Every created child has the intended project and a native `subtask` relation to its parent.
- [ ] Counts were computed in code and match the structured source collection.
- [ ] Pre-existing tasks were preserved; no test/probe tasks remain.
- [ ] Source paths/lines and useful URLs are present in descriptions.
- [ ] Dates, if present, were routed through the calendar approval policy rather than silently creating events.
