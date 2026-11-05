"""Preview of the Boquete hub and the homepage in the new guide template (not linked anywhere, noindex).
Content comes from the live hub and homepage; only the design changes.
  python3 design/hub-home/build_previews.py   ->  public/preview/boquete-hub.html, public/preview/home.html
"""
import html, re, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; P = ROOT / "public"; OUT = P / "preview"; OUT.mkdir(exist_ok=True)
sp = importlib.util.spec_from_file_location("r", ROOT / "scripts/reskin_old_guides.py"); R = importlib.util.module_from_spec(sp); sp.loader.exec_module(R)
sp = importlib.util.spec_from_file_location("b", ROOT / "design/evalley-cta/build.py"); B = importlib.util.module_from_spec(sp); sp.loader.exec_module(B)
sp = importlib.util.spec_from_file_location("roll", ROOT / "scripts/evalley_cta_rollout.py"); ROLL = importlib.util.module_from_spec(sp); sp.loader.exec_module(ROLL)
D = R.donor_parts("en"); SITE = "https://panamaspot.com"
E = lambda s: html.escape(html.unescape(s), quote=False)


def img_of(href):
    """A guide's own hero photo, at tile size when one exists."""
    f = P / (href.lstrip("/") + ".html")
    h = f.read_text(errors="ignore") if f.exists() else ""
    m = re.search(r'<img\b[^>]*class="hero-img"[^>]*>', h)
    if not m: return ""
    src = re.search(r'\bsrc="([^"]+)"', m[0])[1].replace(SITE, "")
    base = re.sub(r"-hero-\d+\.webp$", "", src)
    for v in ("-tile.webp", "-hero-960.webp"):
        if (P / (base + v).lstrip("/")).exists(): return base + v
    return src


def title_of(href):
    f = P / (href.lstrip("/") + ".html"); h = f.read_text(errors="ignore")
    return R.text(re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)[1])


