#!/usr/bin/env bash
# Re-voice every SCRIPT.md line: Kokoro am_michael @1.08 (near-native speed sounds far less synthetic than
# the earlier 1.28), natural sentence/clause pauses, then a light chain: gentle EQ, de-ess, 2.5:1 compression,
# faint small-room ambience so the read sounds recorded rather than dry/synthetic.
set -euo pipefail
PY=${HYPERFRAMES_PYTHON:-$HOME/.venvs/kokoro/bin/python}
FX="highpass=f=70,equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2,deesser,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,aecho=0.85:0.9:16|27:0.07|0.04,loudnorm=I=-16:TP=-1.5"
rm -rf assets/voice/raw
"$PY" - <<'PY'
import re, soundfile as sf
from kokoro_onnx import Kokoro
C = "/root/.cache/hyperframes/tts/"
k = Kokoro(C + "models/kokoro-v1.0.onnx", C + "voices/voices-v1.0.bin")
s = open("SCRIPT.md").read()
for m in re.finditer(r"^## Line (\d+) — .*?\n(?:.*?\n)*?\n    (.+)$", s, re.M):
    a, sr = k.create(m.group(2).strip(), voice="am_michael", speed=1.08, sentence_pause=0.32, clause_pause=0.12)
    sf.write(f"assets/voice/{int(m.group(1)):02d}.tts.wav", a, sr)
PY
for f in assets/voice/*.tts.wav; do
  ffmpeg -nostdin -v error -y -i "$f" -af "$FX" -ar 48000 "${f%.tts.wav}.wav" && rm "$f"
  echo "  voiced $(basename "${f%.tts.wav}")"
done
"$PY" tools/pad-and-time.py | tail -1
