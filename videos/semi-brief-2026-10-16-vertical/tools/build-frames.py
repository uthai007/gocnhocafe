#!/usr/bin/env python3
"""VERTICAL 9:16 (1080x1920, YouTube Shorts) version. Build the 12 scene sub-compositions + the persistent HUD overlay for the semiconductor market update, 16 Oct 2026.

    python3 tools/build-frames.py      # from the project root, after tools/pad-and-time.py + sync-durations

Look: "Neon HUD" (see frame.md) — deep navy ground, glowing cyan circuitry + world map, amber arcs, green gains.
Every figure on screen comes from the brief (capture/extracted/visible-text.txt); reveals are timed to the
narration via cue("word") (frame-relative word start from audio_meta.json).
"""
import json, math, os, re

BG, BG2 = "#030914", "#071531"
CY, CY2, AM, GR, RD = "#38d9ff", "#7fe8ff", "#ffb547", "#3dffa0", "#ff6178"
TXT, MUT = "#e9f7ff", "#8fb6d1"
GLASS = "background: linear-gradient(160deg, rgba(14,40,80,0.72), rgba(6,18,40,0.72)); border: 1.5px solid rgba(56,217,255,0.55); box-shadow: 0 0 28px rgba(56,217,255,0.22), inset 0 0 22px rgba(56,217,255,0.10);"

meta = json.load(open("audio_meta.json"))
WORDS = {v["frame"]: v["words"] for v in meta["voices"]}
sb = open("STORYBOARD.md").read()
FRAMES = []
for m in re.finditer(r"^## Frame (\d+) — .*?$(.*?)(?=^## Frame |\Z)", sb, re.M | re.S):
    body = m.group(2)
    FRAMES.append((int(m.group(1)), float(re.search(r"^- duration: ([\d.]+)s", body, re.M).group(1)), re.search(r"^- src: (\S+)", body, re.M).group(1)))
TOTAL_DUR = sum(d for _, d, _ in FRAMES)

WORLD = json.load(open("data/world.json"))
def rnd(d):
    return re.sub(r"(\d+\.\d)\d+", r"\1", d)
LAND = rnd(WORLD["land"])
CTRY = {k: rnd(v) for k, v in WORLD["countries"].items()}
P = WORLD["points"]


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def cue(n, word, nth=1, off=0.0):
    k = 0
    for w in WORDS[n]:
        if norm(w["text"]).startswith(norm(word)):
            k += 1
            if k == nth:
                return round(max(0.05, w["start"] + off), 3)
    raise KeyError(f"frame {n}: {word!r} #{nth}")


# ---------------------------------------------------------------- shell
def shell(fid, n, dur, stage, js, final=False):
    p = "s" + fid
    # decorative edge circuitry with travelling glow
    traces = ["M0 300 H110 L160 350 H300", "M0 1300 H90 L140 1250 H260", "M1080 240 H960 L910 290 H780",
              "M1080 1180 H990 L940 1130 H820", "M200 1920 V1830 L250 1780 H420", "M880 1920 V1840 L830 1790 H700"]
    tr = "".join(f'<path d="{d}" class="tr"/><path d="{d}" class="trg" pathLength="100"/>' for d in traces)
    return f"""<template id="{p}-template">
  <div id="root" data-composition-id="{fid}" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
    <style>
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; color: {TXT}; font-family: Montserrat, sans-serif; }}
      #{p}-ground {{ position: absolute; inset: 0; background:
          radial-gradient(ellipse 70% 60% at 55% 45%, rgba(20,70,140,0.55) 0%, rgba(3,9,20,0) 70%),
          linear-gradient(180deg, {BG2} 0%, {BG} 100%); }}
      #{p}-ground .grid {{ position: absolute; inset: 0; opacity: 0.35;
          background-image: linear-gradient(rgba(56,217,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(56,217,255,0.08) 1px, transparent 1px);
          background-size: 64px 64px; }}
      #{p}-ground svg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; }}
      #{p}-ground .tr {{ fill: none; stroke: rgba(56,217,255,0.28); stroke-width: 2; }}
      #{p}-ground .trg {{ fill: none; stroke: {CY2}; stroke-width: 4; stroke-dasharray: 6 94; opacity: 0.9; }}
      #{p}-ground .vig {{ position: absolute; inset: 0; background: radial-gradient(ellipse 80% 75% at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.6) 100%); }}
      #{p}-stage {{ position: absolute; inset: 0; }}
      #{p}-stage .abs {{ position: absolute; display: block; }}
      #{p}-stage .glass {{ {GLASS} }}
      #{p}-stage .kick {{ font-family: "JetBrains Mono", monospace; font-size: 20px; letter-spacing: 0.18em; color: {CY}; text-transform: uppercase; }}
      #{p}-stage .h1 {{ font-weight: 800; font-size: 64px; line-height: 1.05; color: {TXT}; text-shadow: 0 0 22px rgba(56,217,255,0.45); }}
      #{p}-stage .big {{ font-family: Oswald, sans-serif; font-weight: 600; line-height: 1; }}
      #{p}-stage .mono {{ font-family: "JetBrains Mono", monospace; }}
      #{p}-stage .g {{ color: {GR}; text-shadow: 0 0 18px rgba(61,255,160,0.55); }}
      #{p}-stage .a {{ color: {AM}; text-shadow: 0 0 18px rgba(255,181,71,0.5); }}
      #{p}-stage .c {{ color: {CY}; text-shadow: 0 0 18px rgba(56,217,255,0.55); }}
      #{p}-stage .mut {{ color: {MUT}; }}
      #{p}-stage svg.full {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }}
      #{p}-stage .land {{ fill: rgba(16,52,104,0.55); stroke: rgba(56,217,255,0.45); stroke-width: 1.2; }}
      #{p}-stage .hi {{ fill: rgba(56,217,255,0.28); stroke: {CY2}; stroke-width: 2; }}
      #{p}-stage .hig {{ fill: none; stroke: rgba(56,217,255,0.22); stroke-width: 12; }}
      #{p}-stage .arc {{ fill: none; stroke: {AM}; stroke-width: 4; }}
      #{p}-stage .ln {{ fill: none; stroke: {CY2}; stroke-width: 3; }}
      #{p}-stage .node {{ fill: {CY2}; }}
      #{p}-stage .halo {{ fill: rgba(56,217,255,0.22); }}
      #{p}-stage .ring {{ fill: none; stroke: {CY}; stroke-width: 2.5; }}
{"" }
    </style>
    <div id="{p}-ground" class="clip" data-start="0" data-duration="{dur}" data-track-index="0">
      <div class="grid"></div>
      <svg viewBox="0 0 1080 1920">{tr}</svg>
      <div class="vig"></div>
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
        const pop = (sel, at, d) => tl.fromTo(q(sel), {{ opacity: 0, y: 26 }}, {{ opacity: 1, y: 0, duration: d || 0.55, ease: "power3.out" }}, at);
        const fade = (sel, at, d) => tl.fromTo(q(sel), {{ opacity: 0 }}, {{ opacity: 1, duration: d || 0.5, ease: "power1.out" }}, at);
        const grow = (sel, at, d) => tl.fromTo(q(sel), {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: d || 0.6, ease: "back.out(1.5)" }}, at);
        const slide = (sel, at, dx) => tl.fromTo(q(sel), {{ opacity: 0, x: dx || 60 }}, {{ opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }}, at);
        const count = (sel, at, from, to, dec, pre, suf, d) => {{
          const el = document.querySelector(q(sel)); const o = {{ v: from }};
          tl.fromTo(o, {{ v: from }}, {{ v: to, duration: d || 1.2, ease: "power2.out", onUpdate: () => {{ el.textContent = pre + o.v.toFixed(dec) + suf; }} }}, at);
        }};
        const pulse = (sel, at) => tl.fromTo(q(sel), {{ scale: 0.4, opacity: 0.9 }}, {{ scale: 2.6, opacity: 0, duration: 1.6, ease: "power1.out", transformOrigin: "50% 50%" }}, at);
        tl.fromTo("#{p}-ground .trg", {{ strokeDashoffset: 100 }}, {{ strokeDashoffset: -100, duration: D, ease: "none" }}, 0);
        tl.fromTo("#{p}-cam", {{ scale: 1 }}, {{ scale: 1.04, duration: D, ease: "none", transformOrigin: "50% 45%" }}, 0);
{js}
{"        tl.to('#" + p + "-cam', { opacity: 0, duration: 0.7, ease: 'power1.in' }, D - 0.8);" if final else ""}
        window.__timelines["{fid}"] = tl;
      }})();
    </script>
  </div>
</template>
"""