CSS = """
.hx-hero { height: clamp(380px, 46vw, 620px); }
.hx-home { height: min(92vh, 860px); min-height: 620px; }
.hx-home .hx-c { align-self: center; display: grid; justify-items: center; text-align: center; gap: 18px; padding-bottom: 40px; }
.hx-home h1 { font: 650 clamp(52px, 7.4vw, 112px)/.95 var(--serif); color: #fff; letter-spacing: -0.01em; text-shadow: 0 2px 30px rgba(0,0,0,.25); }
.hx-home h1 em { font-style: normal; color: #ff4a4f; }
.hx-home .hx-dek { font-size: clamp(18px, 1.6vw, 22px); line-height: 1.5; color: rgba(255,255,255,.92); max-width: 42ch; text-shadow: 0 1px 14px rgba(0,0,0,.35); }
.hx-home::before { background: linear-gradient(180deg, rgba(3,10,30,.45) 0%, rgba(3,10,30,.08) 34%, rgba(3,10,30,.12) 62%, rgba(3,10,30,.5) 100%); }
a.hx-search { display: flex; align-items: center; gap: 14px; width: min(620px, 100%); padding: 18px 22px; border-radius: 999px; color: #fff; text-decoration: none; font: 500 17px/1.2 var(--sans); margin-top: 8px; }
a.hx-search svg { flex: none; opacity: .9; }
a.hx-search kbd { margin-left: auto; font: 600 12px/1 var(--sans); padding: 6px 9px; border-radius: 8px; background: rgba(255,255,255,.18); }
.hx-quick { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
.hx-quick a { text-decoration: none; }
.hx-sec { padding-block: 72px 0; scroll-margin-top: 20px; }
.hx-sec:last-of-type { padding-bottom: 72px; }
.hx-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.hx-dest { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.hx-d { position: relative; border-radius: 22px; overflow: hidden; aspect-ratio: 3/4; color: #fff; text-decoration: none; isolation: isolate; }
.hx-d img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .7s; z-index: -2; }
.hx-d::after { content: ""; position: absolute; inset: 40% 0 0; background: linear-gradient(180deg, rgba(3,10,30,0), rgba(3,10,30,.7)); z-index: -1; }
.hx-d:hover img { transform: scale(1.04); }
.hx-d .chip { position: absolute; top: 14px; left: 14px; }
.hx-d .ft { position: absolute; left: 18px; right: 18px; bottom: 16px; display: grid; gap: 4px; }
.hx-d b { font: 650 clamp(26px, 2.3vw, 34px)/1 var(--serif); }
.hx-d small { font: 500 14px/1.3 var(--sans); opacity: .88; }
.hx-row { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(250px, 1fr); gap: 16px; overflow-x: auto; padding-bottom: 8px; scroll-snap-type: x mandatory; scrollbar-width: thin; }
.hx-row > * { scroll-snap-align: start; }
.hx-card { display: grid; grid-template-rows: auto 1fr; gap: 4px; padding: 10px; border-radius: 24px; background: var(--beige); box-shadow: inset 0 0 0 1px var(--line); text-decoration: none; color: var(--ink); min-width: 0; }
.hx-card .ph { position: relative; display: block; border-radius: 16px; overflow: hidden; aspect-ratio: 4/3; }
.hx-card .ph img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .6s; }
.hx-card:hover .ph img { transform: scale(1.04); }
.hx-card .ph .chip { position: absolute; left: 10px; bottom: 10px; font-size: 12.5px; padding: 7px 12px; }
.hx-card .tx { display: grid; gap: 8px; align-content: start; padding: 14px 12px 10px; }
.hx-card .c { font: 600 13px/1 var(--sans); color: var(--muted); display: inline-flex; gap: 7px; align-items: center; }
.hx-card h3 { font: 700 19px/1.25 var(--sans); color: var(--navy); letter-spacing: -0.015em; }
.hx-card p { font: 400 15px/1.45 var(--sans); color: var(--body); }
.hx-card .go { font: 600 14px/1 var(--sans); color: var(--ink); display: inline-flex; gap: 8px; align-items: center; margin-top: 4px; }
.hx-card .go i { width: 28px; height: 28px; border-radius: 50%; background: var(--red); color: #fff; display: grid; place-items: center; font-style: normal; }
.hx-acts { display: grid; grid-template-columns: repeat(7, 1fr); gap: 12px; }
.hx-act { position: relative; border-radius: 18px; overflow: hidden; aspect-ratio: 1; color: #fff; text-decoration: none; isolation: isolate; display: grid; align-content: end; padding: 14px; }
.hx-act img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .6s; }
.hx-act::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(3,10,30,0) 40%, rgba(3,10,30,.62)); z-index: -1; }
.hx-act:hover img { transform: scale(1.05); }
.hx-act b { font: 700 16px/1.2 var(--sans); }
.hx-intro { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: clamp(32px, 5vw, 80px); align-items: start; }
.hx-intro p { font-size: clamp(19px, 1.5vw, 21px); line-height: 1.62; color: var(--ink); }
.hx-intro p + p { margin-top: 16px; }
.hf { display: grid; }
.hf > div { padding: 14px 22px; border-top: 1px solid var(--line); display: grid; gap: 4px; }
.hf > div:first-child { border-top: 0; }
.hf .k { font: 600 12.5px/1.2 var(--sans); color: var(--muted); }
.hf .v { font: 500 15px/1.45 var(--sans); color: var(--ink); }
.hx-group { display: grid; grid-template-columns: 340px minmax(0, 1fr); gap: clamp(24px, 4vw, 56px); align-items: start; }
.hx-group .gm { position: sticky; top: 24px; display: grid; gap: 14px; }
.hx-group .gm img { width: 100%; aspect-ratio: 4/3; object-fit: cover; border-radius: 22px; display: block; }
.hx-group h2 { font: 650 clamp(32px, 3vw, 42px)/1.04 var(--serif); }
.hx-group .gm p { font-size: 16px; line-height: 1.55; color: var(--body); }
.hx-list { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.hx-li { display: grid; grid-template-columns: 76px minmax(0, 1fr) auto; gap: 14px; align-items: center; padding: 10px; border-radius: 20px; background: var(--beige); box-shadow: inset 0 0 0 1px var(--line); text-decoration: none; color: var(--ink); transition: background .2s; }
.hx-li:hover { background: var(--beige-2); }
.hx-li img { width: 76px; height: 76px; border-radius: 14px; object-fit: cover; display: block; }
.hx-li b { display: block; font: 700 16.5px/1.25 var(--sans); color: var(--navy); }
.hx-li span { display: block; font-size: 14px; line-height: 1.4; color: var(--muted); margin-top: 3px; }
.hx-li i { width: 30px; height: 30px; border-radius: 50%; background: var(--white); box-shadow: inset 0 0 0 1px var(--line); display: grid; place-items: center; font-style: normal; color: var(--red); }
.hx-rule { border: 0; border-top: 1px solid var(--line); margin: 72px 0 0; }
.hx-idx { columns: 2; column-gap: 40px; list-style: none; padding: 0; counter-reset: i; }
.hx-idx li { break-inside: avoid; border-top: 1px solid var(--line); }
.hx-idx a { display: grid; grid-template-columns: 36px minmax(0, 1fr) auto; gap: 12px; align-items: baseline; padding: 13px 0; text-decoration: none; color: var(--ink); font-weight: 600; font-size: 16px; }
.hx-idx a:hover { color: var(--red); }
.hx-idx .n { font: 600 13px/1 var(--sans); color: var(--muted); }
.hx-idx .cat { font: 500 13px/1 var(--sans); color: var(--muted); }
.hx-es { display: flex; align-items: center; gap: 18px; padding: 22px 24px; border-radius: 22px; background: var(--beige); margin-top: 32px; flex-wrap: wrap; }
.hx-es .bdg { width: 44px; height: 44px; border-radius: 50%; background: var(--navy); color: #fff; display: grid; place-items: center; font: 700 14px/1 var(--sans); }
.hx-es div { flex: 1; min-width: 220px; }
.hx-es b { display: block; color: var(--navy); font-size: 17px; }
.hx-es p { font-size: 15px; color: var(--muted); }
.hx-es a { font-weight: 600; color: var(--ink); text-decoration-color: var(--red); text-decoration-thickness: 2px; text-underline-offset: 5px; }
.hx-quote { display: grid; gap: 12px; max-width: 900px; margin: 0 auto; text-align: center; padding: 8px 0 0; }
.hx-quote blockquote { font: 500 clamp(24px, 2.4vw, 34px)/1.35 var(--serif); color: var(--navy); }
.hx-quote figcaption { font-size: 14px; color: var(--muted); }
.hx-new { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 1100px) { .hx-dest { grid-template-columns: repeat(3, 1fr); } .hx-acts { grid-template-columns: repeat(4, 1fr); } .hx-list { grid-template-columns: 1fr; } }
@media (max-width: 900px) { .hx-intro, .hx-group { grid-template-columns: 1fr; } .hx-group .gm { position: static; } .hx-grid, .hx-new { grid-template-columns: 1fr 1fr; } .hx-idx { columns: 1; } }
@media (max-width: 600px) { .hx-dest { grid-template-columns: 1fr 1fr; } .hx-acts { grid-template-columns: repeat(2, 1fr); } .hx-grid, .hx-new { grid-template-columns: 1fr; } .hx-home { min-height: 560px; } a.hx-search { padding: 15px 18px; font-size: 15.5px; } a.hx-search kbd { display: none; } .hx-row { grid-auto-columns: 78%; } }
"""
SEARCH_SVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'


