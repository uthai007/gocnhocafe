#!/usr/bin/env python3
"""Pad each narration line with breathing room and estimate word timings (no ASR available offline).

    ~/.venvs/kokoro/bin/python tools/pad-and-time.py            # run from the project root, after audio.mjs

Per voice line: trim/pad to LEAD s of silence before and TAIL s after the speech; find the silent gaps
inside the speech, use the largest ones as phrase boundaries (one per , . ; : ? !), then spread each
phrase's words across its span weighted by length. Writes padded wavs + words into audio_meta.json.
Idempotent: the original Kokoro output is kept as assets/voice/raw/NN.wav.
"""
import json, os, re, shutil
import numpy as np
import soundfile as sf

LEAD, TAIL, HOP = 0.1, 0.4, 0.01
meta = json.load(open("audio_meta.json"))
script = open("SCRIPT.md").read()
lines = {}
for m in re.finditer(r"^## Line (\d+) — .*?\n(?:.*?\n)*?\n    (.+)$", script, re.M):
    lines[int(m.group(1))] = m.group(2).strip()
os.makedirs("assets/voice/raw", exist_ok=True)

for v in meta["voices"]:
    raw = os.path.join("assets/voice/raw", os.path.basename(v["path"]))
    if not os.path.exists(raw):
        shutil.copy(v["path"], raw)
    x, sr = sf.read(raw)
    if x.ndim > 1:
        x = x.mean(axis=1)
    hop = int(sr * HOP)
    n = len(x) // hop
    rms = np.sqrt(np.array([np.mean(x[i*hop:(i+1)*hop] ** 2) for i in range(n)]) + 1e-12)
    thr = max(0.01, np.percentile(rms, 95) * 0.06)
    voiced = rms > thr
    idx = np.flatnonzero(voiced)
    a, b = idx[0], idx[-1] + 1
    # silent gaps inside the speech
    gaps, i = [], a
    while i < b:
        if not voiced[i]:
            j = i
            while j < b and not voiced[j]:
                j += 1
            gaps.append((i, j))
            i = j
        else:
            i += 1
    text = lines[v["frame"]]
    words = text.split()

    def split(pattern):
        ph, cur = [], []
        for w in words:
            cur.append(w)
            if re.search(pattern, w):
                ph.append(cur); cur = []
        if cur:
            ph.append(cur)
        return ph

    # Real pauses only (>= 0.10 s). Fast reads don't pause at every comma: use comma-level phrases when
    # there are enough pauses for them, else sentence-level, else spread words over the whole line.
    sig = [g for g in gaps if (g[1] - g[0]) * HOP >= 0.10]
    phrases = split(r"[,.;:?!]$")
    if len(sig) < len(phrases) - 1:
        phrases = split(r"[.?!]$")
    k = len(phrases) - 1
    if len(sig) < k:
        phrases, k = [words], 0
    big = sorted(sorted(sig, key=lambda g: g[1] - g[0], reverse=True)[:k])
    if len(big) == k and k > 0:
        bounds = [a] + [g for gp in big for g in gp] + [b]
        spans = [(bounds[2*i], bounds[2*i+1]) for i in range(k + 1)]
    else:  # fall back: one span, proportional
        spans, phrases = [(a, b)], [words]
    out, wid = [], 0
    for (s0, s1), ph in zip(spans, phrases):
        wts = [len(re.sub(r"[^A-Za-z0-9]", "", w)) + 1.5 for w in ph]
        tot, t = sum(wts), s0 * HOP
        for w, wt in zip(ph, wts):
            d = (s1 - s0) * HOP * wt / tot
            out.append({"id": f"{v['frame']:02d}-{wid}", "text": w, "start": round(LEAD + t - a*HOP, 3), "end": round(LEAD + t + d - a*HOP, 3)})
            t += d; wid += 1
    speech = x[a*hop:b*hop]
    y = np.concatenate([np.zeros(int(LEAD*sr)), speech, np.zeros(int(TAIL*sr))])
    sf.write(v["path"], y.astype(np.float32), sr)
    v["duration_s"] = round(len(y) / sr, 3)
    v["words"] = out
    print(f"  {v['frame']:02d}: {v['duration_s']:.2f}s, {len(out)} words, {len(spans)} phrase span(s)")
json.dump(meta, open("audio_meta.json", "w"), indent=2)
print("total", round(sum(v["duration_s"] for v in meta["voices"]), 2), "s")
