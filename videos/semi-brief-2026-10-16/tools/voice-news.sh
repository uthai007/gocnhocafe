#!/usr/bin/env bash
# Re-voice every SCRIPT.md line as a brisk news read: Kokoro am_michael @1.28 + broadcast EQ/compression.
set -euo pipefail
export HYPERFRAMES_PYTHON=${HYPERFRAMES_PYTHON:-$HOME/.venvs/kokoro/bin/python}
FX="highpass=f=90,equalizer=f=180:t=q:w=1:g=-2.5,equalizer=f=2800:t=q:w=1.1:g=5,equalizer=f=7500:t=q:w=1:g=3,acompressor=threshold=-22dB:ratio=4:attack=4:release=60:makeup=4,alimiter=limit=0.95"
python3 - <<'PY' > /tmp/voice-lines.tsv
import re
s=open('SCRIPT.md').read()
for m in re.finditer(r"^## Line (\d+) — .*?\n(?:.*?\n)*?\n    (.+)$", s, re.M):
    print(f"{int(m.group(1)):02d}\t{m.group(2).strip()}")
PY
rm -rf assets/voice/raw
while IFS=$'\t' read -r id text; do
  npx hyperframes tts "$text" -v am_michael -s 1.28 -o "assets/voice/$id.tts.wav" --json </dev/null >/dev/null 2>&1
  ffmpeg -nostdin -v error -y -i "assets/voice/$id.tts.wav" -af "$FX" "assets/voice/$id.wav" && rm "assets/voice/$id.tts.wav"
  echo "  voiced $id"
done < /tmp/voice-lines.tsv
"$HYPERFRAMES_PYTHON" tools/pad-and-time.py | tail -1
