#!/usr/bin/env python3
"""VERTICAL 9:16 (1080x1920) version. Build all 13 frame sub-compositions (compositions/frames/NN-*.html) for "Mechatronics Explained".

    python3 tools/build-frames.py        # run from the project root, after tools/pad-and-time.py + sync-durations

Design: Cobalt Grid (frame.md) — cream graph paper, cobalt ink only, Newsreader / Hanken Grotesk / DM Mono.
Every reveal is timed to the narration: cue("word") returns the frame-relative start time of that spoken
word (from audio_meta.json), so elements appear exactly when the voice names them.
"""
import json, math, os, re

INK, SOFT, PAPER, GRIDC, FAINT = "#1F2BE0", "#5560E5", "#F0EBDE", "rgba(31,43,224,0.10)", "rgba(31,43,224,0.18)"
TOTAL_FRAMES = 13

meta = json.load(open("audio_meta.json"))
WORDS = {v["frame"]: v["words"] for v in meta["voices"]}
sb = open("STORYBOARD.md").read()
FRAMES = []
for m in re.finditer(r"^## Frame (\d+) — .*?$(.*?)(?=^## Frame |\Z)", sb, re.M | re.S):
    n = int(m.group(1))
    body = m.group(2)
    dur = float(re.search(r"^- duration: ([\d.]+)s", body, re.M).group(1))
    src = re.search(r"^- src: (\S+)", body, re.M).group(1)
    FRAMES.append((n, dur, src))


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def cue(n, word, nth=1, off=0.0):
    k = 0
    for w in WORDS[n]:
        if norm(w["text"]).startswith(norm(word)):
            k += 1
            if k == nth:
                return round(max(0.05, w["start"] + off), 3)
    raise KeyError(f"frame {n}: word {word!r} #{nth} not found")


def cue_end(n, word, nth=1, off=0.0):
    k = 0
    for w in WORDS[n]:
        if norm(w["text"]).startswith(norm(word)):
            k += 1
            if k == nth:
                return round(w["end"] + off, 3)
    raise KeyError(word)


# ---------------------------------------------------------------- shared shell
def shell(fid, n, dur, css, stage, js, final=False):
    p = "s" + fid
    return f"""<template id="{p}-template">
  <div id="root" data-composition-id="{fid}" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
    <style>
      @font-face {{ font-family: "Newsreader"; font-style: normal; font-weight: 400; src: url("assets/fonts/Newsreader-Regular.woff2") format("woff2"); }}
      @font-face {{ font-family: "Newsreader"; font-style: italic; font-weight: 400; src: url("assets/fonts/Newsreader-Italic.woff2") format("woff2"); }}
      @font-face {{ font-family: "Hanken Grotesk"; font-style: normal; font-weight: 400 700; src: url("assets/fonts/Hanken_Grotesk-Variable.woff2") format("woff2"); }}
      @font-face {{ font-family: "DM Mono"; font-style: normal; font-weight: 400; src: url("assets/fonts/DM_Mono-Regular.woff2") format("woff2"); }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; color: {INK};
        font-family: "Hanken Grotesk", sans-serif; }}
      #{p}-ground {{ position: absolute; inset: 0; background-color: {PAPER};
        background-image: linear-gradient({GRIDC} 1px, transparent 1px), linear-gradient(90deg, {GRIDC} 1px, transparent 1px);
        background-size: 38.4px 38.4px; background-position: -1px -1px; }}
      #{p}-ground .hl {{ position: absolute; left: 60px; right: 60px; height: 2px; background: {INK}; }}
      #{p}-ground .chrome {{ position: absolute; top: 62px; font-family: "DM Mono", monospace; font-size: 20px;
        letter-spacing: 0.08em; color: {INK}; }}
      #{p}-stage {{ position: absolute; inset: 0; }}
      #{p}-stage .serif {{ font-family: "Newsreader", serif; font-weight: 400; }}
      #{p}-stage .mono {{ font-family: "DM Mono", monospace; letter-spacing: 0.06em; }}
      #{p}-stage .label {{ font-family: "Hanken Grotesk", sans-serif; font-weight: 600; text-transform: uppercase; letter-spacing: 0.16em; }}
      #{p}-stage .abs {{ position: absolute; display: block; }}
      #{p}-stage svg {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }}
      #{p}-stage .draw {{ fill: none; stroke: {INK}; stroke-width: 4; stroke-linecap: square; stroke-linejoin: miter; }}
{css}
    </style>
    <div id="{p}-ground" class="clip" data-start="0" data-duration="{dur}" data-track-index="0">
      <div class="hl" style="top: 100px"></div>
      <div class="hl" style="top: 1850px"></div>
      <div class="chrome" style="left: 60px">MECHATRONICS — EXPLAINED</div>
      <div class="chrome" style="right: 60px">{n:02d} / {TOTAL_FRAMES:02d}</div>
    </div>
    <div id="{p}-stage" class="clip" data-start="0" data-duration="{dur}" data-track-index="1">
      <div id="{p}-cam" class="abs" style="left:0;top:0;width:1080px;height:1920px">
{stage}
      </div>
    </div>
    <script src="assets/vendor/gsap.min.js"></script>
    <script>
      (function () {{
        const tl = gsap.timeline({{ paused: true }});
        const D = {dur};
        const q = (s) => "#{p}-stage " + s;
        const draw = (sel, at, d) => tl.fromTo(q(sel), {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: d || 0.9, ease: "power2.inOut" }}, at);
        const pop = (sel, at, d) => tl.fromTo(q(sel), {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: d || 0.5, ease: "power3.out" }}, at);
        const fade = (sel, at, d) => tl.fromTo(q(sel), {{ opacity: 0 }}, {{ opacity: 1, duration: d || 0.5, ease: "power1.out" }}, at);
        const grow = (sel, at, d) => tl.fromTo(q(sel), {{ opacity: 0, scale: 0.86 }}, {{ opacity: 1, scale: 1, duration: d || 0.55, ease: "back.out(1.6)" }}, at);
        tl.fromTo("#{p}-cam", {{ scale: 1 }}, {{ scale: 1.035, duration: D, ease: "none", transformOrigin: "50% 45%" }}, 0);
{js}
{"        tl.to('#" + p + "-cam', { opacity: 0, duration: 0.6, ease: 'power1.in' }, D - 0.75);" if final else ""}
        window.__timelines["{fid}"] = tl;
      }})();
    </script>
  </div>
</template>
"""


