"""Build V2 guide previews with E-Valley Bikes CTAs. Copy lives in copy.json (one set per region + language).

Four placements, same as the live guides:
  1. banner  - end of section 1
  2. offer   - end of section 3 (the three rides)
  3. rail    - right rail, under "Need to know" (which keeps KNOW_MAX bullets)
  4. closer  - after the photo gallery, before "More guides"

Facts checked against evalleybikes.net on 2026-11-03. No prices (user, 2026-11-04).
Every button and card opens WhatsApp (wa.me, pre-filled message, no tracking codes in the text),
rel="sponsored noopener" because E-Valley is a paying partner.
Reviews must be verbatim from evalleybikes.net (or a checked Google/Tripadvisor page). No faces: the site shows none.
copy.json closer.review_verified=false renders a red UNVERIFIED tag; never ship one.

Usage: python3 design/evalley-cta/build.py
"""
import html as H
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SITE = "https://panamaspot.com"
KNOW_MAX = 3
COPY = json.loads((OUT / "copy.json").read_text())
NOT_LIVE = ("/images/el-valle/elvalle-elmachowaterfall3.webp", "/images/v2/evalley-")  # new files, served from disk in previews until deployed

CSS = r"""
/* ===== E-Valley Bikes partner blocks (V2 type and shapes, E-Valley colours) ===== */
/* Boquete: buttons + pills #2f7a4f, every dot (labels, lists, rating) bright funnel green #25D366. No orange anywhere.
   El Valle: buttons + pills + dots terra #C34D1E (funnel). Light blocks use the page's own --beige. */
.evx { --ev-deep:#102A22; --ev-deep-2:#0b2019; --ev-acc:#25D366; --ev-dot:#25D366; --ev-star:#25D366; --ev-act:#2f7a4f; --ev-act-d:#24613d; --ev-act-ink:#fff; --ev-act-i:rgba(255,255,255,.18);
  --ev-paper:#F4F2EA; --ev-cloud:#E5E8DF; --ev-gold:#D6A23E; --ev-ink:#1b2621; --ev-soft:#40504a; --ev-muted:#5c665f;
  --ev-ring: rgba(27,38,33,.10); font-family: var(--sans); }
.evx.ev-valle { --ev-act:#C34D1E; --ev-act-d:#a63e17; --ev-act-ink:#fff; --ev-act-i:rgba(255,255,255,.18); --ev-dot:#C34D1E; --ev-star:#C34D1E; --ev-deep:#352d10; --ev-deep-2:#241d0a; --ev-acc:#C34D1E; --ev-cloud:#EFE3D6; --ev-soft:#4d4433; --ev-muted:#6b6250; }
.evx a { text-decoration: none; }
.ev-lbl { display: inline-flex; align-items: center; gap: 8px; font: 600 13.5px/1.2 var(--sans); color: var(--ev-ink); flex-wrap: wrap; }
.ev-lbl::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--ev-acc); flex: none; }
.ev-tag { font: 600 11.5px/1 var(--sans); color: var(--ev-muted); padding: 5px 9px; border-radius: 999px; box-shadow: inset 0 0 0 1px var(--ev-ring); }
.ev-dark .ev-lbl { color: #fff; } .ev-dark .ev-lbl::before { background: var(--ev-dot); }
.ev-dark .ev-tag { color: rgba(255,255,255,.72); box-shadow: inset 0 0 0 1px rgba(255,255,255,.22); }
.ev-t { font: 700 clamp(26px, 2.4vw, 32px)/1.06 var(--serif); color: var(--ev-deep); letter-spacing: 0; text-wrap: balance; margin: 0; }
.ev-dark .ev-t { color: #fff; }
.ev-p { font-size: 16px; line-height: 1.6; color: var(--ev-soft); margin: 0; }
.ev-dark .ev-p { color: rgba(255,255,255,.78); }
.ev-btn { display: inline-flex; align-items: center; gap: 12px; background: var(--ev-act); color: var(--ev-act-ink) !important; font: 700 15px/1 var(--sans);
  padding: 8px 8px 8px 20px; border-radius: 999px; transition: background .15s; white-space: nowrap; }
.ev-btn i svg { width: 17px; height: 17px; fill: currentColor; }
.ev-btn i { font-style: normal; width: 32px; height: 32px; border-radius: 50%; background: var(--ev-act-i); display: grid; place-items: center; font-size: 15px; }
.ev-btn:hover { background: var(--ev-act-d); }
.ev-stars { display: inline-flex; gap: 3px; vertical-align: middle; }
.ev-stars i { width: 8px; height: 8px; border-radius: 50%; background: var(--ev-star); }
.ev-micro { display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 13.5px; color: var(--ev-muted); line-height: 1.4; }
.ev-dark .ev-micro { color: rgba(255,255,255,.72); }
.ev-row { display: flex; align-items: center; gap: 12px 18px; flex-wrap: wrap; }

/* 1. Banner */
.ev-banner { display: grid; grid-template-columns: minmax(0, .9fr) minmax(0, 1.2fr); background: var(--beige); border-radius: 22px; overflow: hidden; margin-top: 30px; }
.ev-banner .ev-ph { position: relative; min-height: 260px; }
.ev-banner .ev-ph img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.ev-banner .ev-bd { padding: 24px 28px 26px; display: grid; gap: 12px; align-content: center; }
@media (max-width: 640px) { .ev-banner { grid-template-columns: 1fr; } .ev-banner .ev-ph { min-height: 0; aspect-ratio: 16/10; } .ev-banner .ev-bd { padding: 20px 20px 22px; } }

/* 2. The three rides */
.ev-offer { background: var(--ev-deep); color: #fff; border-radius: 26px; padding: clamp(22px, 3.4vw, 34px); display: grid; gap: 22px; margin-top: 30px; }
.ev-offer .ev-hd { display: grid; gap: 10px; max-width: 58ch; }
.ev-offer .ev-t { font-size: clamp(30px, 3vw, 38px); }
.ev-cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.ev-card { background: var(--beige); border-radius: 18px; padding: 8px; display: grid; grid-template-rows: auto 1fr; color: var(--ev-ink); transition: transform .2s; }
.ev-card:hover { transform: translateY(-2px); }
.ev-card .ev-ph { position: relative; aspect-ratio: 4/3; border-radius: 12px; overflow: hidden; }
.ev-card .ev-ph img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.ev-card .ev-pill { position: absolute; left: 8px; top: 8px; font: 700 12px/1 var(--sans); padding: 7px 10px; border-radius: 999px; color: var(--ev-act-ink); }
.ev-card .ev-pill.top { background: var(--ev-act); }
.ev-card .ev-tx { padding: 12px 8px 8px; display: grid; gap: 6px; align-content: start; }
.ev-card b { font: 700 18px/1.25 var(--sans); color: var(--ev-deep); letter-spacing: -0.01em; }
.ev-card p { font-size: 14.5px; line-height: 1.5; color: var(--ev-soft); margin: 0; }
.ev-card .ev-meta { display: flex; flex-wrap: wrap; gap: 4px 12px; font: 600 12.5px/1.3 var(--sans); color: var(--ev-muted); margin-top: 2px; }
.ev-card .ev-meta span { display: inline-flex; align-items: center; gap: 6px; }
.ev-card .ev-meta span::before { content: ""; width: 5px; height: 5px; border-radius: 50%; background: var(--ev-acc); }
.ev-trust { display: flex; flex-wrap: wrap; gap: 8px 18px; list-style: none; padding: 0; margin: 0; font-size: 13.5px; color: rgba(255,255,255,.8); }
.ev-trust li { display: inline-flex; align-items: center; gap: 8px; }
.ev-trust li::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--ev-dot); }
@media (max-width: 760px) {
  .ev-cards { grid-template-columns: 1fr; }
  .ev-card { grid-template-columns: 116px 1fr; grid-template-rows: auto; gap: 4px; }
  .ev-card .ev-ph { aspect-ratio: auto; min-height: 112px; }
  .ev-card .ev-pill { font-size: 11px; padding: 5px 8px; left: 6px; top: 6px; }
  .ev-card .ev-tx { padding: 6px 8px 6px 10px; }
}

/* 3. Rail card. On pages with the ad, the rail's gaps tighten so postmark, Need to know and the ad sit evenly spaced in one viewport */
.rail-in:has(.ev-rail) { gap: 24px; }
.ev-rail { background: var(--beige); border-radius: 18px; padding: 8px; display: grid; gap: 4px; color: var(--ev-ink); }
.ev-rail .ev-ph { position: relative; aspect-ratio: 5/2; border-radius: 12px; overflow: hidden; }
.ev-rail .ev-ph img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.ev-valle.ev-rail .ev-ph img { object-position: center 62%; }
.ev-valle.ev-rail .ev-ph img[src*="bike-crater"] { object-position: center 72%; }
.ev-rail .ev-ph .chip { position: absolute; left: 8px; bottom: 8px; font-size: 12px; padding: 7px 10px; gap: 6px; }
.ev-rail .ev-bd { padding: 10px 10px 8px; display: grid; gap: 8px; }
.ev-rail .ev-t { font-size: 22px; }
.ev-rail .ev-p { font-size: 13.5px; line-height: 1.5; }
.ev-rail .ev-btn { justify-content: space-between; font-size: 14px; padding: 6px 6px 6px 16px; margin-top: 2px; }
.ev-rail .ev-btn i { width: 28px; height: 28px; font-size: 14px; }

/* 4. Closer, between the gallery and "More guides" */
.ev-closer { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); background: var(--ev-deep); color: #fff; border-radius: 28px; overflow: hidden; }
.ev-closer .ev-bd { padding: clamp(28px, 4vw, 56px); display: grid; gap: 18px; align-content: center; }
.ev-closer .ev-t { font-size: clamp(34px, 3.4vw, 48px); line-height: 1.02; }
.ev-closer .ev-ph { position: relative; min-height: 420px; }
.ev-closer .ev-ph img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.ev-rev { margin: 2px 0 0; padding: 16px 18px; border-radius: 16px; background: rgba(255,255,255,.07); display: grid; gap: 10px; }
.ev-rev-hd { display: flex; align-items: center; gap: 10px; }
.ev-rev-hd .ev-av { width: 40px; height: 40px; border-radius: 50%; flex: none; display: grid; place-items: center; background: rgba(255,255,255,.16); color: #fff; font: 700 16px/1 var(--sans); }
.ev-unv { display: block; background: #da121a; color: #fff; font: 800 12.5px/1.35 var(--sans); letter-spacing: .05em; text-transform: uppercase; padding: 9px 12px; border-radius: 8px; }
.ev-rev-hd .ev-who b { display: block; font: 600 14.5px/1.2 var(--sans); color: #fff; }
.ev-rev-hd .ev-src { display: block; font-size: 12.5px; color: rgba(255,255,255,.6); margin-top: 2px; }
.ev-rev blockquote { margin: 0; font: 500 16.5px/1.55 var(--sans); color: #fff; }
.ev-closer .ev-trust { margin-top: 2px; }
.ev-p strong { font-weight: 700; color: var(--ev-deep); }
.ev-dark .ev-p strong { color: #fff; }
.ev-pp { display: grid; gap: 10px; }
.ev-inc { display: grid; gap: 8px; }
.ev-inc-t { font: 600 14.5px/1.3 var(--sans); color: rgba(255,255,255,.92); }
.ev-inc ul { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 8px 22px; font-size: 15px; line-height: 1.45; color: rgba(255,255,255,.82); }
.ev-inc li { display: inline-flex; align-items: center; gap: 8px; }
.ev-inc li::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--ev-dot); flex: none; }
.ev-steps { display: grid; gap: 12px; }
.ev-steps-t { font: 700 12px/1 var(--sans); letter-spacing: .09em; text-transform: uppercase; color: rgba(255,255,255,.62); }
.ev-steps ol { counter-reset: evs; list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
.ev-steps li { counter-increment: evs; display: grid; grid-template-columns: 30px minmax(0, 1fr); gap: 12px; align-items: start; font-size: 16px; line-height: 1.5; color: rgba(255,255,255,.86); }
.ev-steps li::before { content: counter(evs); width: 30px; height: 30px; border-radius: 50%; background: var(--ev-act); color: #fff; display: grid; place-items: center; font: 700 14px/1 var(--sans); margin-top: -2px; }
.ev-rstars { display: inline-flex; gap: 2px; margin-left: auto; align-self: flex-start; margin-top: 2px; }
.ev-rstars svg { width: 16px; height: 16px; fill: #F5B301; }
@media (max-width: 860px) { .ev-closer { grid-template-columns: 1fr; } .ev-closer .ev-ph { min-height: 0; aspect-ratio: 16/10; order: -1; } }
"""

