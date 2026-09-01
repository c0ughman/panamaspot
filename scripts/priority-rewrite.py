#!/usr/bin/env python3
"""priority-rewrite.py — stage 2, item 6.

The 21 pages sitting at position 5–15 with 500+ impressions each: they win the
ranking and lose the click. Every replacement leads with the keyword and then
promises one specific thing a searcher would have to click to find out — a
price, a distance, a duration, a count.

Every number here was read out of the page it belongs to. Nothing is inferred,
and nothing is carried across from a sibling page in the other language.

Reuses the meta-rewriting helpers in snippet-fix.py so title/og/twitter and
description/og/twitter stay in lockstep.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snippet_fix import apply as apply_meta  # noqa: E402

# path: (title, description)   — title <= 60 chars, description <= 160
REWRITES = {
 # ── El Valle ────────────────────────────────────────────────────────────────
 "articles/india-dormida-hike-el-valle-de-anton": (
   "India Dormida Hike: 3.5 km, 2–3 Hours, $3 Entry",
   "El Valle's signature ridge walk: 3.5 km, 2–3 hours up and back, $3 at the "
   "kiosk. Trailhead directions, sunrise timing and what the legend is about."),
 "articles/chorro-el-macho-waterfall-el-valle-de-anton": (
   "Chorro El Macho: 35m Falls, $3 Trail, 25 Min Walk",
   "A 35-metre waterfall a 25-minute walk from El Valle town. Trail access is $3 "
   "and the pool is $5 — what each one gets you, and how to reach the entrance."),
 "articles/hikes-el-valle-de-anton": (
   "Best Hikes in El Valle: 7 Trails Compared (2026)",
   "Seven El Valle trails compared on distance, difficulty and entry fee — India "
   "Dormida, Cerro Gaital, the waterfall walks and the hot springs route."),
 "articles/tours-en-el-valle-de-anton": (
   "El Valle Tours 2026: Bike, Hike & Canopy Prices",
   "What each El Valle tour actually costs in 2026 — e-bike, hiking, canopy and "
   "horseback — with honest guided vs self-guided advice and how to get there."),
 "articles/el-valle-day-trip-from-panama-city": (
   "El Valle Day Trip: 2 Hours from Panama City, Bus $5",
   "How to do El Valle in a day from Panama City: the Albrook bus for about $5, "
   "two hours each way, and a realistic hour-by-hour plan for what actually fits."),
 "es/articles/cascada-chorro-el-macho-el-valle-de-anton": (
   "Chorro El Macho 2026: Entrada $5, Horario y Cómo Llegar",
   "Entrada $5 adultos y $2.50 niños, abierto de 8:00 am hasta el atardecer. Cómo "
   "llegar a pie, en taxi o en bici, y qué incluye el acceso al sendero."),
 "es/articles/sendero-india-dormida-el-valle-de-anton": (
   "Sendero La India Dormida 2026: 3,5 km y Entrada $3",
   "El sendero insignia de El Valle: 3,5 km, 2–3 horas y entrada de $3 en el "
   "kiosco. La leyenda de Luba, el mejor horario para subir y qué llevar."),
 "es/articles/el-valle-de-anton-desde-ciudad-de-panama": (
   "El Valle desde Panamá 2026: Bus $5 y 2 Horas de Viaje",
   "Bus desde Albrook por unos $5 o dos horas en auto por la Panamericana. Dónde "
   "tomarlo, cuánto tarda de verdad y qué hacer al llegar si vas por el día."),
 "es/articles/zoologico-el-nispero-el-valle-de-anton": (
   "Zoológico El Níspero 2026: Entrada $4–6, Abre 7 am",
   "Entrada $4 panameños y $6 extranjeros, abierto todos los días de 7 am a 5 pm. "
   "La rana dorada, el mariposario y cuánto tiempo dedicarle con niños."),
 "es/articles/aguas-termales-el-valle-de-anton": (
   "Aguas Termales El Valle 2026: Precio, Horario y Cómo Ir",
   "Los pozos de barro y agua caliente al pie del Cerro Cara Iguana: precio, "
   "horario, cómo llegar a pie o en bici, y por qué una o dos horas bastan."),
 # ── Boquete ─────────────────────────────────────────────────────────────────
 "articles/caldera-hot-springs-boquete": (
   "Caldera Hot Springs, Boquete: 38–45°C Pools, 25 Min Out",
   "Three geothermal pools running 38–45°C, 25 minutes from Boquete town. Exact "
   "directions, what a taxi costs, the best months, and whether to book a tour."),
 "articles/boquete-coffee-farm-tour": (
   "Boquete Coffee Farm Tours: 7 Farms Compared (2026)",
   "Seven Boquete coffee farms compared on price, length and whether Geisha "
   "tasting is included — plus which to pick for depth, for views, or for a short visit."),
 "articles/hikes-in-boquete": (
   "Best Hikes in Boquete: 7 Trails Compared (2026)",
   "Seven Boquete trails compared on distance, elevation, time and fee — from the "
   "Lost Waterfalls loop to the overnight Barú summit, and what each one needs."),
 "articles/lost-waterfalls-boquete-hiking-guide": (
   "Lost Waterfalls Boquete: 3 Falls, 6 km, $10 Entry",
   "Three waterfalls on one steep, wet 6 km trail above Boquete — $10 entry, 2–3 "
   "hours round trip. Reaching the trailhead, footwear, and the best months to go."),
 "articles/volcan-baru-hike-sunrise-summit-guide": (
   "Volcán Barú Hike: 13.5 km, 10–13 Hours, Two Oceans",
   "The overnight climb to Panama's highest point: 13.5 km each way, 10–13 hours, "
   "$5 park fee. Gear, pacing, and the honest odds of seeing both oceans at dawn."),
 "articles/tours-in-boquete-panama": (
   "Boquete Tours 2026: Coffee, Bike & Rafting Prices",
   "Real 2026 prices for Boquete's coffee, bike, rafting and birding tours, "
   "compared honestly — including the ones you can just as easily do yourself."),
 "es/articles/aguas-termales-caldera-boquete": (
   "Aguas Termales de Caldera 2026: Precios y Cómo Llegar",
   "Pozos termales a 25 minutos en taxi o 40 en bus desde Boquete. Precios de "
   "entrada y de transporte, mejores meses del año y qué llevar a los pozos."),
 "es/articles/volcan-baru-como-subir-cima-panama": (
   "Volcán Barú 2026: Subida de 5–8 h y Entrada de $5",
   "3.474 m, entre 5 y 8 horas de subida desde Boquete y $5 de entrada para "
   "nacionales. Las dos rutas, la subida nocturna y qué ropa llevar para el frío."),
 # ── Panama City ─────────────────────────────────────────────────────────────
 "articles/panama-canal-tour-miraflores-locks-visitor-guide": (
   "Miraflores Locks 2026: $17.22 Entry & When Ships Pass",
   "Adult entry is $17.22, children 6–12 pay $7.22, under-6s go free. When ships "
   "actually transit, what the ticket covers, and how to time a visit around it."),
 "articles/casco-viejo-panama-walking-guide": (
   "Casco Viejo Walking Route: 1.5 km, 8 Stops, 2–4 Hours",
   "A 1.5-kilometre self-guided route through Casco Viejo covering eight essential "
   "stops in 2–4 hours — what to see in order, and what you can safely skip."),
 "es/articles/casco-viejo-restaurantes-donde-comer-beber-hospedarse": (
   "Restaurantes Casco Viejo: Comer Bien por Menos de $15",
   "Dónde comer bien en el Casco por menos de $15, la cocina panameña moderna que "
   "sí vale el gasto, los bares de azotea y dónde dormir dentro del barrio."),
}


def main():
    bad = [(k, len(t), len(d)) for k, (t, d) in REWRITES.items()
           if len(t) > 60 or len(d) > 160]
    if bad:
        print("  REFUSING — replacement copy too long:")
        for k, lt, ld in bad:
            print(f"    {k}  title {lt}c  desc {ld}c")
        sys.exit(1)
    n = sum(apply_meta(path, title=t, desc=d) for path, (t, d) in REWRITES.items())
    print(f"  rewrote {len(REWRITES)} pages ({n} files changed)")
    print(f"  longest title {max(len(t) for t, _ in REWRITES.values())}c · "
          f"longest description {max(len(d) for _, d in REWRITES.values())}c")


if __name__ == "__main__":
    main()
