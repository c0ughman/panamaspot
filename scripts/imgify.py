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

def convert(s):
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
        alt = alt.replace('"', "&quot;")
        img = img_html(url, alt, GALLERY, SIZES)
        return f'<div class="imgph photo">{img}</div>'
    return PAT.sub(repl, s)

def main():
    total = 0
    for p in glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html"):
        s = pathlib.Path(p).read_text()
        n = len(PAT.findall(s))
        if not n:
            continue
        pathlib.Path(p).write_text(convert(s))
        total += n
        print(f"  ✓ {pathlib.Path(p).name}  ({n})")
    print(f"converted {total} imgph backgrounds")

if __name__ == "__main__":
    main()