STARS = '<span class="ev-stars" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>'
WA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/></svg>'
E = H.escape
RSTAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6L2.5 9.4l6.6-.8z"/></svg>'


def rich(s):
    """Escape, then **bold** -> <strong>, newline -> <br>."""
    out = E(s)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return out.replace("\n", "<br>")


def paras(s, cls="ev-p"):
    """Blank line = new paragraph."""
    if not s:
        return ""
    ps = [f'<p class="{cls}">{rich(x)}</p>' for x in s.split("\n\n")]
    return ps[0] if len(ps) == 1 else '<div class="ev-pp">' + "".join(ps) + "</div>"


VARIANT_W = (640, 1000)
SIZES = {
    "banner": "(max-width: 640px) 100vw, 330px",
    "card": "(max-width: 760px) 116px, 240px",
    "rail": "280px",
    "closer": "(max-width: 860px) 100vw, 680px",
}


def variants(src):
    """Right-sized copies in /images/v2/evalley-<stem>-<w>.webp (made on first use, never wider than the source)."""
    import subprocess
    srcf = ROOT / "public" / src.lstrip("/")
    w0 = int(subprocess.run(["magick", "identify", "-format", "%w", str(srcf)], capture_output=True, text=True).stdout)
    out = []
    for w in VARIANT_W:
        w = min(w, w0)
        if out and out[-1][0] == w:
            break
        rel = f"/images/v2/evalley-{Path(src).stem}-{w}.webp"
        dst = ROOT / "public" / rel.lstrip("/")
        if not dst.exists():
            # every CTA box shows at most a 4:5 slice, so taller portraits are cropped to 4:5 around the centre
            subprocess.run(["magick", str(srcf), "-gravity", "center", "-crop", "%[fx:w]x%[fx:min(h,w*1.25)]+0+0", "+repage",
                            "-resize", f"{w}x", "-quality", "70", "-define", "webp:method=6", str(dst)], check=True)
            if dst.stat().st_size > 300_000:  # busy textures (pine needles): trade a little quality for weight
                subprocess.run(["magick", str(srcf), "-gravity", "center", "-crop", "%[fx:w]x%[fx:min(h,w*1.25)]+0+0", "+repage",
                                "-resize", f"{w}x", "-quality", "56", "-define", "webp:method=6", str(dst)], check=True)
        out.append((w, rel))
    return out


