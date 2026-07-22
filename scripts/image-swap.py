#!/usr/bin/env python3
"""
image-swap.py — apply the user's curated image selections to the article pages.

Source of truth: scripts/image-selections.json (built from the interactive picker).
For each category it:
  - sets the hero image, syncing all four hero-URL locations that these pages keep
    in lockstep: the .art-hero-img-full div, og:image, twitter:image, and the
    JSON-LD "image" array.
  - rebuilds the gallery <figure class="art-inline-img"> blocks with the selected
    images and freshly-authored captions (never the old captions — reusing those
    is what put "Volcán Barú at sunrise" over a photo of Indonesia).

Attribution: CC BY / CC BY-SA images get a small credit line appended to the
caption ("— Photo: {artist}, {license} · Wikimedia Commons"). Pexels, CC0 and
Public-domain images need none.

Idempotent: every figure this script writes is tagged data-imgset="{key}". On a
re-run it finds those tagged figures and rebuilds them in place; on the first run
it uses the page's existing art-inline-img figures as the anchor set. Re-run any
time after editing image-selections.json.

This handles the 1:1 category→page pages. The two multi-category pages
(day-trips, cinta-costera) are handled by image-swap-sections.py.

Usage:  python3 scripts/image-swap.py [--only SUBSTR]
"""
import re, json, sys, pathlib, html
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import cap, HERO, GALLERY

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEL  = json.loads((ROOT/"scripts"/"image-selections.json").read_text(encoding="utf-8"))["selections"]
ARTIST = {}
amap_path = pathlib.Path("/tmp/artist_map.json")
if amap_path.exists():
    ARTIST = json.loads(amap_path.read_text())

# Pages handled by the section-aware script instead of this one.
SECTION_PAGES = {
    "public/articles/day-trips-from-panama-city.html",
    "public/es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo.html",
}

def cat_key(cat_name):
    return re.sub(r"[^a-z0-9]+", "-", cat_name.lower()).strip("-")[:40]

def needs_credit(license):
    l = (license or "").lower()
    return l.startswith("cc by")  # CC BY and CC BY-SA; not CC0 / public domain / pexels

def build_caption(item, lang):
    # Captions are description-only. Photographer credit for CC BY / CC BY-SA
    # images lives in the per-page "Image credits" block (see image-credits.py).
    cap = item.get(f"caption_{lang}") or item.get("caption_en") or item.get("caption_es") or ""
    return html.escape(cap)

def esc_bg(url):
    # background-image urls in these files HTML-escape the & as &amp;
    return url.replace("&", "&amp;")

def bento_overlay(cap):
    """A legible caption overlay for a bento image card (matches the gallery
    caption look): gradient scrim + the image's caption text."""
    if not cap:
        return ""
    return ('<div class="bento-overlay" style="background:linear-gradient('
            'transparent,rgba(0,0,0,.72));padding:44px 22px 18px;font-size:13px;'
            f'line-height:1.42;font-weight:500">{cap}</div>')

def build_figure(item, key, lang):
    url = esc_bg(cap(item["url"], GALLERY))
    capt = build_caption(item, lang)
    return (f'<figure class="art-inline-img" data-imgset="{key}">'
            f'<div class="imgph photo" role="img" aria-label="{capt}" style="background-image:url(\'{url}\')"></div>'
            f'<figcaption>{capt}</figcaption></figure>')

def set_hero(s, new_url):
    """Update all four hero-URL locations independently so pages whose
    div/og/twitter/jsonld URLs disagree still end up consistent."""
    new_plain = cap(new_url, HERO)
    new_bg = esc_bg(new_plain)
    hits = 0
    s, n = re.subn(r'(<div class="art-hero-img-full"[^>]*background-image:url\(\')[^\']+(\'\))',
                   lambda m: m.group(1)+new_bg+m.group(2), s); hits += n
    s, n = re.subn(r'(<meta content=")[^"]+(" property="og:image"/>)',
                   lambda m: m.group(1)+new_plain+m.group(2), s); hits += n
    s, n = re.subn(r'(<meta content=")[^"]+(" name="twitter:image"/>)',
                   lambda m: m.group(1)+new_plain+m.group(2), s); hits += n
    s, n = re.subn(r'("image": \[\s*")[^"]+(")',
                   lambda m: m.group(1)+new_plain+m.group(2), s); hits += n
    if hits < 4:
        print(f"    ! hero: only {hits}/4 locations updated")
    return s, hits

