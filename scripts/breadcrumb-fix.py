#!/usr/bin/env python3
"""
breadcrumb-fix.py — make every BreadcrumbList JSON-LD valid. Google requires an
`item` (URL) on every crumb except the last, but the middle (region/province)
crumbs either had no `item` or pointed at pages that don't exist
(/articles/boquete, /articles/el-valle-de-anton). This gives every non-last crumb
a valid URL: an existing page if the target resolves, otherwise the homepage's
Destinations section (#cat-regions). The last crumb (the article) is left as-is.

Idempotent. The visible HTML breadcrumb is already link-free text, so only the
structured data is touched.
    python3 scripts/breadcrumb-fix.py
"""
import re, json, glob, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

def path_of(url):
    return re.sub(r"^https?://panamaspot\.com", "", url or "")

# valid on-site targets: every page canonical + roots + the two Next region pages
VALID = {"/", "/es", "/articles/panama-city", "/articles/bocas-del-toro",
         "/#cat-regions", "/es#cat-regions"}
for p in glob.glob(str(ROOT/"public"/"articles"/"*.html")) + glob.glob(str(ROOT/"public"/"es"/"articles"/"*.html")):
    c = re.search(r'<link href="https://panamaspot\.com([^"]+)" rel="canonical"/>', pathlib.Path(p).read_text())
    if c:
        VALID.add(c.group(1))

def fix_page(page):
    p = pathlib.Path(page)
    s = p.read_text()
    anchor = "https://panamaspot.com/es#cat-regions" if "/es/" in page else "https://panamaspot.com/#cat-regions"
    fixed = 0

    def repl(m):
        nonlocal fixed
        bl = json.loads(m.group(1))
        items = bl.get("itemListElement", [])
        for i, it in enumerate(items):
            if i == len(items) - 1:
                continue                      # last crumb: item is optional
            u = it.get("item")
            if not isinstance(u, str) or path_of(u) not in VALID:
                it["item"] = anchor
                fixed += 1
        return '<script type="application/ld+json">' + json.dumps(bl, ensure_ascii=False) + "</script>"

    s = re.sub(r'<script type="application/ld\+json">(\{"@context": "https://schema\.org", "@type": "BreadcrumbList".*?\})</script>',
               repl, s, flags=re.S)
    if fixed:
        p.write_text(s)
    return fixed

def main():
    total = pages = 0
    for page in sorted(glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html")):
        n = fix_page(page)
        if n:
            pages += 1; total += n
    print(f"fixed {total} breadcrumb items across {pages} pages")

if __name__ == "__main__":
    main()