EUROPE = [rnd(d) for d in WORLD["europe"]]
EUBOX = WORLD["europeBox"]


def mapsvg(cls_id, highlight=(), viewbox="0 0 1920 1080", extra="", opacity=1.0, europe=False):
    # Highlights are exact areas only: one named country each; Europe = all European countries clipped to
    # Europe's box (lon -25..60, lat 34..72) so French Guiana / Svalbard / Asian Russia stay unlit.
    hi = "".join(f'<path class="hig" d="{CTRY[c]}"/><path class="hi" d="{CTRY[c]}"/>' for c in highlight)
    if europe:
        x, y, w, h = EUBOX
        eu = "".join(f'<path class="hig" d="{d}"/><path class="hi" d="{d}"/>' for d in EUROPE)
        hi += f'<clipPath id="{cls_id}-euclip"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#{cls_id}-euclip)">{eu}</g>'
    return (f'<svg class="full" id="{cls_id}" viewBox="{viewbox}" preserveAspectRatio="xMidYMid slice" style="opacity:{opacity}">'
            f'<path class="land" d="{LAND}"/>{hi}{extra}</svg>')


def node(x, y, nid, r=7):
    return f'<circle class="ring" id="{nid}-r" cx="{x}" cy="{y}" r="{r*2}"/><g id="{nid}"><circle class="halo" cx="{x}" cy="{y}" r="{r*2.6}"/><circle class="node" cx="{x}" cy="{y}" r="{r}"/></g>'


def arc(a, b, aid, lift=0.28):
    (x1, y1), (x2, y2) = a, b
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - abs(x2 - x1) * lift
    return f'<path class="arc" id="{aid}" pathLength="1" style="stroke-dasharray:1" d="M{x1} {y1} Q{mx:.0f} {my:.0f} {x2} {y2}"/>'


def tag(text, x, y, tid, color=CY):
    return f'<div class="abs mono" id="{tid}" style="left:{x}px;top:{y}px;font-size:20px;letter-spacing:0.12em;color:{color};text-shadow:0 0 12px {color}">{text}</div>'


def card(cid, x, y, w, h, inner, extra_style=""):
    return f'<div class="abs glass" id="{cid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;padding:28px 32px;box-sizing:border-box;{extra_style}">{inner}</div>'



def mappanel(pid, vb, top, h, highlight=(), extra="", europe=False, opacity=1.0):
    svg = mapsvg(pid, highlight=highlight, viewbox=vb, extra=extra, opacity=opacity, europe=europe)
    svg = svg.replace(f'style="opacity:{opacity}"', f'style="opacity:{opacity};width:1080px;height:{h}px"')
    return f'<div class="abs" style="left:0;top:{top}px;width:1080px;height:{h}px;overflow:hidden">{svg}</div>'

out = {}
# Vertical 1080x1920. Content lives in y ~110..1350; captions ~1390..1560; ticker 1580..1626; Shorts UI below.
X0, CW = 60, 960  # content left / width

# ---------------------------------------------------------------- 01 open
n = 1
pts = ["Tainan", "Seoul", "Shenzhen", "Dalian", "Johor", "Dresden", "Sunnyvale", "Arizona", "UpstateNY"]
nodes = "".join(node(*P[k], f"o-{k}") for k in pts)
arcs = "".join(arc(P["Tainan"], P[k], f"oa-{k}") for k in ["Seoul", "Johor", "Dresden", "Sunnyvale", "UpstateNY"])
stage = f"""
        {mappanel("o-map", "240 90 1440 1000", 110, 760, extra=arcs + nodes)}
        {card("o-title", X0, 900, CW, 420, f'''<div class="kick" style="font-size:24px">SEMICONDUCTOR MARKET UPDATE</div>
          <div class="h1" style="font-size:96px;margin-top:22px">This week in chips</div>
          <div class="mono c" style="font-size:34px;margin-top:24px">FRI 16 OCT 2026 · SGT</div>''')}
"""
js = '        fade("#o-map", 0.0, 1.2);\n'
for i, k in enumerate(pts):
    js += f'        grow("#o-{k}", {0.3 + i*0.25:.2f}, 0.4); pulse("#o-{k}-r", {0.3 + i*0.25:.2f});\n'
