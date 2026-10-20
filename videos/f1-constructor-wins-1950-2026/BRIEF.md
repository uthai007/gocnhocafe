---
workflow: general-video
flow: automation
storyboard: yes
message: "Ferrari has topped F1's all-time wins table since 1953 — and only twice has anyone taken it away."
destination: youtube
aspect: "16:9"
format: 1920x1080
language: en-US
audience: "F1 fans and casual viewers who enjoy data races"
length: "~2–3 min"
---

## Intent
"F1 constructors ranked by cumulative wins, 1950 → 2026. YouTube 16:9 (1920×1080), about 2–3 minutes. You review a
storyboard before the full build, then the workflow builds it from start to finish."

## Data
- F1DB (github.com/f1db/f1db, CC BY 4.0), commit e2147b8 (19 Oct 2026): 1,166 World Championship races,
  13 May 1950 – 11 Oct 2026 (2026 Singapore GP, round 17 of 23). tools/build-data.py → data/wins.json.
- A shared drive counts once for the constructor. Indianapolis 500 (1950–60) counts, as in F1DB.

## Customizations
- Bar race with team colours and on-screen callouts at the real turning points; slow-downs at lead changes.
- Music only (no voiceover) unless the plan review asks for one.
