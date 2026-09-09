#!/usr/bin/env python3
"""
seo-audit.py — everything a crawler sees and a reader does not.

Checks the head, the structured-data graph, the heading outline, every <img>,
every internal link and the crawl signals, and reports per page. Written for the
2026-09 El Valle batch but runs on any article page.

    python3 scripts/seo-audit.py                 # the El Valle batch
    python3 scripts/seo-audit.py --all           # every article page
    python3 scripts/seo-audit.py --page <slug>   # one page, verbose
"""
import re, sys, json, glob, html, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://panamaspot.com"
BATCH = json.loads((ROOT / "scripts/elvalle-image-plan.json").read_text(encoding="utf-8"))

TITLE_MAX, DESC_MIN, DESC_MAX, ALT_MAX, H1_MAX = 62, 110, 160, 125, 70


def jsonld(s):
    out = []
    for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
        try:
            out.append(json.loads(m.group(1)))
        except json.JSONDecodeError as e:
            out.append({"__invalid__": str(e)})
    return out


def audit(path):
    s = pathlib.Path(path).read_text(encoding="utf-8")
    slug = pathlib.Path(path).stem
    es = "/es/" in path.replace("\\", "/")
    bad, warn = [], []
    G = jsonld(s)
    by = {}
    for d in G:
        if "__invalid__" in d:
            bad.append(f"invalid JSON-LD: {d['__invalid__']}")
        else:
            by.setdefault(d.get("@type"), []).append(d)

    # ── head ────────────────────────────────────────────────────────────────
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    title = html.unescape(t.group(1)).strip() if t else ""
    if not title: bad.append("no <title>")
    elif len(title) > TITLE_MAX: warn.append(f"title {len(title)} chars (>{TITLE_MAX})")

    dm = re.search(r'<meta content="([^"]*)" name="description"/>', s) or \
         re.search(r'<meta name="description" content="([^"]*)"', s)
    desc = html.unescape(dm.group(1)) if dm else ""
    if not desc: bad.append("no meta description")
    elif len(desc) > DESC_MAX: warn.append(f"meta description {len(desc)} chars (>{DESC_MAX})")
    elif len(desc) < DESC_MIN: warn.append(f"meta description {len(desc)} chars (<{DESC_MIN})")

    if not re.search(r'<link[^>]*rel="canonical"', s): bad.append("no canonical")
    else:
        c = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"', s) or \
            re.search(r'<link[^>]*href="([^"]+)"[^>]*rel="canonical"', s)
        want = f"{BASE}/{'es/' if es else ''}articles/{slug}"
        if c and c.group(1).rstrip('/') != want: bad.append(f"canonical is {c.group(1)} not {want}")

    for prop in ("og:title", "og:description", "og:image", "og:image:alt", "og:type",
                 "og:url", "og:site_name", "og:locale"):
        if f'property="{prop}"' not in s: warn.append(f"missing {prop}")
    for nm in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
        if f'name="{nm}"' not in s: warn.append(f"missing {nm}")
    # summary_large_image asks every social platform to render the og:image in a
    # 1.91:1 frame, which they do by centre-cropping. A portrait image loses most
    # of its height to that crop and usually its subject with it, so a portrait
    # og:image and this card type together are a defect, not a preference.
    tw = re.search(r'<meta content="([^"]*)" name="twitter:card"/>', s)
    ow = re.search(r'<meta content="(\d+)" property="og:image:width"/>', s)
    oh = re.search(r'<meta content="(\d+)" property="og:image:height"/>', s)
    if tw and tw.group(1) == "summary_large_image" and ow and oh:
        ar = int(ow.group(1)) / int(oh.group(1))
        if ar < 1.2:
            bad.append(f"og:image is {ow.group(1)}x{oh.group(1)} (ar {ar:.2f}) "
                       f"but twitter:card is summary_large_image — run social-cards.py")
    elif tw and tw.group(1) == "summary_large_image" and not (ow and oh):
        warn.append("summary_large_image with no og:image dimensions")

    # Every other bit of chrome on a Spanish page is translated; a stray English
    # heading is a leak from the template, and readers see it.
    if es:
        import html as _h
        vis = re.sub(r'(?s)<script.*?</script>|<style.*?</style>', '', s)
        for m in re.finditer(r'<span class="eyebrow">(.*?)</span>', vis, re.S):
            t = _h.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
            if t in ("Questions", "In pictures", "The short version",
                     "Keep exploring", "More to see", "The photographs"):
                bad.append(f'English eyebrow on a Spanish page: "{t}"')
                break

    loc = re.search(r'<meta content="([^"]*)" property="og:locale"/>', s)
    if loc and ((es and not loc.group(1).startswith("es")) or (not es and not loc.group(1).startswith("en"))):
        bad.append(f"og:locale {loc.group(1)} wrong for this language")

    hl = {}
    for m in re.finditer(r'<link[^>]*rel="alternate"[^>]*>', s):
        tag = m.group(0)
        lg = re.search(r'hreflang="([^"]+)"', tag); hf = re.search(r'href="([^"]+)"', tag)
        if lg and hf: hl[lg.group(1)] = hf.group(1)
    self_lang = "es" if es else "en"
    if self_lang not in hl: bad.append("hreflang missing self-reference")
    elif hl[self_lang].rstrip('/') != f"{BASE}/{'es/' if es else ''}articles/{slug}":
        bad.append(f"hreflang {self_lang} points at {hl[self_lang]}")
    if "x-default" not in hl: warn.append("no hreflang x-default")

    if re.search(r'<meta[^>]*name="robots"[^>]*content="[^"]*noindex', s): bad.append("noindex!")

    # ── headings ────────────────────────────────────────────────────────────
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    if len(h1) != 1: bad.append(f"{len(h1)} <h1> (want exactly 1)")
    else:
        h1t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h1[0]))).strip()
        if len(h1t) > H1_MAX: warn.append(f"h1 {len(h1t)} chars")
    levels = [int(m.group(1)) for m in re.finditer(r"<h([1-6])\b", s)]
    for a, b in zip(levels, levels[1:]):
        if b > a + 1:
            warn.append(f"heading level skip h{a}->h{b}"); break

    ids = re.findall(r'\sid="([^"]+)"', s)
    dup = [i for i, n in collections.Counter(ids).items() if n > 1]
    if dup: bad.append(f"duplicate id(s): {dup[:5]}")

    # The four destination hubs are a different, legitimate layout: CollectionPage
    # instead of Article, hub-hero-img instead of art-hero-img-full, cards instead
    # of prose. Judge them on their own terms.
    is_hub = "hub-hero-img" in s
    art = re.search(r"(?s)<article\b.*?</article>", s)
    body = art.group(0) if art else s
    sec_ids = re.findall(r'<h2 id="(s\d+)"', body)
    toc = re.findall(r'href="#(s\d+)"', s)
    missing_toc = [x for x in set(toc) if x not in sec_ids]
    if missing_toc: bad.append(f"TOC anchors with no section: {missing_toc}")

    # ── images ──────────────────────────────────────────────────────────────
    imgs = re.findall(r"<img[^>]*>", body)
    eager = [i for i in re.findall(r"<img[^>]*>", s) if 'loading="eager"' in i]
    hero = re.search(r'<div class="(?:art-hero-img-full|hub-hero-img)"><img[^>]*>', s)
    if not hero: bad.append("no hero <img>")
    if len(eager) != 1: warn.append(f"{len(eager)} eager images (want 1: the LCP hero)")
    noalt = [i for i in imgs if 'alt="' not in i]
    if noalt: bad.append(f"{len(noalt)} <img> with no alt attribute at all")
    # alt="" is correct a11y for a card image inside a link whose heading is the
    # label — the hubs do this deliberately. Only flag it outside that pattern.
    empty = [i for i in imgs if 'alt=""' in i and 'hub-card-img' not in body[:0]]
    if empty and not is_hub: warn.append(f"{len(empty)} <img> with empty alt")
    nodim = [i for i in imgs if not (re.search(r'\bwidth="\d+"', i) and re.search(r'\bheight="\d+"', i))]
    if nodim: bad.append(f"{len(nodim)} <img> without width+height (CLS)")
    longalt = [html.unescape(re.search(r'alt="([^"]*)"', i).group(1)) for i in imgs
               if re.search(r'alt="([^"]*)"', i) and len(re.search(r'alt="([^"]*)"', i).group(1)) > ALT_MAX]
    if longalt: warn.append(f"{len(longalt)} alt >{ALT_MAX} chars")
    remote = [i for i in imgs if "srcset" not in i and "upload.wikimedia" in i]
    if remote: warn.append(f"{len(remote)} remote <img> with no srcset")
    if hero and "fetchpriority=\"high\"" not in hero.group(0): warn.append("hero has no fetchpriority=high")
    if not re.search(r'<link[^>]*rel="preload"[^>]*as="image"', s): warn.append("no hero preload")
    if not re.search(r'<link[^>]*rel="preconnect"', s): warn.append("no preconnect to the image CDN")

    # ── structured data ─────────────────────────────────────────────────────
    if is_hub:
        if not by.get("CollectionPage"): bad.append("hub without CollectionPage schema")
        if not by.get("TouristDestination"): bad.append("hub without TouristDestination schema")
    elif not by.get("Article"): bad.append("no Article schema")
    elif by.get("Article"):
        a = by["Article"][0]
        for k in ("headline", "image", "datePublished", "dateModified", "author",
                  "publisher", "mainEntityOfPage", "inLanguage", "@id"):
            if k not in a: bad.append(f"Article missing {k}")
        if len(str(a.get("headline", ""))) > 110: warn.append("Article headline >110 chars")
        if a.get("inLanguage") and a["inLanguage"][:2] != self_lang:
            bad.append(f"Article inLanguage={a['inLanguage']} on a {self_lang} page")
        imgs_ld = a.get("image") or []
        if isinstance(imgs_ld, list):
            rendered = {re.sub(r'[?&]w=\d+', '', re.sub(r'/\d+px-([^/]+)$', r'/\1', h.replace("&amp;", "&")))
                        for h in re.findall(r'<img[^>]*\bsrc="([^"]+)"', body)}
            for io in imgs_ld:
                if not isinstance(io, dict): continue
                own = str(io.get("contentUrl", "")).startswith(("/images/", f"{BASE}/images/"))
                need = ("contentUrl", "width", "height", "caption")
                # a licence URL is only meaningful for third-party files; an
                # image credited to its author with no rights page cannot honestly
                # claim one
                need += () if (own or "creator" in io) else ("license",)
                if own and "creator" not in io:
                    warn.append("own ImageObject without creator")
                for k in need:
                    if k not in io: warn.append(f"ImageObject missing {k}"); break
    if not by.get("BreadcrumbList"): bad.append("no BreadcrumbList")
    else:
        b = by["BreadcrumbList"][0]["itemListElement"]
        pos = [x.get("position") for x in b]
        if pos != list(range(1, len(b) + 1)): bad.append(f"breadcrumb positions {pos}")
        if any("item" not in x for x in b[:-1]):
            bad.append("breadcrumb ListItem without item")   # the LAST one may omit it
        last = b[-1]
        if isinstance(last.get("item"), str) and last["item"].rstrip('/') != \
           f"{BASE}/{'es/' if es else ''}articles/{slug}":
            warn.append("last breadcrumb does not point at this page")
        vis = re.findall(r'<nav[^>]*class="breadcrumb"[^>]*>(.*?)</nav>', s, re.S)
        if vis:
            names = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()
                     for x in re.findall(r"<(?:a|span)[^>]*>(.*?)</(?:a|span)>", vis[0], re.S)]
            names = [n for n in names if n and n != "/"]
            sch = [x.get("name") for x in b]
            if len(names) != len(sch): warn.append(f"visible breadcrumb {len(names)} vs schema {len(sch)}")
    if not by.get("WebPage") and not is_hub: warn.append("no WebPage node")
    if by.get("FAQPage"):
        qs = by["FAQPage"][0].get("mainEntity", [])
        visible = len(re.findall(r'class="faq-q"', s))
        if visible and visible != len(qs):
            bad.append(f"FAQ schema {len(qs)} vs visible {visible}")
        for q in qs:
            txt = q.get("acceptedAnswer", {}).get("text", "")[:50]
            if txt and txt not in html.unescape(re.sub(r"<[^>]+>", " ", s)):
                bad.append("FAQ answer not present in visible HTML"); break
    ldids = [d.get("@id") for d in G if isinstance(d, dict) and d.get("@id")]
    d2 = [i for i, n in collections.Counter(ldids).items() if n > 1]
    if d2: bad.append(f"duplicate @id in JSON-LD: {d2}")

    # ── links ───────────────────────────────────────────────────────────────
    have = {pathlib.Path(f).stem for f in glob.glob(str(ROOT / "public/articles/*.html"))}
    haves = {pathlib.Path(f).stem for f in glob.glob(str(ROOT / "public/es/articles/*.html"))}
    for m in re.finditer(r'href="/(es/)?articles/([^"#?]+)"', s):
        pool = haves if m.group(1) else have
        if m.group(2) not in pool: bad.append(f"dead internal link -> {m.group(0)}")
    prose_links = re.findall(r'<a href="/(?:es/)?articles/[^"]+"[^>]*>(.*?)</a>', body, re.S)
    weak = [re.sub(r"<[^>]+>", "", x).strip() for x in prose_links
            if re.sub(r"<[^>]+>", "", x).strip().lower() in
            ("click here", "aquí", "here", "read more", "leer más", "this guide", "esta guía")]
    if weak: warn.append(f"weak anchor text: {weak}")
    if re.search(r'<a[^>]*href="/(?:es/)?articles/[^"]*"[^>]*rel="[^"]*nofollow', s):
        bad.append("nofollow on an internal link")

    return slug, bad, warn


def main():
    if "--all" in sys.argv:
        files = sorted(glob.glob(str(ROOT / "public/articles/*.html")) +
                       glob.glob(str(ROOT / "public/es/articles/*.html")))
    elif "--page" in sys.argv:
        want = sys.argv[sys.argv.index("--page") + 1]
        files = [f for f in glob.glob(str(ROOT / "public/**/articles/*.html"), recursive=True)
                 if pathlib.Path(f).stem == want]
    else:
        files = [str(ROOT / p) for p in BATCH if not p.startswith("_")]

    nb = nw = 0
    for f in files:
        slug, bad, warn = audit(f)
        nb += len(bad); nw += len(warn)
        if bad or warn:
            print(f"\n{slug}")
            for x in bad:  print(f"   FAIL  {x}")
            for x in warn: print(f"   warn  {x}")
    print(f"\n{len(files)} pages · {nb} failures · {nw} warnings")
    return 1 if nb else 0


if __name__ == "__main__":
    sys.exit(main())
