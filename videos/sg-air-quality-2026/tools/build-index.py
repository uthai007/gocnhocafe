#!/usr/bin/env python3
"""Write index.html from tools/template.html.  usage: build-index.py land|port OUT_DIR [DATA_JSON]
DATA_JSON defaults to data/daily.json (built by tools/fetch-nea.py from NEA readings)."""
import json, sys, pathlib
orient, out = sys.argv[1], pathlib.Path(sys.argv[2])
root = pathlib.Path(__file__).resolve().parent.parent
data = json.load(open(sys.argv[3] if len(sys.argv) > 3 else root / "data/daily.json"))
mp = json.load(open(root / "data/map.json"))
w, h = (1920, 1080) if orient == "land" else (1080, 1920)
PER_DAY = 1.3
n = len(data["days"])
dur = round(4.0 + (n - 1) * PER_DAY + 5.0, 2)
M = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
fmt = lambda d: f"{int(d[8:])} {M[int(d[5:7]) - 1]} {d[:4]}"
last = data.get("last_reading") or ""
rng = f"{fmt(data['days'][0])} – {fmt(data['days'][-1])}"
src = ("Source: National Environment Agency (NEA) via data.gov.sg, hourly regional readings. Each bar spans the lowest to highest "
       "hourly reading of the day (SGT).")
if data.get("partial_last_day"):
    src += f" Last day is partial (to {last[11:16]} SGT)."
s = (root / "tools/template.html").read_text()
for k, v in {"__W__": w, "__H__": h, "__ORIENT__": orient, "__DUR__": dur, "__PER_DAY__": PER_DAY,
             "__SOURCE__": src, "__RANGE__": rng, "__MAP__": json.dumps(mp),
             "__DATA__": json.dumps({k: data[k] for k in ("days", "partial_last_day", "psi", "pm25")})}.items():
    s = s.replace(k, str(v))
(out / "index.html").write_text(s)
print("wrote", out / "index.html", f"{w}x{h}", f"{dur}s", n, "days")
