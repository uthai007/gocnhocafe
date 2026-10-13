# MBA English with William — Session Handoff

Everything a new Claude session needs to continue this project exactly where it stopped.
Repo: `uthai007/gocnhocafe`, branch `main`, project folder `videos/mba-with-william/`.
Local copy target on the owner's PC: `D:\Youtuber\William`.

---

## 1. Ready-to-paste prompt for a new session

> I'm continuing my YouTube/TikTok series **"MBA English with William"**. Read
> `videos/mba-with-william/SESSION_HANDOFF.md` first, then `README.md` and `BRIEF.md` in the same folder.
> Keep every decision in the handoff (character, voice, music, layout, 6 sentences per episode, English-only
> captions). Reply to me in Vietnamese. Next task: <write your request here, e.g. "make Day 11–15">.

---

## 2. The series (owner's original requirements)

1. Presenter character **William**, about **35 years old**, speaks **American English**.
2. He **stands on a stage giving a talk**.
3. Topic: **MBA content** for people preparing to study an MBA — they **practise English and learn MBA** at the same time.
4. Each short video = **exactly 6 sentences** on one MBA topic.
5. **Only William speaks** in every episode.
6. Day 1 script was given by the owner; from Day 2 on, Claude writes the topic and the 6 sentences.

Owner communicates in **Vietnamese**; answer in Vietnamese.

## 3. Decisions locked in (do not change without asking)

| Item | Decision |
|---|---|
| Character look | Illustrated SVG William: short brown hair, light stubble, blue eyes, navy blazer, white open-collar shirt, gold lapel pin, dark trousers, holds a presentation clicker in his left hand |
| Format | Vertical **9:16, 1080×1920, 30 fps** (TikTok / Reels / Shorts) |
| Captions | **English only**, word-by-word highlight (current word gold `#f2c14e`), "SENTENCE n / 6" counter |
| Voice | Kokoro TTS **`am_michael`** (US male), **speed 1.08**, pause 0.45 s between sentences, lead-in 0.8 s, tail 1.4 s |
| Voice processing | high-pass 80 Hz, −2 dB @200 Hz, +4 dB @3 kHz, +2 dB @8 kHz, compressor 3:1, loudnorm −14 LUFS |
| Music | Synthesised upbeat bed (`scripts/make-bgm.py`, 118 BPM, C major, C–G–Am–F), level **−10 dB**, **sidechain-ducked ~10 dB under the voice**, final mix −14 LUFS |
| Rejected options | HeyGen realistic avatar (no account in cloud), voice `am_adam`, Vietnamese subtitles |
| Animation | Lip sync from voice loudness, blinks, body sway, brow raise + head tilt per sentence, right arm alternates "open palm up" / "explaining across body", left hand clicks the clicker before each sentence, screen progress dots advance |
| Stage layout | Navy back wall, red curtains, wooden floor, spotlight beam + floor pool, LED screen (top) showing `MBA ENGLISH · DAY XX`, topic title, subtitle, 6 progress dots; name tag "William / MBA Coach" for the first ~7 s; caption box at bottom |
| Fonts / colours | Montserrat; navy `#0b1020`/`#1f2e4a`, gold `#f2c14e`, light blue text `#c9d6f5` |

## 4. Episodes produced (all rendered, checked, committed)

| Day | Topic | Subtitle | Length |
|---|---|---|---|
| 1 | Strategic Leadership | in Modern Business | 37.9 s |
| 2 | Competitive Advantage | Why Some Companies Win | 43.2 s |
| 3 | SWOT Analysis | A Simple Tool for Big Decisions | 44.0 s |
| 4 | Market Segmentation | Know Exactly Who You Serve | 42.9 s |
| 5 | Value Proposition | Why Customers Choose You | 42.4 s |
| 6 | Financial Statements | The Language of Business | 40.6 s |
| 7 | Cash Flow Management | Cash Is King | 40.2 s |
| 8 | Supply Chain Management | From Supplier to Customer | 44.0 s |
| 9 | Change Management | Leading People Through Change | 43.8 s |
| 10 | Corporate Social Responsibility | Doing Well by Doing Good | 47.2 s |

Exact sentences: `series/day-01.json` … `series/day-10.json`.
Videos: `renders/william-mba-day-01.mp4` … `day-10.mp4`.

