#!/usr/bin/env python3
"""
cta-pass.py — inject E-Valley Bikes CTAs into the El Valle / Boquete article pages.

Single source of truth for the CTA blocks lives in scripts/cta/ :
  styles.css                 the shared <style id="evb-cta-styles"> block
  {ev,bq}_{banner,offer,rail,closer}.html   the four CTA blocks, per location (English)

For each article the script picks blocks by:
  - location:  "boquete" in the filename  -> Boquete (green), else El Valle (terracotta)
  - language:  path contains /es/          -> Spanish (translated below), else English

Placement (anchors present in every generated article):
  CSS     -> before </head>
  banner  -> before <h2 id="s2">      (mid-article)
  offer   -> before <h2 id="s4">      (mid-article)
  rail    -> right after </article>   (fills the empty 3rd grid column, sticky on desktop)
  closer  -> before </main>           (full-width, before the footer)

Idempotent: every injected unit is wrapped in <!--EVB-CTA:key-->...<!--/EVB-CTA:key-->
markers, which are stripped before re-injecting. Re-run any time after editing the
templates or this file — it replaces, never duplicates.

Usage:  python3 scripts/cta-pass.py
"""
import re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CTA  = ROOT / "scripts" / "cta"

ARTICLES = sorted(
    [p for p in (ROOT/"public"/"articles").glob("*.html") if "EXAMPLE" not in p.name] +
    [p for p in (ROOT/"public"/"es"/"articles").glob("*.html") if "EXAMPLE" not in p.name]
)

