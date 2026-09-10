#!/usr/bin/env python3
"""
audit-boquete-seo.py — deep technical-SEO audit of the 2026-09 Boquete pages.

Checks the things that actually change how a page is understood or ranked, and
reports the ones that are wrong rather than a score. Read-only.

    python3 scripts/audit-boquete-seo.py [--all]
"""
import re, sys, json, glob, html, pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent

PAGES = [
 "public/articles/best-time-to-visit-boquete.html",
 "public/articles/boquete-bike-rental.html",
 "public/articles/boquete-cycling-routes.html",
 "public/articles/boquete-hot-springs-caldera-vs-los-pozos.html",
 "public/articles/panama-city-to-boquete.html",
 "public/articles/quetzal-season-boquete-when-where-to-see-resplendent-quetzal.html",
 "public/articles/where-to-stay-in-boquete.html",
 "public/es/articles/boquete-con-ninos-guia-familiar.html",
 "public/es/articles/cuanto-cuesta-boquete-presupuesto-semana.html",
 "public/es/articles/el-volcan-baru-esta-activo.html",
 "public/es/articles/feria-de-las-flores-y-del-cafe-boquete.html",
 "public/es/articles/mi-jardin-es-su-jardin-boquete.html",
]

FAIL, WARN = "FAIL", "warn"
issues = defaultdict(list)


def add(page, level, code, detail):
    issues[page].append((level, code, detail))


def text_of(s):
    b = s[s.find("</style>"):]
    for pat in (r"(?s)<script.*?</script>", r"(?s)<style.*?</style>",
                r"(?s)<!--RELATED-MODULE-->.*?<!--/RELATED-MODULE-->",
                r"(?s)<!--IMGDESC-->.*?<!--/IMGDESC-->",
                r"(?s)<header.*?</header>", r"(?s)<footer.*?</footer>"):
        b = re.sub(pat, " ", b)
    return html.unescape(re.sub(r"<[^>]+>", " ", b))


def jsonld(s):
    out = []
    for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
        try:
            out.append((json.loads(m.group(1)), None))
        except json.JSONDecodeError as e:
            out.append((None, str(e)))
    return out


