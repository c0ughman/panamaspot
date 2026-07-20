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

def _chunk(items, n):
    """Split items into n ordered groups as evenly as possible (front-loaded)."""
    if n <= 0:
        return []
    groups = [[] for _ in range(n)]
    base, extra = divmod(len(items), n)
    idx = 0
    for g in range(n):
        take = base + (1 if g < extra else 0)
        groups[g] = items[idx:idx+take]
        idx += take
    return groups

def rebuild_gallery(s, key, items, lang):
    figs_new = [build_figure(it, key, lang) for it in items]
    # prior run's tagged figures anchor the rebuild; else the page's scattered inline figures
    anchors = list(re.finditer(r'<figure[^>]*data-imgset="'+re.escape(key)+r'"[^>]*>.*?</figure>', s))
    if not anchors:
        anchors = list(re.finditer(r'<figure class="art-inline-img">.*?</figure>', s))
    if not anchors:
        print("    ! no gallery figures found to anchor"); return s, 0
    spans = [(m.start(), m.end()) for m in anchors]
    # Distribute the selected figures across the anchor positions so images stay
    # spread through the article (one-per-section design) instead of clustering.
    groups = _chunk(figs_new, len(spans))
    for i in range(len(spans)-1, -1, -1):
        st, en = spans[i]
        repl = "".join(groups[i]) if i < len(groups) else ""
        s = s[:st] + repl + s[en:]
    return s, len(figs_new)

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
        # gallery = the 'use' list, minus any entry identical to the hero (avoid dup)
        hero = data.get("hero")
        hero_url = hero["url"] if hero else None
        gallery = [it for it in data["use"] if it["url"] != hero_url]
        if hero:
            s, _ = set_hero(s, hero["url"])
        s, n = rebuild_gallery(s, key, gallery, lang)
        p.write_text(s, encoding="utf-8")
        print(f"  ✓ {page}  hero={'set' if hero else '—'}  figures={n}  [{lang}]")

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
