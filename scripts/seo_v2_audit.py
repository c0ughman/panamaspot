#!/usr/bin/env python3
"""
seo_v2_audit.py - technical SEO audit of the V2 guide pages (the <header class="hero"> template).

Runs ~90 automated checks per page from many angles: indexability, head tags, hreflang,
structured data, heading outline, content, images, links, interlinking from the rest of
the site, duplication and cannibalisation, performance signals, the sitemap, and the live
site (status codes, URL variants, headers). Standard library only.

    python3 scripts/seo_v2_audit.py                # audit + live checks, writes the report
    python3 scripts/seo_v2_audit.py --offline      # skip network checks
    python3 scripts/seo_v2_audit.py --page <slug>  # print one page's results

Writes reports/seo-v2-audit.html and reports/seo-v2-audit.json.
"""
import re, sys, json, html, pathlib, collections, subprocess, struct, statistics, datetime
import urllib.request, urllib.error, urllib.parse, concurrent.futures
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
SITE = "https://panamaspot.com"
LAUNCH_COMMIT = "cc96591"
OFFLINE = "--offline" in sys.argv
UA = "PanamaSpot-SEO-audit/1.0"

# ───────────────────────────── tiny DOM ─────────────────────────────
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.children, self.parent, self.text = tag, dict(attrs or {}), [], parent, None

    def cls(self):
        return self.attrs.get("class", "") or ""

    def has_class(self, c):
        return c in self.cls().split()

    def iter(self, tag=None):
        for ch in self.children:
            if ch.tag == "#text":
                continue
            if tag is None or ch.tag == tag:
                yield ch
            yield from ch.iter(tag)

    def find(self, tag=None, cls=None, id=None):
        for n in self.iter(tag):
            if (cls is None or n.has_class(cls)) and (id is None or n.attrs.get("id") == id):
                return n
        return None

    def findall(self, tag=None, cls=None):
        return [n for n in self.iter(tag) if cls is None or n.has_class(cls)]

    def get_text(self, skip=("script", "style", "svg", "noscript")):
        out = []

        def walk(n):
            for ch in n.children:
                if ch.tag == "#text":
                    out.append(ch.text)
                elif ch.tag not in skip:
                    walk(ch)
        walk(self)
        return re.sub(r"\s+", " ", html.unescape("".join(out))).strip()

    def ancestors(self):
        p = self.parent
        while p is not None:
            yield p
            p = p.parent

    def inside(self, tag=None, cls=None):
        return any((tag is None or a.tag == tag) and (cls is None or a.has_class(cls)) for a in self.ancestors())


class Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, d):
        t = Node("#text", parent=self.cur)
        t.text = d
        self.cur.children.append(t)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")


def parse(s):
    b = Builder()
    b.feed(s)
    return b.root


# ───────────────────────────── helpers ─────────────────────────────
def url_for(path):
    rel = path.relative_to(PUB).as_posix()
    return SITE + "/" + rel[:-5]


def local_for_url(u):
    """Map a panamaspot URL or root path to a file under public/ (page or asset)."""
    p = urllib.parse.urlparse(u)
    if p.netloc and p.netloc not in ("panamaspot.com", "www.panamaspot.com"):
        return None
    path = urllib.parse.unquote(p.path)
    if path in ("", "/"):
        return ROOT / "src/app/page.tsx"
    if path in ("/es", "/es/"):
        return ROOT / "src/app/es/page.tsx"
    f = PUB / path.lstrip("/")
    if f.is_file():
        return f
    if (PUB / (path.lstrip("/") + ".html")).is_file():
        return PUB / (path.lstrip("/") + ".html")
    return None


def img_dims(f):
    try:
        b = f.read_bytes()[:64 * 1024]
    except OSError:
        return None
    try:
        if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
            ch = b[12:16]
            if ch == b"VP8 ":
                w, h = struct.unpack("<HH", b[26:30]); return w & 0x3FFF, h & 0x3FFF
            if ch == b"VP8L":
                v = struct.unpack("<I", b[21:25])[0]; return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
            if ch == b"VP8X":
                return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
        if b[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", b[16:24])
        if b[:2] == b"\xff\xd8":
            i = 2
            while i < len(b) - 9:
                if b[i] != 0xFF: i += 1; continue
                m = b[i + 1]
                if m in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", b[i + 5:i + 9]); return w, h
                i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    except Exception:
        return None
    return None


# Rough Arial-at-20px widths, the font Google uses for desktop titles (~600px cut-off).
def px_width(s):
    w = 0
    for c in s:
        if c in "il.,:;'|!I j": w += 5.5
        elif c in "ft()[]r-/\"": w += 6.7
        elif c in "mwMW": w += 16.5
        elif c.isupper(): w += 13.2
        elif c.isdigit(): w += 11.1
        elif c == " ": w += 5.6
        else: w += 11.1
    return w


STOP = set("""a an the and or of to in on for with from by at is are be how what where when which who why your you it its
this that as vs y o de del la las el los en con para por que como cual cuales un una unos unas al es son su sus
2026 guide guia guía complete completa panama panamá""".split())


def toks(s):
    s = html.unescape(s).lower()
    s = re.sub(r"[^\wáéíóúñü]+", " ", s)
    return [t for t in s.split() if t not in STOP and len(t) > 1]


def strip_acc(s):
    return s.translate(str.maketrans("áéíóúñüÁÉÍÓÚÑÜ", "aeiounuAEIOUNU"))


EN_SW = set("the and of to is in that it for you with on are this be at as your from have not or which".split())
# no el/la/de/del/los/las/y: they live inside place names (Bocas del Toro, El Valle, Playa Venao y ...)
ES_SW = set("que en se por un para con una su al lo como más pero sus le ya este es son hay muy desde".split())


def lang_guess(text):
    w = re.findall(r"[a-záéíóúñ]+", text.lower())
    if len(w) < 6:
        return None
    en = sum(x in EN_SW for x in w); es = sum(x in ES_SW for x in w)
    if abs(en - es) < 2: return None
    return "en" if en > es else "es"


def shingles(text, k=6):
    w = re.findall(r"\w+", text.lower())
    return {" ".join(w[i:i + k]) for i in range(0, max(0, len(w) - k + 1))}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def is_iso(d):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?([+-]\d{2}:?\d{2}|Z)?)?$", d or ""))


# ───────────────────────────── site index ─────────────────────────────
def all_pages():
    return sorted(list((PUB / "articles").glob("*.html")) + list((PUB / "es/articles").glob("*.html")))


class Page:
    def __init__(self, path):
        self.path = path
        self.src = path.read_text(encoding="utf-8")
        self.url = url_for(path)
        self.rel = path.relative_to(PUB).as_posix()
        self.lang_dir = "es" if self.rel.startswith("es/") else "en"
        self.v2 = '<header class="hero">' in self.src
        self.dom = parse(self.src)
        self.head = self.dom.find("head") or self.dom
        self.body = self.dom.find("body") or self.dom
        t = self.dom.find("title")
        self.title = t.get_text() if t else ""
        self.desc = self.meta("description")
        h1 = self.dom.find("h1")
        self.h1 = h1.get_text() if h1 else ""
        c = [l for l in self.head.iter("link") if l.attrs.get("rel") == "canonical"]
        self.canonical = c[0].attrs.get("href", "") if c else ""
        self.hreflang = {l.attrs["hreflang"]: l.attrs.get("href", "") for l in self.head.iter("link")
                         if l.attrs.get("rel") == "alternate" and l.attrs.get("hreflang")}
        self.article = self.dom.find("article") or self.dom.find(cls="prose") or self.body
        self.ids = collections.Counter(n.attrs["id"] for n in self.dom.iter() if n.attrs.get("id"))
        self.text = self.article.get_text()
        self.words = len(re.findall(r"\w+", self.text))

    def meta(self, name, attr="name"):
        for m in self.head.iter("meta"):
            if m.attrs.get(attr) == name:
                return html.unescape(m.attrs.get("content", ""))
        return ""

    def jsonld(self):
        out = []
        for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', self.src, re.S):
            try:
                d = json.loads(m.group(1))
            except json.JSONDecodeError as e:
                out.append({"__invalid__": str(e)}); continue
            if isinstance(d, dict) and "@graph" in d:
                out.extend(d["@graph"])
            elif isinstance(d, list):
                out.extend(d)
            else:
                out.append(d)
        return out


