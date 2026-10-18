#!/usr/bin/env python3
"""VERTICAL 9:16 (1080x1920, YouTube Shorts) version. Build the 12 scene sub-compositions + the persistent HUD overlay for "Top 10 · AI, Chips & Quantum" (18 Oct 2026).

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
# Vertical 1080x1920. Content lives in y ~110..1350; captions ~1390..1565; ticker 1580..1626; Shorts UI below.
X0, CW = 60, 960  # content left / width
CAT = {"AI": CY, "CHIPS": AM, "QUANTUM": GR, "AI × QUANTUM": CY2}
VB = 'viewBox="0 0 1080 1920"'


def story(n, num, cat, headline, source, visual, vjs):
    """Vertical story layout: big number + category chip + source (top), headline, visual below (y 580..1350)."""
    col = CAT[cat]
    stage = f"""        <div class="abs big" id="n{n}-num" style="left:{X0}px;top:110px;font-size:200px;color:{col};text-shadow:0 0 30px {col}">{num:02d}</div>
        <div class="abs mono" id="n{n}-cat" style="left:330px;top:140px;font-size:24px;letter-spacing:0.16em;color:#03101f;background:{col};padding:8px 18px;box-shadow:0 0 20px {col}">{cat}</div>
        <div class="abs mono mut" id="n{n}-src" style="left:330px;top:210px;width:690px;font-size:19px;line-height:1.5;letter-spacing:0.08em">SOURCE · <span style="color:#e9f7ff">{source}</span></div>
        <div class="abs" style="left:{X0}px;top:330px;width:{CW}px;height:2px;background:linear-gradient(90deg,rgba(56,217,255,0),rgba(56,217,255,0.6),rgba(56,217,255,0))"></div>
        <div class="abs h1" id="n{n}-h" style="left:{X0}px;top:355px;width:{CW}px;font-size:54px;line-height:1.12">{headline}</div>
{visual}"""
    js = f"""        tl.fromTo(q("#n{n}-num"), {{ opacity: 0, x: -50 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, 0.05);
        fade("#n{n}-cat", 0.25); pop("#n{n}-h", 0.3, 0.6); fade("#n{n}-src", 0.8);
{vjs}"""
    return stage, js


def stat(sid, x, y, w, h, label, value, color, sub="", vsize=96, extra=""):
    return card(sid, x, y, w, h, f'<div class="kick">{label}</div><div class="big" id="{sid}-v" style="font-size:{vsize}px;margin-top:14px;color:{color};text-shadow:0 0 22px {color}">{value}</div>'
                + (f'<div style="font-size:26px;font-weight:600;margin-top:10px;line-height:1.3">{sub}</div>' if sub else ""), extra)


# ---------------------------------------------------------------- 01 open
n = 1
pts = ["Bangkok", "NewDelhi", "NewYork", "Seoul", "Beijing", "SantaClara", "SantaBarbara", "Arlington", "Yorktown"]
nodes = "".join(node(*P[k], f"o-{k}") for k in pts)
stage = f"""
        {mappanel("o-map", "240 0 1500 1056", 90, 720, extra=nodes, opacity=0.9)}
        {card("o-title", X0, 830, CW, 400, f'''<div class="kick" style="font-size:24px">AI · CHIPS · QUANTUM</div>
          <div class="h1" style="font-size:130px;margin-top:14px;line-height:1">Top 10</div>
          <div style="font-size:42px;font-weight:700;margin-top:18px">The stories that moved tech</div>
          <div class="mono c" style="font-size:30px;margin-top:22px">EDITION · 18 OCT 2026</div>''')}
        <div class="abs" id="o-cats" style="left:{X0}px;top:1260px;width:{CW}px;display:flex;justify-content:center;gap:28px">
          <div class="mono" style="font-size:28px;color:#03101f;background:{CY};padding:12px 30px;box-shadow:0 0 20px {CY}">AI</div>
          <div class="mono" style="font-size:28px;color:#03101f;background:{AM};padding:12px 30px;box-shadow:0 0 20px {AM}">CHIPS</div>
          <div class="mono" style="font-size:28px;color:#03101f;background:{GR};padding:12px 30px;box-shadow:0 0 20px {GR}">QUANTUM</div>
        </div>
"""
js = '        fade("#o-map", 0.0, 1.0);\n'
for i, k in enumerate(pts):
    js += f'        grow("#o-{k}", {0.2 + i*0.18:.2f}, 0.4); pulse("#o-{k}-r", {0.2 + i*0.18:.2f});\n'
js += f'        pop("#o-title", {cue(n, "here")}, 0.7); tl.fromTo(q("#o-cats > div"), {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, stagger: 0.25, ease: "power3.out" }}, {cue(n, "ai")});\n'
out[n] = (stage, js)

# ---------------------------------------------------------------- 02 Clark (AI)
n = 2
bar_h = lambda v: v * 7
BASE = 1060
vis = f"""        <div class="abs mono mut" id="c2-k" style="left:{X0}px;top:590px;width:{CW}px;font-size:22px;letter-spacing:0.12em">US ECONOMIC OUTPUT · ANTHROPIC MODEL</div>
        <div class="abs" id="c2-b1" style="left:170px;top:{BASE - bar_h(30):.0f}px;width:300px;height:{bar_h(30):.0f}px;background:linear-gradient(180deg,rgba(143,182,209,0.8),rgba(143,182,209,0.2))"></div>
        <div class="abs" id="c2-b2" style="left:610px;top:{BASE - bar_h(44):.0f}px;width:300px;height:{bar_h(44):.0f}px;background:linear-gradient(180deg,rgba(56,217,255,0.9),rgba(56,217,255,0.25));box-shadow:0 0 34px rgba(56,217,255,0.5)"></div>
        <div class="abs" style="left:{X0}px;top:{BASE}px;width:{CW}px;height:3px;background:{CY}"></div>
        <div class="abs big mut" id="c2-v1" style="left:170px;top:{BASE - bar_h(30) - 84:.0f}px;width:300px;text-align:center;font-size:66px">~$30T</div>
        <div class="abs big c" id="c2-v2" style="left:610px;top:{BASE - bar_h(44) - 84:.0f}px;width:300px;text-align:center;font-size:66px">~$44T</div>
        <div class="abs mono mut" style="left:170px;top:{BASE + 14}px;width:300px;text-align:center;font-size:22px">TODAY</div>
        <div class="abs mono" style="left:610px;top:{BASE + 14}px;width:300px;text-align:center;font-size:22px;color:{CY}">2030 · SCENARIO</div>
        {card("c2-note", X0, 1130, 470, 210, '<div class="kick" style="color:#ffb547">CAVEAT</div><div style="font-size:28px;font-weight:700;margin-top:10px;line-height:1.3">Most aggressive of the model\'s scenarios</div>', "padding:22px 26px;border-color:rgba(255,181,71,0.6)")}
        {card("c2-rules", 550, 1130, 470, 210, '<div class="kick">CLARK\'S ASK</div><div style="font-size:28px;font-weight:700;margin-top:10px;line-height:1.3">International co-operation and serious rules</div>', "padding:22px 26px")}
"""
vjs = f"""        fade("#c2-k", 0.7);
        tl.fromTo(q("#c2-b1"), {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "50% 100%", duration: 0.8, ease: "power3.out" }}, {cue(n, "us") - 0.2}); pop("#c2-v1", {cue(n, "us")});
        tl.fromTo(q("#c2-b2"), {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "50% 100%", duration: 1.0, ease: "power3.out" }}, {cue(n, "44") - 0.3}); pop("#c2-v2", {cue(n, "44")});
        pop("#c2-note", {cue(n, "aggressive")}); pop("#c2-rules", {cue(n, "rules", off=-0.5)});
