#!/usr/bin/env python3
"""Build transparent-background William compositions (bust + full body) from the episode template.
Render each with:  npx hyperframes render --format png-sequence --fps 1 -o <dir>   (RGBA frames)"""
import os, re, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(ROOT, "..", "scripts", "template.html")).read()
svg = re.search(r'<svg id="william".*?</svg>', tpl, re.S).group(0)
# friendly closed smile instead of the talking mouth
svg = re.sub(r'<ellipse id="w-mouth"[^>]*/>',
             '<path d="M232 192 Q250 210 268 192 Q250 200 232 192 Z" fill="#7a2f2f" />'
             '<path d="M234 193 Q250 199 266 193" stroke="#ffffff" stroke-width="3" fill="none" />', svg)
svg = re.sub(r'<path id="w-lip"[^>]*/>',
             '<path d="M230 190 Q250 212 270 190" stroke="#a5604f" stroke-width="3.5" fill="none" stroke-linecap="round" />', svg)
svg = re.sub(r'\sid="w-[a-z-]+"', "", svg)


def page(name, W, H, viewbox):
    s = svg.replace('id="william" viewBox="0 0 500 1000"', f'id="pw" viewBox="{viewbox}" preserveAspectRatio="xMidYMax meet"')
    html = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: transparent; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #pw {{ position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="1" data-width="{W}" data-height="{H}">
      {s}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.set("#pw", {{ opacity: 1 }}, 0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
    d = os.path.join(ROOT, name)
    os.makedirs(os.path.join(d, "assets/vendor"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "..", "assets/vendor/gsap.min.js"), os.path.join(d, "assets/vendor/gsap.min.js"))
    open(os.path.join(d, "index.html"), "w").write(html)


page("transparent-bust", 1080, 1080, "95 22 310 310")
page("transparent-full", 1000, 1920, "110 30 280 935")
print("ok")
