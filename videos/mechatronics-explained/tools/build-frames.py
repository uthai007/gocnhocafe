#!/usr/bin/env python3
"""Build all 13 frame sub-compositions (compositions/frames/NN-*.html) for "Mechatronics Explained".

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
  <div id="root" data-composition-id="{fid}" data-start="0" data-duration="{dur}" data-width="1920" data-height="1080">
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
      #{p}-ground .hl {{ position: absolute; left: 77px; right: 77px; height: 2px; background: {INK}; }}
      #{p}-ground .chrome {{ position: absolute; top: 20px; font-family: "DM Mono", monospace; font-size: 16px;
        letter-spacing: 0.08em; color: {INK}; }}
      #{p}-stage {{ position: absolute; inset: 0; }}
      #{p}-stage .serif {{ font-family: "Newsreader", serif; font-weight: 400; }}
      #{p}-stage .mono {{ font-family: "DM Mono", monospace; letter-spacing: 0.06em; }}
      #{p}-stage .label {{ font-family: "Hanken Grotesk", sans-serif; font-weight: 600; text-transform: uppercase; letter-spacing: 0.16em; }}
      #{p}-stage .abs {{ position: absolute; display: block; }}
      #{p}-stage svg {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: visible; }}
      #{p}-stage .draw {{ fill: none; stroke: {INK}; stroke-width: 4; stroke-linecap: square; stroke-linejoin: miter; }}
{css}
    </style>
    <div id="{p}-ground" class="clip" data-start="0" data-duration="{dur}" data-track-index="0">
      <div class="hl" style="top: 56px"></div>
      <div class="hl" style="top: 1022px"></div>
      <div class="chrome" style="left: 77px">MECHATRONICS — EXPLAINED</div>
      <div class="chrome" style="right: 77px">{n:02d} / {TOTAL_FRAMES:02d}</div>
    </div>
    <div id="{p}-stage" class="clip" data-start="0" data-duration="{dur}" data-track-index="1">
      <div id="{p}-cam" class="abs" style="left:0;top:0;width:1920px;height:1080px">
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

# ---------------------------------------------------------------- 01 hook
n = 1
stage = f"""
        <svg viewBox="0 0 1920 1080">
          <g id="f01-arm">
            {path(rect_d(250, 640, 180, 50), "draw a1")}
            {path("M340 640 L340 500 L500 400 L620 450", "draw a2")}
            {path("M620 450 L668 424 M620 450 L662 494", "draw a3")}
            {path(rect_d(326, 486, 28, 28) + rect_d(486, 386, 28, 28), "draw a4")}
          </g>
          <g id="f01-car">
            {path("M790 650 L810 585 L890 530 L1050 530 L1120 585 L1170 595 L1170 650 Z", "draw c1")}
            {path("M905 545 L1040 545 L1085 585 L880 585 Z", "draw c2")}
            {path(circle_d(880, 655, 36) + circle_d(1090, 655, 36), "draw c3")}
            {path(rect_d(955, 500, 44, 24) + " M948 488 Q977 470 1006 488 M938 476 Q977 450 1016 476", "draw c4")}
          </g>
          <g id="f01-washer">
            {path(rect_d(1360, 410, 300, 300), "draw w1")}
            {path("M1360 470 H1660", "draw w2")}
            {path(circle_d(1510, 595, 92) + circle_d(1510, 595, 62), "draw w3")}
            {path(rect_d(1390, 430, 22, 22) + rect_d(1430, 430, 22, 22), "draw w4")}
          </g>
        </svg>
        <div class="abs label" style="left:250px;top:730px;font-size:18px" id="f01-t1">ROBOT ARM</div>
        <div class="abs label" style="left:790px;top:730px;font-size:18px" id="f01-t2">SELF-DRIVING CAR</div>
        <div class="abs label" style="left:1360px;top:730px;font-size:18px" id="f01-t3">WASHING MACHINE</div>
        <div class="abs serif" id="f01-q" style="left:0;width:1920px;top:110px;text-align:center;font-size:260px;line-height:1">?</div>
        <div class="abs mono" id="f01-tag" style="left:0;width:1920px;top:810px;text-align:center;font-size:22px">WHAT DO THEY SHARE?</div>
