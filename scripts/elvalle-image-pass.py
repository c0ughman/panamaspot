#!/usr/bin/env python3
"""
elvalle-image-pass.py — put real, verified El Valle photographs on the 2026-09
El Valle batch.

The twelve pages generated in September shipped with keyword-picked stock: the
"Chorro El Macho" figure was a lava field, the market pages were shot in Oaxaca
and Guatemala City, and one hero was reused across three articles. This applies
scripts/elvalle-image-plan.json, which maps every hero and every section to a
photograph that is either the site's own El Valle library (/images/el-valle/…)
or a Commons file categorised under El Valle de Antón / the Gran Terminal de
Transporte, plus the handful of stock frames the client asked to keep.

Per page it rewrites:
  - the hero <img>, og:image / twitter:image (+ width, height, alt),
    WebPage.primaryImageOfPage and the Place/TouristDestination image,
  - the inline <figure class="art-inline-img"> set — old figures are stripped
    and one new figure is inserted after the first paragraph of each planned
    section, so nothing is left stranded under the wrong heading,
  - the "In pictures" gallery, which is rebuilt to mirror the article's own
    inline set (first tile = feature).

Article JSON-LD image objects, the credits block, the related-guide cards and
the sitemap image list are all derived from the rendered HTML afterwards:

    python3 scripts/elvalle-image-pass.py
    python3 scripts/enrich-images.py
    python3 scripts/image-credits.py
    python3 scripts/related-module.py
    python3 scripts/build-page-images.py

Idempotent: re-running rebuilds the same markup from the same plan.
"""
import re, json, html, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import cap, img_html, capped_dims, HERO, GALLERY

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "scripts" / "elvalle-image-plan.json").read_text(encoding="utf-8"))
VER = json.loads((ROOT / "scripts" / "commons-verified.json").read_text(encoding="utf-8"))

SIZES_HERO = "100vw"
SIZES_INLINE = "(max-width: 768px) 100vw, 768px"
SIZES_GALLERY = "(max-width: 900px) 50vw, 25vw"
SIZES_FEATURE = "(max-width: 900px) 100vw, 50vw"
BASE = "https://panamaspot.com"


def resolve(key):
    """Plan key -> the URL the page should render."""
    if key.startswith("File:"):
        rec = VER.get(key[5:])
        if not rec:
            raise SystemExit(f"not in commons-verified.json: {key}")
        return rec["url"]
    return key                      # local /images/… path, or a kept stock URL


def abs_url(u):
    return u if u.startswith("http") else BASE + u


# ---------------------------------------------------------------- hero + meta

def set_hero(s, url, alt, pos=None):
    """`pos` is an optional object-position for the hero crop. The hero band is
    much wider than it is tall, so a portrait file gets its middle third and
    nothing else — pass e.g. "50% 78%" when the subject sits low in the frame."""
    esc_alt = html.escape(alt, quote=True)
    style = "width:100%;height:100%;object-fit:cover;display:block"
    if pos:
        style += f";object-position:{pos}"
    img = img_html(url, esc_alt, HERO, SIZES_HERO, eager=True, style=style)
    s, n = re.subn(r'(<div class="art-hero-img-full">)<img[^>]*>', lambda m: m.group(1) + img, s, count=1)
    if not n:
        raise SystemExit("  !! no art-hero-img-full block")

    src = abs_url(cap(url, HERO))
    dims = capped_dims(url, HERO)
    e = src.replace("&", "&amp;")

    def meta(pattern, value):
        nonlocal s
        s = re.sub(pattern, value, s, count=1)

    meta(r'<meta content="[^"]*" property="og:image"/>', f'<meta content="{e}" property="og:image"/>')
    meta(r'<meta content="[^"]*" property="og:image:alt"/>', f'<meta content="{esc_alt}" property="og:image:alt"/>')
    meta(r'<meta content="[^"]*" name="twitter:image"/>', f'<meta content="{e}" name="twitter:image"/>')
    meta(r'<meta content="[^"]*" name="twitter:image:alt"/>', f'<meta content="{esc_alt}" name="twitter:image:alt"/>')
    if dims:
        meta(r'<meta content="\d+" property="og:image:width"/>', f'<meta content="{dims[0]}" property="og:image:width"/>')
        meta(r'<meta content="\d+" property="og:image:height"/>', f'<meta content="{dims[1]}" property="og:image:height"/>')
    return s, src


