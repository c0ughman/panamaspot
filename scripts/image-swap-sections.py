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
import re, json, pathlib, html, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import cap, HERO, GALLERY

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
        ("s4", "Taboga Island", "en", 2),
        ("s5", "Portobelo", "en", 2),
        ("s7", "Gatún Lake / Monkey Island", "en", 2),
    ],
    "public/es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo.html": [
        ("s2", "Cinta Costera / Mercado de Mariscos", "es", 1),
        ("s4", "Cinta Costera / Mercado de Mariscos", "es", 1),  # Mercado shot (tail of set)
        ("s5", "Panamá Viejo ruins", "es", 1),
    ],
}

# Optional hero override per section page (replaces the leftover old hero).
PAGE_HERO = {
    # Taboga Island street scene (user's pick), anchored to the bottom so the
    # foreground/street shows instead of a centered crop.
    "public/articles/day-trips-from-panama-city.html":
        ("https://upload.wikimedia.org/wikipedia/commons/c/c0/Calle_en_Isla_Taboga_-_Panam%C3%A1.jpg", "en", "center bottom"),
}

def seckey(page, sid, cat):
    return re.sub(r"[^a-z0-9]+", "-", f"{sid}-{cat}".lower()).strip("-")[:48]

def needs_credit(lic): return (lic or "").lower().startswith("cc by")

def caption(item, lang):
    # description-only; credits live in the per-page "Image credits" block.
    return html.escape(item.get(f"caption_{lang}") or item.get("caption_en") or item.get("caption_es") or "")

def figure(item, key, lang):
    url = cap(item["url"], GALLERY).replace("&", "&amp;")
    capt = caption(item, lang)
    return (f'<figure class="art-inline-img" data-imgsec="{key}">'
            f'<div class="imgph photo" role="img" aria-label="{capt}" style="background-image:url(\'{url}\')"></div>'
            f'<figcaption>{capt}</figcaption></figure>')

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

def fill_slots(s, items, lang):
    """Put DISTINCT images into the gallery-grid + bento (no cycling), strip their
    text, full-bleed the bento cards. Same behaviour as image-swap.py. Returns
    (s, n_used). These pages have large pools, so the bento stays filled."""
    def esc(u): return cap(u, GALLERY).replace("&", "&amp;")
    used = 0
    gm = re.search(r'<div class="art-gallery-grid">', s)
    if gm:
        gstart = gm.end(); gend = _end_of_div(s, gm.start())
        figs = re.findall(r'<figure.*?</figure>', s[gstart:gend-6], re.S)
        newfigs = []
        for fig in figs:
            if used >= len(items): break
            feat = ' class="feature"' if 'class="feature"' in fig else ''
            alt = caption(items[used], lang)
            capfig = f'<figcaption>{alt}</figcaption>' if alt else ''
            newfigs.append(f'<figure{feat}><div class="imgph photo" role="img" aria-label="{alt}" style="background-image:url(\'{esc(items[used]["url"])}\')"></div>{capfig}</figure>')
            used += 1
        s = s[:gstart] + "".join(newfigs) + s[gend-6:]
    # Leave the hand-authored "More to see" bento untouched (see image-swap.py).
    return s, used

def process(page, placements):
    p = ROOT/page
    lang = "es" if "/es/" in page else "en"
    s = p.read_text(encoding="utf-8")
    # 1) strip prior IMGSEC blocks (idempotent re-run)
    s = re.sub(r"<figure class=\"art-inline-img\" data-imgsec=\"[^\"]*\">.*?</figure>", "", s, flags=re.S)
    # 2) first run: remove the page's original generic inline figures
    s = re.sub(r"<figure class=\"art-inline-img\">.*?</figure>", "", s, flags=re.S)
    # 2b) Reserve the inline images per section (front of each category's pool,
    #     no reuse across sections), THEN build the gallery/bento pool from what
    #     is left, round-robin across categories — so the showcase is a real MIX
    #     of the destinations the page talks about, not a wall of one topic, and
    #     never duplicates an image already used inline.
    used_urls = set()
    inline_plan = []                      # (sid, cat, plang, [items])
    for sid, cat, plang, count in placements:
        d = SEL[cat]; hero = d["hero"]["url"] if d.get("hero") else None
        chosen = []
        for it in d["use"]:
            if len(chosen) >= count: break
            if it["url"] == hero or it["url"] in used_urls: continue
            chosen.append(it); used_urls.add(it["url"])
        inline_plan.append((sid, cat, plang, chosen))

    cats = list(dict.fromkeys(c for _, c, _, _ in placements))
    leftover = {c: [it for it in SEL[c]["use"]
                    if it["url"] not in used_urls
                    and (not SEL[c].get("hero") or it["url"] != SEL[c]["hero"]["url"])]
                for c in cats}
    gallery_pool, i = [], 0
    while any(leftover.values()) and i < 999:
        c = cats[i % len(cats)]
        if leftover[c]:
            gallery_pool.append(leftover[c].pop(0))
        i += 1
    s, ng = fill_slots(s, gallery_pool, lang)

    # 3) Intersperse each section's inline images THROUGH its body — one per
    #    paragraph break, spread out (never two in a row, never on the heading).
    #    Collect absolute insert points first, apply back-to-front.
    heads = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
    starts = {re.search(r'id="(s\d+)"', h.group(0)).group(1): h for h in heads}
    art_end = s.find("</article>")
    # never place a figure inside an injected CTA block (its <p> tags would
    # otherwise skew the paragraph count and break idempotency).
    cta_ranges = [(mm.start(), mm.end()) for mm in
                  re.finditer(r"<!--EVB-CTA:\w+-->.*?<!--/EVB-CTA:\w+-->", s, re.S)]
    def in_cta(pos):
        return any(a <= pos <= b for a, b in cta_ranges)
    inserts, total = [], 0
    for sid, cat, plang, items in inline_plan:
        m = starts.get(sid)
        if not m or not items:
            if items: print(f"    ! {page}: section {sid} not found")
            continue
        nxt = [h for h in heads if h.start() > m.start()]
        sec_end = nxt[0].start() if nxt else len(s)
        if art_end != -1:
            sec_end = min(sec_end, art_end)
        pend = [m.end() + mm.end() for mm in re.finditer(r'</p>', s[m.end():sec_end])]
        pend = [p for p in pend if not in_cta(p)]
        key = seckey(page, sid, cat)
        n = len(items); used_pi = set()
        for j, it in enumerate(items):
            if pend:
                pi = min(len(pend) - 1, max(0, round((j + 1) * len(pend) / (n + 1)) - 1))
                while pi in used_pi and pi < len(pend) - 1: pi += 1
                while pi in used_pi and pi > 0: pi -= 1
                used_pi.add(pi); pos = pend[pi]
            else:
                pos = m.end()
            inserts.append((pos, figure(it, key, plang)))
            total += 1
    for pos, block in sorted(inserts, key=lambda x: -x[0]):
        s = s[:pos] + block + s[pos:]
    # 4) hero override if configured
    if page in PAGE_HERO:
        entry = PAGE_HERO[page]
        url = cap(entry[0], HERO)
        pos = entry[2] if len(entry) > 2 else None
        s = re.sub(r'(<div class="art-hero-img-full"[^>]*background-image:url\(\')[^\']+(\'\))',
                   lambda m: m.group(1)+url.replace("&", "&amp;")+m.group(2), s)
        if pos:
            s = re.sub(r"(<div class=\"art-hero-img-full\"[^>]*background-image:url\('[^']+'\))(?!;background-position)",
                       lambda m: m.group(1)+f";background-position:{pos}", s, count=1)
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
