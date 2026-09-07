#!/usr/bin/env python3
"""
fix-page-images.py — put verifiably-Panamanian photos on three pages.

Stock photos can be captioned to say anything; a Wikimedia Commons file names
the place in its own filename and carries a source page, so the subject can
actually be checked. These three pages needed that:

  renting-a-car-in-panama   its photos showed no recognisable Panama at all
  best-time-to-visit-panama its hero showed a part of the country the client
                            does not want fronting the page
  red-frog-beach            had no body images whatsoever — only a hero and the
                            related-guide thumbnails

Every replacement below is a Commons file already in use elsewhere on the site,
so provenance and dimensions are known. Captions describe what the file itself
says it shows — nothing is asserted about a photo that its source does not.

Idempotent.
    python3 scripts/fix-page-images.py
"""
import re, sys, glob, html, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from img_cap import img_html, HERO, GALLERY as GALLERY_W

SIZES_INLINE = "(max-width: 768px) 100vw, 768px"
SIZES_GALLERY = "(max-width: 900px) 50vw, 25vw"

def commons_pool():
    """filename -> a live thumb URL, harvested from pages that already use it."""
    pool = {}
    for f in sorted(glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html")):
        s = pathlib.Path(f).read_text(encoding="utf-8")
        for u in re.findall(r'src="(https://upload\.wikimedia\.org[^"]+)"', s):
            u = u.replace("&amp;", "&")
            fn = urllib.parse.unquote(u.split("/")[-1])
            pool.setdefault(re.sub(r"^\d+px-", "", fn), u)
    return pool

POOL = commons_pool()

def orig_url(fn):
    """The Commons ORIGINAL url for a filename (img_cap caps it per context)."""
    u = POOL[fn]
    m = re.match(r"^(https://upload\.wikimedia\.org/wikipedia/commons/)thumb/([0-9a-f]/[0-9a-f]{2})/([^/]+)/\d+px-", u)
    return f"{m.group(1)}{m.group(2)}/{m.group(3)}" if m else u

# Pages whose gallery grid also has to be re-stocked (filenames, in order).
GALLERY = {
"public/articles/renting-a-car-in-panama.html": [
  ("Street_Scene_-_El_Valle_de_Anton.jpg", "A street in El Valle de Antón, Coclé"),
  ("Calle_en_Isla_Taboga_-_Panamá.jpg", "A village street on Isla Taboga, Panamá"),
  ("Aerial_view_of_Boquete,_Panama.jpg", "Boquete, Chiriquí, from the air"),
  ("Panama_skyline.jpg", "The Panama City skyline"),
  ("Portobelo_Ruins_and_bay.jpg", "Portobelo and its bay, Colón province"),
],
}

# page -> (hero filename or None, [(section_index, filename, caption), …])
PLAN = {
"public/articles/renting-a-car-in-panama.html": (
  "Boquete,_Alto_Jaramillo,_Chiriquí,_República_de_Panamá.png", [
  (0, "Street_Scene_-_El_Valle_de_Anton_-_Cocle_Province_-_Panama_-_03_(11503415213).jpg",
      "A street in El Valle de Antón, Coclé — small-town driving is most of what a rental does"),
  (4, "Aerial_view_of_the_Province_of_Chiriqui,_Republic_of_Panama_02.jpg",
      "Chiriquí province from the air — the mountain roads west of David"),
  (5, "Calle_Casco_Viejo.jpg",
      "A street in Casco Viejo, Panama City — narrow, one-way, and hard to park in"),
  (6, "Panama_City_Skyline_180107.jpg",
      "Panama City — tolls on the corredores and paid parking are city-only costs"),
  (8, "Countryside_around_El_Valle_(03).jpg",
      "Countryside around El Valle de Antón — the kind of route with no bus and no Uber"),
]),
"public/articles/best-time-to-visit-panama.html": (
  "Aerial_view_of_the_Province_of_Chiriqui,_Republic_of_Panama_06.jpg", []),
"public/articles/red-frog-beach-bocas-del-toro.html": (None, [
  (0, "Bocas_del_Toro_Panama.jpg", "The Bocas del Toro archipelago, Panama"),
  (1, "Bocas_Town_--_Isla_Colon.jpg", "Bocas Town on Isla Colón — where the water taxis to Bastimentos leave from"),
  (3, "Bocas_del_Toro_Panama_6.jpg", "Caribbean water in the Bocas del Toro archipelago"),
  (6, "Bocas1.jpg", "The Bocas del Toro archipelago — Red Frog Beach sits inside the marine park"),
  (7, "Bocas_del_Toro_Province,_Panama_-_panoramio_(13).jpg",
      "A beach in Bocas del Toro province, Panama"),
]),
}

def set_hero(s, fn):
    url = orig_url(fn)
    alt = re.search(r'art-hero-img-full"><img[^>]*alt="([^"]*)"', s).group(1)
    img = img_html(url, alt, HERO, "100vw", eager=True)
    s = re.sub(r'(art-hero-img-full">)<img[^>]*>', lambda m: m.group(1) + img, s, count=1)
    big = re.search(r'art-hero-img-full"><img src="([^"]+)"', s).group(1)
    for pat in (r'(<meta content=")[^"]*(" property="og:image"/>)',
                r'(<meta content=")[^"]*(" name="twitter:image"/>)'):
        s = re.sub(pat, lambda m: m.group(1) + big + m.group(2), s, count=1)
    s = re.sub(r'(<link rel="preload" as="image" href=")[^"]*"[^>]*/>',
               lambda m: m.group(1) + big + '" fetchpriority="high"/>', s, count=1)
    return s

def figure(fn, caption):
    url = orig_url(fn)
    alt = html.escape(caption)
    return (f'<figure class="art-inline-img" data-inlined="1">'
            f'<div class="imgph photo">{img_html(url, alt, GALLERY_W, SIZES_INLINE)}</div>'
            f'<figcaption>{alt}</figcaption></figure>')

def main():
    for page, (hero, swaps) in PLAN.items():
        p = ROOT / page
        s = orig = p.read_text(encoding="utf-8")
        if hero:
            s = set_hero(s, hero)
        if swaps:
            s = re.sub(r'<figure class="art-inline-img" data-inlined="1">.*?</figure>', "", s, flags=re.S)
            hs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
            pts = []
            for si, fn, cap in swaps:
                if si >= len(hs) or fn not in POOL:
                    print(f"  ! skip {fn[:40]} on {page}"); continue
                start = hs[si].end()
                nxt = hs[si + 1].start() if si + 1 < len(hs) else len(s)
                pm = re.search(r"</p>", s[start:nxt])
                pts.append((start + pm.end() if pm else start, fn, cap))
            for off, fn, cap in sorted(pts, reverse=True):
                s = s[:off] + figure(fn, cap) + s[off:]
        ng = 0
        for fn, cap in GALLERY.get(page, []):
            if fn not in POOL:
                print(f"  ! skip gallery {fn[:40]}"); continue
            g = re.search(r'<div class="art-gallery-grid">.*?</section>', s, re.S)
            if not g:
                break
            figs = re.findall(r"<figure[^>]*>.*?</figure>", g.group(0), re.S)
            if ng >= len(figs):
                break
            new = re.sub(r"<img\b[^>]*>",
                         img_html(orig_url(fn), html.escape(cap), GALLERY_W, SIZES_GALLERY),
                         figs[ng], count=1)
            s = s[:g.start()] + g.group(0).replace(figs[ng], new, 1) + s[g.end():]
            ng += 1
        if s != orig:
            p.write_text(s, encoding="utf-8")
            print(f"  ✓ {page.replace('public/','')}  hero={'set' if hero else '—'}  inline={len(swaps)}  gallery={ng}")

if __name__ == "__main__":
    main()
