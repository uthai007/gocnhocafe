#!/usr/bin/env python3
"""Fetch NEA hourly readings from data.gov.sg and build data/daily.json (daily min / max per region).

    python3 tools/fetch-nea.py 2026-09-15 2026-10-18

Sources (NEA via data.gov.sg, open API, no key):
  24-hr PSI     https://api-open.data.gov.sg/v2/real-time/api/psi?date=YYYY-MM-DD   readings.psi_twenty_four_hourly
  1-hr PM2.5    https://api-open.data.gov.sg/v2/real-time/api/pm25?date=YYYY-MM-DD  readings.pm25_one_hourly
  (v1 fallback  https://api.data.gov.sg/v1/environment/{psi,pm25}?date=YYYY-MM-DD)
Every raw response is kept under data/raw/ so each number in the video traces back to an NEA reading.
A day's min / max are taken over that day's hourly readings (SGT). The last day is marked partial when it has < 24 hours.
"""
import datetime as dt
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
REGIONS = ["north", "south", "east", "west", "central"]
METRICS = {"psi": "psi_twenty_four_hourly", "pm25": "pm25_one_hourly"}


def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "hyperframes-aq/1.0"}), timeout=60) as r:
                return json.load(r)
        except Exception as e:  # network hiccup or rate limit: back off and retry
            if attempt == 3:
                raise
            print(f"  retry {url}: {e}", file=sys.stderr)
            time.sleep(2 ** (attempt + 1))


def fetch_items(metric, day):
    """All hourly items for one metric and one date, following pagination; v1 fallback."""
    cache = RAW / f"{metric}-{day}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    items, token = [], None
    try:
        while True:
            q = {"date": day} | ({"paginationToken": token} if token else {})
            body = get(f"https://api-open.data.gov.sg/v2/real-time/api/{metric}?" + urllib.parse.urlencode(q))
            data = body.get("data", {})
            items += data.get("items", [])
            token = data.get("paginationToken")
            if not token:
                break
    except Exception as e:
        print(f"  v2 failed for {metric} {day} ({e}); trying v1", file=sys.stderr)
        items = get(f"https://api.data.gov.sg/v1/environment/{metric}?date={day}").get("items", [])
    cache.write_text(json.dumps(items))
    return items


def main():
    start, end = (dt.date.fromisoformat(a) for a in sys.argv[1:3])
    RAW.mkdir(parents=True, exist_ok=True)
    days, out = [], {m: {r: {"min": [], "max": [], "hours": []} for r in REGIONS} for m in METRICS}
    hours_per_day, last_ts = [], None
    d = start
    while d <= end:
        day = d.isoformat()
        per = {m: {r: [] for r in REGIONS} for m in METRICS}
        stamps = set()
        for m, key in METRICS.items():
            for it in fetch_items(m, day):
                ts = it.get("timestamp", "")
                if not ts.startswith(day):
                    continue
                vals = it.get("readings", {}).get(key, {})
                for r in REGIONS:
                    if isinstance(vals.get(r), (int, float)):
                        per[m][r].append(vals[r])
                stamps.add(ts[:13])
                last_ts = max(last_ts or ts, ts)
        if all(per[m][r] for m in METRICS for r in REGIONS):
            days.append(day)
            hours_per_day.append(len(stamps))
            for m in METRICS:
                for r in REGIONS:
                    v = per[m][r]
                    out[m][r]["min"].append(min(v))
                    out[m][r]["max"].append(max(v))
                    out[m][r]["hours"].append(len(v))
            print(day, " ".join(f"{r[0].upper()} psi {out['psi'][r]['min'][-1]}-{out['psi'][r]['max'][-1]} pm {out['pm25'][r]['min'][-1]}-{out['pm25'][r]['max'][-1]}" for r in REGIONS))
        else:
            print(day, "no complete data — skipped")
        d += dt.timedelta(days=1)
    result = {
        "source": "NEA via data.gov.sg (24-hr PSI, 1-hr PM2.5), hourly readings",
        "days": days,
        "hours": hours_per_day,
        "last_reading": last_ts,
        "partial_last_day": bool(hours_per_day) and hours_per_day[-1] < 24,
        "psi": {r: {k: out["psi"][r][k] for k in ("min", "max")} for r in REGIONS},
        "pm25": {r: {k: out["pm25"][r][k] for k in ("min", "max")} for r in REGIONS},
    }
    (ROOT / "data/daily.json").write_text(json.dumps(result, indent=1))
    print(f"wrote data/daily.json: {len(days)} days, last reading {last_ts}")


if __name__ == "__main__":
    main()
