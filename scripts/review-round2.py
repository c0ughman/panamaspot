#!/usr/bin/env python3
"""
review-round2.py — the client's second round of image notes, applied.

Section numbers below are the numbers PRINTED ON THE PAGE ("Section 05"), which
is what the client is reading; the code converts to the zero-based index.

    python3 scripts/review-round2.py
"""
import re, sys, json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from img_cap import img_html, GALLERY as GW

SIZES = "(max-width: 768px) 100vw, 768px"
META = json.loads((ROOT / "scripts" / "commons-verified.json").read_text(encoding="utf-8"))


def url(ref):
    return ref if ref.startswith("/images/") else META[ref]["url"]


def figures(s):
    hs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
    out = {}
    for m in re.finditer(r'<figure class="art-inline-img[^"]*"[^>]*>.*?</figure>', s, re.S):
        si = sum(1 for h in hs if h.start() < m.start()) - 1
        out[si] = m
    return out


def figure_html(ref, caption):
    alt = html.escape(caption)
    return (f'<figure class="art-inline-img" data-inlined="1" data-verified="1">'
            f'<div class="imgph photo">{img_html(url(ref), alt, GW, SIZES)}</div>'
            f'<figcaption>{alt}</figcaption></figure>')


def swap(path, display_section, ref, caption):
    """Replace the figure in a printed section number."""
    p = ROOT / path; s = p.read_text(encoding="utf-8")
    f = figures(s).get(display_section - 1)
    if not f:
        print(f"  ! {path}: no figure in section {display_section:02d}"); return
    p.write_text(s[:f.start()] + figure_html(ref, caption) + s[f.end():], encoding="utf-8")
    print(f"  ✓ {path.split('/')[-1][:44]:<46} s{display_section:02d} ← {ref.split('/')[-1][:38]}")


def drop(path, display_section):
    p = ROOT / path; s = p.read_text(encoding="utf-8")
    f = figures(s).get(display_section - 1)
    if not f:
        print(f"  ! {path}: no figure in section {display_section:02d}"); return
    p.write_text(s[:f.start()] + s[f.end():], encoding="utf-8")
    print(f"  ✓ {path.split('/')[-1][:44]:<46} s{display_section:02d} removed")


def promote(path, display_section, new_caption_for_old_hero):
    """Make a section's photo the hero, and send the old hero down to that section."""
    p = ROOT / path; s = p.read_text(encoding="utf-8")
    hero = re.search(r'(art-hero-img-full"><img )(.*?)(>)', s, re.S)
    old_src = re.search(r'src="([^"]+)"', hero.group(2)).group(1)
    hero_alt = re.search(r'alt="([^"]*)"', hero.group(2)).group(1)
    f = figures(s).get(display_section - 1)
    new_src = re.search(r'src="([^"]+)"', f.group(0)).group(1)

    # old hero URL -> a source ref the helpers understand
    old_ref = old_src if old_src.startswith("/images/") else next(
        (t for t, m in META.items() if m["url"] == old_src.replace("&amp;", "&")), None)
    if old_ref is None:                       # a capped Commons thumb: reverse it
        from img_cap import wm_original
        o = wm_original(old_src.replace("&amp;", "&"))
        old_ref = next((t for t, m in META.items() if m["url"] == o), None)
    if old_ref is None:
        print(f"  ! {path}: cannot resolve the old hero back to a source"); return

    s = s[:f.start()] + figure_html(old_ref, new_caption_for_old_hero) + s[f.end():]
    new_ref = new_src if new_src.startswith("/images/") else next(
        (t for t, m in META.items() if m["url"] == new_src.replace("&amp;", "&")), new_src)
    s = re.sub(r'(art-hero-img-full">)<img[^>]*>',
               lambda m: m.group(1) + img_html(url(new_ref) if not new_ref.startswith("http") else new_ref,
                                               hero_alt, 1280, "100vw", eager=True), s, count=1)
    big = re.search(r'art-hero-img-full"><img src="([^"]+)"', s).group(1)
    social = "https://panamaspot.com" + big if big.startswith("/") else big
    for pat in (r'(<meta content=")[^"]*(" property="og:image"/>)',
                r'(<meta content=")[^"]*(" name="twitter:image"/>)'):
        s = re.sub(pat, lambda m: m.group(1) + social + m.group(2), s, count=1)
    s = re.sub(r'(<link rel="preload" as="image" href=")[^"]*"[^>]*/>',
               lambda m: m.group(1) + big + '" fetchpriority="high"/>', s, count=1)
    d = re.search(r'art-hero-img-full"><img[^>]*width="(\d+)" height="(\d+)"', s)
    if d:
        s = re.sub(r'(<meta content=")\d+(" property="og:image:width"/>)', lambda m: m.group(1)+d.group(1)+m.group(2), s, count=1)
        s = re.sub(r'(<meta content=")\d+(" property="og:image:height"/>)', lambda m: m.group(1)+d.group(2)+m.group(2), s, count=1)
    p.write_text(s, encoding="utf-8")
    print(f"  ✓ {path.split('/')[-1][:44]:<46} hero ← s{display_section:02d}; old hero → s{display_section:02d}")


