# Google Workspace OAuth token lifecycle and refresh watchdog

Use this reference when Gmail/Calendar OAuth tokens expire, refresh fails, or the user wants proactive renewal/alerts.

## Durable facts

- Google OAuth access tokens are intentionally short-lived, commonly about 1 hour. Do not promise or attempt to request a long-lived access token.
- The durable credential is the refresh token. Automation should periodically use the refresh token to obtain a fresh access token.
- A refresh token can still be revoked or expire, especially if the OAuth consent app is in Testing mode, access is revoked in the Google account, credentials are rotated, password/security changes affect Gmail scopes, or too many refresh tokens are minted for the same user/client.
- If the Google Cloud OAuth consent app is in Testing, move it to Production to reduce recurring reauthorization; a watchdog cannot prevent Testing-mode refresh-token expiry.

## Watchdog pattern

Create a script under `~/.hermes/scripts/` that:

1. Loads `~/.hermes/google_token.json` with `google.oauth2.credentials.Credentials.from_authorized_user_file`.
2. Verifies a `refresh_token` exists.
3. Calls `creds.refresh(Request())` proactively, rather than waiting for the next Gmail call to notice expiry.
4. Writes `creds.to_json()` back to `~/.hermes/google_token.json`.
5. Logs only non-sensitive metadata such as expiry time.
6. Prints nothing on success, so a `cronjob` with `no_agent=True` stays silent.
7. Prints a short actionable alert on failure, never token contents.

Recommended cron delivery for this user: Telegram, not origin/current chat.

Example scheduling shape:

```python
cronjob(
  action="create",
  name="Renovação automática do token Google Workspace",
  schedule="every 45m",
  script="google_token_refresh_watchdog.py",
  no_agent=True,
  deliver="telegram",
)
```

If updating an existing token watchdog job, set `deliver="telegram"` so alerts are not trapped in the active conversation.

## Dependency workaround

If system Python lacks Google dependencies or `pip`, prefer an isolated venv for these scripts rather than altering the system Python environment. On Ubuntu/Debian, install venv support only with user approval when apt changes are required:

```bash
sudo apt-get install -y python3.12-venv
python3 -m venv ~/.hermes/google-workspace-venv
~/.hermes/google-workspace-venv/bin/python -m pip install --upgrade pip
~/.hermes/google-workspace-venv/bin/python -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

Then run Google Workspace scripts with the venv Python:

```bash
~/.hermes/google-workspace-venv/bin/python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
~/.hermes/google-workspace-venv/bin/python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py gmail search "newer_than:7d" --max 1
```

This captures the fix, not the transient failure: the goal is a stable isolated runtime for Google Workspace automation.
