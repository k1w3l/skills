# Whole-scheduler audit and Stalwart agenda verification

Use this reference when the operator asks to validate all Hermes routines, especially the Stalwart-backed agenda and event-email path, without causing side effects.

## Safe audit sequence

1. Run read-only calendar checks and summarize counts/errors:
   - `python3 ~/.hermes/scripts/calendar_ssh.py health`
   - `python3 ~/.hermes/scripts/calendar_ssh.py today`
   - `python3 ~/.hermes/scripts/calendar_ssh.py week`
2. Verify the separate Stalwart mail path through SSH:
   - `mailctl.py health`.
   - `mailctl.py mailboxes`; confirm `Importados` and `Importados/Gmail/INBOX`.
3. Inventory `hermes cron list --all` and `hermes cron status`. Match jobs by name/script, not guessed IDs.
4. Read the newest saved output under `~/.hermes/cron/output/<job-id>/` for every relevant job. Empty output or `[SILENT]` is normal only after confirming the job status and collector/tool result are successful.
5. Do not manually run alert/card/event jobs during a broad audit: they may send Telegram, consume deduplication state, or mutate remote data.
6. Exercise shared Stalwart routines with bounded dry-runs only:
   ```bash
   python3 ~/.hermes/scripts/stalwart_email_routines.py finance --dry-run --limit 1
   python3 ~/.hermes/scripts/stalwart_email_routines.py events --dry-run --limit 1
   python3 ~/.hermes/scripts/stalwart_email_routines.py important --dry-run --limit 1
   python3 ~/.hermes/scripts/stalwart_email_routines.py organize --dry-run --limit 1
   ```
   Require return code zero; `organize` must report `dry_run: true`, `total_modified: 0`, and no failures.
7. Validate Telegram transport with a non-destructive bot `getMe`; never send a fabricated test event or expose its token.

## Event-email approval invariants

- `jarvis_email_events_watch.py` → `stalwart_email_routines.py events` reads Stalwart/JMAP only.
- An explicit date and time creates a persistent `calendar_approvals` request and Telegram buttons.
- The cron pass never calls calendar `create`; only the authorized `ca:y:<id>` callback may call `calendar_ssh.py create`.
- `ca:n:<id>`, no response, Telegram failure, conflict, or incomplete time leave the calendar unchanged.
- Never default a missing event time to 09:00 or any other invented value.
- Keep the Google mirror and unrelated Google token watchdog paused unless OAuth is explicitly completed.

## Classification

Report separately:

- current active-job failures;
- expected silence/no-match runs;
- historical errors on intentionally paused Google jobs;
- historical Telegram/network warnings versus a current `getMe` failure.
