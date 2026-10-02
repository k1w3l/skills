---
name: homelab-scheduled-routines
description: "Use when operating homelab reports. Handoff safely."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [homelab, hermes, cron, monitoring, reports, telegram]
    created_by: agent
---

# Homelab Scheduled Routines

Use this class-level skill for recurring infrastructure reports, monitors, and alerts owned by Tiberius, especially when a routine is inherited from another Hermes profile.

## Procedure

1. **Establish the source of truth.** Consult the canonical wiki and the domain skill, then inspect the live source system read-only. For Proxmox-related work, begin with `proxmox-status`; for Home Assistant, verify the authenticated REST API or the existing deterministic collector.
2. **Inventory every owner and producer.** List jobs in both the old and new profiles with `hermes -p <profile> cron list --all`, then enumerate every `script` referenced by the owning profile's `cron/jobs.json` and search the script tree for report/alert output. Classify each producer as visible, event-only, or intentionally silent before changing anything; do not scope a formatting migration to the first examples the operator mentioned. Match exact job name and script before changing anything; never infer an ID from a name or from another profile.
3. **Define ownership before enabling.** Preserve the old job and pause only the exact active duplicate with `hermes -p <old-profile> cron pause <exact-id>`. Keep unrelated personal-device alerts and execution history intact. The old job is the rollback target.
4. **Keep code profile-scoped.** Store wrappers and implementations under `/home/kiwel/.hermes/profiles/<owner>/scripts/` (or the equivalent active profile path), not the default profile's script directory. Preserve an established artifact path when other consumers depend on it, while keeping ownership in the destination profile. Load existing environment configuration at runtime; never copy tokens, cookies, passwords, or connection strings into jobs, scripts, documentation, or logs.
5. **Use deterministic delivery.** Every user-facing Tiberius report, status, alert, diagnostic summary, synchronization result, and future scheduled output uses the shared Telegram presentation contract: compact thematic sections, blank-line spacing, proportional non-overlapping icons, no Cron/job envelope or operational footer, and inline `👍`/`👎` feedback when delivered to Telegram. Prefer `no_agent=true` only for silent/event-only jobs whose direct delivery is handled by the script. For any visible output, use profile-scoped direct Bot API/card delivery with a compact callback namespace and durable feedback store; choose one parser deliberately and normalize the body to it before sending. When using Telegram `parse_mode=HTML`, convert report Markdown markers such as `**bold**` and `` `code` `` to `<b>` and `<code>` and do not wrap the body in `<pre>`, because HTML parsing will otherwise show literal asterisks or suppress inline emphasis. Emit empty stdout on confirmed success so Hermes does not append or duplicate the message. Return a non-zero exit on source or generation failure so the scheduler records the failure. Load the delivery plugin in the owning profile and restart the gateway only after stating the brief interruption and receiving permission. If gateway multiplexing is enabled, restart the serving `default` gateway (`hermes -p default gateway restart`), not a satellite profile, because starting the latter can create a second Telegram poller and bind conflict.
6. **Verify timezone semantics and message ownership from saved state.** Read the source and destination scheduler timezone before editing, then convert the expression to preserve the effective local execution time; do not copy a UTC cron string into a local-time scheduler blindly. The user's preferred timezone is `America/Sao_Paulo`; a scheduler using local time stores `0 9 * * *` for 09:00 BRT, while a UTC scheduler stores `0 12 * * *`. For direct-delivery scripts, update the job prompt to say the script owns the final Telegram message and must not re-send stdout or append scheduler context. Re-read `schedule`, `enabled/state`, `no_agent`, `script`, `deliver`, and `next_run_at` after creation.
7. **Validate without creating noise.** Execute the destination wrapper against the live source, run a non-delivering alert check, compile/lint the implementation, and run `hermes -p <owner> cron doctor`. For generated dashboards or reports, inspect the actual JSON/HTML schema before asserting counts, then verify expected record cardinality, required visual/data markers, and JavaScript syntax; a zero caused by querying the wrong field is not an empty result. Do not manually run a Telegram-delivering job unless the operator explicitly authorizes an immediate test.
8. **Close the loop.** Update the canonical workflow page, `wiki/index.md`, and `wiki/log.md`; record the new owner, old paused job, rollback command, delivery target, and verification evidence without secrets. Read the old profile back after enabling the new profile to prove only one owner remains active.

## Rollback

For a failed handoff, pause the new job first, resume the preserved old job, verify both profiles' saved state, and leave the source collector unchanged until the failure is understood. Never delete the old job as part of routine migration.

## Communication

Use Telegram for operational reports and material alerts. Keep user-facing output free of cron IDs, job names, script paths, internal footers, debug traces, and secret-derived values. Periodic status remains limited to morning, afternoon, and evening unless a material change requires earlier notification.

## References

- `references/home-assistant-reports.md` — reusable Home Assistant battery/energy report rules, entity filtering, scheduler handoff, and delivery verification.
- For any non-Home-Assistant report, reuse the same procedure and shared delivery helper; do not create a report-specific formatting or feedback path.
- `hermes-cron-operations` — generic Hermes scheduler diagnosis and safe recovery; this skill adds Tiberius's homelab ownership and profile-boundary procedure.
- `infrastructure-state-curation` — durable live-state reconciliation and canonical documentation updates.
