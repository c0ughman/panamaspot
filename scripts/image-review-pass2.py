#!/usr/bin/env python3
"""
image-review-pass2.py — second round of the client's image notes.

  best-time-to-visit  the Bocas section takes an island photo rather than a townscape
  boat-charter        the black-and-white frame in section 3 goes; it broke the
                      flow of an otherwise all-colour page
  starfish-beach      hero reverts to the photo the page originally shipped
                      with, and the first body image is dropped
  which-bocas-island  each island section now shows THAT island: Isla Colón gets
                      Bocas Town, Bastimentos keeps Red Frog, the outer-islands
                      section gets Isla Popa. (No photograph of Isla Solarte
                      exists on Commons — that section keeps its archipelago shot.)
  pearl-islands       hero and first body image swap; San Miguel is dropped
  red-frog-beach      gains the "In pictures" gallery it never had

    python3 scripts/image-review-pass2.py
"""
import re, sys, json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from img_cap import img_html, HERO, GALLERY as GW

SIZES_INLINE  = "(max-width: 768px) 100vw, 768px"
SIZES_GALLERY = "(max-width: 900px) 50vw, 25vw"
VER = json.loads((ROOT / "scripts" / "commons-verified.json").read_text(encoding="utf-8"))

def src_of(spec):
    if isinstance(spec, tuple) and spec[0] == "raw":
        return spec[1]
    return VER[spec]["url"]

def figure(spec, caption):
    alt = html.escape(caption)
    return ('<figure class="art-inline-img" data-inlined="1" data-verified="1">'
            f'<div class="imgph photo">{img_html(src_of(spec), alt, GW, SIZES_INLINE)}</div>'
            f'<figcaption>{alt}</figcaption></figure>')

def set_hero(s, spec):
    alt = re.search(r'art-hero-img-full"><img[^>]*\balt="([^"]*)"', s).group(1)
    s = re.sub(r'(art-hero-img-full">)<img[^>]*>',
               lambda m: m.group(1) + img_html(src_of(spec), alt, HERO, "100vw", eager=True), s, count=1)
    big = re.search(r'art-hero-img-full"><img src="([^"]+)"', s).group(1)
    for pat in (r'(<meta content=")[^"]*(" property="og:image"/>)',
                r'(<meta content=")[^"]*(" name="twitter:image"/>)'):
        s = re.sub(pat, lambda m: m.group(1) + big + m.group(2), s, count=1)
    s = re.sub(r'(<link rel="preload" as="image" href=")[^"]*"[^>]*/>',
               lambda m: m.group(1) + big + '" fetchpriority="high"/>', s, count=1)
    return s

def figs_in(s, si):
    hs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
    return [m for m in re.finditer(r'<figure class="art-inline-img"[^>]*>.*?</figure>', s, re.S)
            if sum(1 for h in hs if h.start() < m.start()) == si]

PLAN = {
"best-time-to-visit-panama": {"hero": None, "drop": [],
  "body": {6: ("Bocas del Drago.jpg", "Boca del Drago in the Bocas del Toro archipelago")}},
"boat-charter-panama": {"hero": None, "drop": [3], "body": {}},
"starfish-beach-bocas-del-toro-playa-estrella-guide": {
  "hero": ("raw", "https://images.pexels.com/photos/30032075/pexels-photo-30032075.jpeg?auto=compress&cs=tinysrgb&w=1600"),
  "drop": [1], "body": {}},
"which-bocas-del-toro-island-to-stay-on": {"hero": None, "drop": [], "body": {
  2: ("Bocas Town -- Isla Colon.jpg", "Bocas Town on Isla Colón, the archipelago's hub"),
  6: ("Isla Popa, Bocas del Toro.jpg", "Isla Popa, one of the outer islands of Bocas del Toro"),
}},
"pearl-islands-panama-guide": {
  "hero": ("raw", "https://images.pexels.com/photos/37208428/pexels-photo-37208428.jpeg?auto=compress&cs=tinysrgb&w=1600"),
  "drop": [1],
  "body": {1: ("Wyspa Contadora, Archipelag Wysp Perłowych, Panama.jpg",
               "Contadora in the Archipiélago de las Perlas")}},
}

GALLERY_TPL = (
 '<section class="art-section"><div class="container">'
 '<div class="art-section-head"><span class="eyebrow">In pictures</span>'
 '<h2>{heading}</h2></div><div class="art-gallery-grid">{figs}</div></div></section>')

def build_gallery(s, heading):
    """Give a page the 'In pictures' grid, built from its own hero + body images."""
    if re.search(r'<div class="art-gallery-grid">', s):
        return s, 0
    imgs = []
    h = re.search(r'art-hero-img-full"><img src="([^"]+)"', s)
    if h: imgs.append(h.group(1))
    for m in re.finditer(r'<figure class="art-inline-img"[^>]*>.*?</figure>', s, re.S):
        mm = re.search(r'src="([^"]+)"', m.group(0))
        cm = re.search(r'<figcaption>(.*?)</figcaption>', m.group(0), re.S)
        if mm: imgs.append((mm.group(1), re.sub(r"<[^>]+>", "", cm.group(1)) if cm else ""))
    hero = imgs[0] if imgs and isinstance(imgs[0], str) else None
    body = [x for x in imgs if isinstance(x, tuple)][:4]
    items = ([(hero, re.search(r'art-hero-img-full"><img[^>]*alt="([^"]*)"', s).group(1))] if hero else []) + body
    figs = ""
    for i, (u, cap) in enumerate(items[:5]):
        cls = ' class="feature"' if i == 0 else ""
        figs += (f'<figure{cls}><div class="imgph photo">'
                 f'{img_html(u.replace("&amp;","&"), html.escape(cap), GW, SIZES_GALLERY)}</div></figure>')
    block = GALLERY_TPL.format(heading=heading, figs=figs)
    # place it where the other pages keep it: just before "The short version"
    anchor = '<section class="art-section tint"><div class="container"><div class="art-section-head"><span class="eyebrow">The short version</span>'
    if anchor in s:
        return s.replace(anchor, block + anchor, 1), len(items[:5])
    return s.replace("</main>", block + "</main>", 1), len(items[:5])

def main():
    for slug, plan in PLAN.items():
        p = ROOT / "public" / "articles" / f"{slug}.html"
        s = orig = p.read_text(encoding="utf-8")
        if plan["hero"]:
            s = set_hero(s, plan["hero"])
        for si in sorted(plan["drop"], reverse=True):
            for m in figs_in(s, si):
                s = s.replace(m.group(0), "", 1)
        for si, (spec, cap) in sorted(plan["body"].items(), reverse=True):
            f = figs_in(s, si)
            if f:
                s = s.replace(f[0].group(0), figure(spec, cap), 1)
        if s != orig:
            p.write_text(s, encoding="utf-8")
            print(f"  ✓ {slug}")
    # red-frog is the only page with no gallery at all
    p = ROOT / "public" / "articles" / "red-frog-beach-bocas-del-toro.html"
    s = p.read_text(encoding="utf-8")
    s, n = build_gallery(s, "Red Frog Beach and Isla Bastimentos")
    if n:
        p.write_text(s, encoding="utf-8")
        print(f"  ✓ red-frog-beach-bocas-del-toro  gallery built ({n} tiles)")

if __name__ == "__main__":
    main()
