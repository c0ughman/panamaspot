#!/usr/bin/env python3
"""
imgify.py — convert any remaining CSS background-image CONTENT images
(<div class="imgph photo" style="background-image:…">) into real responsive
<img> elements on the older, non-image-selections pages. The generator pages
already emit <img> directly; this catches everything else.

alt is taken from the image's own <figcaption>, else a nearby bento <h3>, else
"". Uses img_cap.img_html so dimensions/srcset are included when known (run
build-img-dims.py first so the older Pexels images have dims).

Idempotent: only the background-image form matches. CTA promo art (.evb-*) is
intentionally left alone.
    python3 scripts/imgify.py
"""
import re, glob, html, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import img_html, GALLERY

SIZES = "(max-width: 900px) 50vw, 480px"
PAT = re.compile(r'<div class="imgph photo"[^>]*style="[^"]*background-image:url\(\'([^\']+)\'\)[^"]*"[^>]*></div>')

def page_title(s):
    m = re.search(r'<h1 class="art-title">(.*?)</h1>', s, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""

def convert(s):
    fallback = page_title(s)
    def repl(m):
        url = m.group(1).replace("&amp;", "&")
        after = s[m.end():m.end()+600]
        alt = ""
        cap = re.search(r"<figcaption>(.*?)</figcaption>", after, re.S)
        if cap:
            alt = re.sub(r"<[^>]+>", "", cap.group(1)).strip()
        if not alt:
            h3 = re.search(r"<h3[^>]*>(.*?)</h3>", after, re.S)
            if h3:
                alt = re.sub(r"<[^>]+>", "", h3.group(1)).strip()
        alt = (alt or fallback).replace('"', "&quot;")
        img = img_html(url, alt, GALLERY, SIZES)
        return f'<div class="imgph photo">{img}</div>'
    return PAT.sub(repl, s)

def fill_empty_alts(s):
    """Give any content <img alt=""> a description — the nearest figcaption, else
    the page title. Catches already-converted images (e.g. caption-less
    galleries) so no content image ships alt-less."""
    fallback = page_title(s)
    def repl(m):
        tag = m.group(0)
        after = s[m.end():m.end()+400]
        cap = re.search(r"<figcaption>(.*?)</figcaption>", after, re.S)
        alt = (re.sub(r"<[^>]+>", "", cap.group(1)).strip() if cap else fallback).replace('"', "&quot;")
        return tag.replace('alt=""', f'alt="{alt}"', 1) if alt else tag
    return re.sub(r'<img[^>]*\balt=""[^>]*>', repl, s)

def main():
    conv = filled = 0
    for p in glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html"):
        s = pathlib.Path(p).read_text()
        n = len(PAT.findall(s))
        s2 = convert(s) if n else s
        before_empty = len(re.findall(r'<img[^>]*\balt=""', s2))
        s2 = fill_empty_alts(s2)
        if s2 != s:
            pathlib.Path(p).write_text(s2)
        conv += n
        filled += before_empty - len(re.findall(r'<img[^>]*\balt=""', s2))
    print(f"converted {conv} imgph backgrounds; filled {filled} empty alts")

if __name__ == "__main__":
    main()
