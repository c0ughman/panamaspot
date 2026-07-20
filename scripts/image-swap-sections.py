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
    # description-only; credits live in the per-page "Image credits" block.
    return html.escape(item.get(f"caption_{lang}") or item.get("caption_en") or item.get("caption_es") or "")

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

def _end_of_div(s, i):
    depth = 0; j = i
    while j < len(s):
        nd = s.find('<div', j); cd = s.find('</div>', j)
        if cd == -1: return -1
        if nd != -1 and nd < cd: depth += 1; j = nd + 4
        else:
            depth -= 1; j = cd + 6
            if depth == 0: return j
    return -1

def fill_slots(s, items):
    """Put DISTINCT images into the gallery-grid + bento (no cycling), strip their
    text, full-bleed the bento cards. Same behaviour as image-swap.py. Returns
    (s, n_used). These pages have large pools, so the bento stays filled."""
    def esc(u): return u.replace("&", "&amp;")
    used = 0
    gm = re.search(r'<div class="art-gallery-grid">', s)
    if gm:
        gstart = gm.end(); gend = _end_of_div(s, gm.start())
        figs = re.findall(r'<figure.*?</figure>', s[gstart:gend-6], re.S)
        newfigs = []
        for fig in figs:
            if used >= len(items): break
            feat = ' class="feature"' if 'class="feature"' in fig else ''
            newfigs.append(f'<figure{feat}><div class="imgph photo" style="background-image:url(\'{esc(items[used]["url"])}\')"></div></figure>')
            used += 1
        s = s[:gstart] + "".join(newfigs) + s[gend-6:]
    cards = list(re.finditer(r'<div class="(bento-card[^"]*)">', s))
    remaining = items[used:]
    if cards and len(remaining) >= len(cards):
        spans = [(m.start(), _end_of_div(s, m.start()), m.group(1)) for m in cards]
        for k in range(len(spans)-1, -1, -1):
            st, en, cls = spans[k]
            s = s[:st] + f'<div class="{cls}"><div class="imgph photo" style="position:absolute;inset:0;background-image:url(\'{esc(remaining[k]["url"])}\')"></div></div>' + s[en:]
        used += len(cards)
    elif cards:
        gm2 = re.search(r'<div class="home-bento-grid">', s)
        if gm2:
            gend2 = _end_of_div(s, gm2.start())
            ss = s.rfind('<section', 0, gm2.start()); se = s.find('</section>', gend2)
            s = s[:ss] + s[se+len('</section>'):] if ss != -1 and se != -1 else s[:gm2.start()] + s[gend2:]
    return s, used

def process(page, placements):
    p = ROOT/page
    s = p.read_text(encoding="utf-8")
    # 1) strip prior IMGSEC blocks (idempotent re-run)
    s = re.sub(r"<figure class=\"art-inline-img\" data-imgsec=\"[^\"]*\">.*?</figure>", "", s, flags=re.S)
    # 2) first run: remove the page's original generic inline figures
    s = re.sub(r"<figure class=\"art-inline-img\">.*?</figure>", "", s, flags=re.S)
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
