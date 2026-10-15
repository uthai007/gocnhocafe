#!/usr/bin/env bash
# Full rebuild of "Mechatronics Explained" after editing SCRIPT.md / STORYBOARD.md / tools/build-frames.py.
# Run from the project root. Regenerating narration: delete assets/voice first.
set -euo pipefail
S=../../.claude/skills/faceless-explainer/scripts
PY=${HYPERFRAMES_PYTHON:-$HOME/.venvs/kokoro/bin/python}
export HYPERFRAMES_PYTHON=$PY
if [ ! -f assets/voice/01.wav ]; then
  node $S/audio.mjs --script ./SCRIPT.md --storyboard ./STORYBOARD.md --hyperframes . --out ./audio_meta.json --voice am_michael
  "$PY" tools/pad-and-time.py
  "$PY" tools/make-bgm.py assets/bgm/bed.wav 176
  python3 -c "import json;m=json.load(open('audio_meta.json'));m['bgm']={'path':'assets/bgm/bed.wav','source':'host','volume':0.12};m['bgm_pending']=False;json.dump(m,open('audio_meta.json','w'),indent=2)"
fi
node $S/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md
python3 tools/build-frames.py
node $S/captions.mjs build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json
node $S/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .
node $S/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .
node $S/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html
# the render browser cannot reach CDNs: use the vendored GSAP
sed -i -E 's#<script src="https://cdn.jsdelivr.net/npm/gsap@[0-9.]+/dist/gsap.min.js"[^>]*></script>#<script src="assets/vendor/gsap.min.js"></script>#' index.html compositions/captions.html
sed -i 's|        id="el-captions"|        id="el-captions"\n        data-track-kind="captions"|' index.html
