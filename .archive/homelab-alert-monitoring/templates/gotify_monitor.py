#!/usr/bin/env python3
"""Gotify live alert monitor template.

Set environment variables rather than hard-coding secrets:
  GOTIFY_BASE=http://host:port
  GOTIFY_USER=username              # only needed to refresh application names
  GOTIFY_PASSWORD=***          # optional; avoid unless needed
  GOTIFY_TOKEN_FILE=/path/...oken
  GOTIFY_APP_MAP_FILE=/path/to/app-map.json
  MONITOR_SECONDS=3600
  POLL_SECONDS=10
  OUT_JSONL=/path/to/alarms.jsonl
"""

import base64
import collections
import datetime as dt
import json
import os
import re
import time
import urllib.parse
import urllib.request

BASE = os.environ.get("GOTIFY_BASE", "http://127.0.0.1").rstrip("/")
USER = os.environ.get("GOTIFY_USER", "")
PASSWORD = os.environ.get("GOTIFY_PASSWORD", "")
TOKEN_FILE = os.environ.get("GOTIFY_TOKEN_FILE", "./gotify_client_token")
APP_MAP_FILE = os.environ.get("GOTIFY_APP_MAP_FILE", "./gotify_apps.json")
DURATION = int(os.environ.get("MONITOR_SECONDS", "3600"))
POLL = int(os.environ.get("POLL_SECONDS", "10"))
OUT = os.environ.get("OUT_JSONL", "./gotify_alarms.jsonl")


def local_now():
    return dt.datetime.now().astimezone()


def basic_header():
    raw = f"{USER}:{PASSWORD}".encode()
    return {"Authorization": "Basic " + base64.b64encode(raw).decode()}


def get_json(path, headers=None, timeout=10):
    req = urllib.request.Request(BASE + path, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def classify(title, message):
    text = f"{title} {message}".lower()
    if any(w in text for w in ["down", "offline", "unreachable", "timeout", "failed", "failure", "error", "critical", "alert"]):
        return "falha/indisponibilidade"
    if any(w in text for w in ["up", "online", "resolved", "recovered", "success", "ok"]):
        return "recuperação/normalização"
    if any(w in text for w in ["backup", "pbs", "prune", "garbage", "gc"]):
        return "backup/manutenção"
    if any(w in text for w in ["update", "upgrade", "change detected", "changedetection"]):
        return "mudança/atualização"
    if any(w in text for w in ["disk", "zfs", "pool", "smart", "memory", "cpu", "temperature", "temp"]):
        return "recurso/infraestrutura"
    return "outros"


def short(value, n=110):
    value = re.sub(r"\s+", " ", value or "").strip()
    return value if len(value) <= n else value[: n - 1] + "…"


def load_apps():
    if os.path.exists(APP_MAP_FILE):
        with open(APP_MAP_FILE, encoding="utf-8") as f:
            return {int(k): v for k, v in json.load(f).items()}
    if USER and PASSWORD:
        return {a.get("id"): a.get("name", f"app-{a.get('id')}") for a in get_json("/application", basic_header())}
    return {}


def main():
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    with open(TOKEN_FILE, encoding="utf-8") as f:
        token = f.read().strip()
    headers = {"X-Gotify-Key": token}
    apps = load_apps()
    since = 0
    captured = []
    start = local_now()
    stop_at = time.time() + DURATION

    print(f"Monitoring Gotify at {BASE} from {start:%Y-%m-%d %H:%M:%S %Z} for {DURATION}s", flush=True)
    while time.time() < stop_at:
        try:
            query = urllib.parse.urlencode({"limit": 200, "since": since})
            data = get_json("/message?" + query, headers=headers)
            for msg in sorted(data.get("messages", []), key=lambda x: x.get("id", 0)):
                mid = int(msg.get("id") or 0)
                if mid <= since:
                    continue
                since = max(since, mid)
                rec = {
                    "id": mid,
                    "date": msg.get("date"),
                    "appid": msg.get("appid"),
                    "app": apps.get(msg.get("appid"), f"app-{msg.get('appid')}"),
                    "priority": msg.get("priority"),
                    "title": msg.get("title") or "",
                    "message": msg.get("message") or "",
                }
                captured.append(rec)
                with open(OUT, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception as exc:
            print(f"Temporary Gotify polling failure: {type(exc).__name__}: {exc}", flush=True)
        time.sleep(POLL)

    print("\nGOTIFY ALERT REPORT")
    print(f"Window: {start:%Y-%m-%d %H:%M:%S %Z} to {local_now():%Y-%m-%d %H:%M:%S %Z}")
    print(f"Total alerts captured: {len(captured)}")
    if not captured:
        print("No new alerts captured. Consider a longer window or review Gotify message retention/history settings.")
        return

    by_app = collections.Counter(r["app"] for r in captured)
    by_category = collections.Counter(classify(r["title"], r["message"]) for r in captured)
    by_priority = collections.Counter(str(r.get("priority")) for r in captured)

    print("\nTop sources:")
    for app, count in by_app.most_common(10):
        print(f"- {app}: {count}")

    print("\nCategories:")
    for category, count in by_category.most_common():
        print(f"- {category}: {count}")

    print("\nPriorities:")
    for priority, count in by_priority.most_common():
        print(f"- priority {priority}: {count}")

    print("\nRecent alerts:")
    for rec in captured[-10:]:
        title_or_message = short(rec["title"] or rec["message"])
        print(f"- [{rec['date']}] {rec['app']} p{rec['priority']} — {title_or_message}")

    print("\nTuning suggestions:")
    top_app, top_count = by_app.most_common(1)[0]
    print(f"- Tune the dominant source first: {top_app} ({top_count}/{len(captured)} alerts).")
    if by_category.get("falha/indisponibilidade") and by_category.get("recuperação/normalização"):
        print("- Failure/recovery pairs may indicate flapping; consider debounce, more retries, or a longer confirmation window.")
    if any((rec.get("priority") or 0) >= 8 for rec in captured):
        print("- Reserve priorities 8–10 for alerts requiring immediate human action.")
    if by_category.get("backup/manutenção"):
        print("- Successful backup/maintenance notices can often be downgraded to informational priority.")


if __name__ == "__main__":
    main()