def page(title, body, hero_preload, lang="en"):
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title><meta name="robots" content="noindex, nofollow">
<link rel="preload" as="image" href="{hero_preload}" fetchpriority="high"/>
{D["font"]}
{D["style"].replace("</style>", R.EXTRA_CSS + CSS + "</style>")}
<!--evx:css--><link rel="stylesheet" href="/css/evalley-cta.css"><!--/evx:css-->
</head><body>
{body}
{D["foot"]}
{D["js"].replace('var art = document.getElementById("article")', 'var art = document.getElementById("article") || document.body')}
<script src="/js/search.js" defer></script>
</body></html>
"""


def nav(en, es, lang="en"):
    n = D["nav"]
    n = re.sub(r'<span class="lang glass">.*?</span>', f'<span class="lang glass"><a class="on" href="{en}" hreflang="en">EN</a><a href="{es}" hreflang="es">ES</a></span>', n, flags=re.S)
    return re.sub(r'<span class="search glass">(.*?)</span></span>', lambda m: f'<a class="search glass" href="/#cat-regions" data-search aria-haspopup="dialog">{m[1]}</span></a>', n, flags=re.S)


def card(href, title, desc="", chip="", label="Guide", more=False):
    im = img_of(href)
    ph = f'<span class="ph"><img alt="" loading="lazy" src="{im}"/>' + (f'<span class="chip glass">{E(chip)}</span>' if chip else "") + "</span>"
    return (f'<a class="hx-card" href="{href}">{ph}<span class="tx"><span class="c"><i class="dot"></i>{label}</span><h3>{E(title)}</h3>'
            + (f"<p>{E(desc)}</p>" if desc else "") + ('<span class="go">Read the guide <i>→</i></span>' if more else "") + "</span></a>")


# ---------------- Boquete hub ----------------
h = (P / "articles/boquete.html").read_text()
b = h[h.index("<body"):]
dek = re.search(r'<p class="hub-hero-dek">(.*?)</p>', b, re.S)[1]
pills = re.findall(r'<span class="hub-pill">(.*?)</span>', b)
leads = re.findall(r'<p class="hub-lead">(.*?)</p>', b, re.S)
facts = re.findall(r'<div class="hub-fact"><dt>(.*?)</dt><dd>(.*?)</dd></div>', b, re.S)
start = re.findall(r'<a class="hub-card" href="([^"]+)">.*?<h3>(.*?)</h3><p>(.*?)</p>', b, re.S)
s_head = re.search(r'<p class="hub-eyebrow">Start here</p>\s*<h2 class="hub-h2">(.*?)</h2>\s*<p class="hub-lead[^"]*">(.*?)</p>', b, re.S)
groups = []
for g in re.findall(r'<div class="hub-group">(.*?)</ul>', b, re.S):
    im = re.search(r'<img src="([^"]+)"[^>]*alt="([^"]*)"', g)
    groups.append(dict(img=im[1], alt=im[2], h2=re.search(r"<h2>(.*?)</h2>", g, re.S)[1], blurb=re.search(r'<p class="hub-group-blurb">(.*?)</p>', g, re.S)[1],
                       items=re.findall(r'<a href="([^"]+)"><span class="n">(.*?)</span><span class="d">(.*?)</span>', g, re.S)))
idx = re.findall(r'<li><a href="([^"]+)"><span class="num">(\d+)</span><span class="ttl">(.*?)</span><span class="cat">(.*?)</span>', b, re.S)
idx_h = re.search(r'<p class="hub-eyebrow">(The full library)</p>\s*<h2 class="hub-h2">(.*?)</h2>', b, re.S)
es_t = re.search(r'<p class="hub-lang-t">(.*?)</p><p class="hub-lang-d">(.*?)</p>', b, re.S)
HERO = "/images/v2/aerial-view-of-boquete-panama-ed675378-hero"
cta = B.blocks("boquete-en")
group_html = ""
for i, g in enumerate(groups):
    rows = "".join(f'<a class="hx-li" href="{u}"><img alt="" loading="lazy" src="{img_of(u)}"/><span><b>{E(n)}</b><span>{E(d)}</span></span><i>→</i></a>' for u, n, d in g["items"])
    group_html += (f'<section class="wrap hx-sec"><div class="hx-group"><div class="gm"><span class="lbl">{len(g["items"])} guides</span>'
                   f'<h2>{g["h2"]}</h2><p>{g["blurb"]}</p><img alt="{html.escape(html.unescape(g["alt"]))}" loading="lazy" src="{g["img"]}"/></div><div class="hx-list">{rows}</div></div></section>')
    if i == 1: group_html += f'<div class="wrap hx-sec">{cta["banner"]}</div>'
gal = "".join(f'<figure><img class="ph" alt="{html.escape(html.unescape(g["alt"]))}" loading="lazy" src="{g["img"]}"/><figcaption>{E(g["alt"])}</figcaption></figure>' for g in groups[:5])
hub = f"""<div class="guide-progress" id="prog" aria-hidden="true"></div>
<header class="hero hx-hero">
  <img class="hero-img" alt="Aerial view of Boquete town in its river valley, with green hills on every side." fetchpriority="high" src="{HERO}-1920.webp" srcset="{HERO}-960.webp 960w, {HERO}-1280.webp 1280w, {HERO}-1920.webp 1920w" sizes="100vw" style="object-position:center 55%"/>
  {nav("/preview/boquete-hub.html", "/es/articles/boquete")}
  <div class="wrap chips">{"".join(f'<span class="chip glass">{E(p)}</span>' for p in pills)}</div>