Script-writing style used so far: sentence 1 starts "Today, I would like to talk about …"; sentences 2–5 define and explain;
sentence 6 starts "For example, …" with a well-known company or author. Keep each sentence ≤ ~120 characters
(captions auto-shrink above 85/110 characters).

Suggested next topics (not yet made): Leadership Styles, Organizational Culture, Negotiation, Pricing Strategy,
Brand Management, Business Ethics, Project Management, Entrepreneurship, Mergers & Acquisitions, Digital Transformation.

## 5. Branding assets (in `branding/`)

| File | What |
|---|---|
| `william-profile-1080.png`, `william-profile-400.png` | Profile picture: smiling William bust in gold ring, "MBA ENGLISH" pill, circle-crop safe |
| `banner-youtube.png` | 2560×1440 YouTube banner (content inside the 1546×423 safe area) |
| `banner-facebook.png` | 1640×624 Facebook cover (content inside mobile-safe centre) |
| `william-transparent-bust.png`, `william-transparent-full.png` | William on transparent background (RGBA) |
| `stage-bg-vertical.mp4`, `stage-bg-horizontal.mp4` | 12 s seamless stage loops, no William/text (9:16 and 16:9) |
| `profile/`, `banner-youtube/`, `banner-facebook/`, `transparent-*/`, `stage-bg-*/` | Source HTML compositions for the above |
| `make-transparent.py`, `make-stage-bg.py` | Regenerate the transparent / stage-loop compositions |

Audio test samples (voice/music comparison): `samples/1-michael.mp3` … `4-adam-nhac-nen.mp3`.

## 6. Project structure

```
videos/mba-with-william/
  SESSION_HANDOFF.md   <- this file
  README.md            <- how to add an episode (Vietnamese)
  BRIEF.md             <- HyperFrames brief (workflow general-video, automation, no storyboard)
  series/day-XX.json   <- {day, topic, subtitle, sentences[6]}
  scripts/template.html   <- stage + William SVG + captions + animation (EDIT LOOK HERE)
  scripts/make-episode.mjs <- TTS -> join -> voice FX -> music + ducking -> lip-sync envelope -> word timings -> index.html
  scripts/make-bgm.py     <- music bed generator
  index.html           <- generated composition of the last built episode (never edit by hand)
  assets/audio/day-XX.wav <- final mixed audio per episode
  assets/vendor/gsap.min.js <- vendored (renderer cannot reach CDNs)
  renders/             <- final MP4s
  branding/            <- see section 5
```
Repo root also has `.claude/skills/` (HyperFrames skill pack, installed with `npx skills add heygen-com/hyperframes`)
and `skills-lock.json`.

## 7. How to make a new episode

```bash
cd videos/mba-with-william
# 1. create series/day-11.json (copy day-10.json; edit day, topic, subtitle, 6 sentences)
node scripts/make-episode.mjs 11
npx hyperframes check                     # must say "Check passed"
npx hyperframes snapshot --at 12 --no-end # optional visual check
npx hyperframes render -q delivery -o renders/william-mba-day-11.mp4
```
The `off_pivot_rotation #w-fore-r` warning from `check` is a known false positive (it reads the arm as a gauge needle); ignore it.

## 8. Environment setup (new machine or new cloud container)

- Node.js 18+, ffmpeg/ffprobe, Python 3.10+.
- HyperFrames CLI runs through `npx hyperframes` (project pins `hyperframes@0.8.141` in `package.json`; 0.8.143 also worked).
- Kokoro voice (offline):
  `uv venv ~/.venvs/kokoro && VIRTUAL_ENV=~/.venvs/kokoro uv pip install kokoro-onnx soundfile`
  (Windows: create a venv anywhere and set `HYPERFRAMES_PYTHON` to its `python.exe`; `numpy` comes with kokoro-onnx).
  `make-episode.mjs` auto-uses `~/.venvs/kokoro/bin/python` if `HYPERFRAMES_PYTHON` is not set; the same Python runs `make-bgm.py`.
- TTS results are cached in `.cache/tts/` (git-ignored); first run downloads the Kokoro model.
- GSAP is vendored locally because the render browser could not load CDN scripts in the cloud container.

## 9. Git conventions used

- All work committed directly to `main` of `uthai007/gocnhocafe` and pushed after every step (owner's stop-hook requires a clean, pushed tree).
- `.gitignore` in the project ignores `.cache/`, `snapshots/`, `node_modules/`, `.hyperframes/`.
