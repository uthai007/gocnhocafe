---
workflow: general-video
flow: automation
storyboard: no
message: "How AI tool usage grew across Southeast Asia, month by month, Jan 2024 – Jun 2026."
destination: youtube-shorts
aspect: "9:16"
format: 1080x1920
language: en-US
audience: "General audience curious about AI adoption in Southeast Asia"
length: "54s"
---

## Intent
"Tạo một video thống kê bằng tiếng Anh về lượng người dùng AI các nước đông nam á của các tháng từ năm 2024 đến nay
theo hình thức racing như hình đính kèm" — an English bar-chart race of monthly AI usage in Southeast Asian countries
from 2024 to now, styled like the attached Vietnamese infographic (navy background, yellow / teal / magenta / salmon
bars by rank, round flags, share % inside the bar, visits at the bar end, stacked-outline year, pie of shares).

## Data (see ../sea-ai-race-2024-2026/tools/build-data.py)
- Metric: AI-tool website visits (AITools.xyz, SEMrush + Ahrefs estimates) — the same metric as the reference image.
  Visits, not unique users; app sessions excluded.
- Countries: ASEAN-6 (Indonesia, Philippines, Vietnam, Thailand, Malaysia, Singapore) — the only SEA countries with
  published figures. Myanmar, Cambodia, Laos, Brunei, Timor-Leste have none, so they are left out rather than invented.
- Range: Jan 2024 – Jun 2026, the latest published month (today is 18 Oct 2026).
- No public month-by-month country series exists: months are interpolated (smoothest curve matching the 2024 and 2025
  annual totals and the June 2026 figures). Malaysia and Singapore June 2026 are estimated. Disclosed on screen.
- Callouts use only annual totals and June 2026 figures.

## Customizations
- Music only (synthesised 124 BPM bed, tools/make-bgm.py); no narration.
- One template (tools/template.html) builds both cuts: `python3 tools/build-index.py land|port <dir>`.