def audit(path):
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    name = path.split("public/")[-1]
    es = "/es/" in path
    slug = p.stem

    # ---------------------------------------------------------------- head
    lang = re.search(r'<html[^>]*\blang="([^"]+)"', s)
    if not lang:
        add(name, FAIL, "lang", "<html> has no lang attribute")
    elif lang.group(1) != ("es" if es else "en"):
        add(name, FAIL, "lang", f'<html lang="{lang.group(1)}"> on a {"Spanish" if es else "English"} page')

    t = re.search(r"<title>(.*?)</title>", s, re.S)
    if not t:
        add(name, FAIL, "title", "no <title>")
    else:
        tt = html.unescape(t.group(1)).strip()
        if len(tt) > 60:
            add(name, WARN, "title-len", f"{len(tt)} chars, likely truncated in results: {tt[:70]}")
        if len(tt) < 20:
            add(name, WARN, "title-len", f"only {len(tt)} chars")

    d = re.search(r'<meta content="([^"]*)" name="description"', s) or \
        re.search(r'<meta name="description" content="([^"]*)"', s)
    if not d:
        add(name, FAIL, "meta-desc", "no meta description")
    else:
        dd = html.unescape(d.group(1)).strip()
        if not dd:
            add(name, FAIL, "meta-desc", "meta description is empty")
        elif len(dd) > 160:
            add(name, WARN, "meta-desc-len", f"{len(dd)} chars, will be truncated")
        elif len(dd) < 70:
            add(name, WARN, "meta-desc-len", f"only {len(dd)} chars, under-using the snippet")

    can = re.search(r'<link href="([^"]+)" rel="canonical"', s) or \
          re.search(r'<link rel="canonical" href="([^"]+)"', s)
    if not can:
        add(name, FAIL, "canonical", "no canonical")
    else:
        want = f"https://panamaspot.com/{'es/' if es else ''}articles/{slug}"
        if can.group(1) != want:
            add(name, FAIL, "canonical", f"points at {can.group(1)}, expected {want}")

    rob = re.search(r'<meta content="([^"]*)" name="robots"', s)
    if rob and "noindex" in rob.group(1):
        add(name, FAIL, "robots", f'robots = "{rob.group(1)}"')

    # hreflang: must self-reference, and every alternate must resolve
    alts = re.findall(r'<link href="([^"]+)" hreflang="([^"]+)" rel="alternate"', s)
    if not alts:
        add(name, WARN, "hreflang", "no hreflang alternates")
    else:
        selfhref = f"https://panamaspot.com/{'es/' if es else ''}articles/{slug}"
        langs = {l: h for h, l in alts}
        if langs.get("es" if es else "en") != selfhref:
            add(name, FAIL, "hreflang-self", f"no self-referencing hreflang for '{'es' if es else 'en'}'")
        for href, l in alts:
            rel = href.replace("https://panamaspot.com", "")
            f = ROOT / "public" / rel.lstrip("/")
            if not (f.with_suffix(".html")).exists() and not (ROOT / "public" / (rel.lstrip("/") + ".html")).exists():
                add(name, FAIL, "hreflang-404", f"{l} -> {href} does not exist")

    # open graph / twitter
    for prop, code in (("og:title", "og"), ("og:description", "og"), ("og:image", "og"),
                       ("og:url", "og"), ("og:type", "og"), ("og:locale", "og")):
        if f'property="{prop}"' not in s:
            add(name, WARN, code, f"missing {prop}")
    loc = re.search(r'<meta content="([^"]*)" property="og:locale"', s)
    if loc and loc.group(1) != ("es_PA" if es else "en_US"):
        add(name, FAIL, "og-locale", f'og:locale = {loc.group(1)}')
    if 'name="twitter:card"' not in s:
        add(name, WARN, "twitter", "missing twitter:card")

    # ------------------------------------------------------------ headings
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    if len(h1) != 1:
        add(name, FAIL, "h1", f"{len(h1)} <h1> elements (want exactly 1)")
    levels = [int(m.group(1)) for m in re.finditer(r"<h([1-6])\b", s)]
    prev = 0
    for lv in levels:
        if prev and lv > prev + 1:
            add(name, WARN, "heading-skip", f"h{prev} jumps straight to h{lv}")
            break
        prev = lv

    # --------------------------------------------------------- breadcrumbs
    crumbs = None
    for data, err in jsonld(s):
        if err:
            add(name, FAIL, "jsonld-parse", err); continue
        for node in (data if isinstance(data, list) else [data]):
            if isinstance(node, dict) and node.get("@type") == "BreadcrumbList":
                crumbs = node
    if not crumbs:
        add(name, FAIL, "breadcrumb", "no BreadcrumbList")
    else:
        els = crumbs.get("itemListElement", [])
        for i, el in enumerate(els, 1):
            if el.get("position") != i:
                add(name, FAIL, "breadcrumb-pos", f"item {i} has position {el.get('position')}")
            if not el.get("item"):
                add(name, FAIL, "breadcrumb-item", f"crumb '{el.get('name')}' has no URL")
        last = els[-1] if els else {}
        if last.get("item") and not last["item"].rstrip("/").endswith(slug):
            add(name, FAIL, "breadcrumb-last", f"final crumb points at {last['item']}, not this page")
        vis = re.search(r'(?s)<(nav|div|ol)[^>]*class="breadcrumb"[^>]*>.*?</\1>', s)
        if not vis:
            add(name, WARN, "breadcrumb-visible", "JSON-LD breadcrumb but none rendered on the page")
        else:
            vtxt = [x.strip() for x in re.split(r"/", html.unescape(re.sub(r"<[^>]+>", "|", vis.group(0)))) if x.strip("| ")]
            if len(vtxt) != len(els):
                add(name, WARN, "breadcrumb-mismatch",
                    f"{len(els)} crumbs in JSON-LD, {len(vtxt)} rendered")

    # ------------------------------------------------------------- article
    art = None
    for data, err in jsonld(s):
        if err: continue
        for node in (data if isinstance(data, list) else [data]):
            if isinstance(node, dict) and node.get("@type") in ("Article", "BlogPosting", "NewsArticle"):
                art = node
    if not art:
        add(name, FAIL, "article-schema", "no Article node")
    else:
        for f in ("headline", "description", "datePublished", "dateModified", "author", "publisher", "image"):
            if not art.get(f):
                add(name, FAIL, "article-field", f"Article missing {f}")
        if art.get("headline") and len(art["headline"]) > 110:
            add(name, WARN, "headline-len", f"headline {len(art['headline'])} chars (Google caps ~110)")
        il = art.get("inLanguage")
        if il and il not in (("es", "es-PA") if es else ("en", "en-US")):
            add(name, FAIL, "inlanguage", f'inLanguage = "{il}"')
        if not il:
            add(name, WARN, "inlanguage", "Article has no inLanguage")
        mo = art.get("mainEntityOfPage")
        if isinstance(mo, dict) and mo.get("@id"):
            ids = set()
            for data2, e2 in jsonld(s):
                if e2: continue
                for n2 in (data2 if isinstance(data2, list) else [data2]):
                    if isinstance(n2, dict) and n2.get("@id"):
                        ids.add(n2["@id"])
            # a fragment @id is right as long as the node it names is in the graph
            if mo["@id"] not in ids and slug not in mo["@id"]:
                add(name, FAIL, "mainentity", f"mainEntityOfPage names {mo['@id']}, which is not in the graph")

    # FAQ
    for data, err in jsonld(s):
        if err: continue
        for node in (data if isinstance(data, list) else [data]):
            if isinstance(node, dict) and node.get("@type") == "FAQPage":
                for q in node.get("mainEntity", []):
                    a = q.get("acceptedAnswer", {})
                    if not a.get("text"):
                        add(name, FAIL, "faq", f"FAQ '{str(q.get('name'))[:40]}' has no answer text")

    # -------------------------------------------------------------- images
    body = re.sub(r"(?s)<!--RELATED-MODULE-->.*?<!--/RELATED-MODULE-->", "", s)
    imgs = re.findall(r"<img[^>]*>", body)
    for im in imgs:
        src = re.search(r'src="([^"]+)"', im)
        if not src:
            add(name, FAIL, "img-src", "an <img> has no src"); continue
        a = re.search(r'alt="([^"]*)"', im)
        if a is None:
            add(name, FAIL, "img-alt", f"no alt: {src.group(1)[-46:]}")
        elif not a.group(1).strip():
            add(name, WARN, "img-alt-empty", f"empty alt: {src.group(1)[-46:]}")
        if not (re.search(r'\bwidth="\d+"', im) and re.search(r'\bheight="\d+"', im)):
            add(name, WARN, "img-dims", f"no width/height (CLS): {src.group(1)[-46:]}")
    heroes = re.findall(r'art-hero-img-full"><img[^>]*>', s)
    for h in heroes:
        if 'loading="lazy"' in h:
            add(name, FAIL, "hero-lazy", "the LCP hero is lazy-loaded")
        if "fetchpriority" not in h:
            add(name, WARN, "hero-priority", "hero has no fetchpriority=high")

    # --------------------------------------------------------------- links
    nohdr = re.sub(r"(?s)<header.*?</header>", "", s)
    nohdr = re.sub(r"(?s)<footer.*?</footer>", "", nohdr)
    for href in set(re.findall(r'href="(/(?:es/)?articles/[^"#?]+)"', nohdr)):
        tgt = ROOT / "public" / href.lstrip("/")
        if not tgt.with_suffix(".html").exists():
            add(name, FAIL, "dead-link", href)
        if href.startswith("/es/") != es:
            add(name, FAIL, "xlang-link", href)

    # ------------------------------------------------------------ content
    words = len(text_of(s).split())
    if words < 600:
        add(name, WARN, "thin", f"only {words} words of body copy")
    return name, words


