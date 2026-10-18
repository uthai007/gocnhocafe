#!/usr/bin/env python3
"""Write index.html from tools/template.html + data/monthly.json.  usage: build-index.py land|port OUT_DIR"""
import json, sys, pathlib
orient, out = sys.argv[1], pathlib.Path(sys.argv[2])
root = pathlib.Path(__file__).resolve().parent.parent
w, h = (1920, 1080) if orient == "land" else (1080, 1920)
data = json.load(open(root / "data/monthly.json"))
s = (root / "tools/template.html").read_text()
s = s.replace("__W__", str(w)).replace("__H__", str(h)).replace("__ORIENT__", orient)
s = s.replace("__DATA__", json.dumps({"months": data["months"], "series": data["series"]}))
(out / "index.html").write_text(s)
print("wrote", out / "index.html", w, "x", h)
