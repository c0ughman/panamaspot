#!/usr/bin/env python3
"""
interlink.py — organic in-prose internal links.

The pages carried 0-1 contextual links each; the only real internal linking was
the "Related guides" card module at the foot. This adds links inside the running
text, where a reader is actually thinking about the thing being linked.

Rules the client set, enforced here:
  - 5 to 8 in-prose links per page.
  - ONE link per paragraph, maximum. Never a paragraph that is a list of links,
    never a link bolted onto the end of a paragraph.
  - Spread across the article, not clustered in the intro.
  - Same language only. The English and Spanish sites are separate universes.
  - Same destination, or a genuine contextual reason to cross.
  - Reciprocal: older pages get links back to the newer ones.

Anchors are curated phrases that read as normal prose, matched against the
page's own words — nothing is inserted, only linked. Matching skips anything
inside an existing <a>, headings, captions, CTA blocks, the related module and
the credits list.

Both language universes now run. They never cross: an English page links only
to /articles/…, a Spanish page only to /es/articles/…, each with its own
anchor-phrase map, because the two sites are read by different people.

    python3 scripts/interlink.py            # forward: the pages under review
    python3 scripts/interlink.py --reciprocal   # older pages -> those pages

ADDITIVE. Running the forward pass twice stacks a second set of links on the
same pages. Snapshot before re-running, or restrict FOCUS.
"""
import re, sys, glob, pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ENGLISH universe. target slug -> anchor phrases, longest/most specific first.
# Only phrases a writer would plausibly have typed anyway.
TARGETS_EN = {
 # foundational hubs
 "bocas-del-toro":            ["Bocas del Toro archipelago", "Bocas Town", "Bocas del Toro"],
 "panama-city":               ["Panama City"],
 "boquete":                   ["Boquete", "Chiriquí"],
 "el-valle-de-anton":         ["El Valle de Antón", "El Valle"],
 # Bocas cluster
 "how-to-get-to-bocas-del-toro":        ["how to get to Bocas del Toro", "getting to Bocas del Toro",
                                         "Almirante", "water taxi"],
 "which-bocas-del-toro-island-to-stay-on": ["which island to stay on", "where to stay in Bocas del Toro",
                                            "Isla Colón", "Isla Colon"],
 "red-frog-beach-bocas-del-toro":       ["Red Frog Beach", "Isla Bastimentos", "Bastimentos"],
 "starfish-beach-bocas-del-toro-playa-estrella-guide": ["Starfish Beach", "Playa Estrella",
                                                        "Boca del Drago"],
 "cayos-zapatillas-snorkelling-bocas-del-toro": ["Cayos Zapatillas", "Zapatilla cays", "Cayo Zapatilla"],
 "bocas-del-toro-island-hopping-guide": ["island hopping", "island-hopping"],
 # Guna Yala / islands
 "san-blas-islands-panama-guna-yala-guide": ["San Blas islands", "San Blas Islands", "Guna Yala", "San Blas"],
 # "Cartagena" and the long forms appear nowhere but on the page itself, so this
 # guide had one inbound link. "sailing trip" is the phrase the other pages
 # actually use for it. NOT bare "Colombia" — that turns up in coffee and
 # comparison contexts too.
 "san-blas-sailing-panama-to-colombia":     ["sailing from Panama to Colombia", "sailboat to Colombia",
                                             "Cartagena", "sailing trip"],
 "pearl-islands-panama-guide":              ["Pearl Islands", "Contadora"],
 # practical / national
 "renting-a-car-in-panama":   ["renting a car in Panama", "renting a car", "rental car",
                              "Interamericana"],
 # NOT bare "safety" — it matched "complete safety briefings" on a sailing
 # page and sent the reader to a piece about crime in Panama.
 "is-panama-safe":            ["is Panama safe", "safety in Panama"],
 "best-time-to-visit-panama": ["best time to visit Panama", "dry season"],
 "boat-charter-panama":       ["chartering a boat", "boat charter"],
 # Panama City cluster
 "casco-viejo-panama-walking-guide": ["Casco Viejo"],
 "panama-canal-tour-miraflores-locks-visitor-guide": ["Miraflores Locks", "Miraflores"],
 "amador-causeway-biomuseo-guide":   ["Amador Causeway"],
 "day-trips-from-panama-city":       ["day trips from Panama City", "Portobelo"],
 "panama-city-itinerary-3-days":     ["three days in Panama City"],
 # highlands / Boquete cluster.
 # The generic phrases here ("hiking", "coffee farms", "dry season", "Jaramillo")
 # are safe ONLY because CLUSTER_ONLY locks them to Boquete: on a Boquete page
 # the reader saying "hiking" means Boquete's trails. They are the phrases these
 # pages actually use — checked against the prose, not guessed.
 # NOT bare "Baru": it matched "Super Baru", the supermarket in Bajo Boquete,
 # and sent shoppers to a 13.5 km volcano hike. The accented "Barú" is safe.
 "volcan-baru-hike-sunrise-summit-guide": ["Volcán Barú", "Volcan Baru", "Barú"],
 "things-to-do-in-boquete-panama":    ["things to do in Boquete"],
 "hikes-in-boquete":                  ["hikes in Boquete", "hiking in Boquete", "Pipeline Trail",
                                       "hiking", "hikes", "hike", "trails", "trail"],
 "boquete-coffee-farm-tour":          ["coffee farm tour", "coffee farms", "coffee farm", "coffee tour"],
 "panama-city-to-boquete":            ["Panama City to Boquete", "Albrook", "David", "flight", "bus"],
 "boquete-travel-guide":              ["three days in Boquete", "Boquete itinerary"],
 "tours-in-boquete-panama":           ["tours in Boquete", "Boquete tours", "guided tour", "tours", "tour"],
 # NOT bare "dry season" — best-time-to-visit-panama already claims that phrase
 # and is national, so the two would race for the same anchor on a Boquete page.
 "best-time-to-visit-boquete":        ["best time to visit Boquete", "dry season in Boquete",
                                       "in the dry season", "bajareque", "rainy season"],
 "boquete-bike-rental":               ["bike rental in Boquete", "renting a bike", "bike rental",
                                       "e-bikes", "e-bike"],
 "boquete-cycling-routes":            ["cycling routes", "cycling in Boquete", "Bajo Mono Loop",
                                       "Bajo Mono", "cycling"],
 "boquete-hot-springs-caldera-vs-los-pozos": ["Boquete hot springs", "Los Pozos de Caldera",
                                              "Los Pozos", "hot springs"],
 "caldera-hot-springs-boquete":       ["Caldera Hot Springs", "Caldera hot springs"],
 "where-to-stay-in-boquete":          ["where to stay in Boquete", "Bajo Boquete", "Jaramillo",
                                       "Alto Quiel", "Volcancito", "Palo Alto"],
 "quetzal-season-boquete-when-where-to-see-resplendent-quetzal":
                                      ["resplendent quetzals", "resplendent quetzal", "quetzal season",
                                       "quetzals", "quetzal"],
 "finca-lerida-los-quetzales-trail-birdwatching-boquete":
                                      ["Finca Lérida", "Finca Lerida", "Los Quetzales Trail",
                                       "birdwatching", "birding"],
 "lost-waterfalls-boquete-hiking-guide": ["Lost Waterfalls"],
 "things-to-do-el-valle-de-anton":    ["things to do in El Valle"],
 # El Valle de Antón cluster
 # The extra phrases are the ones the OLDER El Valle pages actually use, so the
 # reciprocal pass has something to bite on: "a single day", "accommodation",
 # "than Boquete".
 "el-valle-de-anton-itinerary-one-day":  ["El Valle in one day", "one-day itinerary",
                                          "one day in El Valle", "a single day"],
 "where-to-stay-in-el-valle-de-anton":   ["where to stay in El Valle", "accommodation in El Valle",
                                          "where to stay", "accommodation"],
 # Unlocked from the El Valle cluster on purpose: a comparison page naming both
 # towns is exactly the "contextually significant" cross-link, so Boquete pages
 # may reach it too. The anchors name both places, so they cannot misfire.
 # ("than Boquete" was a hook for the El Valle reciprocal pass; it has served
 # its purpose and is too loose to keep now that Boquete pages are in play.)
 "el-valle-de-anton-vs-boquete":         ["El Valle or Boquete", "Boquete or El Valle",
                                          "mountain town"],
 "chorro-el-macho-waterfall-el-valle-de-anton": ["Chorro El Macho"],
 "india-dormida-hike-el-valle-de-anton": ["La India Dormida", "India Dormida"],
 "el-valle-de-anton-waterfalls":         ["waterfalls in El Valle"],
 "el-valle-de-anton-with-kids":          ["El Valle with kids"],
 "hikes-el-valle-de-anton":              ["hikes in El Valle", "hiking in El Valle"],
 "tours-en-el-valle-de-anton":           ["tours in El Valle"],
 "el-valle-day-trip-from-panama-city":   ["day trip from Panama City", "day trip to El Valle"],
 "cerro-gaital-cara-iguana-hike-el-valle": ["Cerro Gaital", "Cara Iguana"],
}