def link_zone(a):
    """Where a link sits: body text, nav, footer, rail, related, toc, crumbs, other."""
    for n in a.ancestors():
        c = n.cls().split()
        if n.tag == "footer" or "foot" in c: return "footer"
        if n.tag == "header" or "hero" in c or "home-header" in c: return "header"
        if "crumbs" in c or "breadcrumb" in c: return "crumbs"
        if "toc" in c or "tocl" in c: return "toc/read-next"
        if "refs-box" in c or "srcs" in c or "src-list" in c: return "sources"
        if "rail" in c or "evb-rail" in c: return "rail"
        if "band" in c or "art-section" in c or "related" in " ".join(c) or "bx" in c: return "related"
        if n.tag in ("p", "li", "td", "dd", "blockquote", "figcaption") and (n.inside("article") or n.inside(cls="prose")):
            return "body"
        if n.tag == "article" or "prose" in c: return "body-other"
    return "other"


# ───────────────────────────── checks ─────────────────────────────
class R:
    def __init__(self):
        self.items = []

    def add(self, cat, cid, status, msg="", detail=""):
        self.items.append({"cat": cat, "id": cid, "status": status, "msg": msg, "detail": detail})

    def ok(self, cat, cid, cond, msg_fail, sev="fail", detail=""):
        self.add(cat, cid, "pass" if cond else sev, "" if cond else msg_fail, detail)


EN_UI = ["On this page", "Read next", "Need to know", "At a glance", "Image credits", "min read", "Prices as of",
         "More guides", "Every guide", "Search guides", "Before you go", "Sources", "In pictures", "Where to next"]
ES_UI = ["En esta página", "Leer después", "Lo que debes saber", "De un vistazo", "Créditos de las imágenes", "min de lectura",
         "Fuentes", "Antes de ir"]
GENERIC_ANCHORS = {"here", "click here", "read more", "more", "this", "link", "aquí", "aqui", "clic aquí", "leer más", "ver más", "this guide", "esta guía"}
YMYL = ("stem-cell", "healthcare", "residency", "retiring", "buying-property", "visa")


