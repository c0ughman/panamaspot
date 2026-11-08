#!/usr/bin/env python3
"""make_img_variants.py - smaller copies of the big photos the homepage, hubs and menu show small.

Lighthouse (2026-11 SEO pass) found the Boquete hub sending ~2.2 MB more image than it displays, and
the homepage ~0.6 MB: thumbnails and tiles are served from 960-2048px files. This writes
<name>-w480.webp (and <name>-w960.webp for files >= 1600px wide) next to each such photo, and lists
them in scripts/img-variants.json. scripts/build-static.mjs then gives those <img> tags a srcset with
sizes="auto, 100vw": Chrome picks the copy that fits the rendered size; browsers without sizes=auto
fall back to 100vw and load what they load today. Nothing can get blurrier.

    npm run build:next && python3 scripts/make_img_variants.py   # reads out/, writes public/ + json
    python3 scripts/make_img_variants.py --check                 # list what it would make

Scope: lazy <img> without srcset, file >= 100 KB and >= 800px wide, on the homepages and hubs, plus any
photo that appears on 50+ pages (the site menu). Idempotent; re-run after changing those pages.
"""
import json, re, sys, subprocess, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT, PUB = ROOT / "out", ROOT / "public"
MANIFEST = ROOT / "scripts" / "img-variants.json"
PAGES = ["index", "es", "articles/boquete", "articles/el-valle-de-anton", "articles/panama-city", "articles/bocas-del-toro",
         "articles/san-blas", "es/articles/boquete", "es/articles/el-valle-de-anton", "es/articles/panama-city"]
CHECK = "--check" in sys.argv


def lazy_srcs(p):
    for t in re.findall(r"<img\b[^>]*>", p.read_text(encoding="utf-8")):
        if "srcset=" in t or 'loading="lazy"' not in t:
            continue
        m = re.search(r'\ssrc="(?:https://panamaspot\.com)?(/images/[^"]+\.webp)"', t)
        if m and not re.search(r"-w(480|960)\.webp$", m[1]):
            yield m[1]


def main():
    pages = [p for p in OUT.rglob("*.html") if not str(p.relative_to(OUT)).startswith(("funnels", "preview", "_"))]
    seen = collections.Counter()
    for p in pages:
        for u in set(lazy_srcs(p)):
            seen[u] += 1
    scope = {u for u, c in seen.items() if c >= 50}
    for name in PAGES:
        scope |= set(lazy_srcs(OUT / f"{name}.html"))
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    made = 0
    for u in sorted(scope):
        f = PUB / u.lstrip("/")
        if not f.exists() or f.stat().st_size < 100_000:
            continue
        w = int(subprocess.run(["magick", "identify", "-format", "%w", str(f)], capture_output=True, text=True, check=True).stdout)
        if w < 800:
            continue
        widths = [480] + ([960] if w >= 1600 else [])
        for vw in widths:
            v = f.with_name(f"{f.stem}-w{vw}.webp")
            if CHECK:
                print("would make", v.relative_to(PUB)); continue
            if not v.exists() or v.stat().st_mtime < f.stat().st_mtime:
                subprocess.run(["magick", str(f), "-resize", f"{vw}x", "-strip", "-quality", "80", "-define", "webp:method=6", str(v)], check=True)
                made += 1
        manifest[u] = {"w": w, "variants": widths}
    if not CHECK:
        MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), indent=0) + "\n")
        print(f"{len(manifest)} photos in {MANIFEST.relative_to(ROOT)}; {made} variant files written")


if __name__ == "__main__":
    main()