def path(d, cls="draw", extra=""):
    return f'<path class="{cls}" pathLength="1" style="stroke-dasharray:1" d="{d}" {extra}/>'


def rect_d(x, y, w, h):
    return f"M{x} {y} H{x+w} V{y+h} H{x} Z"


def circle_d(cx, cy, r):
    return f"M{cx-r} {cy} A{r} {r} 0 1 0 {cx+r} {cy} A{r} {r} 0 1 0 {cx-r} {cy}"


def gear_d(cx, cy, r_out, r_in, teeth=8):
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        r = r_out if (i % 4) in (1, 2) else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


out = {}
# Vertical canvas 1080x1920. Content lives in y 140..1580 (captions own the bottom ~17%).

# ---------------------------------------------------------------- 01 hook
n = 1
# reuse the 16:9 line drawings, moved into a vertical stack
stage = f"""
        <svg viewBox="0 0 1080 1920">
          <g id="f01-arm" transform="translate(80 -150)">
            {path(rect_d(250, 640, 180, 50), "draw a1")}
            {path("M340 640 L340 500 L500 400 L620 450", "draw a2")}
            {path("M620 450 L668 424 M620 450 L662 494", "draw a3")}
            {path(rect_d(326, 486, 28, 28) + rect_d(486, 386, 28, 28), "draw a4")}
          </g>
          <g id="f01-car" transform="translate(-440 270)">
            {path("M790 650 L810 585 L890 530 L1050 530 L1120 585 L1170 595 L1170 650 Z", "draw c1")}
            {path("M905 545 L1040 545 L1085 585 L880 585 Z", "draw c2")}
            {path(circle_d(880, 655, 36) + circle_d(1090, 655, 36), "draw c3")}
            {path(rect_d(955, 500, 44, 24) + " M948 488 Q977 470 1006 488 M938 476 Q977 450 1016 476", "draw c4")}
          </g>
          <g id="f01-washer" transform="translate(-970 700)">
            {path(rect_d(1360, 410, 300, 300), "draw w1")}
            {path("M1360 470 H1660", "draw w2")}
            {path(circle_d(1510, 595, 92) + circle_d(1510, 595, 62), "draw w3")}
            {path(rect_d(1390, 430, 22, 22) + rect_d(1430, 430, 22, 22), "draw w4")}
          </g>
        </svg>
        <div class="abs label" style="left:0;width:1080px;text-align:center;top:575px;font-size:24px" id="f01-t1">ROBOT ARM</div>
        <div class="abs label" style="left:0;width:1080px;text-align:center;top:985px;font-size:24px" id="f01-t2">SELF-DRIVING CAR</div>
        <div class="abs label" style="left:0;width:1080px;text-align:center;top:1440px;font-size:24px" id="f01-t3">WASHING MACHINE</div>
        <div class="abs serif" id="f01-q" style="left:0;width:1080px;top:470px;text-align:center;font-size:520px;line-height:1">?</div>
        <div class="abs mono" id="f01-tag" style="left:0;width:1080px;top:1180px;text-align:center;font-size:34px">WHAT DO THEY SHARE?</div>
"""
t_arm, t_car, t_wash, t_q = cue(n, "robot", off=-0.1), cue(n, "self"), cue(n, "washing"), cue(n, "what")
js = f"""
        draw(".a1", {t_arm}, 0.5); draw(".a2", {t_arm + 0.25}, 0.8); draw(".a3", {t_arm + 0.8}, 0.4); draw(".a4", {t_arm + 0.9}, 0.4);
        fade("#f01-t1", {t_arm + 0.5});
        draw(".c1", {t_car}, 0.8); draw(".c2", {t_car + 0.4}, 0.5); draw(".c3", {t_car + 0.6}, 0.5); draw(".c4", {t_car + 0.9}, 0.5);
        fade("#f01-t2", {t_car + 0.6});
        draw(".w1", {t_wash}, 0.7); draw(".w2", {t_wash + 0.3}, 0.3); draw(".w3", {t_wash + 0.4}, 0.7); draw(".w4", {t_wash + 0.7}, 0.3);
        fade("#f01-t3", {t_wash + 0.6});
        tl.to(q("svg"), {{ opacity: 0.22, duration: 0.5, ease: "power1.out" }}, {t_q});
        tl.to(q("#f01-t1, #f01-t2, #f01-t3"), {{ opacity: 0, duration: 0.4 }}, {t_q});
        grow("#f01-q", {t_q + 0.1}, 0.7);
        pop("#f01-tag", {cue(n, "common")});
"""
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 02 concept
n = 2
tiles = [("Mechanics", "MOVING PARTS", 0, 0), ("Electronics", "SIGNALS · POWER", 1, 0), ("Computing", "CODE · LOGIC", 0, 1), ("Control", "FEEDBACK", 1, 1)]
tile_html = ""
for i, (name, sub, cx, cy) in enumerate(tiles):
    x, y = 90 + cx * 460, 720 + cy * 370
    tile_html += f"""        <div class="abs f02-tile" id="f02-tile{i}" style="left:{x}px;top:{y}px;width:440px;height:350px">
          <div class="mono" style="font-size:22px">0{i+1}</div>
          <div class="serif" style="font-size:62px;margin-top:140px">{name}</div>
          <div class="label" style="font-size:20px;margin-top:12px">{sub}</div>
        </div>
"""
css = f"""      #02-concept-stage .f02-tile {{ border: 2px solid {INK}; background: {PAPER}; padding: 26px 30px; box-sizing: border-box; }}"""
stage = f"""
        <div class="abs label" id="f02-kicker" style="left:90px;top:220px;font-size:26px">THE MAJOR</div>
        <div class="abs serif" id="f02-title" style="left:84px;top:270px;font-size:156px;line-height:0.95;letter-spacing:-0.01em">Mechatronics</div>
        <div class="abs serif" id="f02-callout" style="left:90px;top:470px;font-size:58px;font-style:italic;color:{SOFT};width:900px;line-height:1.15">the engineering of smart machines</div>
{tile_html}        <svg viewBox="0 0 1080 1920">{path(rect_d(70, 700, 940, 780), "draw f02-unite")}</svg>
        <div class="abs mono" id="f02-one" style="left:0;width:1080px;text-align:center;top:1500px;font-size:28px">ONE DESIGN</div>
"""
js = f"""
        pop("#f02-kicker", 0.15); pop("#f02-title", 0.25, 0.7);
        tl.fromTo(q("#f02-callout"), {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }}, {cue(n, "engineering")});
        grow("#f02-tile0", {cue(n, "mechanics,")}); grow("#f02-tile1", {cue(n, "electronics")});
        grow("#f02-tile2", {cue(n, "computing")}); grow("#f02-tile3", {cue(n, "control")});
        draw(".f02-unite", {cue(n, "together")}, 1.0);
        fade("#f02-one", {cue(n, "design")});
"""
out[n] = (css, stage, js)

