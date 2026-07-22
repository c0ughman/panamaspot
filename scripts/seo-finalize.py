#!/usr/bin/env python3
"""
seo-finalize.py — head/JSON-LD SEO polish for the overhauled article pages.
Run LAST, after image-swap.py / image-swap-sections.py / image-credits.py.

Applies the SEO-audit items that live in the <head> and structured data:
  M1  refresh article:modified_time + Article.dateModified to the edit date.
  M2  add og:image:alt + twitter:image:alt (from the hero caption).
  M3  add og:image:width + og:image:height (from the capped hero dimensions).
  P1  enrich Article JSON-LD "image" to list EVERY image on the page (not just
      the hero), so image structured data covers the gallery too.
  a11y add role="img" + aria-label to the hero div (gallery/inline already done
      by the image generators).

Everything is idempotent (re-runnable). Captions/licences come from
scripts/image-selections.json; dimensions from scripts/img-dims.json.

    python3 scripts/seo-finalize.py
"""
import re, json, pathlib, html, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import wm_original, capped_dims, rendered_dims, HERO

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEL  = json.loads((ROOT/"scripts"/"image-selections.json").read_text())["selections"]
ARTIST = json.loads((ROOT/"scripts"/"image-artists.json").read_text()) if (ROOT/"scripts"/"image-artists.json").exists() else {}
EDIT_DATE = "2026-07-20"

def license_url(lic):
    """schema.org license: map a licence string to its canonical deed URL."""
    l = (lic or "").strip().lower()
    if not l:
        return None
    if l in ("cc0", "cc0 1.0"):
        return "https://creativecommons.org/publicdomain/zero/1.0/"
    if l in ("public domain", "pd"):
        return "https://en.wikipedia.org/wiki/Public_domain"
    m = re.match(r"cc by(-sa)?\s*([0-9]\.[0-9])", l)
    if m:
        return f"https://creativecommons.org/licenses/by{m.group(1) or ''}/{m.group(2)}/"
    if l.startswith("cc by-sa"):
        return "https://creativecommons.org/licenses/by-sa/4.0/"
    if l.startswith("cc by"):
        return "https://creativecommons.org/licenses/by/4.0/"
    return None

def commons_page(orig_url):
    m = re.match(r"^https://upload\.wikimedia\.org/wikipedia/commons/[0-9a-f]/[0-9a-f]{2}/([^/?#]+)$",
                 (orig_url or "").replace("&amp;", "&"))
    return f"https://commons.wikimedia.org/wiki/File:{m.group(1)}" if m else None

def norm(url):
    """Normalize any (capped or original, escaped or not) image URL to a key that
    matches the originals stored in image-selections.json."""
    u = url.replace("&amp;", "&")
    if "images.pexels.com" in u:
        return re.sub(r"([?&]w=)\d+", r"\g<1>", u)  # drop the width number
    return wm_original(u)

# normalized-url -> (caption_en, caption_es, original_url, license)
CAPT = {}
for c in SEL.values():
    items = list(c["use"])
    if c.get("hero"): items.append(c["hero"])
    for it in items:
        CAPT[norm(it["url"])] = (it.get("caption_en", ""), it.get("caption_es", ""), it["url"], it.get("license", ""))

def caption_for(url, lang):
    e = CAPT.get(norm(url))
    if not e: return None, None
    en, es, orig = e[0], e[1], e[2]
    cap = (es if lang == "es" else en) or en or es
    return cap, orig

def image_object(url, lang):
    """A schema.org ImageObject for one rendered image: contentUrl + dims, and
    (for Commons images) licence + creator so it can earn the Licensable badge."""
    node = {"@type": "ImageObject", "contentUrl": url, "url": url}
    dims = rendered_dims(url)
    if dims:
        node["width"], node["height"] = dims[0], dims[1]
    e = CAPT.get(norm(url))
    if e:
        cap = (e[1] if lang == "es" else e[0]) or e[0] or e[1]
        if cap:
            node["caption"] = cap
        lu = license_url(e[3])
        if lu:
            node["license"] = lu
            node["acquireLicensePage"] = commons_page(e[2]) or lu
        artist = ARTIST.get(e[2]) or ARTIST.get(e[2].replace("&", "&amp;"))
        if artist:
            node["creditText"] = artist
            node["creator"] = {"@type": "Person", "name": artist}
            node["copyrightNotice"] = artist
    if "license" not in node and "images.pexels.com" in url:
        node["license"] = "https://www.pexels.com/license/"
    return node

