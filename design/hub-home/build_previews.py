"""Builds the live homepage (EN + ES) and the five destination hubs in the guide template.

  python3 design/hub-home/build_previews.py
    -> public/articles/{boquete,el-valle-de-anton,panama-city,bocas-del-toro,san-blas}.html
       public/es/articles/{boquete,el-valle-de-anton,panama-city}.html
       site-pages/index.html, site-pages/es.html  (scripts/build-static.mjs swaps these in for the Next homepage
                                                   and keeps the Next page's title, meta, canonical, hreflang and JSON-LD)

Hub content (guide lists, intro, blurbs) and each hub's <head> SEO tags come from the old hub pages, kept in
design/hub-home/source/ (the hubs in public/ are this script's output, so they can't be its input).
The header (menus, search, EN/ES switch) comes from scripts/site_menu.py and config/site-menu.json.
"""
import html, re, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; P = ROOT / "public"; HUBSRC = ROOT / "design/hub-home/source"; HOME_OUT = ROOT / "site-pages"; HOME_OUT.mkdir(exist_ok=True)
def srcf(href):
    """The source HTML for a page: the old hub when it is one of the rebuilt hubs, otherwise the live page."""
    rel = href.lstrip("/"); s = HUBSRC / f"{rel}.html"
    return s if s.exists() else P / f"{rel}.html"
sp = importlib.util.spec_from_file_location("r", ROOT / "scripts/reskin_old_guides.py"); R = importlib.util.module_from_spec(sp); sp.loader.exec_module(R)
sp = importlib.util.spec_from_file_location("b", ROOT / "design/evalley-cta/build.py"); B = importlib.util.module_from_spec(sp); sp.loader.exec_module(B)
sp = importlib.util.spec_from_file_location("roll", ROOT / "scripts/evalley_cta_rollout.py"); ROLL = importlib.util.module_from_spec(sp); sp.loader.exec_module(ROLL)
sp = importlib.util.spec_from_file_location("sm", ROOT / "scripts/site_menu.py"); SM = importlib.util.module_from_spec(sp); sp.loader.exec_module(SM)
# preview addresses used while designing -> the real ones
URLMAP = {"/preview/home-es.html": "/es", "/preview/home.html": "/",
          "/preview/boquete-hub-es.html": "/es/articles/boquete", "/preview/boquete-hub.html": "/articles/boquete",
          "/preview/el-valle-hub-es.html": "/es/articles/el-valle-de-anton", "/preview/el-valle-hub.html": "/articles/el-valle-de-anton",
          "/preview/panama-city-hub-es.html": "/es/articles/panama-city", "/preview/panama-city-hub.html": "/articles/panama-city",
          "/preview/bocas-hub.html": "/articles/bocas-del-toro", "/preview/san-blas-hub.html": "/articles/san-blas"}
def finalize(h):
    for a, b in URLMAP.items(): h = h.replace(f'"{a}"', f'"{b}"')
    assert "/preview/" not in h, "a preview link survived"
    return h
D = R.donor_parts("en"); SITE = "https://panamaspot.com"
E = lambda s: html.escape(html.unescape(s), quote=False)


def img_of(href):
    """A guide's own hero photo, at tile size when one exists."""
    f = srcf(href)
    h = f.read_text(errors="ignore") if f.exists() else ""
    m = re.search(r'<img\b[^>]*class="hero-img"[^>]*>', h) or re.search(r'hub-hero-img"><img\b[^>]*>', h)
    if not m: return ""
    src = re.search(r'\bsrc="([^"]+)"', m[0])[1].replace(SITE, "")
    base = re.sub(r"-hero-\d+\.webp$", "", src)
    for v in ("-tile.webp", "-hero-960.webp"):
        if (P / (base + v).lstrip("/")).exists(): return base + v
    return src


def title_of(href):
    f = srcf(href); h = f.read_text(errors="ignore")
    return R.text(re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)[1])