"""
t_arm, t_car, t_wash, t_q = cue(n, "robot", off=-0.1), cue(n, "self"), cue(n, "washing"), cue(n, "what")
js = f"""
        draw(".a1", {t_arm}, 0.5); draw(".a2", {t_arm + 0.25}, 0.8); draw(".a3", {t_arm + 0.8}, 0.4); draw(".a4", {t_arm + 0.9}, 0.4);
        fade("#f01-t1", {t_arm + 0.5});
        draw(".c1", {t_car}, 0.8); draw(".c2", {t_car + 0.4}, 0.5); draw(".c3", {t_car + 0.6}, 0.5); draw(".c4", {t_car + 0.9}, 0.5);
        fade("#f01-t2", {t_car + 0.6});
        draw(".w1", {t_wash}, 0.7); draw(".w2", {t_wash + 0.3}, 0.3); draw(".w3", {t_wash + 0.4}, 0.7); draw(".w4", {t_wash + 0.7}, 0.3);
        fade("#f01-t3", {t_wash + 0.6});
        tl.to(q("svg"), {{ opacity: 0.28, duration: 0.5, ease: "power1.out" }}, {t_q});
        tl.to(q("#f01-t1, #f01-t2, #f01-t3"), {{ opacity: 0.35, duration: 0.5 }}, {t_q});
        grow("#f01-q", {t_q + 0.1}, 0.7);
        pop("#f01-tag", {cue(n, "common")});
"""
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 02 concept
n = 2
tiles = [("Mechanics", "MOVING PARTS", 0, 0), ("Electronics", "SIGNALS · POWER", 1, 0), ("Computing", "CODE · LOGIC", 0, 1), ("Control", "FEEDBACK", 1, 1)]
tile_html = ""
for i, (name, sub, cx, cy) in enumerate(tiles):
    x, y = 1130 + cx * 300, 290 + cy * 290
    tile_html += f"""        <div class="abs f02-tile" id="f02-tile{i}" style="left:{x}px;top:{y}px;width:280px;height:270px">
          <div class="mono" style="font-size:16px">0{i+1}</div>
          <div class="serif" style="font-size:42px;margin-top:104px">{name}</div>
          <div class="label" style="font-size:15px;margin-top:10px">{sub}</div>
        </div>
"""
css = f"""      #{'02-concept'}-stage .f02-tile {{ border: 2px solid {INK}; background: {PAPER}; padding: 22px 24px; box-sizing: border-box; }}"""
stage = f"""
        <div class="abs label" id="f02-kicker" style="left:120px;top:250px;font-size:20px">THE MAJOR</div>
        <div class="abs serif" id="f02-title" style="left:112px;top:300px;font-size:150px;line-height:0.95;letter-spacing:-0.01em">Mechatronics</div>
        <div class="abs serif" id="f02-callout" style="left:120px;top:500px;font-size:46px;font-style:italic;color:{SOFT};width:880px">the engineering of smart machines</div>
{tile_html}        <svg viewBox="0 0 1920 1080">{path(rect_d(1110, 270, 620, 600), "draw f02-unite")}</svg>
        <div class="abs mono" id="f02-one" style="left:1110px;top:885px;width:620px;text-align:center;font-size:18px">ONE DESIGN</div>
"""
js = f"""
        pop("#f02-kicker", 0.15); pop("#f02-title", 0.25, 0.7);
        tl.fromTo(q("#f02-callout"), {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }}, {cue(n, "engineering")});
        grow("#f02-tile0", {cue(n, "mechanics,")}); grow("#f02-tile1", {cue(n, "electronics")});
        grow("#f02-tile2", {cue(n, "computing")}); grow("#f02-tile3", {cue(n, "control")});
        draw(".f02-unite", {cue(n, "together")}, 1.0);
        fade("#f02-one", {cue(n, "design")});
"""
out[n] = (css.replace("#02-concept", "#02-concept"), stage, js)