# SPANISH universe. Same rules, its own phrases — a Spanish reader never gets
# sent to an English page, so this map is completely separate.
TARGETS_ES = {
 # hubs
 "el-valle-de-anton":  ["El Valle de Antón", "El Valle"],
 "boquete":            ["Boquete", "Chiriquí"],
 "panama-city":        ["Ciudad de Panamá"],
 # El Valle — the guides
 "que-hacer-el-valle-de-anton":        ["qué hacer en El Valle"],
 "tours-el-valle-de-anton":            ["tours en El Valle", "tours guiados"],
 "senderos-el-valle-de-anton":         ["senderos de El Valle", "senderismo"],
 "sendero-india-dormida-el-valle-de-anton": ["La India Dormida", "India Dormida"],
 "cascada-chorro-el-macho-el-valle-de-anton": ["Chorro El Macho", "El Chorro Macho", "Chorro Macho"],
 "chorro-las-mozas-pozas-el-valle-de-anton": ["Chorro Las Mozas", "Las Mozas"],
 "aguas-termales-el-valle-de-anton":   ["aguas termales", "pozas termales", "pozos termales"],
 "zoologico-el-nispero-el-valle-de-anton": ["Zoológico El Níspero", "El Níspero", "zoológico"],
 "mariposario-el-valle-de-anton":      ["Mariposario Butterfly Haven", "mariposario", "Mariposario",
                                        "serpentario", "Serpentario"],
 "piedra-pintada-el-valle-de-anton":   ["La Piedra Pintada", "Piedra Pintada", "petroglifos"],
 "mercado-el-valle-de-anton":          ["mercado artesanal", "Mercado Artesanal", "mercado público",
                                        "mercado de artesanías"],
 "donde-comer-en-el-valle-de-anton":   ["dónde comer", "fondas"],
 "donde-dormir-el-valle-de-anton":     ["dónde dormir", "hospedaje", "alojamiento"],
 "precios-horarios-el-valle-de-anton": ["precios y horarios", "horarios y precios"],
 "tours-en-bicicleta-el-valle-de-anton": ["tours en bicicleta", "alquiler de bicicletas",
                                          "bicicleta eléctrica", "e-bike"],
 "bus-albrook-el-valle-de-anton-horarios-precios": ["Terminal de Albrook", "terminal de Albrook",
                                                    "Albrook"],
 "el-valle-de-anton-desde-ciudad-de-panama": ["desde Ciudad de Panamá"],
 "canopy-el-valle-de-anton-cabalgatas-aventura": ["canopy", "cabalgatas", "tirolesa"],
 # Boquete. Same reasoning as the English cluster: the loose phrases
 # ("senderos", "café", "jardines", "niños") only fire inside Boquete, so a
 # Spanish reader on a Boquete page is never sent to El Valle's version.
 "que-hacer-en-boquete-guia-completa": ["qué hacer en Boquete", "qué hacer", "Bajo Boquete"],
 "senderos-en-boquete-guia-completa":  ["senderos de Boquete", "senderos", "senderismo", "caminata"],
 "volcan-baru-como-subir-cima-panama": ["Volcán Barú", "Barú", "cima", "subida"],
 "el-volcan-baru-esta-activo":         ["está activo", "sigue activo", "volcán activo", "volcán"],
 "como-llegar-a-boquete-sin-carro":    ["cómo llegar a Boquete", "Albrook"],
 "alquiler-de-bicicletas-boquete":     ["alquiler de bicicletas en Boquete", "alquiler de bicicletas",
                                        "bicicletas", "bicicleta"],
 "tours-en-boquete-panama":            ["tours en Boquete", "fincas de café", "cafetales", "tours", "café"],
 "aguas-termales-caldera-boquete":     ["aguas termales de Caldera", "aguas termales", "termales",
                                        "Caldera"],
 "boquete-panama-guia-completa-itinerario": ["itinerario de 3 días", "tres días en Boquete",
                                             "tres días", "itinerario"],
 "rafting-boquete-rio-chiriqui":       ["Río Chiriquí Viejo", "rafting"],
 "boquete-con-ninos-guia-familiar":    ["Boquete con niños", "con niños", "en familia", "niños"],
 "cuanto-cuesta-boquete-presupuesto-semana": ["cuánto cuesta Boquete", "cuánto cuesta", "presupuesto",
                                             "precios"],
 "feria-de-las-flores-y-del-cafe-boquete": ["Feria de las Flores y del Café", "Feria de las Flores",
                                            "la Feria"],
 "mi-jardin-es-su-jardin-boquete":     ["Mi Jardín es Su Jardín", "Mi Jardín", "jardines"],
 # elsewhere
 "san-blas-guna-yala-guia-tours-islas": ["San Blas", "Guna Yala"],
 "como-llegar-a-bocas-del-toro-desde-ciudad-de-panama": ["Bocas del Toro"],
 "isla-coiba-buceo-parque-nacional":   ["isla Coiba", "Coiba"],
 "casco-viejo-restaurantes-donde-comer-beber-hospedarse": ["Casco Viejo"],
 "que-hacer-en-ciudad-de-panama":      ["qué hacer en Ciudad de Panamá"],
}

