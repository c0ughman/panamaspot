#!/usr/bin/env python3
"""
bulk-seo-pass.py — sitewide mechanical SEO corrections that apply to every
article page, not just one batch.

  1. BREADCRUMBS   The visible trail and the BreadcrumbList disagreed and both
                   were wrong. The trail was Home / <Province> / <Region>, where
                   the province was an inert <span> (no link at all) and the
                   final crumb was named after the region but pointed at the
                   article — a name/URL mismatch on every page. On the 2026-09
                   batch the middle ListItem had no `item` at all, which is
                   invalid for a non-final crumb. Region naming had also drifted
                   ("Caribbean" / "Caribbean Coast" / "Caribe Panameño" /
                   "Panamá" all for the same coast — 38 distinct trails).
                   Rewritten to Home / <Destination hub> / <Article title>, every
                   crumb a real URL whose name matches it, visible trail and
                   JSON-LD generated from the same data. Pages whose region has
                   no hub get Home / <Article title>.
  2. inLanguage    38 Spanish pages declared "en" in their Article schema.
  3. og:locale     26 Spanish pages declared en_US.
  4. og:image      21 pages advertised a different photo than the hero they
                   actually render, so the social preview did not match the page.
  5. LCP           No page preconnected to the image CDN or preloaded its hero,
                   although every hero is a cross-origin hotlink and the LCP
                   element. Adds preconnect + a srcset-aware preload.
  6. dateModified  Refreshed to the real edit date (and article:modified_time).

Idempotent. Run after the image pipeline, so heroes are real <img> elements.
    python3 scripts/bulk-seo-pass.py
"""
import re, json, glob, html, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://panamaspot.com"
EDIT_DATE = datetime.date.today().isoformat()

ALL = sorted(glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html"))
HUB_SLUGS = {"boquete", "el-valle-de-anton", "panama-city", "bocas-del-toro"}

HUBS = {
    ("boquete", "en"):    ("/articles/boquete", "Boquete"),
    ("boquete", "es"):    ("/es/articles/boquete", "Boquete"),
    ("elvalle", "en"):    ("/articles/el-valle-de-anton", "El Valle de Antón"),
    ("elvalle", "es"):    ("/es/articles/el-valle-de-anton", "El Valle de Antón"),
    ("panamacity", "en"): ("/articles/panama-city", "Panama City"),
    ("panamacity", "es"): ("/es/articles/panama-city", "Ciudad de Panamá"),
    ("bocas", "en"):      ("/articles/bocas-del-toro", "Bocas del Toro"),
    # no Spanish Bocas hub exists yet — those pages fall back to Home / Title.
}

def cluster(name):
    n = name.lower()
    if any(k in n for k in ("boquete", "volcan-baru", "baru", "caldera", "lerida", "chiriqui")): return "boquete"
    if "el-valle" in n or "valle-de-anton" in n or "albrook" in n: return "elvalle"
    if any(k in n for k in ("casco-viejo", "panama-city", "ciudad-de-panama", "amador",
                            "canal", "cinta-costera", "day-trip", "charter")): return "panamacity"
    if "bocas" in n or "zapatilla" in n or "red-frog" in n or "starfish" in n: return "bocas"
    return "other"

def short(t, n=58):
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > n and ":" in t:
        head = t.split(":")[0].strip()
        if len(head) >= 18:
            t = head
    return t[:n].rsplit(" ", 1)[0] + "…" if len(t) > n else t

def crumbs_for(path):
    p = pathlib.Path(path)
    lang = "es" if "/es/" in path else "en"
    s = p.read_text()
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
    title = short(html.unescape(re.sub(r"<[^>]+>", "", h1.group(1)))) if h1 else ""
    url = "/" + path.replace("public/", "", 1)[:-5]
    out = [("Inicio" if lang == "es" else "Home", "/" if lang == "en" else "/es")]
    hub = HUBS.get((cluster(p.name), lang))
    if hub and hub[0] != url:
        out.append((hub[1], hub[0]))
    out.append((title, url))
    return out

def render_visible(cr):
    first = f'<a href="{cr[0][1]}">{html.escape(cr[0][0])}</a>'
    mid = ""
    for name, href in cr[1:-1]:
        mid += (f'<span style="display:contents"><span class="sep">/</span>'
                f'<a href="{href}">{html.escape(name)}</a></span>')
    last = (f'<span style="display:contents"><span class="sep">/</span>'
            f'<span aria-current="page">{html.escape(cr[-1][0])}</span></span>')
    return first + mid + last

def render_ld(cr):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u}
                for i, (n, u) in enumerate(cr)]}

# Hub hero dimensions. The hubs are built by build-hub.py, which emits the hero
# with no width/height — CLS on the LCP element of the site's highest-priority
# pages. Local files measured with sips; the Pexels one scaled from img-dims.
HUB_HERO_DIMS = {
    "/images/boquete/boquete-hills.webp": (960, 720),
    "/images/el-valle/elvalle-crater-hero.webp": (2400, 1310),
    "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=2400": (2400, 1601),
}