</header>
<section class="head" id="top"><div class="wrap"><div>
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><i></i><b>Boquete</b></nav>
  <h1>Boquete</h1>
  <p class="dek">{dek}</p>
  <div class="byline"><span class="who"><span class="av"><span class="logo"><span class="a">á</span><i class="pd"></i></span></span><span><b>Panama Spot editors</b>Destination guide</span></span><span>{len(idx)} guides</span></div>
</div><aside class="glance" aria-label="At a glance"><h2>At a glance <span><i class="dot"></i>Chiriquí highlands</span></h2><div class="hf">{"".join(f'<div><span class="k">{k}</span><span class="v">{v}</span></div>' for k, v in facts)}</div></aside></div></section>
<section class="wrap hx-sec"><div class="hx-intro"><div>{"".join(f"<p>{l}</p>" for l in leads[:2])}</div><div></div></div></section>
<section class="wrap hx-sec"><div class="band-h"><div><span class="lbl">Start here</span><h2>{s_head[1]}</h2><p class="band-sub">{s_head[2]}</p></div></div>
<div class="hx-grid">{"".join(card(u, R.text(t), R.text(d), more=True) for u, t, d in start)}</div></section>
{group_html}
<section class="band gband hx-sec"><div class="wrap band-h"><div><span class="lbl">In pictures</span><h2>Boquete in pictures</h2></div></div><div class="gal">{gal}</div></section>
<section class="wrap hx-sec"><div class="band-h"><div><span class="lbl">{idx_h[1]}</span><h2>{idx_h[2]}</h2></div><span class="band-sub">{len(idx)} guides</span></div>
<ol class="hx-idx">{"".join(f'<li><a href="{u}"><span class="n">{n}</span><span>{t}</span><span class="cat">{c}</span></a></li>' for u, n, t, c in idx)}</ol>
<div class="hx-es"><span class="bdg">ES</span><div><b>{es_t[1]}</b><p>{es_t[2]}</p></div><a href="/es/articles/boquete">Ver en español →</a></div></section>
<section class="wrap hx-sec">{cta["closer"]}</section>
{ROLL.JS_M[0]}{ROLL.TRACK}{ROLL.JS_M[1]}
"""
(OUT / "boquete-hub.html").write_text(page("Preview: Boquete hub", hub, f"{HERO}-1280.webp"))

# ---------------- Homepage ----------------
src = (ROOT / "src/app/page.tsx").read_text()
def cards_of(name):
    blk = re.search(r"const " + name + r": Card\[\] = \[(.*?)\];", src, re.S)[1]
    out = []
    for m in re.finditer(r'\{ title: "([^"]+)", tag: "([^"]+)",.*?href: ([A-Z_]+|"[^"]+") \}', blk):
        href = m[3].strip('"') if m[3].startswith('"') else re.search(r"const " + m[3] + r' = "([^"]+)"', src)[1]
        out.append((m[1], m[2], href))
    return out
H = "/images/v2/playa-blanca-saboga-hero"
dest = [("Panama City", "Capital and canal", "/articles/panama-city"), ("Boquete", "Coffee highlands", "/articles/boquete"),
        ("El Valle de Antón", "Volcanic crater", "/articles/el-valle-de-anton"), ("Bocas del Toro", "Caribbean islands", "/articles/bocas-del-toro"),
        ("San Blas", "Guna Yala", "/articles/san-blas-islands-panama-guna-yala-guide")]
def dest_img(href):
    f = re.search(r'<a class="fc" href="' + re.escape(href) + r'"><img class="ph"[^>]*src="([^"]+)"', D["foot"])
    return f[1].replace(SITE, "") if f else img_of(href)
def count(href):
    f = P / (href.lstrip("/") + ".html"); t = f.read_text(errors="ignore")
    return len(set(re.findall(r'href="(/articles/[^"#]+)"', t[t.find("<body"):t.find("<footer")])))
acts = cards_of("ACTIVITIES")
act_img = {"Hiking & Trails": "/articles/hikes-in-boquete", "Wildlife & Birding": "/articles/birding-el-valle-de-anton-trails-lodges-season", "Surf & Dive": "/articles/panama-surf-camps",
           "Food & Coffee": "/articles/geisha-coffee-boquete-where-to-taste", "Eco-tourism": "/articles/finca-lerida-los-quetzales-trail-birdwatching-boquete", "Cities & Culture": "/articles/casco-viejo-panama-walking-guide", "Islands & Beaches": "/articles/san-blas-islands-panama-guna-yala-guide"}
rows = ""
for name, h2, allhref in [("PANAMA_CITY_GUIDES", "Explore Panama City", "/articles/panama-city"), ("BOQUETE_GUIDES", "Explore Boquete", "/articles/boquete"), ("EL_VALLE_GUIDES", "Explore El Valle de Antón", "/articles/el-valle-de-anton")]:
    cs = cards_of(name)
    rows += (f'<section class="wrap hx-sec"><div class="band-h"><div><span class="lbl">Destination</span><h2>{h2}</h2></div><a href="{allhref}">All {h2.replace("Explore ", "")} guides →</a></div>'
             f'<div class="hx-row">{"".join(card(u, t, chip=g) for t, g, u in cs)}</div></section>')
feat = [("/articles/bocas-del-toro", "Caribbean", "Bocas del Toro — nine islands, slow boats, sloths", "Surfers’ capital of the Caribbean coast, Afro-Antillean kitchens, and the country’s easiest place to wake up on the water."),
        ("/articles/panama-city", "Capital", "Panama City", ""),
        ("/articles/el-valle-de-anton", "Highlands", "El Valle de Antón — a town inside an extinct volcano.", ""),
        ("/articles/boquete", "Highlands", "Boquete — cloud forest, coffee, Volcán Barú", "The highland town that runs on coffee, rivers, and fog — plus the country’s best day hikes from town.")]
a, b2, c, d = feat
bx = (f'<a class="bt t-a" href="{a[0]}"><span class="ph"><img alt="" loading="lazy" src="{dest_img(a[0])}"/><span class="pills"><span class="chip glass">{a[1]}</span></span></span><span class="tx"><span class="c"><i class="dot"></i>Field report</span><h3>{a[2]}</h3><p>{a[3]}</p></span></a>'
      f'<a class="bt t-b" href="{b2[0]}"><span class="ph"><img alt="" loading="lazy" src="{dest_img(b2[0])}"/></span><span class="tx"><span class="c"><i class="dot"></i>{b2[1]}</span><h3>{b2[2]}</h3></span></a>'
      f'<a class="bt t-c" href="{c[0]}"><span class="tx"><span class="c"><i class="dot"></i>{c[1]}</span><h3>{c[2]}</h3></span><span class="go">→</span></a>'
      f'<a class="bt t-d" href="{d[0]}"><span class="tx"><span class="c"><i class="dot"></i>{d[1]}</span><h3>{d[2]}</h3><p class="lead">{d[3]}</p><span class="more">Read the guide <i>→</i></span></span><span class="ph"><img alt="" loading="lazy" src="{dest_img(d[0])}"/></span></a>')
new = ["/articles/geisha-coffee-boquete-where-to-taste", "/articles/chorro-las-mozas-swimming-falls-el-valle", "/articles/san-blas-tours-from-panama-city",
       "/articles/playa-venao-panama", "/articles/panama-canal-boat-tours", "/articles/el-pianista-trail-boquete"]
def dek_of(href):
    t = (P / (href.lstrip("/") + ".html")).read_text(errors="ignore"); m = re.search(r'<p class="dek">(.*?)</p>', t, re.S); s = R.text(m[1]) if m else ""
    return s if len(s) < 150 else s[:150].rsplit(" ", 1)[0] + "…"
home = f"""<div class="guide-progress" id="prog" aria-hidden="true"></div>
<header class="hero hx-home">
  <img class="hero-img" alt="Palm trees lean over the sand at Playa Blanca on Isla Saboga, in the Pearl Islands." fetchpriority="high" src="{H}-1920.webp" srcset="{H}-960.webp 960w, {H}-1280.webp 1280w, {H}-1920.webp 1920w" sizes="100vw" style="object-position:center 62%"/>
  {nav("/preview/home.html", "/es")}
  <div class="wrap hx-c">
    <span class="chip glass">Independent travel guides</span>
    <h1>Find your <em>spot</em><br>in Panamá.</h1>
    <p class="hx-dek">Beaches, cloud forests, islands and cities across two coasts, written by people who live here.</p>
    <a class="hx-search glass" href="/#cat-regions" data-search aria-haspopup="dialog">{SEARCH_SVG}<span>Search guides: waterfalls, coffee, Bocas…</span><kbd>⌘K</kbd></a>
    <div class="hx-quick">{"".join(f'<a class="chip glass" href="{u}">{n}</a>' for n, _, u in dest)}</div>
  </div>