"""
out[n] = story(n, 1, "AI", "Anthropic's Jack Clark: AI could lift US output to ~$44 trillion by 2030", "REUTERS · 17 OCT · IMF/WORLD BANK MEETINGS, BANGKOK", vis, vjs)

# ---------------------------------------------------------------- 03 CERT-In (AI)
n = 3
rows = [("AI agents under testing reached live systems", "reached"), ("Read personal & confidential business data", "confidential"), ("Via exposed credentials — no firm detected it", "none")]
vis = f"""        <div class="abs mono" id="c3-badge" style="left:{X0}px;top:600px;font-size:24px;letter-spacing:0.12em;color:#03101f;background:{RD};padding:10px 20px;box-shadow:0 0 26px {RD}">⚠ CRITICAL ADVISORY · CIAD-2026-0049</div>
        <div class="abs big" id="c3-t" style="left:{X0}px;top:680px;width:{CW}px;font-size:60px;color:{TXT}">"AI Agents as Attack Vectors"</div>
"""
for i, (t, _) in enumerate(rows):
    vis += f'        <div class="abs glass" id="c3-r{i}" style="left:{X0}px;top:{790 + i*175}px;width:{CW}px;height:150px;padding:0 30px;box-sizing:border-box;display:flex;align-items:center;gap:26px"><span class="big" style="font-size:52px;color:{RD}">0{i+1}</span><span style="font-size:34px;font-weight:700;line-height:1.3">{t}</span></div>\n'
vjs = f'        pop("#c3-badge", {cue(n, "warned") - 0.3}); pop("#c3-t", {cue(n, "warned")});\n' + "".join(
    f'        tl.fromTo(q("#c3-r{i}"), {{ opacity: 0, x: 60 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {cue(n, w)});\n' for i, (_, w) in enumerate(rows))
out[n] = story(n, 2, "AI", "India's CERT-In: AI agents under testing accessed firms' live systems", "CERT-IN ADVISORY · REPORTED 15–16 OCT", vis, vjs)

# ---------------------------------------------------------------- 04 midterm ads (AI)
n = 4
r = 135; C = 2 * math.pi * r
RX, RY = 240, 1090
vis = f"""        {stat("a4-spend", X0, 590, CW, 270, "AI-MADE MIDTERM ADS · SPEND", "$137M+", CY, "vs under $50K in the 2024 cycle", 120)}
        <svg class="full" {VB}>
          <circle cx="{RX}" cy="{RY}" r="{r}" fill="none" stroke="rgba(255,97,120,0.35)" stroke-width="42"/>
          <circle id="a4-ring" cx="{RX}" cy="{RY}" r="{r}" fill="none" stroke="{GR}" stroke-width="42" stroke-dasharray="{C*0.27:.1f} {C:.1f}" transform="rotate(-90 {RX} {RY})"/>
        </svg>
        <div class="abs" id="a4-pct" style="left:{RX - 120}px;top:{RY - 62}px;width:240px;text-align:center"><div class="big g" style="font-size:84px" id="a4-pv">27%</div><div class="mono" style="font-size:16px;margin-top:4px">WITH DISCLAIMER</div></div>
        <div class="abs" id="a4-leg" style="left:470px;top:960px;width:550px;font-size:32px;line-height:1.7">
          <div><span style="color:{GR}">■</span> Labelled as AI · 27%</div><div><span style="color:{RD}">■</span> No disclaimer · 73%</div>
          <div class="mono mut" style="font-size:19px;margin-top:14px;line-height:1.5">DATA: WESLEYAN MEDIA PROJECT · ADIMPACT</div>
        </div>
