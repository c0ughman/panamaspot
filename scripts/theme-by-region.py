#!/usr/bin/env python3
"""
theme-by-region.py — green skin for the Boquete and El Valle clusters, the
default navy/red skin everywhere else.

`data-theme="green"` on <main class="article-page"> swaps the accent to green
and flattens the background to plain cream. Without it a page falls back to the
template default: navy headings, a red pop, and the graded background. The
2026-09 batch stamped green on every page it generated, including Bocas, San
Blas, the Pearl Islands and the nationwide guides, where the green reads as
someone else's brand.

Green is the e-bike clusters' colour — it belongs on the pages that carry the
E-Valley funnel. Everything else takes the default.

Idempotent.
    python3 scripts/theme-by-region.py
"""
import re, glob, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GREEN = ("boquete", "volcan-baru", "baru", "caldera", "lerida", "chiriqui", "quetzal",
         "feria", "jardin", "cafe", "coffee",
         "el-valle", "valle-de-anton", "albrook", "mariposario", "piedra", "mozas",
         "nispero", "india-dormida", "gaital", "macho", "termales", "canopy")

def is_green(name):
    n = name.lower()
    return any(k in n for k in GREEN)

def main():
    on = off = 0
    for f in sorted(glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html")):
        p = pathlib.Path(f)
        s = orig = p.read_text(encoding="utf-8")
        want = is_green(p.name)
        has = 'class="article-page" data-theme="green"' in s
        if want and not has:
            s = s.replace('<main class="article-page"', '<main class="article-page" data-theme="green"', 1)
        elif not want and has:
            s = s.replace('<main class="article-page" data-theme="green"', '<main class="article-page"', 1)
        if s != orig:
            p.write_text(s, encoding="utf-8")
            print(f"  {'green' if want else 'navy '}  {f.replace('public/','')}")
            on += want; off += (not want)
    print(f"\nswitched {off} pages to the default navy skin, {on} to green")

if __name__ == "__main__":
    main()
