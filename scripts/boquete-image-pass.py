#!/usr/bin/env python3
"""
boquete-image-pass.py — put real photographs of Boquete on the Boquete pages.

The 2026-09 batch shipped with Pexels stock under captions that named specific
places ("Rock-lined thermal pools at Caldera Hot Springs", "hexagonal basalt
columns at Los Ladrillos", "a birding guide at Finca Lérida"). The photos do not
show those places, and the claim was repeated into alt text, <figcaption> and the
ImageObject schema. This pass replaces the image AND rewrites the caption from
what the photograph actually shows.

Two sources, both checkable:
  - "/images/boquete/*.webp" — the client's own photography. 37 of these sat
    unconverted as HEIC and had never been used. Every one was viewed before
    being assigned here.
  - a Commons title — resolved through scripts/commons-verified.json. Found by
    GEOSEARCH on the real coordinates (Boquete 8.78,-82.44; Caldera hot springs
    8.667,-82.383) or by a title naming the place, and each one viewed before
    use. Run image-credits.py afterwards so CC BY / BY-SA get their attribution.

Captions describe only what is in frame. Where we have no photograph of the
subject, the slot is left alone rather than filled with something adjacent.

    python3 scripts/boquete-image-pass.py [--only SUBSTR]
"""
import re, sys, json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from img_cap import img_html, HERO, GALLERY as GW

SIZES_INLINE = "(max-width: 768px) 100vw, 768px"
META = json.loads((ROOT / "scripts" / "commons-verified.json").read_text(encoding="utf-8"))
SITE = "https://panamaspot.com"


def url(ref):
    """A source ref is either a local /images/... path or a Commons file title."""
    return ref if ref.startswith("/images/") else META[ref]["url"]


