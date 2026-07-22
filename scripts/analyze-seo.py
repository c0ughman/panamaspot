#!/usr/bin/env python3
"""
analyze-seo.py — read-only audit of two things across every article page:
  1. Images: are content images CSS background-image (bad for Google Images /
     a11y) or real <img> tags?  Per page + totals.
  2. Internal links: how many in-body internal links per page (excluding the
     shared site header/nav, breadcrumb, lang toggle and footer)?

    python3 scripts/analyze-seo.py
"""
import re, glob, pathlib

PAGES = sorted(glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html"))

def body_only(s):
    """Strip <head>/<style>/<script>, the fixed header, and the footer so we only
    look at real page content."""
    s = re.sub(r"<head\b.*?</head>", "", s, flags=re.S)
    s = re.sub(r"<style\b.*?</style>", "", s, flags=re.S)
    s = re.sub(r"<script\b.*?</script>", "", s, flags=re.S)
    s = re.sub(r"<header\b.*?</header>", "", s, flags=re.S)
    s = re.sub(r"<footer\b.*?</footer>", "", s, flags=re.S)
    return s

def article_prose(s):
    m = re.search(r'<article class="prose">.*?</article>', s, re.S)
    return m.group(0) if m else ""

def analyze():
    img_rows, link_rows = [], []
    tot_bg = tot_img = 0
    for p in PAGES:
        name = pathlib.Path(p).name
        raw = pathlib.Path(p).read_text()
        b = body_only(raw)
        # --- images: bg vs real <img> (content photos live in .imgph blocks + hero) ---
        bg = len(re.findall(r"background-image:url\(", b))
        realimg = len(re.findall(r"<img\b", b))
        tot_bg += bg; tot_img += realimg
        kind = "REAL <img>" if realimg and not bg else ("background" if bg and not realimg else "mixed")
        img_rows.append((name, bg, realimg, kind))
        # --- in-body internal links (inside <article class=prose>) ---
        prose = article_prose(raw)
        links = re.findall(r'<a\s[^>]*href="(/[^"#][^"]*)"', prose)
        internal = [l for l in links if l.startswith(("/articles/", "/es/articles/", "/#", "/"))]
        # keep only real article/section destinations, drop pure "/" home links count separately
        art_links = [l for l in internal if "/articles/" in l]
        link_rows.append((name, len(art_links), len(set(art_links))))
    return img_rows, link_rows, tot_bg, tot_img

def main():
    img_rows, link_rows, tot_bg, tot_img = analyze()
    print("=" * 72)
    print("1) IMAGE DELIVERY  (background-image = invisible to Google Images)")
    print("=" * 72)
    bgpages = [r for r in img_rows if r[3] == "background"]
    realpages = [r for r in img_rows if r[3] == "REAL <img>"]
    mixed = [r for r in img_rows if r[3] == "mixed"]
    print(f"  pages all-background : {len(bgpages)}")
    print(f"  pages all-real-<img> : {len(realpages)}")
    print(f"  pages mixed          : {len(mixed)}")
    print(f"  TOTAL background-image instances: {tot_bg}")
    print(f"  TOTAL real <img> instances      : {tot_img}")
    print("\n  --- all-background pages (need conversion) ---")
    for n, bg, ri, k in sorted(bgpages):
        print(f"    {bg:3d} bg  {n}")
    print("\n  --- mixed pages ---")
    for n, bg, ri, k in sorted(mixed):
        print(f"    {bg:3d} bg / {ri:3d} img  {n}")
    print("\n" + "=" * 72)
    print("2) IN-BODY INTERNAL LINKS  (links to other /articles/ inside the prose)")
    print("=" * 72)
    counts = [c for _, c, _ in link_rows]
    avg = sum(counts) / len(counts) if counts else 0
    print(f"  pages analyzed: {len(link_rows)}")
    print(f"  avg in-body article links/page: {avg:.1f}")
    print(f"  pages with 0 in-body links: {sum(1 for c in counts if c == 0)}")
    print(f"  min/max: {min(counts)}/{max(counts)}")
    print("\n  per page (unique in parens):")
    for n, c, u in sorted(link_rows, key=lambda r: r[1]):
        print(f"    {c:2d} ({u:2d} uniq)  {n}")

if __name__ == "__main__":
    main()
