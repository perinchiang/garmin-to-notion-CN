"""Import Garmin activities and daily health facts into Agent Signals.

The legacy Garmin databases are intentionally not touched here. This exporter
keeps one stable signal per activity/record/day and omits raw telemetry.
"""

from __future__ import annotations

import json
import os
import time
from datetime import date
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from garminconnect import Garmin


NOTION_VERSION = "2026-03-11"
DATA_SOURCE_ID = os.environ["NOTION_AGENT_SIGNALS_DATA_SOURCE_ID"]
TOKEN = os.environ["NOTION_AGENT_SIGNALS_TOKEN"]


def notion(method: str, path: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        "https://api.notion.com/v1" + path,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    for attempt in range(4):
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode())
        except HTTPError as exc:
            if exc.code == 429 and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"Notion API failed ({exc.code})") from exc
    raise AssertionError("unreachable")


def existing_ids() -> set[str]:
    known: set[str] = set()
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        result = notion("POST", f"/data_sources/{DATA_SOURCE_ID}/query", body)
        for page in result.get("results", []):
            parts = page.get("properties", {}).get("External ID", {}).get("rich_text", [])
            value = "".join(part.get("plain_text", "") for part in parts)
            if value:
                known.add(value)
        if not result.get("has_more"):
            return known
        cursor = result.get("next_cursor")


def signal(name: str, external_id: str, signal_type: str, observed_on: str, evidence: str, url: str = "") -> dict:
    properties = {
        "Name": {"title": [{"type": "text", "text": {"content": name[:180]}}]},
        "Source": {"select": {"name": "Garmin"}},
        "Domain": {"multi_select": [{"name": "health"}]},
        "Signal type": {"select": {"name": signal_type}},
        "External ID": {"rich_text": [{"type": "text", "text": {"content": external_id}}]},
        "Evidence": {"rich_text": [{"type": "text", "text": {"content": evidence[:1800]}}]},
        "Status": {"select": {"name": "new"}},
        "Confidence": {"select": {"name": "direct"}},
    }
    if observed_on:
        properties["Observed on"] = {"date": {"start": observed_on[:10]}}
    if url:
        properties["Source URL"] = {"url": url}
    return properties


def collect(garmin: Garmin) -> list[tuple[str, dict]]:
    rows: list[tuple[str, dict]] = []
    for activity in garmin.get_activities(0, 1000):
        activity_id = activity.get("activityId")
        if not activity_id:
            continue
        activity_name = activity.get("activityName") or "Unnamed activity"
        activity_type = (activity.get("activityType") or {}).get("typeKey", "unknown")
        distance = float(activity.get("distance") or 0) / 1000
        duration = float(activity.get("duration") or 0) / 60
        calories = round(float(activity.get("calories") or 0))
        observed = activity.get("startTimeGMT", "")
        evidence = f"Garmin activity; type={activity_type}; distance={distance:.2f} km; duration={duration:.1f} min; calories={calories}."
        rows.append((f"garmin-activity:{activity_id}", signal(activity_name, f"garmin-activity:{activity_id}", "activity", observed, evidence, f"https://connect.garmin.cn/modern/activity/{activity_id}")))

    today = date.today().isoformat()
    daily_steps = garmin.get_daily_steps(today, today)
    if daily_steps:
        steps = daily_steps[0]
        rows.append((f"garmin-steps:{today}", signal(
            f"Garmin steps {today}", f"garmin-steps:{today}", "activity", today,
            f"Garmin daily steps; total={steps.get('totalSteps', 0)}; distance={float(steps.get('totalDistance') or 0) / 1000:.2f} km.",
        )))

    sleep = garmin.get_sleep_data(today) or {}
    dto = sleep.get("dailySleepDTO") or {}
    sleep_date = dto.get("calendarDate") or today
    total_sleep = sum(float(dto.get(key) or 0) for key in ("deepSleepSeconds", "lightSleepSeconds", "remSleepSeconds"))
    if dto and total_sleep:
        rows.append((f"garmin-sleep:{sleep_date}", signal(
            f"Garmin sleep {sleep_date}", f"garmin-sleep:{sleep_date}", "activity", sleep_date,
            f"Garmin sleep summary; total={total_sleep / 3600:.1f} h; deep={float(dto.get('deepSleepSeconds') or 0) / 3600:.1f} h; REM={float(dto.get('remSleepSeconds') or 0) / 3600:.1f} h.",
        )))
    return rows


def main() -> None:
    garmin = Garmin(os.environ["GARMIN_EMAIL"], os.environ["GARMIN_PASSWORD"], is_cn=True)
    garmin.login()
    rows = collect(garmin)
    known = existing_ids()
    created = 0
    for external_id, properties in rows:
        if external_id in known:
            continue
        notion("POST", "/pages", {"parent": {"type": "data_source_id", "data_source_id": DATA_SOURCE_ID}, "properties": properties})
        known.add(external_id)
        created += 1
        time.sleep(0.36)
    print(json.dumps({"signals_seen": len(rows), "created": created, "already_present": len(rows) - created}))


if __name__ == "__main__":
    main()