# page -> {hero: ref|None, place: [(section_index, ref, caption), …]}
PLAN = {

# ── Volcán Barú (ES) — the best-covered page; all owned or verified Barú ──────
"public/es/articles/el-volcan-baru-esta-activo.html": {
 "hero": "Volcán-barú-panama-at-sunrise.jpg",
 "place": [
  (0, "/images/boquete/boquete-volcanbaru.webp",
      "La cima del Barú entre nubes, vista desde el aire sobre la selva de Chiriquí"),
  (1, "Vulkan Baru Boquete (27238202851).jpg",
      "La silueta del Barú sobre los techos de Boquete, con la antena de la cima visible"),
  (2, "/images/boquete/boquete-volcanview.webp",
      "El Barú visto desde un porche en Boquete en una mañana con neblina"),
  (3, "/images/boquete/boquete-street-peak.webp",
      "Casas y cultivos de Boquete al pie del cerro, en la falda del volcán"),
  (5, "/images/boquete/boquete-cloudforest.webp",
      "Bosque nuboso denso en las laderas altas: el terreno real de la subida"),
  (6, "/images/boquete/boquete-losquetzales.webp",
      "El letrero del Camino Los Quetzales, en el Parque Nacional Volcán Barú"),
  (7, "/images/boquete/boquete-nightvolcan.webp",
      "El Barú al anochecer sobre las luces del valle; la subida clásica arranca de noche"),
]},

# ── Hot springs (EN) — Caldera and Los Pozos, photographed ────────────────────
"public/articles/boquete-hot-springs-caldera-vs-los-pozos.html": {
 "hero": "Heiße Quellen bei Boquete (26700913504).jpg",
 "place": [
  (0, "Calderahotsprings.JPG",
      "Bathers in a stone-lined thermal pool at Caldera Hot Springs"),
  (1, "Heiße Quellen Boquete (27032980500).jpg",
      "A pool walled with river stones, built into the boulder bed beside the water"),
  (2, "Caminando a los Pozos de Caldera, Panama.jpg",
      "The suspension footbridge on the walk in to Los Pozos de Caldera"),
  (4, "YellowJeepCrossingRiver.JPG",
      "A tour jeep fording the river on the track to the springs — the road is the hard part"),
  (9, "/images/boquete/boquete-river-euc.webp",
      "The river running fast over its stone bed below Boquete"),
]},

# ── Quetzal season (EN) — the actual bird, the actual finca ───────────────────
"public/articles/quetzal-season-boquete-when-where-to-see-resplendent-quetzal.html": {
 "hero": "Resplendent quetzal (Pharomachrus mocinno) male 3.jpg",
 "place": [
  (0, "/images/boquete/boquete-cloudforest.webp",
      "Cloud forest canopy above Boquete — the habitat the birds depend on"),
  (1, "Resplendent Quetzal (Pharomachrus mocinno) - Flickr - gailhampshire.jpg",
      "A male resplendent quetzal, crimson belly and trailing tail streamers"),
  (2, "Volcan Baru, Quetzal Trail - Flickr - gailhampshire.jpg",
      "Smallholdings give way to forest along the Quetzal Trail on Barú's flank"),
  (4, "Finca Lerida, Boquete, Panama.jpg",
      "Finca Lérida, its lodge set among coffee terraces on the ridge above Boquete"),
  (5, "/images/boquete/boquete-losquetzales.webp",
      "The Camino Los Quetzales trailhead sign, Parque Nacional Volcán Barú"),
]},

# ── Where to stay (EN) — neighbourhood by neighbourhood, all owned ────────────
"public/articles/where-to-stay-in-boquete.html": {
 "hero": "/images/boquete/boquete-town2.webp",
 "place": [
  (0, "/images/boquete/boquete-clouds.webp",
      "Cloud pouring over the ridge into the Boquete valley in the afternoon"),
  (1, "/images/boquete/boquete-town.webp",
      "A converted van serving coffee on a street in Bajo Boquete"),
  (2, "/images/boquete/boquete-cafeview.webp",
      "A café counter built along the window, looking out over the coffee slopes"),
  (3, "/images/boquete/boquete-cloudforest.webp",
      "Cloud forest on the upper slopes, where the birding lodges sit"),
  (4, "/images/boquete/boquete-cabins.webp",
      "Timber A-frame cabins set back behind hydrangeas on the hillside"),
  (5, "/images/boquete/boquete-houseclouds.webp",
      "Mist rolling down the ridge behind a house on the valley edge"),
  (6, "/images/boquete/boquete-street-peak.webp",
      "A Boquete street under the cloud-wrapped peak, farm plots on the slope behind"),
]},

# ── Boquete con niños (ES) — sections 04 and 06 kept per the client's note ────
"public/es/articles/boquete-con-ninos-guia-familiar.html": {
 "hero": "/images/boquete/boquete-firepit.webp",
 "place": [
  (0, "/images/boquete/boquete-strawberry.webp",
      "Una fresa recién cortada en la mano, en un cultivo de las tierras altas"),
  (2, "/images/boquete/boquete-sheep.webp",
      "Ovejas en el corral de una finca, al alcance de la mano"),
  (4, "/images/boquete/boquete-plantation.webp",
      "Hileras de cafetos en una finca de Boquete, con el cerro nublado al fondo"),
  (6, "/images/boquete/boquete-cafeview2.webp",
      "Un café con ventanales sobre el bosque: el plan de los días de lluvia"),
  (7, "/images/boquete/boquete-food2.webp",
      "Ropa vieja servida sobre plátano en hoja de bijao"),
]},

# ── ¿Cuánto cuesta Boquete? (ES) — real prices, real plates ───────────────────
"public/es/articles/cuanto-cuesta-boquete-presupuesto-semana.html": {
 "hero": "/images/boquete/boquete-town2.webp",
 "place": [
  (0, "/images/boquete/boquete-street-peak.webp",
      "Una calle de Boquete bajo el cerro, con los cultivos en la ladera"),
  (2, "/images/boquete/boquete-cabins.webp",
      "Cabañas de madera en la ladera, una de las categorías de hospedaje"),
  (3, "/images/boquete/boquete-food.webp",
      "Carne guisada con puré y plátano frito en un restaurante de Boquete"),
  (4, "/images/boquete/boquete-zipline-rider.webp",
      "Un participante cruzando por cable sobre el bosque nuboso"),
  (5, "/images/boquete/boquete-town.webp",
      "Una van convertida en cafetería, estacionada en la calle"),
  (6, "/images/boquete/boquete-market.webp",
      "Un puesto de frutas y verduras en Boquete"),
]},

# ── Feria de las Flores (ES) — photographs OF the fair ────────────────────────
"public/es/articles/feria-de-las-flores-y-del-cafe-boquete.html": {
 "hero": "Feria de las Flores y el Café de Boquete 2019.jpg",
 "place": [
  (0, "Feria de las Flores.jpg",
      "Un macizo de flores sembrado en el recinto de la Feria, en Boquete"),
  (1, "/images/boquete/boquete-flowers2.webp",
      "Macizos de dalias bajo los pinos, con la montaña detrás"),
  (3, "/images/boquete/boquete-town2.webp",
      "El recinto ferial y sus jardines junto al río, vistos desde la ladera"),
  (4, "/images/boquete/boquete-plantation.webp",
      "Cafetos en producción en una finca de Boquete"),
  (5, "/images/boquete/boquete-street-peak.webp",
      "La calle de entrada a Boquete bajo el cerro"),
]},

# ── Mi Jardín es Su Jardín (ES) — the gardens themselves ──────────────────────
"public/es/articles/mi-jardin-es-su-jardin-boquete.html": {
 "hero": "/images/boquete/boquete-flowers2.webp",
 "place": [
  (1, "/images/boquete/boquete-pond.webp",
      "Un estanque con nenúfares entre helechos y platanillos en un jardín de Boquete"),
  (2, "/images/boquete/boquete-flowers.webp",
      "Un arbusto de coralillo en flor, con racimos naranjas y rojos"),
  (3, "Boquete, Panama.jpg",
      "Una casa de Boquete entre el jardín, con el cerro boscoso detrás"),
  (5, "/images/boquete/boquete-tree.webp",
      "El tronco de un árbol cubierto de líquenes entre los cafetos"),
  (6, "/images/boquete/boquete-town2.webp",
      "Los jardines sembrados junto al río, vistos desde arriba"),
]},

# ── Panama City to Boquete (EN) — the road and what waits at the end ──────────
"public/articles/panama-city-to-boquete.html": {
 "hero": "Vulkan Baru Boquete (27238202851).jpg",
 "place": [
  (1, "Albrook Bus Terminal.jpg",
      "The Albrook terminal in Panama City, where the long-distance buses west depart"),
  (2, "Aerial view of the Province of Chiriqui, Republic of Panama 09.jpg",
      "The Chiriquí highlands from the air — farm plots and cloud-topped ridge above David"),
  (3, "/images/boquete/boquete-terraces.webp",
      "Pines and terraced smallholdings on the climb up from the lowlands"),
  (5, "/images/boquete/boquete-street-peak.webp",
      "Arriving in Boquete: the road in, under the cloud-wrapped peak"),
  (7, "/images/boquete/boquete-clouds.webp",
      "Cloud spilling over the ridge — the bajareque that defines Boquete's weather"),
  (8, "/images/boquete/boquete-town2.webp",
      "Boquete town from the hillside, gardens along the river"),
]},

# ── Bike rental (EN) — the operator's own kit, not stock ──────────────────────
"public/articles/boquete-bike-rental.html": {
 "hero": "/images/boquete/boquete-ebike-hero.webp",
 "place": [
  (0, "/images/boquete/boquete-ebike-trail.webp",
      "Two riders on a dirt track through the coffee, e-bikes under them"),
  (1, "/images/boquete/boquete-ebike-orbea.webp",
      "A hardtail mountain bike — the standard rental, no motor"),
  (3, "/images/boquete/boquete-ebike-riders.webp",
      "An e-bike parked in the coffee bushes, helmet hooked over the bars"),
  (4, "/images/boquete/boquete-terraces.webp",
      "Pines and terraced plots on the slopes the routes climb through"),
  (5, "/images/boquete/boquete-clouds.webp",
      "Cloud rolling over the ridge — the afternoon pattern riders plan around"),
  (7, "/images/boquete/boquete-town.webp",
      "A street in Bajo Boquete, where the rides start and finish"),
]},

# ── Cycling routes (EN) — including the basalt wall we actually photographed ──
"public/articles/boquete-cycling-routes.html": {
 "hero": "/images/boquete/boquete-ebike-trail.webp",
 "place": [
  (1, "/images/boquete/boquete-ebike-orbea.webp",
      "A hardtail mountain bike, the baseline rental for these routes"),
  (2, "/images/boquete/boquete-rocks.webp",
      "A wall of columnar basalt beside the road north of Boquete"),
  (3, "/images/boquete/boquete-street-peak.webp",
      "The road out of town under the cloud-wrapped peak, farm plots on the slope"),
  (4, "/images/boquete/boquete-river2.webp",
      "The river running through its boulder bed between green hills"),
  (6, "/images/boquete/boquete-cloudforest.webp",
      "Cloud forest closing in on the upper slopes above Boquete"),
]},
}