CSS = """
.hx-hero { height: clamp(300px, 27vw, 400px); }
/* homepage hero: the original layout (50vh, min 480px, wordmark bottom-left), new-template details */
.hx-home { height: clamp(468px, 48vh, 560px); min-height: 0; grid-template-rows: auto 1fr; }
.hx-home::before { background: linear-gradient(180deg, rgba(3,10,30,.42) 0%, rgba(3,10,30,0) 34%, rgba(3,10,30,.1) 60%, rgba(3,10,30,.5) 100%); }
.hx-home .hx-c { align-self: end; display: flex; flex-direction: column; align-items: flex-start; gap: 16px; padding-top: 32px; padding-bottom: 54px; }
.hx-home .hx-mark { font: 400 clamp(64px, 11vw, 160px)/.86 var(--serif); letter-spacing: -0.02em; color: #fff; margin: 0; text-shadow: 0 2px 30px rgba(0,0,0,.18); }
.hx-mark .a { color: var(--red); }
.hx-home .hx-mark { margin-bottom: -.09em; }
.hx-mark .pd { display: inline-block; width: .17em; height: .17em; border-radius: 50%; background: var(--red); margin-left: .03em; }
.hx-home .hx-dek { font: 400 16px/1.55 var(--sans); color: rgba(255,255,255,.88); max-width: 56ch; text-shadow: 0 1px 12px rgba(0,0,0,.3); }
a.hx-btn { margin-top: 12px; display: inline-flex; align-items: center; gap: 10px; background: #fff; color: var(--ink); padding: 14px 28px; border-radius: 999px; font: 600 14.5px/1 var(--sans); text-decoration: none; transition: transform .2s; }
a.hx-btn:hover { transform: translateY(-1px); }
.hx-rw { position: relative; }
.hx-row { scrollbar-width: none; }
.hx-row::-webkit-scrollbar { display: none; }
.hx-arr { position: absolute; top: 34%; z-index: 3; width: 42px; height: 42px; border-radius: 50%; border: 0; background: #fff; color: var(--ink); box-shadow: 0 0 0 1px var(--line), 0 6px 18px -8px rgba(8,18,38,.4); font: 600 20px/1 var(--sans); cursor: pointer; display: grid; place-items: center; transition: opacity .2s; }
.hx-arr.l { left: -14px; } .hx-arr.r { right: -14px; }
.hx-arr[disabled] { opacity: 0; pointer-events: none; }
@media (max-width: 700px) { .hx-arr { display: none; } }
/* homepage: rotating hero photos */
.hx-home .hx-rot { opacity: 0; transition: opacity .9s ease; }
.hx-home .hx-rot.on { opacity: 1; }
/* homepage: 7-column destination grids */
.hx-g7 { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 18px 26px; }
/* five places: tiles sized by screen height so the row always fits the first screen, spread across the width */
.hx-g7.g6 { grid-template-columns: repeat(5, minmax(0, 23vh)); justify-content: space-between; column-gap: 26px; }
@media (max-width: 1100px) { .hx-g7.g6 { grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 26px; } }
@media (max-width: 700px) { .hx-g7.g6 { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.hx-t { display: grid; gap: 4px; align-content: start; text-decoration: none; color: var(--ink); min-width: 0; }
.hx-t .ph { display: block; aspect-ratio: 1/1; border-radius: 24px; overflow: hidden; background: var(--beige); }
.hx-t img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .6s; }
.hx-t b { font: 700 15.5px/1.3 var(--sans); color: var(--navy); margin-top: 8px; }
.hx-t .c { font: 600 12px/1 var(--sans); color: var(--muted); display: inline-flex; gap: 6px; align-items: center; }
.hx-bx2 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px; }
.hx-bx2 .hx-card .ph { aspect-ratio: 16/10; }
@media (max-width: 1100px) { .hx-g7 { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 700px) { .hx-g7 { grid-template-columns: repeat(2, minmax(0, 1fr)); } .hx-bx2 { grid-template-columns: 1fr; } }
/* photo tiles with the title on the picture and a red arrow */
.hx-pt { position: relative; display: grid; align-content: end; gap: 6px; aspect-ratio: 4/3; padding: 20px; border-radius: 22px; overflow: hidden; color: #fff; text-decoration: none; isolation: isolate; }
.hx-pt img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .7s; }
.hx-pt::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(3,10,30,0) 35%, rgba(3,10,30,.74)); z-index: -1; }
.hx-pt .lbl { color: #fff; font-size: 13px; }
.hx-pt b { font: 700 clamp(18px, 1.5vw, 22px)/1.2 var(--sans); letter-spacing: -0.015em; padding-right: 56px; }
.hx-pt .ar { position: absolute; right: 18px; bottom: 18px; width: 40px; height: 40px; }
.hx-pt p { font: 400 14px/1.45 var(--sans); color: rgba(255,255,255,.88); padding-right: 56px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
/* red arrow circle; the glyph comes from --arw so the preview can swap styles */
:root { --arw: ARWVAL; }
.ia { display: inline-block; width: 1em; height: 1em; margin-left: .35em; vertical-align: -.14em; background: currentColor; -webkit-mask: var(--arw) center / contain no-repeat; mask: var(--arw) center / contain no-repeat; }
.ar .ia { display: none; }
.ar { display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; background: var(--red); flex: none; font-size: 0; }
.ar::before { content: ""; width: 50%; height: 50%; background: #fff; -webkit-mask: var(--arw) center / contain no-repeat; mask: var(--arw) center / contain no-repeat; }
.arw-pick { position: fixed; left: 16px; bottom: 16px; z-index: 900; display: flex; align-items: center; gap: 6px; padding: 8px 10px; border-radius: 999px; background: rgba(5,24,63,.82); color: #fff; font: 600 12.5px/1 var(--sans); box-shadow: 0 10px 30px rgba(0,0,0,.25); }
.arw-pick button { width: 34px; height: 34px; border-radius: 50%; border: 0; padding: 0; background: rgba(255,255,255,.12); cursor: pointer; display: grid; place-items: center; }
.arw-pick button.on { background: var(--red); }
.arw-pick button i { width: 16px; height: 16px; background: #fff; -webkit-mask: var(--g) center / contain no-repeat; mask: var(--g) center / contain no-repeat; }
/* homepage: one mixed bento */
.hx-mix { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-template-rows: 300px 300px 270px; gap: 16px;
  grid-template-areas: "a b c c" "a d e e" "f f g g"; }
.hx-mix > * { aspect-ratio: auto; min-height: 0; }
.m-a { grid-area: a; } .m-b { grid-area: b; } .m-c { grid-area: c; } .m-d { grid-area: d; } .m-e { grid-area: e; } .m-f { grid-area: f; } .m-g { grid-area: g; }
.hx-navy { position: relative; display: grid; align-content: end; gap: 10px; padding: 26px; border-radius: 22px; background: var(--navy); color: #fff; text-decoration: none; }
.hx-navy .lbl { color: rgba(255,255,255,.75); }
.hx-navy b { font: 700 clamp(20px, 1.7vw, 25px)/1.2 var(--sans); letter-spacing: -0.015em; padding-right: 60px; }
.hx-navy p { font-size: 15px; line-height: 1.5; color: rgba(255,255,255,.75); max-width: 46ch; }
.hx-navy .ar { position: absolute; right: 22px; bottom: 22px; width: 44px; height: 44px; }
.hx-split { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr); gap: 10px; padding: 10px; border-radius: 22px; background: var(--beige); box-shadow: inset 0 0 0 1px var(--line); text-decoration: none; color: var(--ink); }
.hx-split .tx { display: grid; align-content: center; gap: 10px; padding: 14px 12px; }
.hx-split .c { font: 600 13px/1 var(--sans); color: var(--muted); display: inline-flex; gap: 7px; align-items: center; }
.hx-split b { font: 700 21px/1.2 var(--sans); color: var(--navy); }
.hx-split p { font-size: 15px; line-height: 1.5; color: var(--body); }
.hx-split .go { font: 600 14px/1 var(--sans); display: inline-flex; gap: 8px; align-items: center; }
.hx-split .go .ar { width: 28px; height: 28px; }
.hx-split .ph { border-radius: 16px; overflow: hidden; }
.hx-split img { width: 100%; height: 100%; object-fit: cover; display: block; }
@media (max-width: 900px) { .hx-mix { grid-template-columns: 1fr 1fr; grid-template-rows: none; grid-auto-rows: 260px; grid-template-areas: "a a" "b d" "c c" "e e" "f g"; } }
@media (max-width: 560px) { .hx-mix { grid-template-columns: 1fr; grid-template-areas: "a" "b" "d" "c" "e" "f" "g"; } .hx-split { grid-template-columns: 1fr; } .hx-split .ph { min-height: 180px; } }
/* hub: topic index and sections */
.guide-progress { display: none; }
.hb-pills { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 6px; }
.hb-pills a { display: flex; align-items: center; gap: 12px; padding: 6px 18px 6px 6px; border-radius: 999px; background: var(--beige); box-shadow: inset 0 0 0 1px var(--line); color: var(--ink); text-decoration: none; transition: background .2s, color .2s; }
.hb-pills img { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; }
.hb-pills b { display: block; font: 700 15px/1.2 var(--sans); color: inherit; }
.hb-pills small { display: block; font: 500 12.5px/1.2 var(--sans); color: var(--muted); }
.hb-pills a:hover { background: var(--navy); color: #fff; box-shadow: none; }
.hb-pills a:hover small { color: rgba(255,255,255,.7); }
.hx-fr { display: grid; align-content: start; gap: 8px; color: var(--ink); text-decoration: none; min-width: 0; }
.hx-fr .hx-pt { margin-bottom: 4px; }
.hx-fr .c, .hx-fr p { margin-inline: 16px; }
.hx-fr .c { display: inline-flex; align-items: center; gap: 7px; font: 600 13px/1 var(--sans); color: var(--muted); }
.hx-fr p { font-size: 15px; line-height: 1.5; color: var(--body); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
@media (max-width: 760px) { .hb-pills a { padding-right: 14px; } .hb-start .hx-pt { aspect-ratio: 1/1; } }
.hb-start .hx-pt { aspect-ratio: 4/5; }
.hb-start .hx-pt::after { background: linear-gradient(180deg, rgba(3,10,30,0) 38%, rgba(3,10,30,.84)); }
.hb-start .hx-pt p { -webkit-line-clamp: 3; }
@media (max-width: 760px) { .hb-pills a { padding-right: 14px; } .hb-start .hx-pt { aspect-ratio: 1/1; } }
/* hub: icon facts */
.hb-icons { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; margin: 36px auto 0; text-align: center; max-width: 720px; }
.hb-icons > div { display: grid; justify-items: center; gap: 10px; }
.hb-icons .ic { display: grid; place-items: center; }
.hb-icons svg { width: 34px; height: 34px; color: var(--red); }
.hb-icons b { display: block; font: 700 17px/1.15 var(--sans); color: var(--navy); }
.hb-icons span span { display: block; font: 500 12.5px/1.3 var(--sans); color: var(--muted); margin-top: 3px; }
.hb-orient { align-items: center; }
/* hub: topic groups as photo bentos, alternating sides */
.hb-bento { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.hb-bento + .hb-bento { margin-top: 48px; }
.hb-side { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-content: start; }
.hb-bento.flip .hb-feat { order: 2; }
.hb-more { grid-column: 1 / -1; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.hb-g.s2 { grid-column: span 2; } .hb-g.s4 { grid-column: span 4; }
.hb-g.wide { grid-template-columns: minmax(0, 44%) minmax(0, 1fr); grid-template-rows: none; gap: 10px; }
.hb-g.wide .ph { aspect-ratio: auto; position: relative; min-height: 128px; }
.hb-g.wide .ph img { position: absolute; inset: 0; }
.hb-side.fill { grid-auto-rows: 1fr; align-content: stretch; }
.hb-g.wide .tx { align-content: center; }
.hb-feat { position: relative; border-radius: 24px; overflow: hidden; min-height: 380px; color: #fff; display: grid; align-content: end; padding: 26px; isolation: isolate; }
.hb-feat img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; }
.hb-feat::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(3,10,30,0) 30%, rgba(3,10,30,.78)); z-index: -1; }
.hb-feat .lbl { color: #fff; }
.hb-feat h2 { font: 650 clamp(30px, 2.8vw, 42px)/1.04 var(--serif); color: #fff; margin: 10px 0 8px; }
.hb-feat p { font-size: 16px; line-height: 1.5; color: rgba(255,255,255,.9); max-width: 46ch; }
.hb-g { display: grid; grid-template-rows: auto 1fr; gap: 10px; text-decoration: none; color: var(--ink); min-width: 0; }
.hb-g .ph { position: relative; display: block; aspect-ratio: 16/10; border-radius: 16px; overflow: hidden; }
.hb-g img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .6s; }
.hb-g .ph .ar { position: absolute; right: 10px; bottom: 10px; }
.hb-all { display: grid; align-content: end; gap: 6px; padding: 20px; border-radius: 16px; border: 0; background: var(--navy); color: #fff; text-align: left; text-decoration: none; cursor: pointer; position: relative; font: 650 22px/1.15 var(--serif); min-height: 180px; }
.hb-all small { font: 500 13px/1 var(--sans); color: rgba(255,255,255,.7); }
.hb-all .ar { position: absolute; right: 16px; top: 16px; }
.hb-g[hidden] { display: none; }
.hb-g .tx { display: grid; gap: 4px; align-content: start; }
.hb-g b { font: 700 16.5px/1.25 var(--sans); color: var(--navy); }
.hb-g span.d { font-size: 14px; line-height: 1.45; color: var(--muted); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.hb-g i { display: none; }
.hb-cat { padding-top: 104px; }
.hb-cat:first-of-type { padding-top: 8px; }
.hb-cat .num { font: 600 13px/1 var(--sans); color: var(--muted); letter-spacing: .04em; margin-bottom: 14px; display: flex; align-items: center; gap: 12px; }
.hb-cat .num::after { content: ""; flex: 1; height: 1px; background: var(--line); }
.hb-glance .gg { padding-bottom: 14px; }
.hb-start { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.hb-gal { grid-template-rows: repeat(3, clamp(274px, 26.2vw, 424px)); }
.hb-gal figure:nth-child(6) { grid-column: 1 / 2; }
.hb-gal figure:nth-child(7) { grid-column: 2 / 4; }
@media (max-width: 900px) { .hb-start { grid-template-columns: 1fr; } .hb-icons { grid-template-columns: repeat(3, minmax(0, 1fr)); row-gap: 22px; } .hb-gal { grid-template-rows: none; } .hb-gal figure:nth-child(6), .hb-gal figure:nth-child(7) { grid-column: auto; } }
@media (max-width: 1000px) { .hb-bento { grid-template-columns: 1fr; } .hb-bento.flip .hb-feat { order: 0; } .hb-feat { min-height: 320px; } .hb-more { grid-template-columns: 1fr 1fr; } .hb-g.s4 { grid-column: span 2; } .hb-icons { grid-template-columns: 1fr 1fr; } }
@media (max-width: 560px) { .hb-side, .hb-more { grid-template-columns: 1fr; grid-auto-rows: auto; } .hb-g.s2, .hb-g.s4 { grid-column: auto; } }
/* hub: the original layout, restyled */
.hb-hero { height: clamp(370px, calc(38vw - 50px), 490px); grid-template-rows: auto 1fr; }
.hb-hero::before { background: linear-gradient(180deg, rgba(3,10,30,.42) 0%, rgba(3,10,30,0) 26%, rgba(3,10,30,.28) 50%, rgba(3,10,30,.72) 76%, rgba(3,10,30,.94) 100%); }
.hb-hero > .wrap:last-of-type { align-self: end; }
.hb-ev-ph img { object-position: center 34% !important; }
.hb-hero .hb-c { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 34ch); align-items: end; gap: 14px 56px; padding-bottom: 44px; margin: 0; }
.hb-hero .hb-t { display: grid; gap: 14px; }
.hb-hero .hb-c > p { padding-bottom: 6px; }
@media (max-width: 860px) { .hb-hero .hb-c { grid-template-columns: 1fr; } .hb-hero .hb-c > p { padding-bottom: 0; } }
/* Boquete hub: the e-bike banner on the dark spruce green */
.hb-ev-dark.ev-banner { background: var(--ev-deep); }
.hb-ev-dark .ev-p strong { color: #fff; }
.hb-hero .lbl { color: #fff; }
.hb-hero h1 { font: 650 clamp(56px, 6.4vw, 96px)/.95 var(--serif); color: #fff; letter-spacing: -0.01em; }
.hb-hero p { font: 400 clamp(17px, 1.4vw, 20px)/1.55 var(--sans); color: rgba(255,255,255,.92); max-width: 52ch; }
.hb-hero .hb-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
.hb-sec { padding-block: 56px 0; }
.hb-sec.first { padding-top: 48px; }
.hb-sec.last { padding-bottom: 72px; }
.hb-orient { display: grid; grid-template-columns: minmax(0, 1fr) 420px; gap: clamp(32px, 6vw, 96px); align-items: start; }
.hb-orient .lead p { font-size: clamp(18px, 1.4vw, 20px); line-height: 1.65; color: var(--ink); }
.hb-orient .lead p + p { margin-top: 18px; }
.hb-head { display: grid; gap: 10px; margin-bottom: 28px; }
.hb-head h2 { font: 650 clamp(34px, 3.2vw, 46px)/1.04 var(--serif); }
.hb-head p { font-size: 17px; color: var(--body); max-width: 62ch; }
.hb-group { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: clamp(28px, 4vw, 64px); scroll-margin-top: 24px; }
.hb-group + .hb-group { margin-top: 80px; }
.hb-pills + .hb-group { margin-top: 44px; }
.hb-group.flip { grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); }
.hb-group.flip .gi { order: 2; }
.hb-group .gi { position: relative; min-height: 380px; border-radius: 22px; overflow: hidden; }
.hb-group .gi img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
.hb-group .gt { min-width: 0; align-self: center; }
.hb-group h2 { font: 650 clamp(30px, 2.8vw, 40px)/1.05 var(--serif); }
.hb-group .bl { font-size: 17px; line-height: 1.55; color: var(--body); margin: 10px 0 16px; max-width: 56ch; }
.hb-list { list-style: none; padding: 0; margin: 0; }
.hb-list li + li { border-top: 1px solid var(--line); }
.hb-list a { display: grid; grid-template-columns: 68px minmax(0, 1fr) 24px; gap: 16px; align-items: center; padding: 12px 8px 12px 0; text-decoration: none; }
.hb-list img { width: 68px; height: 68px; border-radius: 14px; object-fit: cover; display: block; transition: transform .5s; }
.hb-list .t { display: grid; gap: 2px; min-width: 0; }
.hb-list b { font: 700 16.5px/1.3 var(--sans); color: var(--navy); }
.hb-list .t span { font-size: 14.5px; line-height: 1.45; color: var(--muted); }
.hb-list .go { color: var(--red); justify-self: end; font-size: 18px; }
.hb-list .go .ia { margin: 0; }
@media (max-width: 900px) { .hb-orient, .hb-group, .hb-group.flip { grid-template-columns: 1fr; } .hb-group.flip .gi { order: 0; } .hb-group .gi { min-height: 0; aspect-ratio: 16/10; } .hb-group + .hb-group { margin-top: 56px; } .hb-list a { grid-template-columns: 56px minmax(0, 1fr) 20px; gap: 12px; } .hb-list img { width: 56px; height: 56px; } }
a.hx-search { display: flex; align-items: center; gap: 14px; width: min(620px, 100%); padding: 18px 22px; border-radius: 999px; color: #fff; text-decoration: none; font: 500 17px/1.2 var(--sans); margin-top: 8px; }
a.hx-search svg { flex: none; opacity: .9; }
a.hx-search kbd { margin-left: auto; font: 600 12px/1 var(--sans); padding: 6px 9px; border-radius: 8px; background: rgba(255,255,255,.18); }
.hx-quick { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
.hx-quick a { text-decoration: none; }
.hx-band { background: var(--beige); margin-top: 88px; padding-bottom: 72px; }
.hx-band.bento { margin-top: 64px; padding-bottom: 0; }
.hx-band.bento .hx-sec { padding-bottom: 30px; }
/* the last Explore row: half the space down to the bento (176px -> 88px; phones 128px -> 64px) */
section.hx-sec:has(+ .hx-band.bento) { padding-bottom: 24px; }
@media (max-width: 760px) { section.hx-sec:has(+ .hx-band.bento) { padding-bottom: 8px; } }
/* no zoom on image hover anywhere */
.fc:hover .ph { transform: none; }
.hx-band > .hx-sec:first-child { padding-top: 76px; }
.hx-band + .hx-sec { padding-top: 72px; }
.foot > .f-mid:first-child { padding-top: 56px; }
#cat-regions.hx-sec { padding-top: 34px; }
#cat-regions .band-h { margin-bottom: 18px; }
.hx-sec { padding-block: 112px 0; scroll-margin-top: 20px; }
.hx-sec:last-of-type { padding-bottom: 112px; }
.hx-sec .band-h { margin-bottom: 26px; }
.hx-sec .band-h h2 { font-size: clamp(28px, 2.3vw, 34px); }
@media (max-width: 760px) { .hx-sec { padding-top: 72px; } .hx-sec:last-of-type { padding-bottom: 72px; } .hx-band, .hx-band.bento { margin-top: 56px; padding-bottom: 56px; } .hx-band > .hx-sec:first-child { padding-top: 56px; } .hx-band + .hx-sec, #cat-regions.hx-sec { padding-top: 56px; } .foot > .f-mid:first-child { padding-top: 56px; } .hx-band.bento { padding-bottom: 0; } }
.hx-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.hx-dest { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.hx-dest.hx-do { grid-template-columns: repeat(6, minmax(0, 1fr)); }
.hx-do .hx-d b { display: flex; align-items: center; gap: 8px; }
.hx-do .hx-d b::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--red); flex: none; }
@media (max-width: 1000px) { .hx-dest.hx-do { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 600px) { .hx-dest.hx-do { grid-template-columns: 1fr 1fr; } }
.hx-d { position: relative; border-radius: 22px; overflow: hidden; aspect-ratio: 3/4; color: #fff; text-decoration: none; isolation: isolate; }
.hx-d img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .7s; z-index: -2; }
.hx-d::after { content: ""; position: absolute; inset: 40% 0 0; background: linear-gradient(180deg, rgba(3,10,30,0), rgba(3,10,30,.7)); z-index: -1; }
.hx-d .chip { position: absolute; top: 14px; left: 14px; }
.hx-d .ft { position: absolute; left: 18px; right: 18px; bottom: 16px; display: grid; gap: 4px; }
.hx-d b { font: 650 clamp(20px, 1.6vw, 24px)/1.05 var(--serif); }
.hx-d small { font: 500 14px/1.3 var(--sans); opacity: .88; }
.hx-row { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(250px, 1fr); gap: 16px; overflow-x: auto; padding-bottom: 8px; scroll-snap-type: x mandatory; scrollbar-width: thin; }
.hx-row > * { scroll-snap-align: start; }
.hx-card { display: grid; grid-template-rows: auto 1fr; gap: 4px; padding: 10px; border-radius: 24px; background: var(--beige); box-shadow: inset 0 0 0 1px var(--line); text-decoration: none; color: var(--ink); min-width: 0; }
.hx-card .ph { position: relative; display: block; border-radius: 16px; overflow: hidden; aspect-ratio: 4/3; }
.hx-card .ph img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .6s; }
.hx-card .ph .chip { position: absolute; left: 10px; bottom: 10px; font-size: 12.5px; padding: 7px 12px; }
.hx-card .tx { display: grid; gap: 8px; align-content: start; padding: 14px 12px 10px; }
.hx-card .c { font: 600 13px/1 var(--sans); color: var(--muted); display: inline-flex; gap: 7px; align-items: center; }
.hx-card h3 { font: 700 19px/1.25 var(--sans); color: var(--navy); letter-spacing: -0.015em; }
.hx-card p { font: 400 15px/1.45 var(--sans); color: var(--body); }
.hx-card .go { font: 600 14px/1 var(--sans); color: var(--ink); display: inline-flex; gap: 8px; align-items: center; margin-top: 4px; }
.hx-card .go .ar { width: 28px; height: 28px; }
.hx-acts { display: grid; grid-template-columns: repeat(7, 1fr); gap: 12px; }
.hx-act { position: relative; border-radius: 18px; overflow: hidden; aspect-ratio: 1; color: #fff; text-decoration: none; isolation: isolate; display: grid; align-content: end; padding: 14px; }
.hx-act img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .6s; }
.hx-act::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(3,10,30,0) 40%, rgba(3,10,30,.62)); z-index: -1; }
.hx-act b { font: 700 16px/1.2 var(--sans); display: flex; align-items: center; gap: 8px; }
.hx-act b::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--red); flex: none; }
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
.hx-new { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px 16px; }
@media (max-width: 1100px) { .hx-dest { grid-template-columns: repeat(3, 1fr); } .hx-acts { grid-template-columns: repeat(4, 1fr); } .hx-list { grid-template-columns: 1fr; } }
@media (max-width: 900px) { .hx-intro, .hx-group { grid-template-columns: 1fr; } .hx-group .gm { position: static; } .hx-grid, .hx-new { grid-template-columns: 1fr 1fr; } .hx-idx { columns: 1; } }
@media (max-width: 600px) { .hx-dest { grid-template-columns: 1fr 1fr; } .hx-acts { grid-template-columns: repeat(2, 1fr); } .hx-grid, .hx-new { grid-template-columns: 1fr; } .hx-home { min-height: 560px; } a.hx-search { padding: 15px 18px; font-size: 15.5px; } a.hx-search kbd { display: none; } .hx-row { grid-auto-columns: 78%; } }
"""
SEARCH_SVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'


