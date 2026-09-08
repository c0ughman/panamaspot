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

    python3 scripts/interlink.py [--reciprocal]
"""
import re, sys, glob, pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent

# target slug -> anchor phrases, longest/most specific first.
# Only phrases a writer would plausibly have typed anyway.
TARGETS = {
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
 "san-blas-sailing-panama-to-colombia":     ["sailing from Panama to Colombia", "sailboat to Colombia",
                                             "Cartagena"],
 "pearl-islands-panama-guide":              ["Pearl Islands", "Contadora"],
 # practical / national
 "renting-a-car-in-panama":   ["renting a car in Panama", "renting a car", "rental car"],
 "is-panama-safe":            ["is Panama safe", "safety in Panama"],
 "best-time-to-visit-panama": ["best time to visit Panama", "dry season"],
 "boat-charter-panama":       ["chartering a boat", "boat charter"],
 # Panama City cluster
 "casco-viejo-panama-walking-guide": ["Casco Viejo"],
 "panama-canal-tour-miraflores-locks-visitor-guide": ["Miraflores Locks", "Miraflores"],
 "amador-causeway-biomuseo-guide":   ["Amador Causeway"],
 "day-trips-from-panama-city":       ["day trips from Panama City", "Portobelo"],
 "panama-city-itinerary-3-days":     ["three days in Panama City"],
 # highlands
 "volcan-baru-hike-sunrise-summit-guide": ["Volcán Barú", "Volcan Baru"],
 "things-to-do-in-boquete-panama":    ["things to do in Boquete"],
 "hikes-in-boquete":                  ["hikes in Boquete", "hiking in Boquete"],
 "boquete-coffee-farm-tour":          ["coffee farm tour", "coffee farms"],
 "panama-city-to-boquete":            ["Panama City to Boquete", "David"],
 "things-to-do-el-valle-de-anton":    ["things to do in El Valle"],
}

# which destination each page belongs to, so links stay in-cluster unless the
# target is national/foundational
CLUSTER = {
 "bocas": ["bocas","zapatilla","red-frog","starfish","which-bocas"],
 "guna":  ["san-blas","guna"],
 "pearl": ["pearl"],
 "city":  ["panama-city","casco","amador","canal","miraflores","day-trips","charter"],
 "boquete":["boquete","baru","caldera","quetzal","lerida"],
 "elvalle":["el-valle","valle-de-anton","india-dormida","gaital","macho","nispero"],
}
NATIONAL = {"renting-a-car-in-panama","is-panama-safe","best-time-to-visit-panama",
            "panama-city","bocas-del-toro","boquete","el-valle-de-anton"}

# Targets whose anchor phrases are generic enough to fire anywhere ("island
# hopping", "water taxi", "coffee farms"). Linking those from another
# destination is a non-sequitur — a Pearl Islands page should not send "island
# hopping" to a Bocas guide — so they only fire inside their own cluster.
CLUSTER_ONLY = {"bocas-del-toro-island-hopping-guide": "bocas",
                "how-to-get-to-bocas-del-toro": "bocas",
                "boquete-coffee-farm-tour": "boquete",
                "which-bocas-del-toro-island-to-stay-on": "bocas",
                "red-frog-beach-bocas-del-toro": "bocas"}

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
        r'(?s)<section class="evb-cta.*?</section>',
        r'(?s)<div class="evb-cta".*?</div></div></div>',
        r'(?s)<script.*?</script>', r'(?s)<header.*?</header>',
        r'(?s)<footer.*?</footer>', r'(?s)<figure.*?</figure>',
        r'(?s)<nav class="breadcrumb".*?</nav>']

def protected_spans(s):
    spans = []
    for pat in SKIP:
        spans += [(m.start(), m.end()) for m in re.finditer(pat, s)]
    spans += [(m.start(), m.end()) for m in re.finditer(r"(?s)<a\b.*?</a>", s)]
    return spans

def in_span(i, spans):
    return any(a <= i < b for a, b in spans)

def paragraphs(s):
    """(start, end) of every prose <p> that is not inside a skipped region."""
    spans = protected_spans(s)
    out = []
    for m in re.finditer(r"(?s)<p>(.*?)</p>", s):
        if in_span(m.start(), spans):
            continue
        out.append((m.start(1), m.end(1)))
    return out

def link_page(path, targets, want_min, want_max, only=None):
    p = pathlib.Path(path)
    s = p.read_text(encoding="utf-8")
    slug = p.stem
    lang = "es" if "/es/" in p.as_posix() else "en"
    if lang != "en":
        return 0
    mine = cluster_of(slug)

    paras = paragraphs(s)
    if not paras:
        return 0
    prose = " ".join(s[a:b] for a, b in paras)
    already = set(re.findall(r'href="/articles/([^"#?]+)"', prose))

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
            if tslug in CLUSTER_ONLY and CLUSTER_ONLY[tslug] != mine:
                continue
            prio = 0 if (tc == mine or tslug in NATIONAL) else 1
            for ph in phrases:
                m = re.search(r"(?<![\w>])" + re.escape(ph) + r"(?![\w<])", chunk)
                if m:
                    cands.append((pi, a + m.start(), a + m.end(), ph, tslug, prio))
                    break

    # Spread: split the article into want_max bands and allow one link per band,
    # so they never bunch up in the intro or read as a list.
    chosen, used_p, used_t, used_b = [], set(), set(), set()
    band = max(1, len(paras) / float(max(want_max, 1)))
    for pi, st, en, ph, tslug, prio in sorted(cands, key=lambda c: (c[5], c[0], -len(c[3]))):
        b = int(pi // band)
        if pi in used_p or tslug in used_t or b in used_b:
            continue
        chosen.append((pi, st, en, ph, tslug))
        used_p.add(pi); used_t.add(tslug); used_b.add(b)
        if len(chosen) >= want_max:
            break
    if len(chosen) < want_min:                  # relax the banding to reach the floor
        for pi, st, en, ph, tslug, prio in sorted(cands, key=lambda c: (c[5], c[0], -len(c[3]))):
            if len(chosen) >= want_min:
                break
            if pi in used_p or tslug in used_t:
                continue
            chosen.append((pi, st, en, ph, tslug))
            used_p.add(pi); used_t.add(tslug)
        chosen.sort()

    for pi, st, en, ph, tslug in sorted(chosen, key=lambda c: -c[1]):
        s = s[:st] + f'<a href="/articles/{tslug}">{s[st:en]}</a>' + s[en:]
    if chosen:
        p.write_text(s, encoding="utf-8")
    return len(chosen)

FOCUS = ["best-time-to-visit-panama","boat-charter-panama","cayos-zapatillas-snorkelling-bocas-del-toro",
 "how-to-get-to-bocas-del-toro","red-frog-beach-bocas-del-toro","renting-a-car-in-panama",
 "starfish-beach-bocas-del-toro-playa-estrella-guide","which-bocas-del-toro-island-to-stay-on",
 "san-blas-islands-panama-guna-yala-guide","san-blas-sailing-panama-to-colombia",
 "pearl-islands-panama-guide","is-panama-safe"]

def main():
    recip = "--reciprocal" in sys.argv
    if not recip:
        print("forward links (the pages under review):")
        for slug in FOCUS:
            n = link_page(ROOT/"public"/"articles"/f"{slug}.html", TARGETS, 5, 8)
            print(f"  {slug:<52} +{n}")
    else:
        print("reciprocal links (older pages -> the pages under review):")
        only = set(FOCUS)
        for f in sorted(glob.glob("public/articles/*.html")):
            if pathlib.Path(f).stem in FOCUS:
                continue
            n = link_page(f, {k: v for k, v in TARGETS.items() if k in only}, 0, 2, only=only)
            if n:
                print(f"  {pathlib.Path(f).stem:<52} +{n}")

if __name__ == "__main__":
    main()