for i, k in enumerate(["Seoul", "Johor", "Dresden", "Sunnyvale", "UpstateNY"]):
    js += f'        draw("#oa-{k}", {cue(n, "moved") - 0.6 + i*0.3:.2f}, 1.2);\n'
js += f'        pop("#o-title", {cue(n, "friday")}, 0.7);\n'
out[n] = (stage, js)

# ---------------------------------------------------------------- 02 headlines
n = 2
cards = [("h-mem", "MEMORY", "Still digesting Tuesday's AI scare", '<span class="a">▼ SENTIMENT</span>', "memory"),
         ("h-tsmc", "TSMC", "Another record quarter", '<span class="g">▲ +50.9% YoY</span>', "tsmc"),
         ("h-amat", "APPLIED MATERIALS", "US$5bn collaborative R&amp;D cleanroom campus", '<span class="c">SUNNYVALE · LAB-TO-FAB</span>', "applied")]
stage = f'        <div class="abs kick" id="h-k" style="left:{X0}px;top:150px;font-size:24px">TOP LINES · THIS WEEK</div>\n'
for i, (cid, k, h, d, _) in enumerate(cards):
    stage += card(cid, X0, 220 + i*380, CW, 340, f'''<div class="kick" style="font-size:24px">{k}</div>
          <div style="font-weight:800;font-size:62px;line-height:1.08;margin-top:26px">{h}</div>
          <div class="mono" style="font-size:30px;position:absolute;left:32px;bottom:30px">{d}</div>''') + "\n"
js = '        fade("#h-k", 0.1);\n' + "".join(f'        pop("#{cid}", {cue(n, w)}, 0.6);\n' for cid, _, _, _, w in cards)
out[n] = (stage, js)

# ---------------------------------------------------------------- 03 TSMC Q3
n = 3
tx, ty = P["Tainan"]
stage = f"""
        {mappanel("t-map", f"{tx-270:.0f} {ty-150:.0f} 540 290", 90, 560, highlight=["Taiwan"], extra=node(tx, ty, "t-node", 4))}
        {tag("TAIWAN · REPORTED 15 OCT", X0, 130, "t-tag")}
        <div class="abs kick" id="t-k" style="left:{X0}px;top:680px;font-size:24px">TSMC · RECORD Q3</div>
        <div class="abs" id="t-rev" style="left:{X0}px;top:720px">
          <div class="big g" id="t-yoy" style="font-size:200px">+50.9%</div>
          <div style="font-size:36px;font-weight:700;margin-top:4px">YoY revenue · US$<span id="t-usd">46.7</span>bn</div>
          <div class="mut" style="font-size:30px;margin-top:6px">NT$1.494tn</div>
        </div>
        {card("t-ni", X0, 1090, 380, 240, '<div class="kick">NET INCOME</div><div class="big c" style="font-size:66px;margin-top:18px">NT$763bn</div><div class="mono g" style="font-size:26px;margin-top:8px">▲ +68.7%</div>', "padding:24px 26px")}
        {card("t-gm", X0 + 400, 1090, 270, 240, '<div class="kick">GROSS MARGIN</div><div class="big c" id="t-gmv" style="font-size:72px;margin-top:18px">66.4%</div>', "padding:24px 26px")}
        {card("t-eps", X0 + 690, 1090, 270, 240, '<div class="kick">EPS</div><div class="big c" style="font-size:52px;margin-top:26px">NT$29.43</div>', "padding:24px 22px")}
"""
t_rev = cue(n, "revenue")
js = f"""        fade("#t-map", 0.0, 1.0); pulse("#t-node-r", 0.6); pulse("#t-node-r", 2.6); fade("#t-tag", 0.4);
        fade("#t-k", {cue(n, "tsmc")});
        pop("#t-rev", {t_rev}); count("#t-usd", {t_rev}, 0, 46.7, 1, "", "", 1.2); count("#t-yoy", {cue(n, "50") - 0.3}, 0, 50.9, 1, "+", "%", 1.3);
        pop("#t-ni", {cue(n, "net")}); pop("#t-eps", {cue(n, "net") + 0.6});
        pop("#t-gm", {cue(n, "net") + 0.3}); count("#t-gmv", {cue(n, "net") + 0.3}, 0, 66.4, 1, "", "%", 0.9);
"""
out[n] = (stage, js)

