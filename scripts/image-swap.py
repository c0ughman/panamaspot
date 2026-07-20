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
    cap = item.get(f"caption_{lang}") or item.get("caption_en") or item.get("caption_es") or ""
    cap = html.escape(cap)
    if needs_credit(item.get("license")):
        artist = ARTIST.get(item["url"], "").strip()
        artist = re.split(r"\s+from\s+", artist)[0].strip()  # drop Flickr "… from Town, Country"
        if len(artist) > 45:
            artist = artist[:45].rsplit(" ", 1)[0] + "…"
        artist = html.escape(artist) if artist else "Wikimedia Commons"
        photo = "Foto" if lang == "es" else "Photo"
        who = f"{photo}: {artist}, {item['license']} · Wikimedia Commons" if artist != "Wikimedia Commons" else f"{item['license']} · Wikimedia Commons"
        credit = f'<span class="img-credit" style="display:block;opacity:.55;font-size:.82em;margin-top:2px">— {who}</span>'
        cap = f"{cap} {credit}" if cap else credit
    return cap

def esc_bg(url):
    # background-image urls in these files HTML-escape the & as &amp;
    return url.replace("&", "&amp;")

def build_figure(item, key, lang):
    url = esc_bg(item["url"])
    cap = build_caption(item, lang)
    return (f'<figure class="art-inline-img" data-imgset="{key}">'
            f'<div class="imgph photo" style="background-image:url(\'{url}\')"></div>'
            f'<figcaption>{cap}</figcaption></figure>')

def set_hero(s, new_url):
    """Update all four hero-URL locations independently so pages whose
    div/og/twitter/jsonld URLs disagree still end up consistent."""
    new_plain = new_url
    new_bg = esc_bg(new_url)
    hits = 0
    s, n = re.subn(r'(<div class="art-hero-img-full" style="background-image:url\(\')[^\']+(\'\))',
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
    return re.sub(r'<figure class="art-inline-img"[^>]*>.*?</figure>', '', s)

def fill_slots(s, items):
    """Overwrite every remaining imgph-photo background (the art-gallery-grid and
    bento cards) with the selected images, cycling. Must run AFTER strip_inline so
    only gallery/bento slots remain. Removes the old wrong-location images that
    lived only in these containers. Captions/headings in those blocks are topical
    and left intact."""
    if not items:
        return s, 0
    box = {"i": 0}
    def repl(m):
        it = items[box["i"] % len(items)]; box["i"] += 1
        return m.group(1) + esc_bg(it["url"]) + m.group(2)
    s, n = re.subn(r'(<div class="imgph photo" style="background-image:url\(\')[^\']+(\'\))', repl, s)
    return s, n

def place_inline(s, key, items, lang):
    """Insert ONE figure after each section <h2>, spread through the article to
    break up the text (never stacked)."""
    secs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
    n = min(len(items), len(secs))
    for i in range(n-1, -1, -1):           # end-to-start keeps offsets valid
        fig = build_figure(items[i], key, lang)
        pos = secs[i].end()
        s = s[:pos] + fig + s[pos:]
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
        s = strip_inline(s)                       # 1. clear old/previous inline figures
        s, ng = fill_slots(s, pool)               # 2. new images into gallery + bento
        s, ni = place_inline(s, key, pool, lang)  # 3. one image per section, spread
        if hero:
            s, _ = set_hero(s, hero["url"])       # 4. hero + og/twitter/jsonld
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