</header>
<section class="wrap hx-sec" id="cat-regions"><div class="band-h"><div><span class="lbl">Destinations</span><h2>Where in Panama?</h2></div><a href="/articles/best-time-to-visit-panama">Plan your trip →</a></div>
<div class="hx-dest">{"".join(f'<a class="hx-d" href="{u}"><img alt="" loading="lazy" src="{dest_img(u)}"/><span class="chip glass">{count(u)} guides</span><span class="ft"><b>{n}</b><small>{s}</small></span></a>' for n, s, u in dest)}</div></section>
<section class="wrap hx-sec" id="cat-activities"><div class="band-h"><div><span class="lbl">Activities</span><h2>What will you do?</h2></div></div>
<div class="hx-acts">{"".join(f'<a class="hx-act" href="{u}"><img alt="" loading="lazy" src="{img_of(act_img.get(html.unescape(t), u))}"/><b>{E(t)}</b></a>' for t, g, u in acts)}</div></section>
<section class="wrap hx-sec"><div class="explore"><div class="band-h"><div><span class="lbl">Field reports from the ground</span><h2>Seven Panamas, one isthmus.</h2></div><a href="/#cat-regions">All destinations →</a></div><div class="bx">{bx}</div></div></section>
<section class="wrap hx-sec"><figure class="hx-quote"><blockquote>We don’t have one country here. We have a coast that faces Cuba, a coast that faces Ecuador, and a mountain range between them that hides whatever it wants to hide.</blockquote><figcaption>— Almirante, Bocas del Toro</figcaption></figure></section>
<section class="wrap hx-sec"><div class="band-h"><div><span class="lbl">New on Panama Spot</span><h2>Fresh guides</h2></div></div>
<div class="hx-new">{"".join(card(u, title_of(u), dek_of(u), more=True) for u in new)}</div></section>
{rows}
"""
(OUT / "home.html").write_text(page("Preview: Panama Spot homepage", home, f"{H}-1280.webp"))
print("wrote", OUT / "boquete-hub.html", OUT / "home.html")
