# Bichon tag automation and cron validation

Use this reference when implementing or repairing Bichon classification routines that mutate tags or run under Hermes Cron.

## Core rule

A classifier producing plausible matches is not evidence that Bichon was changed. Verify the mutation by querying the same messages again and confirming the expected tags are present.

Likewise, Hermes Cron reporting `last_status=ok` is not enough when the script catches exceptions and exits zero. Inspect the script's structured report and verify the remote state.

## Tight verification loop

1. Verify authentication and discover accounts/mailboxes through the API.
2. Run classification in dry-run mode and record aggregate counts only.
3. Before a bulk mutation, test the tag endpoint on one reversible message or the smallest safe batch.
4. Re-query that exact message and confirm the expected tag is returned by `list-messages` or `message-content`.
5. Only then run the bulk operation.
6. Re-query aggregate counts and confirm that tagged/classified counts increased as expected.
7. Inspect the routine's persisted report for `failures`, not only its process exit status.
8. For cron jobs, manually trigger one run and then confirm `last_run_at`, `last_status`, delivery errors, and the remote Bichon result.

## Facet/tag contract pitfall

A `POST /api/v1/update-tags` request using arbitrary textual names can return HTTP 400 with `FacetParseError`, for example when sent a value such as `classificado`. Treat this as evidence that the endpoint contract or tag lifecycle has not been established—not as a reason to retry the same bulk payload.

Investigate the current Bichon frontend/API contract to determine whether tags must:

- already exist as facets;
- be sent as IDs or another structured representation;
- be created through a separate endpoint first; or
- use a different payload shape.

Confirm the contract with a single-message round trip before bulk tagging. Frontend bundle inspection is an acceptable discovery method when OpenAPI paths serve the SPA rather than JSON.

## Cron and error semantics

For `no_agent=true` watchdogs:

- empty stdout on success/no findings keeps delivery silent;
- actionable findings should be printed as the complete Telegram message;
- operational failures should print a concise diagnostic and return non-zero so the scheduler cannot record a false success;
- do not swallow an exception and return zero merely to make the alert deliver.

When migrating routines from Gmail/Google API to Bichon:

- update job names and prompts so they describe Bichon rather than Gmail;
- verify paused jobs are explicitly resumed;
- check that schedules match their descriptions;
- preserve deduplication state deliberately;
- use dry-run during diagnosis because it should not mark messages as seen;
- after the first real run, confirm alerts were delivered and subsequent runs remain silent for already-seen messages.

## Security

Never log or persist API keys. Reports may contain message metadata, so keep diagnostic output concise and avoid copying subjects, bodies, or sender data into durable skills unless essential and explicitly sanitized.
