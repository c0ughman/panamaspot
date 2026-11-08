#!/usr/bin/env python3
"""
site_seo_audit.py - sitewide SEO + technical SEO audit of every built page in out/.

Covers all page types (homepages, hubs, V2 guides, old guides, funnels, 404) and
the live site. Standard library only.

    npm run build   (or use the existing out/)
    python3 scripts/site_seo_audit.py [--offline] [--out DIR]

Writes DIR/site-audit.json (per-page facts + issues) and prints a summary.
"""
import re, sys, json, html, pathlib, collections, struct, datetime, statistics, hashlib
import urllib.request, urllib.error, urllib.parse, concurrent.futures, ssl, time
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SITE = "https://panamaspot.com"
OFFLINE = "--offline" in sys.argv
DEST = pathlib.Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else ROOT / "reports"
UA = "Mozilla/5.0 (compatible; PanamaSpot-site-audit/1.0)"


# ───────────────────────── parsing ─────────────────────────
class Page(HTMLParser):
    """Single pass collecting everything the checks need."""
    SKIP = {"script", "style", "noscript", "template", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.title = ""; self._in_title = False
        self.metas = []; self.links = []; self.anchors = []; self.imgs = []
        self.headings = []; self._h = None
        self.jsonld = []; self._ld = None
        self.scripts = []; self.styles_inline = 0; self._style = False
        self.text = []; self._skip = 0
        self.zone = []          # nav/header/footer/aside zone stack
        self.html_lang = ""
        self.ids = set()
        self.iframes = []; self.videos = 0
        self.body_started = False
        self.a_open = None
        self.bg_imgs = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if "id" in a: self.ids.add(a["id"])
        st = a.get("style", "")
        if "url(" in st:
            self.bg_imgs += re.findall(r"url\(['\"]?([^'\")]+)", st)
        if tag == "html": self.html_lang = a.get("lang", "")
        if tag == "body": self.body_started = True
        if tag in ("nav", "header", "footer", "aside") or ("wrap nav" in a.get("class", "")) or a.get("role") == "navigation":
            self.zone.append(tag if tag in ("nav", "header", "footer", "aside") else "nav")
            self.stack.append(("zone", tag))
        else:
            self.stack.append((None, tag))
        if tag in ("area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"):
            self.stack.pop()
        if tag == "title" and not self.body_started: self._in_title = True
        elif tag == "meta": self.metas.append(a)
        elif tag == "link": self.links.append(a)
        elif tag == "a":
            self.a_open = {"href": a.get("href", ""), "rel": a.get("rel", ""), "text": "", "zone": self.cur_zone(),
                           "aria": a.get("aria-label", ""), "target": a.get("target", ""), "hreflang": a.get("hreflang", ""),
                           "cls": a.get("class", "")}
            self.anchors.append(self.a_open)
        elif tag == "img":
            a["_zone"] = self.cur_zone(); a["_idx"] = len(self.imgs)
            self.imgs.append(a)
            if self.a_open is not None and not self.a_open["text"]:
                self.a_open["text"] += " " + a.get("alt", "")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._h = [tag, "", self.cur_zone(), a.get("id", "")]
        elif tag == "script":
            t = a.get("type", "")
            if t == "application/ld+json": self._ld = []
            self.scripts.append(a)
            self._skip += 1
        elif tag == "style":
            self._style = True; self._skip += 1
        elif tag in ("noscript", "template", "svg"):
            self._skip += 1
        elif tag == "iframe": self.iframes.append(a)
        elif tag == "video": self.videos += 1

    def cur_zone(self):
        return self.zone[-1] if self.zone else "body"

    def handle_endtag(self, tag):
        if tag == "title": self._in_title = False
        elif tag == "a": self.a_open = None
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._h:
            self.headings.append((self._h[0], re.sub(r"\s+", " ", self._h[1]).strip(), self._h[2], self._h[3])); self._h = None
        elif tag == "script":
            if self._ld is not None:
                self.jsonld.append("".join(self._ld)); self._ld = None
            self._skip = max(0, self._skip - 1)
        elif tag == "style":
            self._style = False; self._skip = max(0, self._skip - 1)
        elif tag in ("noscript", "template", "svg"):
            self._skip = max(0, self._skip - 1)
        # pop stack to matching tag
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][1] == tag:
                for kind, _ in self.stack[i:]:
                    if kind == "zone" and self.zone: self.zone.pop()
                del self.stack[i:]
                break

    def handle_data(self, d):
        if self._in_title: self.title += d
        if self._ld is not None: self._ld.append(d); return
        if self._style: self.styles_inline += len(d); return
        if self._skip: return
        if self._h: self._h[1] += d
        if self.a_open is not None: self.a_open["text"] += d
        if self.body_started:
            self.text.append((d, self.cur_zone()))


def meta(p, name, attr="name"):
    for m in p.metas:
        if m.get(attr, "").lower() == name.lower():
            return m.get("content", "")
    return ""


