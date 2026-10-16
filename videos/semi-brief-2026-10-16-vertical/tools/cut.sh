#!/usr/bin/env bash
# cut.sh <in.mp4> <out.mp4> <end_seconds> — trim with a 0.4 s video+audio fade-out, loudness -14 LUFS.
set -euo pipefail
in=$1; out=$2; end=$3
fo=$(python3 -c "print(max(0,$end-0.4))")
ffmpeg -nostdin -v error -y -i "$in" -t "$end" -vf "fade=t=out:st=$fo:d=0.4" -af "afade=t=out:st=$fo:d=0.4,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$out"