def img(src, alt, role="card"):
    v = variants(src)
    srcset = ", ".join(f"{r} {w}w" for w, r in v)
    return f'<img src="{v[0][1]}" srcset="{srcset}" sizes="{SIZES[role]}" alt="{E(alt)}" loading="lazy" decoding="async">'


def wa(c, msg):
    return f'https://wa.me/{c["wa_number"]}?text={quote(msg)}'


def link_attrs(c, msg, block):
    return f'href="{E(wa(c, msg))}" target="_blank" rel="sponsored noopener" data-ev="{block}"'


def btn(c, label, msg, block):
    return f'<a class="ev-btn" {link_attrs(c, msg, block)}>{E(label)} <i>{WA}</i></a>'


# images per region (copy-independent)
IMAGES = {
    "boquete": {
        "banner": ("/images/boquete/boquete-ebike-trail.webp", {"en": "Two riders on E-Valley e-bikes on a farm track in Boquete", "es": "Dos ciclistas en bicis eléctricas de E-Valley por un camino de finca en Boquete"}),
        "cards": [
            ("/images/v2/clusters-of-ripe-red-coffee-cherries-14776857-gallery.webp", {"en": "Ripe red coffee cherries on a branch", "es": "Granos de café maduros en la rama"}),
            ("/images/boquete/boquete-ebike-hero.webp", {"en": "Two riders with e-bikes in front of a waterfall near Boquete", "es": "Dos ciclistas con bicis eléctricas frente a una cascada cerca de Boquete"}),
            ("/images/boquete/boquete-ebike-riders.webp", {"en": "An E-Valley e-bike and helmet among coffee plants in Boquete", "es": "Bici eléctrica de E-Valley y casco entre cafetos en Boquete"}),
        ],
        "rail": ("/images/boquete/boquete-ebike-riders.webp", {"en": "E-Valley e-bike among coffee plants", "es": "Bici eléctrica de E-Valley entre cafetos"}),
        "closer": ("/images/boquete/boquete-ebike-hero.webp", {"en": "Riders with E-Valley e-bikes at a waterfall in the Boquete highlands", "es": "Ciclistas con bicis de E-Valley junto a una cascada en las tierras altas de Boquete"}),
    },
    "elvalle": {
        "banner": ("/images/el-valle/evbike-crater-view.webp", {"en": "Rider with an e-bike looking out over the El Valle crater", "es": "Ciclista con bici eléctrica mirando el cráter de El Valle de Antón"}),
        "cards": [
            ("/images/el-valle/elvalle-elmachowaterfall3.webp", {"en": "Chorro El Macho waterfall in El Valle de Antón", "es": "La cascada Chorro El Macho en El Valle de Antón"}),
            ("/images/el-valle/evbike-bike-crater.webp", {"en": "Rider with her e-bike at a lookout above El Valle", "es": "Ciclista con su bici eléctrica en un mirador sobre El Valle"}),
            ("/images/el-valle/evbike-group.webp", {"en": "Group on e-bikes on a road in El Valle de Antón", "es": "Grupo en bicis eléctricas por una calle de El Valle de Antón"}),
        ],
        # E-Valley's own photos from evalleybikes.net (download approved by the user 2026-11-04)
        "rail": ("/images/el-valle/evbike-bike-crater.webp", {"en": "Rider with an E-Valley e-bike at a lookout above El Valle", "es": "Ciclista con bici eléctrica de E-Valley en un mirador sobre El Valle"}),
        "closer": ("/images/el-valle/evbike-sunset2.webp", {"en": "An E-Valley Bikes rider in a branded cap watching the sunset over El Valle", "es": "Una clienta de E-Valley Bikes con gorra de la marca mirando el atardecer sobre El Valle"}),
    },
}