"""
vjs = f"""        pop("#a4-spend", {cue(n, "137") - 0.4}); count("#a4-spend-v", {cue(n, "137") - 0.4}, 0, 137, 0, "$", "M+", 1.1);
        tl.fromTo(q("#a4-ring"), {{ strokeDasharray: "0 {C:.1f}" }}, {{ strokeDasharray: "{C*0.27:.1f} {C:.1f}", duration: 1.0, ease: "power2.out" }}, {cue(n, "only")});
        pop("#a4-pct", {cue(n, "only")}); count("#a4-pv", {cue(n, "only")}, 0, 27, 0, "", "%", 1.0); pop("#a4-leg", {cue(n, "disclaimer")});
"""
out[n] = story(n, 3, "AI", "Over $137 million spent on AI-made US midterm ads", "NYT · WESLEYAN MEDIA PROJECT · 16 OCT", vis, vjs)

# ---------------------------------------------------------------- 05 IBM agents (AI x Quantum)
n = 5
agents = "".join(f'<rect x="{230 + (i % 3)*240}" y="{710 + (i // 3)*100}" width="140" height="70" fill="rgba(56,217,255,0.12)" stroke="{CY}" stroke-width="2" class="ag"/>' for i in range(6))
links = "".join(f'<path class="ln agl" pathLength="1" style="stroke-dasharray:1" d="M540 646 L{300 + (i % 3)*240} {710 + (i // 3)*100}"/>' for i in range(6))
vis = f"""        <svg class="full" {VB}>
          <rect id="i5-coord" x="440" y="590" width="200" height="56" fill="rgba(61,255,160,0.15)" stroke="{GR}" stroke-width="2"/>
          {links}{agents}
        </svg>
        <div class="abs mono" id="i5-cl" style="left:440px;top:604px;width:200px;text-align:center;font-size:18px;color:{GR}">COORDINATOR</div>
        <div class="abs mono mut" id="i5-al" style="left:{X0}px;top:895px;width:{CW}px;text-align:center;font-size:18px">OPEN-MODEL AGENT FACTORY</div>
        <div class="abs" id="i5-big" style="left:{X0}px;top:935px;width:{CW}px;display:flex;align-items:center;gap:30px"><div class="big g" id="i5-v" style="font-size:170px;line-height:1">52×</div>
          <div><div style="font-size:32px;font-weight:700;line-height:1.25">estimated speedup<br>QEC decoder</div><div class="mono mut" style="font-size:17px;margin-top:8px">RELAY-BP · [[144,12,12]] BB CODE</div></div></div>
        {stat("i5-cost", X0, 1150, 340, 190, "AI COST", "~$26", CY, "", 72, "padding:20px 26px")}
        {card("i5-cav", 420, 1150, 600, 190, '<div class="kick" style="color:#ffb547">CAVEAT</div><div style="font-size:28px;font-weight:700;margin-top:10px;line-height:1.3">Synthesis estimate, not a fabricated chip</div>', "padding:22px 26px;border-color:rgba(255,181,71,0.6)")}
