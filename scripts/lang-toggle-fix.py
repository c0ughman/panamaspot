#!/usr/bin/env python3
"""lang-toggle-fix.py — make the header EN/ES switch land somewhere useful.

Two faults, both inherited from whichever article each page was generated from:

  1. One page points at a URL that does not exist (a 404 for real users).
  2. 22 pages have no translation, so their switch drops you on the bare
     homepage. Sending a reader to the matching destination hub in the other
     language keeps them in context and adds a real internal link.

Pages with a genuine translation pair keep pointing at their sibling.
Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# true EN <-> ES translation pairs
PAIRS = {
 "articles/hikes-in-boquete": "es/articles/senderos-en-boquete-guia-completa",
 "articles/things-to-do-in-boquete-panama": "es/articles/que-hacer-en-boquete-guia-completa",
 "articles/tours-in-boquete-panama": "es/articles/tours-en-boquete-panama",
 "articles/hikes-el-valle-de-anton": "es/articles/senderos-el-valle-de-anton",
 "articles/things-to-do-el-valle-de-anton": "es/articles/que-hacer-el-valle-de-anton",
 "articles/tours-en-el-valle-de-anton": "es/articles/tours-el-valle-de-anton",
 "articles/caldera-hot-springs-boquete": "es/articles/aguas-termales-caldera-boquete",
 "articles/chorro-el-macho-waterfall-el-valle-de-anton": "es/articles/cascada-chorro-el-macho-el-valle-de-anton",
 "articles/el-valle-day-trip-from-panama-city": "es/articles/el-valle-de-anton-desde-ciudad-de-panama",
 "articles/india-dormida-hike-el-valle-de-anton": "es/articles/sendero-india-dormida-el-valle-de-anton",
 "articles/volcan-baru-hike-sunrise-summit-guide": "es/articles/volcan-baru-como-subir-cima-panama",
 "articles/boquete-travel-guide": "es/articles/boquete-panama-guia-completa-itinerario",
 "articles/el-valle-de-anton-with-kids": "es/articles/zoologico-el-nispero-el-valle-de-anton",
 "articles/el-valle-de-anton": "es/articles/el-valle-de-anton",
 "articles/boquete": "es/articles/boquete",
 "articles/panama-city": "es/articles/panama-city",
}

# no sibling — send them to the cluster hub in the other language instead of "/"
HUB_BY_CLUSTER = {
    "elvalle": ("articles/el-valle-de-anton", "es/articles/el-valle-de-anton"),
    "boquete": ("articles/boquete", "es/articles/boquete"),
    "pty":     ("articles/panama-city", "es/articles/panama-city"),
    # No Bocas hub yet (one English article, see the roadmap). Until the cluster
    # is written, each side points at the nearest same-cluster page.
    "bocas":   ("articles/bocas-del-toro",
                "es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama"),
}

def cluster_of(slug):
    s = slug.lower()
    if any(k in s for k in ("el-valle", "valle-de-anton", "chorro", "india-dormida",
                            "nispero", "canopy", "gaital")):
        return "elvalle"
    if any(k in s for k in ("boquete", "caldera", "baru", "lerida", "quetzal",
                            "chiriqui", "rafting")):
        return "boquete"
    if any(k in s for k in ("panama-city", "ciudad-de-panama", "casco-viejo",
                            "cinta-costera", "amador", "canal", "miraflores", "day-trips")):
        return "pty"
    if "bocas" in s:
        return "bocas"
    return None


def target_for(rel):
    """Where should this page's other-language switch point?"""
    other = None
    if rel.startswith("es/"):
        for en, es in PAIRS.items():
            if es == rel:
                other = en; break
    else:
        other = PAIRS.get(rel)
    if other:
        return "/" + other
    c = cluster_of(rel.split("/")[-1])
    if c:
        en_hub, es_hub = HUB_BY_CLUSTER[c]
        return "/" + (en_hub if rel.startswith("es/") else es_hub)
    return "/" if rel.startswith("es/") else "/es"   # genuine fallback


def patch(p):
    rel = str(p.relative_to(ROOT / "public")).replace(".html", "")
    h = p.read_text(encoding="utf8")
    if "<header" not in h:
        return 0
    a, b = h.index("<header"), h.index("</header>") + len("</header>")
    head = h[a:b]
    is_es = rel.startswith("es/")
    self_url = "/" + rel
    other_url = target_for(rel)
    en_url = self_url if not is_es else other_url
    es_url = other_url if not is_es else self_url

    def rewrite(tag):
        hl = re.search(r'hreflang="(\w+)"', tag)
        if not hl:
            return tag
        want = en_url if hl.group(1) == "en" else es_url
        return re.sub(r'(href=")[^"]*(")', lambda m: m.group(1) + want + m.group(2), tag)

    new_head = re.sub(r'<a[^>]*class="[^"]*lang-opt[^"]*"[^>]*>', lambda m: rewrite(m.group(0)), head)
    if new_head == head:
        return 0
    p.write_text(h[:a] + new_head + h[b:], encoding="utf8")
    return 1


def main():
    files = sorted((ROOT / "public").rglob("*.html"))
    n = sum(patch(p) for p in files if "/funnels/" not in str(p))
    print(f"  repointed language toggles on {n} pages")

if __name__ == "__main__":
    main()
