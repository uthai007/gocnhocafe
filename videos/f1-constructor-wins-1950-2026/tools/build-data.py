#!/usr/bin/env python3
"""Build data/wins.json from an F1DB checkout: every World Championship race, its winning constructor(s), cumulative tallies.

    python3 tools/build-data.py <path-to-f1db>     (git clone --depth 1 --filter=blob:none --sparse https://github.com/f1db/f1db;
                                                     git sparse-checkout set src/data/seasons src/data/constructors)
Source: F1DB (CC BY 4.0), src/data/seasons/<year>/races/<NN-gp>/race-results.yml. A race counts once per constructor
even when a win was shared between two drivers of the same car (1950s). Indianapolis 500 (1950-1960) is included,
as it was a World Championship round and F1DB counts it.
"""
import json, pathlib, sys, yaml

src = pathlib.Path(sys.argv[1]) / "src/data"
names = {}
for f in (src / "constructors").glob("*.yml"):
    c = yaml.safe_load(f.read_text())
    names[c["id"]] = {"name": c.get("name"), "full": c.get("fullName"), "country": c.get("countryId")}
races = []
for ydir in sorted((src / "seasons").iterdir()):
    if not ydir.name.isdigit():
        continue
    for rdir in sorted((ydir / "races").iterdir()):
        res = rdir / "race-results.yml"
        if not res.exists():
            continue
        meta = yaml.safe_load((rdir / "race.yml").read_text())
        rows = yaml.safe_load(res.read_text()) or []
        winners = sorted({r["constructorId"] for r in rows if str(r.get("position")) == "1"})
        if not winners:
            continue
        races.append({"year": int(ydir.name), "round": meta["round"], "date": str(meta["date"]), "gp": meta["grandPrixId"],
                      "name": meta.get("officialName"), "winners": winners,
                      "drivers": sorted({r["driverId"] for r in rows if str(r.get("position")) == "1"})})
races.sort(key=lambda r: r["date"])
tot = {}
for r in races:
    for c in r["winners"]:
        tot[c] = tot.get(c, 0) + 1
used = sorted(tot, key=lambda c: -tot[c])
out = {"source": "F1DB (github.com/f1db/f1db, CC BY 4.0)", "races": races,
       "constructors": {c: names.get(c, {"name": c}) | {"wins": tot[c]} for c in used}}
pathlib.Path("data/wins.json").write_text(json.dumps(out, indent=1))
print(len(races), "races,", races[0]["date"], "->", races[-1]["date"], races[-1]["gp"])
for c in used[:20]:
    print(f"{tot[c]:4d} {c:20s} {names.get(c, {}).get('name')}")