# which destination each page belongs to, so links stay in-cluster unless the
# target is national/foundational
# Checked in this order: a slug like el-valle-de-anton-desde-ciudad-de-panama
# must resolve to El Valle, not to Panama City, so the destinations come first.
CLUSTER = {
 "elvalle":["el-valle","valle-de-anton","india-dormida","gaital","macho","nispero","mozas",
            "piedra-pintada","mariposario","tours-en-bicicleta","precios-horarios","bus-albrook"],
 "boquete":["boquete","baru","caldera","quetzal","lerida"],
 "bocas": ["bocas","zapatilla","red-frog","starfish","which-bocas"],
 "guna":  ["san-blas","guna"],
 "pearl": ["pearl"],
 "city":  ["panama-city","ciudad-de-panama","casco","amador","canal","miraflores","day-trips","charter","cinta-costera"],
}
NATIONAL = {"renting-a-car-in-panama","is-panama-safe","best-time-to-visit-panama",
            "panama-city","bocas-del-toro","boquete","el-valle-de-anton"}

# Targets whose anchor phrases are generic enough to fire anywhere ("island
# hopping", "water taxi", "coffee farms"). Linking those from another
# destination is a non-sequitur — a Pearl Islands page should not send "island
# hopping" to a Bocas guide — so they only fire inside their own cluster.
# Spanish anchors generic enough to fire anywhere ("aguas termales", "canopy",
# "senderismo", "alojamiento"). Locked to their own destination for the same
# reason as the English ones: a Boquete page saying "aguas termales" means the
# Caldera pools, not El Valle's.
CLUSTER_ONLY_ES = {
 # "Albrook" is where every long-distance bus in Panama leaves from, so the
 # word turns up on the Bocas, Boquete, Coiba and Panama City guides. Their
 # readers want their own route, not El Valle's — lock it to the crater.
 "bus-albrook-el-valle-de-anton-horarios-precios": "elvalle",
 "chorro-las-mozas-pozas-el-valle-de-anton": "elvalle",
 "aguas-termales-el-valle-de-anton": "elvalle",
 "zoologico-el-nispero-el-valle-de-anton": "elvalle",
 "mariposario-el-valle-de-anton": "elvalle",
 "mercado-el-valle-de-anton": "elvalle",
 "donde-comer-en-el-valle-de-anton": "elvalle",
 "donde-dormir-el-valle-de-anton": "elvalle",
 "precios-horarios-el-valle-de-anton": "elvalle",
 "tours-en-bicicleta-el-valle-de-anton": "elvalle",
 "senderos-el-valle-de-anton": "elvalle",
 "tours-el-valle-de-anton": "elvalle",
 "canopy-el-valle-de-anton-cabalgatas-aventura": "elvalle",
 "piedra-pintada-el-valle-de-anton": "elvalle",
 "aguas-termales-caldera-boquete": "boquete",
 "alquiler-de-bicicletas-boquete": "boquete",
 "senderos-en-boquete-guia-completa": "boquete",
 "tours-en-boquete-panama": "boquete",
 # the 2026-09 Spanish Boquete pages and the older guides they pair with
 "que-hacer-en-boquete-guia-completa": "boquete",
 "volcan-baru-como-subir-cima-panama": "boquete",
 "el-volcan-baru-esta-activo": "boquete",
 "como-llegar-a-boquete-sin-carro": "boquete",
 "boquete-panama-guia-completa-itinerario": "boquete",
 "rafting-boquete-rio-chiriqui": "boquete",
 "boquete-con-ninos-guia-familiar": "boquete",
 "cuanto-cuesta-boquete-presupuesto-semana": "boquete",
 "feria-de-las-flores-y-del-cafe-boquete": "boquete",
 "mi-jardin-es-su-jardin-boquete": "boquete",
}
NATIONAL_ES = {"el-valle-de-anton", "boquete", "panama-city"}