def set_schema_hero(s, hero_src):
    """primaryImageOfPage (WebPage) and image (TouristDestination/Place)."""
    def fix(block):
        try:
            d = json.loads(block)
        except json.JSONDecodeError:
            return block
        t = d.get("@type")
        touched = False
        if t == "WebPage" and isinstance(d.get("primaryImageOfPage"), dict):
            d["primaryImageOfPage"]["url"] = hero_src
            touched = True
        elif t in ("TouristDestination", "TouristAttraction", "Place", "LandmarksOrHistoricalBuildings") \
                and isinstance(d.get("image"), str):
            d["image"] = hero_src
            touched = True
        return json.dumps(d, ensure_ascii=False) if touched else block

    return re.sub(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)',
                  lambda m: m.group(1) + fix(m.group(2)) + m.group(3), s, flags=re.S)


# -------------------------------------------------------------- inline images

def figure_html(url, caption):
    c = html.escape(caption, quote=True)
    img = img_html(url, c, GALLERY, SIZES_INLINE)
    return (f'<figure class="art-inline-img" data-inlined="1">'
            f'<div class="imgph photo">{img}</div>'
            f'<figcaption>{c}</figcaption></figure>')


def strip_inline(s):
    return re.sub(r'<figure class="art-inline-img".*?</figure>', "", s, flags=re.S)


def insert_inline(s, sid, fig):
    """Put `fig` straight after the first closing </p> below <h2 id="sid">."""
    m = re.search(rf'<h2 id="{sid}"[^>]*>.*?</h2>', s, re.S)
    if not m:
        print(f"  !! no section {sid}")
        return s
    end = s.find("</p>", m.end())
    if end == -1:
        print(f"  !! no paragraph under {sid}")
        return s
    end += 4
    return s[:end] + fig + s[end:]


# ------------------------------------------------------------------- gallery

def _end_of_div(s, i):
    depth, j = 0, i
    while j < len(s):
        nd, cd = s.find("<div", j), s.find("</div>", j)
        if cd == -1:
            return -1
        if nd != -1 and nd < cd:
            depth += 1
            j = nd + 4
        else:
            depth -= 1
            j = cd + 6
            if depth == 0:
                return j
    return -1


def rebuild_gallery(s, items):
    m = re.search(r'<div class="art-gallery-grid">', s)
    if not m:
        print("  !! no gallery grid")
        return s
    start, end = m.end(), _end_of_div(s, m.start())
    figs = []
    for i, (url, capt) in enumerate(items):
        feat = ' class="feature"' if i == 0 else ""
        c = html.escape(capt, quote=True)
        img = img_html(url, c, GALLERY, SIZES_FEATURE if i == 0 else SIZES_GALLERY)
        # No gallery <figcaption>: this cluster carries the description in alt
        # only, so the tile text is not a duplicate of the inline caption.
        figs.append(f'<figure{feat}><div class="imgph photo">{img}</div></figure>')
    return s[:start] + "".join(figs) + s[end - 6:]


# ----------------------------------------------------------------------- main

def main():
    total = 0
    for page, spec in PLAN.items():
        if page.startswith("_"):
            continue
        p = ROOT / page
        s = p.read_text(encoding="utf-8")
        print(f"* {page}")

        hero_url, hero_alt = spec["hero"][:2]
        hero_pos = spec["hero"][2] if len(spec["hero"]) > 2 else None
        s, hero_src = set_hero(s, resolve(hero_url), hero_alt, hero_pos)
        s = set_schema_hero(s, hero_src)

        s = strip_inline(s)
        items = []
        for sid, (key, capt) in spec["sections"].items():
            url = resolve(key)
            items.append((url, capt))
            s = insert_inline(s, sid, figure_html(url, capt))

        s = rebuild_gallery(s, items)
        p.write_text(s, encoding="utf-8")
        print(f"    hero + {len(items)} inline + gallery")
        total += 1 + len(items)
    print(f"\n  {len(PLAN) - 1} pages, {total} images placed")


if __name__ == "__main__":
    main()