# ---------------------------------------------------------------- 04 node mix + guidance
n = 4
stage = f"""        <div class="abs kick" id="m-k" style="left:{X0}px;top:150px;font-size:24px">TSMC · Q3 WAFER REVENUE MIX</div>
        <div class="abs h1" id="m-h" style="left:{X0}px;top:200px;width:{CW}px;font-size:72px">Advanced nodes carry the quarter</div>
        <div class="abs" id="m-bar" style="left:{X0}px;top:420px;width:{CW}px;height:120px;border:1.5px solid rgba(56,217,255,0.55);background:rgba(10,30,60,0.6)">
          <div id="m-adv" style="position:absolute;left:0;top:0;height:100%;width:79%;background:linear-gradient(90deg,rgba(56,217,255,0.35),rgba(56,217,255,0.75));box-shadow:0 0 30px rgba(56,217,255,0.5)"></div>
          <div id="m-2nm" style="position:absolute;left:71%;top:0;height:100%;width:8%;background:{AM};box-shadow:0 0 30px rgba(255,181,71,0.7)"></div>
        </div>
        <div class="abs" id="m-l1" style="left:{X0}px;top:570px"><span class="big c" style="font-size:110px" id="m-79">79%</span><span style="font-size:32px;font-weight:700;margin-left:18px">≥7nm advanced nodes</span></div>
        <div class="abs" id="m-l2" style="left:{X0}px;top:710px"><span class="big a" style="font-size:110px">8%</span><span style="font-size:32px;font-weight:700;margin-left:18px">2nm already</span></div>
        {card("m-g1", X0, 880, CW, 210, '<div class="kick">FY2026 REVENUE GROWTH GUIDE</div><div class="big g" style="font-size:100px;margin-top:14px">~44% <span style="font-size:40px" class="mut">USD · LIFTED</span></div>')}
        {card("m-g2", X0, 1120, CW, 210, '<div class="kick">Q4 REVENUE GUIDE</div><div class="big c" style="font-size:100px;margin-top:14px">US$52.3–54.3bn</div>')}
"""
t_a = cue(n, "advanced")
js = f"""        fade("#m-k", 0.1); pop("#m-h", 0.2);
        fade("#m-bar", {t_a - 0.3}, 0.3);
        tl.fromTo(q("#m-adv"), {{ width: "0%" }}, {{ width: "79%", duration: 1.3, ease: "power2.out" }}, {t_a});
        pop("#m-l1", {t_a + 0.3}); count("#m-79", {t_a + 0.3}, 0, 79, 0, "", "%", 1.2);
        tl.fromTo(q("#m-2nm"), {{ opacity: 0, scaleY: 0 }}, {{ opacity: 1, scaleY: 1, duration: 0.5, ease: "back.out(2)" }}, {cue(n, "2")});
        pop("#m-l2", {cue(n, "2") + 0.2});
        pop("#m-g1", {cue(n, "guide")}); pop("#m-g2", {cue(n, "guide") + 0.9});
"""
out[n] = (stage, js)

# ---------------------------------------------------------------- 05 capacity (vertical timeline)
n = 5
ys = {"2026": 520, "2027": 770, "2028": 1020, "2029": 1270}
ticks = "".join(f'<line x1="150" y1="{y}" x2="180" y2="{y}" stroke="{CY}" stroke-width="3"/><text x="135" y="{y+9}" fill="{MUT}" font-family="JetBrains Mono" font-size="26" text-anchor="end">{yr}</text>' for yr, y in ys.items())
y_az, y_tn = 770 + 250 * 0.5, 1020 + 250 * 0.12
stage = f"""        <div class="abs kick" id="c-k" style="left:{X0}px;top:150px;font-size:24px">TSMC · NEW CAPACITY</div>
        <div class="abs h1" id="c-h" style="left:{X0}px;top:200px;font-size:72px">Chasing every last wafer</div>
        {card("c-2nm", X0, 310, CW, 150, '<div class="kick">2NM CAPACITY</div><div class="big g" style="font-size:60px;margin-top:8px">&gt;2× next year</div>', "padding:20px 28px")}
        <svg class="full" viewBox="0 0 1080 1920">
          <path class="ln" id="c-axis" pathLength="1" style="stroke-dasharray:1" d="M165 490 V1300"/>
          <g id="c-ticks">{ticks}</g>
          <circle class="node" id="c-az" cx="165" cy="{y_az:.0f}" r="14"/><circle class="ring" id="c-az-r" cx="165" cy="{y_az:.0f}" r="26"/>
          <circle class="node" id="c-tn" cx="165" cy="{y_tn:.0f}" r="14" style="fill:{AM}"/><circle class="ring" id="c-tn-r" cx="165" cy="{y_tn:.0f}" r="26" style="stroke:{AM}"/>
          <path class="ln" id="c-l1" pathLength="1" style="stroke-dasharray:1" d="M180 {y_az:.0f} H230"/>
          <path class="ln" id="c-l2" pathLength="1" style="stroke-dasharray:1;stroke:{AM}" d="M180 {y_tn:.0f} H230"/>
        </svg>
        {card("c-az-card", 230, int(y_az) - 75, 790, 150, '<div class="kick">Q3 2027 · ARIZONA FAB 2</div><div style="font-size:32px;font-weight:700;margin-top:10px">Mass production · slightly ahead</div>', "padding:20px 28px")}
        {card("c-tn-card", 230, int(y_tn) - 20, 790, 150, '<div class="kick" style="color:#ffb547">1H 2028 · TAINAN</div><div style="font-size:32px;font-weight:700;margin-top:10px">One more 3nm plant · volume</div>', "padding:20px 28px;border-color:rgba(255,181,71,0.6)")}
        {card("c-note1", 230, 1200, 790, 125, '<div class="kick">ARIZONA FAB 2 STATUS</div><div style="font-size:28px;font-weight:600;margin-top:10px">Construction complete · tools going in</div>', "padding:18px 28px")}
"""
t_tn, t_az = cue(n, "tainan"), cue(n, "arizona")
js = f"""        fade("#c-k", 0.1); pop("#c-h", 0.2); pop("#c-2nm", 0.5); draw("#c-axis", 0.4, 1.0); fade("#c-ticks", 0.8);
        grow("#c-tn", {t_tn}); pulse("#c-tn-r", {t_tn}); draw("#c-l2", {t_tn + 0.2}, 0.3); pop("#c-tn-card", {t_tn + 0.3});
        grow("#c-az", {t_az}); pulse("#c-az-r", {t_az}); draw("#c-l1", {t_az + 0.2}, 0.3); pop("#c-az-card", {t_az + 0.3});
        pop("#c-note1", {cue(n, "production")});
"""
out[n] = (stage, js)