PAGES = [  # key in copy.json, source guide, output preview
    ("boquete-en", "public/articles/geisha-coffee-boquete-where-to-taste.html", "boquete-geisha-coffee-evalley.html"),
    ("boquete-es", "public/es/articles/bajo-mono-boquete-circuito-y-senderos.html", "boquete-es-bajo-mono-evalley.html"),
    ("elvalle-es", "public/es/articles/cascadas-el-valle-de-anton-como-llegar.html", "el-valle-cascadas-evalley.html"),
    ("elvalle-en", "public/articles/chorro-las-mozas-swimming-falls-el-valle.html", "el-valle-en-las-mozas-evalley.html"),
]


def blocks(key):
    c = COPY[key]
    region, lang = key.split("-")
    im = IMAGES[region]
    cls = "evx ev-valle" if region == "elvalle" else "evx"
    aria = f'{E(c["tag"])}: {E(c["brand"])}'
    lbl = f'<div class="ev-row"><span class="ev-lbl">{E(c["brand"])}</span><span class="ev-tag">{E(c["tag"])}</span></div>'
    b, o, r, cl = c["banner"], c["offer"], c["rail"], c["closer"]
    banner = f"""
<aside class="{cls} ev-banner" aria-label="{aria}">
  <a class="ev-ph" {link_attrs(c, c["wa_msg"], "banner")} tabindex="-1">{img(im["banner"][0], im["banner"][1][lang], "banner")}</a>
  <div class="ev-bd">
    {lbl}
    <p class="ev-t">{rich(b["title"])}</p>
    {paras(b["body"])}
    <div class="ev-row">{btn(c, b["button"], c["wa_msg"], "banner")}
      <span class="ev-micro">{STARS} {E(c["rating_short"])}</span></div>
  </div>
</aside>"""
    cards = ""
    for i, (card, (src, alt)) in enumerate(zip(o["cards"], im["cards"])):
        pill = f'<span class="ev-pill top">{E(card["pill"])}</span>' if card["pill"] else ""
        meta = "".join(f"<span>{E(m)}</span>" for m in card["meta"])
        cards += f"""
    <a class="ev-card" {link_attrs(c, c["wa_msg"], f"offer-card-{i+1}")}><span class="ev-ph">{img(src, alt[lang], "card")}{pill}</span>
      <span class="ev-tx"><b>{E(card["name"])}</b><p>{E(card["desc"])}</p><span class="ev-meta">{meta}</span></span></a>"""
    trust = lambda xs: "".join(f"<li>{E(x)}</li>" for x in xs)
    offer = f"""
<aside class="{cls} ev-dark ev-offer" aria-label="{aria}">
  <div class="ev-hd">
    {lbl}
    <p class="ev-t">{rich(o["title"])}</p>
    {paras(o.get("intro", ""))}
    <div class="ev-inc"><span class="ev-inc-t">{E(o["includes_title"])}</span><ul>{"".join(f"<li>{E(x)}</li>" for x in o["includes"])}</ul></div>
  </div>
  <div class="ev-cards">{cards}
  </div>
  <div class="ev-row">{btn(c, o["button"], c["wa_msg"], "offer")}
    <ul class="ev-trust">{trust(o["trust"])}</ul></div>
</aside>"""
    rail = f"""
<aside class="{cls} ev-rail" aria-label="{aria}">
  <a class="ev-ph" {link_attrs(c, c["wa_msg"], "rail")} tabindex="-1">{img(im["rail"][0], im["rail"][1][lang], "rail")}<span class="chip glass">{STARS} {E(r["chip"])}</span></a>
  <div class="ev-bd">
    <p class="ev-t">{rich(r["title"])}</p>
    {paras(r["body"])}
    {btn(c, r["button"], c["wa_msg"], "rail")}
  </div>
</aside>"""
    closer = f"""
<section class="wrap band" aria-label="{aria}">
<div class="{cls} ev-dark ev-closer">
  <div class="ev-bd">
    {lbl}
    <span class="ev-micro">{STARS} {E(cl["rating"])}</span>
    <p class="ev-t">{rich(cl["title"])}</p>
    <div class="ev-steps"><span class="ev-steps-t">{E(cl["steps_title"])}</span><ol>{"".join(f"<li><span>{E(x)}</span></li>" for x in cl["steps"])}</ol></div>
    <figure class="ev-rev">
      {"" if cl.get("review_verified") else '<span class="ev-unv">Unverified review: not found on evalleybikes.net, Tripadvisor could not be checked. Replace or remove before launch.</span>'}
      <figcaption class="ev-rev-hd"><span class="ev-av" aria-hidden="true">{E(cl["review_name"][:1].upper())}</span><span class="ev-who"><b>{E(cl["review_name"])}</b><span class="ev-src">{E(cl["review_source"])}</span></span><span class="ev-rstars" role="img" aria-label="5 out of 5">{RSTAR * 5}</span></figcaption>
      <blockquote>&ldquo;{E(cl["review_quote"])}&rdquo;</blockquote>
    </figure>
    <div class="ev-row">{btn(c, cl["button"], c["wa_msg"], "closer")}
      <ul class="ev-trust">{trust(cl["trust"])}</ul></div>
  </div>
  <div class="ev-ph">{img(im["closer"][0], im["closer"][1][lang], "closer")}</div>
</div>
</section>"""
    return {"banner": banner, "offer": offer, "rail": rail, "closer": closer}