def main():
    rows = []
    for path in PAGES:
        rows.append(audit(path))

    # cross-page uniqueness
    seen_t, seen_d = defaultdict(list), defaultdict(list)
    for path in PAGES:
        s = (ROOT / path).read_text(encoding="utf-8")
        n = path.split("public/")[-1]
        t = re.search(r"<title>(.*?)</title>", s, re.S)
        d = re.search(r'<meta content="([^"]*)" name="description"', s)
        if t: seen_t[html.unescape(t.group(1)).strip()].append(n)
        if d: seen_d[html.unescape(d.group(1)).strip()].append(n)
    for val, pages in seen_t.items():
        if len(pages) > 1:
            for pg in pages: add(pg, FAIL, "dup-title", f'shared with {len(pages)-1} other page(s): "{val[:50]}"')
    for val, pages in seen_d.items():
        if len(pages) > 1:
            for pg in pages: add(pg, FAIL, "dup-desc", f"description shared with {len(pages)-1} other page(s)")

    nf = nw = 0
    for name, words in rows:
        its = issues.get(name, [])
        f = [i for i in its if i[0] == FAIL]; w = [i for i in its if i[0] == WARN]
        nf += len(f); nw += len(w)
        flag = "" if not f else "  ← FAIL"
        print(f"\n{name}  ({words} words){flag}")
        if not its:
            print("   clean")
        for lvl, code, det in sorted(its, key=lambda x: (x[0] != FAIL, x[1])):
            print(f"   {'FAIL' if lvl == FAIL else 'warn'}  {code:<20} {det}")
    print(f"\n{'='*70}\n{nf} failures, {nw} warnings across {len(PAGES)} pages")


if __name__ == "__main__":
    main()