def audit_page(p, site, ctx):
    r = R()
    s, head = p.src, p.head
    exp_url = p.url
    G = p.jsonld()
    by = collections.defaultdict(list)
    for d in G:
        if "__invalid__" in d:
            by["__invalid__"].append(d)
        else:
            t = d.get("@type"); t = t[0] if isinstance(t, list) else t
            by[t].append(d)

    # ── 1. Indexability & URL ──
    C = "Indexability & URL"
    robots = p.meta("robots")
    r.ok(C, "robots-index", "noindex" not in robots and "nofollow" not in robots, f"robots meta = '{robots}'")
    r.ok(C, "robots-large-preview", "max-image-preview:large" in robots, "no max-image-preview:large", "warn")
    cans = [l for l in head.iter("link") if l.attrs.get("rel") == "canonical"]
    r.ok(C, "canonical-single", len(cans) == 1, f"{len(cans)} canonical tags")
    r.ok(C, "canonical-self", p.canonical == exp_url, f"canonical {p.canonical} ≠ {exp_url}")
    r.ok(C, "canonical-https-apex", p.canonical.startswith(SITE + "/"), "canonical not https apex")
    r.ok(C, "canonical-clean", not re.search(r"(\.html|/|\?|#)$", p.canonical) and "?" not in p.canonical, "canonical has .html/slash/query")
    slug = p.path.stem
    r.ok(C, "slug-format", re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug) is not None, f"slug '{slug}' not lowercase-hyphen ascii")
    r.ok(C, "slug-length", len(slug) <= 60, f"slug {len(slug)} chars (>60)", "warn")
    r.ok(C, "slug-no-year", not re.search(r"20\d\d", slug), "year in slug", "warn")
    r.ok(C, "in-sitemap", exp_url in ctx["sitemap"], "not in live sitemap" if ctx["sitemap"] else "sitemap unavailable",
         "fail" if ctx["sitemap"] else "info")
    sm = ctx["sitemap"].get(exp_url)
    pub = p.meta("article:published_time", "property")
    mod = p.meta("article:modified_time", "property")
    if sm:
        lm = sm.get("lastmod", "")[:10]
        r.ok(C, "sitemap-lastmod", lm and mod and lm >= mod[:10], f"sitemap lastmod {lm or '—'} older than page modified {mod or '—'}", "warn")
        sm_alt = sm.get("alternates", {})
        r.ok(C, "sitemap-hreflang-match", sm_alt == p.hreflang if sm_alt else len(p.hreflang) <= 2,
             f"sitemap alternates {sorted(sm_alt.items())} ≠ page {sorted(p.hreflang.items())}", "warn")
        r.ok(C, "sitemap-images", len(sm.get("images", [])) > 0, "no <image:image> entries in sitemap", "warn")
    redirected = ctx["redirect_sources"]
    r.ok(C, "not-redirect-source", "/" + p.rel[:-5] not in redirected, "URL is also a _redirects source")

    # ── 2. Head tags ──
    C = "Head tags"
    r.ok(C, "title-present", bool(p.title), "no <title>")
    tl, tpx = len(p.title), px_width(p.title)
    r.ok(C, "title-length", 30 <= tl <= 65, f"title {tl} chars", "warn")
    r.ok(C, "title-pixels", tpx <= 600, f"title ≈{int(tpx)}px, likely truncated in Google (≈600px)", "warn")
    r.ok(C, "title-unique", ctx["titles"][p.title.lower()] == 1, "title duplicated elsewhere on the site")
    r.ok(C, "title-no-brand-dup", p.title.lower().count("panama spot") + p.title.lower().count("panamaspot") <= 1, "brand repeated in title", "warn")
    dl = len(p.desc)
    r.ok(C, "desc-present", bool(p.desc), "no meta description")
    r.ok(C, "desc-length", 110 <= dl <= 160, f"description {dl} chars", "warn")
    r.ok(C, "desc-unique", ctx["descs"][p.desc.lower()] == 1, "description duplicated elsewhere")
    lang_attr = (p.dom.find("html").attrs.get("lang", "") if p.dom.find("html") else "")
    r.ok(C, "html-lang", lang_attr.split("-")[0] == p.lang_dir, f"<html lang='{lang_attr}'> in /{p.lang_dir} folder")
    r.ok(C, "desc-language", lang_guess(p.desc) in (None, p.lang_dir), f"description reads as {lang_guess(p.desc)}")
    r.ok(C, "charset-viewport", 'charset="utf-8"' in s[:400].lower() and p.meta("viewport") != "" or 'name="viewport"' in s[:600], "missing charset/viewport")
    og = {k: p.meta(k, "property") for k in ("og:title", "og:description", "og:url", "og:image", "og:type", "og:locale", "og:site_name", "og:image:width", "og:image:height", "og:image:alt")}
    missing = [k for k in ("og:title", "og:description", "og:url", "og:image", "og:type") if not og[k]]
    r.ok(C, "og-core", not missing, f"missing {', '.join(missing)}")
    r.ok(C, "og-url-canonical", og["og:url"] == p.canonical, f"og:url {og['og:url']} ≠ canonical")
    r.ok(C, "og-type-article", og["og:type"] == "article", f"og:type '{og['og:type']}'", "warn")
    want_loc = "es_" if p.lang_dir == "es" else "en_"
    r.ok(C, "og-locale", og["og:locale"].startswith(want_loc), f"og:locale '{og['og:locale'] or '—'}'", "warn")
    r.ok(C, "og-site-name", bool(og["og:site_name"]), "no og:site_name", "warn")
    r.ok(C, "og-image-dims", bool(og["og:image:width"] and og["og:image:height"]), "no og:image:width/height", "warn")
    r.ok(C, "og-image-alt", bool(og["og:image:alt"]), "no og:image:alt", "warn")
    ogf = local_for_url(og["og:image"]) if og["og:image"] else None
    r.ok(C, "og-image-exists", ogf is not None or not og["og:image"].startswith(SITE), f"og:image file missing: {og['og:image']}")
    if ogf:
        d = img_dims(ogf)
        r.ok(C, "og-image-size", d and d[0] >= 1200 and 1.5 <= d[0] / d[1] <= 2.1, f"og:image {d} (want ≥1200 wide, ~1.91:1)", "warn")
    tw = [k for k in ("twitter:card", "twitter:title", "twitter:description", "twitter:image") if not p.meta(k)]
    r.ok(C, "twitter-tags", not tw, f"missing {', '.join(tw)}", "warn")
    r.ok(C, "article-dates", is_iso(pub) and is_iso(mod), f"published '{pub}' modified '{mod}'")
    r.ok(C, "dates-order", not (pub and mod) or mod >= pub, "modified before published")
    r.ok(C, "favicon", any(l.attrs.get("rel") in ("icon", "shortcut icon") for l in head.iter("link")), "no favicon link", "warn")
    r.ok(C, "no-meta-keywords", not p.meta("keywords"), "meta keywords present (ignored, leaks targets)", "warn")

    # ── 3. Hreflang ──
    C = "Hreflang"
    hl = p.hreflang
    r.ok(C, "hreflang-self", hl.get(p.lang_dir) == p.url, f"no self hreflang '{p.lang_dir}' → {hl.get(p.lang_dir)}")
    r.ok(C, "hreflang-x-default", "x-default" in hl, "no x-default")
    bad_codes = [k for k in hl if k not in ("en", "es", "x-default") and not re.fullmatch(r"[a-z]{2}(-[A-Z]{2})?", k)]
    r.ok(C, "hreflang-codes", not bad_codes, f"invalid codes {bad_codes}")
    other = "en" if p.lang_dir == "es" else "es"
    if other in hl:
        twin_url = hl[other]
        twin = site.get(twin_url)
        r.ok(C, "hreflang-target-exists", twin is not None, f"alternate {twin_url} not found")
        if twin:
            r.ok(C, "hreflang-reciprocal", twin.hreflang.get(p.lang_dir) == p.url, f"twin {twin_url} does not link back")
            r.ok(C, "hreflang-target-canonical", twin.canonical == twin_url, "alternate is not the twin's canonical")
            r.ok(C, "hreflang-target-lang", twin.lang_dir == other, "alternate is in the wrong language folder")
        xd = hl.get("x-default")
        r.ok(C, "x-default-en", xd == (p.url if p.lang_dir == "en" else twin_url), f"x-default → {xd}", "warn")
        toggle = [a for a in p.dom.iter("a") if a.attrs.get("hreflang") == other and a.inside(cls="lang")]
        tgt = toggle[0].attrs.get("href", "") if toggle else ""
        r.ok(C, "lang-toggle-twin", tgt and (SITE + tgt if tgt.startswith("/") else tgt) == twin_url, f"language switch goes to '{tgt}', not the twin", "warn")
    else:
        r.add(C, "hreflang-single-language", "info", "no translation declared")
        twin_guess = ctx["twin_candidates"].get(p.url)
        if twin_guess:
            r.add(C, "hreflang-missing-twin", "warn", f"possible untagged twin: {twin_guess}")

    # ── 4. Structured data ──
    C = "Structured data"
    r.ok(C, "jsonld-valid", not by.get("__invalid__"), f"invalid JSON-LD: {by.get('__invalid__')}")
    for t in ("Organization", "WebSite", "WebPage", "Article", "BreadcrumbList"):
        r.ok(C, f"has-{t}", t in by, f"no {t}")
    r.ok(C, "single-article", len(by.get("Article", [])) + len(by.get("BlogPosting", [])) <= 1, "more than one Article node", "warn")
    ids = {d.get("@id") for d in G if isinstance(d, dict) and d.get("@id")}
    refs = set()

    def collect(o):
        if isinstance(o, dict):
            if set(o.keys()) == {"@id"}: refs.add(o["@id"])
            for v in o.values(): collect(v)
        elif isinstance(o, list):
            for v in o: collect(v)
    collect(G)
    dangling = sorted(x for x in refs - ids if x.startswith(SITE))
    r.ok(C, "id-refs-resolve", not dangling, f"@id references with no node: {dangling[:3]}")
    art = (by.get("Article") or by.get("BlogPosting") or [{}])[0]
    if art:
        hd = art.get("headline", "")
        r.ok(C, "article-headline", 0 < len(hd) <= 110, f"headline {len(hd)} chars")
        r.ok(C, "article-headline-h1", toks(hd) and len(set(toks(hd)) & set(toks(p.h1))) / max(1, len(set(toks(hd)))) >= .6,
             f"headline '{hd}' ≠ H1 '{p.h1}'", "warn")
        im = art.get("image")
        ims = im if isinstance(im, list) else [im] if im else []
        ims = [i.get("url") if isinstance(i, dict) else i.get("@id") if isinstance(i, dict) else i for i in ims]
        r.ok(C, "article-image", bool(ims), "Article has no image")
        r.ok(C, "article-dates", is_iso(art.get("datePublished", "")) and is_iso(art.get("dateModified", "")), "Article dates missing/not ISO")
        r.ok(C, "article-dates-match-meta", art.get("datePublished", "")[:10] == pub[:10] and art.get("dateModified", "")[:10] == mod[:10],
             f"schema {art.get('datePublished')}/{art.get('dateModified')} vs meta {pub}/{mod}", "warn")
        au = art.get("author") or {}
        au = au[0] if isinstance(au, list) else au
        r.ok(C, "article-author", bool(au.get("name") or au.get("@id")), "no author")
        is_ymyl = any(k in slug for k in YMYL)
        r.ok(C, "author-person", au.get("@type") == "Person" or not is_ymyl,
             f"YMYL topic with author @type {au.get('@type')} '{au.get('name')}'", "warn")
        r.ok(C, "article-publisher", bool(art.get("publisher")), "no publisher", "warn")
        meop = art.get("mainEntityOfPage")
        meop = meop.get("@id") if isinstance(meop, dict) else meop
        r.ok(C, "article-mainEntity", meop in (p.canonical, p.canonical + "#webpage") or (meop or "").startswith(p.canonical), f"mainEntityOfPage {meop}", "warn")
        r.ok(C, "article-lang", art.get("inLanguage", "")[:2] == p.lang_dir, f"inLanguage {art.get('inLanguage')}")
    wp = (by.get("WebPage") or [{}])[0]
    if wp:
        r.ok(C, "webpage-url", wp.get("url") == p.canonical, f"WebPage url {wp.get('url')}")
        r.ok(C, "webpage-lang", wp.get("inLanguage", "")[:2] == p.lang_dir, f"WebPage inLanguage {wp.get('inLanguage')}")
    bc = (by.get("BreadcrumbList") or [{}])[0]
    if bc:
        items = bc.get("itemListElement", [])
        pos_ok = [it.get("position") for it in items] == list(range(1, len(items) + 1))
        r.ok(C, "breadcrumb-positions", pos_ok, "positions not 1..n")
        broken = []
        for it in items[:-1]:
            u = it.get("item")
            u = u.get("@id") if isinstance(u, dict) else u
            if not u or local_for_url(u) is None: broken.append(u)
        r.ok(C, "breadcrumb-items-resolve", not broken, f"breadcrumb items not found: {broken}")
        vis = p.dom.find(cls="crumbs")
        vis_names = [x.get_text() for x in vis.iter() if x.tag in ("a", "b")] if vis else []
        sch_names = [it.get("name", "") for it in items]
        norm = lambda x: strip_acc(x.lower()).rstrip("…. ")
        same = len(vis_names) == len(sch_names) and all(norm(b).startswith(norm(a)) for a, b in zip(vis_names, sch_names))
        r.ok(C, "breadcrumb-matches-visible", same,
             f"visible {vis_names} vs schema {sch_names}", "warn")
    faq = (by.get("FAQPage") or [{}])[0]
    faqsec = p.dom.find("section", id="faq")
    vis_q = [h.get_text() for h in faqsec.iter("h3")] if faqsec else []
    if faq:
        qs = [q.get("name", "") for q in faq.get("mainEntity", [])]
        ans = [((q.get("acceptedAnswer") or {}).get("text") or "") for q in faq.get("mainEntity", [])]
        r.ok(C, "faq-matches-visible", [x.strip() for x in qs] == [x.strip() for x in vis_q], f"{len(qs)} schema Qs vs {len(vis_q)} visible Qs")
        r.ok(C, "faq-answers", all(len(a) > 40 for a in ans), "empty/short FAQ answers")
        if faqsec:
            vis_a = " ".join(x.get_text() for x in faqsec.iter("p"))
            nz = lambda x: re.sub(r"\s+", "", strip_acc(re.sub(r"<[^>]+>", "", html.unescape(x)).lower()))
            miss = [a[:50] for a in ans if nz(a)[:60] not in nz(vis_a)]
            r.ok(C, "faq-answers-visible", not miss, f"{len(miss)} answers not visible on page", "warn")
        junk = [a[:60] for a in ans if re.search(r"\s[,.;:)]", a)]
        r.ok(C, "faq-text-clean", not junk, f"{len(junk)} schema answers with stray spaces before punctuation (citation marks stripped)", "warn", " | ".join(junk[:2]))
    elif vis_q:
        r.add(C, "faq-schema", "warn", "visible FAQ without FAQPage schema")
    io = by.get("ImageObject", [])
    r.ok(C, "imageobject-license", not io or all(i.get("license") or i.get("creditText") or i.get("copyrightNotice") for i in io),
         "ImageObject without license/creditText", "warn")
    places = sum(len(by.get(t, [])) for t in ("TouristAttraction", "TouristDestination", "Place", "LocalBusiness", "Restaurant", "LodgingBusiness", "Hotel", "Park"))
    r.add(C, "place-entities", "pass" if places else "info", "" if places else "no Place/TouristAttraction entities (rich context for local topics)")

    # ── 5. Heading outline ──
    C = "Headings & outline"
    h1s = p.dom.findall("h1")
    r.ok(C, "one-h1", len(h1s) == 1, f"{len(h1s)} H1 tags")
    r.ok(C, "h1-length", 10 <= len(p.h1) <= 70, f"H1 {len(p.h1)} chars", "warn")
    r.ok(C, "h1-not-title-copy", p.h1.strip().lower() != p.title.strip().lower(), "H1 identical to title (missed second phrasing)", "warn")
    heads = [(int(n.tag[1]), n.get_text(), n) for n in p.dom.iter() if re.fullmatch(r"h[1-6]", n.tag)]
    art_heads = [(l, t) for l, t, n in heads if n.inside("article")]
    skips, prev = [], 1
    for l, t in art_heads:
        if l > prev + 1: skips.append(f"H{prev}→H{l} '{t[:40]}'")
        prev = l
    r.ok(C, "no-level-skips", not skips, "; ".join(skips[:3]), "warn")
    r.ok(C, "no-empty-headings", all(t for _, t, _ in heads), "empty heading tag")
    h2s = [t for l, t in art_heads if l == 2]
    r.ok(C, "h2-count", len(h2s) >= 5, f"only {len(h2s)} H2s in article", "warn")
    dups = [t for t, c in collections.Counter(t.lower() for l, t in art_heads).items() if c > 1]
    r.ok(C, "no-duplicate-headings", not dups, f"duplicates: {dups[:3]}", "warn")
    outside = [f"H{l} {t[:30]}" for l, t, n in heads if l <= 3 and not n.inside("article") and l != 1]
    r.add(C, "template-headings", "pass" if len(outside) <= 6 else "warn",
          "" if len(outside) <= 6 else f"{len(outside)} H2/H3 outside the article (template headings dilute the outline)", "; ".join(outside[:12]))
    long_h = [t for l, t in art_heads if l == 2 and len(t) > 75]
    r.ok(C, "h2-length", not long_h, f"{len(long_h)} H2s over 75 chars", "warn")
    secs = p.article.findall("section", "sec")
    no_id = [s_.attrs.get("id") for s_ in secs if not s_.attrs.get("id")]
    r.ok(C, "sections-have-ids", not no_id, f"{len(no_id)} sections without id")
    toc = [a.attrs.get("href", "") for a in p.dom.iter("a") if a.inside(cls="toc")]
    bad_toc = [h for h in toc if h.startswith("#") and p.ids.get(h[1:], 0) == 0]
    r.ok(C, "toc-anchors-resolve", toc and not bad_toc, f"TOC anchors missing: {bad_toc[:3]}" if toc else "no TOC")
    dup_ids = [i for i, c in p.ids.items() if c > 1]
    r.ok(C, "unique-ids", not dup_ids, f"duplicate ids: {dup_ids[:5]}")
    kw = toks(slug.replace("-", " "))[:3]
    h2_text = strip_acc(" ".join(h2s).lower())
    r.ok(C, "keyword-in-h2", any(strip_acc(k) in h2_text for k in kw), f"none of {kw} in any H2", "warn")

    # ── 6. Content ──
    C = "Content"
    r.ok(C, "word-count", p.words >= 1200, f"{p.words} words", "warn")
    lead = p.article.find("p")
    first100 = strip_acc(" ".join(re.findall(r"\w+", p.text)[:120]).lower())
    r.ok(C, "keyword-early", sum(strip_acc(k) in first100 for k in kw) >= min(2, len(kw)), f"slug terms {kw} not in first 120 words", "warn")
    tkw = strip_acc(p.title.lower())
    r.ok(C, "keyword-in-title", sum(strip_acc(k) in tkw for k in kw) >= min(2, len(kw)), f"slug terms {kw} weak in title", "warn")
    dkw = strip_acc(p.desc.lower())
    r.ok(C, "keyword-in-desc", any(strip_acc(k) in dkw for k in kw), f"slug terms {kw} not in description", "warn")
    long_p = [len(re.findall(r"\w+", x.get_text())) for x in p.article.findall("p")]
    lp = [w for w in long_p if w > 140]
    r.ok(C, "paragraph-length", not lp, f"{len(lp)} paragraphs over 140 words", "warn")
    bl = p.dom.find(cls="byline")
    mm = re.search(r"(\d+)\s*min", bl.get_text() if bl else "")
    if mm:
        est = round(p.words / 230)
        r.ok(C, "read-time-claim", abs(int(mm.group(1)) - est) <= max(3, est * .3), f"byline says {mm.group(1)} min, text ≈{est} min", "warn")
    vis = p.body.get_text()
    ph = re.findall(r"lorem ipsum|\bTODO\b|\bTBD\b|\{\{|\}\}|\bundefined\b|\bNaN\b|\[object|\bXXX+\b|\$X\b", vis)
    r.ok(C, "no-placeholders", not ph, f"placeholder text: {sorted(set(ph))[:4]}")
    ui_bad = [u for u in (EN_UI if p.lang_dir == "es" else ES_UI) if re.search(r"\b" + re.escape(u) + r"\b", vis)]
    r.ok(C, "ui-language", not ui_bad, f"other-language UI strings: {ui_bad}")
    lg = lang_guess(p.text)
    r.ok(C, "body-language", lg == p.lang_dir, f"article text reads as {lg}")
    paras = [x.get_text() for x in p.article.findall("p") if len(x.get_text()) > 80]
    wrong = [x[:60] for x in paras if lang_guess(x) not in (None, p.lang_dir)]
    r.ok(C, "mixed-language-paragraphs", len(wrong) == 0, f"{len(wrong)} paragraphs in the other language", "warn", " | ".join(wrong[:3]))
    cites = [a.attrs.get("href", "") for a in p.dom.iter("a") if a.inside(tag="sup")]
    bad_c = [h for h in cites if h.startswith("#") and p.ids.get(h[1:], 0) == 0]
    r.ok(C, "citations-resolve", not bad_c, f"{len(bad_c)} citation links to missing ids")
    srcs = p.dom.find(id="sources")
    nsrc = len([li for li in srcs.iter("li")]) if srcs else 0
    r.ok(C, "has-sources", nsrc >= 3, f"{nsrc} sources listed", "warn")
    cited = {h[1:] for h in cites}
    src_ids = [li.attrs.get("id") for li in (srcs.iter("li") if srcs else []) if li.attrs.get("id", "").startswith("s")]
    uncited = [i for i in src_ids if i not in cited and not i.startswith("img")]
    r.ok(C, "sources-cited", len(uncited) <= 2, f"{len(uncited)} listed sources never cited in the text", "warn")
    yrs = re.findall(r"\b(20[12]\d)\b", p.title + " " + p.h1)
    r.ok(C, "no-stale-year", all(y >= "2026" for y in yrs), f"old year in title/H1: {yrs}", "warn")
    r.add(C, "near-duplicate", "pass" if ctx["dup"].get(p.url, (0, ""))[0] < .12 else "warn",
          "" if ctx["dup"].get(p.url, (0, ""))[0] < .12 else f"{ctx['dup'][p.url][0]:.0%} of 6-word phrases shared with {ctx['dup'][p.url][1]}")
    can = ctx["cannibal"].get(p.url)
    r.add(C, "cannibalisation", "pass" if not can else "warn", "" if not can else f"title/H1 overlaps {can[1]} ({can[0]:.0%})")

    # ── 7. Images ──
    C = "Images"
    imgs = list(p.body.iter("img"))
    no_alt = [i for i in imgs if "alt" not in i.attrs]
    r.ok(C, "alt-attribute", not no_alt, f"{len(no_alt)} <img> without alt attribute")
    content = [i for i in imgs if i.inside("article") or i.inside(cls="gal") or i.has_class("hero-img")]
    empty_content = [i.attrs.get("src", "")[-50:] for i in content if not i.attrs.get("alt", "").strip()]
    r.ok(C, "alt-content-images", not empty_content, f"{len(empty_content)} content images with empty alt", "fail", "; ".join(empty_content[:3]))
    deco = [i for i in imgs if i not in content and not i.attrs.get("alt", "").strip()]
    unnamed_links = []
    for i in deco:
        a = next((x for x in i.ancestors() if x.tag == "a"), None)
        if a is not None and not a.get_text() and not a.attrs.get("aria-label"):
            unnamed_links.append(a.attrs.get("href"))
    r.ok(C, "linked-images-named", not unnamed_links, f"{len(unnamed_links)} image links with no accessible text")
    alts = [i.attrs.get("alt", "") for i in imgs if i.attrs.get("alt")]
    longa = [a for a in alts if len(a) > 125]
    r.ok(C, "alt-length", not longa, f"{len(longa)} alts over 125 chars", "warn")
    fname = [a for a in alts if re.search(r"\.(jpe?g|png|webp)|^img[_-]?\d|^dsc|^\d+$|_", a, re.I)]
    r.ok(C, "alt-not-filename", not fname, f"filename-like alts: {fname[:2]}", "warn")
    dupa = [a for a, c in collections.Counter(alts).items() if c > 1]
    srcs_by_alt = collections.defaultdict(set)
    for i in imgs:
        if i.attrs.get("alt"): srcs_by_alt[i.attrs["alt"]].add(i.attrs.get("src", ""))
    dupa = [a for a in dupa if len(srcs_by_alt[a]) > 1]
    r.ok(C, "alt-unique", not dupa, f"{len(dupa)} alts reused on different images", "warn")
    wrong_lang = [a[:50] for a in alts if len(a) > 40 and lang_guess(a) not in (None, p.lang_dir)]
    r.ok(C, "alt-language", len(wrong_lang) <= 1, f"{len(wrong_lang)} alts in the other language", "warn", " | ".join(wrong_lang[:3]))
    reserved = lambda i: i.has_class("hero-img") or any(i.inside(cls=c) for c in ("fig", "gal", "stamp", "bt", "fc", "ev-ph"))
    nodim = [i.attrs.get("src", "")[-40:] for i in imgs if not (i.attrs.get("width") and i.attrs.get("height")) and not reserved(i)]
    r.ok(C, "space-reserved", not nodim, f"{len(nodim)} images with no width/height and no fixed CSS frame (layout shift)", "warn", "; ".join(nodim[:3]))
    r.ok(C, "width-height-attrs", sum(1 for i in content if i.attrs.get("width")) >= .5 * max(1, len(content)),
         "content images rely on CSS only (add width/height so browsers know the ratio before CSS loads)", "info")
    exts = collections.Counter()
    hosts = collections.Counter()
    missing, heavy, small, local_bytes = [], [], [], 0
    for i in imgs:
        src = i.attrs.get("src", "")
        u = urllib.parse.urlparse(src if "://" in src else SITE + src)
        hosts[u.netloc] += 1
        ext = pathlib.PurePosixPath(u.path).suffix.lower().lstrip(".") or "?"
        if "pexels" in u.netloc: ext = "jpeg(pexels)"
        exts[ext] += 1
        if u.netloc in ("panamaspot.com", ""):
            f = local_for_url(src if "://" in src else SITE + src)
            if f is None:
                missing.append(src)
            else:
                sz = f.stat().st_size; local_bytes += sz
                if sz > 350_000: heavy.append(f"{f.name} {sz // 1024}KB")
                d = img_dims(f)
                if d and (i.inside("article") or i.inside(cls="gal")) and d[0] < 800: small.append(f"{f.name} {d[0]}px")
    r.ok(C, "local-files-exist", not missing, f"{len(missing)} image files missing", "fail", "; ".join(missing[:3]))
    r.ok(C, "modern-format", sum(v for k, v in exts.items() if k in ("webp", "avif", "svg")) >= .8 * max(1, len(imgs)),
         f"formats {dict(exts)}", "warn")
    ext_hosts = {h: c for h, c in hosts.items() if h not in ("panamaspot.com", "")}
    r.ok(C, "self-hosted", not ext_hosts, f"hotlinked: {ext_hosts}", "warn")
    r.ok(C, "file-weight", not heavy, f"{len(heavy)} images over 350KB", "warn", "; ".join(heavy[:3]))
    r.ok(C, "resolution", not small, f"{len(small)} content images under 800px wide", "warn", "; ".join(small[:3]))
    hero = p.dom.find("img", cls="hero-img")
    r.ok(C, "hero-img-tag", hero is not None, "hero is not an <img> (not indexable)")
    if hero:
        r.ok(C, "hero-priority", hero.attrs.get("fetchpriority") == "high" and hero.attrs.get("loading") != "lazy", "hero not eager/high priority")
        r.ok(C, "hero-srcset", bool(hero.attrs.get("srcset")), "hero without srcset", "warn")
        pre = [l for l in head.iter("link") if l.attrs.get("rel") == "preload" and l.attrs.get("as") == "image"]
        r.ok(C, "hero-preload-matches", pre and pre[0].attrs.get("href") == hero.attrs.get("src"), "preloaded image ≠ hero src (double download)")
        r.ok(C, "hero-alt", len(hero.attrs.get("alt", "")) > 20, "hero alt short/empty")
    below = [i for i in imgs if i is not hero and i.attrs.get("loading") != "lazy"]
    r.ok(C, "lazy-below-fold", len(below) <= 1, f"{len(below)} non-hero images not lazy-loaded", "warn")
    ugly = [pathlib.PurePosixPath(urllib.parse.urlparse(i.attrs.get("src", "")).path).name for i in imgs
            if re.search(r"(^[0-9a-f]{8}-)|(_2C|_28|_29|%2|__)", pathlib.PurePosixPath(urllib.parse.urlparse(i.attrs.get("src", "")).path).name)]
    r.ok(C, "descriptive-filenames", len(ugly) <= 2, f"{len(ugly)} hash/encoded filenames (weak image-search signal)", "warn", "; ".join(ugly[:2]))
    figs = [f for f in p.article.findall("figure")]
    nocap = [f for f in figs if not f.find("figcaption")]
    r.ok(C, "figure-captions", not nocap, f"{len(nocap)} figures without caption", "warn")
    third = sum(1 for i in imgs if re.search(r"wikimedia|pexels|commons|unsplash", i.attrs.get("src", "") + "", re.I) or "_2C" in i.attrs.get("src", ""))
    r.ok(C, "image-credits", not third or p.dom.find(cls="img-refs") is not None or "credit" in vis.lower() or "créditos" in vis.lower(),
         "third-party images without a credits section", "warn")
    p.local_img_bytes = local_bytes

    # ── 8. Links ──
    C = "Links"
    anchors = [a for a in p.body.iter("a") if a.attrs.get("href")]
    broken, to_redirect, generic, blank_noopener, insecure, empty = [], [], [], [], [], []
    body_targets = collections.Counter()
    cross_lang = []
    for a in anchors:
        h = a.attrs["href"]
        txt = a.get_text() or a.attrs.get("aria-label", "")
        if h.startswith(("mailto:", "tel:", "javascript:")): continue
        if h.startswith("#"):
            if h != "#" and p.ids.get(h[1:], 0) == 0: broken.append(h)
            continue
        u = urllib.parse.urlparse(h)
        internal = not u.netloc or u.netloc in ("panamaspot.com", "www.panamaspot.com")
        if internal:
            path = u.path or "/"
            if path not in ("/", "/es") and local_for_url(SITE + path) is None and not path.startswith("/funnels/"):
                broken.append(h)
            if path.startswith("/funnels/") and not (PUB / (path.lstrip("/") + ".html")).exists():
                broken.append(h)
            if path in redirected: to_redirect.append(h)
            if u.netloc: to_redirect.append(h + " (absolute)") if False else None
            zone = link_zone(a)
            if zone == "body":
                body_targets[path] += 1
                if (path.startswith("/es/") and p.lang_dir == "en") or (path.startswith("/articles/") and p.lang_dir == "es"):
                    cross_lang.append(path)
        else:
            if u.scheme == "http": insecure.append(h)
            if a.attrs.get("target") == "_blank" and "noopener" not in a.attrs.get("rel", "") and "noreferrer" not in a.attrs.get("rel", ""):
                blank_noopener.append(h)
        if txt.strip().lower() in GENERIC_ANCHORS: generic.append(txt)
        if not txt.strip() and not a.find("img"): empty.append(h)
    r.ok(C, "no-broken-internal", not broken, f"{len(broken)} broken internal links/anchors", "fail", "; ".join(broken[:4]))
    r.ok(C, "no-links-to-redirects", not to_redirect, f"{len(to_redirect)} links to redirected URLs", "warn", "; ".join(to_redirect[:3]))
    r.ok(C, "no-generic-anchors", not generic, f"generic anchors: {generic[:4]}", "warn")
    r.ok(C, "no-empty-anchors", not empty, f"{len(empty)} links without text", "fail", "; ".join(empty[:3]))
    r.ok(C, "external-noopener", not blank_noopener, f"{len(blank_noopener)} target=_blank without rel=noopener", "warn")
    r.ok(C, "external-https", not insecure, f"{len(insecure)} http:// links", "warn", "; ".join(insecure[:3]))
    nbody = sum(body_targets.values())
    r.ok(C, "body-links-min", nbody >= 5, f"only {nbody} internal links in the article text", "warn")
    r.ok(C, "body-links-max", nbody <= 60, f"{nbody} internal links in the article text", "warn")
    rep = [t for t, c in body_targets.items() if c > 3]
    r.ok(C, "no-repeated-targets", not rep, f"same page linked >3× in text: {rep[:3]}", "warn")
    r.ok(C, "no-cross-language-body-links", not cross_lang, f"{len(cross_lang)} body links into the other language", "warn", "; ".join(cross_lang[:3]))
    self_links = [a for a in anchors if a.attrs["href"] in (p.url, "/" + p.rel[:-5]) and link_zone(a) not in ("header", "footer")]
    r.ok(C, "no-self-links", not self_links, f"{len(self_links)} links to the page itself", "warn")
    inb = ctx["inbound"].get(p.url, collections.Counter())
    r.ok(C, "inbound-body-links", inb["body"] >= 2, f"{inb['body']} in-text links from other guides", "warn" if inb["body"] else "fail")
    r.ok(C, "inbound-sources", len(ctx["inbound_src"].get(p.url, set())) >= 2, f"linked from {len(ctx['inbound_src'].get(p.url, set()))} other guides (any zone)", "warn")
    funnel = [a for a in anchors if a.attrs["href"].startswith("/funnels/")]
    r.add(C, "conversion-path", "pass" if funnel else "info", "" if funnel else "no funnel/CTA link on the page")
    nav = [a.attrs["href"] for a in p.dom.iter("a") if a.inside(cls="links")]
    dupnav = [h for h, c in collections.Counter(nav).items() if c > 1]
    r.ok(C, "nav-unique-targets", not dupnav, f"main nav repeats {dupnav}", "warn")
    fake = p.dom.find(cls="search")
    r.ok(C, "no-dead-ui", not (fake and fake.tag in ("span", "div")), "search box is a non-interactive <span>", "warn")

    # ── 9. Performance signals ──
    C = "Performance"
    kb = len(s.encode()) / 1024
    r.ok(C, "html-size", kb <= 150, f"HTML {kb:.0f}KB", "warn")
    css = sum(len(x) for x in re.findall(r"<style[^>]*>(.*?)</style>", s, re.S)) / 1024
    r.ok(C, "inline-css", css <= 40, f"{css:.0f}KB inline CSS on every page (not cacheable)", "warn")
    blocking = [l.attrs.get("href", "") for l in head.iter("link") if l.attrs.get("rel") == "stylesheet"]
    r.ok(C, "render-blocking-css", len(blocking) <= 1, f"{len(blocking)} external stylesheets", "warn")
    gf = [b for b in blocking if "fonts.googleapis" in b]
    r.ok(C, "third-party-fonts", not gf, "Google Fonts CSS is render-blocking (self-host Hanken like GildaC)", "warn")
    preconnect = [l for l in head.iter("link") if l.attrs.get("rel") == "preconnect"]
    r.ok(C, "preconnect-fonts", not gf or preconnect, "no preconnect for font host", "warn")
    swap = "font-display:swap" in s.replace(" ", "") or "display=swap" in s
    r.ok(C, "font-display-swap", swap, "no font-display: swap")
    scripts = [x for x in p.dom.iter("script") if x.attrs.get("src")]
    r.ok(C, "no-blocking-scripts", all(x.attrs.get("async") is not None or x.attrs.get("defer") is not None or x.attrs.get("type") == "module" for x in scripts),
         "synchronous external script")
    n_img = len(imgs)
    r.ok(C, "image-count", n_img <= 40, f"{n_img} images", "warn")
    r.ok(C, "local-image-bytes", local_bytes <= 2_500_000, f"{local_bytes / 1e6:.1f}MB of self-hosted images", "warn")
    dom_n = sum(1 for _ in p.dom.iter())
    r.ok(C, "dom-size", dom_n <= 1500, f"{dom_n} DOM elements", "warn")
    req_urls = [i.attrs.get("src", "") for i in p.dom.iter() if i.tag in ("img", "script", "iframe", "source")] + \
               [l.attrs.get("href", "") for l in head.iter("link") if l.attrs.get("rel") in ("stylesheet", "preload", "preconnect", "icon")]
    ext_req = len({urllib.parse.urlparse(x).netloc for x in req_urls if x.startswith("http")} - {"panamaspot.com"})
    r.add(C, "third-party-hosts", "pass" if ext_req <= 4 else "warn", "" if ext_req <= 4 else f"{ext_req} third-party hosts referenced")

    # ── 10. Live (network) ──
    live = ctx["live"].get(p.url)
    if live:
        C = "Live site"
        r.ok(C, "live-200", live["status"] == 200, f"status {live['status']}")
        r.ok(C, "live-no-x-robots", "noindex" not in (live.get("x-robots") or ""), f"X-Robots-Tag {live.get('x-robots')}")
        r.ok(C, "live-html", "text/html" in (live.get("ctype") or ""), f"content-type {live.get('ctype')}")
        r.ok(C, "live-deployed", live.get("title") == html.unescape(p.title), f"live title '{live.get('title')}' ≠ repo")
        r.ok(C, "live-canonical", live.get("canonical") == p.canonical, f"live canonical {live.get('canonical')}")
        r.ok(C, "live-ga", live.get("ga"), "no GA4 tag in deployed HTML", "warn")
        for k, lab in (("html", ".html variant"), ("slash", "trailing-slash variant"), ("www", "www host"), ("http", "http://")):
            v = live.get(k)
            if v is None: continue
            st, loc = v
            good = st in (301, 308) and loc and loc.rstrip("/").replace("http://", "https://").endswith(urllib.parse.urlparse(p.url).path) or st == 404
            if k == "html" and st == 200:
                good = False
            r.ok(C, f"variant-{k}", good, f"{lab} → {st} {loc or ''}", "warn")
        r.ok(C, "live-cache-header", bool(live.get("cache")), "no cache-control", "info")
    return r.items


