#!/usr/bin/env python3
"""
image-review-pass.py — the client's page-by-page image notes, applied.

Two kinds of change:

1. SPECIFIC swaps called out during review (a hero that framed only sky, a
   shipwreck that read as ominous, a church where a townscape belonged, and
   several sections whose photo did not match what the section is about).

2. GALLERY = CONTENT, everywhere. The "In pictures" grid held a different set
   of photos from the article body, so a page could show verified pictures of
   the real place in its text and unrelated stock underneath. The gallery is
   now rebuilt from the page's own hero + body images, which means every
   verification the body earned the gallery inherits.

    python3 scripts/image-review-pass.py
"""
import re, sys, json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from img_cap import img_html, HERO, GALLERY as GW

SIZES_INLINE  = "(max-width: 768px) 100vw, 768px"
SIZES_GALLERY = "(max-width: 900px) 50vw, 25vw"
VER = json.loads((ROOT / "scripts" / "commons-verified.json").read_text(encoding="utf-8"))

def _site_pool():
    """Commons files already used on the site but not in commons-verified.json
    (they came from the original image-selections set)."""
    import glob, urllib.parse
    pool = {}
    for f in glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html"):
        for u in re.findall(r'src="(https://upload\.wikimedia\.org[^"]+)"',
                            pathlib.Path(f).read_text(encoding="utf-8")):
            u = u.replace("&amp;", "&")
            m = re.match(r"^(https://upload\.wikimedia\.org/wikipedia/commons/)thumb/"
                         r"([0-9a-f]/[0-9a-f]{2})/([^/]+)/\d+px-", u)
            orig = f"{m.group(1)}{m.group(2)}/{m.group(3)}" if m else u
            pool.setdefault(urllib.parse.unquote(orig.split("/")[-1]), orig)
    return pool

POOL = _site_pool()

def wurl(title):
    if title in VER:
        return VER[title]["url"]
    # Commons URLs spell filenames with underscores; titles use spaces.
    for k in (title, title.replace(" ", "_")):
        if k in POOL:
            return POOL[k]
    raise KeyError(f"{title} is in neither commons-verified.json nor the site pool")

# hero: a Commons title, or ("raw", url) to restore a previous non-Commons image
# body: {section_index: (title|("raw",url), caption)}   drop: [section_index, …]
PLAN = {
"best-time-to-visit-panama": {"hero": None, "body": {
  5: ("Aerial view of Boquete, Panama.jpg", "Boquete in the Chiriquí highlands, where the dry season behaves differently"),
  6: ("Bocas Town -- Isla Colon.jpg", "Bocas Town on Isla Colón — the Caribbean calendar runs the other way"),
  11:("Feria de las Flores y el Café de Boquete 2019.jpg", "The Feria de las Flores y del Café in Boquete"),
}},
"renting-a-car-in-panama": {"hero": None, "body": {
  6: ("Street Scene - El Valle de Anton.jpg", "A street in El Valle de Antón, Coclé"),
}},
"cayos-zapatillas-snorkelling-bocas-del-toro": {"hero": None, "body": {
  1: ("Zapatillas Islands - panoramio.jpg", "Cayos Zapatillas, Bocas del Toro"),
  2: ("Zapatillas Islands - panoramio (1).jpg", "The Zapatilla cays, Bastimentos marine park"),
  3: ("Insel Zapatilla (27083959796).jpg", "Reef and shallows at Cayo Zapatilla"),
  5: ("Zapatillas Islands - panoramio (2).jpg", "Approaching the Zapatilla cays by boat"),
  8: ("Zapatillas Islands - panoramio (3).jpg", "Cayos Zapatillas, Bocas del Toro"),
}},
"how-to-get-to-bocas-del-toro": {"hero": None, "body": {
  1: ("Bocas Town -- Isla Colon.jpg", "Bocas Town on Isla Colón, where every route ends up"),
}},
"starfish-beach-bocas-del-toro-playa-estrella-guide": {
  "hero": "Starfish Beach 04036.jpg", "body": {
  1: ("Women at Starfish Beach, Boca del Drago.jpg", "The shallows at Playa Estrella, Boca del Drago"),
}},
"which-bocas-del-toro-island-to-stay-on": {"hero": None, "body": {
  1: ("Bocas del Toro Province, Panama - panoramio (15).jpg", "The Bocas del Toro archipelago"),
}},
"san-blas-islands-panama-guna-yala-guide": {
  "hero": "Isla Perro en la Comarca Guna Yala.JPG", "body": {
  1: ("San Blas Islands.jpg", "The San Blas islands, Comarca de Guna Yala"),
}},
"san-blas-sailing-panama-to-colombia": {
  "hero": ("raw", "https://images.pexels.com/photos/36117831/pexels-photo-36117831.jpeg?auto=compress&cs=tinysrgb&w=1600"),
  "body": {
  1: ("Island of Chichimen, Cuyos Limones, Guna Yala, Panama.jpg", "Chichimen island, Cayos Limones, Guna Yala"),
}},
"pearl-islands-panama-guide": {
  "hero": "Wyspa Contadora, Archipelag Wysp Perłowych, Panama.jpg", "body": {
  1: ("San Miguel (1).jpg", "San Miguel on Isla del Rey, the archipelago's largest town"),
}},
}

