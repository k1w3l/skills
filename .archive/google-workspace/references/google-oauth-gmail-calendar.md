# Google OAuth for Gmail + Calendar automation

This reference captures a compact, reusable pattern for authorizing Gmail/Calendar automation when the standard `google-workspace` setup path needs narrower scopes or the installed setup script does not support `--services`.

## Minimal and broad scope sets

Minimal monitoring + event creation:

```python
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]
```

Broader Gmail + Calendar access when explicitly approved by the user:

```python
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]
```

## Generate a fresh auth URL manually

Use the Hermes venv Python for installed Google dependencies:

```bash
/home/kiwel/.hermes/hermes-agent/venv/bin/python - <<'PY'
import json
from pathlib import Path
from google_auth_oauthlib.flow import Flow

H = Path('/home/kiwel/.hermes')
CLIENT = H / 'google_client_secret.json'
PENDING = H / 'google_oauth_pending.json'
LAST = H / 'google_oauth_last_url.txt'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
]

flow = Flow.from_client_secrets_file(
    str(CLIENT),
    scopes=SCOPES,
    redirect_uri='http://localhost:1',
    autogenerate_code_verifier=True,
)
url, state = flow.authorization_url(
    access_type='offline',
    prompt='consent',
    include_granted_scopes='true',
)
PENDING.write_text(json.dumps({
    'state': state,
    'code_verifier': flow.code_verifier,
    'redirect_uri': 'http://localhost:1',
    'scopes': SCOPES,
}, indent=2))
LAST.write_text(url)
print(url)
PY
```

Ask the user to open the URL and paste the entire redirect URL that starts with `http://localhost:1/` and contains `code=`.

## Exchange the redirect URL

```bash
/home/kiwel/.hermes/hermes-agent/venv/bin/python \
  /home/kiwel/.hermes/skills/productivity/google-workspace/scripts/setup.py \
  --auth-code '<full http://localhost:1 redirect URL>'
```

Then verify Gmail with:

```bash
/home/kiwel/.hermes/hermes-agent/venv/bin/python \
  /home/kiwel/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  gmail search 'newer_than:1d' --max 3
```

## Calendar verification note

If only `calendar.events` was granted, a check that calls `calendarList.list` can return 403 `insufficientPermissions`. This does not mean OAuth failed; it means the check used a broader Calendar endpoint than the granted scope allows. Verify by creating/listing events through an endpoint covered by the granted scope, or request full `https://www.googleapis.com/auth/calendar` when the user approves broader access.

## Google testing-mode errors

If Google says the app is still being tested and only developer-approved testers can use it, the fix is in Google Cloud Console:

1. Open OAuth consent/Audience.
2. Add the user's Google account under Test users.
3. Save.
4. Generate a new auth URL; old URLs may still fail.

If the redirect lands on `accounts.google.com/info/unknownerror` and lacks `code=`, do not run token exchange. Generate a fresh URL after checking consent-screen completeness, test-user status, and scopes.
