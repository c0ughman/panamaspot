#!/usr/bin/env python3
"""
convert-legacy-heroes.py — convert the remaining CSS background-image heroes
(the older pages not driven by image-selections) into real <img> elements, to
match the generator pages. alt comes from og:image:alt if present, else the H1.
Local /images/*.webp heroes have no bucket variants, so they get a plain src
(the fixed-height hero container controls sizing, so there's no CLS).

Idempotent: only the background-image form matches; already-converted <img>
heroes are skipped.
    python3 scripts/convert-legacy-heroes.py
"""
import re, glob, html, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import img_html, HERO

def alt_for(s):
    m = re.search(r'content="([^"]+)" property="og:image:alt"', s)
    if m:
        return m.group(1)
    h = re.search(r'<h1 class="art-title">(.*?)</h1>', s, re.S)
    return html.escape(re.sub(r"<[^>]+>", "", h.group(1)).strip()) if h else ""

def main():
    n = 0
    for p in glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html"):
        s = pathlib.Path(p).read_text()
        m = re.search(r"<div class=\"art-hero-img-full\"[^>]*style=\"background-image:url\('([^']+)'\)[^\"]*\"[^>]*></div>", s)
        if not m:
            continue
        url = m.group(1).replace("&amp;", "&")
        img = img_html(url, alt_for(s), HERO, "100vw", eager=True)
        s = s[:m.start()] + f'<div class="art-hero-img-full">{img}</div>' + s[m.end():]
        pathlib.Path(p).write_text(s)
        n += 1
        print(f"  ✓ {pathlib.Path(p).name}")
    print(f"converted {n} legacy heroes")

if __name__ == "__main__":
    main()