CLUSTER_ONLY = {
                # "accommodation", "where to stay", "a single day" and "than
                # Boquete" turn up on every destination guide on the site. They
                # may only point at the El Valle pages from inside El Valle.
                "where-to-stay-in-el-valle-de-anton": "elvalle",
                "el-valle-de-anton-itinerary-one-day": "elvalle",
                "bocas-del-toro-island-hopping-guide": "bocas",
                "how-to-get-to-bocas-del-toro": "bocas",
                "boquete-coffee-farm-tour": "boquete",
                "which-bocas-del-toro-island-to-stay-on": "bocas",
                "red-frog-beach-bocas-del-toro": "bocas",
                # 2026-09 English Boquete pages + the older guides they pair
                # with. "hiking", "tours", "dry season", "Jaramillo", "David"
                # and "Barú" all turn up across the site; inside Boquete they
                # mean Boquete's version of the thing, nowhere else.
                "hikes-in-boquete": "boquete",
                "tours-in-boquete-panama": "boquete",
                "boquete-travel-guide": "boquete",
                "things-to-do-in-boquete-panama": "boquete",
                "best-time-to-visit-boquete": "boquete",
                "boquete-bike-rental": "boquete",
                "boquete-cycling-routes": "boquete",
                "boquete-hot-springs-caldera-vs-los-pozos": "boquete",
                "caldera-hot-springs-boquete": "boquete",
                "where-to-stay-in-boquete": "boquete",
                "quetzal-season-boquete-when-where-to-see-resplendent-quetzal": "boquete",
                "finca-lerida-los-quetzales-trail-birdwatching-boquete": "boquete",
                "lost-waterfalls-boquete-hiking-guide": "boquete",
                "volcan-baru-hike-sunrise-summit-guide": "boquete",
                "panama-city-to-boquete": "boquete"}