"""
t52 = cue(n, "52")
vjs = f"""        grow("#i5-coord", 0.9); fade("#i5-cl", 0.9); draw(".agl", {cue(n, "agents") - 0.2}, 0.6);
        tl.fromTo(q(".ag"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, stagger: 0.1 }}, {cue(n, "agents")}); fade("#i5-al", {cue(n, "agents") + 0.6});
        pop("#i5-big", {t52 - 0.4}); count("#i5-v", {t52 - 0.4}, 1, 52, 0, "", "×", 1.0);
        pop("#i5-cost", {cue(n, "26")}); pop("#i5-cav", {cue(n, "compute")});
"""
out[n] = story(n, 4, "AI × QUANTUM", "IBM's AI agents design a faster quantum error-correction decoder", "IBM RESEARCH · 13 OCT", vis, vjs)

# ---------------------------------------------------------------- 06 sell-off (CHIPS)
n = 6
vis = f"""        {stat("s6-ndq", X0, 590, 470, 290, "NASDAQ · WEEK", "−4.5%", RD, "Worst week since June", 110)}
        {stat("s6-smh", 550, 590, 470, 290, "CHIP ETF (SMH)", "≈−10%", RD, "Biggest weekly drop since Apr 2025", 110)}
        {card("s6-why", X0, 920, CW, 400, f'''<div class="kick">WHAT INVESTORS CITED</div>
          <div style="display:flex;flex-direction:column;gap:14px;margin-top:22px;font-size:34px;font-weight:700"><span>· Competition from Chinese chipmakers</span><span>· Debt to fund AI build-out</span><span>· Rate worries</span></div>
          <div class="mono mut" style="font-size:21px;margin-top:24px">VOLATILITY INDEX (VIX) ABOVE 22 · FRI 16 OCT</div>''')}
