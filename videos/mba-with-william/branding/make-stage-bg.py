#!/usr/bin/env python3
"""Build seamless 12 s stage-background loops (no William, no text) in 9:16 and 16:9.
Render each with:  npx hyperframes render -q delivery -o ../stage-bg-<name>.mp4"""
import os, random, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
LOOP = 12


def page(name, W, H):
    rnd = random.Random(42)
    cw = round(W * (0.11 if W < H else 0.065))          # curtain width
    floor_top = round(H * (0.75 if W < H else 0.78))
    beam_w = round(W * (0.62 if W < H else 0.42))
    dots = []
    for _ in range(70 if W < H else 90):
        x = rnd.uniform(0.5 - beam_w / W / 2.2, 0.5 + beam_w / W / 2.2) * W
        y = rnd.uniform(0, H)
        r = rnd.uniform(1.5, 4.0)
        a = rnd.uniform(0.25, 0.7)
        dots.append(f'<span class="p" style="left:{x:.0f}px;top:{y:.0f}px;width:{r*2:.1f}px;height:{r*2:.1f}px;opacity:{a:.2f}"></span>')
    dust = "".join(dots)
    html = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #05070d; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      .layer {{ position: absolute; inset: 0; }}
      #wall {{ background:
          radial-gradient(ellipse 60% 45% at 50% 35%, #1d2f5a 0%, rgba(11, 16, 32, 0) 70%),
          linear-gradient(180deg, #0b1020 0%, #070a14 70%, #05070d 100%); }}
      #glow {{ background: radial-gradient(ellipse 40% 30% at 50% 40%, rgba(90, 130, 255, 0.22) 0%, rgba(90, 130, 255, 0) 70%); }}
      .curtain {{ position: absolute; top: 0; height: {floor_top}px; width: {cw}px;
        background: repeating-linear-gradient(90deg, #4a0f1c 0 {cw*0.22:.0f}px, #6b1626 {cw*0.22:.0f}px {cw*0.37:.0f}px, #3a0b16 {cw*0.37:.0f}px {cw*0.5:.0f}px); opacity: 0.9; }}
      #cl {{ left: 0; border-bottom-right-radius: {cw*0.75:.0f}px; }}
      #cr {{ right: 0; border-bottom-left-radius: {cw*0.75:.0f}px; }}
      #valance {{ position: absolute; left: 0; right: 0; top: 0; height: {H*0.035:.0f}px;
        background: repeating-linear-gradient(90deg, #5a1222 0 {W*0.03:.0f}px, #7a1a2c {W*0.03:.0f}px {W*0.045:.0f}px); }}
      #floor {{ position: absolute; left: 0; right: 0; top: {floor_top}px; bottom: 0;
        background: linear-gradient(180deg, #3a2a20 0%, #241912 45%, #120c09 100%); border-top: {max(4, H*0.004):.0f}px solid #6d5240; }}
      #boards {{ position: absolute; left: 0; right: 0; top: {floor_top}px; bottom: 0; opacity: 0.25;
        background: repeating-linear-gradient(90deg, rgba(0,0,0,0) 0 {W*0.09:.0f}px, rgba(0,0,0,0.6) {W*0.09:.0f}px {W*0.09+2:.0f}px); }}
      #beam-wrap {{ position: absolute; left: {(W-beam_w)/2:.0f}px; top: 0; width: {beam_w}px; height: {floor_top + H*0.06:.0f}px; }}
      #beam {{ position: absolute; inset: 0;
        background: linear-gradient(180deg, rgba(255, 240, 210, 0.20) 0%, rgba(255, 240, 210, 0.05) 100%);
        clip-path: polygon(44% 0, 56% 0, 100% 100%, 0 100%); }}
      #pool {{ position: absolute; left: {(W - beam_w*1.1)/2:.0f}px; top: {floor_top - H*0.03:.0f}px; width: {beam_w*1.1:.0f}px; height: {H*0.11:.0f}px;
        border-radius: 50%; background: radial-gradient(ellipse at center, rgba(255, 236, 196, 0.42) 0%, rgba(255, 236, 196, 0) 70%); }}
      #dust-wrap {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; overflow: hidden;
        clip-path: polygon({50-beam_w/W*50*0.25:.1f}% 0, {50+beam_w/W*50*0.25:.1f}% 0, {50+beam_w/W*50:.1f}% {floor_top/H*100:.1f}%, {50-beam_w/W*50:.1f}% {floor_top/H*100:.1f}%); }}
      #dust {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H*2}px; }}
      .tile {{ position: absolute; left: 0; width: {W}px; height: {H}px; }}
      .p {{ position: absolute; display: block; border-radius: 50%; background: #fff3d6; }}
      #vignette {{ background: radial-gradient(ellipse 75% 70% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{LOOP}" data-width="{W}" data-height="{H}">
      <div id="wall" class="layer"></div>
      <div id="glow" class="layer"></div>
      <div id="cl" class="curtain"></div>
      <div id="cr" class="curtain"></div>
      <div id="valance"></div>
      <div id="floor"></div>
      <div id="boards"></div>
      <div id="beam-wrap"><div id="beam"></div></div>
      <div id="pool"></div>
      <div id="dust-wrap"><div id="dust"><div class="tile" style="top:0">{dust}</div><div class="tile" style="top:{H}px">{dust}</div></div></div>
      <div id="vignette" class="layer"></div>
    </div>
    <script>
      const L = {LOOP};
      const tl = gsap.timeline({{ paused: true }});
      // light "breathing": 3 s each way, ends where it started
      tl.fromTo("#beam", {{ opacity: 0.75 }}, {{ opacity: 1, duration: 3, ease: "sine.inOut", yoyo: true, repeat: 3 }}, 0);
      tl.fromTo("#pool", {{ opacity: 0.8 }}, {{ opacity: 1, duration: 3, ease: "sine.inOut", yoyo: true, repeat: 3 }}, 0);
      tl.fromTo("#glow", {{ opacity: 1 }}, {{ opacity: 0.6, duration: 6, ease: "sine.inOut", yoyo: true, repeat: 1 }}, 0);
      // gentle beam sway from the lamp: -1.5deg -> 1.5deg -> -1.5deg
      tl.fromTo("#beam-wrap", {{ rotation: -1.5 }}, {{ rotation: 1.5, transformOrigin: "50% 0%", duration: 6, ease: "sine.inOut", yoyo: true, repeat: 1 }}, 0);
      // dust drifts up exactly one tile per loop -> seamless
      tl.fromTo("#dust", {{ y: 0 }}, {{ y: -{H}, duration: L, ease: "none" }}, 0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
    d = os.path.join(ROOT, name)
    os.makedirs(os.path.join(d, "assets/vendor"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "..", "assets/vendor/gsap.min.js"), os.path.join(d, "assets/vendor/gsap.min.js"))
    open(os.path.join(d, "index.html"), "w").write(html)


page("stage-bg-vertical", 1080, 1920)
page("stage-bg-horizontal", 1920, 1080)
print("ok")