def src_of(spec):
    return spec[1] if isinstance(spec, tuple) and spec[0] == "raw" else wurl(spec)

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

def page_images(s):
    """hero + body images, document order, de-duplicated — what the gallery shows."""
    out, seen = [], set()
    h = re.search(r'art-hero-img-full"><img src="([^"]+)"', s)
    urls = [h.group(1)] if h else []
    for m in re.finditer(r'<figure class="art-inline-img"[^>]*>.*?</figure>', s, re.S):
        mm = re.search(r'src="([^"]+)"', m.group(0))
        if mm: urls.append(mm.group(1))
    for u in urls:
        k = re.sub(r"[?&]w=\d+", "", u)
        if k not in seen:
            seen.add(k); out.append(u.replace("&amp;", "&"))
    return out

def sync_gallery(s):
    """Rebuild the grid from the page's own hero + body images."""
    g = re.search(r'<div class="art-gallery-grid">(.*?)</div></div></section>', s, re.S)
    if not g: return s, 0
    figs = re.findall(r"<figure[^>]*>.*?</figure>", g.group(1), re.S)
    imgs = page_images(s)
    if not figs or not imgs: return s, 0
    inner = g.group(1); n = 0
    for i, fig in enumerate(figs):
        if i >= len(imgs): break
        alt = re.search(r'<img[^>]*\balt="([^"]*)"', fig)
        # keep the tile's own alt when it has one, else borrow the body image's
        src_alt = alt.group(1) if alt else ""
        m2 = re.search(r'<img[^>]*\bsrc="%s"[^>]*\balt="([^"]*)"' % re.escape(imgs[i].replace("&", "&amp;")), s)
        if m2: src_alt = m2.group(1)
        new = re.sub(r"<img\b[^>]*>", img_html(imgs[i], src_alt, GW, SIZES_GALLERY), fig, count=1)
        inner = inner.replace(fig, new, 1); n += 1
    return s[:g.start(1)] + inner + s[g.end(1):], n

def main():
    for slug, plan in PLAN.items():
        p = ROOT / "public" / "articles" / f"{slug}.html"
        s = orig = p.read_text(encoding="utf-8")
        if plan["hero"]:
            s = set_hero(s, plan["hero"])
        hs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
        for si, (spec, cap) in sorted(plan["body"].items(), reverse=True):
            figs = [m for m in re.finditer(r'<figure class="art-inline-img"[^>]*>.*?</figure>', s, re.S)
                    if sum(1 for h in hs if h.start() < m.start()) == si]
            if figs:
                s = s.replace(figs[0].group(0), figure(spec, cap), 1)
            elif si - 1 < len(hs):
                start = hs[si - 1].end()
                nxt = hs[si].start() if si < len(hs) else len(s)
                pm = re.search(r"</p>", s[start:nxt])
                off = start + pm.end() if pm else start
                s = s[:off] + figure(spec, cap) + s[off:]
        s, ng = sync_gallery(s)
        if s != orig:
            p.write_text(s, encoding="utf-8")
            print(f"  ✓ {slug}  hero={'set' if plan['hero'] else '—'}  body={len(plan['body'])}  gallery={ng}")

if __name__ == "__main__":
    main()
