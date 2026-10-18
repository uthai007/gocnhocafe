#!/usr/bin/env python3
"""After assembly: local GSAP, mount the HUD overlay, tag captions, restyle captions as dark HUD glass."""
import re
idx = open("index.html").read()
idx = re.sub(r'<script src="https://cdn\.jsdelivr\.net/npm/gsap@[0-9.]+/dist/gsap\.min\.js"[^>]*></script>', '<script src="assets/vendor/gsap.min.js"></script>', idx)
dur = re.search(r'id="el-captions".*?data-duration="([\d.]+)"', idx, re.S).group(1)
if 'id="el-hud"' not in idx:
    host = f'''      <div
        id="el-hud"
        class="scene"
        data-composition-id="hud"
        data-composition-src="compositions/hud.html"
        data-start="0"
        data-duration="{dur}"
        data-track-index="3"
      ></div>
'''
    idx = idx.replace('      <div\n        id="el-captions"', host + '      <div\n        id="el-captions"', 1)
idx = idx.replace('        id="el-captions"\n        class="scene"', '        id="el-captions"\n        data-track-kind="captions"\n        class="scene"')
open("index.html", "w").write(idx)

cap = open("compositions/captions.html").read()
cap = re.sub(r'<script src="https://cdn\.jsdelivr\.net/npm/gsap@[0-9.]+/dist/gsap\.min\.js"[^>]*></script>', '<script src="assets/vendor/gsap.min.js"></script>', cap)
override = """<style data-hud-captions>
  :root { --cap-band-top: 866px; --cap-band-height: 160px; }
  .caption-pill { background: rgba(5,16,36,0.84); border: 1.5px solid rgba(56,217,255,0.6); border-radius: 6px;
    box-shadow: 0 0 26px rgba(56,217,255,0.28), inset 0 0 18px rgba(56,217,255,0.10); padding: 14px 40px 18px; }
  .caption-line { font-family: Montserrat, sans-serif; font-weight: 700; font-size: 44px; letter-spacing: 0; line-height: 1.22; }
  .caption-word, .caption-word.cap-num { color: rgba(233,247,255,0.42); }
  .caption-word.is-active { color: #38d9ff; border-bottom: 3px solid #38d9ff; text-shadow: 0 0 14px rgba(56,217,255,0.8); }
  .caption-word.is-spoken, .caption-word.cap-brand, .caption-word.cap-cta { color: #e9f7ff; }
</style>
"""
cap = re.sub(r"<style data-hud-captions>.*?</style>\n", "", cap, flags=re.S)
cap = cap.replace("</template>", override + "</template>", 1)
open("compositions/captions.html", "w").write(cap)
print("post-assemble ok")