def fix_hub_hero(s):
    """Add width/height + a preload (and preconnect when the hero is remote) to
    the destination hubs, which the article pipeline does not touch."""
    m = re.search(r'class="hub-hero-img"><img ([^>]*)>', s)
    if not m:
        return s, False
    tag, attrs = m.group(0), m.group(1)
    src = re.search(r'src="([^"]+)"', attrs)
    if not src:
        return s, False
    url = src.group(1).replace("&amp;", "&")
    dims = HUB_HERO_DIMS.get(url)
    new = tag
    if dims and "width=" not in attrs:
        new = tag.replace("<img ", f'<img width="{dims[0]}" height="{dims[1]}" ', 1)
        s = s.replace(tag, new, 1)
    s = re.sub(r'<link rel="preload" as="image"[^>]*/?>', "", s)
    s = re.sub(r'<link rel="preconnect" href="https://images\.pexels\.com"[^>]*/?>', "", s)
    s = re.sub(r'<link rel="dns-prefetch" href="https://images\.pexels\.com"[^>]*/?>', "", s)
    tags = ""
    if "images.pexels.com" in url:
        tags += ('<link rel="preconnect" href="https://images.pexels.com" crossorigin/>'
                 '<link rel="dns-prefetch" href="https://images.pexels.com"/>')
    tags += f'<link rel="preload" as="image" href="{src.group(1)}" fetchpriority="high"/>'
    cm = re.search(r'<link[^>]*rel="canonical"[^>]*/?>', s)
    if not cm:
        return s, False
    return s[:cm.end()] + tags + s[cm.end():], True

def process(path):
    p = pathlib.Path(path)
    s = orig = p.read_text()
    lang = "es" if "/es/" in path else "en"
    changed = set()

    # ── hubs: only the hero treatment applies (no breadcrumb nav, and the rest
    #    of their head is already correct — they are built by build-hub.py)
    if p.stem in HUB_SLUGS:
        s, ok = fix_hub_hero(s)
        if s != orig:
            p.write_text(s)
        return {"hub hero"} if ok else set()

    # ── 1. breadcrumbs
    if 'class="breadcrumb">' in s:
        cr = crumbs_for(path)
        s = re.sub(r'(class="breadcrumb">).*?(</nav>)',
                   lambda m: m.group(1) + render_visible(cr) + m.group(2), s, count=1, flags=re.S)
        ld = json.dumps(render_ld(cr), ensure_ascii=False)
        def swap_bc(m):
            try:
                if json.loads(m.group(1)).get("@type") == "BreadcrumbList":
                    return m.group(0).replace(m.group(1), ld)
            except Exception:
                pass
            return m.group(0)
        s = re.sub(r'(?s)application/ld\+json[^>]*>(.*?)</script>', swap_bc, s)
        changed.add("breadcrumb")

    # ── 2. inLanguage on the Article node
    want = "es" if lang == "es" else "en"
    if re.search(r'"inLanguage": "(?!%s")' % want, s):
        s = re.sub(r'"inLanguage": "[^"]*"', f'"inLanguage": "{want}"', s); changed.add("inLanguage")

    # ── 3. og:locale
    loc = "es_PA" if lang == "es" else "en_US"
    m = re.search(r'<meta content="([^"]*)" property="og:locale"/>', s)
    if m and m.group(1) != loc:
        s = s.replace(m.group(0), f'<meta content="{loc}" property="og:locale"/>'); changed.add("og:locale")

    # ── 4. og:image / twitter:image must be the hero actually rendered
    hero = re.search(r'art-hero-img-full"><img src="([^"]+)"', s)
    if hero:
        # advertise the widest variant we know is live, not the rendered one.
        # og:image must be absolute, so a local /images/… hero gets the origin.
        big = re.sub(r'([?&]w=)\d+', r'\g<1>1600', hero.group(1))
        if big.startswith("/"):
            big = BASE + big
        for prop, pat in (("og:image", r'<meta content="([^"]*)" property="og:image"/>'),
                          ("twitter:image", r'<meta content="([^"]*)" name="twitter:image"/>')):
            mm = re.search(pat, s)
            if mm and mm.group(1).replace("&amp;", "&") != big.replace("&amp;", "&"):
                s = s.replace(mm.group(0), mm.group(0).replace(mm.group(1), big)); changed.add("og:image")

    # ── 5. preconnect + hero preload (LCP)
    s = re.sub(r'<link rel="preconnect"[^>]*images\.pexels\.com[^>]*/?>', "", s)
    s = re.sub(r'<link rel="dns-prefetch"[^>]*images\.pexels\.com[^>]*/?>', "", s)
    s = re.sub(r'<link rel="preload" as="image"[^>]*/?>', "", s)
    if hero:
        src = hero.group(1)
        host = "https://images.pexels.com" if "images.pexels.com" in src else (
               "https://upload.wikimedia.org" if "upload.wikimedia.org" in src else None)
        tags = ""
        if host:
            tags += f'<link rel="preconnect" href="{host}" crossorigin/><link rel="dns-prefetch" href="{host}"/>'
        tag = re.search(r'art-hero-img-full"><img[^>]*>', s).group(0)
        ss = re.search(r'srcset="([^"]*)"', tag)
        sz = re.search(r'sizes="([^"]*)"', tag)
        tags += f'<link rel="preload" as="image" href="{src}"'
        if ss: tags += f' imagesrcset="{ss.group(1)}"'
        if sz: tags += f' imagesizes="{sz.group(1)}"'
        tags += ' fetchpriority="high"/>'
        mm = re.search(r'<link[^>]*rel="canonical"[^>]*/?>', s)
        if mm:
            s = s[:mm.end()] + tags + s[mm.end():]; changed.add("lcp")

    # ── 6. dateModified
    s2 = re.sub(r'("dateModified": ")[^"]*(")', lambda m: m.group(1) + EDIT_DATE + m.group(2), s)
    s2 = re.sub(r'(<meta content=")[^"]*(" property="article:modified_time"/>)',
                lambda m: m.group(1) + EDIT_DATE + m.group(2), s2)
    if s2 != s:
        s = s2; changed.add("dateModified")

    if s != orig:
        p.write_text(s)
    return changed

def main():
    tally = {}
    for path in ALL:
        for k in process(path):
            tally[k] = tally.get(k, 0) + 1
    for k, v in sorted(tally.items()):
        print(f"  {k:<14} {v} pages")

if __name__ == "__main__":
    main()