ARROWS5 = [("Chevron", "<path d='m9 5.5 6.5 6.5L9 18.5'/>", "stroke-width='2.8'"),
           ("Short arrow", "<path d='M5.5 12h12M12.5 6.5 18 12l-5.5 5.5'/>", "stroke-width='2.6'"),
           ("Diagonal", "<path d='M7 17 17 7M8.5 7H17v8.5'/>", "stroke-width='2.6'"),
           ("Solid", "<path d='M8.5 5.5v13L18.5 12z' fill='black' stroke='black'/>", "stroke-width='1.5'"),
           ("Double", "<path d='m6 6 6 6-6 6M12.5 6l6 6-6 6'/>", "stroke-width='2.4'")]
def svg_url(path, sw):
    from urllib.parse import quote
    return 'url("data:image/svg+xml,' + quote(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' {sw} stroke-linecap='round' stroke-linejoin='round'>{path}</svg>", safe="/:= ") + '")'
PICK = ('<div class="arw-pick" aria-label="Preview only: arrow style">Arrow' + "".join(
    f'<button type="button" title="{n}" data-arw=\'{svg_url(p, w)}\'{" class=on" if i == 0 else ""} style=\'--g:{svg_url(p, w)}\'><i></i></button>' for i, (n, p, w) in enumerate(ARROWS5)) + "</div>"
    + """<script>(function(){var b=[].slice.call(document.querySelectorAll("[data-arw]"));function set(i){document.documentElement.style.setProperty("--arw",b[i].dataset.arw);b.forEach(function(x,j){x.classList.toggle("on",i==j)});try{localStorage.setItem("arw",i)}catch(e){}}
b.forEach(function(x,i){x.onclick=function(){set(i)}});try{var k=+localStorage.getItem("arw");if(k>0&&b[k])set(k)}catch(e){}})();</script>""")
ARW = svg_url(ARROWS5[1][1], ARROWS5[1][2])
def arrows(html_text):
    """Every text arrow becomes the same short arrow glyph as the red circles."""
    head, body_ = html_text.split("<body>", 1)
    body_ = re.sub(r"\s*→", '<i class="ia" aria-hidden="true"></i>', body_)
    body_ = body_.replace('<span class="ar"><i class="ia" aria-hidden="true"></i></span>', '<span class="ar"></span>')
    return head + "<body>" + body_
def page(title, body, hero_preload, lang="en", head=None):
    D = donors(lang)
    return arrows(f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{head or f'<title>{title}</title><meta name="robots" content="noindex, nofollow">'}
<link rel="preload" as="image" href="{hero_preload}" fetchpriority="high"/>
{D["font"]}
<link rel="preload" as="font" type="font/woff2" href="/fonts/GildaC-450.woff2" crossorigin>
<style>.fw .hero > .wrap, .fw #cat-regions .band-h, .fw .hx-t b, .fw .hx-t .c {{ opacity: 0; }} .hero > .wrap, #cat-regions .band-h, .hx-t b, .hx-t .c {{ transition: opacity .18s; }}</style>
{D["style"].replace("</style>", R.EXTRA_CSS + CSS.replace("ARWVAL", ARW) + "</style>")}
{SM.css_block()}
<script>(function(){{var d=document.documentElement,f=document.fonts;if(!f||!f.load)return;d.classList.add("fw");var done=function(){{d.classList.remove("fw")}};
Promise.all(["400 1em GildaC","650 1em GildaC","700 1em GildaC","400 1em 'Hanken Grotesk'","500 1em 'Hanken Grotesk'","600 1em 'Hanken Grotesk'","700 1em 'Hanken Grotesk'"].map(function(x){{return f.load(x)}})).then(done,done);setTimeout(done,1500)}})();</script>
<noscript><style>.fw .hero > .wrap {{ opacity: 1; }}</style></noscript>
<!--evx:css--><link rel="stylesheet" href="/css/evalley-cta.css"><!--/evx:css-->
</head><body>
{body}
{D["foot"]}
{D["js"].replace('var art = document.getElementById("article")', 'var art = document.getElementById("article") || document.body')}
<script src="/js/search.js" defer></script>
{SM.js_block()}
</body></html>
""")


# ---------------- Main menu (frosted dropdowns) ----------------
EV_PHOTO = "/images/v2/the-flat-floor-of-the-el-f491c24a-hero-960.webp"
def _foot_photo(href):
    if href == "/articles/el-valle-de-anton": return EV_PHOTO
    if href.startswith("/images/"): return href
    m = re.search(r'<a class="fc" href="' + re.escape(href) + r'"><img class="ph"[^>]*src="([^"]+)"', D["foot"])
    return m[1].replace(SITE, "") if m else img_of(href)
def nav(en, es, lang="en"):
    """The site header, shared with every guide (scripts/site_menu.py)."""
    return SM.nav_html(lang, en, es)



def ptile(u, t, label, im=None, desc=""):
    return f'<a class="hx-pt" href="{u}"><img alt="" loading="lazy" src="{im or img_of(u)}"/><span class="lbl">{label}</span><b>{t}</b>{f'<p>{E(desc)}</p>' if desc else ''}<span class="ar"></span></a>'

def card(href, title, desc="", chip="", label="Guide", more=False):
    im = img_of(href)
    ph = f'<span class="ph"><img alt="" loading="lazy" src="{im}"/>' + (f'<span class="chip glass">{E(chip)}</span>' if chip else "") + "</span>"
    return (f'<a class="hx-card" href="{href}">{ph}<span class="tx"><span class="c"><i class="dot"></i>{label}</span><h3>{E(title)}</h3>'
            + (f"<p>{E(desc)}</p>" if desc else "") + ('<span class="go">Read the guide <span class="ar"></span></span>' if more else "") + "</span></a>")


# ---------------- Hubs ----------------
DD = {"en": D}
def donors(lang):
    if lang not in DD: DD[lang] = R.donor_parts(lang)
    return DD[lang]
UI = {"en": dict(by_topic="By topic", find="Find your guide", in_pics="In pictures", pics="{} in pictures", read_first="Read first", guides="guides",
                 glance="At a glance", aria="{} guides by topic"),
      "es": dict(by_topic="Por tema", find="Encuentra tu guía", in_pics="En imágenes", pics="{} en imágenes", read_first="Lee primero", guides="guías",
                 glance="De un vistazo", aria="Guías de {} por tema")}
ICO = {
 "mountain": '<path d="m3 20 6.5-11 4 6.5 2.5-4L21 20Z"/>',
 "pin": '<path d="M12 21s7-6.2 7-11.5a7 7 0 0 0-14 0C5 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>',
 "bus": '<rect x="4" y="3" width="16" height="15" rx="3"/><path d="M4 11h16M8 21v-3M16 21v-3"/><circle cx="8" cy="14.5" r=".8"/><circle cx="16" cy="14.5" r=".8"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 "cal": '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/>',
 "book": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2Z"/><path d="M4 19V5"/>',
 "peak": '<path d="m2 20 7-12 3.5 5.5L15 10l7 10Z"/><path d="M7.5 11.5 9 13l1.5-1.5"/>',
 "crater": '<path d="M2 18c3-7 5-10 7-10s2.5 3 3 3 1-3 3-3 4 3 7 10"/><path d="M7 18c1.5-2 3-3 5-3s3.5 1 5 3"/>',
 "plane": '<path d="M10.5 21 12 16l6.5 2.5L20 17l-6-5V6a2 2 0 0 0-4 0v6l-6 5 1.5 1.5L12 16"/>',
 "city": '<path d="M3 21h18M5 21V9l5-3v15M10 21V4l6 3v14M16 21V11l3 1.5V21"/><path d="M7 12h1M7 15h1M12.5 9h1M12.5 12h1M12.5 15h1"/>',
 "island": '<path d="M2 20c3-1.5 6-1.5 9 0s6 1.5 9 0"/><path d="M12 18c0-4-.5-7-2-10"/><path d="M10 8C8 6 5 6 4 7.5c2-.5 4 0 6 .5ZM10 8c1-2.5 4-3.5 6-2.5-2 .3-4.2 1.2-6 2.5ZM10 8c2.5-.5 5.5.5 6.5 2.5-2-1-4.3-1.8-6.5-2.5Z"/>'}
icon = lambda k: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICO[k]}</svg>'
import subprocess
_HASH = {}
def look(im):
    """A tiny fingerprint of the picture itself, so the same photo under two file names counts once."""
    if im not in _HASH:
        f = P / im.replace(SITE, "").lstrip("/")
        px = subprocess.run(["magick", str(f) + "[0]", "-resize", "8x8!", "-colorspace", "gray", "-depth", "8", "gray:-"], capture_output=True).stdout if f.exists() else b""
        avg = sum(px) / len(px) if px else 0
        _HASH[im] = int("".join("1" if b > avg else "0" for b in px) or "0", 2)
    return _HASH[im]
def same(a, b): return bin(look(a) ^ look(b)).count("1") <= 12
def photos_of(u):
    """A guide's hero first, then the other photos in the guide, so a repeated hero can be swapped."""
    h = srcf(u).read_text(errors="ignore")
    rest = re.findall(r'src="(?:' + re.escape(SITE) + r')?(/images/v2/[^"]+?-(?:wide|gallery)\.webp)"', h)
    return [img_of(u)] + rest
def hero_alt(u):
    h = srcf(u).read_text(errors="ignore")
    m = re.search(r'<img\b[^>]*class="hero-img"[^>]*>', h)
    a = re.search(r'\balt="([^"]*)"', m[0]) if m else None
    return html.unescape(a[1]) if a else ""
# photos the live hubs load from other sites, mapped to the same photo already self-hosted
LOCAL = {"17477516": "/images/v2/panama-city-skyline-from-the-waterfront-17477516-hero-1920.webp",
         "18049699": "/images/v2/narrow-street-in-casco-viejo-with-18049699-hero-1920.webp",
         "Panama_Canal_Gatun_Locks": "/images/v2/gatun-locks-of-the-panama-canal-f75c6691-hero-1920.webp",
         "Red_Frog_Beach_Bastimentos.jpg": "/images/v2/red-frog-beach-bastimentos-wide.webp"}
def local(src):
    src = src.replace(SITE, "")
    if src.startswith("/"): return src
    return next((v for k, v in LOCAL.items() if k in src), None)

def build_hub(rel, out, cfg):
    lang = "es" if rel.startswith("es/") else "en"; T = UI[lang]
    b = cfg.get("src") or srcf(rel).read_text(); b = b[b.index("<body"):]
    name = re.sub("<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", b, re.S)[1]).strip()
    short = cfg.get("short", name)
    dek = cfg.get("dek") or re.search(r'<p class="hub-hero-dek">(.*?)</p>', b, re.S)[1]
    leads = re.findall(r'<p class="hub-lead">(.*?)</p>', b, re.S)
    eyebrow = re.search(r'<p class="hub-eyebrow">(.*?)</p>', b)[1]
    pairs = re.findall(r'<p class="hub-eyebrow">([^<]*)</p>\s*<h2 class="hub-h2">([^<]*)</h2>(?:\s*<p class="hub-lead[^"]*">([^<]*)</p>)?', b)
    s_head, idx_h = pairs[0], pairs[-1]
    start = re.findall(r'<a class="hub-card" href="([^"]+)">.*?<h3>(.*?)</h3><p>(.*?)</p>', b, re.S)
    start_img = re.findall(r'<a class="hub-card" href="[^"]+"><div class="hub-card-img"><img src="([^"]+)"', b)
    groups = []
    for g in re.findall(r'<div class="hub-group">(.*?)</ul>', b, re.S):
        im = re.search(r'<img src="([^"]+)"[^>]*alt="([^"]*)"', g)
        groups.append(dict(img=local(im[1]), alt=im[2], h2=re.search(r"<h2>(.*?)</h2>", g, re.S)[1], blurb=re.search(r'<p class="hub-group-blurb">(.*?)</p>', g, re.S)[1],
                           items=re.findall(r'<a href="([^"]+)"><span class="n">(.*?)</span><span class="d">(.*?)</span>', g, re.S)))
    idx = re.findall(r'<li><a href="([^"]+)"><span class="num">(\d+)</span><span class="ttl">(.*?)</span><span class="cat">(.*?)</span>', b, re.S)
    HB = re.search(r'<div class="hub-hero-img"><img src="([^"]+)"[^>]*alt="([^"]*)"', b)
    hero = cfg.get("hero") or local(HB[1])
    pill_img = {}
    if cfg.get("tweak"): cfg["tweak"](groups, pill_img)
    # a topic photo that is missing or repeats an earlier one becomes the first fresh hero among its own guides
    seen = [img_of(u) for u, t, d in start] + [x for x in map(local, start_img) if x]
    for i, im in cfg.get("topic_img", {}).items(): groups[i]["img"], groups[i]["alt"] = im
    for gi, g in enumerate(groups):
        if not g["img"] or (gi not in cfg.get("topic_img", {}) and any(same(g["img"], x) for x in seen)):
            dist = lambda u: min([bin(look(img_of(u)) ^ look(x)).count("1") for x in seen] or [64]) if img_of(u) else -1
            alt = max((u for u, n, d in g["items"]), key=dist)  # the guide photo least like anything already on the page
            g["img"], g["alt"] = img_of(alt), hero_alt(alt)
        seen.append(g["img"])
    used = [look(g["img"]) for g in groups] + ([] if cfg.get("hero_in_thumbs") else [look(hero)])
    tile_photo = cfg.get("tile_photo", {})
    def fresh_photo(u):
        if u in tile_photo:
            used.append(look(tile_photo[u])); return tile_photo[u]
        for im in photos_of(u):
            if "-map-" in im: continue  # route maps make poor tiles
            k = look(im)
            if k and not any(bin(k ^ x).count("1") <= 12 for x in used):
                used.append(k); return im
        return img_of(u)
    icons_html = '<div class="hb-icons">' + "".join(f"<div><span class=\"ic\">{icon(k)}</span><span><b>{v}</b><span>{l}</span></span></div>" for k, v, l in cfg["icons"]) + "</div>"
    pills_html = f'<nav class="hb-pills" aria-label="{T["aria"].format(short)}">' + "".join(
        f'<a href="#topic-{i + 1}"><img alt="" src="{pill_img.get(i, g["img"])}"/><span><b>{g["h2"].split(":")[0]}</b><small>{len(g["items"])} {T["guides"]}</small></span></a>'
        for i, g in enumerate(groups)) + "</nav>"
    topics = ""
    for i, g in enumerate(groups):
        rows = "".join(f'<li><a href="{u}"><img alt="" loading="lazy" src="{fresh_photo(u)}"/><span class="t"><b>{n}</b><span>{d}</span></span><span class="go">→</span></a></li>' for u, n, d in g["items"])
        topics += (f'<div class="hb-group{" flip" if i % 2 else ""}" id="topic-{i + 1}"><div class="gi"><img alt="{html.escape(html.unescape(g["alt"]))}" loading="lazy" src="{g["img"]}"/></div>'
                   f'<div class="gt"><h2>{g["h2"]}</h2><p class="bl">{g["blurb"]}</p><ul class="hb-list">{rows}</ul></div></div>')
    gal = cfg.get("gallery")
    if gal is None:  # the best photos the hub's own guides use as heroes, none repeated from higher up the page
        taken = [g["img"] for g in groups] + [hero]; gal = []
        for u, n, t, c in idx:
            im = img_of(u)
            if im and not any(same(im, x) for x in taken):
                taken.append(im); gal.append((im, hero_alt(u)))
            if len(gal) == 7: break
    gal_html = "".join(f'<figure><img class="ph" alt="{html.escape(a)}" loading="lazy" src="{u}"/><figcaption>{E(a)}</figcaption></figure>' for u, a in gal)
    cta = cfg.get("cta", "")
    def start_photo(u, im):
        im = cfg.get("start_photo", {}).get(u) or local(im) or img_of(u)
        if same(im, hero):
            im = next((x for x in photos_of(u)[1:] if not same(x, hero)), im)
        return im
    start_html = "".join(ptile(u, R.text(t), T["read_first"], start_photo(u, im), desc=R.text(d)) for (u, t, d), im in zip(start, start_img))
    body = f"""<div class="guide-progress" id="prog" aria-hidden="true"></div>
<header class="hero hb-hero">
  <img class="hero-img" alt="{html.escape(cfg.get("hero_alt") or html.unescape(HB[2]))}" fetchpriority="high" src="{hero}" style="object-position:center {cfg.get("focus", 45)}%"/>
  {nav(cfg["en"], cfg["es"], lang)}
  <div class="wrap"><div class="hb-c">
    <div class="hb-t"><span class="lbl">{eyebrow}</span>
    <h1>{name}</h1></div>
    <p>{dek}</p>
  </div></div>
</header>
<section class="wrap hb-sec first"><div class="hb-orient"><div class="lead">{"".join(f"<p>{l}</p>" for l in leads[:1])}{icons_html}</div>
<aside class="glance hb-glance" aria-label="{T["glance"]}"><h2>{T["glance"]} <span><i class="dot"></i>{cfg["region"]}</span></h2><div class="gg">{"".join(f'<div><span class="k">{k}</span><b class="sm">{v}</b><span class="s">{x}</span></div>' for k, v, x in cfg["glance"])}</div></aside></div></section>
<section class="wrap hb-sec"><div class="hb-head"><span class="lbl">{s_head[0]}</span><h2>{s_head[1]}</h2><p>{s_head[2]}</p></div>
<div class="hb-start">{start_html}</div></section>
<section class="wrap hb-sec" id="topics"><div class="hb-head"><span class="lbl">{T["by_topic"]}</span><h2>{T["find"]}</h2></div>{pills_html}{topics}</section>
{f'<section class="wrap hb-sec">{cta}</section>' if cta else ""}
<section class="band gband hb-sec"><div class="wrap band-h"><div><span class="lbl">{T["in_pics"]}</span><h2>{T["pics"].format(short)}</h2></div></div><div class="gal hb-gal">{gal_html}</div></section>
<section class="wrap hb-sec last" id="all-guides"><div class="band-h"><div><span class="lbl">{idx_h[0]}</span><h2>{idx_h[1]}</h2></div><span class="band-sub">{len(idx)} {T["guides"]}</span></div>
<ol class="hx-idx">{"".join(f'<li><a href="{u}"><span class="n">{n}</span><span>{t}</span><span class="cat">{c}</span></a></li>' for u, n, t, c in idx)}</ol>
</section>
{(ROLL.JS_M[0] + ROLL.TRACK + ROLL.JS_M[1]) if cta else ""}
"""
    dest = URLMAP["/preview/" + out].lstrip("/")
    head = cfg.get("head") or hub_head(rel, hero, cfg.get("hero_alt") or html.unescape(HB[2]))
    (P / f"{dest}.html").write_text(finalize(page(name, body, hero, lang, head=head)))
    print("wrote", P / f"{dest}.html")

def hub_head(rel, hero, alt):
    """The old hub's own SEO tags (title, description, robots, canonical, hreflang, Open Graph, JSON-LD), with the share image updated."""
    h = (HUBSRC / f"{rel}.html").read_text(); head = h[:h.index("</head>")]
    keep = []
    for m in re.finditer(r'<title>.*?</title>|<script type="application/ld\+json">.*?</script>|<meta\b[^>]*>|<link\b[^>]*>', head, re.S):
        t = m[0]
        if t.startswith("<meta") and re.search(r'charset|name="viewport"|"viewport"|next-size-adjust', t): continue
        if t.startswith("<link") and not re.search(r'rel="(?:canonical|alternate|icon)"', t): continue
        keep.append(t)
    out = "".join(keep)
    old = re.search(r'<meta property="og:image" content="([^"]+)"', out)
    if old:
        new = SITE + hero
        for v in {old[1], html.unescape(old[1])}: out = out.replace(v, new)
    out = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m[1] + html.escape(alt), out)
    return out

