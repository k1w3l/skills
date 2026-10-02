# Home Assistant battery sensor monitoring

Use this reference when Sr. Kiwel asks for scheduled monitoring of battery-powered Home Assistant entities.

## Scope

- Match entities whose `entity_id` or `attributes.friendly_name` contains Portuguese or English battery terms: `bateria`, `battery`.
- Prefer entities with numeric percent-like state values. Accept `device_class: battery`, `unit_of_measurement: %`, or a numeric state with a battery term in the name.
- Ignore states that are unavailable, unknown, empty, non-numeric, or not a percentage.

## Suggested alert/report shape

- Low-battery alert threshold: `<= 5%` when requested by Sr. Kiwel.
- Daily report: sort sensors by battery ascending, show friendly name, entity_id, percent, and last_updated.
- Deliver scheduled notifications to Telegram by default for Sr. Kiwel.
- For alert jobs, suppress output when nothing is low so no-agent cron remains silent.
- Use state/cooldown files under `~/.hermes/state/` to avoid duplicate low-battery alerts; daily reports can always print.

## Credential handling for scheduled jobs

Scheduled scripts need credentials available without chat context. Use environment variables such as:

- `HASS_URL`, defaulting to `http://192.168.1.47:8123` for Sr. Kiwel's local Home Assistant.
- `HASS_TOKEN`, a Home Assistant Long-Lived Access Token.

Do not store tokens in memory, skills, or final replies. If a persistent scheduled job needs a token and it is not already configured, ask for explicit permission to write it to a local secure environment/config file before creating the cron job.

## REST query pattern

Fetch all states:

```python
import json, os, urllib.request
base = os.getenv('HASS_URL', 'http://192.168.1.47:8123').rstrip('/')
token = os.environ['HASS_TOKEN']
req = urllib.request.Request(
    base + '/api/states',
    headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
)
with urllib.request.urlopen(req, timeout=20) as r:
    states = json.load(r)
```

Filter example:

```python
def parse_percent(value):
    try:
        pct = float(str(value).replace(',', '.'))
    except ValueError:
        return None
    return pct if 0 <= pct <= 100 else None

matches = []
for s in states:
    attrs = s.get('attributes') or {}
    eid = s.get('entity_id', '')
    name = attrs.get('friendly_name', '') or eid
    hay = f'{eid} {name}'.lower()
    pct = parse_percent(s.get('state'))
    if pct is None:
        continue
    if 'bateria' in hay or 'battery' in hay or attrs.get('device_class') == 'battery':
        matches.append((pct, name, eid, s.get('last_updated')))
```
