#!/usr/bin/env python3
"""
schema-graph-fix.py — repair the structured-data graph.

Article.mainEntityOfPage pointed at `<url>#webpage`, but no WebPage node with
that @id existed anywhere on the page — a dangling reference. The nodes were
also unconnected: BreadcrumbList and Article carried no @id, so nothing could
link to them and each node floated on its own.

This adds the missing WebPage and wires the graph the way Google's own examples
do:

    WebSite  <-- isPartOf --  WebPage  --breadcrumb-->  BreadcrumbList
                                 ^
                                 |  isPartOf / mainEntityOfPage
                              Article

  WebPage         @id <url>#webpage, isPartOf the site, carries the breadcrumb,
                  the primary image, the dates and the language
  BreadcrumbList  @id <url>#breadcrumb, so WebPage.breadcrumb resolves
  Article         @id <url>#article, isPartOf the WebPage

Idempotent. Run after enrich-images.py (which rewrites Article.image and leaves
everything else alone).
    python3 scripts/schema-graph-fix.py [slug ...]
"""
import re, sys, json, html, glob, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://panamaspot.com"

def blocks(s):
    return [(m.start(1), m.end(1), m.group(1))
            for m in re.finditer(r'(?s)<script[^>]*application/ld\+json[^>]*>(.*?)</script>', s)]

def process(path):
    p = pathlib.Path(path)
    s = orig = p.read_text(encoding="utf-8")
    url = BASE + "/" + p.as_posix().split("public/", 1)[1][:-5]
    lang = "es" if "/es/" in p.as_posix() else "en"

    def _safe(raw):
        try: return json.loads(raw)
        except Exception: return {}
    art = bc = None
    for st, en, raw in blocks(s):
        try: d = json.loads(raw)
        except Exception: continue
        if d.get("@type") in ("Article", "BlogPosting"): art = d
        elif d.get("@type") == "BreadcrumbList": bc = d
    if not art:
        return False

    title = re.search(r"<title>(.*?)</title>", s, re.S)
    desc = re.search(r'<meta content="([^"]*)" name="description"/>', s)
    hero = re.search(r'art-hero-img-full"><img src="([^"]+)"', s) \
        or re.search(r'hub-hero-img"><img[^>]*src="([^"]+)"', s)

    # 1. give the breadcrumb an @id so it can be referenced
    if bc is not None and bc.get("@id") != url + "#breadcrumb":
        new_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList",
                  "@id": url + "#breadcrumb", "itemListElement": bc["itemListElement"]}
        for st, en, raw in blocks(s):
            try:
                if json.loads(raw).get("@type") == "BreadcrumbList":
                    s = s[:st] + json.dumps(new_bc, ensure_ascii=False) + s[en:]
                    break
            except Exception: pass

    # 2. the WebPage the Article already claimed to belong to.
    #    mainEntityOfPage declares it INLINE as {"@type":"WebPage","@id":…} — valid,
    #    but a bare stub with no properties. Look for a real top-level node, not
    #    the substring, or this never fires.
    has_wp = any(_safe(raw).get("@type") == "WebPage"
                 for _, _, raw in blocks(s)
                 if raw.strip().startswith("{"))
    if not has_wp:
        wp = {"@context": "https://schema.org", "@type": "WebPage",
              "@id": url + "#webpage", "url": url,
              "name": html.unescape(title.group(1)).strip() if title else "",
              "isPartOf": {"@id": BASE + "/#website"},
              "inLanguage": lang}
        if desc: wp["description"] = html.unescape(desc.group(1))
        if bc is not None: wp["breadcrumb"] = {"@id": url + "#breadcrumb"}
        if hero: wp["primaryImageOfPage"] = {"@type": "ImageObject",
                                             "url": hero.group(1).replace("&amp;", "&")}
        for k in ("datePublished", "dateModified"):
            if art.get(k): wp[k] = art[k]
        block = ('<script type="application/ld+json">'
                 + json.dumps(wp, ensure_ascii=False) + "</script>")
        # sit it just before the Article node
        m = re.search(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "(?:Article|BlogPosting)"', s)
        if m: s = s[:m.start()] + block + s[m.start():]
        else: s = s.replace("</head>", block + "</head>", 1)

    # 3. anchor the Article and point it at the WebPage.
    #    Parse and re-serialise the node rather than splicing a string in: a
    #    prefix-only guard cannot see fields the rest of the pipeline appended,
    #    so it re-inserted @id/isPartOf on every run and stacked duplicate JSON
    #    keys. Re-serialising also normalises any that already accumulated.
    out = []
    last = 0
    for st, en, raw in blocks(s):
        d = _safe(raw)
        if not d:
            continue
        changed = False
        if d.get("@type") in ("Article", "BlogPosting"):
            if d.get("@id") != url + "#article":
                d["@id"] = url + "#article"; changed = True
            if d.get("isPartOf") != {"@id": url + "#webpage"}:
                d["isPartOf"] = {"@id": url + "#webpage"}; changed = True
            # key order: @context/@type/@id first, as the rest of the site emits
            d = {k: d[k] for k in ["@context", "@type", "@id"] if k in d} | \
                {k: v for k, v in d.items() if k not in ("@context", "@type", "@id")}
            changed = True
        if changed or raw != json.dumps(d, ensure_ascii=False):
            out.append((st, en, json.dumps(d, ensure_ascii=False)))
    for st, en, txt in sorted(out, reverse=True):
        s = s[:st] + txt + s[en:]

    if s != orig:
        p.write_text(s, encoding="utf-8")
        return True
    return False

def main():
    args = sys.argv[1:]
    files = ([ROOT/"public"/"articles"/f"{a}.html" for a in args] if args
             else sorted(glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html")))
    n = 0
    for f in files:
        if process(f): n += 1
    print(f"  graph wired on {n} pages")

if __name__ == "__main__":
    main()