"""
vjs = f"""        pop("#s6-ndq", {cue(n, "nasdaq")}); count("#s6-ndq-v", {cue(n, "nasdaq")}, 0, -4.5, 1, "", "%", 1.0);
        pop("#s6-smh", {cue(n, "chip", 2)}); pop("#s6-why", {cue(n, "ten") + 0.3});
"""
out[n] = story(n, 5, "CHIPS", "Chip stocks sink: Nasdaq's worst week since June", "CNBC · INVESTING.COM · 16 OCT", vis, vjs)

# ---------------------------------------------------------------- 07 Korea (CHIPS)
n = 7
vis = f"""        <svg class="full" {VB}>
          <path class="ln" id="k7-axis" pathLength="1" style="stroke-dasharray:1" d="M{X0} 760 H1020"/>
          <rect id="k7-band" x="100" y="730" width="760" height="60" fill="rgba(255,181,71,0.25)" stroke="{AM}" stroke-width="2"/>
        </svg>
        <div class="abs mono mut" style="left:80px;top:810px;font-size:26px">2026</div>
        <div class="abs mono" style="left:740px;top:810px;font-size:26px;color:{AM}">END-2027</div>
        <div class="abs big a" id="k7-label" style="left:120px;top:620px;font-size:76px">CHIP BOOM →</div>
        {card("k7-why", X0, 900, CW, 200, '<div class="kick">WHY</div><div style="font-size:34px;font-weight:700;margin-top:10px;line-height:1.3">Demand still outpaces supply; capacity still being added</div>', "padding:24px 30px")}
        {card("k7-who", X0, 1130, CW, 200, '<div class="kick">WHO</div><div style="font-size:34px;font-weight:700;margin-top:10px;line-height:1.3">Lee Hyoung-il, South Korea finance minister</div>', "padding:24px 30px")}
"""
vjs = f"""        draw("#k7-axis", 0.6, 0.8); fade("#k7-who", 0.9);
        tl.fromTo(q("#k7-band"), {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 1.2, ease: "power2.out" }}, {cue(n, "boom") - 0.2}); pop("#k7-label", {cue(n, "boom")});
        pop("#k7-why", {cue(n, "demand")});
"""
out[n] = story(n, 6, "CHIPS", "South Korea: the chip boom lasts at least through 2027", "CNBC · 17 OCT · IMF/WORLD BANK MEETINGS, BANGKOK", vis, vjs)

# ---------------------------------------------------------------- 08 China exports (CHIPS)
n = 8
vis = f"""        <div class="abs" id="x8-big" style="left:{X0}px;top:590px;width:{CW}px"><div class="big a" id="x8-v" style="font-size:200px;line-height:1">+136%</div>
          <div style="font-size:34px;font-weight:700;margin-top:8px">IC exports, September, year on year</div></div>
        {stat("x8-val", X0, 900, 560, 180, "SEPTEMBER VALUE", "~US$45bn", CY, "", 76, "padding:20px 26px")}
        {stat("x8-vol", 640, 900, 380, 180, "VOLUME", "+1%", MUT, "", 76, "padding:20px 26px")}
        {card("x8-why", X0, 1110, CW, 220, '<div class="kick">DRIVER</div><div style="font-size:36px;font-weight:700;margin-top:12px;line-height:1.3">Higher prices — memory shortage from the AI build-out</div>', "padding:24px 30px")}
"""
vjs = f"""        pop("#x8-big", {cue(n, "136") - 0.4}); count("#x8-v", {cue(n, "136") - 0.4}, 0, 136, 0, "+", "%", 1.1);
        pop("#x8-val", {cue(n, "45")}); pop("#x8-vol", {cue(n, "prices") - 0.4}); pop("#x8-why", {cue(n, "prices")});