def _boquete(groups, pill_img):
    g = lambda s: next(x for x in groups if html.unescape(x["h2"]).startswith(s))
    hot, wheels = g("Hot water"), g("On two wheels")
    tours = next(x for x in hot["items"] if "Tours" in x[1]); hot["items"].remove(tours); wheels["items"].append(tours)
    hot["h2"] = "Hot water and rivers"
    t = g("Trails"); t["img"] = "/images/v2/volcan-baru-in-a-cloud-shroud-wide.webp"; t["alt"] = "Volcán Barú's summit above a band of cloud, seen across highland forest and pasture."
    c = g("Coffee"); c["img"] = "/images/v2/al-in-los-quetzales-national-park-photo-hero-1280.webp"; c["alt"] = "A resplendent quetzal perched on a mossy branch."
    pill_img[groups.index(wheels)] = "/images/v2/boquete-ebike-hero-tile.webp"
_bq_cta = B.blocks("boquete-en")["banner"]
# hub only: the waterfall photo in the banner; the riders photo is overused (live guide CTAs are unchanged)
_bq_cta = _bq_cta.replace("evalley-boquete-ebike-trail", "evalley-boquete-ebike-hero").replace("Two riders on E-Valley e-bikes on a farm track in Boquete", "Two riders with e-bikes in front of a waterfall near Boquete").replace('class="ev-ph"', 'class="ev-ph hb-ev-ph"').replace('class="evx ev-banner"', 'class="evx ev-dark ev-banner hb-ev-dark"')
# every value in icons and glance is taken from that hub's own text
build_hub("articles/boquete", "boquete-hub.html", dict(dek="A cool, green coffee town in the Chiriquí highlands, an hour from Costa Rica.",
    en="/preview/boquete-hub.html", es="/preview/boquete-hub-es.html", region="Chiriquí highlands", hero="/images/v2/boquete-hills-hero-1920.webp",
    icons=[("mountain", "1,200 m", "Elevation"), ("pin", "Chiriquí", "Province"), ("peak", "3,475 m", "Volcán Barú"), ("bus", "1 hr", "To the Costa Rican border"), ("book", "24 guides", "In this library")],
    glance=[("Getting there", "Fly to David", "then 45 min by road; 7 hrs by bus"), ("When to go", "Dec–Apr", "driest months; mist any time"),
            ("How long", "3 days", "a fourth for Volcán Barú"), ("Getting around", "Walk town", "bike, taxi or car beyond it")],
    tweak=_boquete, cta=_bq_cta, hero_in_thumbs=True, tile_photo={"/articles/boquete-cycling-routes": "/images/v2/evalley-boquete-ebike-riders-640.webp"},
    gallery=[("/images/v2/volcan-baru-emerging-through-clouds-d35d9b87-hero-1280.webp", "Volcán Barú rising through cloud above forested slopes."),
             ("/images/v2/resplendent-quetzal-646deb1a-gallery.webp", "A resplendent quetzal, the bird most birders come to Boquete for."),
             ("/images/v2/red-coffee-cherries-at-peak-ripeness-35629753-wide.webp", "Red coffee cherries at peak ripeness on the slopes of Volcán Barú."),
             ("/images/boquete/boquete-rafting.webp", "Rafters in yellow boats on a river near Boquete."),
             ("/images/boquete/boquete-cabins.webp", "Timber A-frame cabins on a hillside above Boquete."),
             ("/images/boquete/boquete-market.webp", "Fruit and vegetables for sale at a market stall in Boquete."),
             ("/images/v2/view-from-restaurant-covered-los-molinos-hero-1280.webp", "Storm light over the green canyons around Boquete.")]))
