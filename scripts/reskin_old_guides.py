"""Convert old-template guides to the V2 template by code. No text is rewritten and no tokens are spent per page.

Takes the words, headings, photos, schema and metadata from the old page and pours them into the V2 template
taken from a live V2 guide (style, nav, footer, scripts). Always reads the old page from git at BASE, so it can be
re-run after a template fix. A page that fails check() is not written.

  python3 scripts/reskin_old_guides.py --dry                 # convert all 80 in memory, report, write nothing
  python3 scripts/reskin_old_guides.py --page=articles/x     # convert and write one page (repeatable)
Then run scripts/evalley_cta_rollout.py --page=articles/x.html for the new CTAs.
"""
import html, json, re, subprocess, sys
from pathlib import Path
from urllib.parse import quote

BASE = "ef8aefe"
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "public"
DONOR = {"en": "articles/el-pianista-trail-boquete", "es": "es/articles/sendero-el-pianista-boquete-ruta-dificultad"}
T = {
    "en": dict(toc="On this page", glance="At a glance", who="Panama Spot editors", role="Guides to Panama", upd="Updated", know="Need to know", read="Read next",
               confirm="Always confirm with the operator before booking.", guide="Guide", explore=("Keep exploring", "More guides to read next", "All guides →"),
               more="Continue reading", faq="Questions", photos="Photos", home="/#cat-regions", of="of", place="PANAMA",
               months="January February March April May June July August September October November December".split()),
    "es": dict(toc="En esta página", glance="De un vistazo", who="Editores de Panama Spot", role="Guías de Panamá", upd="Actualizado en", know="Lo esencial", read="Lee después",
               confirm="Confirme siempre con el operador antes de reservar.", guide="Guía", explore=("Sigue explorando", "Más guías para leer después", "Todas las guías →"),
               more="Seguir leyendo", faq="Preguntas", photos="Fotos", home="/es#cat-regions", of="de", place="PANAMÁ",
               months="enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()),
}
EXTRA_CSS = """
/* old-guide components in the V2 template */
a.search { color: inherit; text-decoration: none; cursor: pointer; }
.gg b.sm { font: 700 15px/1.3 var(--sans); letter-spacing: 0; }
.note.warn { background: #fdf0ec; }
.fig.is-map img { aspect-ratio: auto; object-fit: contain; }
.prices.p3 { grid-template-columns: repeat(3, 1fr); }
.prices h3.k { font: 600 12.5px/1.3 var(--sans); color: var(--muted); letter-spacing: 0; }
@media (max-width: 760px) { .prices.p3 { grid-template-columns: 1fr; } .prices.p3 > div + div { box-shadow: inset 0 1px 0 var(--beige-2); } }
.sec ul, .sec ol, .article > ul { padding-left: 22px; display: grid; gap: 8px; color: var(--body); }
.t-c .tx { min-height: 0; overflow: hidden; }
.t-c p { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; line-clamp: 2; overflow: hidden; }
.id-t { display: block; font-weight: 600; color: var(--ink); }
.id-d { font-size: 14.5px; color: var(--body); margin: 2px 0; }
"""
SEARCH_TAG = '<script src="/js/search.js" defer></script>'


COPY = json.loads((ROOT / "design/evalley-cta/copy.json").read_text())
# E-Valley facts in old article text, from evalleybikes.net (read 2026-11-05). Applied to article text and FAQ schema alike.
ALLOWED_EV = {"35", "45", "55", "20", "25", "30", "66", "75", "85", "100", "115"}
PRICE_RULES = [
    (r"(E-?Valley[^.$]{0,140}?)\b(from|starting at) \$30(?: per bike| per person|/day| a day| per day)?", r"\1\2 $35 per person"),
    (r"(E-?Valley[^.$]{0,140}?)\b(desde|a partir de) \$30(?: por bici(?:cleta)?| por persona| al día| por día)?", r"\1\2 $35 por persona"),
]


def apply_prices(s):
    for pat, rep in PRICE_RULES:
        s = re.sub(pat, rep, s)
    return s


def funnel_to_whatsapp(s, lang):
    """Article links to E-Valley go straight to WhatsApp, like the CTAs (user decision 2026-11-04)."""
    def rep(m):
        region = "elvalle" if m[1] == "elvalle" else "boquete"
        c = COPY[f"{region}-{lang}"]
        return f'<a href="{html.escape("https://wa.me/" + c["wa_number"] + "?text=" + quote(c["wa_msg"]))}" target="_blank" rel="sponsored noopener" data-ev="inline" data-region="{"el-valle" if region == "elvalle" else "boquete"}">{m[2]}</a>'
    return re.sub(r'<a href="/funnels/evalley_(elvalle|boquete)[^"]*"[^>]*>(.*?)</a>', rep, s, flags=re.S)


def old_html(rel):
    return subprocess.run(["git", "show", f"{BASE}:public/{rel}.html"], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def block(s, start, tag="div"):
    """Return (begin, end) of the element whose opening tag starts at index `start`."""
    depth = 0
    for m in re.finditer(rf"<{tag}\b|</{tag}>", s[start:]):
        depth += -1 if m[0].startswith("</") else 1
        if depth == 0:
            return start, start + m.end()
    raise ValueError("unbalanced " + tag)


def find_block(s, needle, tag="div"):
    i = s.find(needle)
    return None if i < 0 else s[slice(*block(s, i, tag))]


def attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m[1] if m else ""


def clean_img(tag, cls=None, keep_lazy=True):
    """Keep src, srcset, sizes, alt and dimensions. Drop inline layout, keep a focal point."""
    a = []
    if cls: a.append(f'class="{cls}"')
    for n in ("srcset", "sizes", "alt"):
        v = attr(tag, n)
        if v or n == "alt": a.append(f'{n}="{v}"')
    if keep_lazy: a += ['loading="lazy"', 'decoding="async"']
    a.append(f'src="{attr(tag, "src")}"')
    for n in ("width", "height"):
        if attr(tag, n): a.append(f'{n}="{attr(tag, n)}"')
    fp = re.search(r"object-position:\s*([^;\"]+)", attr(tag, "style"))
    if fp: a.append(f'style="object-position:{fp[1].strip()}"')
    return "<img " + " ".join(a) + "/>"


def text(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def glance_cell(k, v):
    plain = text(v)
    m = re.match(r"^(.{1,20}?)(?:\s+\(|,\s+|;\s+|\s+[—–-]\s+|\s+(?:from|by|desde|en|por|via)\s+)(.+)$", plain)
    if m:
        rest = plain[len(m[1]):].strip(" ,;—–")
        if rest.startswith("(") and rest.endswith(")") and rest.count("(") == 1: rest = rest[1:-1]
        return f'<div><span class="k">{k}</span><b>{html.escape(m[1], quote=False)}</b><span class="s">{html.escape(rest, quote=False)}</span></div>'
    if len(plain) <= 16:
        return f'<div><span class="k">{k}</span><b>{v}</b></div>'
    return f'<div><span class="k">{k}</span><b class="sm">{v}</b></div>'


def convert_figures(s):
    def fig(m):
        cls = "fig is-map" if "is-map" in m[1] else "fig"
        img = re.search(r"<img\b[^>]*>", m[2])[0]
        cap = re.search(r"<figcaption\b[^>]*>.*?</figcaption>", m[2], re.S)
        return f'<figure class="{cls}">{clean_img(img)}{cap[0] if cap else ""}</figure>'
    return re.sub(r'<figure class="([^"]*)"[^>]*>(.*?)</figure>', fig, s, flags=re.S)


def convert_callouts(s):
    out = ""; pos = 0
    for m in re.finditer(r'<div class="callout([^"]*)">', s):
        if m.start() < pos: continue
        a, b = block(s, m.start())
        inner = s[m.end():b - 6]
        lab = re.match(r'\s*<span class="label">(.*?)</span>\s*', inner, re.S)
        body = inner[lab.end():] if lab else inner
        if not re.search(r"<(p|ul|ol)\b", body): body = f"<p>{body.strip()}</p>"
        cls = "note warn" if "warning" in m[1] else "note"
        out += s[pos:a] + f'<div class="{cls}">' + (f'<span class="lbl">{lab[1]}</span>' if lab else "") + body + "</div>"
        pos = b
    return out + s[pos:]


def convert_tables(s):
    s = re.sub(r'<table class="compare">(.*?)</table>', r'<div class="tbl"><table>\1</table></div>', s, flags=re.S)
    s = re.sub(r'<span class="pill good">', '<span class="yn">', s)
    s = re.sub(r'<span class="pill mid">', '<span class="yn mid">', s)
    s = re.sub(r'<span class="pill bad">', '<span class="yn no">', s)
    return re.sub(r'<span class="pill[^"]*">', '<span class="yn">', s)


def split_sections(prose, labels):
    prose = re.sub(r'<p class="lede">', '<p class="lead">', prose)
    parts = re.split(r'(?=<h2\b)', prose)
    intro, out = parts[0], []
    for p in parts[1:]:
        m = re.match(r'<h2\b([^>]*)>(.*?)</h2>', p, re.S)
        sid = attr(m[1], "id")
        title = re.sub(r'<span class="num">.*?</span>', "", m[2], flags=re.S).strip()
        idattr = f' id="{sid}"' if sid else ""
        lbl = labels.get(sid) or ""
        if text(title).lower().startswith(lbl.lower()): lbl = ""  # a label that only repeats the heading adds nothing
        eye = f'<span class="lbl">{lbl}</span>' if lbl else ""
        out.append(f'<section class="sec"{idattr}>{eye}<h2>{title}</h2>{p[m.end():].strip()}</section>')
    return intro.strip(), "\n\n".join(out)


def card_data(s):
    """Related guides: linked bento cards from the old page."""
    g = find_block(s, '<div class="home-bento-grid')
    cards = []
    if not g: return cards
    for m in re.finditer(r'<a class="bento-card[^"]*" href="([^"]+)">(.*?)</a>', g, re.S):
        img = re.search(r"<img\b[^>]*>", m[2]); h3 = re.search(r"<h3>(.*?)</h3>", m[2], re.S); pp = re.search(r"<p>(.*?)</p>", m[2], re.S); tag = re.search(r'b-tag">(.*?)<', m[2])
        cards.append(dict(href=m[1], src=attr(img[0], "src") if img else "", title=h3[1] if h3 else "", dek=pp[1] if pp else "", tag=tag[1] if tag else ""))
    return cards


def meta_of(href):
    f = P / (href.lstrip("/") + ".html")
    if not f.exists(): return None
    h = f.read_text(errors="ignore")
    t = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    d = re.search(r'<p class="(?:dek|art-dek|hub-hero-dek)">(.*?)</p>', h, re.S)
    i = re.search(r'<img\b[^>]*class="hero-img"[^>]*>', h) or re.search(r'(?:art-hero-img-full|hub-hero-img)"[^>]*>\s*<img\b[^>]*>', h)
    dek = text(d[1]) if d else ""
    if len(dek) > 170: dek = dek[:170].rsplit(" ", 1)[0] + "…"
    return dict(href=href, title=text(t[1]) if t else href, dek=dek, src=attr(i[0], "src") if i else "", tag="")


def tile_src(src):
    """Use the small tile of a photo that already has one, not its full-width hero."""
    m = re.match(r"(https://panamaspot\.com)?(/images/v2/.*)-hero-\d+\.webp$", src)
    if m and (P / (m[2].lstrip("/") + "-tile.webp")).exists(): return f"{m[1] or ''}{m[2]}-tile.webp"
    return src


def related(s, prose, rel, lang, hub):
    """Three related guides with their full titles and descriptions, plus the destination hub when there is one."""
    pre = "/es/articles/" if lang == "es" else "/articles/"
    hub_card = meta_of(hub) if hub.startswith(pre) else None
    if hub_card: hub_card["is_hub"] = True
    skip = {"/" + rel, hub}
    need = 3 if hub_card else 4
    hub_links = re.findall(r'href="(' + re.escape(pre) + r'[^"#]+)"', (P / (hub.lstrip("/") + ".html")).read_text(errors="ignore")) if hub_card else []
    fallback = {"en": ["/articles/best-time-to-visit-panama", "/articles/is-panama-safe", "/articles/panama-city", "/articles/bocas-del-toro"], "es": ["/es/articles/panama-city", "/es/articles/boquete", "/es/articles/el-valle-de-anton", "/es/articles/que-hacer-en-ciudad-de-panama"]}[lang]
    cards = []
    for href in [c["href"] for c in card_data(s)] + re.findall(r'href="(' + re.escape(pre) + r'[^"#]+)"', prose) + hub_links + fallback:
        if len(cards) >= need: break
        if href in skip: continue
        skip.add(href); d = meta_of(href)
        if d and d["src"] and d["dek"]: cards.append(d)
    return cards + ([hub_card] if hub_card else [])


def explore_html(cards, hub, t):
    """Top middle holds the hub: it only needs its name. The guides get the room for a full title and description."""
    guides = [c for c in cards if not c.get("is_hub")]
    hubs = [c for c in cards if c.get("is_hub")]
    a, b, g, d = (guides[0], hubs[0], guides[1], guides[2]) if hubs else cards[:4]
    pills = lambda: f'<span class="pills"><span class="chip glass">{t["guide"]}</span></span>'
    c = lambda x: f'<span class="c"><i class="dot"></i>{t["guide"]}</span><h3>{x["title"]}</h3>'
    im = lambda x: f'<img alt="" loading="lazy" src="{tile_src(x["src"])}"/>'
    out = (f'<a class="bt t-a" href="{a["href"]}"><span class="ph">{im(a)}{pills()}</span><span class="tx">{c(a)}<p>{a["dek"]}</p></span></a>'
           f'<a class="bt t-b" href="{b["href"]}"><span class="ph">{im(b)}</span><span class="tx">{c(b)}</span></a>'
           f'<a class="bt t-c" href="{g["href"]}"><span class="tx">{c(g)}<p>{g["dek"]}</p></span><span class="go">→</span></a>'
           f'<a class="bt t-d" href="{d["href"]}"><span class="tx">{c(d)}<p class="lead">{d["dek"]}</p><span class="more">{t["more"]} <i>→</i></span></span><span class="ph">{im(d)}{pills()}</span></a>')
    e = t["explore"]
    return f'<section class="wrap band"><div class="explore"><div class="band-h"><div><span class="lbl">{e[0]}</span><h2>{e[1]}</h2></div><a href="{hub}">{e[2]}</a></div><div class="bx">{out}</div></div></section>'


def donor_parts(lang):
    h = (P / (DONOR[lang] + ".html")).read_text()
    head = h[:h.index("</head>")]
    style = re.search(r"<style[^>]*>.*?</style>", head, re.S)[0]
    nav = find_block(h, '<div class="wrap nav">')
    foot = h[h.index('<footer class="foot">'):h.index("</footer>") + 9]
    js = re.search(r"<script>\s*\(function \(\) \{.*?</script>", h, re.S)[0]
    pm = re.search(r'<div class="pm">(<svg.*?</svg>)', h, re.S)[1]
    font = '<link rel="preload" as="font" type="font/woff2" href="/fonts/GildaC-650.woff2" crossorigin>\n<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&display=swap">'
    return dict(style=style, nav=nav, foot=foot, js=js, pm=pm, font=font)


DONORS = {}


def convert(rel):
    s = old_html(rel)
    lang = "es" if rel.startswith("es/") else "en"
    t = T[lang]
    d = DONORS.setdefault(lang, donor_parts(lang))
    s = apply_prices(s)
    ld = re.findall(r'<script type="application/ld\+json">.*?</script>', s, re.S)
    head = s[:s.index("</head>")]
    head = re.sub(r'<script type="application/ld\+json">.*?</script>|<style\b.*?</style>|<!--.*?-->', "", head, flags=re.S)
    head = re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>|<link\b[^>]*as="(?:font|style)"[^>]*>|<meta content="" name="next-size-adjust"/>|<link\b[^>]*rel="preconnect"[^>]*>|<link\b[^>]*rel="dns-prefetch"[^>]*>|<script\b.*?</script>', "", head, flags=re.S)
    head = head.split("<head>", 1)[1]
    b = s[s.index("<body"):]
    b = re.sub(r"<style\b.*?</style>", "", b, flags=re.S)
    b = re.sub(r"<!--EVB-CTA:\w+-->.*?<!--/EVB-CTA:\w+-->", "", b, flags=re.S)
    # hero
    hero = re.search(r'art-hero-img-full"[^>]*>\s*(<img\b[^>]*>)', b, re.S)[1]
    hero = clean_img(hero, "hero-img", keep_lazy=False).replace("<img ", '<img fetchpriority="high" loading="eager" decoding="async" ', 1)
    chips = "".join(f'<span class="chip glass">{c}</span>' for c in re.findall(r'class="art-hero-tag">(.*?)</span>', b, re.S))
    # EN/ES switch: the same guide in the other language when there is one, otherwise that language's homepage
    twin = {}
    for tag in re.findall(r"<link\b[^>]*hreflang=[^>]*>", head):
        m = re.search(r'hreflang="(en|es)"', tag); u = re.search(r'href="https://panamaspot\.com(/[^"]*)"', tag)
        if m and u: twin[m[1]] = u[1]
    en = "/" + rel if lang == "en" else twin.get("en", "/")
    es = "/" + rel if lang == "es" else twin.get("es", "/es")
    nav = d["nav"]
    nav = re.sub(r'<span class="lang glass">.*?</span>', f'<span class="lang glass"><a{" class=" + chr(34) + "on" + chr(34) if lang == "en" else ""} href="{en}" hreflang="en">EN</a><a{" class=" + chr(34) + "on" + chr(34) if lang == "es" else ""} href="{es}" hreflang="es">ES</a></span>', nav, flags=re.S)
    nav = re.sub(r'<span class="search glass">(.*?)</span></span>', lambda m: f'<a class="search glass" href="{t["home"]}" data-search aria-haspopup="dialog">{m[1]}</span></a>', nav, flags=re.S)
    # head block
    crumbs = re.search(r'<nav aria-label="Breadcrumb" class="breadcrumb">(.*?)</nav>', b, re.S)[1]
    links = re.findall(r'<a href="([^"]+)">(.*?)</a>', crumbs)
    cur = text(re.search(r'aria-current="page">(.*?)</span>', crumbs, re.S)[1])
    cur = (cur[:34].rsplit(" ", 1)[0] + "…") if len(cur) > 36 else cur
    crumb = "<i></i>".join(f'<a href="{u}">{n}</a>' for u, n in links) + f"<i></i><b>{html.escape(cur, quote=False)}</b>"
    hub = links[1][0] if len(links) > 1 else ("/es" if lang == "es" else "/")
    place = text(links[1][1]).upper() if len(links) > 1 else t["place"]
    h1 = re.search(r'<h1 class="art-title">(.*?)</h1>', b, re.S)[1]
    dek = re.search(r'<p class="art-dek">(.*?)</p>', b, re.S)[1]
    mins = re.search(r'byline-stats"><span><strong>(.*?)</strong>\s*(.*?)</span>', b, re.S)
    read = f"{mins[1]} {mins[2]}".strip() if mins else ""
    if lang == "es": read = read.replace("min read", "min de lectura")
    mod = re.search(r'content="(\d{4})-(\d\d)-\d\d" property="article:modified_time"', s) or re.search(r'property="article:modified_time" content="(\d{4})-(\d\d)', s)
    upd_month = f'{t["months"][int(mod[2]) - 1]} {mod[1]}' if lang == "es" else f'{t["months"][int(mod[2]) - 1]} {mod[1]}'
    fact = re.search(r'<aside class="fact-card">(.*?)</aside>', b, re.S)[1]
    rows = re.findall(r'<div class="fact-row"><span class="k">(.*?)</span><span class="v">(.*?)</span></div>', fact, re.S)
    best = next(((k, v) for k, v in rows if re.search(r"best|mejor|season|temporada|época", k, re.I)), None)
    # always four facts; "Language" is what the EN/ES switch at the top is for
    keep = [(k, v) for k, v in rows if not re.fullmatch(r"language|idioma", text(k), re.I)][:4]
    cells = "".join(glance_cell(k, v) for k, v in keep)
    rates = []
    for lab, bar in re.findall(r'<span class="lbl">(.*?)</span><span class="bar">(.*?)</span>', fact, re.S):
        n = bar.count('class="on"'); tot = bar.count("<i ")
        rates.append(f'<span class="rate">{lab} <span class="rd" aria-label="{n} {t["of"]} {tot}">' + "<i></i>" * n + '<i class="o"></i>' * (tot - n) + "</span></span>")
    glance = f'<aside class="glance" aria-label="{t["glance"]}"><h2>{t["glance"]}</h2><div class="gg">{cells}</div>' + (f'<div class="rates">{"".join(rates)}</div>' if rates else "") + "</aside>"
    # prose
    prose = re.search(r'<article class="prose[^"]*"[^>]*>(.*)</article>', b[:b.index("</article>") + 10], re.S)[1]
    toc = re.search(r'<aside class="toc">(.*?)</aside>', b, re.S)[1]
    labels = {i: text(n) for i, n in re.findall(r'<a href="#([^"]+)"[^>]*><span class="n">.*?</span><span>(.*?)</span>', toc, re.S)}
    prose = funnel_to_whatsapp(convert_tables(convert_callouts(convert_figures(prose))), lang)
    intro, secs = split_sections(prose, labels)
    after = b[b.index("</article>"):]
    # highlights
    hl = re.search(r'<span class="eyebrow">([^<]*)</span><h2>([^<]*)</h2></div><div class="art-highlights-grid">', after)
    high = ""; know = []
    if hl:
        g = find_block(after, '<div class="art-highlights-grid">')
        cs = re.findall(r'<div class="art-highlight-card">.*?<div class="stat">(.*?)</div><h3>(.*?)</h3><p>(.*?)</p></div>', g, re.S)
        high = f'<section class="sec" id="short-version"><span class="lbl">{hl[1]}</span><h2>{hl[2]}</h2><div class="prices p3">' + "".join(f'<div><h3 class="k">{h3}</h3><b>{st}</b><p>{p}</p></div>' for st, h3, p in cs) + "</div></section>"
        know = [f"{text(st)}: {text(h3)}" for st, h3, _ in cs]
    # FAQ
    fq = re.search(r'<span class="eyebrow">([^<]*)</span><h2>([^<]*)</h2></div><div class="faq"', after)
    faq = ""
    if fq:
        g = find_block(after, '<div class="faq"')
        items = []
        for m in re.finditer(r'<button[^>]*class="faq-q"[^>]*>(.*?)</button><div class="faq-a">', g, re.S):
            a, e = block(g, m.end() - len('<div class="faq-a">'))
            ans = funnel_to_whatsapp(g[m.end():e - 6].strip(), lang)
            items.append(f"<div><h3>{m[1]}</h3>" + (ans if re.search(r"<(p|ul|ol)\b", ans) else f"<p>{ans}</p>") + "</div>")
        faq = f'<section class="sec" id="faq"><span class="lbl">{fq[1]}</span><h2>{fq[2]}</h2><div class="faq">{"".join(items)}</div></section>'
    # photo notes
    refs = ""
    dsc = re.search(r'<section class="img-desc">.*?<h2>(.*?)</h2><p class="id-sub">(.*?)</p><ol>(.*?)</ol>', after, re.S)
    crd = re.search(r'<section class="img-credits"[^>]*>(.*?)</section>', after, re.S)
    if dsc:
        lis = re.sub(r"<li>(.*?)</li>", lambda m: "<li><div>" + m[1].replace('class="id-m"', 'class="src-domain"') + "</div></li>", dsc[3], flags=re.S)
        refs = f'<section class="refs-box" id="sources"><div class="refs img-refs"><h2>{dsc[1]}</h2><p class="intro">{dsc[2]}</p><ul class="src-list">{lis}</ul></div></section>'
    elif crd:
        refs = f'<section class="refs-box" id="sources"><div class="refs img-refs">{crd[1]}</div></section>'
    # toc
    li = "".join(f'<li><a href="#{i}">{n}</a></li>' for i, n in labels.items() if re.search(rf'id="{re.escape(i)}"', secs))
    if faq: li += f'<li><a href="#faq">{t["faq"]}</a></li>'
    if refs: li += f'<li><a href="#sources">{t["photos"]}</a></li>'
    cards = related(after, prose, rel, lang, hub)
    rn = "".join(f'<a class="sf" href="{c["href"]}"><span class="sw"><span class="stamp"><img class="in" alt="" loading="lazy" src="{c["src"]}"/></span></span><span class="sl">{c["title"]} →</span></a>' for c in cards[:2])
    # gallery
    gal = ""
    gh = re.search(r'<span class="eyebrow">([^<]*)</span><h2>([^<]*)</h2></div><div class="art-gallery-grid">', after)
    if gh:
        g = find_block(after, '<div class="art-gallery-grid">')
        figs = []
        for m in re.finditer(r"<figure\b[^>]*>(.*?)</figure>", g, re.S):
            cap = re.search(r"<figcaption\b[^>]*>.*?</figcaption>", m[1], re.S)
            figs.append("<figure>" + clean_img(re.search(r"<img\b[^>]*>", m[1])[0], "ph") + (cap[0] if cap else "") + "</figure>")
        gal = f'<section class="band gband"><div class="wrap band-h"><div><span class="lbl">{gh[1]}</span><h2>{gh[2]}</h2></div></div><div class="gal">{"".join(figs)}</div></section>'
    pm = re.sub(r'(<textPath[^>]*>).*?(</textPath>)', lambda m: f'{m[1]}{place} · PANAM{"Á" if lang == "es" else "A"} · {mod[1]} ·{m[2]}' if place not in ("PANAMA", "PANAMÁ") else f'{m[1]}PANAM{"Á" if lang == "es" else "A"} · {mod[1]} · GUÍA ·{m[2]}' if lang == "es" else f'{m[1]}PANAMA · {mod[1]} · GUIDE ·{m[2]}', d["pm"], flags=re.S)
    know_html = "".join(f"<li>{html.escape(x, quote=False)}</li>" for x in know) or (f"<li>{best[1]}</li>" if best else "")
    page = f"""<!doctype html>
<html lang="{lang}"><head>{head}
{d["font"]}
{d["style"].replace("</style>", EXTRA_CSS + "</style>")}
{"".join(ld)}
</head><body>
<div class="guide-progress" id="prog" aria-hidden="true"></div>
<header class="hero">
  {hero}
  {nav}
  <div class="wrap chips">{chips}</div>
</header>
<section class="head" id="top"><div class="wrap"><div>
  <nav class="crumbs" aria-label="Breadcrumb">{crumb}</nav>
  <h1>{h1}</h1>
  <p class="dek">{dek}</p>
  <div class="byline"><span class="who"><span class="av"><span class="logo"><span class="a">á</span><i class="pd"></i></span></span><span><b>{t["who"]}</b>{t["role"]}</span></span><span>{read}</span><span>{t["upd"]} {upd_month}</span></div>
</div>{glance}</div></section>
<div class="wrap body">
  <aside class="tocl" aria-label="{t["toc"]}"><div class="tocl-in"><nav class="toc"><h2>{t["toc"]}</h2><ol id="toc">{li}</ol></nav><div class="lst"><span class="mh">{t["read"]}</span>{rn}</div></div></aside>
  <article class="article" id="article">
{intro}

{secs}

{high}
{faq}
{refs}
  </article>
  <aside class="rail" aria-label="Guide extras"><div class="rail-in"><div class="pm">{pm}<p><b>{t["upd"]} {upd_month}</b>{t["confirm"]}</p></div><div class="know"><span class="lbl">{t["know"]}</span><ul>{know_html}</ul></div></div></aside>
</div>
{gal}
{explore_html(cards, hub, t)}
{d["foot"]}
{d["js"]}
{SEARCH_TAG}
</body></html>
"""
    return s, page


def main_text(s, new):
    h = s[s.index("<body"):]
    h = re.sub(r"<style\b.*?</style>|<script\b.*?</script>|<svg\b.*?</svg>", " ", h, flags=re.S)
    if new:
        h = re.sub(r"<!--evx:\w+-->.*?<!--/evx-->", " ", h, flags=re.S)
        h = h[h.index('<article class="article"'):h.index("</article>")]
    else:
        h = re.sub(r"<!--EVB-CTA:\w+-->.*?<!--/EVB-CTA:\w+-->", " ", h, flags=re.S)
        h = h[h.index('<article class="prose'):h.index("</article>")] + " ".join(re.findall(r'<div class="art-highlights-grid">.*?</section>|<div class="faq".*?</section>|<section class="img-desc">.*?</section>', h, re.S))
    return [w.lower() for w in re.findall(r"[^\W_]+", html.unescape(re.sub(r"<[^>]+>", " ", h)))]


def head_val(s, pat):
    return sorted(re.findall(pat, s[:s.index("</head>")]))


def check(old, new, rel):
    """Everything Google already knows about the page has to survive. Returns a list of problems."""
    bad = []
    old = apply_prices(old)
    for name, pat in (("title", r"<title>(.*?)</title>"), ("description", r'<meta content="([^"]*)" name="description"'), ("robots", r'<meta content="([^"]*)" name="robots"'),
                      ("canonical", r'<link href="([^"]*)" rel="canonical"'), ("hreflang", r"<link\b[^>]*hreflang=[^>]*>"), ("og", r'<meta content="[^"]*" property="[^"]*"'), ("twitter", r'<meta content="[^"]*" name="twitter:[^"]*"')):
        if head_val(old, pat) != head_val(new, pat): bad.append(name + " changed")
    if sorted(re.findall(r'<script type="application/ld\+json">.*?</script>', old, re.S)) != sorted(re.findall(r'<script type="application/ld\+json">.*?</script>', new[:new.index("</head>")], re.S)): bad.append("schema changed")
    a = re.search(r'<h1 class="art-title">(.*?)</h1>', old, re.S)[1]; b = re.search(r"<h1>(.*?)</h1>", new, re.S)[1]
    if a != b: bad.append("h1 changed")
    op = old[old.index('<article class="prose'):old.index("</article>")]
    op = re.sub(r"<!--EVB-CTA:\w+-->.*?<!--/EVB-CTA:\w+-->", "", op, flags=re.S)
    oh2 = [text(re.sub(r'<span class="num">.*?</span>', "", x, flags=re.S)) for x in re.findall(r"<h2\b[^>]*>(.*?)</h2>", op, re.S)]
    nh2 = [text(x) for x in re.findall(r"<h2\b[^>]*>(.*?)</h2>", new, re.S)]
    miss = [x for x in oh2 if x not in nh2]
    if miss: bad.append(f"h2 lost: {miss[:2]}")
    ids = re.findall(r'<h2 id="([^"]+)"', op)
    lost = [i for i in ids if f'id="{i}"' not in new]
    if lost: bad.append(f"anchors lost: {lost}")
    allids = re.findall(r'\bid="([^"]+)"', new[new.index("<body"):])
    allids = [i for i in allids if i != "pmr"]
    if len(allids) != len(set(allids)): bad.append(f"duplicate ids: {sorted({i for i in allids if allids.count(i) > 1})[:3]}")
    ow, nw = main_text(old, False), main_text(new, True)
    from collections import Counter
    dropped = Counter(ow) - Counter(nw)
    gone = sum(dropped.values())
    if gone > max(25, len(ow) * 0.01): bad.append(f"words lost {gone}/{len(ow)}: {list(dropped)[:10]}")
    lang = "es" if rel.startswith("es/") else "en"
    for href in set(re.findall(r'href="(/(?:es/)?articles/[^"#]+)"', op)):
        if f'href="{href}"' not in new: bad.append("prose link lost: " + href)
    for src in set(re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', op)):
        if f'src="{src}"' not in new: bad.append("photo lost: " + src[:60])
    body = new[new.index("<body"):]; body = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "", body, flags=re.S)
    if "/funnels/" in body: bad.append("funnel link left")
    if len(re.findall(r'class="bt t-[abcd]"', body)) != 4: bad.append("explore does not have 4 cards")
    if len(re.findall(r'<span class="k">', body[body.index('class="gg"'):body.index('class="wrap body"')])) > 4: bad.append("more than 4 glance facts")
    other_lang = "en" if lang == "es" else "es"
    sw = re.search(r'<span class="lang glass">.*?</span>', body, re.S)[0]
    sw_to = re.search(r'href="([^"]+)" hreflang="' + other_lang + '"', sw)[1]
    tw = [re.search(r'href="https://panamaspot\.com(/[^"]*)"', x) for x in re.findall(r"<link\b[^>]*hreflang=[^>]*>", new[:new.index("</head>")]) if f'hreflang="{other_lang}"' in x]
    want = tw[0][1] if tw and tw[0] else ("/es" if other_lang == "es" else "/")
    if sw_to != want: bad.append(f"language switch goes to {sw_to}, should be {want}")
    words = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<!--evx:\w+-->.*?<!--/evx-->", " ", body[:body.index('<footer')], flags=re.S)))
    for sent in re.split(r"(?<=[.!?])\s+", words):
        if re.search(r"E-?Valley", sent):
            amounts = re.findall(r"\$\s?(\d+)", sent)
            if any(a not in ALLOWED_EV for a in amounts) or re.search(r"\$30\b", sent) or re.search(r"audio ?gu|canasta|basket|\block\b|candado|Plaza Paseo|cancel", sent, re.I):
                bad.append("E-Valley fact to check: " + sent.strip()[:110]); break
    pv = None
    for m in re.finditer(r"<h([1-6])\b", body):
        l = int(m[1])
        if pv and l > pv + 1: bad.append(f"heading skip h{pv}->h{l}"); break
        pv = l
    other = r'href="(?:https://panamaspot\.com)?/articles/' if lang == "es" else r'href="(?:https://panamaspot\.com)?/es/articles/'
    cross = [m for m in re.finditer(r"<a\b[^>]*" + other + r'[^>]*>', body) if "hreflang" not in m[0]]
    if cross: bad.append(f"{len(cross)} cross-language links")
    left = re.findall(r'class="[^"]*\b(art-[\w-]+|evb-[\w-]+|imgph|callout|compare|pill|lede|faq-q|faq-a|bento-[\w-]+|fact-[\w-]+|home-[\w-]+|id-m|img-desc[\w-]*)\b', body)
    if left: bad.append(f"old template leftovers: {sorted(set(left))[:6]}")
    if re.search(r"<h[1-6][^>]*>\s*</h[1-6]>|<span class=\"sl\"> →", body): bad.append("empty title")
    if re.search(r'\bstyle="[^"]*(position:absolute|width:100%)', body): bad.append("old inline image layout")
    return bad


def all_old():
    out = []
    for f in sorted(P.glob("articles/*.html")) + sorted(P.glob("es/articles/*.html")):
        rel = str(f.relative_to(P))[:-5]
        try: h = old_html(rel)
        except subprocess.CalledProcessError: continue
        if 'class="article-page' in h: out.append(rel)
    return out


if __name__ == "__main__":
    pages = [a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--page=")]
    dry = "--dry" in sys.argv
    todo = all_old() if dry else pages
    ok = 0; fails = []
    for rel in todo:
        try:
            old, new = convert(rel)
            bad = check(old, new, rel)
        except Exception as e:
            bad = [f"CRASH {type(e).__name__}: {e}"]; new = None
        if bad:
            fails.append((rel, bad)); print("FAIL", rel, "::", " | ".join(bad)[:300])
        else:
            ok += 1
            if not dry: (P / (rel + ".html")).write_text(new); print("wrote", rel)
    print(f"{ok} of {len(todo)} pass" + (" (dry run, nothing written)" if dry else ""))
