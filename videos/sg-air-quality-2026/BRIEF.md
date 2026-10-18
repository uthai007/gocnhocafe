---
workflow: general-video
flow: automation
storyboard: no
message: "How Singapore's air quality moved, day by day, region by region, since 15 Sep 2026."
destination: youtube (+ youtube-shorts cut in ../sg-air-quality-2026-vertical)
aspect: "16:9"
language: en-US
audience: "Singapore residents and anyone following the 2026 haze"
length: "~52s (34 days at 1.3s/day + intro/outro)"
---

## Intent
"Air quality including PSI and PM racing in Singapore every day since 15 September 2026 until now. Show the map with
5 place" + "Hiển thị chart có số liệu thấp nhất và cao nhất trong ngày" (show each day's lowest and highest readings).
Reference: the NEA / myENV app screen (1-hr PM2.5 boxes on a map of the five regions, 24-hr PSI).

## Data
- NEA via data.gov.sg open API, hourly 24-hr PSI and 1-hr PM2.5 for North / South / East / West / Central.
- tools/fetch-nea.py keeps every raw response in data/raw/ and builds data/daily.json (daily min / max per region, SGT).
- Nothing is rendered until data/daily.json comes from the real API (network access to api-open.data.gov.sg needed).

## Build
    python3 tools/fetch-nea.py 2026-09-15 <today>
    python3 tools/build-index.py land .  &&  python3 tools/build-index.py port ../sg-air-quality-2026-vertical
    python3 tools/make-bgm.py assets/bgm/bed.wav <duration+1>   (copy to the vertical project too)

## Customizations
- Map: Natural Earth 10m coastline (world-atlas) with five region boxes coloured by the day's PSI band.
- Racing: per metric, five rows ranked by the day's high; each bar spans low → high and shows NEA band colours.
- Island-wide daily-high PSI sparkline; callouts computed from the data (first Unhealthy day, peaks, count of days).
- Music only.