build_hub("es/articles/el-valle-de-anton", "el-valle-hub-es.html", dict(dek="Un pueblo dentro de un volcán, a dos horas de la capital y más fresco que la costa.",
    en="/preview/el-valle-hub.html", es="/preview/el-valle-hub-es.html", short="El Valle", region="Provincia de Coclé", focus=58,
    hero="/images/v2/the-el-valle-de-anton-crater-829139d1-hero-1920.webp", hero_alt="El valle del cráter de El Valle de Antón, rodeado de cerros verdes.",
    icons=[("mountain", "600 m", "De altura"), ("pin", "Coclé", "Provincia"), ("crater", "5 km", "De cráter de lado a lado"), ("bus", "2 h", "Desde la capital"), ("book", "29 guías", "En esta biblioteca")],
    glance=[("Cómo llegar", "2½ h en bus", "desde Albrook; 2 h en carro"), ("Cuándo ir", "Dic–abr", "la temporada seca"),
            ("Cuánto quedarse", "Un día", "dos noches, mejor"), ("Cómo moverse", "En bici", "senderos a 10–25 min")],
    cta=B.blocks("elvalle-es")["banner"],
    topic_img={0: ("/images/v2/forested-foothills-rising-toward-the-cerro-c28c8ac8-hero-1280.webp", "Laderas boscosas que suben hacia el Cerro Gaital."),
               2: ("/images/v2/jaguar-at-el-nispero-12861718-hero-1280.webp", "Un jaguar en el Zoológico El Níspero."),
               3: ("/images/el-valle/elvalle-flowermarket.webp", "Plantas y flores a la venta bajo el techo del mercado de El Valle"), 4: ('/images/v2/la-entrada-al-valle-por-carretera-d9c1199f-wide.webp', 'La entrada al valle por carretera, con el cerro cerrando el fondo — los últimos kilómetros de la subida.')},
    gallery=[('/images/v2/cortinas-de-agua-sobre-roca-cubierta-f60dd697-hero-1280.webp', 'Cortinas de agua sobre roca en el Chorro El Macho.'),
             ('/images/v2/dusk-settling-over-el-valle-from-22d3aa14-wide.webp', 'El Valle al anochecer desde el borde del cráter.'),
             ('/images/v2/una-heliconius-charithonia-alimentandose-de-flores-4cb016d1-wide.webp', 'Una Heliconius charithonia en flores amarillas.'),
             ('/images/v2/pinas-y-naranjas-apiladas-en-cajas-2281d6e3-wide.webp', 'Piñas y naranjas de las fincas del cráter.'),
             ('/images/v2/elvalle-panorama-wide.webp', 'La ladera boscosa del cráter vista desde el valle.'),
             ('/images/v2/artesania-pintada-a-mano-colgada-en-df5c68cf-wide.webp', 'Artesanía pintada a mano en el mercado.'),
             ('/images/v2/things-to-do-el-valle-hero-1280.webp', 'Flores bajo una pérgola en El Valle de Antón.')]))
build_hub("articles/panama-city", "panama-city-hub.html", dict(dek="A glass skyline on one side of the bay, a 350-year-old walled quarter on the other.",
    en="/preview/panama-city-hub.html", es="/preview/panama-city-hub-es.html", region="Pacific coast", focus=50,
    topic_img={0: ("/images/v2/string-lights-between-balconies-in-casco-2564872-wide.webp", "String lights between balconies in Casco Viejo.")},
    icons=[("pin", "Pacific", "Coast"), ("city", "350 years", "The walled old quarter"), ("plane", "Tocumen", "Main airport (PTY)"), ("cal", "2–3 days", "For the city and the canal"), ("book", "9 guides", "In this library")],
    glance=[("Getting there", "Tocumen (PTY)", "Metro Line 2 reaches it"), ("When to go", "Dec–Apr", "dry; the canal works any time"),
            ("How long", "2 days", "three for the canal"), ("Getting around", "Metro + Uber", "skip driving in Casco")],
    gallery=[('/images/v2/casco-viejo-at-night-with-city-33803474-wide.webp', 'Casco Viejo at night, with the skyline behind it.'),
             ('/images/v2/panama-city-skyline-33803476-wide.webp', 'The skyline across the bay after dark.'),
             ('/images/v2/metropolitan-cathedral-of-panama-city-1d602aa6-wide.webp', 'The Metropolitan Cathedral in Casco Viejo.'),
             ('/images/v2/three-toed-sloth-on-ancon-hill-35179277-wide.webp', 'A three-toed sloth on Ancón Hill.'),
             ('/images/v2/casco-antiguo-san-felipe-21af3ff1-gallery.webp', 'Casco Antiguo from the air.'),
             ('/images/v2/cruise-ship-passing-miraflores-locks-2019-10-gallery.webp', 'A cruise ship inside a Miraflores Locks chamber.'),
             ('/images/v2/islands-of-the-amador-causeway-994a1080-wide.webp', 'The islands at the end of the Amador Causeway.')]))
build_hub("articles/bocas-del-toro", "bocas-hub.html", dict(dek="Hundreds of islands off the Caribbean coast: warm sea, mangroves and reef.",
    en="/preview/bocas-hub.html", es="/preview/home-es.html", region="Caribbean coast", focus=50,
    hero="/images/v2/nyara-bocas-del-toro-panama-hero-1920.webp", hero_alt="Thatched overwater bungalows on stilts over calm water in Bocas del Toro.",
    icons=[("pin", "Caribbean", "Coast"), ("island", "9 islands", "The main ones"), ("plane", "1 hr", "Flight from Panama City"), ("sun", "Sep–Oct", "Calmest, clearest water"), ("book", "7 guides", "In this library")],
    glance=[("Getting there", "1-hr flight", "or overnight bus + water taxi"), ("When to go", "Sep–Oct", "or February to April"),
            ("How long", "3 nights", "a week for the outer cays"), ("Getting around", "Water taxi", "$6–$35 per crossing")],
    gallery=[('/images/v2/red-frog-beach-island-resort-wide.webp', 'Red Frog Beach from the air.'),
             ('/images/v2/a-three-toed-sloth-peers-from-7200626-wide.webp', 'A three-toed sloth on a tree trunk.'),
             ('/images/v2/bocas-scene-ef3a4170-wide.webp', 'Bocas Town on Isla Colón from the air.'),
             ('/images/v2/a-quiet-stretch-of-pale-sand-9a4453d2-wide.webp', 'Pale sand and calm water on a quiet beach.'),
             ('/images/v2/two-round-thatched-roof-structures-stand-33990238-gallery.webp', 'Thatched huts at the end of a dock over shallow water.'),
             ('/images/v2/whitewater-rolls-onto-a-sandy-shore-5f05bf22-wide.webp', 'Surf rolling onto a forest-backed beach.'),
             ('/images/v2/an-aerial-view-of-turquoise-channels-9f639d6b-wide.webp', 'Turquoise channels through low mangrove islets.')]))

# the other language of each hub (same photos and facts, taken from that hub's own text)
_bq_cta_es = B.blocks("boquete-es")["banner"].replace("evalley-boquete-ebike-trail", "evalley-boquete-ebike-hero").replace('class="ev-ph"', 'class="ev-ph hb-ev-ph"').replace('class="evx ev-banner"', 'class="evx ev-dark ev-banner hb-ev-dark"')
_bq_cta_es = re.sub(r'(<img[^>]*evalley-boquete-ebike-hero[^>]*alt=")[^"]*', r'\1Dos ciclistas con e-bikes frente a una cascada cerca de Boquete', _bq_cta_es)
build_hub("es/articles/boquete", "boquete-hub-es.html", dict(dek="Un pueblo cafetero fresco y verde en las tierras altas de Chiriquí, a una hora de Costa Rica.",
    en="/preview/boquete-hub.html", es="/preview/boquete-hub-es.html", region="Tierras altas de Chiriquí", hero="/images/v2/boquete-hills-hero-1920.webp",
    icons=[("mountain", "1,200 m", "De altura"), ("pin", "Chiriquí", "Provincia"), ("peak", "3,475 m", "Volcán Barú"), ("bus", "1 h", "A la frontera con Costa Rica"), ("book", "24 guías", "En esta biblioteca")],
    glance=[("Cómo llegar", "Vuelo a David", "y 45 min por carretera; 7 h en bus"), ("Cuándo ir", "Dic–abr", "los meses más secos; neblina siempre"),
            ("Cuánto quedarse", "3 días", "un cuarto para el Volcán Barú"), ("Cómo moverse", "A pie", "bici, taxi o carro fuera del pueblo")],
    cta=_bq_cta_es, hero_in_thumbs=True,
    topic_img={0: ("/images/v2/volcan-baru-in-a-cloud-shroud-wide.webp", "La cumbre del Volcán Barú sobre una franja de nubes."),
               1: ("/images/v2/al-in-los-quetzales-national-park-photo-hero-1280.webp", "Un quetzal posado en una rama cubierta de musgo.")},
    gallery=[("/images/v2/volcan-baru-emerging-through-clouds-d35d9b87-hero-1280.webp", "El Volcán Barú entre las nubes, sobre laderas de bosque."),
             ("/images/v2/resplendent-quetzal-646deb1a-gallery.webp", "Un quetzal, el ave por la que vienen casi todos los observadores a Boquete."),
             ("/images/v2/red-coffee-cherries-at-peak-ripeness-35629753-wide.webp", "Granos de café rojos y maduros en las faldas del Volcán Barú."),
             ("/images/boquete/boquete-rafting.webp", "Balsas amarillas en un río cerca de Boquete."),
             ("/images/boquete/boquete-cabins.webp", "Cabañas de madera en una ladera sobre Boquete."),
             ("/images/boquete/boquete-market.webp", "Frutas y verduras en un puesto del mercado de Boquete."),
             ("/images/v2/view-from-restaurant-covered-los-molinos-hero-1280.webp", "Luz de tormenta sobre los cañones verdes de Boquete.")]))
