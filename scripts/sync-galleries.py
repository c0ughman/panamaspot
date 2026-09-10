#!/usr/bin/env python3
"""
sync-galleries.py — make the "In pictures" grid mirror the article body again.

The grid is a copy of the page's hero + first body images. When an image pass
replaces the body photos, the grid keeps the OLD ones — and on the 2026-09
Boquete batch that meant the grid still carried the stock photos under the
fabricated captions the pass had just removed ("Rock-lined thermal pools at
Caldera Hot Springs" over a stock image), including in the alt text.

This rebuilds each existing .art-gallery-grid from the page's own hero and
art-inline-img figures, in document order. Pages with no grid are left alone —
creating one is image-review-pass2.py's job, not this one.

    python3 scripts/sync-galleries.py [--only SUBSTR]
"""
import re, sys, glob, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from img_cap import img_html, GALLERY as GW

SIZES_GALLERY = "(max-width: 900px) 50vw, 25vw"
GRID = re.compile(r'(<div class="art-gallery-grid">)(.*?)(</div></div></section>)', re.S)


def rebuild(s):
    m = GRID.search(s)
    if not m:
        return s, 0

    items = []
    h = re.search(r'art-hero-img-full"><img src="([^"]+)"[^>]*alt="([^"]*)"', s)
    if h:
        items.append((h.group(1), h.group(2)))
    for fm in re.finditer(r'<figure class="art-inline-img"[^>]*>.*?</figure>', s, re.S):
        if 'is-map' in fm.group(0)[:80]:
            continue          # a map is not a photograph; it does not belong in the grid
        um = re.search(r'src="([^"]+)"', fm.group(0))
        cm = re.search(r'<figcaption>(.*?)</figcaption>', fm.group(0), re.S)
        if um:
            items.append((um.group(1), re.sub(r"<[^>]+>", "", cm.group(1)) if cm else ""))

    items = items[:5]
    if not items:
        return s, 0

    figs = ""
    for i, (u, cap) in enumerate(items):
        cls = ' class="feature"' if i == 0 else ""
        # captions already come HTML-escaped out of the figure; don't double-escape
        alt = cap if "&" in cap and "&amp;" not in cap.replace("&amp;", "") else html.escape(html.unescape(cap))
        figs += (f'<figure{cls}><div class="imgph photo">'
                 f'{img_html(u.replace("&amp;", "&"), alt, GW, SIZES_GALLERY)}</div></figure>')

    return s[:m.start(2)] + figs + s[m.end(2):], len(items)


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    pages = sorted(glob.glob(str(ROOT / "public/articles/*.html")) +
                   glob.glob(str(ROOT / "public/es/articles/*.html")))
    for pg in pages:
        if only and only not in pg:
            continue
        p = pathlib.Path(pg)
        s = orig = p.read_text(encoding="utf-8")
        s, n = rebuild(s)
        if s != orig:
            p.write_text(s, encoding="utf-8")
            print(f"  ✓ {pg.split('public/')[-1]:<62} gallery={n}")


if __name__ == "__main__":
    main()