# ---------------------------------------------------------------- 06 Texas / Terafab
n = 6
ax, ay = P["Arizona"]; tx_, ty_ = P["Texas"]
sx, nyx = P["Sunnyvale"][0], P["UpstateNY"][0]
cx, w = (sx + nyx) / 2, (nyx - sx) * 1.35
vb = f"{cx - w/2:.0f} {ay - w*0.33:.0f} {w:.0f} {w*0.574:.0f}"
stage = f"""
        {mappanel("x-map", vb, 90, 620, highlight=["USA"], extra=node(ax, ay, "x-az", 3) + node(tx_, ty_, "x-tx", 3) + f'<path class="arc" id="x-arc" pathLength="1" style="stroke-dasharray:1" d="M{ax} {ay} Q{(ax+tx_)/2:.0f} {min(ay,ty_)-30:.0f} {tx_} {ty_}"/>', opacity=0.95)}
        <div class="abs kick" id="x-k" style="left:{X0}px;top:130px;font-size:24px">TSMC · BEYOND ARIZONA</div>
        {tag("C.C. WEI · CEO", X0, 170, "x-who")}
        {card("x-c1", X0, 740, 470, 160, '<div class="kick">ARIZONA</div><div style="font-size:30px;font-weight:700;margin-top:10px">Fab 2 · mass production Q3 2027</div>', "padding:20px 24px")}
        {card("x-c2", X0 + 490, 740, 470, 160, '<div class="kick" style="color:#ffb547">TEXAS</div><div style="font-size:30px;font-weight:700;margin-top:10px">Teams evaluating capacity</div>', "padding:20px 24px;border-color:rgba(255,181,71,0.6)")}
        {card("x-c3", X0, 930, CW, 230, '<div class="kick">CUSTOMER-BUILT TERAFAB</div><div style="font-size:34px;font-weight:700;margin-top:10px;line-height:1.3">Talks on using its capacity — fab must be run by TSMC</div><div class="mono mut" style="font-size:20px;margin-top:10px">JAPAN / EUROPE-STYLE FRAMEWORKS POSSIBLE</div>', "padding:22px 28px")}
        <div class="abs big a" id="x-deal" style="left:250px;top:1195px;font-size:80px;border:3px solid {AM};padding:6px 30px;box-shadow:0 0 30px rgba(255,181,71,0.5)">NO DEAL YET</div>
"""
js = f"""        fade("#x-map", 0.0, 1.0); fade("#x-k", 0.1); fade("#x-who", 0.4); grow("#x-az", 0.4); pulse("#x-az-r", 0.4); pop("#x-c1", 0.6);
        draw("#x-arc", {cue(n, "texas") - 0.3}, 0.8); grow("#x-tx", {cue(n, "texas")}); pulse("#x-tx-r", {cue(n, "texas")}); pulse("#x-tx-r", {cue(n, "texas") + 2});
        pop("#x-c2", {cue(n, "texas")}); pop("#x-c3", {cue(n, "terafab")});
        tl.fromTo(q("#x-deal"), {{ opacity: 0, scale: 1.6, rotation: -6 }}, {{ opacity: 1, scale: 1, rotation: -3, duration: 0.45, ease: "power4.out" }}, {cue(n, "deal")});
"""
out[n] = (stage, js)

# ---------------------------------------------------------------- 07 Samsung
n = 7
layers = ""
for i in range(14):
    y = 660 - i * 30
    layers += f'<path class="lay" d="M300 {y} L540 {y-80} L780 {y} L540 {y+80} Z" fill="rgba(56,217,255,{0.10 + i*0.03:.2f})" stroke="{CY}" stroke-width="1.8"/>'
specs = [("BIT DENSITY", "+58%", 58, GR, "s-b1"), ("I/O SPEED", "+33%", 33, GR, "s-b2"), ("POWER", "−25%", 25, AM, "s-b3")]
stage = f"""        <div class="abs kick" id="s-k" style="left:{X0}px;top:130px;font-size:22px">KOREA · SAMSUNG · GMIF2026 · SHENZHEN · 15 OCT</div>
        <svg class="full" viewBox="0 0 1080 1920"><g id="s-stack">{layers}</g></svg>
        <div class="abs" id="s-cnt" style="left:760px;top:330px;width:280px;text-align:center"><span class="big c" style="font-size:96px" id="s-layers">400+</span><div class="kick" style="margin-top:4px">LAYERS</div></div>
        <div class="abs h1" id="s-h" style="left:{X0}px;top:770px;width:{CW}px;font-size:50px;white-space:nowrap">V10 BV-NAND · first 400+ layers</div>
"""
for i, (lab, val, pct, col, sid) in enumerate(specs):
    y = 860 + i * 112
    stage += f"""        <div class="abs" id="{sid}" style="left:{X0}px;top:{y}px;width:{CW}px">
          <div style="display:flex;justify-content:space-between;align-items:baseline"><span class="kick">{lab} vs V9</span><span class="big" style="font-size:56px;color:{col};text-shadow:0 0 18px {col}">{val}</span></div>
          <div style="height:14px;background:rgba(56,217,255,0.12);margin-top:6px"><div class="bar" style="height:100%;width:{pct*1.5}%;background:{col};box-shadow:0 0 18px {col}"></div></div>
        </div>
"""
stage += card("s-c1", X0, 1210, 470, 140, '<div class="kick">PM1763 · PCIe GEN6 SSD</div><div style="font-size:28px;font-weight:700;margin-top:10px">Samples Q4 2026</div>', "padding:20px 24px") + "\n"
stage += card("s-c2", X0 + 490, 1210, 470, 140, '<div class="kick">zNAND-O · ON-DEVICE AI</div><div style="font-size:24px;font-weight:700;margin-top:10px">UCIe · ~10× DRAM bit density</div>', "padding:20px 24px") + "\n"
js = f"""        fade("#s-k", 0.1);
        tl.fromTo(q(".lay"), {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.25, stagger: 0.12, ease: "power2.out" }}, 0.3);
        pop("#s-h", {cue(n, "v")}); pop("#s-cnt", {cue(n, "400") - 0.3}); count("#s-layers", {cue(n, "400") - 0.3}, 0, 400, 0, "", "+", 1.0);
        pop("#s-b1", {cue(n, "58")}); tl.fromTo(q("#s-b1 .bar"), {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.8, ease: "power2.out" }}, {cue(n, "58")});
        pop("#s-b2", {cue(n, "58") + 0.7}); tl.fromTo(q("#s-b2 .bar"), {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.8, ease: "power2.out" }}, {cue(n, "58") + 0.7});
        pop("#s-b3", {cue(n, "power", off=-0.6)}); tl.fromTo(q("#s-b3 .bar"), {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.8, ease: "power2.out" }}, {cue(n, "power", off=-0.6)});
        pop("#s-c1", {cue(n, "58") + 1.8}); pop("#s-c2", {cue(n, "58") + 2.3});
"""
out[n] = (stage, js)