def page_images(s):
    """The article's own images — hero + gallery/inline <figure> images — in
    document order (hero first), de-duplicated, plain-& for JSON. Excludes the
    related-guides module (those are other articles' heroes)."""
    out, seen = [], set()
    hm = re.search(r'art-hero-img-full">\s*<img[^>]*\bsrc="([^"]+)"', s)
    urls = [hm.group(1)] if hm else []
    for fm in re.finditer(r'<figure[^>]*>.*?</figure>', s, re.S):
        im = re.search(r'<img[^>]*\bsrc="([^"]+)"', fm.group(0))
        if im:
            urls.append(im.group(1))
    for u in urls:
        u = u.replace("&amp;", "&")
        if u not in seen:
            seen.add(u); out.append(u)
    return out

def upsert_after(s, anchor_re, new_tags, cleanup_res):
    for cr in cleanup_res:
        s = re.sub(cr, "", s)
    m = re.search(anchor_re, s)
    if m:
        s = s[:m.end()] + new_tags + s[m.end():]
    return s

def process(page):
    p = ROOT/page
    s = p.read_text(encoding="utf-8")
    lang = "es" if "/es/" in page else "en"

    # hero URL + caption (hero is now a real <img>)
    hm = re.search(r'art-hero-img-full">\s*<img[^>]*\bsrc="([^"]+)"', s)
    hero_url = hm.group(1) if hm else None
    hero_alt, hero_orig = (caption_for(hero_url, lang) if hero_url else (None, None))
    hero_alt = hero_alt or ""
    alt_esc = html.escape(hero_alt)

    # ── M1: refresh modified dates (keep datePublished) ──────────────────────
    s = re.sub(r'(content=")[^"]*(" property="article:modified_time"/>)',
               lambda m: m.group(1) + EDIT_DATE + m.group(2), s)
    s = re.sub(r'("dateModified": ")[^"]*(")',
               lambda m: m.group(1) + EDIT_DATE + m.group(2), s)

    # ── M2 + M3: og/twitter image alt + dimensions ───────────────────────────
    dims = capped_dims(hero_orig, HERO) if hero_orig else None
    og_extra = f'<meta content="{alt_esc}" property="og:image:alt"/>'
    if dims:
        og_extra += (f'<meta content="{dims[0]}" property="og:image:width"/>'
                     f'<meta content="{dims[1]}" property="og:image:height"/>')
    s = upsert_after(s,
        r'<meta content="[^"]*" property="og:image"/>',
        og_extra,
        [r'<meta content="[^"]*" property="og:image:alt"/>',
         r'<meta content="[^"]*" property="og:image:width"/>',
         r'<meta content="[^"]*" property="og:image:height"/>'])
    s = upsert_after(s,
        r'<meta content="[^"]*" name="twitter:image"/>',
        f'<meta content="{alt_esc}" name="twitter:image:alt"/>',
        [r'<meta content="[^"]*" name="twitter:image:alt"/>'])

    # ── a11y: set the hero <img>'s alt authoritatively from the caption ───────
    if hero_alt:
        s = re.sub(r'(<div class="art-hero-img-full"><img[^>]*\balt=")[^"]*(")',
                   lambda m: m.group(1) + alt_esc + m.group(2), s, count=1)

    # ── P1: Article JSON-LD image array → full ImageObjects (licence+creator) ─
    imgs = page_images(s)
    if imgs:
        arr = ", ".join(json.dumps(image_object(u, lang), ensure_ascii=False) for u in imgs)
        s = re.sub(r'("image": \[)[^\]]*(\])',
                   lambda m: m.group(1) + arr + m.group(2), s, count=1)

    p.write_text(s, encoding="utf-8")
    print(f"  ✓ {page}  images={len(imgs)}  hero_alt={'y' if hero_alt else 'N'}  dims={dims}")

def main():
    pages = []
    for c in SEL.values():
        pages += c["pages"]
    for page in dict.fromkeys(pages):
        process(page)

if __name__ == "__main__":
    main()