# ---------------------------------------------------------------- 03 origin
n = 3
stage = f"""
        <div class="abs label" id="f03-k" style="left:90px;top:220px;font-size:26px">WHERE THE WORD CAME FROM</div>
        <div class="abs serif" id="f03-year" style="left:76px;top:260px;font-size:330px;line-height:0.9;letter-spacing:-0.015em">1969</div>
        <div class="abs mono" id="f03-japan" style="left:90px;top:600px;font-size:32px">JAPAN</div>
        <div class="abs mono" id="f03-who" style="left:90px;top:650px;font-size:30px">TETSURO MORI · YASKAWA ELECTRIC</div>
        <div class="abs serif" id="f03-r1" style="left:90px;top:800px;font-size:120px"><span>Mecha</span><span style="opacity:0.28">nics</span></div>
        <div class="abs serif" id="f03-plus" style="left:90px;top:940px;font-size:96px">+</div>
        <div class="abs serif" id="f03-r2" style="left:90px;top:1050px;font-size:120px"><span style="opacity:0.28">Elec</span><span>tronics</span></div>
        <div class="abs" id="f03-rule" style="left:90px;top:1230px;width:900px;height:3px;background:{INK}"></div>
        <div class="abs serif" id="f03-res" style="left:84px;top:1270px;font-size:140px;letter-spacing:-0.01em">Mechatronics</div>
"""
t_year = cue(n, "1969")
js = f"""
        pop("#f03-k", 0.1);
        const yr = {{ v: 1900 }};
        const yel = document.querySelector("#03-origin-stage #f03-year");
        tl.fromTo(yr, {{ v: 1900 }}, {{ v: 1969, duration: 1.1, ease: "power2.out", onUpdate: () => {{ yel.textContent = Math.round(yr.v); }} }}, {t_year - 0.6});
        fade("#f03-year", {t_year - 0.6}, 0.3);
        pop("#f03-japan", {cue(n, "japan")}); pop("#f03-who", {cue(n, "tetsuro")});
        pop("#f03-r1", {cue(n, "mechanics")}); fade("#f03-plus", {cue(n, "plus")}); pop("#f03-r2", {cue(n, "electronics")});
        tl.fromTo(q("#f03-rule"), {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.5, ease: "power2.out" }}, {cue_end(n, "electronics", off=0.1)});
        grow("#f03-res", {cue_end(n, "electronics", off=0.35)}, 0.7);
"""
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 04 compare
n = 4
def blk(id_, x, y, name, sub, inverse=False, w=440):
    bg, fg = (INK, PAPER) if inverse else (PAPER, INK)
    return f"""        <div class="abs" id="{id_}" style="left:{x}px;top:{y}px;width:{w}px;height:190px;border:2px solid {INK};background:{bg};color:{fg};padding:30px 34px;box-sizing:border-box">
          <div class="serif" style="font-size:64px;line-height:1">{name}</div>
          <div class="label" style="font-size:20px;margin-top:20px">{sub}</div>
        </div>
"""
stage = f"""
        <div class="abs serif" id="f04-h" style="left:90px;top:220px;font-size:110px;line-height:1;width:900px">Not just one field</div>
        <svg viewBox="0 0 1080 1920">{path("M310 740 V880", "draw f04-l1")}{path("M770 740 V880", "draw f04-l2")}{path("M540 1070 V1200", "draw f04-l3")}</svg>
{blk("f04-mech", 90, 550, "Mechanical", "MOVING PARTS")}{blk("f04-elec", 550, 550, "Electrical", "CIRCUITS · POWER")}{blk("f04-soft", 270, 1200, "Software", "CODE", w=540)}{blk("f04-mt", 170, 880, "Mechatronics", "CONNECTS ALL THREE", True, w=740)}
"""
t_c = cue(n, "connects")
js = f"""
        pop("#f04-h", 0.15);
        grow("#f04-mech", {cue(n, "mechanical")}); grow("#f04-elec", {cue(n, "electrical")}); grow("#f04-soft", {cue(n, "software")});
        grow("#f04-mt", {cue(n, "mechatronics")}, 0.7);
        draw(".f04-l1", {t_c}, 0.5); draw(".f04-l2", {t_c + 0.2}, 0.5); draw(".f04-l3", {t_c + 0.4}, 0.5);
"""
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 05 loop
n = 5
def lblock(id_, y, name, verb):
    return f"""        <div class="abs" id="{id_}" style="left:150px;top:{y}px;width:640px;height:210px;border:2px solid {INK};background:{PAPER};padding:34px 40px;box-sizing:border-box">
          <div class="serif" style="font-size:76px;line-height:1">{name}</div>
          <div class="label" style="font-size:22px;margin-top:24px">{verb}</div>
        </div>
"""
stage = f"""
        <div class="abs serif" id="f05-h" style="left:90px;top:200px;font-size:120px;line-height:1">One loop</div>
        <div class="abs mono" id="f05-sub" style="left:94px;top:345px;font-size:30px">SENSE → THINK → ACT</div>
        <svg viewBox="0 0 1080 1920">
          {path("M470 670 V800 M454 780 L470 800 L486 780", "draw f05-a1")}
          {path("M470 1010 V1140 M454 1120 L470 1140 L486 1120", "draw f05-a2")}
          {path("M790 1245 H950 V565 H812 M832 549 L812 565 L832 581", "draw f05-fb")}
        </svg>
{lblock("f05-s", 460, "Sensors", "MEASURE")}{lblock("f05-c", 800, "Controller", "DECIDE")}{lblock("f05-a", 1140, "Actuators", "MOVE")}
        <div class="abs label" id="f05-fbl" style="left:968px;top:820px;font-size:22px;writing-mode:vertical-rl">FEEDBACK</div>
        <div class="abs" id="f05-pulse" style="left:778px;top:1233px;width:26px;height:26px;background:{INK}"></div>
"""
t_fb = cue(n, "sensors", 2)
t_again = cue(n, "again")
pts = [(778, 1233), (938, 1233), (938, 553), (778, 553)]
loop_js = ""
t = t_again
for lap in range(2):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d = abs(x1 - x0) / 1200 + abs(y1 - y0) / 1200 + 0.12
        loop_js += f'        tl.fromTo(q("#f05-pulse"), {{ x: {x0-778}, y: {y0-1233} }}, {{ x: {x1-778}, y: {y1-1233}, duration: {d:.2f}, ease: "none", immediateRender: false }}, {t:.2f});\n'
        t += d
