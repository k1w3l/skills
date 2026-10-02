# Vikunja API Reference

This reference records the verified REST shapes used by the `vikunja-task-management` skill. Recheck live project IDs and the instance version before relying on them.

## Authentication probe

Read `~/.config/vikunja/credentials.json` without printing its token and call:

```text
GET /api/v1/user
Authorization: Bearer ***
```

A successful response includes the username and user id. Keep the credential file at mode `0600`.

## Project and task reads

```text
GET /api/v1/projects
GET /api/v1/projects/{project_id}/tasks?page=1&per_page=50
GET /api/v1/tasks/{task_id}
```

Paginate project tasks until a short page or no new IDs appears. The task representation includes `project_id`, `title`, `description`, `done`, and `related_tasks`.

## Create and delete

```text
PUT /api/v1/projects/{project_id}/tasks
Content-Type: application/json

{"title":"Example","description":"Source provenance"}
```

The tested create response is HTTP 201 with the created task object and its numeric `id`.

```text
DELETE /api/v1/tasks/{task_id}
```

Only delete IDs selected by an explicit import marker/source provenance or an explicit operator request.

## Native subtasks

Create the relation with the child as the base task:

```text
PUT /api/v1/tasks/{child_id}/relations
Content-Type: application/json

{"other_task_id": <parent_id>, "relation_kind": "subtask"}
```

The tested response is HTTP 201. Reading the parent task then exposes the child under `related_tasks.parenttask`; reading the child exposes the parent under `related_tasks.subtask`.

Do not reverse the IDs: using the parent as the base task makes the semantic direction wrong. Repeated child titles are valid when they belong to different parents; identity is the parent/source relationship, not title alone.

## Bulk safety pattern

Use a run marker plus source path/line in descriptions. Collect every created ID, create parents before children, then add relations. On a failure, remove only this run's relations/tasks and verify unrelated tasks remain. After completion, re-read all target projects, verify counts and relations, and ensure no probe/task-test records remain.