# ───────────────────────────── site-wide context ─────────────────────────────
def fetch(url, method="GET", follow=True, timeout=20):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read() if method == "GET" else b""
            return resp.status, dict(resp.headers), body
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), b""
    except Exception as e:
        return None, {"error": str(e)}, b""


def live_check(p):
    st, hd, body = fetch(p.url)
    hd = {k.lower(): v for k, v in hd.items()}
    b = body.decode("utf-8", "replace")
    t = re.search(r"<title>(.*?)</title>", b, re.S)
    c = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"|<link[^>]*href="([^"]+)"[^>]*rel="canonical"', b)
    out = {"status": st, "ctype": hd.get("content-type"), "x-robots": hd.get("x-robots-tag"), "cache": hd.get("cache-control"),
           "title": html.unescape(t.group(1).strip()) if t else None, "canonical": (c.group(1) or c.group(2)) if c else None,
           "ga": "googletagmanager.com/gtag" in b or "gtag(" in b}
    path = urllib.parse.urlparse(p.url).path
    for k, u in (("html", SITE + path + ".html"), ("slash", SITE + path + "/"), ("www", "https://www.panamaspot.com" + path),
                 ("http", "http://panamaspot.com" + path)):
        s2, h2, _ = fetch(u, "HEAD", follow=False)
        h2 = {kk.lower(): vv for kk, vv in h2.items()}
        out[k] = (s2, h2.get("location"))
    return p.url, out


def load_sitemap():
    st, _, body = fetch(SITE + "/sitemap.xml")
    if st != 200: return {}
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml",
          "i": "http://www.google.com/schemas/sitemap-image/1.1"}
    out = {}
    for u in ET.fromstring(body).findall("s:url", ns):
        loc = u.findtext("s:loc", "", ns).strip()
        out[loc] = {"lastmod": u.findtext("s:lastmod", "", ns), "alternates": {l.get("hreflang"): l.get("href") for l in u.findall("x:link", ns)},
                    "images": [i.findtext("i:loc", "", ns) for i in u.findall("i:image", ns)]}
    return out


def launch_added_links():
    """Links to V2 pages that the launch commit added to older pages: {(file, href)}."""
    try:
        d = subprocess.run(["git", "show", LAUNCH_COMMIT, "--", "public/articles", "public/es/articles"], cwd=ROOT,
                           capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return set()
    added, cur = set(), None
    for line in d.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
        elif line.startswith("+") and cur:
            for h in re.findall(r'href="(/(?:es/)?articles/[^"#]+)"', line):
                added.add((cur, h))
    return added


BASE_COMMIT = "8aa8866"   # last commit before any V2 work (2026-10-22)


def interlink_changes(pages, v2_paths):
    """Every link to a V2 page that older pages gained since BASE_COMMIT, classified by how it was placed."""
    rows = []
    for q in pages:
        if q.v2: continue
        try:
            before = subprocess.run(["git", "show", f"{BASE_COMMIT}:public/{q.rel}"], cwd=ROOT, capture_output=True, text=True).stdout
        except Exception:
            before = ""
        bdom = parse(before) if before else None
        b_links = collections.Counter()
        b_anchor_text = set()
        if bdom:
            for a in bdom.iter("a"):
                b_links[urllib.parse.urlparse(a.attrs.get("href", "")).path] += 1
                b_anchor_text.add(a.get_text().lower())
        m = re.search(r"<!--PS-V2-LINKS-->(.*?)<!--/PS-V2-LINKS-->", q.src, re.S)
        block_hrefs = set(re.findall(r'href="([^"]+)"', m.group(1))) if m else set()
        seen = collections.Counter()
        for a in q.body.iter("a"):
            path = urllib.parse.urlparse(a.attrs.get("href", "")).path
            if path not in v2_paths: continue
            seen[path] += 1
            if seen[path] <= b_links.get(path, 0): continue      # already linked before the V2 work
            anchor = a.get_text()
            blk = next((x for x in a.ancestors() if x.tag in ("p", "li", "td", "dd", "figcaption")), None)
            txt = blk.get_text() if blk is not None else ""
            words = len(re.findall(r"\w+", txt))
            nl = len([x for x in blk.iter("a")]) if blk is not None else 0
            zone = link_zone(a)
            if a.attrs.get("href") in block_hrefs and a.inside(cls="art-section") and blk is not None and blk.tag == "li" and words <= 14:
                kind = "New guides list"
            elif zone == "footer":
                kind = "footer"
            elif blk is not None and blk.tag in ("p", "td", "dd") and words >= 12:
                link_share = len(" ".join(x.get_text() for x in blk.iter("a")).split()) / max(1, words)
                if nl >= 4 or link_share > .45:
                    kind = "link-heavy paragraph"
                elif anchor.lower() in b_anchor_text:
                    kind = "repointed (same words, new target)"
                else:
                    kind = "in a sentence"
            elif blk is not None and blk.tag == "li":
                kind = "list item in text"
            else:
                kind = zone
            rows.append({"from": q.url.replace(SITE, ""), "to": path, "anchor": anchor, "kind": kind, "links_in_block": nl,
                         "words": words, "text": txt[:420]})
    return rows


def main():
    pages = [Page(f) for f in all_pages()]
    site = {p.url: p for p in pages}
    v2 = [p for p in pages if p.v2]
    if "--page" in sys.argv:
        slug = sys.argv[sys.argv.index("--page") + 1]
        v2 = [p for p in v2 if p.path.stem == slug]
    ctx = {"titles": collections.Counter(p.title.lower() for p in pages), "descs": collections.Counter(p.desc.lower() for p in pages)}
    red = set()
    rf = PUB / "_redirects"
    if rf.exists():
        for line in rf.read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                red.add(line.split()[0])
    ctx["redirect_sources"] = red

    # twin candidates: EN page without hreflang 'es' whose slug terms match an ES page well
    ctx["twin_candidates"] = {}

    # duplication: 6-word shingles, V2 vs every page
    sh = {p.url: shingles(p.text) for p in pages}
    ctx["dup"] = {}
    for p in v2:
        best = (0, "")
        for q in pages:
            if q.url == p.url or q.lang_dir != p.lang_dir: continue
            j = len(sh[p.url] & sh[q.url]) / max(1, len(sh[p.url]))
            if j > best[0]: best = (j, q.url.replace(SITE, ""))
        ctx["dup"][p.url] = best

    # cannibalisation: title+H1 content-word overlap with another page in the same language
    ctx["cannibal"] = {}
    tk = {p.url: set(strip_acc(t) for t in toks(p.title + " " + p.h1)) for p in pages}
    for p in v2:
        best = (0, "")
        for q in pages:
            if q.url == p.url or q.lang_dir != p.lang_dir: continue
            j = jaccard(tk[p.url], tk[q.url])
            if j > best[0]: best = (j, q.url.replace(SITE, ""))
        if best[0] >= .6: ctx["cannibal"][p.url] = best

    # inbound links (all pages → V2 pages), by zone
    inbound = collections.defaultdict(collections.Counter)
    inbound_src = collections.defaultdict(set)
    anchors_in = collections.defaultdict(list)
    v2_paths = {urllib.parse.urlparse(p.url).path: p.url for p in v2}
    for q in pages:
        for a in q.body.iter("a"):
            h = a.attrs.get("href", "")
            path = urllib.parse.urlparse(h).path if h.startswith(("/", SITE)) else None
            if not path or path not in v2_paths or v2_paths[path] == q.url: continue
            tgt = v2_paths[path]
            zone = link_zone(a)
            inbound[tgt][zone] += 1
            inbound[tgt]["any"] += 1
            inbound_src[tgt].add(q.url)
            if zone == "body":
                anchors_in[tgt].append(a.get_text())
    interlinks = interlink_changes(pages, v2_paths)
    ctx["inbound"], ctx["inbound_src"] = inbound, inbound_src

    # sitemap + live
    ctx["sitemap"], ctx["live"] = {}, {}
    if not OFFLINE:
        print("fetching sitemap and live pages…", file=sys.stderr)
        ctx["sitemap"] = load_sitemap()
        with concurrent.futures.ThreadPoolExecutor(8) as ex:
            for url, res in ex.map(live_check, v2):
                ctx["live"][url] = res

    results = {}
    for p in v2:
        results[p.url] = {"rel": p.rel, "lang": p.lang_dir, "title": p.title, "h1": p.h1, "words": p.words,
                          "checks": audit_page(p, site, ctx),
                          "outline": [(int(n.tag[1]), n.get_text()[:110], "article" if n.inside("article") else "template")
                                      for n in p.dom.iter() if re.fullmatch(r"h[1-4]", n.tag)],
                          "inbound": dict(inbound.get(p.url, {})), "inbound_pages": len(inbound_src.get(p.url, ())),
                          "anchors_in": anchors_in.get(p.url, []), "img_bytes": getattr(p, "local_img_bytes", 0)}

    if "--page" in sys.argv:
        for u, d in results.items():
            print(u)
            for c in d["checks"]:
                if c["status"] != "pass": print(f"  {c['status'].upper():5} [{c['cat']}] {c['id']}: {c['msg']}")
        return

    # external image availability (hotlinks)
    ext_status = {}
    if not OFFLINE:
        ext = sorted({i.attrs.get("src") for p in v2 for i in p.body.iter("img") if i.attrs.get("src", "").startswith("http") and "panamaspot.com" not in i.attrs.get("src", "")})
        with concurrent.futures.ThreadPoolExecutor(8) as ex:
            for u, (st, _, _) in zip(ext, ex.map(lambda u: fetch(u, "HEAD"), ext)):
                ext_status[u] = st
    robots_txt = fetch(SITE + "/robots.txt")[2].decode("utf-8", "replace") if not OFFLINE else ""

    out = {"generated": datetime.datetime.now().isoformat(timespec="minutes"), "pages": results, "interlinks": interlinks,
           "ext_images": ext_status, "robots": robots_txt, "sitemap_count": len(ctx["sitemap"]),
           "n_site_pages": len(pages)}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/seo-v2-audit.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"audited {len(results)} V2 pages, {sum(len(d['checks']) for d in results.values())} checks → reports/seo-v2-audit.json")


if __name__ == "__main__":
    main()