js = f"""
        pop("#f05-h", 0.15); fade("#f05-sub", 0.5);
        grow("#f05-s", {cue(n, "sensors")}); draw(".f05-a1", {cue(n, "controller", off=-0.2)}, 0.4);
        grow("#f05-c", {cue(n, "controller")}); draw(".f05-a2", {cue(n, "actuators", off=-0.2)}, 0.4);
        grow("#f05-a", {cue(n, "actuators")});
        draw(".f05-fb", {t_fb}, 1.2); fade("#f05-fbl", {t_fb + 0.6});
        fade("#f05-pulse", {t_again - 0.2}, 0.2);
{loop_js}"""
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 06 example
n = 6
path_pts = "M200 380 H880 V500 H200 V620 H880 V740 H200 V860"
stage = f"""
        <div class="abs label" id="f06-k" style="left:90px;top:200px;font-size:26px">EXAMPLE · ROBOT VACUUM</div>
        <svg viewBox="0 0 1080 1920">
          {path(rect_d(90, 260, 900, 700), "draw f06-room")}
          <path class="f06-plan" d="{path_pts}" fill="none" stroke="{SOFT}" stroke-width="3" stroke-dasharray="14 12" pathLength="1000" />
          <g id="f06-dirt" fill="{INK}">
            <rect x="520" y="480" width="14" height="14"/><rect x="560" y="520" width="12" height="12"/><rect x="330" y="720" width="14" height="14"/>
            <rect x="760" y="600" width="12" height="12"/><rect x="800" y="840" width="14" height="14"/>
          </g>
        </svg>
        <div class="abs" id="f06-bot" style="left:136px;top:316px;width:128px;height:128px">
          <svg viewBox="0 0 128 128" style="width:128px;height:128px">
            <circle cx="64" cy="64" r="58" fill="{PAPER}" stroke="{INK}" stroke-width="4"/>
            <path d="M18 40 A58 58 0 0 1 110 40" fill="none" stroke="{INK}" stroke-width="10"/>
            <rect x="52" y="56" width="24" height="24" fill="{INK}"/>
          </svg>
        </div>
"""
rows = [("f06-r1", "Sense", "BUMPER · DIRT SENSOR", "sensors"), ("f06-r2", "Think", "CHIP PLANS A PATH", "chip"), ("f06-r3", "Act", "MOTORS · WHEELS · BRUSHES", "motors")]
for i, (rid, name, sub, _) in enumerate(rows):
    stage += f"""        <div class="abs" id="{rid}" style="left:90px;top:{1010 + i*190}px;width:900px;border-top:2px solid {INK};padding-top:16px;display:flex;align-items:baseline;gap:34px">
          <div class="mono" style="font-size:24px">0{i+1}</div>
          <div class="serif" style="font-size:84px;line-height:1;width:300px">{name}</div>
          <div class="label" style="font-size:20px">{sub}</div>
        </div>
"""
t_m, t_end = cue(n, "motors"), cue(n, "sense")
segs = [(200, 380), (880, 380), (880, 500), (200, 500), (200, 620), (880, 620), (880, 740), (200, 740), (200, 860)]
total_len = sum(abs(b[0]-a[0]) + abs(b[1]-a[1]) for a, b in zip(segs, segs[1:]))
travel = max(4.0, (cue(n, "many") - t_m) + 2.5)
mv, t = "", t_m
for (x0, y0), (x1, y1) in zip(segs, segs[1:]):
    d = (abs(x1-x0) + abs(y1-y0)) / total_len * travel
    mv += f'        tl.fromTo(q("#f06-bot"), {{ x: {x0-200}, y: {y0-380} }}, {{ x: {x1-200}, y: {y1-380}, duration: {d:.2f}, ease: "none", immediateRender: false }}, {t:.2f});\n'
    t += d
