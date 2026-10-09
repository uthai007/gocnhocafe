#!/usr/bin/env python3
"""Synthesise a light, upbeat background-music bed (royalty-free, deterministic).

    ~/.venvs/kokoro/bin/python scripts/make-bgm.py assets/audio/bgm.wav 60

118 BPM, C major, I-V-vi-IV: soft kick, off-beat hats, light clap, bass, warm pad, bright pluck arpeggio.
Ends with a 2-second fade-out. Same output every run.
"""
import sys
import numpy as np
import soundfile as sf

SR = 48000
BPM = 118
BEAT = 60 / BPM
out_path = sys.argv[1] if len(sys.argv) > 1 else "bgm.wav"
seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
n = int(seconds * SR)
mix = np.zeros((n, 2))
rng = np.random.default_rng(7)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= n:
        return
    sig = sig[: n - i] * gain
    mix[i : i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2)
    mix[i : i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2)


def env(length, a=0.005, d=0.2, s=0.0, r=0.05):
    t = np.arange(int(length * SR)) / SR
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    tail = int(r * SR)
    if tail and len(e) > tail:
        e[-tail:] *= np.linspace(1, 0, tail)
    return e


def kick():
    L = 0.35
    t = np.arange(int(L * SR)) / SR
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def hat():
    L = 0.06
    x = rng.standard_normal(int(L * SR))
    x = np.diff(x, prepend=0)  # crude high-pass
    return x * env(L, 0.001, 0.015) * 0.5


def clap():
    L = 0.18
    x = rng.standard_normal(int(L * SR))
    x = np.diff(x, prepend=0)
    return x * env(L, 0.002, 0.05) * 0.6


def pluck(m, L=0.35):
    t = np.arange(int(L * SR)) / SR
    f = midi(m)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return s * env(L, 0.003, 0.12)


def pad(ms, L):
    t = np.arange(int(L * SR)) / SR
    s = sum(np.sin(2 * np.pi * midi(m) * t) + 0.5 * np.sin(2 * np.pi * midi(m) * 1.003 * t) for m in ms)
    e = np.minimum(1, t / 0.25) * np.minimum(1, (L - t) / 0.3)
    return s * e / len(ms)


def bass(m, L):
    t = np.arange(int(L * SR)) / SR
    f = midi(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return s * env(L, 0.005, 0.5, 0.4, 0.05)


# C - G - Am - F  (root, chord tones for pad, arpeggio notes)
chords = [
    (36, [60, 64, 67], [72, 76, 79, 76]),
    (43, [59, 62, 67], [71, 74, 79, 74]),
    (45, [60, 64, 69], [72, 76, 81, 76]),
    (41, [60, 65, 69], [72, 77, 81, 77]),
]
bar = 4 * BEAT
bars = int(np.ceil(seconds / bar))
for b in range(bars):
    t0 = b * bar
    root, tones, arp = chords[b % 4]
    place(pad(tones, bar), t0, 0, 0.10)
    for k in range(8):  # eighth-note bass pulse
        place(bass(root, BEAT / 2 * 0.9), t0 + k * BEAT / 2, 0, 0.22)
    for k in range(8):  # pluck arpeggio, alternating pan
        place(pluck(arp[k % 4]), t0 + k * BEAT / 2, -0.3 if k % 2 else 0.3, 0.09)
    for k in range(4):
        place(kick(), t0 + k * BEAT, 0, 0.55)
        place(hat(), t0 + k * BEAT + BEAT / 2, 0.2, 0.25)
        if k in (1, 3):
            place(clap(), t0 + k * BEAT, -0.1, 0.18)

fade = int(2.0 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= np.max(np.abs(mix)) + 1e-9
sf.write(out_path, (mix * 0.89).astype(np.float32), SR)
print(f"wrote {out_path} ({seconds:.1f}s)")