# ---------------------------------------------------------------- 08 SK hynix
n = 8
dx, dy = P["Dalian"]; nx, ny = P["UpstateNY"]
k_arc = f'<path class="arc" id="k-arc" pathLength="1" style="stroke-dasharray:1" d="M{dx} {dy} C{dx-300} {dy-330} {nx+300} {ny-330} {nx} {ny}"/>'
stage = f"""
        {mappanel("k-map", "380 60 1360 790", 90, 640, extra=k_arc + node(dx, dy, "k-dl", 7) + node(nx, ny, "k-ny", 7), opacity=0.9)}
        <div class="abs kick" id="k-k" style="left:{X0}px;top:130px;font-size:22px">KOREA · SK HYNIX / SOLIDIGM · REUTERS 15 OCT</div>
        {card("k-c1", X0, 760, CW, 190, '<div class="kick" style="color:#ffb547">DALIAN, CHINA · MOD B</div><div style="font-size:34px;font-weight:700;margin-top:10px;line-height:1.3">More US-made tools in unused space — US approval sought</div>', "padding:22px 28px;border-color:rgba(255,181,71,0.6)")}
        {card("k-c2", X0, 980, CW, 170, '<div class="kick">UPSTATE NEW YORK</div><div style="font-size:34px;font-weight:700;margin-top:10px;line-height:1.3">Leading site for a possible US NAND fab</div>', "padding:22px 28px")}
        {card("k-c3", X0, 1180, CW, 130, '<div style="font-size:30px;font-weight:700;text-align:center">Company: <span class="c">not pursuing China capacity expansion</span></div>', "padding:22px 24px")}
"""
js = f"""        fade("#k-map", 0.0, 1.0); fade("#k-k", 0.1);
        grow("#k-dl", {cue(n, "dalian") - 0.4}); pulse("#k-dl-r", {cue(n, "dalian") - 0.4}); pop("#k-c1", {cue(n, "approval")});
        draw("#k-arc", {cue(n, "linked")}, 1.4); grow("#k-ny", {cue(n, "new")}); pulse("#k-ny-r", {cue(n, "new")}); pop("#k-c2", {cue(n, "nand")});
        pop("#k-c3", {cue(n, "possible")});
"""
out[n] = (stage, js)

# ---------------------------------------------------------------- 09 Applied EPIC
n = 9
def iso(x, y, w, d, h):
    c = math.cos(math.radians(30)); s = 0.5
    p = lambda a, b, z: (x + (a - b) * c, y + (a + b) * s - z)
    pts = {k: p(*v) for k, v in {"a": (0, 0, 0), "b": (w, 0, 0), "c": (w, d, 0), "d": (0, d, 0), "e": (0, 0, h), "f": (w, 0, h), "g": (w, d, h), "h": (0, d, h)}.items()}
    L = lambda u, v: f"M{pts[u][0]:.0f} {pts[u][1]:.0f} L{pts[v][0]:.0f} {pts[v][1]:.0f} "
    return "".join(L(u, v) for u, v in ["ab", "bc", "cd", "da", "ef", "fg", "gh", "he", "ae", "bf", "cg", "dh"])
bld = iso(560, 420, 320, 220, 110) + iso(620, 460, 100, 70, 50)
bays = "".join(f"M{560 + i*32*0.866:.0f} {420 + i*16 + 35:.0f} l{-0.866*170:.0f} {85:.0f} " for i in range(1, 10))
partners = [("TSMC", 790, 300), ("Intel", 870, 470), ("Samsung", 780, 640), ("Micron", 470, 740), ("SK hynix", 120, 640)]
plinks = "".join(f'<path class="ln" id="e-l{i}" pathLength="1" style="stroke-dasharray:1" d="M560 560 L{x + 60} {y + 28}"/>' for i, (_, x, y) in enumerate(partners))
stage = f"""        <div class="abs kick" id="e-k" style="left:{X0}px;top:130px;font-size:22px">USA · APPLIED MATERIALS · SUNNYVALE · 12 OCT</div>
        <div class="abs h1" id="e-h" style="left:{X0}px;top:175px;font-size:76px">EPIC Center</div>
        <svg class="full" viewBox="0 0 1080 1920">
          <path class="ln" id="e-bld" pathLength="1" style="stroke-dasharray:1;stroke-width:3" d="{bld}"/>
          <path id="e-bays" d="{bays}" fill="none" stroke="rgba(56,217,255,0.35)" stroke-width="1.5"/>
          {plinks}
        </svg>
        <div class="abs mut" id="e-sub" style="left:{X0}px;top:830px;width:{CW}px;font-size:28px;line-height:1.35">World's largest collaborative chip process &amp; equipment R&amp;D facility</div>
        {card("e-s1", X0, 930, 470, 170, '<div class="kick">INVESTMENT</div><div class="big g" style="font-size:80px;margin-top:8px">US$5bn</div>', "padding:20px 26px")}
        {card("e-s2", X0 + 490, 930, 470, 170, '<div class="kick">FLOOR AREA</div><div class="big c" style="font-size:66px;margin-top:12px;white-space:nowrap">~600k ft²</div>', "padding:20px 26px")}
        {card("e-s3", X0, 1130, CW, 170, '<div class="kick">CLEANROOM</div><div class="big c" style="font-size:76px;margin-top:8px">~4 acres <span style="font-size:32px" class="mut">· lab-to-fab cycles ↓</span></div>', "padding:20px 26px")}
"""
for i, (name, x, y) in enumerate(partners):
    stage += f'        <div class="abs glass" id="e-p{i}" style="left:{x}px;top:{y}px;padding:12px 22px;font-weight:800;font-size:28px">{name}</div>\n'
js = f"""        fade("#e-k", 0.1); pop("#e-h", 0.2); fade("#e-sub", 0.8); draw("#e-bld", 0.3, 2.2); fade("#e-bays", 1.6, 1.0);
        pop("#e-s1", {cue(n, "5")}); pop("#e-s2", {cue(n, "sunnyvale")}); pop("#e-s3", {cue(n, "cleanroom")});
"""
for i, w in enumerate(["tsmc", "intel", "samsung", "micron", "hynix"]):
    js += f'        draw("#e-l{i}", {cue(n, w) - 0.2}, 0.4); grow("#e-p{i}", {cue(n, w)}, 0.45);\n'