# ── Spanish translation maps (applied to the English template text) ──────────
# Natural, native Panamanian Spanish. Brand + location chips are left as-is.
ES = {
 "ev": {
  "/funnels/evalley_elvalle\"": "/funnels/evalley_elvalle_es\"",
  # banner
  "See the whole crater by bike.": "Conoce el cráter entero en bici.",
  "Self-guided e-bike tours from $30 — helmet, GPS audio guide and lock included. Ride the volcano floor at your own pace.":
    "Tours en e-bike autoguiados desde $30 — casco, audioguía GPS y candado incluidos. Recorre el fondo del volcán a tu ritmo.",
  "See the bike tours": "Ver los tours en bici",
  "Four routes · Beginner &amp; family friendly · Cancel free up to 24h":
    "Cuatro rutas · Ideal para principiantes y familias · Cancela gratis hasta 24 h",
  # offer
  "Ride El Valle": "Recorre El Valle",
  "Four ways to do El Valle by bike.": "Cuatro formas de recorrer El Valle en bici.",
  "Self-guided freedom with a GPS audio guide that does the narrating — no group, no fixed itinerary. Helmet, lock and front basket included.":
    "Libertad total con una audioguía GPS que te lo va contando — sin grupo, sin itinerario fijo. Casco, candado y canasta incluidos.",
  "2 hours": "2 horas", "4 hours": "4 horas", "Full day": "Día completo", "/bike": "/bici",
  "Easy start": "Para empezar", "Town &amp; Art Loop": "Vuelta por el Pueblo y el Arte",
  "Historic center, the artisan market and the church. Flat, easy, perfect for a first ride.":
    "Centro histórico, el mercado artesanal y la iglesia. Plano, fácil, perfecto para estrenarte.",
  "EASY · GREAT FOR FIRST-TIMERS": "FÁCIL · IDEAL PARA PRINCIPIANTES",
  "Family": "Familiar", "Falls &amp; Wildlife": "Cascadas y Naturaleza",
  "Chorro El Macho waterfall, the Butterfly Haven and the Níspero Zoo. Built for groups with kids.":
    "La cascada del Chorro El Macho, el Mariposario y el Zoo El Níspero. Pensado para ir con niños.",
  "EASY–MODERATE · KID FRIENDLY": "FÁCIL–MODERADO · APTO PARA NIÑOS",
  "Best at sunset": "Mejor al atardecer", "Crater Ridge": "Cima del Cráter",
  "Up to the panoramic ridge over the crater. The sunset slot is the one to book.":
    "Hasta la cima panorámica sobre el cráter. El turno del atardecer es el que hay que reservar.",
  "MODERATE · BOOK THE SUNSET SLOT": "MODERADO · RESERVA EL TURNO DEL ATARDECER",
  "For riders": "Para ciclistas", "Mountain &amp; India Dormida": "Montaña y La India Dormida",
  "Off-road, real elevation, real views — for experienced riders who want to earn it.":
    "Fuera de ruta, desnivel de verdad, vistas de verdad — para ciclistas con experiencia que quieren ganárselas.",
  "ADVANCED · OFF-ROAD": "AVANZADO · FUERA DE RUTA",
  "View tours &amp; pricing": "Ver tours y precios",
  "✓ Helmet, audio guide, lock &amp; basket": "✓ Casco, audioguía, candado y canasta",
  "✓ Pickup at Plaza Paseo El Valle": "✓ Recogida en Plaza Paseo El Valle",
  "✓ Cancel free up to 24h": "✓ Cancela gratis hasta 24 h",
  # rail
  "Ride El Valle by e-bike": "Recorre El Valle en e-bike",
  "Self-guided tours from $30/bike. Helmet, audio guide &amp; lock included.":
    "Tours autoguiados desde $30/bici. Casco, audioguía y candado incluidos.",
  "Learn more": "Saber más",
  # closer
  "Your next great ride is one click away.": "Tu próximo gran paseo está a un clic.",
  "See the four routes, the timings and exactly what's included — then pick the slot that fits your day in the crater.":
    "Mira las cuatro rutas, los horarios y todo lo que incluye — y elige el turno que encaje con tu día en el cráter.",
  "From $30/bike · Beginner &amp; family friendly": "Desde $30/bici · Ideal para principiantes y familias",
  "Explore El Valle bike tours": "Explora los tours en bici de El Valle",
  "El Valle &amp; Boquete, same trusted team · Pickup at Plaza Paseo El Valle · Cancel free up to 24h":
    "El Valle y Boquete, el mismo equipo de confianza · Recogida en Plaza Paseo El Valle · Cancela gratis hasta 24 h",
 },
 "bq": {
  "/funnels/evalley_boquete\"": "/funnels/evalley_boquete_es\"",
  # banner
  "Three hours on a bike = a full day on foot.": "Tres horas en bici = un día entero a pie.",
  "Premium Orbea e-bikes flatten every climb — coffee farms, cloud forest and the Lost Waterfalls, all at your own pace.":
    "Las e-bikes Orbea premium aplanan cada subida — fincas de café, bosque nuboso y las Lost Waterfalls, todo a tu ritmo.",
  "See the e-bike tours": "Ver los tours en e-bike",
  "★ 5.0 · 80+ Tripadvisor reviews · English &amp; Spanish · Pay when you arrive":
    "★ 5.0 · 80+ reseñas en Tripadvisor · Español e inglés · Pagas al llegar",
  # offer
  "Ride Boquete": "Recorre Boquete",
  "Three rides. One unforgettable Boquete.": "Tres recorridos. Un Boquete inolvidable.",
  "Premium Orbea e-bikes that do the climbing for you. Helmet, gloves, water and route support included — and you pay when you arrive.":
    "E-bikes Orbea premium que suben por ti. Casco, guantes, agua y apoyo en ruta incluidos — y pagas al llegar.",
  "Most booked": "El más reservado", "Coffee Farm E-Bike Tour": "Tour de Finca de Café en E-Bike",
  "Ride to a working farm and see how Geisha — the world's most expensive coffee — is made. Tasting at Altieri Specialty Coffee, geisha ice cream included.":
    "Pedalea hasta una finca en pleno trabajo y descubre cómo se produce el Geisha — el café más caro del mundo. Cata en Altieri Specialty Coffee, con helado de geisha incluido.",
  "~3 HOURS · GUIDED · TASTING": "~3 HORAS · GUIADO · CON CATA",
  "Local secret": "Secreto local", "Guided Highlights Ride": "Recorrido Guiado de Imperdibles",
  "Lost Waterfalls, Library Park and the highland viewpoints locals love — the spots most visitors never find.":
    "Las Lost Waterfalls, el Parque de la Biblioteca y los miradores de altura que aman los locales — los lugares que casi nadie encuentra.",
  "HALF DAY · GUIDED · PHOTO STOPS": "MEDIO DÍA · GUIADO · PARADAS PARA FOTOS",
  "Your pace": "A tu ritmo", "Self-Paced Rental": "Alquiler Libre",
  "Hourly or full-day. Take a recommended route or just wander. The e-bike means hills don't decide your day.":
    "Por horas o día completo. Toma una ruta recomendada o explora a tu aire. Con la e-bike, las subidas ya no deciden tu día.",
  "FLEXIBLE · SOLO &amp; BEGINNER FRIENDLY": "FLEXIBLE · IDEAL PARA IR SOLO Y PRINCIPIANTES",
  "View tours &amp; details": "Ver tours y detalles",
  "✓ Premium Orbea e-bikes": "✓ E-bikes Orbea premium",
  "✓ English &amp; Spanish": "✓ Español e inglés",
  "✓ Cancel free up to 24h": "✓ Cancela gratis hasta 24 h",
  "✓ No deposit": "✓ Sin depósito",
  # rail
  "Ride Boquete by e-bike": "Recorre Boquete en e-bike",
  "Premium Orbea e-bikes. ★ 5.0 · 80+ Tripadvisor reviews.":
    "E-bikes Orbea premium. ★ 5.0 · 80+ reseñas en Tripadvisor.",
  "Learn more": "Saber más",
  # closer
  "★★★★★ 5.0 · 80+ reviews on Tripadvisor": "★★★★★ 5.0 · 80+ reseñas en Tripadvisor",
  "See Boquete the way locals do.": "Conoce Boquete como lo hacen los locales.",
  "Coffee-farm rides, highland viewpoints and self-paced explores — see the full line-up and pick the one that fits your trip.":
    "Recorridos por fincas de café, miradores de altura y rutas libres — mira todo lo que hay y elige el que encaje con tu viaje.",
  "\"This was an AMAZING tour and trip! Andrish and Ricardo are VERY FUN and flexible with our group.\"":
    "\"¡Fue un tour y un viaje INCREÍBLE! Andrish y Ricardo son MUY DIVERTIDOS y flexibles con nuestro grupo.\"",
  "Explore Boquete bike tours": "Explora los tours en bici de Boquete",
  "Pay when you arrive · Cancel free up to 24h · English &amp; Spanish · Open Wed–Mon":
    "Pagas al llegar · Cancela gratis hasta 24 h · Español e inglés · Abierto mié–lun",
 },
}