js = f"""
        pop("#f06-k", 0.1); draw(".f06-room", 0.2, 1.0); grow("#f06-bot", {cue(n, "robot")});
        pop("#f06-r1", {cue(n, "sensors")}); fade("#f06-dirt", {cue(n, "dirt")});
        pop("#f06-r2", {cue(n, "chip")});
        tl.fromTo(q(".f06-plan"), {{ strokeDashoffset: 1000, opacity: 0 }}, {{ strokeDashoffset: 0, opacity: 1, duration: 1.4, ease: "power1.inOut" }}, {cue(n, "path")});
        pop("#f06-r3", {t_m});
{mv}        tl.fromTo(q("#f06-r1"), {{ x: 0 }}, {{ x: 18, duration: 0.25, ease: "power2.out" }}, {t_end});
        tl.fromTo(q("#f06-r2"), {{ x: 0 }}, {{ x: 18, duration: 0.25, ease: "power2.out" }}, {cue(n, "think")});
        tl.fromTo(q("#f06-r3"), {{ x: 0 }}, {{ x: 18, duration: 0.25, ease: "power2.out" }}, {cue(n, "act")});
"""
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 07 / 08 ledgers
def ledger(n, fs, title, tag, rows, start_no):
    st = f"""
        <div class="abs serif" id="{fs}-h" style="left:90px;top:190px;font-size:120px;line-height:1">{title}</div>
        <div class="abs label" id="{fs}-tag" style="left:94px;top:330px;font-size:26px">{tag}</div>
        <div class="abs" id="{fs}-rule" style="left:90px;top:385px;width:900px;height:3px;background:{INK}"></div>
"""
    for i, (name, desc, _) in enumerate(rows):
        st += f"""        <div class="abs" id="{fs}-row{i}" style="left:90px;top:{410 + i*190}px;width:900px;height:175px;border-bottom:1px solid {FAINT};box-sizing:border-box;padding-top:24px">
          <div style="display:flex;align-items:baseline;gap:26px"><div class="mono" style="font-size:26px;width:50px">{start_no + i:02d}</div>
          <div class="serif" style="font-size:66px;line-height:1">{name}</div></div>
          <div style="font-size:32px;line-height:1.3;margin:14px 0 0 76px">{desc}</div>
        </div>
"""
    cells = "".join(f'<div class="{fs}-cell" style="width:80px;height:44px;margin-right:10px;background:{GRIDC}"></div>' for _ in range(len(rows) * 2))
    st += f"""        <div class="abs" id="{fs}-bar" style="left:90px;top:1400px;display:flex">{cells}</div>
"""
    js = f"""        pop("#{fs}-h", 0.1); fade("#{fs}-tag", 0.4);
        tl.fromTo(q("#{fs}-rule"), {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.7, ease: "power2.out" }}, 0.3);
"""
    for i, (_, _, word) in enumerate(rows):
        t = cue(n, word)
        js += f'        tl.fromTo(q("#{fs}-row{i}"), {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {t});\n'
        js += f'        tl.to(q(".{fs}-cell:nth-child({2*i+1}), .{fs}-cell:nth-child({2*i+2})"), {{ backgroundColor: "{INK}", duration: 0.25, stagger: 0.08 }}, {t + 0.1});\n'
    return st, js


