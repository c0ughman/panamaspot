#!/usr/bin/env python3
"""
place-schema.py — attach a schema.org Place (TouristAttraction / TouristDestination)
to each article: geo coordinates, Panama address, and sameAs links to Wikipedia +
Wikidata (entity SEO — tells Google which real-world place the page is about).

Inputs:
  scripts/page-places.json   page -> place-key (curated)
  scripts/places-data.json   place-key -> {qid, names, lat, lng, type, region, wikipedia_*}
                             (built by the Wikidata sub-agent)

Per page it (idempotently):
  - injects a <!--PLACE-LD-->…<!--/PLACE-LD--> JSON-LD block with the Place node
    (@id = <canonical>#place), and
  - adds "about": {@id ref} to the Article JSON-LD so the two are linked.

    python3 scripts/place-schema.py
"""
import re, json, pathlib

ROOT   = pathlib.Path(__file__).resolve().parent.parent
PAGES  = json.loads((ROOT/"scripts"/"page-places.json").read_text())["pages"]
PLACES = json.loads((ROOT/"scripts"/"places-data.json").read_text())

def clean_name(n):
    return re.sub(r"\s*\(.*?\)", "", n or "").strip()

def canonical(s):
    m = re.search(r'<link href="([^"]+)" rel="canonical"/>', s) or re.search(r'<link rel="canonical" href="([^"]+)"', s)
    return m.group(1) if m else None

def meta_desc(s):
    m = re.search(r'<meta content="([^"]*)" name="description"/>', s)
    return m.group(1) if m else ""

def hero_src(s):
    m = re.search(r'art-hero-img-full">\s*<img[^>]*\bsrc="([^"]+)"', s)
    return m.group(1).replace("&amp;", "&") if m else None

def place_node(place, url, lang, desc, hero):
    name = clean_name(place["name_es"] if lang == "es" else place["name_en"]) or clean_name(place["name_en"])
    wp = place.get("wikipedia_es" if lang == "es" else "wikipedia_en") or place.get("wikipedia_en") or place.get("wikipedia_es")
    same = [x for x in (wp, f"https://www.wikidata.org/wiki/{place['qid']}") if x]
    node = {
        "@context": "https://schema.org", "@type": place["type"], "@id": url + "#place",
        "name": name, "description": desc,
        "geo": {"@type": "GeoCoordinates", "latitude": place["lat"], "longitude": place["lng"]},
        "address": {"@type": "PostalAddress", "addressCountry": "PA", "addressRegion": place["region"]},
        "sameAs": same, "containedInPlace": {"@type": "Country", "name": "Panama"}, "url": url,
    }
    if hero:
        node["image"] = hero
    return node

def process(page):
    key = PAGES.get(page)
    if not key or key not in PLACES:
        print(f"  – no place for {page}"); return
    place = PLACES[key]
    if not place.get("qid"):
        print(f"  – place {key} unresolved, skipping {page}"); return
    p = ROOT/page
    s = p.read_text(encoding="utf-8")
    lang = "es" if "/es/" in page else "en"
    url = canonical(s)
    if not url:
        print(f"  ! no canonical: {page}"); return
    node = place_node(place, url, lang, meta_desc(s), hero_src(s))
    block = ('<!--PLACE-LD--><script type="application/ld+json">'
             + json.dumps(node, ensure_ascii=False) + "</script><!--/PLACE-LD-->")

    # 1) inject/replace the Place block (right after the Article JSON-LD)
    s = re.sub(r"<!--PLACE-LD-->.*?<!--/PLACE-LD-->", "", s, flags=re.S)
    am = re.search(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "Article".*?</script>', s, re.S)
    if am:
        s = s[:am.end()] + block + s[am.end():]
    else:
        print(f"  ! no Article block: {page}"); return

    # 2) link the Article to the Place via "about" (idempotent add/replace)
    about = json.dumps({"@type": place["type"], "@id": url + "#place",
                        "name": clean_name(place["name_es"] if lang == "es" else place["name_en"]) or clean_name(place["name_en"])},
                       ensure_ascii=False)
    s = re.sub(r'("@type": "Article", )"about": \{[^}]*\}, ', r"\1", s)      # strip prior about
    s = re.sub(r'("@type": "Article", )', lambda m: m.group(1) + '"about": ' + about + ", ", s, count=1)

    p.write_text(s, encoding="utf-8")
    print(f"  ✓ {page}  → {place['type']} {place['qid']}")

def main():
    for page in PAGES:
        process(page)

if __name__ == "__main__":
    main()