def cluster_of(slug):
    s = slug.lower()
    for c, keys in CLUSTER.items():
        if any(k in s for k in keys):
            return c
    return "other"

# regions of the document that must never be touched
SKIP = [r'(?s)<!--RELATED-MODULE-->.*?<!--/RELATED-MODULE-->',
        r'(?s)<!--IMGCREDITS-->.*?<!--/IMGCREDITS-->',
        r'(?s)<aside class="evb-rail".*?</aside>',
        r'(?s)<!--EVB-CTA:[a-z]+-->.*?<!--/EVB-CTA:[a-z]+-->',
        r'(?s)<section class="evb-cta.*?</section>',
        r'(?s)<script.*?</script>', r'(?s)<header.*?</header>',
        r'(?s)<footer.*?</footer>', r'(?s)<figure.*?</figure>',
        r'(?s)<nav class="breadcrumb".*?</nav>']

# Divs whose whole subtree is off limits. These need real nesting awareness:
# the old rule was r'<div class="evb-cta".*?</div></div></div>', and because the
# CTA's own nesting does not end on the first triple </div> the match ran on far
# past the block — swallowing 1005 of 3852 body paragraphs (26%) across 60 pages,
# worst on the Boquete pages where the e-bike CTAs live. Every interlinking pass
# before 2026-09-09 was choosing anchors from only three-quarters of the article.
SKIP_DIV = [r'<div class="evb-cta']

