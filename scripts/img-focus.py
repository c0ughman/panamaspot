#!/usr/bin/env python3
"""
img-focus.py — set the focal point of an inline body image.

.art-inline-img frames are a fixed 416px tall with object-fit:cover, so a
PORTRAIT photograph shows only a horizontal band from its middle — on a bird
shot that means the body and no head. Rather than reshooting every tall image
as a landscape crop, keep the tall original and choose which part of it the
frame lands on.

  python3 scripts/img-focus.py <page.html> <section-index> <Y%>
"""
import re, sys, pathlib

def main():
    path, si, y = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    hs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
    target = None
    for m in re.finditer(r'<figure class="art-inline-img[^"]*"[^>]*>.*?</figure>', s, re.S):
        if sum(1 for h in hs if h.start() < m.start()) - 1 == si:
            target = m
    if not target:
        print(f"  ! {path}: no figure in section {si}"); return
    fig = target.group(0)
    im = re.search(r'(<img\b[^>]*?style=")([^"]*)(")', fig)
    if not im:
        print(f"  ! {path}: figure in section {si} has no style attribute"); return
    style = re.sub(r'object-position:[^;"]*;?', '', im.group(2)).rstrip(';')
    new_fig = fig[:im.start(2)] + f"{style};object-position:50% {y}%" + fig[im.end(2):]
    p.write_text(s.replace(fig, new_fig, 1), encoding="utf-8")
    src = re.search(r'src="([^"]+)"', fig).group(1).split('/')[-1][:44]
    print(f"  ✓ {path.split('public/')[-1]:<50} s{si} {src}  →  50% {y}%")

if __name__ == "__main__":
    main()