build_hub("articles/el-valle-de-anton", "el-valle-hub.html", dict(dek="A town inside a volcano, two hours from Panama City and cooler than the coast.",
    en="/preview/el-valle-hub.html", es="/preview/el-valle-hub-es.html", short="El Valle", region="Coclé province", focus=58,
    hero="/images/v2/the-el-valle-de-anton-crater-829139d1-hero-1920.webp", hero_alt="The El Valle de Antón crater valley ringed by green peaks.",
    icons=[("mountain", "600 m", "Elevation"), ("pin", "Coclé", "Province"), ("crater", "5 km", "Crater, rim to rim"), ("bus", "2 hrs", "From Panama City"), ("book", "19 guides", "In this library")],
    glance=[("Getting there", "2½ hrs by bus", "from Albrook; 2 hrs by car"), ("When to go", "Dec–Apr", "the dry season"),
            ("How long", "A day", "two nights is better"), ("Getting around", "By bike", "trails 10–25 min away")],
    cta=B.blocks("elvalle-en")["banner"],
    topic_img={0: ("/images/v2/forested-foothills-rising-toward-the-cerro-c28c8ac8-hero-1280.webp", "Forested foothills rising toward Cerro Gaital.")},
    gallery=[('/images/v2/cortinas-de-agua-sobre-roca-cubierta-f60dd697-hero-1280.webp', 'Curtains of water over rock at Chorro El Macho.'),
             ('/images/v2/dusk-settling-over-el-valle-from-22d3aa14-wide.webp', 'El Valle at dusk from the crater rim.'),
             ('/images/v2/una-heliconius-charithonia-alimentandose-de-flores-4cb016d1-wide.webp', 'A zebra longwing butterfly on yellow flowers.'),
             ('/images/v2/pinas-y-naranjas-apiladas-en-cajas-2281d6e3-wide.webp', 'Pineapples and oranges from the crater farms.'),
             ('/images/v2/elvalle-panorama-wide.webp', 'The forested crater wall seen from the valley.'),
             ('/images/v2/artesania-pintada-a-mano-colgada-en-df5c68cf-wide.webp', 'Hand-painted crafts at the market.'),
             ('/images/v2/things-to-do-el-valle-hero-1280.webp', 'Flowers under a pergola in El Valle de Antón.')]))
build_hub("es/articles/panama-city", "panama-city-hub-es.html", dict(dek="Rascacielos de vidrio a un lado de la bahía y un casco amurallado de 350 años al otro.",
    en="/preview/panama-city-hub.html", es="/preview/panama-city-hub-es.html", region="Costa del Pacífico", focus=50,
    topic_img={0: ("/images/v2/string-lights-between-balconies-in-casco-2564872-wide.webp", "Luces colgadas entre balcones en el Casco Viejo.")},
    icons=[("pin", "Pacífico", "Costa"), ("city", "350 años", "El casco amurallado"), ("plane", "Tocumen", "Aeropuerto principal (PTY)"), ("cal", "2–3 días", "Para la ciudad y el canal"), ("book", "5 guías", "En esta biblioteca")],
    glance=[("Cómo llegar", "Tocumen (PTY)", "la Línea 2 del metro llega"), ("Cuándo ir", "Dic–abr", "seco; el canal, todo el año"),
            ("Cuánto quedarse", "2 días", "tres con el canal"), ("Cómo moverse", "Metro + Uber", "no manejes en el Casco")],
    gallery=[('/images/v2/casco-viejo-at-night-with-city-33803474-wide.webp', 'El Casco Viejo de noche, con los rascacielos detrás.'),
             ('/images/v2/panama-city-skyline-33803476-wide.webp', 'Los rascacielos al otro lado de la bahía, de noche.'),
             ('/images/v2/metropolitan-cathedral-of-panama-city-1d602aa6-wide.webp', 'La Catedral Metropolitana en el Casco Viejo.'),
             ('/images/v2/three-toed-sloth-on-ancon-hill-35179277-wide.webp', 'Un perezoso de tres dedos en el Cerro Ancón.'),
             ('/images/v2/casco-antiguo-san-felipe-21af3ff1-gallery.webp', 'El Casco Antiguo desde el aire.'),
             ('/images/v2/cruise-ship-passing-miraflores-locks-2019-10-gallery.webp', 'Un crucero dentro de una cámara de las Esclusas de Miraflores.'),
             ('/images/v2/islands-of-the-amador-causeway-994a1080-wide.webp', 'Las islas al final de la Calzada de Amador.')]))

# Hubs with no live page yet (English only for now): the source is written here in the live hub markup,
# every fact taken from the hub's own guides.
def hub_src(name, dek, hero, hero_alt, lead, start, groups, idx, idx_h2):
    E2 = html.escape
    card = lambda u, im, t, d: f'<a class="hub-card" href="{u}"><div class="hub-card-img"><img src="{im}" alt=""></div><div class="hub-card-body"><h3>{E2(t)}</h3><p>{E2(d)}</p></div></a>'
    grp = lambda im, alt, h2, bl, items: (f'<div class="hub-group"><div class="hub-group-media"><img src="{im}" alt="{E2(alt)}"></div><div><h2>{E2(h2)}</h2><p class="hub-group-blurb">{E2(bl)}</p><ul class="hub-list">'
        + "".join(f'<li><a href="{u}"><span class="n">{E2(n)}</span><span class="d">{E2(d)}</span></a></li>' for u, n, d in items) + "</ul></div></div>")
    return (f'<body><section class="hub-hero"><div class="hub-hero-img"><img src="{hero}" alt="{E2(hero_alt)}"></div><p class="hub-eyebrow">Destination guide</p><h1>{name}</h1><p class="hub-hero-dek">{E2(dek)}</p></section>'
            f'<p class="hub-lead">{E2(lead)}</p>'
            f'<p class="hub-eyebrow">Start here</p>\n<h2 class="hub-h2">If you only read three</h2>\n<p class="hub-lead hub-narrow">The three guides that answer most of what people ask before a first trip.</p>'
            + "".join(card(*c) for c in start) + "".join(grp(*g) for g in groups)
            + f'<p class="hub-eyebrow">The full library</p>\n<h2 class="hub-h2">{idx_h2}</h2>'
            + "".join(f'<li><a href="{u}"><span class="num">{i + 1}</span><span class="ttl">{E2(t)}</span><span class="cat">{c}</span></a></li>' for i, (u, t, c) in enumerate(idx)) + "</body>")

