#!/usr/bin/env python3
"""Build data/monthly.json: estimated monthly AI-tool website visits, Jan 2024 - Jun 2026, ASEAN-6.

Anchors (AITools.xyz, estimates compiled from SEMrush + Ahrefs; website visits, not unique users, no app sessions):
  2025 totals  - aitools.xyz/ai-visits-by-country/2025 (also Visual Capitalist / BusinessToday, Sep 2026)
  2024 totals  - ID, PH from aitools.xyz/statistics/2024; VN, TH, MY, SG = 2025 total minus the YoY gain on the 2025 page
  Jun 2026     - monthly figures for ID, PH, VN, TH reported by The Nation Thailand (from AITools.xyz)
                 MY, SG Jun 2026 not published: estimated as 2025 monthly average x median Jun-26/2025 ratio of the others
No public month-by-month country series exists, so months are interpolated: the smoothest curve
(minimum squared 2nd difference) whose 2024 and 2025 sums equal the annual totals and that lands on Jun 2026.
"""
import json
import numpy as np

A24 = {"ID": 2.56e9, "PH": 2.57e9, "VN": 2.67e9 - 1.12e9, "TH": 1.50e9 - 519.61e6,
       "MY": 1.35e9 - 408.25e6, "SG": 903.96e6 - 291.88e6}
A25 = {"ID": 3.66e9, "PH": 2.93e9, "VN": 2.67e9, "TH": 1.50e9, "MY": 1.35e9, "SG": 903.96e6}
J26 = {"ID": 314.34e6, "PH": 243.82e6, "VN": 154.68e6, "TH": 130.56e6}
ratio = float(np.median([J26[c] / (A25[c] / 12) for c in ["ID", "PH", "TH"]]))
for c in ["MY", "SG"]:
    J26[c] = A25[c] / 12 * ratio

N = 30  # Jan 2024 .. Jun 2026
D = np.diff(np.eye(N), 2, axis=0)
H = 2 * D.T @ D
C = np.zeros((3, N)); C[0, :12] = 1; C[1, 12:24] = 1; C[2, 29] = 1
months = [f"{y}-{m:02d}" for y in (2024, 2025, 2026) for m in range(1, 13)][:N]
out = {"months": months, "unit": "visits (millions)", "series": {}, "jun2026_estimated": ["MY", "SG"]}
for c in A24:
    b = np.array([A24[c], A25[c], J26[c]])
    K = np.block([[H, C.T], [C, np.zeros((3, 3))]])
    x = np.linalg.solve(K, np.concatenate([np.zeros(N), b]))[:N]
    assert x.min() > 0, c
    out["series"][c] = [round(v / 1e6, 1) for v in x]
    print(c, " ".join(f"{v/1e6:5.0f}" for v in x))
json.dump(out, open("data/monthly.json", "w"), indent=1)
