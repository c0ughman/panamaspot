#!/usr/bin/env python3
"""
hero-focus.py — set the focal point of a page's hero image.

The hero box is 140% tall and pinned at top:-20%, so an <img> with the default
object-position:50% 50% shows the vertical MIDDLE of the photo. On a sky-heavy
frame that is all sky: the Barú sunrise hero rendered as haze with the summit
cropped out entirely, and the Boquete-rooftops hero gave half a screen of empty
blue above the ridge.

  python3 scripts/hero-focus.py <page.html> <Y%> [X%]   # 50 = middle, 100 = bottom/right
"""
import re, sys, pathlib

def set_focus(path, y, x="50"):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    m = re.search(r'(art-hero-img-full"><img\b[^>]*?style=")([^"]*)(")', s)
    if not m:
        print(f"  ! {path}: no hero <img> with a style attribute"); return False
    style = re.sub(r'object-position:[^;"]*;?', '', m.group(2)).rstrip(';')
    style = f"{style};object-position:{x}% {y}%"
    s = s[:m.start(2)] + style + s[m.end(2):]
    p.write_text(s, encoding="utf-8")
    print(f"  ✓ {path.split('public/')[-1]:<56} object-position: {x}% {y}%")
    return True

if __name__ == "__main__":
    set_focus(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "50")
