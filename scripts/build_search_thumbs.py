"""Tiny square thumbnails for the search box, one per guide whose hero photo is on our own site.
Guides whose hero is still on Wikimedia or Pexels get a small version from those CDNs instead (see build-static.mjs).
  python3 scripts/build_search_thumbs.py [--force]
"""
import html, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / "public"; OUT = P / "images/thumbs"; OUT.mkdir(parents=True, exist_ok=True)
force = "--force" in sys.argv; made = skipped = remote = missing = 0
for f in sorted(P.glob("articles/*.html")) + sorted(P.glob("es/articles/*.html")):
    h = f.read_text(errors="ignore")
    m = re.search(r'<img\b[^>]*class="hero-img"[^>]*>', h) or re.search(r'art-hero-img-full"[^>]*>\s*<img\b[^>]*>', h) or re.search(r'hub-hero-img"[^>]*>\s*<img\b[^>]*>', h)
    src = html.unescape(re.search(r'\bsrc="([^"]+)"', m[0])[1]) if m else ""
    src = src.replace("https://panamaspot.com", "")
    if not src.startswith("/"):
        remote += 1; continue
    name = ("es-" if str(f.relative_to(P)).startswith("es/") else "") + f.stem + ".webp"
    dst = OUT / name; srcf = P / src.lstrip("/")
    if not srcf.exists(): missing += 1; print("missing", src); continue
    if dst.exists() and not force: skipped += 1; continue
    subprocess.run(["magick", str(srcf), "-auto-orient", "-resize", "96x96^", "-gravity", "center", "-extent", "96x96", "-strip", "-quality", "50", str(dst)], check=True)
    made += 1
size = sum(x.stat().st_size for x in OUT.glob("*.webp"))
print(f"made {made}, kept {skipped}, on other sites {remote}, missing {missing}; folder {size // 1024} KB")
