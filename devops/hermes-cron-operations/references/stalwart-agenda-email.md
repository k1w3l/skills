# Stalwart-backed agenda and event-email jobs

Use this reference when auditing or enabling Hermes jobs that read event emails and/or operate the calendar. It records the durable workflow, not a one-off run result.

## Source and transport

- Calendar source of truth: Stalwart `calctl` on the mail LXC.
- Hermes calendar bridge: `python3 ~/.hermes/scripts/calendar_ssh.py <args>`.
- Remote calendar target: `mailagent@192.168.1.13:/home/mailagent/mail-agent/calctl.py`.
- Mail source for event-email automation: Stalwart/JMAP through the `mailagent` SSH bridge. Never substitute Gmail or Google Calendar as the origin.

## Audit sequence

1. Check the calendar path first:

   ```bash
   python3 ~/.hermes/scripts/calendar_ssh.py health
   ```

2. Check the mail path separately, without exposing credentials or message bodies:

   ```bash
   ssh -o BatchMode=yes -o ConnectTimeout=8 mailagent@192.168.1.13 \
     'python3 /home/mailagent/mail-agent/mailctl.py health'
   ssh -o BatchMode=yes -o ConnectTimeout=8 mailagent@192.168.1.13 \
     'python3 /home/mailagent/mail-agent/mailctl.py mailboxes'
   ```

   A calendar `health` result alone does not prove that the email-triggered routine can read Stalwart mail.

3. Inventory both enabled and disabled jobs:

   ```bash
   hermes cron list --all
   hermes cron status
   ```

   Match by job name and script, never by an assumed ID. Record state, script, delivery target, schedule, and last status.

## Recognizing the email-to-event routine

The event-creation job may be named as an event alert rather than “calendar creation”. Inspect the wrapper and follow the chain:

- `jarvis_email_events_watch.py` delegates to `stalwart_email_routines.py events`.
- The routine reads recent messages through the Stalwart bridge.
- For a recognized date/time it calls `calendar_ssh.py create`, so the event is written to Stalwart.
- The routine prints the calendar result (`created`, `duplicate`, `conflict`, or failure) in its normal stdout.
- Because this is a `no-agent` cron with `Deliver: telegram`, stdout is the Telegram confirmation channel. Do not replace it with a Google Calendar API call or a second Telegram sender, which can duplicate notices.

A job that is already active and has `Deliver: telegram` needs no duplicate cron. Activate only a genuinely paused Stalwart job.

## Safe activation and validation

- Resume a paused Stalwart job only after its source and delivery have been verified.
- Keep a Google calendar mirror paused until the operator explicitly completes OAuth; it is an optional one-way Stalwart → Google sink, never a briefing, reminder, or event-creation source.
- Keep unrelated Google Workspace token watchdogs unchanged.
- Do not manually fire an alert/event job merely to validate activation: it may send Telegram messages and create real events. Use a bounded dry-run when the script supports it:

  ```bash
  python3 ~/.hermes/scripts/stalwart_email_routines.py events --dry-run --limit 1
  ```

- A dry-run must report success with zero mutations. For an immediate live run, require explicit operator authorization and verify the fresh `last_status` afterward.
- After any resume, re-run `hermes cron list --all` and confirm the job is enabled, the delivery target remains Telegram, and the last run is not an old historical error. Do not claim that a Telegram message was delivered unless the cron/tool output proves it; a successful scheduled execution only proves the job completed.

## Conflict and provenance rules

- All create/update/delete/freebusy/week/today actions go through `calendar_ssh.py` and therefore Stalwart `calctl`.
- Never invent an event from incomplete email data. If `calctl` returns `conflict`, preserve the returned busy information and ask for another time rather than overwriting or silently choosing a slot.
- Report the exact source path and the state of the Google mirror separately so an old mirror error is not confused with a Stalwart calendar failure.