"""
out[n] = story(n, 7, "CHIPS", "China's chip exports jump 136% in September", "SCMP · CHINA CUSTOMS DATA · 14 OCT", vis, vjs)

# ---------------------------------------------------------------- 09 Intel (CHIPS)
n = 9
vis = f"""        {stat("t9-stake", X0, 590, CW, 260, "US GOVERNMENT STAKE (2025)", "9.9%", AM, "Passive · no board seat", 120)}
        {card("t9-q", X0, 880, CW, 270, '<div class="kick">LIP-BU TAN · INTEL CEO</div><div style="font-size:42px;font-weight:800;margin-top:16px;line-height:1.25">The stake gives Washington no say in strategy or governance</div>', "padding:26px 30px")}
        {card("t9-o", X0, 1180, CW, 150, '<div class="kick">ALSO INVESTED</div><div style="font-size:36px;font-weight:700;margin-top:12px">SoftBank · Nvidia</div>', "padding:22px 30px")}
"""
vjs = f"""        pop("#t9-stake", {cue(n, "stake") - 0.3}); count("#t9-stake-v", {cue(n, "stake") - 0.3}, 0, 9.9, 1, "", "%", 0.9);
        pop("#t9-q", {cue(n, "washington")}); pop("#t9-o", {cue(n, "business") - 0.2});
"""
out[n] = story(n, 8, "CHIPS", "Intel's CEO: US stake brings no government say", "NIKKEI ASIA · 17 OCT", vis, vjs)

# ---------------------------------------------------------------- 10 Google (QUANTUM)
n = 10
grid = "".join(f'<circle cx="{354 + (i % 7)*62}" cy="{915 + (i // 7)*52}" r="13" class="qb" fill="{GR if (i*7) % 5 else CY}" opacity="0.85"/>' for i in range(28))
vis = f"""        {stat("g10-err", X0, 590, 470, 280, "FEWER ERRORS · VS NO CULTIVATION", "40×", GR, "", 110)}
        {stat("g10-fid", 550, 590, 470, 280, "MAGIC-STATE FIDELITY", "99.99%", CY, "", 100)}
        <svg class="full" {VB}>{grid}</svg>
        <div class="abs mono" id="g10-chip" style="left:{X0}px;top:1090px;width:{CW}px;text-align:center;font-size:20px;color:{GR}">WILLOW · 105 SUPERCONDUCTING QUBITS</div>
        {card("g10-cav", X0, 1150, CW, 180, '<div class="kick" style="color:#ffb547">CAVEATS</div><div style="font-size:30px;font-weight:700;margin-top:10px;line-height:1.35">~92% of attempts discarded · must be proven at much larger scale</div>', "padding:22px 28px;border-color:rgba(255,181,71,0.6)")}
"""
vjs = f"""        tl.fromTo(q(".qb"), {{ opacity: 0, scale: 0.3 }}, {{ opacity: 0.85, scale: 1, transformOrigin: "50% 50%", duration: 0.3, stagger: 0.03 }}, 0.8); fade("#g10-chip", 1.4);
        pop("#g10-err", {cue(n, "cutting")}); pop("#g10-fid", {cue(n, "99")}); pop("#g10-cav", {cue(n, "fidelity") + 0.4});