def figure(ref, caption):
    alt = html.escape(caption)
    return (f'<figure class="art-inline-img" data-inlined="1" data-verified="1">'
            f'<div class="imgph photo">{img_html(url(ref), alt, GW, SIZES_INLINE)}</div>'
            f'<figcaption>{alt}</figcaption></figure>')


def set_hero(s, ref):
    alt = re.search(r'art-hero-img-full"><img[^>]*alt="([^"]*)"', s).group(1)
    s = re.sub(r'(art-hero-img-full">)<img[^>]*>',
               lambda m: m.group(1) + img_html(url(ref), alt, HERO, "100vw", eager=True),
               s, count=1)
    big = re.search(r'art-hero-img-full"><img src="([^"]+)"', s).group(1)
    # og/twitter need an absolute URL; local heroes are site-relative in the <img>.
    social = SITE + big if big.startswith("/") else big
    for pat in (r'(<meta content=")[^"]*(" property="og:image"/>)',
                r'(<meta content=")[^"]*(" name="twitter:image"/>)'):
        s = re.sub(pat, lambda m: m.group(1) + social + m.group(2), s, count=1)
    s = re.sub(r'(<link rel="preload" as="image" href=")[^"]*"[^>]*/>',
               lambda m: m.group(1) + big + '" fetchpriority="high"/>', s, count=1)
    # keep og:image:width/height honest
    d = re.search(r'art-hero-img-full"><img[^>]*width="(\d+)" height="(\d+)"', s)
    if d:
        s = re.sub(r'(<meta content=")\d+(" property="og:image:width"/>)',
                   lambda m: m.group(1) + d.group(1) + m.group(2), s, count=1)
        s = re.sub(r'(<meta content=")\d+(" property="og:image:height"/>)',
                   lambda m: m.group(1) + d.group(2) + m.group(2), s, count=1)
    return s