_DIV = re.compile(r'<div\b[^>]*>|</div>', re.S)

def balanced_div_span(s, start):
    """End offset of the <div> opening at `start`, respecting nesting."""
    depth = 0
    for m in _DIV.finditer(s, start):
        depth += 1 if m.group(0)[1] != '/' else -1
        if depth == 0:
            return m.end()
    return len(s)          # unbalanced markup: skip to the end, never past it

def protected_spans(s):
    spans = []
    for pat in SKIP:
        spans += [(m.start(), m.end()) for m in re.finditer(pat, s)]
    for pat in SKIP_DIV:
        for m in re.finditer(pat, s):
            spans.append((m.start(), balanced_div_span(s, m.start())))
    spans += [(m.start(), m.end()) for m in re.finditer(r"(?s)<a\b.*?</a>", s)]
    return spans

def in_span(i, spans):
    return any(a <= i < b for a, b in spans)

def paragraphs(s):
    """Linkable prose units, in document order.

    Every <p>, plus each <ul>/<ol> taken WHOLE — a bullet is running prose and
    often the only place a page names a thing, but treating a list as one unit
    means it can take one link, never a bulleted column of them. Tables are left
    out on purpose: a link in a price cell reads as a footnote, not as prose.
    """
    spans = protected_spans(s)
    # Only the article body. <p>s also live in the "Three things to know" cards
    # and the FAQ below it; those are summaries, not running prose, and a link
    # in a stat card reads as a stray.
    art = re.search(r"(?s)<article\b.*?</article>", s)
    lo, hi = (art.start(), art.end()) if art else (0, len(s))
    out = []
    for m in re.finditer(r"(?s)<p>(.*?)</p>|<(ul|ol)>(.*?)</\2>", s):
        if not (lo <= m.start() < hi) or in_span(m.start(), spans):
            continue
        g = 1 if m.group(1) is not None else 3
        out.append((m.start(g), m.end(g)))
    return sorted(out)

