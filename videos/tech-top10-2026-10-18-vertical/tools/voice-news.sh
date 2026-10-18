#!/usr/bin/env bash
# Re-voice every SCRIPT.md line as an energetic news read that still sounds natural: Kokoro am_michael is
# generated near its native pace (1.06, where its prosody is cleanest), then time-stretched 12% faster with a
# 3% formant-preserving pitch lift (rubberband) for energy, then a punchy broadcast chain: presence/air EQ,
# de-ess, 3.5:1 compression and a faint room so it doesn't sound dry/synthetic.
set -euo pipefail
PY=${HYPERFRAMES_PYTHON:-$HOME/.venvs/kokoro/bin/python}
FX="rubberband=tempo=1.12:pitch=1.03:formant=preserved,highpass=f=80,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=1.1:g=3.5,equalizer=f=8000:t=q:w=1:g=2,deesser,acompressor=threshold=-22dB:ratio=3.5:attack=5:release=80:makeup=3,aecho=0.85:0.9:14|23:0.05|0.03,loudnorm=I=-16:TP=-1.5"
rm -rf assets/voice/raw
"$PY" - <<'PY'
import re, soundfile as sf
from kokoro_onnx import Kokoro
C = "/root/.cache/hyperframes/tts/"
k = Kokoro(C + "models/kokoro-v1.0.onnx", C + "voices/voices-v1.0.bin")
s = open("SCRIPT.md").read()
for m in re.finditer(r"^## Line (\d+) — .*?\n(?:.*?\n)*?\n    (.+)$", s, re.M):
    a, sr = k.create(m.group(2).strip(), voice="am_michael", speed=1.06, sentence_pause=0.22, clause_pause=0.06)
    sf.write(f"assets/voice/{int(m.group(1)):02d}.tts.wav", a, sr)
PY
for f in assets/voice/*.tts.wav; do
  ffmpeg -nostdin -v error -y -i "$f" -af "$FX" -ar 48000 "${f%.tts.wav}.wav" && rm "$f"
  echo "  voiced $(basename "${f%.tts.wav}")"
done
"$PY" tools/pad-and-time.py | tail -1