def load(loc, name):
    return (CTA / f"{loc}_{name}.html").read_text(encoding="utf-8").strip()

def localize(html, loc, lang):
    if lang == "es":
        for en, es in ES[loc].items():
            html = html.replace(en, es)
    return html

def wrap(key, html):
    return f"<!--EVB-CTA:{key}-->{html}<!--/EVB-CTA:{key}-->"

def strip_old(s):
    return re.sub(r"<!--EVB-CTA:(\w+)-->.*?<!--/EVB-CTA:\1-->", "", s, flags=re.S)

def _remove_balanced(s, open_re, tag):
    """Remove every element matching `open_re` up to its depth-matched closing
    </tag>, including nested same-tag children."""
    opn, cls = f"<{tag}", f"</{tag}>"
    while True:
        m = re.search(open_re, s)
        if not m:
            return s
        i, depth = m.end(), 1
        while i < len(s) and depth:
            no, nc = s.find(opn, i), s.find(cls, i)
            if nc == -1:
                break
            if no != -1 and no < nc:
                depth += 1; i = no + len(opn)
            else:
                depth -= 1; i = nc + len(cls)
        s = s[:m.start()] + s[i:]

def strip_evb_blocks(s):
    """Remove ANY e-bike CTA blocks, marker-wrapped or hardcoded into the page
    template. The new-page templates shipped with stray/inconsistent hardcoded
    CTAs (e.g. an El Valle rail on a Boquete page, or a CTA on a non-region
    page); strip them all so injection is the single source of truth."""
    s = re.sub(r'<style id="evb-cta-styles">.*?</style>', "", s, flags=re.S)
    s = _remove_balanced(s, r'<section class="evb-cta evb-closer"', "section")
    s = _remove_balanced(s, r'<aside class="evb-rail"', "aside")
    s = _remove_balanced(s, r'<div class="evb-cta"', "div")
    return s

