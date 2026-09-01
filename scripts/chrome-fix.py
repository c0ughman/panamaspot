#!/usr/bin/env python3
"""chrome-fix.py — repair the shared chrome (header + footer) in static pages.

Three problems, all sitewide:
  1. Every destination is rendered as an inert <span class="footer-link-muted">,
     so 18 potential internal links per page do nothing. Destinations that now
     have a hub become real links; the rest stay muted until they have content.
  2. All 27 Spanish pages ship the ENGLISH footer. The Next component has the
     Spanish copy, but the static pages were generated from an English shell.
  3. Same for the header: the Spanish pages carry the English nav and search
     label, and their nav links point at the English homepage anchors.

Idempotent — safe to re-run after any content batch.
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# destination -> hub url (None = no page yet, stays muted)
EN_LINKS = {
    "Panama City": "/articles/panama-city",
    "Bocas del Toro": "/articles/bocas-del-toro",
    "Boquete &amp; Chiriquí": "/articles/boquete",
    "San Blas / Guna Yala": None,
    "Azuero Peninsula": None,
    "Coiba &amp; the Pacific": None,
    "The Darién": None,
}
ES_LINKS = {
    "Ciudad de Panamá": "/es/articles/panama-city",
    "Bocas del Toro": None,
    "San Blas / Guna Yala": "/es/articles/san-blas-guna-yala-guia-tours-islas",
    "Boquete y Chiriquí": "/es/articles/boquete",
    "Península de Azuero": None,
    "Coiba y el Pacífico": "/es/articles/isla-coiba-buceo-parque-nacional",
    "El Darién": None,
}
# El Valle is the strongest cluster on the site and was missing from the list
EN_EXTRA = ("El Valle de Antón", "/articles/el-valle-de-anton")
ES_EXTRA = ("El Valle de Antón", "/es/articles/el-valle-de-anton")

# Header, same root cause as the footer: generated from an English shell.
ES_HEADER = [
    ('<a href="/#cat-regions">Destinations</a>', '<a href="/es#cat-regions">Destinos</a>'),
    ('<a href="/#cat-activities">Eco-tourism</a>', '<a href="/es#cat-activities">Ecoturismo</a>'),
    ('<a href="/#cat-regions">Guides</a>', '<a href="/es#cat-regions">Guías</a>'),
    ('<a href="/#cat-regions">Plan a trip</a>', '<a href="/es#cat-regions">Planifica tu viaje</a>'),
    ('<span class="home-search-label">Search guides</span>',
     '<span class="home-search-label">Buscar guías</span>'),
]

# English -> Spanish, for the static /es pages that shipped the English footer
ES_COPY = [
    ("Every corner of the <em>isthmus</em>, written by people who live here.",
     "Cada rincón del <em>istmo</em>, escrito por quienes vivimos aquí."),
    ("Start exploring →", "Empieza a explorar →"),
    ("Independent travel journalism, written and edited by people who live in Panama. "
     "Eight provinces, three indigenous comarcas, one obsession.",
     "Periodismo de viajes independiente, escrito y editado por quienes vivimos en Panamá. "
     "Ocho provincias, tres comarcas indígenas, una obsesión."),
    ("<h4>Destinations</h4>", "<h4>Destinos</h4>"),
    ("<h4>By topic</h4>", "<h4>Por tema</h4>"),
    ("<h4>About</h4>", "<h4>Nosotros</h4>"),
    ("Panama City", "Ciudad de Panamá"),
    ("Boquete &amp; Chiriquí", "Boquete y Chiriquí"),
    ("Azuero Peninsula", "Península de Azuero"),
    ("Coiba &amp; the Pacific", "Coiba y el Pacífico"),
    ("The Darién", "El Darién"),
    ("Eco-tourism", "Ecoturismo"),
    ("Itineraries", "Itinerarios"),
    ("Wildlife &amp; birding", "Fauna y aves"),
    ("Food &amp; coffee", "Comida y café"),
    ("Surf &amp; dive", "Surf y buceo"),
    ("Practical info", "Información práctica"),
    ("Our writers", "Nuestros autores"),
    ("Editorial standards", "Estándares editoriales"),
    ("Work with us", "Trabaja con nosotros"),
    ("Press &amp; partners", "Prensa y socios"),
    ("Contact", "Contacto"),
    ("© 2026 Panamaspot · Panamá City, RP", "© 2026 Panamaspot · Ciudad de Panamá, RP"),
    ('href="/#cat-regions"', 'href="/es#cat-regions"'),
]

def patch_header(html, es):
    """Localise the Spanish pages' nav. English pages are already correct."""
    if not es or "<header" not in html:
        return html, 0
    a, b = html.index("<header"), html.index("</header>") + len("</header>")
    head, n = html[a:b], 0
    for en, sp in ES_HEADER:
        if en in head:
            head = head.replace(en, sp)
            n += 1
    return html[:a] + head + html[b:], n


def patch_footer(html, es):
    if "<footer" not in html:
        return html, 0
    a, b = html.index("<footer"), html.index("</footer>") + len("</footer>")
    foot, n = html[a:b], 0

    if es:
        for en, sp in ES_COPY:
            if en in foot:
                foot = foot.replace(en, sp)
                n += 1

    links = ES_LINKS if es else EN_LINKS
    for label, href in links.items():
        span = f'<span class="footer-link-muted">{label}</span>'
        if href and span in foot:
            foot = foot.replace(span, f'<a href="{href}">{label}</a>')
            n += 1

    # add El Valle to the destinations column if it isn't there yet
    label, href = ES_EXTRA if es else EN_EXTRA
    head = "<h4>Destinos</h4><ul>" if es else "<h4>Destinations</h4><ul>"
    if head in foot and f'>{label}</a>' not in foot:
        foot = foot.replace(head, f'{head}<li><a href="{href}">{label}</a></li>', 1)
        n += 1

    return html[:a] + foot + html[b:], n


def main():
    files = sorted(glob.glob(str(ROOT / "public/**/*.html"), recursive=True))
    touched = links_made = 0
    for f in files:
        p = Path(f)
        if "/funnels/" in f:
            continue
        html = p.read_text(encoding="utf8")
        es = "/es/" in f
        out, n = patch_footer(html, es)
        out, n2 = patch_header(out, es)
        n += n2
        if out != html:
            p.write_text(out, encoding="utf8")
            touched += 1
            links_made += n
    print(f"  patched {touched} files, {links_made} replacements")
    leftover = [f for f in files
                if "/es/" in f and "Eco-tourism</a>" in Path(f).read_text(encoding="utf8")]
    print(f"  ES pages still showing the English nav: {len(leftover)}")
    # report what's still inert, so the gap stays visible
    sample = ROOT / "public/articles/caldera-hot-springs-boquete.html"
    if sample.exists():
        h = sample.read_text(encoding="utf8")
        foot = h[h.index("<footer"):h.index("</footer>")]
        muted = re.findall(r'<span class="footer-link-muted">(.*?)</span>', foot)
        live = re.findall(r'<li><a href="(/[^"]+)">(.*?)</a></li>', foot)
        print(f"  EN sample -> {len(live)} live links, {len(muted)} still inert")
        for u, l in live:
            print(f"      link  {l:24} {u}")

if __name__ == "__main__":
    main()