n = 7
stage, js = ledger(n, "f07", "Years 1–2", "FOUNDATION", [
    ("Calculus & Physics", "The language of motion and force", "calculus"),
    ("Mechanics of Materials", "How parts bend, twist and break", "mechanics"),
    ("Electric Circuits", "Current, voltage and power", "electric"),
    ("Programming", "Logic that runs machines", "programming"),
    ("Computer-Aided Design", "Model every part in 3D", "computer")], 1)
out[n] = ("", stage, js)

n = 8
stage, js = ledger(n, "f08", "Years 3–4", "INTEGRATION", [
    ("Control Systems", "Keep a machine on target", "control"),
    ("Sensors & Actuators", "Measure the world, move in it", "sensors"),
    ("Embedded Systems", "Microcontrollers inside products", "microcontrollers"),
    ("PLC & Automation", "Run factory lines", "plcs"),
    ("Robotics", "Bring it all together", "robotics")], 6)
t_cap = cue(n, "capstone")
stage += f"""        <div class="abs" id="f08-cap" data-layout-allow-overlap data-layout-allow-occlusion style="left:90px;top:620px;width:900px;height:460px;background:{INK};color:{PAPER};padding:56px 60px;box-sizing:border-box">
          <div class="label" style="font-size:24px">FINAL YEAR</div>
          <div class="serif" style="font-size:132px;line-height:0.98;margin-top:30px">Capstone project</div>
          <div class="mono" id="f08-team" style="font-size:28px;margin-top:34px">TEAM BUILD · WORKING MACHINE</div>
        </div>
"""
js += f"""        tl.to(q("[id^=f08-row]"), {{ opacity: 0.18, duration: 0.5 }}, {t_cap - 0.1}); tl.to(q("#f08-bar"), {{ opacity: 0, duration: 0.4 }}, {t_cap - 0.1});
        grow("#f08-cap", {t_cap}, 0.7); fade("#f08-team", {cue(n, "team")});
"""
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 09 skills
n = 9
icons = [
    path(gear_d(220, 520, 100, 76, 10) + circle_d(220, 520, 30), "draw f09-i0"),
    path("M130 820 H230 V900 H310 M230 900 V960 H170 M310 900 V960 H330" + rect_d(114, 804, 32, 32) + rect_d(314, 944, 32, 32) + rect_d(154, 944, 32, 32), "draw f09-i1"),
    path("M180 1160 L120 1240 L180 1320 M280 1160 L340 1240 L280 1320 M250 1150 L210 1330", "draw f09-i2"),
]
stage = f"""
        <div class="abs label" id="f09-k" style="left:90px;top:230px;font-size:28px">YOU LEARN TO</div>
        <svg viewBox="0 0 1080 1920">{''.join(icons)}{path("M90 1420 V1460 H990 V1420", "draw f09-br")}</svg>
"""
cols = [("Design", "THE MECHANISM", 420, "design"), ("Wire", "THE ELECTRONICS", 810, "wire"), ("Code", "THE SOFTWARE", 1180, "write")]
for i, (name, sub, y, _) in enumerate(cols):
    stage += f"""        <div class="abs" id="f09-c{i}" style="left:420px;top:{y}px;width:600px">
          <div class="serif" style="font-size:150px;line-height:1">{name}</div>
          <div class="label" style="font-size:24px;margin-top:14px">{sub}</div>
        </div>
"""
stage += f"""        <div class="abs mono" id="f09-one" style="left:0;width:1080px;text-align:center;top:1485px;font-size:30px">ONE ENGINEER · THE WHOLE SYSTEM</div>
"""
js = f"""        pop("#f09-k", 0.1);
"""
for i, (_, _, _, word) in enumerate(cols):
    t = cue(n, word)
    js += f'        draw(".f09-i{i}", {t}, 0.9); pop("#f09-c{i}", {t + 0.15});\n'
