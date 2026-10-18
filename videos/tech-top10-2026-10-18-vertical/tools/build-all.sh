#!/usr/bin/env bash
# Rebuild the Top 10 AI · Chips · Quantum video — 18 Oct 2026 (run from the project root).
set -euo pipefail
S=../../.claude/skills/faceless-explainer/scripts
node $S/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md
python3 tools/build-frames.py
node $S/captions.mjs build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json
node $S/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .
node $S/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .
node $S/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html
python3 tools/post-assemble.py