def insert_before_nth_section(html, n, block):
    """Insert block at the end of the n-th article section (1-based) = before section n+1."""
    starts = [m.start() for m in re.finditer(r'<section class="sec"', html)]
    pos = starts[n]
    return html[:pos] + block + "\n" + html[pos:]


def absolutize(html):
    for d in NOT_LIVE:  # not deployed yet: point previews at the repo copy
        html = html.replace(f'src="{d}', f'src="../../public{d}')
    html = re.sub(r'((?:src|href|imagesrcset)=")/(?!/)', r"\1" + SITE + "/", html)
    html = re.sub(r'url\((["\']?)/(?!/)', r"url(\1" + SITE + "/", html)
    html = re.sub(r'(srcset="[^"]*)', lambda m: re.sub(r'(^|, )/(?!/)', r"\1" + SITE + "/", m.group(1)), html)
    return html


def strip_live_blocks(html):
    """The source guides now carry the live blocks (scripts/evalley_cta_rollout.py); remove them so previews don't double up."""
    for k in ("banner", "offer", "rail", "closer"):
        html = re.sub(rf"<!--evx:{k}-->.*?<!--/evx-->\n?", "", html, flags=re.S)
    for a, b in (("<!--evx:css-->", "<!--/evx:css-->"), ("<!--evx:js-->", "<!--/evx:js-->"), ("/* evx:css */", "/* /evx:css */")):
        html = re.sub(re.escape(a) + r".*?" + re.escape(b) + r"\n?", "", html, flags=re.S)
    return html


def build(key, src, out):
    html = strip_live_blocks((ROOT / src).read_text())
    bl = blocks(key)
    html = html.replace("</style>", CSS + "\n</style>", 1)
    html = insert_before_nth_section(html, 3, bl["offer"])
    html = insert_before_nth_section(html, 1, bl["banner"])
    i = html.index('<div class="know">')
    k = html.index("</ul>", i)
    lis = re.findall(r"<li>.*?</li>", html[i:k], re.S)
    if len(lis) > KNOW_MAX:
        ul = html.index("<ul>", i) + len("<ul>")
        html = html[:ul] + "".join(lis[:KNOW_MAX]) + html[k:]
    j = html.index("</div>", html.index("</ul>", i)) + len("</div>")
    html = html[:j] + bl["rail"] + html[j:]
    i = html.index('<section class="band gband">')
    j = html.index("</section>", i) + len("</section>")
    html = html[:j] + bl["closer"] + html[j:]
    html = html.replace('content="index, follow, max-image-preview:large"', 'content="noindex, nofollow"')
    html = absolutize(html)
    (OUT / out).write_text(html)
    print("wrote", OUT / out)


if __name__ == "__main__":
    for key, src, out in PAGES:
        build(key, src, out)