_SB = ("/articles/san-blas-islands-panama-guna-yala-guide", "/articles/san-blas-tours-from-panama-city", "/articles/san-blas-sailing-panama-to-colombia")
import json as _json
def _sb_head():
    url = SITE + "/articles/san-blas"; img = SITE + "/images/v2/x-diadup-kuna-yala-panam-c3-a1-hero-1920.webp"
    t = "San Blas (Guna Yala): Every Guide to the Islands"
    d = "All our San Blas guides in one place: the complete Guna Yala island guide, tours from Panama City compared, and sailing to Colombia."
    items = [("/articles/san-blas-islands-panama-guna-yala-guide", "San Blas Islands (Guna Yala): The Complete Guide"),
             ("/articles/san-blas-tours-from-panama-city", "San Blas Tours From Panama City"), ("/articles/san-blas-sailing-panama-to-colombia", "San Blas Sailing, Panama to Colombia")]
    ld = [{"@context": "https://schema.org", "@type": "Organization", "@id": SITE + "/#organization", "name": "PanamaSpot", "url": SITE,
           "logo": {"@type": "ImageObject", "url": SITE + "/logo.png", "width": 512, "height": 512}, "sameAs": ["https://www.instagram.com/panamaspot", "https://twitter.com/panamaspot"]},
          {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "name": "PanamaSpot", "url": SITE, "publisher": {"@id": SITE + "/#organization"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "San Blas"}]},
          {"@context": "https://schema.org", "@type": "CollectionPage", "@id": url + "#collection", "url": url, "name": t, "description": d, "inLanguage": "en-US",
           "isPartOf": {"@id": SITE + "/#website"}, "primaryImageOfPage": {"@type": "ImageObject", "url": img},
           "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + u, "name": n} for i, (u, n) in enumerate(items)]}}]
    e = lambda x: html.escape(x, quote=True)
    return (f'<meta content="#ffffff" name="theme-color"/><title>{e(t)}</title><meta name="description" content="{e(d)}"/><meta content="PanamaSpot" name="application-name"/>'
            f'<meta content="index, follow" name="robots"/><link href="{url}" rel="canonical"/><link href="{url}" hreflang="en" rel="alternate"/><link href="{url}" hreflang="x-default" rel="alternate"/>'
            f'<meta property="og:title" content="{e(t)}"/><meta property="og:description" content="{e(d)}"/><meta property="og:url" content="{url}"/><meta content="PanamaSpot" property="og:site_name"/>'
            f'<meta property="og:locale" content="en_US"/><meta property="og:image" content="{img}"/><meta property="og:image:alt" content="A leaning palm on a white sand beach facing turquoise water in Guna Yala."/>'
            f'<meta property="og:type" content="website"/><meta content="summary_large_image" name="twitter:card"/><meta content="@panamaspot" name="twitter:site"/>'
            f'<meta name="twitter:title" content="{e(t)}"/><meta name="twitter:description" content="{e(d)}"/><meta name="twitter:image" content="{img}"/><link href="/favicon.ico" rel="icon"/>'
            + "".join(f'<script type="application/ld+json">{_json.dumps(x, ensure_ascii=False)}</script>' for x in ld))
build_hub("articles/san-blas", "san-blas-hub.html", dict(head=_sb_head(),
    src=hub_src("San Blas", "Palm cays and turquoise water on the Caribbean, home of the Guna people.",
        "/images/v2/x-diadup-kuna-yala-panam-c3-a1-hero-1920.webp", "A leaning palm on a white sand beach facing turquoise water in Guna Yala.",
        "San Blas is the Comarca Guna Yala: 365 islands and cays off Panama's Caribbean coast, governed by the Guna. You get there by 4x4 from Panama City to the port of Cartí, then by boat, and most people come for a day trip or a night or two on an island.",
        [(_SB[0], "/images/v2/coconut-palms-lean-over-a-white-10490913-wide.webp", "San Blas: The Complete Guide", "Getting there, day trip or overnight, 2026 prices and the Guna Yala rules."),
         (_SB[1], "/images/v2/caba-c3-b1as-guna-yala-hero-960.webp", "Tours From Panama City", "Day trips, one and two-night tours and private trips, compared with prices."),
         (_SB[2], "/images/v2/a-single-sailboat-glides-across-a-36117831-hero-960.webp", "Sailing to Colombia", "Five days through San Blas to Cartagena: boats, operators and the real budget.")],
        [("/images/v2/isla-pelicano-san-blas-panama-sg105536-wide.webp", "A thatched Guna hut under leaning palms on a small sandy island.", "Visiting the islands", "A day trip or a night on an island, what it costs, and the rules of the comarca.",
          [(_SB[0], "The Complete Guide", "Entry fee, getting there, where to stay and the weather by season."), (_SB[1], "Tours From Panama City", "Day trips vs overnight, what is included and how to book.")]),
         ("/images/v2/a-dark-rock-outcrop-breaks-the-36095905-wide.webp", "Two sailboats at anchor in calm water off the San Blas cays.", "Sailing to Colombia", "The open-water way out of Panama, with three days in the islands on the way.",
          [(_SB[2], "Panama to Colombia by Boat", "Itinerary, monohull or catamaran, operators and seasickness.")])],
        [(_SB[0], "San Blas Islands (Guna Yala): The Complete Guide", "Overview"), (_SB[1], "San Blas Tours From Panama City", "Tours"), (_SB[2], "San Blas Sailing, Panama to Colombia", "Sailing")],
        "Every San Blas guide"),
    en="/preview/san-blas-hub.html", es="/preview/home-es.html", region="Caribbean coast", focus=55,
    icons=[("island", "365", "Islands and cays"), ("pin", "Guna Yala", "Comarca"), ("bus", "2.5–3 hrs", "By 4x4 to Cartí"), ("sun", "Dec–Apr", "The sunniest months"), ("book", "3 guides", "In this library")],
    glance=[("Getting there", "4x4 + boat", "2.5–3 hrs to Cartí, then the boat"), ("When to go", "Dec–Apr", "February and March driest"),
            ("How long", "1–2 nights", "or a day trip from the city"), ("Entry fee", "$22 cash", "foreigners, at the checkpoint")],
    topic_img={0: ("/images/v2/a-small-sand-cay-with-a-9122911-gallery.webp", "A small sand cay with a cluster of coconut palms in clear blue water."),
               1: ("/images/v2/a-dark-rock-outcrop-breaks-the-36095905-wide.webp", "Two sailboats at anchor in calm water off the San Blas cays.")},
    gallery=[("/images/v2/san-blas-islands-wide.webp", "An island crowded with thatched and tin-roofed houses in San Blas."),
             ("/images/v2/a-green-roofed-boat-crosses-turquoise-30826587-wide.webp", "A boat crosses turquoise water toward a palm-covered island."),
             ("/images/v2/snorkelling-in-guna-yala-panama-panoramio-gallery.webp", "A brain coral on the sandy bottom, snorkelling in Guna Yala."),
             ("/images/v2/morrodub-cayos-holandeses-san-blas-panam-c3-wide.webp", "Leaning coconut palms on a small island in the Cayos Holandeses."),
             ("/images/v2/bathers-wade-on-a-pale-sandbar-e71210b9-wide.webp", "Bathers wading on a pale sandbar in turquoise shallows."),
             ("/images/v2/a-dense-palm-cay-ringed-by-5b275fca-wide.webp", "A dense palm cay ringed by white sand and thatched shelters."),
             ("/images/v2/a-palm-lined-white-sand-beach-10490919-gallery.webp", "A palm-lined white sand beach curving along turquoise water.")]))


ARROWS = """<script>document.querySelectorAll(".hx-rw").forEach(function(w){var r=w.querySelector(".hx-row"),l=w.querySelector(".hx-arr.l"),n=w.querySelector(".hx-arr.r");
function st(){l.disabled=r.scrollLeft<4;n.disabled=r.scrollLeft+r.clientWidth>=r.scrollWidth-4;}
l.onclick=function(){r.scrollBy({left:-r.clientWidth*.8,behavior:"smooth"})};n.onclick=function(){r.scrollBy({left:r.clientWidth*.8,behavior:"smooth"})};
r.addEventListener("scroll",st,{passive:true});addEventListener("resize",st);st();});</script>"""
# ---------------- Homepage ----------------
SRC = {"en": (ROOT / "src/app/page.tsx").read_text(), "es": (ROOT / "src/app/es/page.tsx").read_text()}
def cards_of(name, lang="en"):
    src = SRC[lang]
    blk = re.search(r"const " + name + r": Card\[\] = \[(.*?)\];", src, re.S)[1]
    out = []
    for m in re.finditer(r'\{ title: "([^"]+)", tag: "([^"]+)",.*?href: ([A-Z_]+|"[^"]+") \}', blk):
        href = m[3].strip('"') if m[3].startswith('"') else re.search(r"const " + m[3] + r' = "([^"]+)"', src)[1]
        out.append((m[1], m[2], href))
    return out
HOME_BG = "https://images.pexels.com/photos/2474690/pexels-photo-2474690.jpeg?auto=compress&cs=tinysrgb&w=2400"
ROT_IMGS = [(HOME_BG, "", 50)] + [(f"/images/v2/{n}-hero-1920.webp", a, y) for n, a, y in [
    ("playa-blanca-saboga", "Palm trees over Playa Blanca on Isla Saboga, Pearl Islands.", 62),
    ("volcan-baru-emerging-through-clouds-d35d9b87", "Volcán Barú rising through cloud above forested slopes.", 40),
    ("isla-en-guna-yala", "A palm-lined beach on an island in Guna Yala.", 55),
    ("panama-city-skyline-from-the-waterfront-17477516", "The Panama City skyline seen across the water.", 55),
    ("aerial-view-of-boquete-panama-ed675378", "Boquete in its river valley, seen from the air.", 55),
    ("late-light-on-the-crater-wall-a262b398", "Late light on the crater wall above El Valle de Antón.", 60)]]
ROT_ES = {"Palm trees over Playa Blanca on Isla Saboga, Pearl Islands.": "Palmeras sobre Playa Blanca, en isla Saboga, archipiélago de las Perlas.",
          "Volcán Barú rising through cloud above forested slopes.": "El Volcán Barú asomando entre las nubes sobre laderas de bosque.",
          "A palm-lined beach on an island in Guna Yala.": "Una playa con palmeras en una isla de Guna Yala.",
          "The Panama City skyline seen across the water.": "Los rascacielos de Ciudad de Panamá vistos desde el agua.",
          "Boquete in its river valley, seen from the air.": "Boquete en su valle de río, visto desde el aire.",
          "Late light on the crater wall above El Valle de Antón.": "Luz de tarde en la pared del cráter de El Valle de Antón."}
def rot(lang):
    return "".join(f'<img class="hero-img hx-rot{" on" if i == 0 else ""}" alt="{ROT_ES.get(a, a) if lang == "es" else a}" {"fetchpriority=" + chr(34) + "high" + chr(34) + " src" if i == 0 else "data-src"}="{u}" style="object-position:center {y}%"/>' for i, (u, a, y) in enumerate(ROT_IMGS))
ROTJS = """<script>(function(){var im=[].slice.call(document.querySelectorAll(".hx-rot"));if(im.length<2||matchMedia("(prefers-reduced-motion: reduce)").matches)return;
addEventListener("load",function(){im.forEach(function(i){if(i.dataset.src)i.src=i.dataset.src;});var k=0;setInterval(function(){var n=(k+1)%im.length;if(!im[n].complete)return;im[k].classList.remove("on");im[n].classList.add("on");k=n;},3200);});})();</script>"""
# destination photos are the English footer's, matched by region so both languages show the same pictures
DEST_PHOTO = {k: re.search(r'<a class="fc" href="' + re.escape(k) + r'"><img class="ph"[^>]*src="([^"]+)"', D["foot"])[1].replace(SITE, "")
              for k in ["/articles/panama-city", "/articles/boquete", "/articles/el-valle-de-anton", "/articles/bocas-del-toro", "/articles/san-blas-islands-panama-guna-yala-guide"]}
ES_TWIN = {"/es/articles/panama-city": "/articles/panama-city", "/es/articles/boquete": "/articles/boquete", "/es/articles/el-valle-de-anton": "/articles/el-valle-de-anton",
           "/es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama": "/articles/bocas-del-toro", "/es/articles/san-blas-guna-yala-guia-tours-islas": "/articles/san-blas-islands-panama-guna-yala-guide"}
DEST_PHOTO["/articles/el-valle-de-anton"] = EV_PHOTO
def dest_img(href):
    return DEST_PHOTO.get(ES_TWIN.get(href, href)) or img_of(href)
def count(href):
    f = srcf(href); t = f.read_text(errors="ignore")
    pre = "/es/articles/" if href.startswith("/es/") else "/articles/"
    return len(set(re.findall(r'href="(' + pre + r'[^"#]+)"', t[t.find("<body"):t.find("<footer")])))
HUBS = {"/articles/boquete", "/articles/el-valle-de-anton", "/articles/panama-city", "/articles/bocas-del-toro",
        "/es/articles/boquete", "/es/articles/el-valle-de-anton", "/es/articles/panama-city"}
ROW_PHOTO = {"/articles/tours-in-boquete-panama": "/images/v2/grupo-disfrutando-de-aguas-rapidas-emocionantes-36791113-hero-1280.webp",
             "/articles/where-to-stay-in-panama-city": "/images/v2/casco-viejo-panama-city-panama-54319827771-hero-1280.webp",
             "/es/articles/tours-en-boquete-panama": "/images/v2/boquete-zipline-rider-hero-1280.webp",
             "/es/articles/panama-city": "/images/v2/skyscrapers-catch-the-last-light-at-13842831-hero-1280.webp"}
def dek_of(href):
    t = srcf(href).read_text(errors="ignore"); m = re.search(r'<p class="dek">(.*?)</p>', t, re.S); s = R.text(m[1]) if m else ""
    return s if len(s) < 150 else s[:150].rsplit(" ", 1)[0] + "…"
ACT_PHOTO = {"Eco-tourism": "/images/v2/mist-drifts-through-the-cloud-forest-36345390-wide.webp"}
act_img = {"Hiking & Trails": "/articles/hikes-in-boquete", "Wildlife & Birding": "/articles/birding-el-valle-de-anton-trails-lodges-season", "Surf & Dive": "/articles/panama-surf-camps",
           "Food & Coffee": "/articles/geisha-coffee-boquete-where-to-taste", "Eco-tourism": "/articles/finca-lerida-los-quetzales-trail-birdwatching-boquete", "Cities & Culture": "/articles/casco-viejo-panama-walking-guide", "Islands & Beaches": "/articles/san-blas-islands-panama-guna-yala-guide"}
ACT_ES = {"Ciudades y Cultura": "Cities & Culture", "Senderismo": "Hiking & Trails", "Ecoturismo": "Eco-tourism", "Fauna y Aves": "Wildlife & Birding",
          "Surf y Buceo": "Surf & Dive", "Comida y Café": "Food & Coffee", "Islas y Playas": "Islands & Beaches"}
def act_photo(t):
    t = ACT_ES.get(t, t)
    return ACT_PHOTO.get(t) or img_of(act_img[t])

PLACES = {
 "en": [("Panama City", "Capital and canal", "/articles/panama-city", None), ("Boquete", "Coffee highlands", "/articles/boquete", None),
        ("El Valle de Antón", "Volcanic crater", "/articles/el-valle-de-anton", None), ("Bocas del Toro", "Caribbean islands", "/articles/bocas-del-toro", None),
        ("San Blas", "Guna Yala", "/preview/san-blas-hub.html", img_of("/articles/san-blas-islands-panama-guna-yala-guide"))],
 "es": [("Ciudad de Panamá", "Capital y canal", "/es/articles/panama-city", None), ("Boquete", "Tierras altas del café", "/es/articles/boquete", None),
        ("El Valle de Antón", "Cráter volcánico", "/es/articles/el-valle-de-anton", None), ("Bocas del Toro", "Islas del Caribe", "/es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama", None),
        ("San Blas", "Guna Yala", "/es/articles/san-blas-guna-yala-guia-tours-islas", None)]}
# (title, where it is, link, photo key in act_photo)
DOING = {
 "en": [("Hiking", "El Valle and Boquete", "/articles/hiking-in-panama-best-trails", "Hiking & Trails"),
        ("Birding and wildlife", "El Valle de Antón", "/articles/birding-el-valle-de-anton-trails-lodges-season", "Wildlife & Birding"),
        ("Surf and dive", "Venao and Santa Catalina", "/articles/panama-surf-camps", "Surf & Dive"),
        ("Food and coffee", "Boquete", "/articles/geisha-coffee-boquete-where-to-taste", "Food & Coffee"),
        ("City and culture", "Casco Viejo, Panama City", "/articles/casco-viejo-panama-walking-guide", "Cities & Culture"),
        ("Islands and beaches", "San Blas and Guna Yala", "/articles/san-blas-islands-panama-guna-yala-guide", "Islands & Beaches")],
 "es": [("Senderismo", "Boquete", "/es/articles/senderos-en-boquete-guia-completa", "Hiking & Trails"),
        ("Fauna y aves", "El Valle de Antón", "/es/articles/avistamiento-de-aves-el-valle-de-anton", "Wildlife & Birding"),
        ("Surf y buceo", "Coiba", "/es/articles/isla-coiba-buceo-parque-nacional", "Surf & Dive"),
        ("Comida y café", "Boquete", "/es/articles/tour-de-cafe-boquete-fincas-precios-reservar", "Food & Coffee"),
        ("Ciudad y cultura", "Ciudad de Panamá", "/es/articles/que-hacer-en-ciudad-de-panama", "Cities & Culture"),
        ("Islas y playas", "San Blas y Guna Yala", "/es/articles/san-blas-guna-yala-guia-tours-islas", "Islands & Beaches")]}
L = {"en": dict(file="home.html", title="Preview: Panama Spot homepage", en="/preview/home.html", es="/preview/home-es.html",
                dek="The complete guide to traveling in Panama — ten provinces, two coasts, written by people who live here.", cta="Start exploring →",
                where="Where in Panama?", what="What will you do?", fresh_h="Fresh guides", new="New guide", all="All guides →", guides="guides", read="Read the guide",
                bento="Seven Panamas, one isthmus.", guide_tag="Guide",
                dest=[("Panama City", "Capital and canal", "/articles/panama-city"), ("Boquete", "Coffee highlands", "/articles/boquete"),
                      ("El Valle de Antón", "Volcanic crater", "/articles/el-valle-de-anton"), ("Bocas del Toro", "Caribbean islands", "/articles/bocas-del-toro"),
                      ("San Blas", "Guna Yala", "/articles/san-blas-islands-panama-guna-yala-guide")],
                rows=[("BOQUETE_GUIDES", "Boquete", "Explore Boquete", "/articles/boquete"), ("EL_VALLE_GUIDES", "El Valle de Antón", "Explore El Valle de Antón", "/articles/el-valle-de-anton"),
                      ("PANAMA_CITY_GUIDES", "Panama City", "Explore Panama City", "/articles/panama-city")],
                new_list=["/articles/geisha-coffee-boquete-where-to-taste", "/articles/chorro-las-mozas-swimming-falls-el-valle", "/articles/san-blas-tours-from-panama-city",
                          "/articles/playa-venao-panama", "/articles/panama-canal-boat-tours", "/articles/el-pianista-trail-boquete"],
                new_photo={"/articles/san-blas-tours-from-panama-city": "/images/v2/isla-pelicano-san-blas-panama-sg105536-wide.webp"},
                mix=[("/articles/bocas-del-toro", "a", "Caribbean", "Bocas del Toro — nine islands, slow boats, sloths", "", "photo", "/images/v2/nyara-bocas-del-toro-panama-hero-1280.webp"),
                     ("/articles/san-blas-islands-panama-guna-yala-guide", "b", "Caribbean", "San Blas and Guna Yala", "", "photo", "/images/v2/x-diadup-kuna-yala-panam-c3-a1-hero-1280.webp"),
                     ("/articles/el-valle-de-anton", "c", "Highlands", "El Valle de Antón — a town inside an extinct volcano.", "Waterfalls, hot springs and the India Dormida ridge, two hours from the capital.", "navy", None),
                     ("/articles/chorro-el-macho-waterfall-el-valle-de-anton", "d", "Highlands", "Chorro El Macho, El Valle", "", "photo", None),
                     ("/articles/boquete", "e", "Highlands", "Boquete — cloud forest, coffee, Volcán Barú", "The highland town that runs on coffee, rivers, and fog — plus the country’s best day hikes from town.", "split", None),
                     ("/articles/panama-city", "f", "Capital", "Panama City", "", "photo", "/images/v2/panama-city-skyline-from-the-waterfront-17477516-hero-1280.webp"),
                     ("/articles/playa-venao-panama", "g", "Pacific coast", "Playa Venao and the Azuero coast", "", "photo", None)]),
     "es": dict(file="home-es.html", title="Vista previa: portada de Panama Spot", en="/preview/home.html", es="/preview/home-es.html",
                dek="La guía completa para viajar por Panamá — nueve provincias, tres costas, escrita por quienes vivimos aquí.", cta="Empieza a explorar →",
                where="¿En qué parte de Panamá?", what="¿Qué vas a hacer?", fresh_h="Guías nuevas", new="Guía nueva", all="Todas las guías →", guides="guías", read="Leer la guía",
                bento="Siete Panamás, un istmo.", guide_tag="Guía",
                dest=[("Ciudad de Panamá", "Capital y canal", "/es/articles/panama-city"), ("Boquete", "Tierras altas del café", "/es/articles/boquete"),
                      ("El Valle de Antón", "Cráter volcánico", "/es/articles/el-valle-de-anton"), ("Bocas del Toro", "Islas del Caribe", "/es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama"),
                      ("San Blas", "Guna Yala", "/es/articles/san-blas-guna-yala-guia-tours-islas")],
                rows=[("BOQUETE_GUIAS", "Boquete", "Explora Boquete", "/es/articles/boquete"), ("EL_VALLE_GUIAS", "El Valle de Antón", "Explora El Valle de Antón", "/es/articles/el-valle-de-anton"),
                      ("PANAMA_CITY_GUIAS", "Ciudad de Panamá", "Explora Ciudad de Panamá", "/es/articles/panama-city")],
                new_list=["/es/articles/tour-de-cafe-boquete-fincas-precios-reservar", "/es/articles/miradores-el-valle-de-anton", "/es/articles/sendero-los-quetzales-quetzal-boquete",
                          "/es/articles/senderismo-en-panama-mejores-senderos-ciudad", "/es/articles/cerro-la-silla-sendero-amanecer-el-valle", "/es/articles/lugares-turisticos-de-cocle"],
                new_photo={},
                # the Spanish library has few city guides: these three are about the city too
                row_extra={"PANAMA_CITY_GUIAS": [("Hoteles en Casco Viejo", "Guía", "/es/articles/hoteles-en-casco-viejo"),
                                                 ("Cómo llegar a Bocas", "Guía", "/es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama"),
                                                 ("Senderos cerca de la ciudad", "Senderismo", "/es/articles/senderismo-en-panama-mejores-senderos-ciudad")]},
                mix=[("/es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama", "a", "Caribe", "Bocas del Toro — nueve islas, lanchas lentas, perezosos", "", "photo", "/images/v2/nyara-bocas-del-toro-panama-hero-1280.webp"),
                     ("/es/articles/san-blas-guna-yala-guia-tours-islas", "b", "Caribe", "San Blas y Guna Yala", "", "photo", "/images/v2/x-diadup-kuna-yala-panam-c3-a1-hero-1280.webp"),
                     ("/es/articles/el-valle-de-anton", "c", "Tierras altas", "El Valle de Antón — un pueblo dentro de un volcán extinto.", "Cascadas, aguas termales y la cresta de la India Dormida, a dos horas de la capital.", "navy", None),
                     ("/es/articles/cascada-chorro-el-macho-el-valle-de-anton", "d", "Tierras altas", "Chorro El Macho, El Valle", "", "photo", None),
                     ("/es/articles/boquete", "e", "Tierras altas", "Boquete — bosque nuboso, café, Volcán Barú", "El pueblo de montaña que vive del café, los ríos y la neblina — y las mejores caminatas de un día del país.", "split", None),
                     ("/es/articles/panama-city", "f", "Capital", "Ciudad de Panamá", "", "photo", "/images/v2/panama-city-skyline-from-the-waterfront-17477516-hero-1280.webp"),
                     ("/es/articles/isla-coiba-buceo-parque-nacional", "g", "Pacífico", "Coiba y su parque nacional", "", "photo", None)])}

def build_home(lang):
    C = L[lang]; foot = donors(lang)["foot"]
    groups_ = {n: re.findall(r'href="(/(?:es/)?articles/[^"]+)">(.*?)</a>', ul) for n, ul in re.findall(r"<h4>(.*?)</h4><ul>(.*?)</ul>", foot, re.S)}
    def tile_img(u): return ROW_PHOTO.get(u) or (dest_img(u) if u in HUBS else img_of(u))
    def seven(name, group):
        cands = [(html.unescape(t), g, u) for t, g, u in cards_of(name, lang)] + [(html.unescape(t), C["guide_tag"], u) for u, t in groups_.get(group, [])] + C.get("row_extra", {}).get(name, [])
        for strict in (12, 4, 0):   # prefer clearly different photos; relax only if a row would come up short
            out, seen, pics = [], set(), []
            for t, g, u in cands:
                if len(out) >= 7: break
                if u in HUBS and strict > 4: continue  # the "All guides" link already goes to the hub; use it only to fill a short row
                im = tile_img(u)
                if u in seen or not im: continue
                key = look(im)
                if any(bin(key ^ k).count("1") <= strict for k in pics): continue
                seen.add(u); pics.append(key); out.append((t, g, u))
            if len(out) >= 7: return out
        return out
    rows = ""
    for name, group, h2, allhref in C["rows"]:
        cs = seven(name, group)
        if len(cs) < 7: print("short row:", lang, h2, len(cs)); continue
        rows += (f'<section class="wrap hx-sec"><div class="band-h"><div><h2>{h2}</h2></div><a href="{allhref}">{C["all"]}</a></div>'
                 f'<div class="hx-g7">{"".join(f'<a class="hx-t" href="{u}"><span class="ph"><img alt="" loading="lazy" src="{tile_img(u)}"/></span><b>{E(t)}</b><span class="c"><i class="dot"></i>{E(g)}</span></a>' for t, g, u in cs)}</div></section>')
    def mixcard(u, area, label, t, d, kind, im=None):
        if kind == "photo":
            return ptile(u, t, label, im or (dest_img(u) if u in HUBS else img_of(u)), desc=d).replace('class="hx-pt"', f'class="hx-pt m-{area}"', 1)
        if kind == "navy":
            return f'<a class="hx-navy m-{area}" href="{u}"><span class="lbl">{label}</span><b>{t}</b><p>{d}</p><span class="ar"></span></a>'
        im = dest_img(u)
        return (f'<a class="hx-split m-{area}" href="{u}"><span class="tx"><span class="c"><i class="dot"></i>{label}</span><b>{t}</b><p>{d}</p>'
                f'<span class="go">{C["read"]} <span class="ar"></span></span></span><span class="ph"><img alt="" loading="lazy" src="{im}"/></span></a>')
    def fresh(u):
        im = C["new_photo"].get(u) or img_of(u)
        return (f'<a class="hx-fr" href="{u}"><span class="hx-pt"><img alt="" loading="lazy" src="{im}"/><b>{title_of(u).split(":")[0]}</b><span class="ar"></span></span>'
                f'<span class="c"><i class="dot"></i>{C["new"]}</span><p>{E(dek_of(u))}</p></a>')
    acts = cards_of("ACTIVITIES", lang)
    body = f"""<div class="guide-progress" id="prog" aria-hidden="true"></div>
<header class="hero hx-home">
  {rot(lang)}
  {nav(C["en"], C["es"], lang)}
  <div class="wrap hx-c">
    <h1 class="hx-mark">Panam<span class="a">á</span><i class="pd"></i></h1>
    <p class="hx-dek">{C["dek"]}</p>
    <a class="hx-btn" href="#cat-regions">{C["cta"]}</a>
  </div>
</header>
<section class="wrap hx-sec" id="cat-regions"><div class="band-h"><div><h2>{C["where"]}</h2></div></div>
<div class="hx-g7 g6">{"".join(f'<a class="hx-t" href="{u}"><span class="ph"><img alt="" loading="lazy" src="{ph or (dest_img(u) if (u in HUBS or u in ES_TWIN) else img_of(u))}"/></span><b>{n}</b><span class="c"><i class="dot"></i>{t}</span></a>' for n, t, u, ph in PLACES[lang])}</div></section>
<div class="hx-band"><section class="wrap hx-sec" id="cat-activities"><div class="band-h"><div><h2>{C["what"]}</h2></div></div>
<div class="hx-dest hx-do">{"".join(f'<a class="hx-d" href="{u}"><img alt="" loading="lazy" src="{act_photo(k)}"/><span class="ft"><b>{n}</b><small>{w}</small></span></a>' for n, w, u, k in DOING[lang])}</div></section>
<section class="wrap hx-sec"><div class="band-h"><div><h2>{C["fresh_h"]}</h2></div></div>
<div class="hx-new">{"".join(fresh(u) for u in C["new_list"])}</div></section></div>
{rows}
<div class="hx-band bento"><section class="wrap hx-sec"><div class="band-h"><div><h2>{C["bento"]}</h2></div></div><div class="hx-mix">{"".join(mixcard(*m) for m in C["mix"])}</div></section></div>
"""
    out = page(C["title"], body + ROTJS, HOME_BG, lang, head="<!--SEO-HEAD-->")
    # the footer's opening band ("Find your spot in Panama", Start exploring, Where to next?) repeats the hero and "Where in Panama?" on the homepage
    out = re.sub(r'<div class="wrap f-top">.*?</div>', "", out, count=1, flags=re.S)
    out = re.sub(r'<div class="wrap f-dest">.*?</div></div>', "", out, count=1, flags=re.S)
    f = HOME_OUT / ("index.html" if lang == "en" else "es.html")
    f.write_text(finalize(out))
    print("wrote", f)
build_home("en"); build_home("es")