# ───────────────────────── helpers ─────────────────────────
CHARW = collections.defaultdict(lambda: 9.0, {**{c: 5.0 for c in "iljtf.,:;'|!I "}, **{c: 13.5 for c in "mwMW"},
                                              **{c: 11.5 for c in "ABCDEFGHKNOPQRSTUVXYZ&"}, **{c: 6.5 for c in "r()-"}})


def px_width(s):  # rough Arial 20px (Google desktop title)
    return sum(CHARW[c] for c in s)


def url_for_file(rel):
    rel = rel[:-5] if rel.endswith(".html") else rel
    if rel == "index": return SITE
    if rel == "es": return SITE + "/es"
    return SITE + "/" + rel


def norm_url(href, base):
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "data:", "#", "sms:", "whatsapp:")): return None
    u = urllib.parse.urljoin(base + ("/" if base == SITE else ""), href)
    pu = urllib.parse.urlsplit(u)
    return pu


def img_dims(f):
    try:
        b = f.read_bytes()[:65536]
    except Exception:
        return None
    try:
        if b[:8] == b"\x89PNG\r\n\x1a\n": return struct.unpack(">II", b[16:24])
        if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
            ch = b[12:16]
            if ch == b"VP8X": return (int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1)
            if ch == b"VP8 ": w, h = struct.unpack("<HH", b[26:30]); return (w & 0x3FFF, h & 0x3FFF)
            if ch == b"VP8L":
                bits = int.from_bytes(b[21:25], "little"); return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
        if b[:2] == b"\xff\xd8":
            i = 2
            while i < len(b) - 9:
                if b[i] != 0xFF: i += 1; continue
                m = b[i + 1]
                if m in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", b[i + 5:i + 9]); return (w, h)
                i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
        if b[:6] in (b"GIF87a", b"GIF89a"): return struct.unpack("<HH", b[6:10])
        if b[4:12] in (b"ftypavif", b"ftypheic"): return None
    except Exception:
        return None
    return None


def local_file(u):
    """Map a site URL/path to a file in out/ (pages or assets)."""
    pu = urllib.parse.urlsplit(u)
    if pu.netloc and pu.netloc not in ("panamaspot.com", "www.panamaspot.com"): return None
    path = urllib.parse.unquote(pu.path)
    if path in ("", "/"): return OUT / "index.html"
    p = OUT / path.lstrip("/")
    if p.is_file(): return p
    if (OUT / (path.lstrip("/") + ".html")).is_file(): return OUT / (path.lstrip("/") + ".html")
    if p.is_dir() and (p / "index.html").is_file(): return p / "index.html"
    return None


def toks(s):
    s = html.unescape(s.lower())
    return [w for w in re.findall(r"[a-záéíóúñü0-9]+", s)]


STOP = set("the a an of to in and for on with at from by is are your you how what best de la el en y los las del para con por que un una su es al lo como guía guide panama panamá 2026".split())


def shingles(words, k=5):
    return {" ".join(words[i:i + k]) for i in range(max(0, len(words) - k + 1))}


def jacc(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def fetch(url, method="GET", follow=False, timeout=25, headers=None):
    h = {"User-Agent": UA, "Accept-Encoding": "gzip, br"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, method=method, headers=h)

    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedir)
    t0 = time.time()
    try:
        r = opener.open(req, timeout=timeout)
        body = r.read() if method == "GET" else b""
        return {"status": r.status, "headers": dict(r.headers), "url": r.geturl(), "ms": int((time.time() - t0) * 1000), "len": len(body)}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "headers": dict(e.headers or {}), "url": url, "ms": int((time.time() - t0) * 1000), "len": 0}
    except Exception as e:
        return {"status": 0, "error": str(e)[:120], "url": url, "headers": {}, "ms": int((time.time() - t0) * 1000), "len": 0}


# ───────────────────────── load site ─────────────────────────
def kind_of(rel, s):
    if rel in ("index.html", "es.html"): return "home"
    if rel.startswith("funnels/"): return "funnel"
    if rel in ("404.html", "_not-found.html"): return "404"
    if '<header class="hero">' in s or "<header class=\"hero\"" in s: return "v2"
    if 'class="article-page' in s: return "old"
    if '__PS_PAGE__ = {"type":"hub"' in s: return "hub"
    return "other"


