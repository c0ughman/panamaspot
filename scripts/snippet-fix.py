#!/usr/bin/env python3
"""snippet-fix.py — apply the hand-written title and description rewrites.

Titles: 24 pages carried no year while competing against results that do.
Each replacement is written individually rather than pattern-appended, and is
kept under 60 rendered characters so it doesn't truncate in the SERP.

Descriptions: 6 ran past 160 rendered characters and cut off mid-sentence.

Both are applied to <title>/<meta name=description> and to the matching
og: and twitter: pairs, so the three never drift apart.
Idempotent: a page already carrying the new text is skipped.
"""
import html as H
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TITLES = {
 "articles/boquete-coffee-farm-tour": "Boquete Coffee Farm Tour 2026: Which One to Choose",
 "es/articles/aguas-termales-caldera-boquete": "Aguas Termales de Caldera, Boquete: Guía 2026",
 "es/articles/sendero-india-dormida-el-valle-de-anton": "Sendero La India Dormida, El Valle: Guía 2026",
 "articles/chorro-el-macho-waterfall-el-valle-de-anton": "Chorro El Macho Waterfall, El Valle: 2026 Guide",
 "es/articles/el-valle-de-anton-desde-ciudad-de-panama": "El Valle de Antón desde Ciudad de Panamá: Guía 2026",
 "es/articles/casco-viejo-restaurantes-donde-comer-beber-hospedarse": "Restaurantes Casco Viejo 2026: Dónde Comer y Beber",
 "es/articles/volcan-baru-como-subir-cima-panama": "Volcán Barú 2026: Cómo Subir a la Cima de Panamá",
 "articles/india-dormida-hike-el-valle-de-anton": "India Dormida Hike, El Valle: Trail Guide 2026",
 "articles/tours-in-boquete-panama": "Tours in Boquete, Panama 2026: Bikes, Coffee & Prices",
 "articles/volcan-baru-hike-sunrise-summit-guide": "Volcán Barú Hike 2026: Sunrise Summit, Two Oceans",
 # also the one genuinely over-length title, at 62 characters
 "articles/hikes-el-valle-de-anton": "Best Hikes in El Valle de Antón: Every Trail (2026)",
 "articles/el-valle-day-trip-from-panama-city": "El Valle Day Trip from Panama City: 2026 Guide",
 "es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama": "Cómo Llegar a Bocas del Toro desde Panamá (2026)",
 "articles/day-trips-from-panama-city": "Best Day Trips From Panama City 2026: 7 Routes Ranked",
 "articles/cerro-gaital-cara-iguana-hike-el-valle": "Cerro Gaital & Cara Iguana 2026: El Valle's Hard Hikes",
 "es/articles/canopy-el-valle-de-anton-cabalgatas-aventura": "Canopy El Valle de Antón 2026: Zipline y Cabalgatas",
 "es/articles/boquete-panama-guia-completa-itinerario": "Boquete Panamá 2026: Itinerario Completo de 3 Días",
 "es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo": "Cinta Costera y Mercado de Mariscos: Guía 2026",
 "articles/el-valle-de-anton-with-kids": "El Valle de Antón With Kids 2026: Zoo & Butterflies",
 "es/articles/rafting-boquete-rio-chiriqui": "Rafting en Boquete 2026: Guía del Río Chiriquí",
 "es/articles/isla-coiba-buceo-parque-nacional": "Isla Coiba 2026: Guía de Buceo y Parque Nacional",
 "articles/finca-lerida-los-quetzales-trail-birdwatching-boquete": "Finca Lérida & Los Quetzales 2026: Birdwatching Guide",
 "es/articles/alquiler-de-bicicletas-boquete": "Alquiler de Bicicletas Boquete 2026: E-Bikes desde $35",
 "es/articles/san-blas-guna-yala-guia-tours-islas": "San Blas (Guna Yala) 2026: Guía de Tours e Islas",
}

DESCRIPTIONS = {
 "articles/boquete-travel-guide":
   "Plan 3 days in Boquete: when to go, getting there, where to stay, and a "
   "day-by-day itinerary covering coffee, trails and hot springs.",
 "articles/el-valle-de-anton-with-kids":
   "A family day in El Valle de Antón: golden frogs at El Níspero, Butterfly "
   "Haven, APROVACA orchids and the Sunday market — with real 2026 prices.",
 "articles/hikes-el-valle-de-anton":
   "Length, difficulty and entry fees for every El Valle hike — India Dormida, "
   "Cerro Gaital and the waterfall loops — plus start times and what to pack.",
 "articles/tours-en-el-valle-de-anton":
   "Real 2026 tour prices, e-bike vs hiking routes, exact times, and honest "
   "guided vs self-guided advice for El Valle de Antón.",
 "articles/volcan-baru-hike-sunrise-summit-guide":
   "Everything you need to hike Volcán Barú from Boquete — timing, gear, "
   "pacing, permits, costs, and the honest odds of seeing both oceans.",
 "es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo":
   "Guía de la Cinta Costera: mejores horas, ceviche en el Mercado de "
   "Mariscos, ruinas de Panamá Viejo y un itinerario de medio día.",
}


def set_meta(html, key, value, attr="name"):
    """Rewrite a meta tag's content regardless of attribute order."""
    esc = H.escape(value, quote=True)
    out, n = [], 0
    pos = 0
    for m in re.finditer(r"<meta ([^>]*?)/?>", html):
        attrs = dict(re.findall(r'([\w:-]+)="([^"]*)"', m.group(1)))
        if attrs.get(attr) != key:
            continue
        rebuilt = re.sub(r'(content=")[^"]*(")', lambda x: x.group(1) + esc + x.group(2), m.group(0))
        out.append(html[pos:m.start()]); out.append(rebuilt); pos = m.end(); n += 1
    out.append(html[pos:])
    return "".join(out), n


def apply(path, title=None, desc=None):
    p = ROOT / "public" / (path + ".html")
    if not p.exists():
        print(f"  MISSING {path}")
        return 0
    h = p.read_text(encoding="utf8")
    before = h
    if title:
        h = re.sub(r"<title>.*?</title>", "<title>" + H.escape(title) + "</title>", h, count=1, flags=re.S)
        h, _ = set_meta(h, "og:title", title, "property")
        h, _ = set_meta(h, "twitter:title", title)
    if desc:
        h, _ = set_meta(h, "description", desc)
        h, _ = set_meta(h, "og:description", desc, "property")
        h, _ = set_meta(h, "twitter:description", desc)
    if h == before:
        return 0
    p.write_text(h, encoding="utf8")
    return 1


def main():
    over_t = [(k, v) for k, v in TITLES.items() if len(v) > 60]
    over_d = [(k, v) for k, v in DESCRIPTIONS.items() if len(v) > 160]
    if over_t or over_d:
        print("  REFUSING — replacement copy is itself too long:")
        for k, v in over_t: print(f"    title {len(v)}c  {k}")
        for k, v in over_d: print(f"    desc  {len(v)}c  {k}")
        sys.exit(1)

    n = 0
    for path, t in TITLES.items():
        n += apply(path, title=t)
    for path, d in DESCRIPTIONS.items():
        n += apply(path, desc=d)
    print(f"  rewrote {len(TITLES)} titles and {len(DESCRIPTIONS)} descriptions across {n} files")
    print(f"  longest new title: {max(len(v) for v in TITLES.values())}c "
          f"· longest new description: {max(len(v) for v in DESCRIPTIONS.values())}c")


if __name__ == "__main__":
    main()
