#!/usr/bin/env python3
"""
fix-local-img-dims.py — rewrite width/height on /images/boquete/ <img> tags
from scripts/img-dims.json.

Needed after the HEIC re-conversion: the first pass piped HEIC through
`sips -s format png`, which drops EXIF orientation, so 28 portrait photographs
were written to WebP on their side and every width/height attribute derived
from them had the axes swapped. Re-encoded with `magick -auto-orient`; this
brings the markup back in line.

    python3 scripts/fix-local-img-dims.py
"""
import re, json, glob, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIMS = json.loads((ROOT / "scripts" / "img-dims.json").read_text())
TARGET = {"hero": 1280, "inline": 960, "gallery": 960, "card": 500}


def capped(key, target):
    d = DIMS.get(key)
    if not d:
        return None
    ow, oh = d["w"], d["h"]
    if ow <= target:
        return ow, oh
    return target, round(oh * target / ow)


def main():
    total = 0
    for f in sorted(glob.glob(str(ROOT / "public/articles/*.html")) +
                    glob.glob(str(ROOT / "public/es/articles/*.html"))):
        p = pathlib.Path(f); s = orig = p.read_text(encoding="utf-8")

        def fix(m):
            nonlocal s
            whole, src = m.group(0), m.group(1)
            key = src.split("?")[0]
            if not key.startswith("/images/boquete/"):
                return whole
            # a hero <img> sits inside .art-hero-img-full; everything else is 960
            i = s.find(whole)
            is_hero = 'art-hero-img-full"><img' in s[max(0, i - 40):i + 12]
            c = capped(key, TARGET["hero"] if is_hero else TARGET["inline"])
            if not c:
                return whole
            out = re.sub(r'width="\d+"', f'width="{c[0]}"', whole)
            out = re.sub(r'height="\d+"', f'height="{c[1]}"', out)
            return out

        s2 = re.sub(r'<img[^>]*\bsrc="(/images/boquete/[^"]+)"[^>]*>', fix, s)
        if s2 != orig:
            p.write_text(s2, encoding="utf-8")
            n = sum(1 for _ in re.finditer(r'<img[^>]*\bsrc="/images/boquete/[^"]+"[^>]*>', s2))
            total += 1
            print(f"  ✓ {f.split('public/')[-1]:<58} {n} local <img>")
    print(f"pages rewritten: {total}")


if __name__ == "__main__":
    main()