def load():
    pages = {}
    for f in sorted(OUT.rglob("*.html")):
        rel = str(f.relative_to(OUT))
        if rel.startswith(("_next", "preview/")):
            if rel.startswith("preview/"):
                pass
            else:
                continue
        s = f.read_text(encoding="utf-8", errors="replace")
        p = Page()
        try:
            p.feed(s)
        except Exception as e:
            print("parse error", rel, e)
        p.rel, p.src, p.file = rel, s, f
        p.url = url_for_file(rel)
        p.kind = kind_of(rel, s)
        m = re.search(r'__PS_PAGE__ = (\{.*?\});', s)
        p.ps = json.loads(m.group(1)) if m else {}
        if p.kind == "other" and p.ps.get("type") == "hub": p.kind = "hub"
        p.lang_dir = "es" if rel.startswith("es/") or rel == "es.html" or rel.endswith("_es.html") or "_es_" in rel else "en"
        p.robots = meta(p, "robots").lower()
        p.desc = meta(p, "description")
        p.canon = [l.get("href", "") for l in p.links if l.get("rel", "").lower() == "canonical"]
        p.hreflang = {}
        for l in p.links:
            if l.get("rel", "").lower() == "alternate" and (l.get("hreflang") or l.get("hrefLang")):
                p.hreflang[(l.get("hreflang") or l.get("hrefLang"))] = l.get("href", "")
        p.title = html.unescape(re.sub(r"\s+", " ", p.title)).strip()
        p.ld = []
        for raw in p.jsonld:
            try:
                d = json.loads(raw)
                for x in (d if isinstance(d, list) else d.get("@graph", [d]) if isinstance(d, dict) else []):
                    p.ld.append(x)
            except Exception as e:
                p.ld.append({"__invalid__": str(e)[:80], "raw": raw[:120]})
        words_all = " ".join(t for t, z in p.text)
        words_main = " ".join(t for t, z in p.text if z in ("body", "header"))
        p.words_all = toks(words_all)
        p.words_main = toks(words_main)
        p.indexable = "noindex" not in p.robots and p.kind not in ("404",)
        pages[p.url] = p
    return pages


def load_redirects():
    rules = {}
    f = OUT / "_redirects"
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split()
            if len(parts) >= 2: rules[parts[0]] = (parts[1], parts[2] if len(parts) > 2 else "301")
    return rules


def load_sitemap_local():
    f = OUT / "sitemap.xml"
    sm = {}
    if not f.exists(): return sm
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml", "i": "http://www.google.com/schemas/sitemap-image/1.1"}
    root = ET.fromstring(f.read_bytes())
    for u in root.findall("s:url", ns):
        loc = u.findtext("s:loc", "", ns).strip()
        sm[loc] = {"lastmod": u.findtext("s:lastmod", "", ns), "alts": {x.get("hreflang"): x.get("href") for x in u.findall("x:link", ns)},
                   "images": [i.findtext("i:loc", "", ns) for i in u.findall("i:image", ns)],
                   "priority": u.findtext("s:priority", "", ns), "changefreq": u.findtext("s:changefreq", "", ns)}
    return sm


# ───────────────────────── checks ─────────────────────────
GENERIC_ANCHORS = {"click here", "here", "read more", "more", "learn more", "aquí", "aqui", "leer más", "ver más", "más", "this", "link", "esta guía", "this guide"}