out[n] = (stage, js)

# ---------------------------------------------------------------- 10 SEMI
n = 10
base = 930
h26, h29 = 149 * 2.3, 227 * 2.3
stage = f"""        <div class="abs kick" id="m2-k" style="left:{X0}px;top:130px;font-size:22px">USA · SEMI @ SEMICON WEST · 13 OCT</div>
        <div class="abs h1" id="m2-h" style="left:{X0}px;top:175px;width:{CW}px;font-size:62px">300mm fab equipment spend</div>
        <div class="abs" id="m2-b1" style="left:170px;top:{base - h26:.0f}px;width:280px;height:{h26:.0f}px;background:linear-gradient(180deg,rgba(56,217,255,0.85),rgba(56,217,255,0.25));box-shadow:0 0 34px rgba(56,217,255,0.5)"></div>
        <div class="abs" id="m2-b2" style="left:630px;top:{base - h29:.0f}px;width:280px;height:{h29:.0f}px;background:linear-gradient(180deg,rgba(61,255,160,0.85),rgba(61,255,160,0.25));box-shadow:0 0 34px rgba(61,255,160,0.5)"></div>
        <div class="abs" style="left:{X0}px;top:{base}px;width:{CW}px;height:3px;background:{CY}"></div>
        <div class="abs mono mut" style="left:170px;top:{base + 14}px;width:280px;text-align:center;font-size:30px">2026</div>
        <div class="abs mono mut" style="left:630px;top:{base + 14}px;width:280px;text-align:center;font-size:30px">2029</div>
        <div class="abs big c" id="m2-v1" style="left:130px;top:{base - h26 - 100:.0f}px;width:360px;text-align:center;font-size:80px">US$149bn</div>
        <div class="abs big g" id="m2-v2" style="left:590px;top:{base - h29 - 100:.0f}px;width:360px;text-align:center;font-size:80px">US$227bn</div>
        <svg class="full" viewBox="0 0 1080 1920"><path class="arc" id="m2-arc" pathLength="1" style="stroke-dasharray:1" d="M450 {base - h26 - 30:.0f} Q 540 {base - h29 - 110:.0f} 630 {base - h29 - 10:.0f}"/></svg>
        {card("m2-c1", X0, 1010, 400, 170, '<div class="kick">2026 GROWTH</div><div class="big g" style="font-size:76px;margin-top:8px">+31% YoY</div>', "padding:20px 26px")}
        {card("m2-c2", X0 + 420, 1010, 540, 300, '<div class="kick">NEW 300MM FABS / LINES · 2026</div><div class="big c" style="font-size:110px;margin-top:8px">20</div><div style="font-size:30px;font-weight:700">start construction · 3 in US</div>', "padding:20px 26px")}
"""
t1, t3 = cue(n, "149"), cue(n, "227")
js = f"""        fade("#m2-k", 0.1); pop("#m2-h", 0.2);
        tl.fromTo(q("#m2-b1"), {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "50% 100%", duration: 1.0, ease: "power3.out" }}, {t1 - 0.4});
        pop("#m2-v1", {t1}); pop("#m2-c1", {cue(n, "31")});
        draw("#m2-arc", {t3 - 0.6}, 0.7);
        tl.fromTo(q("#m2-b2"), {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "50% 100%", duration: 1.0, ease: "power3.out" }}, {t3 - 0.3});
        pop("#m2-v2", {t3}); pop("#m2-c2", {t3 + 1.0});
"""
out[n] = (stage, js)

# ---------------------------------------------------------------- 11 Europe + SEA
n = 11
ex, ey = P["Dresden"]; jx, jy = P["Johor"]
stage = f"""
        {mappanel("u-map", "790 220 860 500", 90, 620, highlight=["Malaysia"], europe=True, extra=node(ex, ey, "u-dr", 5) + node(jx, jy, "u-jh", 5), opacity=0.95)}
        <div class="abs kick" id="u-k" style="left:{X0}px;top:130px;font-size:24px">EUROPE &amp; SOUTH EAST ASIA</div>
        {tag("EUROPE", 330, 360, "u-eu", "#7fe8ff")}
        {tag("MALAYSIA", 760, 640, "u-my", "#ffb547")}
        {card("u-c1", X0, 740, CW, 290, '''<div class="kick">GLOBALFOUNDRIES · DRESDEN · 9 OCT</div>
          <div><span class="big c" style="font-size:80px">€1.1bn</span><span style="font-size:30px;font-weight:700;margin-left:16px">SPRINT topped out</span></div>
          <div style="font-size:26px;margin-top:10px;line-height:1.4" class="mut">&gt;1M 300mm wafers / year by end-2028</div>
          <div style="font-size:26px;margin-top:4px;line-height:1.4" class="mut">FDX Fusion · next-gen FD-SOI for Physical AI</div>''', "padding:22px 28px")}
        {card("u-c2", X0, 1060, CW, 290, '''<div class="kick" style="color:#ffb547">FIC GLOBAL · JOHOR, MALAYSIA · 15 OCT</div>
          <div><span class="big a" style="font-size:80px">800G–3.2T</span><span style="font-size:30px;font-weight:700;margin-left:16px">optical transceivers</span></div>
          <div style="font-size:26px;margin-top:10px;line-height:1.4" class="mut">New i-Park @ Senai plant · CPO / LPO · silicon photonics</div>
          <div style="font-size:26px;margin-top:4px;line-height:1.4" class="mut">Johor–Singapore twinning model</div>''', "padding:22px 28px;border-color:rgba(255,181,71,0.6)")}
"""
js = f"""        fade("#u-map", 0.0, 1.0); fade("#u-k", 0.1);
        grow("#u-dr", {cue(n, "globalfoundries") - 0.3}); pulse("#u-dr-r", {cue(n, "globalfoundries") - 0.3}); fade("#u-eu", {cue(n, "europe")}); pop("#u-c1", {cue(n, "globalfoundries")});
        grow("#u-jh", {cue(n, "malaysia") - 0.3}); pulse("#u-jh-r", {cue(n, "malaysia") - 0.3}); fade("#u-my", {cue(n, "malaysia")}); pop("#u-c2", {cue(n, "malaysia")});
"""
out[n] = (stage, js)

