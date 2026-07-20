#!/usr/bin/env python3
"""
image-swap-sections.py — place images section-by-section on the two article
pages that cover multiple destinations in one page:

  day-trips-from-panama-city.html      (Taboga, Portobelo, Gatún, El Valle, intro)
  cinta-costera-...-panama-viejo.html  (Cinta Costera, Mercado, Panamá Viejo)

Unlike image-swap.py (one topic per page), here each section needs its own
topical images, so a blanket gallery swap won't do. This script:
  - removes the page's original generic art-inline-img figures (first run only),
  - inserts a small set of the user-selected images right after the target
    section's <h2>, wrapped in <!--IMGSEC:key-->…<!--/IMGSEC:key--> markers so
    re-runs replace rather than duplicate.

Image data + captions come from scripts/image-selections.json (same source of
truth as image-swap.py). Hero for each page is left as image-swap.py / the
existing page set it (both pages already carry an appropriate hero).

Usage:  python3 scripts/image-swap-sections.py
"""
import re, json, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEL  = json.loads((ROOT/"scripts"/"image-selections.json").read_text(encoding="utf-8"))["selections"]
ARTIST = json.loads(pathlib.Path("/tmp/artist_map.json").read_text()) if pathlib.Path("/tmp/artist_map.json").exists() else {}

# page -> list of (section-id, category-name, lang, count) placements.
# category-name must match a key in image-selections.json; count caps how many
# of that category's images land in the section (they stack, so keep it tidy).
# One image per section (never stacked); spread across as many sections as we
# have topical categories for. HERO per page set separately below.
PLACEMENTS = {
    "public/articles/day-trips-from-panama-city.html": [
        ("s1", "Panama City — sights & variety", "en", 1),
        ("s3", "El Valle waterfalls — Chorro El Macho / Las Mozas", "en", 1),
        ("s4", "Taboga Island", "en", 1),
        ("s5", "Portobelo", "en", 1),
        ("s7", "Gatún Lake / Monkey Island", "en", 1),
    ],
    "public/es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo.html": [
        ("s2", "Cinta Costera / Mercado de Mariscos", "es", 1),
        ("s4", "Cinta Costera / Mercado de Mariscos", "es", 1),  # Mercado shot (tail of set)
        ("s5", "Panamá Viejo ruins", "es", 1),
    ],
}

# Optional hero override per section page (replaces the leftover old hero).
PAGE_HERO = {
    "public/articles/day-trips-from-panama-city.html":
        ("https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=1600", "en"),
}

def seckey(page, sid, cat):
    return re.sub(r"[^a-z0-9]+", "-", f"{sid}-{cat}".lower()).strip("-")[:48]

def needs_credit(lic): return (lic or "").lower().startswith("cc by")

def caption(item, lang):
    cap = html.escape(item.get(f"caption_{lang}") or item.get("caption_en") or item.get("caption_es") or "")
    if needs_credit(item.get("license")):
        artist = re.split(r"\s+from\s+", ARTIST.get(item["url"], "").strip())[0].strip()
        if len(artist) > 45: artist = artist[:45].rsplit(" ", 1)[0] + "…"
        photo = "Foto" if lang == "es" else "Photo"
        who = f"{photo}: {html.escape(artist)}, {item['license']} · Wikimedia Commons" if artist else f"{item['license']} · Wikimedia Commons"
        cap += f'<span class="img-credit" style="display:block;opacity:.55;font-size:.82em;margin-top:2px">— {who}</span>'
    return cap

def figure(item, key, lang):
    url = item["url"].replace("&", "&amp;")
    return (f'<figure class="art-inline-img" data-imgsec="{key}">'
            f'<div class="imgph photo" style="background-image:url(\'{url}\')"></div>'
            f'<figcaption>{caption(item, lang)}</figcaption></figure>')

def images_for(cat, section_index, count):
    """Pick `count` images for a section; for a category used in two sections,
    section_index lets the 2nd section take a different slice (avoids repeats)."""
    data = SEL[cat]
    hero_url = data["hero"]["url"] if data.get("hero") else None
    pool = [it for it in data["use"] if it["url"] != hero_url]
    start = 0 if section_index == 0 else max(0, len(pool) - count)
    return pool[start:start+count] if section_index == 0 else pool[start:start+count]

def fill_slots(s, items):
    """Overwrite the gallery-grid + bento imgph backgrounds (old generic photos)
    with this page's selected images, cycling. Run after inline figures are
    stripped so only gallery/bento slots remain."""
    if not items:
        return s, 0
    box = {"i": 0}
    def repl(m):
        it = items[box["i"] % len(items)]; box["i"] += 1
        return m.group(1) + it["url"].replace("&", "&amp;") + m.group(2)
    return re.subn(r'(<div class="imgph photo" style="background-image:url\(\')[^\']+(\'\))', repl, s)

def process(page, placements):
    p = ROOT/page
    s = p.read_text(encoding="utf-8")
    # 1) strip prior IMGSEC blocks (idempotent re-run)
    s = re.sub(r"<figure class=\"art-inline-img\" data-imgsec=\"[^\"]*\">.*?</figure>", "", s)
    # 2) first run: remove the page's original generic inline figures
    s = re.sub(r"<figure class=\"art-inline-img\">.*?</figure>", "", s)
    # 2b) refill the gallery-grid + bento slots (old wrong images) with a mix of
    #     this page's category images — done before inserting section figures so
    #     it only touches the gallery/bento containers.
    pool = []
    for cat in dict.fromkeys(c for _, c, _, _ in placements):
        d = SEL[cat]; hero = d["hero"]["url"] if d.get("hero") else None
        pool += [it for it in d["use"] if it["url"] != hero]
    s, ng = fill_slots(s, pool)
    # 3) insert per section
    # track how many times each category has been placed, to vary the slice
    seen = {}
    total = 0
    for sid, cat, lang, count in placements:
        idx = seen.get(cat, 0); seen[cat] = idx + 1
        imgs = images_for(cat, idx, count)
        key = seckey(page, sid, cat)
        block = "".join(figure(it, key, lang) for it in imgs)
        m = re.search(r'(<h2[^>]*id="'+sid+r'"[^>]*>.*?</h2>)', s)
        if not m:
            print(f"    ! {page}: section {sid} not found"); continue
        s = s[:m.end()] + block + s[m.end():]
        total += len(imgs)
    # 4) hero override if configured
    if page in PAGE_HERO:
        url, _ = PAGE_HERO[page]
        s = re.sub(r'(<div class="art-hero-img-full" style="background-image:url\(\')[^\']+(\'\))',
                   lambda m: m.group(1)+url.replace("&", "&amp;")+m.group(2), s)
        for pat in (r'(<meta content=")[^"]+(" property="og:image"/>)',
                    r'(<meta content=")[^"]+(" name="twitter:image"/>)',
                    r'("image": \[\s*")[^"]+(")'):
            s = re.sub(pat, lambda m: m.group(1)+url+m.group(2), s)
    p.write_text(s, encoding="utf-8")
    print(f"  ✓ {page}  gallery/bento={ng}  section-figures={total} across {len(placements)} sections")

def main():
    for page, placements in PLACEMENTS.items():
        print(f"[{page.split('/')[-1]}]")
        process(page, placements)

if __name__ == "__main__":
    main()
