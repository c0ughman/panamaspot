#!/usr/bin/env python3
"""
place-map.py — put the Boquete routes map on a page.

A map is the one image that must never be cropped: .art-inline-img sets a fixed
416px frame with object-fit:cover, which would cut roughly a quarter off a
1348x1016 map. So the figure carries an `is-map` modifier that switches the
frame to the image's own aspect ratio and object-fit:contain.

  python3 scripts/place-map.py <page.html> top      # above the opening paragraph
  python3 scripts/place-map.py <page.html> s4       # after the first prose <p> of that section
"""
import re, sys, pathlib

MAP   = "/images/boquete/boquete-cycling-map.webp"
W, H  = 1348, 1016
ALT   = ("Map of the cycling routes out of Bajo Boquete — Alto Quiel, Jaramillo, "
         "Volcancito and Palmira, with viewpoints, water and coffee stops marked")
CAP   = ("The routes out of Bajo Boquete: Alto Quiel and Jaramillo to the north, "
         "Volcancito and Palmira to the west, with viewpoints, water and coffee stops marked. "
         "Map data © Mapbox © OpenStreetMap.")

CSS = ("\n.art-inline-img.is-map .imgph{height:auto;background:#f2f0e9}"
       "\n.art-inline-img.is-map .imgph img{position:static;width:100%;height:auto;object-fit:contain}")

FIG = (f'<figure class="art-inline-img is-map" data-inlined="1" data-verified="1">'
       f'<div class="imgph photo"><img src="{MAP}" alt="{ALT}" width="{W}" height="{H}" '
       f'loading="lazy" decoding="async"></div><figcaption>{CAP}</figcaption></figure>')


def ensure_css(s):
    if ".art-inline-img.is-map" in s:
        return s
    i = s.rfind("</style>")
    return s[:i] + CSS + s[i:]


def main():
    path, where = sys.argv[1], sys.argv[2]
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    if MAP in s:
        print(f"  – {path}: map already present"); return
    s = ensure_css(s)
    art = re.search(r"(?s)<article\b.*?</article>", s)
    lo, hi = art.span()

    if where == "top":
        m = re.search(r"</p>", s[lo:hi])
        off = lo + m.end()
    else:
        hs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
        si = int(where[1:])
        start = hs[si].end()
        nxt = hs[si + 1].start() if si + 1 < len(hs) else hi
        m = re.search(r"</p>", s[start:nxt])
        off = start + (m.end() if m else 0)

    s = s[:off] + FIG + s[off:]
    p.write_text(s, encoding="utf-8")
    print(f"  ✓ {path.split('public/')[-1]:<52} map placed at {where}")


if __name__ == "__main__":
    main()