# ---------------------------------------------------------------- 12 close
n = 12
regions = [("TAIWAN", 1), ("KOREA", 1), ("USA", 1), ("EUROPE", 1), ("SE ASIA", 1), ("JAPAN", 0), ("CHINA", 0), ("INDIA", 0)]
stage = f'        <div class="abs kick" id="z-k" style="left:{X0}px;top:150px;font-size:24px">REGION BOARD · 16 OCT 2026</div>\n'
for i, (r, act) in enumerate(regions):
    x, y = X0 + (i % 2) * 490, 210 + (i // 2) * 125
    col, st = (GR, "● ACTIVE") if act else (MUT, "○ QUIET")
    stage += f'        <div class="abs glass" id="z-r{i}" style="left:{x}px;top:{y}px;width:470px;height:105px;padding:18px 26px;box-sizing:border-box;display:flex;justify-content:space-between;align-items:center"><span style="font-weight:800;font-size:34px">{r}</span><span class="mono" style="font-size:24px;color:{col}">{st}</span></div>\n'
stage += f"""        <div class="abs h1" id="z-line" style="left:{X0}px;top:760px;width:{CW}px;font-size:66px">Record quarters still need wet benches that turn wafers <span class="a">this quarter.</span></div>
        <div class="abs glass" id="z-cta" style="left:{X0}px;top:1150px;padding:22px 36px;font-weight:800;font-size:44px">Shout if that gap is yours <span class="c">→</span></div>
"""
js = '        fade("#z-k", 0.1);\n'
for i in [0, 1, 2, 3, 4]:
    js += f'        pop("#z-r{i}", {0.2 + i*0.12:.2f}, 0.4);\n'
for i in range(5, 8):
    js += f'        pop("#z-r{i}", {cue(n, "japan") + (i-5)*0.35:.2f}, 0.4);\n'
js += f'        pop("#z-line", {cue(n, "record")}, 0.7); grow("#z-cta", {cue(n, "if")});\n'
out[n] = (stage, js)

# ---------------------------------------------------------------- write frames
os.makedirs("compositions/frames", exist_ok=True)
for n, dur, src in FRAMES:
    fid = os.path.splitext(os.path.basename(src))[0]
    stage, js = out[n]
    open(src, "w").write(shell(fid, n, dur, stage, js, final=(n == len(FRAMES))))
    print(f"  {src}  ({dur}s)")

# ---------------------------------------------------------------- HUD overlay (top bar + ticker), full length
items = ["TSMC Q3 REVENUE US$46.7BN ▲50.9% YoY", "NET INCOME NT$763BN ▲68.7%", "GROSS MARGIN 66.4%", "EPS NT$29.43",
         "Q4 GUIDE US$52.3–54.3BN", "FY26 GROWTH GUIDE ~44%", "≥7NM 79% OF WAFER REVENUE", "2NM 8%",
         "SAMSUNG V10 · 400+ LAYERS", "AMAT EPIC CENTER US$5BN", "300MM FAB EQUIPMENT 2026 US$149BN ▲31%", "2029 US$227BN",
         "20 NEW 300MM FABS/LINES IN 2026", "GF DRESDEN €1.1BN SPRINT", "FICG JOHOR 800G–3.2T OPTICS"]
tick = "".join(f'<span style="margin-right:70px"><span style="color:{CY}">◆</span> {t}</span>' for t in items)
dur = round(TOTAL_DUR, 2)
overlay = f"""<template id="hud-template">
  <div id="root" data-composition-id="hud" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
    <style>
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #hud-top {{ position: absolute; left: 0; top: 0; width: 1080px; height: 72px; display: flex; align-items: center; justify-content: space-between;
        padding: 0 40px; box-sizing: border-box; background: linear-gradient(180deg, rgba(3,9,20,0.92), rgba(3,9,20,0.55));
        border-bottom: 1px solid rgba(56,217,255,0.45); font-family: "JetBrains Mono", monospace; font-size: 19px; letter-spacing: 0.10em; color: {TXT}; }}
      #hud-top .live {{ color: {RD}; text-shadow: 0 0 10px {RD}; }}
      #hud-tick {{ position: absolute; left: 0; top: 1580px; width: 1080px; height: 46px; overflow: hidden; background: rgba(3,9,20,0.88);
        border-top: 1px solid rgba(56,217,255,0.45); font-family: "JetBrains Mono", monospace; font-size: 20px; color: {TXT}; letter-spacing: 0.06em; }}
      #hud-tape {{ position: absolute; left: 0; top: 9px; white-space: nowrap; }}
    </style>
    <div id="hud-top" class="clip" data-start="0" data-duration="{dur}" data-track-index="0">
      <span>SEMICONDUCTOR MARKET UPDATE</span><span class="live" id="hud-live">● LIVE</span><span>16 OCT 2026</span>
    </div>
    <div id="hud-tick" data-layout-allow-overflow class="clip" data-start="0" data-duration="{dur}" data-track-index="1"><div id="hud-tape">{tick}{tick}{tick}</div></div>
    <script src="assets/vendor/gsap.min.js"></script>
    <script>
      (function () {{
        const tl = gsap.timeline({{ paused: true }});
        tl.fromTo("#hud-tape", {{ x: 0 }}, {{ x: -{int(dur*110)}, duration: {dur}, ease: "none" }}, 0);
        const n = Math.floor({dur} / 1.6);
        for (let i = 0; i < n; i++) tl.fromTo("#hud-live", {{ opacity: 1 }}, {{ opacity: 0.35, duration: 0.8, ease: "sine.inOut" }}, i * 1.6).to("#hud-live", {{ opacity: 1, duration: 0.8, ease: "sine.inOut" }}, i * 1.6 + 0.8);
        window.__timelines["hud"] = tl;
      }})();
    </script>
  </div>
</template>
"""
open("compositions/hud.html", "w").write(overlay)
print("  compositions/hud.html", dur)