# ---------------------------------------------------------------- 03 origin
n = 3
stage = f"""
        <div class="abs label" id="f03-k" style="left:120px;top:190px;font-size:20px">WHERE THE WORD CAME FROM</div>
        <div class="abs serif" id="f03-year" style="left:108px;top:230px;font-size:260px;line-height:0.9;letter-spacing:-0.015em">1969</div>
        <div class="abs mono" id="f03-japan" style="left:120px;top:500px;font-size:24px">JAPAN</div>
        <div class="abs mono" id="f03-who" style="left:120px;top:545px;font-size:24px">TETSURO MORI · YASKAWA ELECTRIC</div>
        <div class="abs serif" id="f03-r1" style="left:1060px;top:250px;font-size:96px"><span>Mecha</span><span style="opacity:0.28">nics</span></div>
        <div class="abs serif" id="f03-plus" style="left:1060px;top:360px;font-size:80px">+</div>
        <div class="abs serif" id="f03-r2" style="left:1060px;top:450px;font-size:96px"><span style="opacity:0.28">Elec</span><span>tronics</span></div>
        <div class="abs" id="f03-rule" style="left:1060px;top:600px;width:660px;height:3px;background:{INK}"></div>
        <div class="abs serif" id="f03-res" style="left:1060px;top:630px;font-size:118px;letter-spacing:-0.01em">Mechatronics</div>
"""
t_year = cue(n, "1969")
js = f"""
        pop("#f03-k", 0.1);
        const yr = {{ v: 1900 }};
        const yel = document.querySelector("#{'03-origin'}-stage #f03-year");
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
def blk(id_, x, y, name, sub, inverse=False):
    bg, fg = (INK, PAPER) if inverse else (PAPER, INK)
    return f"""        <div class="abs" id="{id_}" style="left:{x}px;top:{y}px;width:420px;height:160px;border:2px solid {INK};background:{bg};color:{fg};padding:26px 30px;box-sizing:border-box">
          <div class="serif" style="font-size:54px;line-height:1">{name}</div>
          <div class="label" style="font-size:16px;margin-top:16px">{sub}</div>
        </div>