js += f'        draw(".f09-br", {cue(n, "life", off=-0.4)}, 0.8); fade("#f09-one", {cue(n, "life")});\n'
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 10 careers
n = 10
stage = f"""
        <div class="abs serif" id="f10-h" style="left:90px;top:190px;font-size:120px;line-height:1">Where it leads</div>
        <div class="abs label" id="f10-k1" style="left:94px;top:350px;font-size:24px">ROLES</div>
        <div class="abs label" id="f10-k2" style="left:94px;top:850px;font-size:24px">INDUSTRIES</div>
"""
roles = [("Robotics Engineer", "robotics"), ("Automation & Control Engineer", "automation"), ("Embedded Systems Engineer", "embedded")]
for i, (name, _) in enumerate(roles):
    stage += f"""        <div class="abs" id="f10-r{i}" style="left:90px;top:{395 + i*140}px;width:900px;border-top:2px solid {INK};padding-top:20px;display:flex;gap:28px;align-items:baseline">
          <div class="mono" style="font-size:24px">0{i+1}</div><div class="serif" style="font-size:58px;line-height:1.05">{name}</div>
        </div>
"""
inds = [("Electric vehicles", "electric"), ("Aerospace", "aerospace"), ("Medical devices", "medical"), ("Smart factories", "smart")]
for i, (name, _) in enumerate(inds):
    x, y = 90 + (i % 2) * 460, 900 + (i // 2) * 330
    stage += f"""        <div class="abs" id="f10-t{i}" style="left:{x}px;top:{y}px;width:440px;height:310px;border:2px solid {INK};background:{PAPER};box-sizing:border-box">
          <div class="abs" style="left:30px;top:30px;width:32px;height:32px;background:{INK}"></div>
          <div class="serif abs" style="left:30px;bottom:28px;font-size:60px;line-height:1.02;width:380px">{name}</div>
        </div>
"""
js = f"""        pop("#f10-h", 0.1); fade("#f10-k1", 0.5); fade("#f10-k2", 0.6);
"""
for i, (_, w) in enumerate(roles):
    js += f'        tl.fromTo(q("#f10-r{i}"), {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {cue(n, w)});\n'
for i, (_, w) in enumerate(inds):
    js += f'        grow("#f10-t{i}", {cue(n, w)});\n'
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 11 why now
n = 11
stage = f"""
        <div class="abs serif" id="f11-h" style="left:90px;top:190px;font-size:130px;line-height:1">Demand <span class="mono" style="font-size:110px">↑</span></div>
        <svg viewBox="0 0 1080 1920">
          {path("M300 940 C300 1030 540 1020 540 1100", "draw f11-a0")}
          {path("M540 940 V1100", "draw f11-a1")}
          {path("M780 940 C780 1030 540 1020 540 1100 M524 1080 L540 1100 L556 1080", "draw f11-a2")}
        </svg>
        <div class="abs" id="f11-goal" style="left:90px;top:1110px;width:900px;height:300px;background:{INK};color:{PAPER};padding:46px 56px;box-sizing:border-box">
          <div class="label" style="font-size:22px">ALL OF THEM NEED</div>
          <div class="serif" style="font-size:90px;line-height:1;margin-top:24px">Whole-system engineers</div>
        </div>
"""
trends = [("Factory automation", "factories"), ("Cars → computers on wheels", "cars"), ("Smarter products", "product")]
for i, (name, _) in enumerate(trends):
    stage += f"""        <div class="abs" id="f11-r{i}" style="left:90px;top:{390 + i*170}px;width:900px;height:130px;border-bottom:1px solid {FAINT};display:flex;align-items:center;justify-content:space-between">
          <div class="serif" style="font-size:60px">{name}</div><div class="mono" style="font-size:56px">↑</div>
        </div>
"""
js = f"""        pop("#f11-h", 0.1);
"""
for i, (_, w) in enumerate(trends):
    js += f'        tl.fromTo(q("#f11-r{i}"), {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {cue(n, w)});\n'
t_w = cue(n, "whole")
js += f'        draw(".f11-a0", {t_w - 0.6}, 0.6); draw(".f11-a1", {t_w - 0.5}, 0.6); draw(".f11-a2", {t_w - 0.4}, 0.6); grow("#f11-goal", {t_w}, 0.7);\n'
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 12 fit
n = 12
stage = f"""
        <div class="abs serif" id="f12-h" style="left:90px;top:190px;font-size:120px;line-height:1">Is it for you?</div>
        <svg viewBox="0 0 1080 1920">
"""
checks = [("Math & physics", "math"), ("Taking things apart", "apart"), ("Code that moves something", "code")]
for i in range(3):
    y = 400 + i * 150
    stage += f'          <rect x="90" y="{y}" width="76" height="76" fill="none" stroke="{INK}" stroke-width="3" id="f12-box{i}"/>\n'
    stage += "          " + path(f"M106 {y+40} L126 {y+60} L152 {y+18}", f"draw f12-tick{i}", 'style="stroke-dasharray:1;stroke-width:7"') + "\n"
stage += "        </svg>\n"
for i, (name, _) in enumerate(checks):
    stage += f'        <div class="abs serif" id="f12-c{i}" style="left:200px;top:{396 + i*150}px;font-size:62px;line-height:1.25">{name}</div>\n'
stack = ["Software", "Electrical", "Mechanical"]
for i, name in enumerate(stack):
    stage += f"""        <div class="abs f12-st" id="f12-s{i}" style="left:190px;top:{950 + i*140}px;width:700px;height:128px;border:2px solid {INK};background:{PAPER};display:flex;align-items:center;padding-left:40px;box-sizing:border-box">
          <div class="serif" style="font-size:62px">{name}</div>
        </div>
"""
stage += f'        <div class="abs label" id="f12-bd" style="left:0;top:1395px;width:1080px;text-align:center;font-size:28px">BROAD · DEMANDING</div>\n'
js = f"""        pop("#f12-h", 0.1);
"""
for i, (_, w) in enumerate(checks):
    t = cue(n, w)
    js += f'        fade("#f12-box{i}", {t - 0.3}, 0.3); pop("#f12-c{i}", {t - 0.2}); draw(".f12-tick{i}", {t + 0.2}, 0.4);\n'
t_b = cue(n, "broad")
for i in range(3):
    js += f'        tl.fromTo(q("#f12-s{2-i}"), {{ opacity: 0, y: -140 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "bounce.out" }}, {t_b - 0.4 + i*0.35:.2f});\n'
js += f'        pop("#f12-bd", {cue(n, "demanding")});\n'
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 13 close
n = 13
glitch = "".join(f'<div style="height:{h}px;width:{w}px;margin-top:6px;background:repeating-linear-gradient(90deg,{INK} 0 2px,transparent 2px 8px)"></div>'
                 for h, w in [(50, 160), (40, 260), (60, 120), (44, 320), (40, 200), (56, 90)])
stage = f"""
        <svg viewBox="0 0 1080 1920">
          {path(rect_d(90, 230, 250, 100) + rect_d(415, 230, 250, 100) + rect_d(740, 230, 250, 100) + " M340 280 H415 M665 280 H740", "draw f13-loop")}
        </svg>
        <div class="abs mono" id="f13-lt" style="left:90px;top:264px;width:900px;display:flex;justify-content:space-between;font-size:26px">
          <span style="width:250px;text-align:center">SENSE</span><span style="width:250px;text-align:center">THINK</span><span style="width:250px;text-align:center">ACT</span>
        </div>
        <div class="abs label" id="f13-k" style="left:90px;top:470px;font-size:28px">MECHATRONICS — YOUR MAJOR?</div>
        <div class="abs serif" style="left:84px;top:530px;font-size:220px;line-height:1.0;letter-spacing:-0.005em">
          <div id="f13-w0">Sense.</div><div id="f13-w1">Think.</div><div id="f13-w2">Move.</div>
        </div>
        <div class="abs" id="f13-gl" style="left:90px;top:1250px;width:400px">{glitch}</div>
"""
js = f"""        tl.fromTo(q("#f13-gl"), {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.8, ease: "power2.out" }}, 0.1);
        draw(".f13-loop", 0.2, 1.0); fade("#f13-lt", 0.7);
        pop("#f13-w0", {cue(n, "sense")}); pop("#f13-w1", {cue(n, "think")}); pop("#f13-w2", {cue(n, "move")});
        pop("#f13-k", {cue(n, "major", off=-0.6)});
"""
out[n] = ("", stage, js)

# ---------------------------------------------------------------- write
os.makedirs("compositions/frames", exist_ok=True)
for n, dur, src in FRAMES:
    fid = os.path.splitext(os.path.basename(src))[0]
    css, stage, js = out[n]
    css = css.replace("#02-concept-stage", f"#s{fid}-stage")
    stage = stage.replace("#{'02-concept'}", f"#{fid}")
    js = js.replace("#03-origin-stage", f"#s{fid}-stage")
    html = shell(fid, n, dur, css, stage, js, final=(n == len(FRAMES)))
    open(src, "w").write(html)
    print(f"  {src}  ({dur}s)")