def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]

    for page, plan in PLAN.items():
        if only and only not in page:
            continue
        p = ROOT / page
        s = orig = p.read_text(encoding="utf-8")

        if plan["hero"]:
            s = set_hero(s, plan["hero"])

        hs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
        existing = {}
        for m in re.finditer(r'<figure class="art-inline-img"[^>]*>.*?</figure>', s, re.S):
            si = sum(1 for h in hs if h.start() < m.start()) - 1
            existing.setdefault(si, []).append(m.group(0))

        ins, swapped, added = [], 0, 0
        for si, ref, cap in plan["place"]:
            if si >= len(hs):
                print(f"  ! {page}: no section {si}")
                continue
            if existing.get(si):
                s = s.replace(existing[si].pop(0), figure(ref, cap), 1)
                swapped += 1
            else:
                start = hs[si].end()
                nxt = hs[si + 1].start() if si + 1 < len(hs) else len(s)
                pm = re.search(r"</p>", s[start:nxt])
                ins.append((start + pm.end() if pm else start, ref, cap))
                added += 1
        for off, ref, cap in sorted(ins, reverse=True):
            s = s[:off] + figure(ref, cap) + s[off:]

        if s != orig:
            p.write_text(s, encoding="utf-8")
            print(f"  ✓ {page.replace('public/',''):<62} hero={'set' if plan['hero'] else '—':<4} "
                  f"swapped={swapped} added={added}")


if __name__ == "__main__":
    main()
