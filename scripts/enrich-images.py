#!/usr/bin/env python3
"""
enrich-images.py — set the Article JSON-LD "image" to full ImageObjects on EVERY
article page (the selection pages AND the older ones), built from each page's own
rendered <img> tags (hero + figures):
  contentUrl + width/height, caption (image-selections caption when known, else
  the rendered alt), and licence/creator (Commons CC data when known, else the
  Pexels licence). This makes every image Licensable-badge eligible site-wide.

Single source of truth for the Article image array (seo-finalize.py no longer
sets it). Idempotent; run after the image pipeline (imgify) so every image is a
real <img>.
    python3 scripts/enrich-images.py
"""
import re, json, glob, html, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import rendered_dims, wm_original

ROOT   = pathlib.Path(__file__).resolve().parent.parent
SEL    = json.loads((ROOT/"scripts"/"image-selections.json").read_text())["selections"]
ARTIST = json.loads((ROOT/"scripts"/"image-artists.json").read_text()) if (ROOT/"scripts"/"image-artists.json").exists() else {}

def norm(url):
    u = url.replace("&amp;", "&")
    if "images.pexels.com" in u:
        return re.sub(r"([?&]w=)\d+", r"\g<1>", u)
    return wm_original(u)

CAPT = {}
for c in SEL.values():
    items = list(c["use"]) + ([c["hero"]] if c.get("hero") else [])
    for it in items:
        CAPT[norm(it["url"])] = (it.get("caption_en", ""), it.get("caption_es", ""), it["url"], it.get("license", ""))

def license_url(lic):
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

def page_imgs(s):
    """(src, alt) for the hero + each <figure> image, doc order, deduped."""
    out, seen = [], set()
    tags = []
    hm = re.search(r'art-hero-img-full">\s*<img([^>]*)>', s)
    if hm:
        tags.append(hm.group(1))
    for fm in re.finditer(r"<figure[^>]*>.*?</figure>", s, re.S):
        im = re.search(r"<img([^>]*)>", fm.group(0))
        if im:
            tags.append(im.group(1))
    for t in tags:
        sm = re.search(r'\bsrc="([^"]+)"', t)
        am = re.search(r'\balt="([^"]*)"', t)
        if sm and sm.group(1) not in seen:
            seen.add(sm.group(1))
            out.append((sm.group(1), html.unescape(am.group(1)) if am else ""))
    return out

def image_object(src, alt, lang):
    url = src.replace("&amp;", "&")
    node = {"@type": "ImageObject", "contentUrl": url, "url": url}
    d = rendered_dims(url)
    if d:
        node["width"], node["height"] = d[0], d[1]
    e = CAPT.get(norm(url))
    cap = ""
    if e:
        cap = (e[1] if lang == "es" else e[0]) or e[0] or e[1]
    cap = cap or alt
    if cap:
        node["caption"] = cap
    if e:
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

def process(page):
    s = pathlib.Path(page).read_text()
    lang = "es" if "/es/" in page else "en"
    imgs = page_imgs(s)
    if not imgs:
        return
    arr = ", ".join(json.dumps(image_object(src, alt, lang), ensure_ascii=False) for src, alt in imgs)
    am = re.search(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "Article".*?</script>', s, re.S)
    if not am:
        print(f"  ! no Article block: {page}"); return
    block = re.sub(r'("image": \[)[^\]]*(\])', lambda m: m.group(1) + arr + m.group(2), am.group(0), count=1)
    s = s[:am.start()] + block + s[am.end():]
    pathlib.Path(page).write_text(s)

def main():
    n = 0
    for page in sorted(glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html")):
        process(page); n += 1
    print(f"enriched Article images on {n} pages")

if __name__ == "__main__":
    main()