def strip_inline(s):
    """Remove every inline figure (this script's and the page's originals) so we
    start each run from a clean body."""
    return re.sub(r'<figure class="art-inline-img"[^>]*>.*?</figure>', '', s, flags=re.S)

def _end_of_div(s, i):
    """Given index i at a '<div', return the index just past its matching </div>."""
    depth = 0; j = i
    while j < len(s):
        nd = s.find('<div', j); cd = s.find('</div>', j)
        if cd == -1:
            return -1
        if nd != -1 and nd < cd:
            depth += 1; j = nd + 4
        else:
            depth -= 1; j = cd + 6
            if depth == 0:
                return j
    return -1

def fill_showcase(s, items, lang):
    """Put DISTINCT selected images into the art-gallery-grid and bento cards —
    no cycling/repeats — and strip all their text (captions/headings), since that
    text was written for the old images. Extra gallery figures are dropped; the
    bento block is filled full-bleed only when there are enough unique images for
    all its cards, otherwise the whole bento (heading + grid) is removed rather
    than shown half-empty. Must run AFTER strip_inline. Returns (s, n_used)."""
    used = 0
    imgs = list(items)
    # --- gallery-grid: rebuild figures, image-only (no figcaption), no repeats ---
    gm = re.search(r'<div class="art-gallery-grid">', s)
    if gm:
        gstart = gm.end()
        gend = _end_of_div(s, gm.start())
        inner = s[gstart:gend-6]
        figs = re.findall(r'<figure.*?</figure>', inner, re.S)
        newfigs = []
        for fig in figs:
            if used >= len(imgs):
                break
            feat = ' class="feature"' if 'class="feature"' in fig else ''
            alt = build_caption(imgs[used], lang)
            capfig = f'<figcaption>{alt}</figcaption>' if alt else ''
            newfigs.append(f'<figure{feat}><div class="imgph photo" role="img" aria-label="{alt}" '
                           f'style="background-image:url(\'{esc_bg(cap(imgs[used]["url"], GALLERY))}\')"></div>{capfig}</figure>')
            used += 1
        s = s[:gstart] + "".join(newfigs) + s[gend-6:]
    # The "More to see / Across the region" bento is a hand-authored editorial
    # section (structured cards: bento-body / bento-split-body / bento-overlay
    # with tag + h3 + paragraph). We deliberately DO NOT touch it — flattening it
    # into bare images destroyed that layout. Leave it exactly as templated.
    return s, used

def place_inline(s, key, items, lang):
    """Insert ONE figure per section, after that section's first paragraph so it
    sits inside the body text (and never lands adjacent to the next heading)."""
    secs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
    n = min(len(items), len(secs))
    # compute an insertion point per section: first </p> after the h2, before the
    # next section starts; fall back to just after the h2.
    points = []
    for i in range(n):
        start = secs[i].end()
        nxt = secs[i+1].start() if i+1 < len(secs) else len(s)
        pm = re.search(r'</p>', s[start:nxt])
        points.append(start + pm.end() if pm else start)
    for i in range(n-1, -1, -1):           # end-to-start keeps offsets valid
        fig = build_figure(items[i], key, lang)
        s = s[:points[i]] + fig + s[points[i]:]
    return s, n

def process(cat_name, data):
    key = cat_key(cat_name)
    for page in data["pages"]:
        if page in SECTION_PAGES:
            continue
        p = ROOT/page
        if not p.exists():
            print(f"  ! missing {page}"); continue
        lang = "es" if "/es/" in page else "en"
        s = p.read_text(encoding="utf-8")
        # image pool = the 'use' list, minus any entry identical to the hero
        hero = data.get("hero")
        hero_url = hero["url"] if hero else None
        pool = [it for it in data["use"] if it["url"] != hero_url]
        s = strip_inline(s)                                    # 1. clear inline figures
        s, ng = fill_showcase(s, list(reversed(pool)), lang)   # 2. distinct images, no text
        s, ni = place_inline(s, key, pool, lang)               # 3. one image per section
        if hero:
            s, _ = set_hero(s, hero["url"])                    # 4. hero + og/twitter/jsonld
        p.write_text(s, encoding="utf-8")
        print(f"  ✓ {page}  hero={'set' if hero else '—'}  gallery/bento={ng}  inline={ni}  [{lang}]")

def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only")+1].lower()
    for cat, data in SEL.items():
        if only and only not in cat.lower():
            continue
        if all(p in SECTION_PAGES for p in data["pages"]):
            continue  # purely section-page categories
        print(f"[{cat}]")
        process(cat, data)

if __name__ == "__main__":
    main()