def main():
    A = "public/articles/"; E = "public/es/articles/"

    # 1. best-time: section 05 loses the bike map, gains the town
    swap(A+"best-time-to-visit-boquete.html", 5, "/images/boquete/boquete-town2.webp",
         "Boquete on the valley floor, the gardens running along the river")

    # 2. bike rental: the map belongs where the routes are listed
    swap(A+"boquete-bike-rental.html", 5, "/images/boquete/boquete-cycling-map.webp",
         "The five rides, mapped: routes climbing north to Alto Quiel and Jaramillo and west "
         "toward Volcancito and Palmira, with viewpoints, water, coffee and the bike shop marked. "
         "Map data © Mapbox © OpenStreetMap.")

    # 3. cycling routes: a new photo for the Volcancito Road section
    swap(A+"boquete-cycling-routes.html", 4, "/images/boquete/boquete-terraces.webp",
         "Pines and terraced smallholdings on the slopes west of the valley")

    # 4. where to stay: the section 07 photo becomes the hero
    promote(A+"where-to-stay-in-boquete.html", 7,
            "Boquete from the hillside, the town compact on the valley floor")

    # 5. niños: section 06 photo becomes the hero; section 06 gets the hot springs it describes
    promote(E+"boquete-con-ninos-guia-familiar.html", 6,
            "Un grupo de niños con mochilas explorando un bosque de pinos")
    swap(E+"boquete-con-ninos-guia-familiar.html", 6, "Calderahotsprings.JPG",
         "Las pozas de aguas termales de Caldera, de piedra y poca profundidad")
    drop(E+"boquete-con-ninos-guia-familiar.html", 9)

    # 6. cuánto cuesta: section 03 photo becomes the hero; section 04 takes the niños plate
    promote(E+"cuanto-cuesta-boquete-presupuesto-semana.html", 3,
            "Boquete visto desde la ladera, el pueblo compacto en el fondo del valle")
    swap(E+"cuanto-cuesta-boquete-presupuesto-semana.html", 4, "/images/boquete/boquete-food2.webp",
         "Ropa vieja servida sobre plátano en hoja de bijao")

    # 7. feria: the riverside flower gardens at the entrance bridge — an actual Feria photograph
    swap(E+"feria-de-las-flores-y-del-cafe-boquete.html", 4, "RVN06957.jpg",
         "El recinto junto al río Caldera: bancas de colores, barriles sembrados y macizos de "
         "flores a lo largo de la orilla")

    # 8. how to get to Boquete: section 06 swapped
    swap(A+"panama-city-to-boquete.html", 6, "/images/boquete/boquete-cabbage.webp",
         "Campos de repollo junto a la carretera en las tierras altas, con los cerros en la neblina"
         if False else "Cabbage fields beside the road in the highlands, the hills lost in mist")

    # 9. Barú: the client's own dusk photograph of the volcano becomes the hero
    promote(E+"el-volcan-baru-esta-activo.html", 8,
            "La cima del Barú al amanecer, por encima de la capa de nubes")


if __name__ == "__main__":
    main()
