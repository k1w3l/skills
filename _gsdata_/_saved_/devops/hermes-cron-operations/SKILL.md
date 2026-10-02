---
name: hermes-cron-operations
description: "Use for Hermes cron diagnosis and safe job recovery."
version: 1.0.0
created_by: agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, cron, scheduling, model-drift, delivery, troubleshooting]
---

# Hermes Cron Operations

Use this class-level skill whenever a Hermes scheduled job stops producing output, reports a failure, needs a schedule/model/routing change, or must be verified after a Hermes update. It complements the domain-specific `scheduled-news-digests` skill: this skill owns scheduler diagnosis and safe job mutation; that skill owns editorial collection and curation.

## Safety contract

- Inspect the exact job and saved output before changing it; do not infer a cause from `last_status` alone.
- Never guess a job ID. Use `cronjob(action="list")` or `hermes cron list` and match the name/script.
- Preserve the job's editorial prompt, schedule, collector, deduplication, and delivery contract unless the user explicitly asks to change them.
- Do not manually fire a job that can send external messages unless the operator explicitly authorizes an immediate edition/test. For direct-card jobs, validate the collector and saved schedule instead.
- Treat saved secrets as opaque. Never print tokens, OAuth files, or credentials.

## Diagnosis workflow

1. **Inventory**: list enabled and disabled jobs; record job ID, schedule, enabled state, provider/model, delivery target, last status, next run, and last error.
2. **Read evidence**: inspect the newest job output under `~/.hermes/cron/output/<job-id>/` and the matching `~/.hermes/logs/agent.log`/`errors.log` entries. Distinguish collection, generation, delivery, and scheduler-guard failures.
3. **Check current configuration**: read the non-secret `model.default`, `model.provider`, and any relevant cron settings from `~/.hermes/config.yaml`.
4. **Classify the failure**:
   - `drift_skip:silent` / “job is unpinned” → Hermes intentionally made no inference call because the global model/provider changed.
   - collector JSON/HTTP/parse error → repair or verify the collector and its source fallback.
   - plugin import error → compare fresh-process imports with the current source and reload the gateway before changing prompts.
   - card-tool or platform error → inspect the tool result, routing, and Telegram/API error separately from model generation.
5. **Apply the smallest fix** and preserve unrelated fields.
6. **Verify** with a fresh job list, a direct collector run through its interpreter, and the relevant fresh-process import or service health check.

## Model-drift recovery

When a job is skipped with `[drift_skip:silent]`:

1. Read the current `model.default` and `model.provider`.
2. Pin the affected job explicitly rather than reverting the global model or changing the prompt:

```bash
hermes cron edit <job-id> --provider <current-provider> --model <current-model>
```

3. Confirm `cronjob(action="list")` shows non-null provider/model for that job.
4. Leave schedule, script, prompt, `deliver`, and enabled state unchanged unless independently proven wrong.
5. Treat old drift-skip output as historical. The next scheduled run is the first live proof; do not claim delivery before it.

See `references/model-drift-recovery.md` for a compact evidence and verification recipe.

## Collector and delivery verification

For a job with a pre-run script:

- execute the script with its intended interpreter; do not assume the executable bit is set;
- require parseable, bounded output and inspect candidate count, timestamps, source diversity, real URLs, and fetch errors;
- for direct-card jobs, keep ordinary cron delivery local/suppressed when the card tool itself sends the platform messages, preventing duplicate plain text;
- verify tool-reported sent count and errors before accepting a silence sentinel;
- do not treat `last_status: ok`, an empty response, or `[SILENT]` as proof that the user received content;
- after a successful change, verify the next-run schedule in the editorial timezone and report what is proven: collected, generated, tool-sent, platform-accepted, or user-confirmed.

## Persistent service jobs

When a Hermes web/dashboard or other long-running helper must survive VM reboot, prefer a dedicated `systemd --user` unit:

- `WantedBy=default.target`;
- `Restart=always` with a short `RestartSec`;
- explicit `HERMES_HOME`, `VIRTUAL_ENV`, and `PATH`;
- bind locally by default unless authentication is configured for a network bind;
- verify `systemctl --user is-enabled`, `is-active`, the listening port, and a real health/HTTP response;
- confirm user lingering (`loginctl show-user <user> -p Linger`) when boot persistence is required.

Do not report a persistent service as complete from the unit file alone; confirm the live process and port.

## Common pitfalls

- Editing collectors or delivery routing when the scheduler skipped the job before inference because of model drift.
- Running a direct-card job manually merely to clear a historical error and accidentally sending an unrequested duplicate edition.
- Reporting the old `last_status: error` as a current failure after a pin/reload without waiting for or explicitly running the next authorized job.
- Binding a dashboard to a non-loopback address without a configured auth provider.
- Restarting the gateway from inside the gateway process; use the documented external service mechanism or the gateway's own restart control.

## Related skills

- `scheduled-news-digests` — editorial collection, ranking, deduplication, cards, and newsletter-specific verification.
- `hermes-agent` — Hermes configuration, gateway, cron CLI, and service operations.
