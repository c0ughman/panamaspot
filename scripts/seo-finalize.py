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
from img_cap import wm_original, capped_dims, HERO

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEL  = json.loads((ROOT/"scripts"/"image-selections.json").read_text())["selections"]
EDIT_DATE = "2026-07-20"

def norm(url):
    """Normalize any (capped or original, escaped or not) image URL to a key that
    matches the originals stored in image-selections.json."""
    u = url.replace("&amp;", "&")
    if "images.pexels.com" in u:
        return re.sub(r"([?&]w=)\d+", r"\g<1>", u)  # drop the width number
    return wm_original(u)

# normalized-url -> (caption_en, caption_es, original_url)
CAPT = {}
for c in SEL.values():
    items = list(c["use"])
    if c.get("hero"): items.append(c["hero"])
    for it in items:
        CAPT[norm(it["url"])] = (it.get("caption_en", ""), it.get("caption_es", ""), it["url"])

def caption_for(url, lang):
    e = CAPT.get(norm(url))
    if not e: return None, None
    en, es, orig = e
    cap = (es if lang == "es" else en) or en or es
    return cap, orig

def page_images(s):
    """All rendered image URLs in document order (hero first), de-duplicated,
    plain-& for JSON."""
    out, seen = [], set()
    m = re.search(r'art-hero-img-full"[^>]*background-image:url\(\'([^\']+)\'', s)
    urls = ([m.group(1)] if m else []) + re.findall(r'imgph photo"[^>]*background-image:url\(\'([^\']+)\'', s)
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

    # hero URL + caption
    hm = re.search(r'art-hero-img-full"[^>]*background-image:url\(\'([^\']+)\'', s)
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

    # ── a11y: hero div role + aria-label (set OR update if already present) ───
    if hero_alt:
        if re.search(r'art-hero-img-full" role="img" aria-label="', s):
            s = re.sub(r'(art-hero-img-full" role="img" aria-label=")[^"]*(")',
                       lambda m: m.group(1) + alt_esc + m.group(2), s, count=1)
        else:
            s = s.replace('<div class="art-hero-img-full" style=',
                          f'<div class="art-hero-img-full" role="img" aria-label="{alt_esc}" style=', 1)

    # ── P1: enrich Article JSON-LD image array with every page image ─────────
    imgs = page_images(s)
    if imgs:
        arr = ", ".join(json.dumps(u, ensure_ascii=False) for u in imgs)
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