def audit(pages, redirects, sm):
    issues = collections.defaultdict(list)   # url -> [(sev, code, detail)]
    site_issues = []

    def I(u, sev, code, detail=""):
        issues[u].append((sev, code, detail))

    idx = {u: p for u, p in pages.items() if p.indexable and p.kind != "funnel"}
    titles = collections.Counter(p.title.lower() for p in idx.values())
    descs = collections.Counter(p.desc.lower() for p in idx.values() if p.desc)
    h1s = collections.Counter()
    for p in idx.values():
        h = [t for tag, t, z, _ in p.headings if tag == "h1"]
        if h: h1s[h[0].lower()] += 1

    # link graph
    inlinks = collections.defaultdict(lambda: {"ctx": set(), "nav": set(), "anchors": collections.Counter()})
    outlinks = {}
    broken = collections.defaultdict(list)
    to_redirect = collections.defaultdict(list)
    ext_links = collections.Counter()
    all_ext = set()
    img_refs = collections.defaultdict(set)
    missing_imgs = collections.defaultdict(set)

    for u, p in pages.items():
        outs = []
        for a in p.anchors:
            href = a["href"].strip()
            pu = norm_url(href, u)
            if pu is None: continue
            if pu.scheme not in ("http", "https"): continue
            host = pu.netloc.lower()
            if host in ("panamaspot.com", "www.panamaspot.com"):
                path = pu.path.rstrip("/") or ""
                target = SITE + path if path else SITE
                if host.startswith("www") or pu.scheme == "http":
                    I(u, "warn", "link-non-canonical-host", href)
                if path.endswith(".html"):
                    I(u, "warn", "link-html-ext", href)
                if pu.path.endswith("/") and pu.path != "/":
                    I(u, "warn", "link-trailing-slash", href)
                if path in redirects:
                    to_redirect[u].append((href, redirects[path][0]))
                    target = SITE + redirects[path][0]
                tf = local_file(target)
                if tf is None and not path.startswith(("/images", "/fonts", "/video", "/css", "/js")):
                    if not (path.startswith("/funnels/") and (OUT / (path.lstrip("/") + ".html")).exists()):
                        broken[u].append(href)
                outs.append(target)
                zone = a["zone"]
                key = "nav" if zone in ("nav", "header", "footer", "aside") else "ctx"
                if target != u:
                    inlinks[target][key].add(u)
                    txt = re.sub(r"\s+", " ", a["text"] or a["aria"]).strip()
                    inlinks[target]["anchors"][txt.lower()[:80]] += 1
                    if txt.lower() in GENERIC_ANCHORS:
                        I(u, "info", "anchor-generic", f"'{txt}' → {path}")
                if "nofollow" in a["rel"]:
                    I(u, "warn", "internal-nofollow", href)
            else:
                ext_links[host] += 1
                all_ext.add(pu.geturl())
        outlinks[u] = outs
        # images
        for im in p.imgs:
            src = im.get("src", "") or im.get("data-src", "")
            if not src or src.startswith("data:"): continue
            pu = urllib.parse.urlsplit(urllib.parse.urljoin(u + "/", src))
            if pu.netloc in ("panamaspot.com", ""):
                img_refs[pu.path].add(u)
                if local_file(SITE + pu.path) is None: missing_imgs[u].add(pu.path)
            for part in (im.get("srcset", "") or "").split(","):
                part = part.strip().split(" ")[0]
                if part:
                    q = urllib.parse.urlsplit(urllib.parse.urljoin(u + "/", part))
                    if q.netloc in ("panamaspot.com", "") and local_file(SITE + q.path) is None: missing_imgs[u].add(q.path)
        for b in p.bg_imgs:
            q = urllib.parse.urlsplit(urllib.parse.urljoin(u + "/", html.unescape(b)))
            if q.netloc in ("panamaspot.com", "") and q.path and local_file(SITE + q.path) is None: missing_imgs[u].add(q.path)

    # click depth from homepages (all links)
    depth = {}
    frontier = [SITE, SITE + "/es"]
    for s0 in frontier: depth[s0] = 0
    q = list(frontier)
    while q:
        cur = q.pop(0)
        for t in outlinks.get(cur, []):
            if t not in depth and t in pages:
                depth[t] = depth[cur] + 1; q.append(t)
    # depth using contextual links only (excluding menu/footer)
    depth_ctx = {SITE: 0, SITE + "/es": 0}
    q = [SITE, SITE + "/es"]
    ctx_out = collections.defaultdict(set)
    for t, d in inlinks.items():
        for src in d["ctx"]: ctx_out[src].add(t)
    while q:
        cur = q.pop(0)
        for t in ctx_out.get(cur, []):
            if t not in depth_ctx and t in pages:
                depth_ctx[t] = depth_ctx[cur] + 1; q.append(t)

    # similarity
    sh = {u: shingles(p.words_main) for u, p in idx.items()}
    near_dupes = []
    ul = list(idx)
    for i in range(len(ul)):
        for j in range(i + 1, len(ul)):
            a, b = ul[i], ul[j]
            if idx[a].lang_dir != idx[b].lang_dir: continue
            jv = jacc(sh[a], sh[b])
            if jv > 0.12: near_dupes.append((round(jv, 3), a, b))
    near_dupes.sort(reverse=True)

    # title keyword overlap (cannibalisation candidates)
    def core(t):
        return frozenset(w for w in toks(t) if w not in STOP and len(w) > 2)
    cann = []
    for i in range(len(ul)):
        for j in range(i + 1, len(ul)):
            a, b = idx[ul[i]], idx[ul[j]]
            if a.lang_dir != b.lang_dir: continue
            ca, cb = core(a.title), core(b.title)
            if not ca or not cb: continue
            ov = len(ca & cb) / min(len(ca), len(cb))
            if ov >= 0.6 and len(ca & cb) >= 2: cann.append((round(ov, 2), a.url, b.url, a.title, b.title))
    cann.sort(reverse=True)

    facts = {}
    for u, p in pages.items():
        f = {"kind": p.kind, "lang": p.lang_dir, "title": p.title, "title_len": len(p.title), "title_px": int(px_width(p.title)),
             "desc": p.desc, "desc_len": len(p.desc), "robots": p.robots, "canonical": p.canon, "hreflang": p.hreflang,
             "html_kb": round(len(p.src.encode()) / 1024), "inline_css_kb": round(p.styles_inline / 1024),
             "words_main": len(p.words_main), "words_all": len(p.words_all),
             "h1": [t for tag, t, z, _ in p.headings if tag == "h1"],
             "h2": [t for tag, t, z, _ in p.headings if tag == "h2" and z in ("body", "header")],
             "imgs": len(p.imgs), "ld_types": [], "depth": depth.get(u), "depth_ctx": depth_ctx.get(u),
             "in_ctx": len(inlinks[u]["ctx"]), "in_nav": len(inlinks[u]["nav"]),
             "out_internal": len(set(outlinks.get(u, []))), "in_sitemap": u in sm,
             "pub": meta(p, "article:published_time", "property"), "mod": meta(p, "article:modified_time", "property"),
             "og_image": meta(p, "og:image", "property"), "og_type": meta(p, "og:type", "property")}
        for d in p.ld:
            t = d.get("@type", "?") if isinstance(d, dict) else "?"
            f["ld_types"].append(t if isinstance(t, str) else "/".join(t))
        facts[u] = f
        if p.kind == "404":
            continue
        is_idx = p.indexable
        # ── indexability
        if p.kind == "funnel":
            if "noindex" not in p.robots: I(u, "warn", "funnel-indexable", p.robots)
            if u in sm: I(u, "fail", "noindex-in-sitemap")
            if len(inlinks[u]["ctx"]) + len(inlinks[u]["nav"]) and "nofollow" not in p.robots:
                pass
            continue
        if not is_idx:
            I(u, "fail" if u in sm else "info", "noindex", p.robots); continue
        if "max-image-preview:large" not in p.robots:
            I(u, "info", "no-max-image-preview-large", p.robots)
        if len(p.canon) != 1: I(u, "fail", "canonical-count", str(len(p.canon)))
        elif p.canon[0] != u: I(u, "fail", "canonical-not-self", p.canon[0])
        if u not in sm: I(u, "fail", "not-in-sitemap")
        # ── title / desc
        if not p.title: I(u, "fail", "title-missing")
        else:
            if titles[p.title.lower()] > 1: I(u, "fail", "title-duplicate", p.title)
            if len(p.title) > 65 or px_width(p.title) > 600: I(u, "warn", "title-long", f"{len(p.title)} chars ≈{int(px_width(p.title))}px: {p.title}")
            if len(p.title) < 30: I(u, "warn", "title-short", p.title)
        if not p.desc: I(u, "fail", "desc-missing")
        else:
            if descs[p.desc.lower()] > 1: I(u, "fail", "desc-duplicate", p.desc[:80])
            if len(p.desc) > 165: I(u, "info", "desc-long", f"{len(p.desc)}")
            if len(p.desc) < 100: I(u, "warn", "desc-short", f"{len(p.desc)}: {p.desc}")
        # ── lang
        hl = p.html_lang.split("-")[0].lower()
        if hl != p.lang_dir: I(u, "fail", "html-lang-mismatch", p.html_lang)
        # ── headings
        h1 = facts[u]["h1"]
        if len(h1) != 1: I(u, "fail" if not h1 else "warn", "h1-count", f"{len(h1)}: {h1[:3]}")
        elif h1s[h1[0].lower()] > 1: I(u, "warn", "h1-duplicate", h1[0])
        levels = [int(tag[1]) for tag, t, z, _ in p.headings if z in ("body", "header")]
        for a_, b_ in zip(levels, levels[1:]):
            if b_ > a_ + 1: I(u, "info", "heading-skip", f"h{a_}→h{b_}"); break
        empty_h = [tag for tag, t, z, _ in p.headings if not t]
        if empty_h: I(u, "warn", "heading-empty", ",".join(empty_h))
        nav_h = [(tag, t) for tag, t, z, _ in p.headings if z in ("nav", "footer", "aside") and tag in ("h2", "h3")]
        if len(nav_h) > 4: I(u, "info", "headings-in-chrome", f"{len(nav_h)} h2/h3 in nav/footer")
        # ── content
        wc = len(p.words_main)
        if p.kind in ("v2", "old") and wc < 900: I(u, "warn", "thin-content", f"{wc} words")
        if p.kind == "hub" and wc < 500: I(u, "warn", "thin-hub", f"{wc} words")
        # ── hreflang
        hlx = p.hreflang
        if hlx:
            if hlx.get(p.lang_dir) != u: I(u, "fail", "hreflang-no-self", str(hlx))
            if "x-default" not in hlx: I(u, "warn", "hreflang-no-xdefault")
            other = "es" if p.lang_dir == "en" else "en"
            if other in hlx:
                t = pages.get(hlx[other])
                if t is None: I(u, "fail", "hreflang-target-missing", hlx[other])
                else:
                    if t.hreflang.get(p.lang_dir) != u: I(u, "fail", "hreflang-not-reciprocal", f"{hlx[other]} → {t.hreflang.get(p.lang_dir)}")
                    if not t.indexable: I(u, "fail", "hreflang-target-noindex", hlx[other])
            smalt = sm.get(u, {}).get("alts", {})
            if smalt and smalt != hlx: I(u, "warn", "hreflang-sitemap-mismatch", f"sitemap {smalt} vs page {hlx}")
            if not smalt and other in hlx: I(u, "info", "hreflang-not-in-sitemap")
            for k in hlx:
                if k not in ("en", "es", "x-default") and not re.fullmatch(r"[a-z]{2}(-[A-Z]{2})?", k): I(u, "fail", "hreflang-bad-code", k)
        else:
            I(u, "info", "hreflang-none")
        # ── social
        for k in ("og:title", "og:description", "og:image", "og:url", "og:type"):
            if not meta(p, k, "property"): I(u, "warn", "og-missing", k)
        ogu = meta(p, "og:url", "property")
        if ogu and ogu != u: I(u, "warn", "og-url-not-canonical", ogu)
        ogi = meta(p, "og:image", "property")
        if ogi:
            lf = local_file(ogi)
            if lf is None: I(u, "fail", "og-image-missing-file", ogi)
            else:
                d = img_dims(lf)
                if lf.suffix.lower() == ".webp": I(u, "info", "og-image-webp", ogi)
                if d and (d[0] < 1200 or not (1.5 <= d[0] / max(1, d[1]) <= 2.1)): I(u, "info", "og-image-size", f"{d}")
                if lf.stat().st_size > 600_000: I(u, "info", "og-image-heavy", f"{lf.stat().st_size // 1024} KB")
        ogalt = meta(p, "og:image:alt", "property")
        if ogalt and p.kind == "hub":
            pass
        # ── structured data
        ldt = facts[u]["ld_types"]
        inval = [d for d in p.ld if isinstance(d, dict) and "__invalid__" in d]
        if inval: I(u, "fail", "jsonld-invalid", inval[0]["__invalid__"])
        if "BreadcrumbList" not in ldt and p.kind != "home": I(u, "warn", "no-breadcrumb-schema")
        arts = [d for d in p.ld if isinstance(d, dict) and d.get("@type") in ("Article", "BlogPosting", "TravelArticle", "NewsArticle")]
        if p.kind in ("v2", "old"):
            if not arts: I(u, "warn", "no-article-schema", ",".join(ldt))
            for a in arts:
                for k in ("headline", "image", "datePublished", "dateModified", "author"):
                    if not a.get(k): I(u, "warn", "article-schema-missing", k)
                au = a.get("author")
                aus = au if isinstance(au, list) else [au]
                for x in aus:
                    if isinstance(x, dict):
                        if x.get("@type") == "Organization": I(u, "info", "author-is-organization", x.get("name", ""))
                        elif x.get("@type") == "Person" and not x.get("url"): I(u, "info", "author-person-no-url", x.get("name", ""))
                hl_ = a.get("headline", "")
                if isinstance(hl_, str) and len(hl_) > 110: I(u, "warn", "headline-long", str(len(hl_)))
                if a.get("dateModified", "")[:10] != (facts[u]["mod"] or "")[:10] and facts[u]["mod"]:
                    I(u, "warn", "date-mismatch-meta-vs-ld", f"meta {facts[u]['mod']} ld {a.get('dateModified')}")
        faq = [d for d in p.ld if isinstance(d, dict) and d.get("@type") == "FAQPage"]
        if faq:
            # visible check: first question should be on page
            qs = faq[0].get("mainEntity", [])
            if qs:
                qn = html.unescape(qs[0].get("name", ""))[:40].lower()
                body_text = " ".join(t for t, z in p.text).lower()
                if qn and qn not in re.sub(r"\s+", " ", body_text): I(u, "warn", "faq-schema-not-visible", qn)
        for d in p.ld:
            if not isinstance(d, dict): continue
            for k in ("url", "@id"):
                v = d.get(k)
                if isinstance(v, str) and v.startswith("http://"): I(u, "warn", "ld-http-url", v)
        # ── dates
        smm = sm.get(u, {}).get("lastmod", "")[:10]
        if facts[u]["mod"] and smm and smm < facts[u]["mod"][:10]: I(u, "warn", "sitemap-lastmod-older", f"sitemap {smm} < page {facts[u]['mod']}")
        if facts[u]["mod"] and smm and smm > facts[u]["mod"][:10]: I(u, "info", "sitemap-lastmod-newer", f"sitemap {smm} > page {facts[u]['mod']}")
        # ── images
        no_alt = [im.get("src", "")[-50:] for im in p.imgs if "alt" not in im]
        empty_alt_ctx = [im for im in p.imgs if im.get("alt", None) == "" and im["_zone"] == "body"]
        no_dims = [im.get("src", "")[-50:] for im in p.imgs if not (im.get("width") and im.get("height"))]
        if no_alt: I(u, "warn", "img-no-alt", f"{len(no_alt)}: {no_alt[:2]}")
        if len(empty_alt_ctx) > 3: I(u, "info", "img-empty-alt", f"{len(empty_alt_ctx)} in content")
        if no_dims: I(u, "info", "img-no-dims", f"{len(no_dims)}/{len(p.imgs)}")
        first_body = [im for im in p.imgs if im["_zone"] in ("body", "header")][:1]
        if first_body and first_body[0].get("loading") == "lazy" and p.kind in ("v2", "old"):
            I(u, "info", "first-img-lazy", first_body[0].get("src", "")[-60:])
        alts = collections.Counter(im.get("alt", "").strip().lower() for im in p.imgs if im.get("alt", "").strip())
        rep = [(a, c) for a, c in alts.items() if c > 2]
        if rep: I(u, "info", "img-alt-repeated", f"{rep[:2]}")
        if missing_imgs.get(u): I(u, "fail", "img-missing-file", f"{len(missing_imgs[u])}: {sorted(missing_imgs[u])[:3]}")
        # img weight
        tot = 0; heavy = []
        for im in p.imgs:
            src = im.get("src", "")
            lf = local_file(urllib.parse.urljoin(u + "/", src)) if src and not src.startswith("data:") else None
            if lf:
                sz = lf.stat().st_size; tot += sz
                if sz > 400_000: heavy.append(f"{lf.name} {sz // 1024}KB")
        facts[u]["img_kb"] = tot // 1024
        if heavy: I(u, "warn", "img-heavy", f"{len(heavy)}: {heavy[:3]}")
        # ── links
        if broken.get(u): I(u, "fail", "broken-internal-link", f"{len(broken[u])}: {broken[u][:4]}")
        if to_redirect.get(u): I(u, "warn", "link-to-redirect", f"{len(to_redirect[u])}: {to_redirect[u][:3]}")
        if inlinks[u]["ctx"] == set() and p.kind not in ("home",):
            I(u, "warn", "no-contextual-inlinks", f"only menu/footer links ({len(inlinks[u]['nav'])})")
        elif len(inlinks[u]["ctx"]) <= 2 and p.kind in ("v2", "old"):
            I(u, "info", "few-contextual-inlinks", str(len(inlinks[u]["ctx"])))
        if depth.get(u) is None and p.kind != "home": I(u, "fail", "orphan-unreachable")
        elif (depth.get(u) or 0) > 3: I(u, "warn", "deep-page", f"depth {depth[u]}")
        # ── tech
        if "http://" in re.sub(r'(xmlns(:\w+)?="http://[^"]+"|http://www\.w3\.org[^"\s]*|http://schema\.org)', "", p.src):
            m = re.findall(r'(?:src|href)="(http://[^"]+)"', p.src)
            if m: I(u, "warn", "mixed-content", m[:3])
        if len(p.src) > 250_000: I(u, "info", "html-heavy", f"{len(p.src) // 1024} KB")
        blocking = [l.get("href") for l in p.links if l.get("rel") == "stylesheet" and "media" not in l and "onload" not in l]
        facts[u]["render_blocking_css"] = blocking
        sync_js = [s.get("src") for s in p.scripts if s.get("src") and "async" not in s and "defer" not in s and s.get("type") != "module"]
        if sync_js: I(u, "warn", "sync-script", sync_js[:3])
        if not meta(p, "viewport"): I(u, "fail", "no-viewport")
        lazy_iframes = [i for i in p.iframes if i.get("loading") != "lazy"]
        if lazy_iframes: I(u, "info", "iframe-not-lazy", [i.get("src", "")[:60] for i in lazy_iframes][:2])

    # sitemap-level
    for loc in sm:
        p = pages.get(loc)
        if p is None: site_issues.append(("fail", "sitemap-url-no-file", loc))
        elif not p.indexable: site_issues.append(("fail", "sitemap-url-noindex", loc))
        elif p.canon and p.canon[0] != loc: site_issues.append(("fail", "sitemap-url-not-canonical", loc))
    lm = collections.Counter(v["lastmod"][:10] for v in sm.values())
    site_issues.append(("info", "sitemap-lastmod-distribution", dict(lm.most_common(12))))
    for path, (tgt, code) in redirects.items():
        if local_file(SITE + tgt.split("?")[0].split("#")[0]) is None and not tgt.startswith("http") and ":" not in tgt:
            site_issues.append(("fail", "redirect-target-missing", f"{path} → {tgt}"))
        if tgt in redirects: site_issues.append(("warn", "redirect-chain", f"{path} → {tgt} → {redirects[tgt][0]}"))
        if local_file(SITE + path) is not None and ":" not in path: site_issues.append(("warn", "redirect-shadowed-by-file", path))

    return issues, site_issues, facts, {
        "inlinks": {u: {"ctx": len(v["ctx"]), "nav": len(v["nav"]), "top_anchors": v["anchors"].most_common(6)} for u, v in inlinks.items()},
        "near_dupes": near_dupes[:60], "cannibal_titles": cann[:80], "ext_hosts": ext_links.most_common(40),
        "all_ext": sorted(all_ext), "img_refs": len(img_refs),
    }