def link_page(path, targets, want_min, want_max, only=None):
    p = pathlib.Path(path)
    s = p.read_text(encoding="utf-8")
    slug = p.stem
    lang = "es" if "/es/" in p.as_posix() else "en"
    prefix = "/es/articles" if lang == "es" else "/articles"
    only_map = CLUSTER_ONLY_ES if lang == "es" else CLUSTER_ONLY
    national = NATIONAL_ES if lang == "es" else NATIONAL
    mine = cluster_of(slug)

    paras = paragraphs(s)
    if not paras:
        return 0
    prose = " ".join(s[a:b] for a, b in paras)
    already = set(re.findall(r'href="/(?:es/)?articles/([^"#?]+)"', prose))
    have = len(re.findall(r'href="/(?:es/)?articles/', prose))   # link INSTANCES
    # paragraphs that already carry an internal link are off limits
    occupied = {i for i, (a, b) in enumerate(paras)
                if re.search(r'href="/(?:es/)?articles/', s[a:b])}

    # candidate (paragraph_index, position, phrase, target)
    cands = []
    for pi, (a, b) in enumerate(paras):
        chunk = s[a:b]
        for tslug, phrases in targets.items():
            if tslug == slug or tslug in already or (only and tslug not in only):
                continue
            tc = cluster_of(tslug)
            # Same destination and the foundational pages come first; a
            # different destination is still allowed, because the anchor phrase
            # only matches when the page's own prose already names that place —
            # the match IS the contextual justification. Ranking, not blocking,
            # keeps most links inside the cluster.
            if tslug in only_map and only_map[tslug] != mine:
                continue
            prio = 0 if (tc == mine or tslug in national) else 1
            for ph in phrases:
                m = re.search(r"(?<![\w>])" + re.escape(ph) + r"(?![\w<])", chunk)
                if m:
                    cands.append((pi, a + m.start(), a + m.end(), ph, tslug, prio))
                    break

    # Spread: split the article into want_max bands and allow one link per band,
    # so they never bunch up in the intro or read as a list.
    chosen, used_p, used_t, used_b = [], set(occupied), set(), set()
    band = max(1, len(paras) / float(max(want_max, 1)))
    for pi, st, en, ph, tslug, prio in sorted(cands, key=lambda c: (c[5], c[0], -len(c[3]))):
        b = int(pi // band)
        if pi in used_p or tslug in used_t or b in used_b:
            continue
        chosen.append((pi, st, en, ph, tslug))
        used_p.add(pi); used_t.add(tslug); used_b.add(b)
        if len(chosen) + have >= want_max:      # ceiling counts what was already there
            break
    if len(chosen) + have < want_min:           # relax the banding to reach the floor
        for pi, st, en, ph, tslug, prio in sorted(cands, key=lambda c: (c[5], c[0], -len(c[3]))):
            if len(chosen) + have >= want_min:
                break
            if pi in used_p or tslug in used_t:
                continue
            chosen.append((pi, st, en, ph, tslug))
            used_p.add(pi); used_t.add(tslug)
        chosen.sort()

    for pi, st, en, ph, tslug in sorted(chosen, key=lambda c: -c[1]):
        s = s[:st] + f'<a href="{prefix}/{tslug}">{s[st:en]}</a>' + s[en:]
    if chosen:
        p.write_text(s, encoding="utf-8")
    return len(chosen)

# The 2026-09 BOQUETE batch. The El Valle batch was done in b9ebef8; this pass
# is the Boquete cluster. interlink.py is ADDITIVE, so el-valle-de-anton-vs-boquete
# is deliberately absent from the forward lists — it already carries 10 in-prose
# links from the El Valle pass and a second forward run would stack another set on
# top. It stays in RECIP_* so the other Boquete pages still link INTO it.
FOCUS_EN = ["best-time-to-visit-boquete",
            "boquete-bike-rental",
            "boquete-cycling-routes",
            "boquete-hot-springs-caldera-vs-los-pozos",
            "panama-city-to-boquete",
            "quetzal-season-boquete-when-where-to-see-resplendent-quetzal",
            "where-to-stay-in-boquete"]
FOCUS_ES = ["boquete-con-ninos-guia-familiar",
            "cuanto-cuesta-boquete-presupuesto-semana",
            "el-volcan-baru-esta-activo",
            "feria-de-las-flores-y-del-cafe-boquete",
            "mi-jardin-es-su-jardin-boquete"]

# What the reciprocal pass is allowed to point older pages AT.
RECIP_EN = FOCUS_EN + ["el-valle-de-anton-vs-boquete"]
RECIP_ES = list(FOCUS_ES)

def main():
    recip = "--reciprocal" in sys.argv
    jobs = (("en", FOCUS_EN, TARGETS_EN, ROOT/"public"/"articles", "public/articles/*.html"),
            ("es", FOCUS_ES, TARGETS_ES, ROOT/"public"/"es"/"articles", "public/es/articles/*.html"))
    for lang, focus, targets, folder, pattern in jobs:
        if not recip:
            print(f"forward links, {lang.upper()} — the pages under review:")
            for slug in focus:
                n = link_page(folder/f"{slug}.html", targets, 5, 8)
                print(f"  {slug:<52} +{n}")
        else:
            print(f"reciprocal links, {lang.upper()} — older pages -> the pages under review:")
            only = set(RECIP_EN if lang == "en" else RECIP_ES)
            for f in sorted(glob.glob(pattern)):
                if pathlib.Path(f).stem in only:
                    continue
                n = link_page(f, {k: v for k, v in targets.items() if k in only}, 0, 2, only=only)
                if n:
                    print(f"  {pathlib.Path(f).stem:<52} +{n}")
        print()

if __name__ == "__main__":
    main()