"""
stage = f"""
        <div class="abs serif" id="f04-h" style="left:120px;top:110px;font-size:84px;line-height:1">Not just one field</div>
        <svg viewBox="0 0 1920 1080">{path("M750 505 H600", "draw f04-l1")}{path("M1170 505 H1320", "draw f04-l2")}{path("M960 585 V690", "draw f04-l3")}</svg>
{blk("f04-mech", 180, 425, "Mechanical", "MOVING PARTS")}{blk("f04-elec", 1320, 425, "Electrical", "CIRCUITS · POWER")}{blk("f04-soft", 750, 690, "Software", "CODE")}{blk("f04-mt", 750, 425, "Mechatronics", "CONNECTS ALL THREE", True)}
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
def lblock(id_, x, name, verb):
    return f"""        <div class="abs" id="{id_}" style="left:{x}px;top:380px;width:400px;height:200px;border:2px solid {INK};background:{PAPER};padding:30px 32px;box-sizing:border-box">
          <div class="serif" style="font-size:60px;line-height:1">{name}</div>
          <div class="label" style="font-size:17px;margin-top:22px">{verb}</div>
        </div>
"""
stage = f"""
        <div class="abs serif" id="f05-h" style="left:120px;top:110px;font-size:96px;line-height:1">One loop</div>
        <div class="abs mono" id="f05-sub" style="left:124px;top:230px;font-size:22px">SENSE → THINK → ACT</div>
        <svg viewBox="0 0 1920 1080">
          {path("M600 480 H748 M728 466 L748 480 L728 494", "draw f05-a1")}
          {path("M1160 480 H1308 M1288 466 L1308 480 L1288 494", "draw f05-a2")}
          {path("M1520 580 V760 H400 V600 M386 620 L400 600 L414 620", "draw f05-fb")}
        </svg>
{lblock("f05-s", 200, "Sensors", "MEASURE")}{lblock("f05-c", 760, "Controller", "DECIDE")}{lblock("f05-a", 1320, "Actuators", "MOVE")}
        <div class="abs label" id="f05-fbl" style="left:0;width:1920px;text-align:center;top:780px;font-size:17px">FEEDBACK</div>
        <div class="abs" id="f05-pulse" style="left:388px;top:468px;width:24px;height:24px;background:{INK}"></div>
"""
t_fb = cue(n, "sensors", 2)
t_again = cue(n, "again")
pts = [(388, 468), (1508, 468), (1508, 748), (388, 748), (388, 468)]
loop_js = ""
t = t_again
for lap in range(2):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d = abs(x1 - x0) / 1400 + abs(y1 - y0) / 1400 + 0.12
        loop_js += f'        tl.fromTo(q("#f05-pulse"), {{ x: {x0-388}, y: {y0-468} }}, {{ x: {x1-388}, y: {y1-468}, duration: {d:.2f}, ease: "none", immediateRender: false }}, {t:.2f});\n'
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
path_pts = "M300 300 H1000 V420 H300 V540 H1000 V660 H300 V780"
stage = f"""
        <div class="abs label" id="f06-k" style="left:120px;top:96px;font-size:20px">EXAMPLE · ROBOT VACUUM</div>
        <svg viewBox="0 0 1920 1080">
          {path(rect_d(180, 160, 940, 720), "draw f06-room")}
          <path class="f06-plan" d="{path_pts}" fill="none" stroke="{SOFT}" stroke-width="3" stroke-dasharray="14 12" pathLength="1000" />
          <g id="f06-dirt" fill="{INK}">
            <rect x="620" y="400" width="12" height="12"/><rect x="660" y="430" width="10" height="10"/><rect x="420" y="640" width="12" height="12"/>
            <rect x="860" y="520" width="10" height="10"/><rect x="900" y="760" width="12" height="12"/>
          </g>
        </svg>
        <div class="abs" id="f06-bot" style="left:236px;top:236px;width:128px;height:128px">
          <svg viewBox="0 0 128 128" style="width:128px;height:128px">
            <circle cx="64" cy="64" r="58" fill="{PAPER}" stroke="{INK}" stroke-width="4"/>
            <path d="M18 40 A58 58 0 0 1 110 40" fill="none" stroke="{INK}" stroke-width="10"/>
            <rect x="52" y="56" width="24" height="24" fill="{INK}"/>
          </svg>
        </div>
"""
rows = [("f06-r1", "Sense", "BUMPER · DIRT SENSOR", "sensors"), ("f06-r2", "Think", "CHIP PLANS A PATH", "chip"), ("f06-r3", "Act", "MOTORS · WHEELS · BRUSHES", "motors")]
for i, (rid, name, sub, _) in enumerate(rows):
    stage += f"""        <div class="abs" id="{rid}" style="left:1240px;top:{250 + i*190}px;width:560px;border-top:2px solid {INK};padding-top:18px">
          <div class="mono" style="font-size:16px">0{i+1}</div>
          <div class="serif" style="font-size:72px;line-height:1;margin-top:6px">{name}</div>
          <div class="label" style="font-size:16px;margin-top:12px">{sub}</div>
        </div>
"""
t_m, t_end = cue(n, "motors"), cue(n, "sense")
segs = [(300, 300), (1000, 300), (1000, 420), (300, 420), (300, 540), (1000, 540), (1000, 660), (300, 660), (300, 780)]
total_len = sum(abs(b[0]-a[0]) + abs(b[1]-a[1]) for a, b in zip(segs, segs[1:]))
travel = max(4.0, (cue(n, "many") - t_m) + 2.5)
mv, t = "", t_m
for (x0, y0), (x1, y1) in zip(segs, segs[1:]):
    d = (abs(x1-x0) + abs(y1-y0)) / total_len * travel
    mv += f'        tl.fromTo(q("#f06-bot"), {{ x: {x0-300}, y: {y0-300} }}, {{ x: {x1-300}, y: {y1-300}, duration: {d:.2f}, ease: "none", immediateRender: false }}, {t:.2f});\n'
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
def ledger(n, fid_short, title, tag, rows, start_no):
    st = f"""
        <div class="abs serif" id="{fid_short}-h" style="left:120px;top:96px;font-size:96px;line-height:1">{title}</div>
        <div class="abs label" id="{fid_short}-tag" style="right:120px;top:150px;font-size:20px">{tag}</div>
        <div class="abs" id="{fid_short}-rule" style="left:120px;top:215px;width:1680px;height:3px;background:{INK}"></div>
"""
    for i, (name, desc, _) in enumerate(rows):
        st += f"""        <div class="abs" id="{fid_short}-row{i}" style="left:120px;top:{240 + i*118}px;width:1240px;height:104px;border-bottom:1px solid {FAINT};display:flex;align-items:center;gap:40px">
          <div class="mono" style="font-size:22px;width:60px">{start_no + i:02d}</div>
          <div class="serif" style="font-size:56px;width:640px;line-height:1">{name}</div>
          <div style="font-size:26px;line-height:1.3;color:{INK}">{desc}</div>
        </div>
"""
    cells = ""
    for c in range(len(rows) * 2):
        cells += f'<div class="{fid_short}-cell" style="width:120px;height:44px;margin-top:6px;background:{GRIDC}"></div>'
    st += f"""        <div class="abs" id="{fid_short}-bar" style="left:1560px;top:{240 + 5*118 - (len(rows)*2)*50 + 4}px;width:120px;display:flex;flex-direction:column-reverse">{cells}</div>
        <div class="abs" style="left:1540px;top:{240 + 5*118 + 6}px;width:160px;height:3px;background:{INK}"></div>
"""
    js = f"""        pop("#{fid_short}-h", 0.1); fade("#{fid_short}-tag", 0.4);
        tl.fromTo(q("#{fid_short}-rule"), {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.7, ease: "power2.out" }}, 0.3);
"""
    for i, (_, _, word) in enumerate(rows):
        t = cue(n, word)
        js += f'        tl.fromTo(q("#{fid_short}-row{i}"), {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {t});\n'
        js += f'        tl.to(q(".{fid_short}-cell:nth-child({2*i+1}), .{fid_short}-cell:nth-child({2*i+2})"), {{ backgroundColor: "{INK}", duration: 0.25, stagger: 0.08 }}, {t + 0.1});\n'
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
stage += f"""        <div class="abs" id="f08-cap" data-layout-allow-overlap data-layout-allow-occlusion style="left:980px;top:330px;width:760px;height:330px;background:{INK};color:{PAPER};padding:44px 52px;box-sizing:border-box">
          <div class="label" style="font-size:18px">FINAL YEAR</div>
          <div class="serif" style="font-size:104px;line-height:1;margin-top:26px">Capstone project</div>
          <div class="mono" id="f08-team" style="font-size:22px;margin-top:30px">TEAM BUILD · WORKING MACHINE</div>
        </div>
"""
js += f"""        tl.to(q("[id^=f08-row]"), {{ opacity: 0.22, duration: 0.5 }}, {t_cap - 0.1}); tl.to(q("#f08-bar, #f08-bar + div"), {{ opacity: 0, duration: 0.4 }}, {t_cap - 0.1});
        grow("#f08-cap", {t_cap}, 0.7); fade("#f08-team", {cue(n, "team")});
"""
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 09 skills
n = 9
icons = [
    path(gear_d(330, 360, 92, 70, 10) + circle_d(330, 360, 28), "draw f09-i0"),
    path("M840 300 H940 V380 H1040 M940 380 V440 H880 M1040 380 V440 H1100" + rect_d(824, 284, 32, 32) + rect_d(1084, 424, 32, 32) + rect_d(864, 424, 32, 32), "draw f09-i1"),
    path("M1450 290 L1400 360 L1450 430 M1590 290 L1640 360 L1590 430 M1545 280 L1495 440", "draw f09-i2"),
]
stage = f"""
        <div class="abs label" id="f09-k" style="left:120px;top:110px;font-size:22px">YOU LEARN TO</div>
        <svg viewBox="0 0 1920 1080">{''.join(icons)}{path("M200 760 V800 H1720 V760", "draw f09-br")}</svg>
"""
cols = [("Design", "THE MECHANISM", 160, "design"), ("Wire", "THE ELECTRONICS", 760, "wire"), ("Code", "THE SOFTWARE", 1360, "write")]
for i, (name, sub, x, _) in enumerate(cols):
    stage += f"""        <div class="abs" id="f09-c{i}" style="left:{x}px;top:500px;width:420px;text-align:center">
          <div class="serif" style="font-size:120px;line-height:1">{name}</div>
          <div class="label" style="font-size:18px;margin-top:20px">{sub}</div>
        </div>
"""
stage += f"""        <div class="abs mono" id="f09-one" style="left:0;width:1920px;text-align:center;top:820px;font-size:24px">ONE ENGINEER · THE WHOLE SYSTEM</div>
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
        <div class="abs serif" id="f10-h" style="left:120px;top:96px;font-size:96px;line-height:1">Where it leads</div>
        <div class="abs label" id="f10-k1" style="left:120px;top:250px;font-size:18px">ROLES</div>
        <div class="abs label" id="f10-k2" style="left:1130px;top:250px;font-size:18px">INDUSTRIES</div>
"""
roles = [("Robotics Engineer", "robotics"), ("Automation & Control Engineer", "automation"), ("Embedded Systems Engineer", "embedded")]
for i, (name, _) in enumerate(roles):
    stage += f"""        <div class="abs" id="f10-r{i}" style="left:120px;top:{300 + i*160}px;width:880px;border-top:2px solid {INK};padding-top:20px;display:flex;gap:30px;align-items:baseline">
          <div class="mono" style="font-size:20px">0{i+1}</div><div class="serif" style="font-size:58px;line-height:1.05">{name}</div>
        </div>
"""
inds = [("Electric vehicles", "electric"), ("Aerospace", "aerospace"), ("Medical devices", "medical"), ("Smart factories", "smart")]
for i, (name, _) in enumerate(inds):
    x, y = 1130 + (i % 2) * 330, 300 + (i // 2) * 280
    stage += f"""        <div class="abs" id="f10-t{i}" style="left:{x}px;top:{y}px;width:310px;height:260px;border:2px solid {INK};background:{PAPER};padding:24px;box-sizing:border-box">
          <div class="abs" style="left:24px;top:24px;width:26px;height:26px;background:{INK}"></div>
          <div class="serif abs" style="left:24px;bottom:22px;font-size:46px;line-height:1.02;width:262px">{name}</div>
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
        <div class="abs serif" id="f11-h" style="left:120px;top:96px;font-size:96px;line-height:1">Demand <span class="mono" style="font-size:80px">↑</span></div>
        <svg viewBox="0 0 1920 1080">
          {path("M1000 352 C1150 352 1150 520 1290 520", "draw f11-a0")}
          {path("M1000 522 H1290", "draw f11-a1")}
          {path("M1000 692 C1150 692 1150 520 1290 520 M1270 506 L1290 520 L1270 534", "draw f11-a2")}
        </svg>
        <div class="abs" id="f11-goal" style="left:1300px;top:410px;width:500px;height:220px;background:{INK};color:{PAPER};padding:34px 40px;box-sizing:border-box">
          <div class="label" style="font-size:16px">ALL OF THEM NEED</div>
          <div class="serif" style="font-size:64px;line-height:1;margin-top:18px">Whole-system engineers</div>
        </div>
"""
trends = [("Factory automation", "factories"), ("Cars → computers on wheels", "cars"), ("Smarter products", "product")]
for i, (name, _) in enumerate(trends):
    stage += f"""        <div class="abs" id="f11-r{i}" style="left:120px;top:{300 + i*170}px;width:880px;height:110px;border-bottom:1px solid {FAINT};display:flex;align-items:center;justify-content:space-between">
          <div class="serif" style="font-size:58px">{name}</div><div class="mono" style="font-size:48px">↑</div>
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
        <div class="abs serif" id="f12-h" style="left:120px;top:96px;font-size:96px;line-height:1">Is it for you?</div>
        <svg viewBox="0 0 1920 1080">
"""
checks = [("Math & physics", "math"), ("Taking things apart", "apart"), ("Code that moves something", "code")]
for i in range(3):
    y = 300 + i * 160
    stage += f'          <rect x="120" y="{y}" width="64" height="64" fill="none" stroke="{INK}" stroke-width="3" id="f12-box{i}"/>\n'
    stage += "          " + path(f"M134 {y+34} L150 {y+50} L172 {y+16}", f"draw f12-tick{i}", 'style="stroke-dasharray:1;stroke-width:6"') + "\n"
stage += "        </svg>\n"
for i, (name, _) in enumerate(checks):
    stage += f'        <div class="abs serif" id="f12-c{i}" style="left:220px;top:{296 + i*160}px;font-size:58px;line-height:1.2">{name}</div>\n'
stack = ["Software", "Electrical", "Mechanical"]
for i, name in enumerate(stack):
    stage += f"""        <div class="abs f12-st" id="f12-s{i}" style="left:1220px;top:{330 + i*130}px;width:520px;height:120px;border:2px solid {INK};background:{PAPER};display:flex;align-items:center;padding-left:34px;box-sizing:border-box">
          <div class="serif" style="font-size:52px">{name}</div>
        </div>
"""
stage += f'        <div class="abs label" id="f12-bd" style="left:1220px;top:740px;width:520px;text-align:center;font-size:20px">BROAD · DEMANDING</div>\n'
js = f"""        pop("#f12-h", 0.1);
"""
for i, (_, w) in enumerate(checks):
    t = cue(n, w)
    js += f'        fade("#f12-box{i}", {t - 0.3}, 0.3); pop("#f12-c{i}", {t - 0.2}); draw(".f12-tick{i}", {t + 0.2}, 0.4);\n'
t_b = cue(n, "broad")
for i in range(3):
    js += f'        tl.fromTo(q("#f12-s{2-i}"), {{ opacity: 0, y: -120 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "bounce.out" }}, {t_b - 0.4 + i*0.35:.2f});\n'
js += f'        pop("#f12-bd", {cue(n, "demanding")});\n'
out[n] = ("", stage, js)

# ---------------------------------------------------------------- 13 close
n = 13
glitch = "".join(f'<div style="height:{h}px;width:{w}px;margin-top:6px;background:repeating-linear-gradient(90deg,{INK} 0 2px,transparent 2px 8px)"></div>'
                 for h, w in [(90, 120), (60, 180), (120, 90), (80, 220), (70, 140), (110, 60), (60, 160)])
stage = f"""
        <div class="abs" id="f13-gl" style="left:77px;top:150px;width:240px">{glitch}</div>
        <svg viewBox="0 0 1920 1080">
          {path(rect_d(1080, 160, 180, 80) + rect_d(1330, 160, 180, 80) + rect_d(1580, 160, 180, 80) + " M1260 200 H1330 M1510 200 H1580", "draw f13-loop")}
        </svg>
        <div class="abs mono" id="f13-lt" style="left:1080px;top:186px;width:680px;display:flex;font-size:18px">
          <span style="width:250px;text-align:center;margin-left:-35px">SENSE</span><span style="width:250px;text-align:center">THINK</span><span style="width:250px;text-align:center">ACT</span>
        </div>
        <div class="abs label" id="f13-k" style="right:160px;top:330px;font-size:22px;text-align:right">MECHATRONICS — YOUR MAJOR?</div>
        <div class="abs serif" style="right:150px;top:380px;font-size:150px;line-height:1.02;text-align:right;letter-spacing:-0.005em">
          <span id="f13-w0" style="display:inline-block">Sense.</span> <span id="f13-w1" style="display:inline-block">Think.</span><br><span id="f13-w2" style="display:inline-block">Move.</span>
        </div>
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