# ───────────────────────── live checks ─────────────────────────
def live(pages, sm, all_ext):
    res = {}
    # protocol / host / variants
    sample = SITE + "/articles/boquete-coffee-farm-tour"
    variants = {
        "http_apex": "http://panamaspot.com/", "https_www": "https://www.panamaspot.com/", "http_www": "http://www.panamaspot.com/",
        "html_ext": sample + ".html", "trailing_slash": sample + "/", "uppercase": SITE + "/articles/Boquete-Coffee-Farm-Tour",
        "query": sample + "?utm_source=x", "index_html": SITE + "/index.html", "es_slash": SITE + "/es/", "garbage_404": SITE + "/articles/this-does-not-exist-xyz",
        "robots": SITE + "/robots.txt", "sitemap": SITE + "/sitemap.xml", "funnel_noext": SITE + "/funnels/evalley_boquete",
        "funnel_old": SITE + "/funnels/evalley_boquete_old", "llms": SITE + "/llms.txt", "favicon": SITE + "/favicon.ico",
        "apple_touch": SITE + "/apple-touch-icon.png", "search_index": SITE + "/search-index.json", "next_txt": SITE + "/es.txt",
        "not_found_html": SITE + "/_not-found", "manifest": SITE + "/manifest.webmanifest",
    }
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        out = dict(zip(variants, ex.map(lambda u: fetch(u), variants.values())))
    res["variants"] = {k: {"url": variants[k], "status": v["status"], "location": v["headers"].get("Location") or v["headers"].get("location"),
                           "x-robots": v["headers"].get("X-Robots-Tag") or v["headers"].get("x-robots-tag"), "ms": v["ms"],
                           "cache": v["headers"].get("Cache-Control") or v["headers"].get("cache-control")} for k, v in out.items()}
    # headers on home + a guide + an image
    hd = {}
    for k, u in {"home": SITE + "/", "guide": sample, "image": SITE + "/images/v2/hikes-boquete-hero-1280.webp", "css": SITE + "/css/evalley-cta.css", "font": SITE + "/fonts/GildaC-650.woff2"}.items():
        r = fetch(u)
        hd[k] = {"status": r["status"], "ms": r["ms"], **{h: r["headers"].get(h) for h in ("Cache-Control", "Content-Encoding", "Strict-Transport-Security", "Server", "Age", "X-Nf-Request-Id", "Content-Type", "Vary", "Link", "Content-Security-Policy", "X-Content-Type-Options", "Cache-Status")}}
    res["headers"] = hd
    # every page live (sitemap + all built pages)
    urls = sorted(set(sm) | {u for u, p in pages.items() if p.kind not in ("404",)})
    with concurrent.futures.ThreadPoolExecutor(10) as ex:
        st = dict(zip(urls, ex.map(lambda u: fetch(u, method="GET"), urls)))
    res["pages"] = {u: {"status": v["status"], "location": v["headers"].get("Location") or v["headers"].get("location"), "ms": v["ms"],
                        "x-robots": v["headers"].get("X-Robots-Tag") or v["headers"].get("x-robots-tag"), "kb": v["len"] // 1024} for u, v in st.items()}
    # live sitemap vs local
    try:
        b = urllib.request.urlopen(urllib.request.Request(SITE + "/sitemap.xml", headers={"User-Agent": UA}), timeout=20).read()
        ET.fromstring(b); res["sitemap_xml_valid"] = True
        res["sitemap_live_count"] = b.count(b"<loc>")
        res["sitemap_live_bytes"] = len(b)
    except Exception as e:
        res["sitemap_xml_valid"] = str(e)
    # redirects live
    reds = load_redirects()
    with concurrent.futures.ThreadPoolExecutor(10) as ex:
        rr = dict(zip(reds, ex.map(lambda pth: fetch(SITE + pth, method="GET"), reds)))
    res["redirects"] = {k: {"status": v["status"], "location": v["headers"].get("Location") or v["headers"].get("location")} for k, v in rr.items()}
    # external links
    def ext(u):
        r = fetch(u, method="HEAD", follow=True, timeout=15)
        if r["status"] in (0, 403, 405, 400, 404, 429, 501):
            r2 = fetch(u, method="GET", follow=True, timeout=15)
            if r2["status"]: r = r2
        return r
    ext_urls = [u for u in all_ext if "wa.me" not in u and "api.whatsapp" not in u]
    with concurrent.futures.ThreadPoolExecutor(16) as ex:
        er = dict(zip(ext_urls, ex.map(ext, ext_urls)))
    res["external"] = {u: {"status": v["status"], "final": v.get("url"), "err": v.get("error")} for u, v in er.items()}
    return res


def main():
    pages = load()
    redirects = load_redirects()
    sm = load_sitemap_local()
    issues, site_issues, facts, extra = audit(pages, redirects, sm)
    live_res = {} if OFFLINE else live(pages, sm, extra["all_ext"])
    DEST.mkdir(parents=True, exist_ok=True)
    out = {"generated": datetime.datetime.now().isoformat(timespec="seconds"), "n_pages": len(pages),
           "kinds": collections.Counter(p.kind for p in pages.values()), "facts": facts,
           "issues": {u: v for u, v in issues.items()}, "site_issues": site_issues, "extra": extra, "live": live_res,
           "sitemap": sm}
    (DEST / "site-audit.json").write_text(json.dumps(out, indent=1, default=list, ensure_ascii=False))
    # summary
    codes = collections.Counter()
    sev = {}
    for u, lst in issues.items():
        for s, c, d in lst:
            codes[c] += 1; sev[c] = s
    print(f"{len(pages)} pages:", dict(out["kinds"]))
    for c, n in sorted(codes.items(), key=lambda x: ({"fail": 0, "warn": 1, "info": 2}[sev[x[0]]], -x[1])):
        print(f"  {sev[c]:4} {n:4}  {c}")
    print("site:", [(s, c, (d if isinstance(d, str) else "")[:80]) for s, c, d in site_issues if s != "info"][:30])
    print("wrote", DEST / "site-audit.json")


if __name__ == "__main__":
    main()