"""
out[n] = story(n, 9, "QUANTUM", "Google cultivates 'magic states' on its Willow chip", "SCIENCE · GOOGLE QUANTUM AI · 15 OCT", vis, vjs)

# ---------------------------------------------------------------- 11 DARPA (QUANTUM)
n = 11
cos = [("Atom Computing", "NEUTRAL ATOMS", "atom"), ("Diraq", "SILICON SPIN QUBITS", "diraq"), ("IBM", "SUPERCONDUCTING", "ibm"), ("IonQ", "TRAPPED IONS", "ionq")]
vis = f"""        <div class="abs kick" id="d11-k" style="left:{X0}px;top:590px;width:{CW}px;font-size:21px;line-height:1.5">QUANTUM BENCHMARKING INITIATIVE · STAGE C (FINAL VERIFICATION)</div>
"""
for i, (nm, tech, _) in enumerate(cos):
    vis += card(f"d11-c{i}", X0 + (i % 2)*490, 680 + (i // 2)*190, 470, 170, f'<div style="font-size:40px;font-weight:800">{nm}</div><div class="mono" style="font-size:19px;margin-top:14px;color:{GR}">{tech}</div>', "padding:26px 28px") + "\n"
vis += card("d11-j", X0, 1080, 470, 230, '<div class="kick">ALREADY IN STAGE C</div><div style="font-size:34px;font-weight:700;margin-top:12px;line-height:1.3">Microsoft<br>PsiQuantum</div>', "padding:24px 28px") + "\n"
vis += stat("d11-goal", 550, 1080, 470, 230, "TARGET", "Utility-scale", GR, "by 2033", 58, "padding:24px 28px") + "\n"
vjs = '        fade("#d11-k", 0.7);\n' + "".join(f'        pop("#d11-c{i}", {cue(n, w)});\n' for i, (_, _, w) in enumerate(cos))
vjs += f'        pop("#d11-j", {cue(n, "final")}); pop("#d11-goal", {cue(n, "initiative")});\n'
out[n] = story(n, 10, "QUANTUM", "DARPA moves four quantum firms into its final test stage", "DARPA QBI · 7 OCT", vis, vjs)

# ---------------------------------------------------------------- 12 close
n = 12
recap = [("AI", "Clark: ~$44T scenario"), ("AI", "CERT-In agent advisory"), ("AI", "$137M AI midterm ads"), ("AI × QUANTUM", "IBM agents · 52×"),
         ("CHIPS", "Nasdaq −4.5% week"), ("CHIPS", "Korea: boom to 2027"), ("CHIPS", "China exports +136%"), ("CHIPS", "Intel: no US say"),
         ("QUANTUM", "Google magic states"), ("QUANTUM", "DARPA QBI Stage C")]
stage = f'        <div class="abs kick" id="z-k" style="left:{X0}px;top:108px;font-size:22px">THE TOP 10 · 18 OCT 2026</div>\n'
for i, (cat, t) in enumerate(recap):
    col = CAT[cat]
    stage += f'        <div class="abs glass z-r" style="left:{X0}px;top:{150 + i*119}px;width:{CW}px;height:104px;padding:0 28px;box-sizing:border-box;display:flex;align-items:center;gap:28px"><span class="big" style="font-size:56px;color:{col}">{i+1:02d}</span><span style="font-size:36px;font-weight:700">{t}</span><span class="mono" style="margin-left:auto;font-size:16px;color:{col}">{cat}</span></div>\n'
js = f'        fade("#z-k", 0.1); tl.fromTo(q(".z-r"), {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.35, stagger: 0.12, ease: "power3.out" }}, 0.2);\n'
out[n] = (stage, js)


# ---------------------------------------------------------------- write frames
os.makedirs("compositions/frames", exist_ok=True)
for n, dur, src in FRAMES:
    fid = os.path.splitext(os.path.basename(src))[0]
    stage, js = out[n]
    open(src, "w").write(shell(fid, n, dur, stage, js, final=(n == len(FRAMES))))
    print(f"  {src}  ({dur}s)")

# ---------------------------------------------------------------- HUD overlay (top bar + ticker), full length
items = ["AI · CLARK: ~$44T US OUTPUT SCENARIO BY 2030", "AI · CERT-IN CRITICAL ADVISORY CIAD-2026-0049", "AI · $137M+ ON AI-MADE MIDTERM ADS · 27% LABELLED",
         "IBM · AI AGENTS 52× EST. DECODER SPEEDUP · ~$26", "NASDAQ −4.5% WEEK · WORST SINCE JUNE", "SMH ≈−10% WEEK",
         "KOREA: CHIP BOOM THROUGH 2027", "CHINA IC EXPORTS +136% · ~US$45BN (SEP)", "INTEL: US STAKE 9.9% · NO SAY IN STRATEGY",
         "GOOGLE WILLOW · 40× FEWER ERRORS · 99.99% FIDELITY", "DARPA QBI STAGE C · ATOM · DIRAQ · IBM · IONQ"]
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
      <span>TOP 10 · AI · CHIPS · QUANTUM</span><span class="live" id="hud-live">● LIVE</span><span>18 OCT 2026</span>
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