def cta_region(name):
    """Which e-bike funnel a page should carry, by topic:
      'ev' -> El Valle,  'bq' -> Boquete / Chiriquí,  None -> no CTA at all.
    Only El Valle and Boquete-area pages get a funnel; everything else (Panama
    City, Casco Viejo, Coiba, Bocas, San Blas, …) gets nothing."""
    n = name.lower()
    if "el-valle" in n or "valle-de-anton" in n:
        return "ev"
    if any(k in n for k in ("boquete", "volcan-baru", "caldera", "lerida", "chiriqui")):
        return "bq"
    return None

def inject(path):
    loc = cta_region(path.name)
    lang = "es" if "/es/" in path.as_posix() else "en"
    s = path.read_text(encoding="utf-8")
    s = strip_evb_blocks(strip_old(s))   # always clean every CTA first
    if loc is None:
        path.write_text(s, encoding="utf-8")   # non-region page → cleaned, no CTA
        return None, None

    css    = (CTA / "styles.css").read_text(encoding="utf-8").strip()
    css    = f'<style id="evb-cta-styles">{css}</style>'
    banner = localize(load(loc, "banner"), loc, lang)
    offer  = localize(load(loc, "offer"),  loc, lang)
    rail   = localize(load(loc, "rail"),   loc, lang)
    closer = localize(load(loc, "closer"), loc, lang)

    anchors = {
        "css":    ("</head>",        wrap("css", css)    + "</head>"),
        "banner": ('<h2 id="s2"',    wrap("banner", banner) + '<h2 id="s2"'),
        "offer":  ('<h2 id="s4"',    wrap("offer", offer)   + '<h2 id="s4"'),
        "rail":   ("</article>",     "</article>" + wrap("rail", rail)),
        "closer": ('<section class="art-section tint"><div class="container"><div class="art-section-head"><span class="eyebrow">The short version</span><h2>Three things to know</h2>', wrap("closer", closer) + '<section class="art-section tint"><div class="container"><div class="art-section-head"><span class="eyebrow">The short version</span><h2>Three things to know</h2>'),
    }
    for key, (anchor, repl) in anchors.items():
        if s.count(anchor) < 1:
            raise SystemExit(f"  !! anchor {anchor!r} not found in {path.name}")
        s = s.replace(anchor, repl, 1)

    path.write_text(s, encoding="utf-8")
    return loc, lang

def main():
    # Optional CLI filters: only process articles whose filename contains any of
    # the given substrings (e.g. `cta-pass.py volcan-baru`). No args = all.
    filters = [a.lower() for a in sys.argv[1:]]
    targets = [p for p in ARTICLES if not filters or any(f in p.name.lower() for f in filters)]
    done = skipped = 0
    for p in targets:
        loc, lang = inject(p)
        if loc is None:
            skipped += 1; continue
        done += 1
        print(f"  ✓ {p.relative_to(ROOT)}  [{loc} · {lang}]")
    print(f"\nDone. Injected {done}, skipped {skipped} (non-Boquete/El-Valle).")

if __name__ == "__main__":
    main()
