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
    m = re.search(r'<img\b[^>]*class="hero-img"[^>]*>', h) or re.search(r'hub-hero-img"><img\b[^>]*>', h)
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
.hx-hero { height: clamp(300px, 27vw, 400px); }
/* homepage hero: the original layout (50vh, min 480px, wordmark bottom-left), new-template details */
.hx-home { height: 50vh; min-height: 480px; grid-template-rows: auto 1fr; }
.hx-home::before { background: linear-gradient(180deg, rgba(3,10,30,.42) 0%, rgba(3,10,30,0) 34%, rgba(3,10,30,.1) 60%, rgba(3,10,30,.5) 100%); }
.hx-home .hx-c { align-self: end; display: flex; flex-direction: column; align-items: flex-start; gap: 16px; padding-bottom: 56px; }
.hx-home .hx-mark { font: 400 clamp(64px, 11vw, 160px)/.86 var(--serif); letter-spacing: -0.02em; color: #fff; margin: 0; text-shadow: 0 2px 30px rgba(0,0,0,.18); }
.hx-mark .a { color: var(--red); }
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
.hx-home .hx-rot { opacity: 0; transition: opacity 1.6s ease; }
.hx-home .hx-rot.on { opacity: 1; }
/* homepage: 7-column destination grids */
.hx-g7 { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 14px; }
.hx-t { display: grid; gap: 4px; align-content: start; text-decoration: none; color: var(--ink); min-width: 0; }
.hx-t .ph { display: block; aspect-ratio: 1/1; border-radius: 16px; overflow: hidden; background: var(--beige); }
.hx-t img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .6s; }
.hx-t:hover img { transform: scale(1.05); }
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
.hx-pt:hover img { transform: scale(1.04); }
.hx-pt .lbl { color: #fff; font-size: 13px; }
.hx-pt b { font: 650 clamp(24px, 2vw, 30px)/1.08 var(--serif); padding-right: 56px; }
.hx-pt .ar { position: absolute; right: 18px; bottom: 18px; width: 40px; height: 40px; }
.hx-pt p { font: 400 14px/1.45 var(--sans); color: rgba(255,255,255,.88); padding-right: 56px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
/* red arrow circle; the glyph comes from --arw so the preview can swap styles */
:root { --arw: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m9 5.5 6.5 6.5L9 18.5'/%3E%3C/svg%3E"); }
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
.hx-navy b { font: 650 clamp(26px, 2.4vw, 36px)/1.08 var(--serif); padding-right: 60px; }
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
/* hub: icon facts */
.hb-icons { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; margin-top: 36px; text-align: center; max-width: 720px; }
.hb-icons > div { display: grid; justify-items: center; gap: 10px; }
.hb-icons .ic { width: 52px; height: 52px; border-radius: 50%; background: var(--red); display: grid; place-items: center; }
.hb-icons svg { width: 24px; height: 24px; color: #fff; }
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
.hb-g:hover img { transform: scale(1.04); }
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
.hb-gal { grid-template-columns: repeat(6, minmax(0, 1fr)); grid-template-rows: 300px 300px 340px; gap: 12px; background: none; }
.hb-gal figure { border-radius: 20px; overflow: hidden; }
.hb-gal figure img { transition: transform .8s ease; }
.hb-gal figure:hover img { transform: scale(1.05); }
.hb-gal figure:nth-child(1) { grid-column: 1 / 3; grid-row: 1 / 3; }
.hb-gal figure:nth-child(2) { grid-column: 3 / 5; grid-row: 1; } .hb-gal figure:nth-child(3) { grid-column: 5 / 7; grid-row: 1; }
.hb-gal figure:nth-child(4) { grid-column: 3 / 5; grid-row: 2; } .hb-gal figure:nth-child(5) { grid-column: 5 / 7; grid-row: 2; }
.hb-gal figure:nth-child(6) { grid-column: 1 / 4; grid-row: 3; } .hb-gal figure:nth-child(7) { grid-column: 4 / 7; grid-row: 3; }
.hb-gal figcaption { font-size: 13px; }
@media (max-width: 900px) { .hb-start { grid-template-columns: 1fr; } .hb-icons { grid-template-columns: repeat(3, minmax(0, 1fr)); row-gap: 22px; } .hb-gal { grid-template-columns: 1fr 1fr; grid-template-rows: none; grid-auto-rows: 200px; } .hb-gal figure:nth-child(n) { grid-column: auto; grid-row: auto; } .hb-gal figure:nth-child(1) { grid-column: 1 / -1; } }
@media (max-width: 1000px) { .hb-bento { grid-template-columns: 1fr; } .hb-bento.flip .hb-feat { order: 0; } .hb-feat { min-height: 320px; } .hb-more { grid-template-columns: 1fr 1fr; } .hb-g.s4 { grid-column: span 2; } .hb-icons { grid-template-columns: 1fr 1fr; } }
@media (max-width: 560px) { .hb-side, .hb-more { grid-template-columns: 1fr; grid-auto-rows: auto; } .hb-g.s2, .hb-g.s4 { grid-column: auto; } }
/* hub: the original layout, restyled */
.hb-hero { height: clamp(420px, 38vw, 540px); grid-template-rows: auto 1fr; }
.hb-hero::before { background: linear-gradient(180deg, rgba(3,10,30,.45) 0%, rgba(3,10,30,.05) 30%, rgba(3,10,30,.25) 58%, rgba(3,10,30,.72) 100%); }
.hb-hero > .wrap:last-of-type { align-self: end; }
.hb-hero .hb-c { display: grid; gap: 14px; padding-bottom: 44px; max-width: 760px; margin: 0; }
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
.hb-group { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: clamp(28px, 4vw, 64px); align-items: center; }
.hb-group + .hb-group { margin-top: 64px; }
.hb-group .gi img { width: 100%; aspect-ratio: 4/3; object-fit: cover; border-radius: 22px; display: block; }
.hb-group h2 { font: 650 clamp(30px, 2.8vw, 40px)/1.05 var(--serif); }
.hb-group .bl { font-size: 17px; line-height: 1.55; color: var(--body); margin: 10px 0 18px; max-width: 56ch; }
.hb-list { list-style: none; padding: 0; margin: 0; border-top: 2px solid var(--navy); }
.hb-list a { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr) 28px; gap: 18px; align-items: baseline; padding: 14px 6px; border-bottom: 1px solid var(--line); text-decoration: none; transition: background .2s; }
.hb-list a:hover { background: var(--beige); }
.hb-list b { font: 700 16.5px/1.3 var(--sans); color: var(--navy); }
.hb-list span { font-size: 14.5px; line-height: 1.45; color: var(--muted); }
.hb-list i { font-style: normal; color: var(--red); justify-self: end; }
@media (max-width: 900px) { .hb-orient, .hb-group { grid-template-columns: 1fr; } .hb-list a { grid-template-columns: 1fr 24px; } .hb-list span { grid-column: 1; } .hb-list i { grid-row: 1; grid-column: 2; } }
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
.hx-card .go .ar { width: 28px; height: 28px; }
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
{PICK}
{D["js"].replace('var art = document.getElementById("article")', 'var art = document.getElementById("article") || document.body')}
<script src="/js/search.js" defer></script>
</body></html>
"""


def nav(en, es, lang="en"):
    n = D["nav"]
    n = re.sub(r'<span class="lang glass">.*?</span>', f'<span class="lang glass"><a class="on" href="{en}" hreflang="en">EN</a><a href="{es}" hreflang="es">ES</a></span>', n, flags=re.S)
    return re.sub(r'<span class="search glass">(.*?)</span></span>', lambda m: f'<a class="search glass" href="/#cat-regions" data-search aria-haspopup="dialog">{m[1]}</span></a>', n, flags=re.S)


def ptile(u, t, label, im=None, desc=""):
    return f'<a class="hx-pt" href="{u}"><img alt="" loading="lazy" src="{im or img_of(u)}"/><span class="lbl">{label}</span><b>{t}</b>{f'<p>{E(desc)}</p>' if desc else ''}<span class="ar"></span></a>'

def card(href, title, desc="", chip="", label="Guide", more=False):
    im = img_of(href)
    ph = f'<span class="ph"><img alt="" loading="lazy" src="{im}"/>' + (f'<span class="chip glass">{E(chip)}</span>' if chip else "") + "</span>"
    return (f'<a class="hx-card" href="{href}">{ph}<span class="tx"><span class="c"><i class="dot"></i>{label}</span><h3>{E(title)}</h3>'
            + (f"<p>{E(desc)}</p>" if desc else "") + ('<span class="go">Read the guide <span class="ar"></span></span>' if more else "") + "</span></a>")


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
HB = re.search(r'<div class="hub-hero-img"><img src="([^"]+)"[^>]*alt="([^"]*)"', b)
eyebrow = re.search(r'<p class="hub-eyebrow">(.*?)</p>', b)[1]
start_img = re.findall(r'<a class="hub-card" href="[^"]+"><div class="hub-card-img"><img src="([^"]+)"', b)
def hcard(u, t, d, im):
    return (f'<a class="hx-card" href="{u}"><span class="ph"><img alt="" loading="lazy" src="{im}"/></span><span class="tx"><span class="c"><i class="dot"></i>Guide</span>'
            f'<h3>{t}</h3><p>{d}</p><span class="go">Read the guide <i>→</i></span></span></a>')
ICO = {
 "mountain": '<path d="m3 20 6.5-11 4 6.5 2.5-4L21 20Z"/>',
 "pin": '<path d="M12 21s7-6.2 7-11.5a7 7 0 0 0-14 0C5 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>',
 "bus": '<rect x="4" y="3" width="16" height="15" rx="3"/><path d="M4 11h16M8 21v-3M16 21v-3"/><circle cx="8" cy="14.5" r=".8"/><circle cx="16" cy="14.5" r=".8"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 "cal": '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/>',
 "book": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2Z"/><path d="M4 19V5"/>'}
ICO["peak"] = '<path d="m2 20 7-12 3.5 5.5L15 10l7 10Z"/><path d="M7.5 11.5 9 13l1.5-1.5"/>'
icon = lambda k: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICO[k]}</svg>'
# every value below is taken from the hub's own text
ICONS = [("mountain", "1,200 m", "Elevation"), ("pin", "Chiriquí", "Province"), ("peak", "3,475 m", "Volcán Barú"),
         ("bus", "1 hr", "To the Costa Rican border"), ("book", f"{len(idx)} guides", "In this library")]
GLANCE = [("Getting there", "Fly to David", "then 45 min by road; 7 hrs by bus"), ("When to go", "Dec–Apr", "driest months; mist any time"),
          ("How long", "3 days", "a fourth for Volcán Barú"), ("Getting around", "Walk town", "bike, taxi or car beyond it")]
icons_html = '<div class="hb-icons">' + "".join(f"<div><span class=\"ic\">{icon(k)}</span><span><b>{v}</b><span>{l}</span></span></div>" for k, v, l in ICONS) + "</div>"
def gcard(u, n, d, extra=""):
    return f'<a class="hb-g" href="{u}"{extra}><span class="ph"><img alt="" loading="lazy" src="{img_of(u)}"/><span class="ar"></span></span><span class="tx"><b>{n}</b><span class="d">{d}</span></span></a>'
groups_html = ""
for gi, g in enumerate(groups):
    it = g["items"]; n = len(it)
    if n <= 4:
        cells = "".join(gcard(u, t, d) for u, t, d in it)
        if n < 4:  # the empty slots become one link to the full list, so every card keeps the same size
            cells += f'<a class="hb-all" href="#all-guides" style="grid-column: span {4 - n if n > 1 else 2}"><span>All {len(idx)} Boquete guides</span><span class="ar"></span></a>'
    else:
        cells = "".join(gcard(u, t, d) for u, t, d in it[:3])
        cells += f'<button class="hb-all" type="button" data-more><span>See all {n} guides</span><small>+{n - 3} more</small><span class="ar"></span></button>'
        cells += "".join(gcard(u, t, d, ' hidden data-x') for u, t, d in it[3:])
    groups_html += (f'<div class="hb-cat"><div class="num">{gi + 1:02d} · {E(g["h2"])}</div><div class="hb-bento{" flip" if gi % 2 else ""}"><div class="hb-feat"><img alt="{html.escape(html.unescape(g["alt"]))}" loading="lazy" src="{g["img"]}"/>'
                    f'<span class="lbl">{n} guides</span><h2>{g["h2"]}</h2><p>{g["blurb"]}</p></div><div class="hb-side">{cells}</div></div></div>')
MOREJS = """<script>document.querySelectorAll("[data-more]").forEach(function(b){b.addEventListener("click",function(){b.parentElement.querySelectorAll("[data-x]").forEach(function(a){a.hidden=false;});b.remove();});});</script>"""
GAL = [("/images/v2/volcan-baru-emerging-through-clouds-d35d9b87-hero-1280.webp", "Volcán Barú rising through cloud above forested slopes."),
       ("/images/v2/resplendent-quetzal-646deb1a-gallery.webp", "A resplendent quetzal, the bird most birders come to Boquete for."),
       ("/images/v2/finca-lerida-boquete-panama-wide.webp", "Finca Lérida, one of the Boquete farms that pours Geisha."),
       ("/images/boquete/boquete-rafting.webp", "Rafters in yellow boats on a river near Boquete."),
       ("/images/boquete/boquete-cabins.webp", "Timber A-frame cabins on a hillside above Boquete."),
       ("/images/boquete/boquete-market.webp", "Fruit and vegetables for sale at a market stall in Boquete."),
       ("/images/boquete/boquete-clouds.webp", "Bajareque mist rolling through the Boquete valley.")]
gal_html = "".join(f'<figure><img class="ph" alt="{a}" loading="lazy" src="{u}"/><figcaption>{a}</figcaption></figure>' for u, a in GAL)
hub = f"""<div class="guide-progress" id="prog" aria-hidden="true"></div>
<header class="hero hb-hero">
  <img class="hero-img" alt="{html.escape(html.unescape(HB[2]))}" fetchpriority="high" src="{HB[1]}" style="object-position:center 45%"/>
  {nav("/preview/boquete-hub.html", "/es/articles/boquete")}
  <div class="wrap"><div class="hb-c">
    <span class="lbl">{eyebrow}</span>
    <h1>Boquete</h1>
    <p>{dek}</p>
    <div class="hb-pills">{"".join(f'<span class="chip glass">{E(p)}</span>' for p in pills)}</div>
  </div></div>
</header>
<section class="wrap hb-sec first"><div class="hb-orient"><div class="lead">{"".join(f"<p>{l}</p>" for l in leads[:1])}{icons_html}</div>
<aside class="glance hb-glance" aria-label="At a glance"><h2>At a glance <span><i class="dot"></i>Chiriquí highlands</span></h2><div class="gg">{"".join(f'<div><span class="k">{k}</span><b class="sm">{v}</b><span class="s">{x}</span></div>' for k, v, x in GLANCE)}</div></aside></div></section>
<section class="wrap hb-sec"><div class="hb-head"><span class="lbl">Start here</span><h2>{s_head[1]}</h2><p>{s_head[2]}</p></div>
<div class="hb-start">{"".join(ptile(u, R.text(t), "Read first", im) for (u, t, d), im in zip(start, start_img))}</div></section>
<section class="wrap hb-sec"><div class="hb-head"><span class="lbl">By topic</span><h2>Find your guide</h2></div>{groups_html}</section>
<section class="wrap hb-sec">{cta["banner"]}</section>
<section class="wrap hb-sec"><div class="band-h"><div><span class="lbl">In pictures</span><h2>Boquete in pictures</h2></div></div><div class="gal hb-gal">{gal_html}</div></section>
<section class="wrap hb-sec last" id="all-guides"><div class="band-h"><div><span class="lbl">{idx_h[1]}</span><h2>{idx_h[2]}</h2></div><span class="band-sub">{len(idx)} guides</span></div>
<ol class="hx-idx">{"".join(f'<li><a href="{u}"><span class="n">{n}</span><span>{t}</span><span class="cat">{c}</span></a></li>' for u, n, t, c in idx)}</ol>
<div class="hx-es"><span class="bdg">ES</span><div><b>{es_t[1]}</b><p>{es_t[2]}</p></div><a href="/es/articles/boquete">Ver en español →</a></div></section>
{ROLL.JS_M[0]}{ROLL.TRACK}{ROLL.JS_M[1]}
{MOREJS}
"""
(OUT / "boquete-hub.html").write_text(page("Preview: Boquete hub", hub, HB[1]))

ARROWS = """<script>document.querySelectorAll(".hx-rw").forEach(function(w){var r=w.querySelector(".hx-row"),l=w.querySelector(".hx-arr.l"),n=w.querySelector(".hx-arr.r");
function st(){l.disabled=r.scrollLeft<4;n.disabled=r.scrollLeft+r.clientWidth>=r.scrollWidth-4;}
l.onclick=function(){r.scrollBy({left:-r.clientWidth*.8,behavior:"smooth"})};n.onclick=function(){r.scrollBy({left:r.clientWidth*.8,behavior:"smooth"})};
r.addEventListener("scroll",st,{passive:true});addEventListener("resize",st);st();});</script>"""
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
HOME_BG = "https://images.pexels.com/photos/2474690/pexels-photo-2474690.jpeg?auto=compress&cs=tinysrgb&w=2400"
ROT_IMGS = [(HOME_BG, "", 50)] + [(f"/images/v2/{n}-hero-1920.webp", a, y) for n, a, y in [
    ("playa-blanca-saboga", "Palm trees over Playa Blanca on Isla Saboga, Pearl Islands.", 62),
    ("volcan-baru-emerging-through-clouds-d35d9b87", "Volcán Barú rising through cloud above forested slopes.", 40),
    ("isla-en-guna-yala", "A palm-lined beach on an island in Guna Yala.", 55),
    ("panama-city-skyline-from-the-waterfront-17477516", "The Panama City skyline seen across the water.", 55),
    ("aerial-view-of-boquete-panama-ed675378", "Boquete in its river valley, seen from the air.", 55),
    ("late-light-on-the-crater-wall-a262b398", "Late light on the crater wall above El Valle de Antón.", 60)]]
ROT = "".join(f'<img class="hero-img hx-rot{" on" if i == 0 else ""}" alt="{a}" {"fetchpriority=" + chr(34) + "high" + chr(34) + " src" if i == 0 else "data-src"}="{u}" style="object-position:center {y}%"/>' for i, (u, a, y) in enumerate(ROT_IMGS))
ROTJS = """<script>(function(){var im=[].slice.call(document.querySelectorAll(".hx-rot"));if(im.length<2||matchMedia("(prefers-reduced-motion: reduce)").matches)return;
addEventListener("load",function(){im.forEach(function(i){if(i.dataset.src)i.src=i.dataset.src;});var k=0;setInterval(function(){var n=(k+1)%im.length;if(!im[n].complete)return;im[k].classList.remove("on");im[n].classList.add("on");k=n;},6000);});})();</script>"""
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
FOOT_GROUPS = {n: re.findall(r'href="(/articles/[^"]+)">(.*?)</a>', ul) for n, ul in re.findall(r"<h4>(.*?)</h4><ul>(.*?)</ul>", D["foot"], re.S)}
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
HUBS = {"/articles/boquete", "/articles/el-valle-de-anton", "/articles/panama-city", "/articles/bocas-del-toro"}
def seven(name, group):
    cands = [(html.unescape(t), g, u) for t, g, u in (cards_of(name) if name else [])] + [(html.unescape(t), "Guide", u) for u, t in FOOT_GROUPS.get(group, [])]
    for strict in (12, 4):
        if strict == 4: cands = cands[:]  # second pass: hubs allowed   # prefer clearly different photos; relax only if a row would come up short
        out, seen, pics = [], set(), []
        for t, g, u in cands:
            if len(out) >= 7: break
            if u in HUBS and strict > 4: continue  # the "All guides" link already goes to the hub; use it only to fill a short row
            im = dest_img(u) if u in HUBS else img_of(u)
            if u in seen or not im: continue
            key = look(im)
            if any(bin(key ^ k).count("1") <= strict for k in pics): continue
            seen.add(u); pics.append(key); out.append((t, g, u))
        if len(out) >= 7: return out
    return out
rows = ""
for name, group, h2, allhref in [("BOQUETE_GUIDES", "Boquete", "Explore Boquete", "/articles/boquete"), ("EL_VALLE_GUIDES", "El Valle de Antón", "Explore El Valle de Antón", "/articles/el-valle-de-anton"),
                                 ("PANAMA_CITY_GUIDES", "Panama City", "Explore Panama City", "/articles/panama-city"), (None, "Bocas del Toro", "Explore Bocas del Toro", "/articles/bocas-del-toro"),
                                 (None, "Islands and sea", "Explore San Blas and the islands", "/articles/san-blas-islands-panama-guna-yala-guide")]:
    cs = seven(name, group)
    if len(cs) < 7: continue
    rows += (f'<section class="wrap hx-sec"><div class="band-h"><div><span class="lbl">Destination</span><h2>{h2}</h2></div><a href="{allhref}">All guides →</a></div>'
             f'<div class="hx-g7">{"".join(f'<a class="hx-t" href="{u}"><span class="ph"><img alt="" loading="lazy" src="{dest_img(u) if u in HUBS else img_of(u)}"/></span><b>{E(t)}</b><span class="c"><i class="dot"></i>{E(g)}</span></a>' for t, g, u in cs)}</div></section>')
def dek_of(href):
    t = (P / (href.lstrip("/") + ".html")).read_text(errors="ignore"); m = re.search(r'<p class="dek">(.*?)</p>', t, re.S); s = R.text(m[1]) if m else ""
    return s if len(s) < 150 else s[:150].rsplit(" ", 1)[0] + "…"
def mixcard(u, area, label, t, d, kind):
    if kind == "photo":
        return ptile(u, t, label, dest_img(u) if u in HUBS else img_of(u), desc=d).replace('class="hx-pt"', f'class="hx-pt m-{area}"', 1)
    if kind == "navy":
        return f'<a class="hx-navy m-{area}" href="{u}"><span class="lbl">{label}</span><b>{t}</b><p>{d}</p><span class="ar"></span></a>'
    im = dest_img(u) if u in HUBS else img_of(u)
    return (f'<a class="hx-split m-{area}" href="{u}"><span class="tx"><span class="c"><i class="dot"></i>{label}</span><b>{t}</b><p>{d}</p>'
            f'<span class="go">Read the guide <span class="ar"></span></span></span><span class="ph"><img alt="" loading="lazy" src="{im}"/></span></a>')
MIX = "".join([
    mixcard("/articles/bocas-del-toro", "a", "Caribbean", "Bocas del Toro — nine islands, slow boats, sloths", "Surfers’ capital of the Caribbean coast, Afro-Antillean kitchens, and the country’s easiest place to wake up on the water.", "photo"),
    mixcard("/articles/san-blas-islands-panama-guna-yala-guide", "b", "Caribbean", "San Blas and Guna Yala", dek_of("/articles/san-blas-islands-panama-guna-yala-guide"), "photo"),
    mixcard("/articles/el-valle-de-anton", "c", "Highlands", "El Valle de Antón — a town inside an extinct volcano.", "Waterfalls, hot springs and the India Dormida ridge, two hours from the capital.", "navy"),
    mixcard("/articles/pearl-islands-panama-guide", "d", "Pacific", "The Pearl Islands", dek_of("/articles/pearl-islands-panama-guide"), "photo"),
    mixcard("/articles/boquete", "e", "Highlands", "Boquete — cloud forest, coffee, Volcán Barú", "The highland town that runs on coffee, rivers, and fog — plus the country’s best day hikes from town.", "split"),
    mixcard("/articles/panama-city", "f", "Capital", "Panama City", "Casco Viejo, the canal and the causeway, and the best day trips out of town.", "photo"),
    mixcard("/articles/playa-venao-panama", "g", "Pacific coast", "Playa Venao and the Azuero coast", dek_of("/articles/playa-venao-panama"), "photo"),
])
new = ["/articles/geisha-coffee-boquete-where-to-taste", "/articles/chorro-las-mozas-swimming-falls-el-valle", "/articles/san-blas-tours-from-panama-city",
       "/articles/playa-venao-panama", "/articles/panama-canal-boat-tours", "/articles/el-pianista-trail-boquete"]
home = f"""<div class="guide-progress" id="prog" aria-hidden="true"></div>
<header class="hero hx-home">
  {ROT}
  {nav("/preview/home.html", "/es")}
  <div class="wrap hx-c">
    <h1 class="hx-mark">Panam<span class="a">á</span><i class="pd"></i></h1>
    <p class="hx-dek">The complete guide to traveling in Panama — ten provinces, two coasts, written by people who live here.</p>
    <a class="hx-btn" href="#cat-regions">Start exploring →</a>
  </div>
</header>
<section class="wrap hx-sec" id="cat-regions"><div class="band-h"><div><span class="lbl">Destinations</span><h2>Where in Panama?</h2></div><a href="/articles/best-time-to-visit-panama">Plan your trip →</a></div>
<div class="hx-dest">{"".join(f'<a class="hx-d" href="{u}"><img alt="" loading="lazy" src="{dest_img(u)}"/><span class="chip glass">{count(u)} guides</span><span class="ft"><b>{n}</b><small>{s}</small></span></a>' for n, s, u in dest)}</div></section>
<section class="wrap hx-sec" id="cat-activities"><div class="band-h"><div><span class="lbl">Activities</span><h2>What will you do?</h2></div></div>
<div class="hx-acts">{"".join(f'<a class="hx-act" href="{u}"><img alt="" loading="lazy" src="{img_of(act_img.get(html.unescape(t), u))}"/><b>{E(t)}</b></a>' for t, g, u in acts)}</div></section>
<section class="wrap hx-sec"><div class="band-h"><div><span class="lbl">New on Panama Spot</span><h2>Fresh guides</h2></div></div>
<div class="hx-new">{"".join(ptile(u, title_of(u).split(":")[0], "New guide", desc=dek_of(u)) for u in new)}</div></section>
{rows}
<section class="wrap hx-sec"><div class="band-h"><div><span class="lbl">Field reports from the ground</span><h2>Seven Panamas, one isthmus.</h2></div><a href="/#cat-regions">All destinations →</a></div><div class="hx-mix">{MIX}</div></section>
"""
(OUT / "home.html").write_text(page("Preview: Panama Spot homepage", home + ROTJS, HOME_BG))
print("wrote", OUT / "boquete-hub.html", OUT / "home.html")
