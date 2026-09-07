#!/usr/bin/env python3
"""
place-verified-images.py — put photos of the ACTUAL place on the island,
beach and road pages.

Stock photos were captioned to name places they may not show. Every image
below is a Wikimedia Commons file found either by GEOSEARCH (Commons returns
only files geotagged within a radius of the real coordinates) or by a title
that names the place outright — so "is this really Red Frog Beach?" has an
answer that is checkable rather than assumed.

Placement is by section index. `hero` replaces the lead image and the og /
twitter / preload URLs with it. `slots` REPLACE the inline figure sitting in
that section; `add` inserts a new one where none exists.

All files are CC BY / CC BY-SA / PD — run image-credits.py afterwards so the
BY and BY-SA ones get their required attribution.

    python3 scripts/place-verified-images.py
"""
import re, sys, json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from img_cap import img_html, HERO, GALLERY as GW

SIZES_INLINE = "(max-width: 768px) 100vw, 768px"
META = json.loads((ROOT / "scripts" / "commons-verified.json").read_text(encoding="utf-8"))

def url(title):
    return META[title]["url"]

# page -> {hero: title|None, place: [(section_index, title, caption), …]}
PLAN = {
"public/articles/renting-a-car-in-panama.html": {
 "hero": "Corredor Sur Panama.jpg",
 "place": [
  (0, "Vía Israel y Corredor Sur en Ciudad de Panamá.jpg",
      "Vía Israel meeting the Corredor Sur in Panama City"),
  (4, "Carretera Interamericana en Penonomé, Provincia de Coclé, Panamá (2024).jpg",
      "The Interamericana at Penonomé, Coclé province"),
  (5, "Interamericana Santa Marta.jpg", "The Interamericana highway, Panama"),
  (6, "Puente de las Americas 2013 09 14.jpg",
      "The Bridge of the Americas carries the Interamericana over the canal"),
  (8, "Entrada al Darién en la Carretera Interamericana, Panamá (2020).jpg",
      "Where the Interamericana runs out at the edge of the Darién"),
]},
"public/articles/red-frog-beach-bocas-del-toro.html": {
 "hero": "Red Frog Beach Bastimentos 8.jpg",
 "place": [
  (0, "Red Frog Beach Bastimentos.jpg", "Red Frog Beach, Isla Bastimentos"),
  (3, "Red Frog Beach Bastimentos 3.jpg", "The surf at Red Frog Beach, Isla Bastimentos"),
  (4, "Oophaga pumilio 120574497.jpg",
      "Oophaga pumilio, the strawberry poison-dart frog the beach is named for"),
  (6, "Red Frog Beach Bastimentos 6.jpg", "Red Frog Beach inside the Bastimentos marine park"),
  (7, "Bastimentos Wizzard Beach (26708686196).jpg", "Wizard Beach, the next bay along on Bastimentos"),
]},
"public/articles/starfish-beach-bocas-del-toro-playa-estrella-guide.html": {
 "hero": "Women at Starfish Beach, Boca del Drago.jpg",
 "place": [
  (0, "Starfish Beach 04036.jpg", "Playa Estrella at Boca del Drago, Isla Colón"),
  (2, "Paradise - Bocas del drago (6778445008).jpg", "The shallows at Boca del Drago, Isla Colón"),
  (4, "Bocas del Drago.jpg", "Boca del Drago on the north-west tip of Isla Colón"),
]},
"public/articles/which-bocas-del-toro-island-to-stay-on.html": {
 "hero": None,
 "place": [
  (0, "Bocas del Toro Province, Panama - panoramio (16).jpg", "The Bocas del Toro archipelago, Panama"),
  (3, "Red Frog Beach Bastimentos 8.jpg", "Red Frog Beach on Isla Bastimentos"),
  (4, "Bocas del Toro Province, Panama - panoramio (14).jpg", "Waterfront in Bocas del Toro province"),
]},
"public/articles/how-to-get-to-bocas-del-toro.html": {
 "hero": None,
 "place": [
  (1, "Bocas del Toro Province, Panama - panoramio (14).jpg",
      "The Bocas del Toro waterfront — water taxis are the last leg of every route"),
  (5, "Bocas del Drago.jpg", "Boca del Drago, Isla Colón"),
]},
"public/articles/san-blas-islands-panama-guna-yala-guide.html": {
 "hero": "Guna Yala Island.jpg",
 "place": [
  (0, "Isla Perro en la Comarca Guna Yala.JPG", "Isla Perro, Comarca de Guna Yala"),
  (2, "Cabañas Guna Yala.jpg", "Guna-run cabañas, Comarca de Guna Yala"),
  (4, "Banco de Arena - San Blas - Guna Yala.jpg", "A sandbank in the San Blas islands, Guna Yala"),
  (6, "Snorkelling in Guna Yala - Panama - panoramio.jpg", "Snorkelling in Guna Yala, Panama"),
]},
"public/articles/san-blas-sailing-panama-to-colombia.html": {
 "hero": "Island of Chichimen, Cuyos Limones, Guna Yala, Panama.jpg",
 "place": [
  (0, "Shipwreck near Chichimen Island, Cuyos Limones, Guna Yala, Panama.jpg",
      "A wreck off Chichimen island, Cayos Limones, Guna Yala"),
  (3, "Banco de Arena - San Blas - Guna Yala.jpg", "A San Blas sandbank, Guna Yala"),
  (5, "Isla Perro en la Comarca Guna Yala.JPG", "Isla Perro, a standard anchorage in Guna Yala"),
]},
"public/articles/pearl-islands-panama-guide.html": {
 "hero": "Strand in Contadora (27117318015).jpg",
 "place": [
  (0, "Wyspa Contadora, Archipelag Wysp Perłowych, Panama.jpg",
      "Contadora, Archipiélago de las Perlas"),
]},
}

def figure(title, caption):
    alt = html.escape(caption)
    return (f'<figure class="art-inline-img" data-inlined="1" data-verified="1">'
            f'<div class="imgph photo">{img_html(url(title), alt, GW, SIZES_INLINE)}</div>'
            f'<figcaption>{alt}</figcaption></figure>')

def set_hero(s, title):
    alt = re.search(r'art-hero-img-full"><img[^>]*alt="([^"]*)"', s).group(1)
    s = re.sub(r'(art-hero-img-full">)<img[^>]*>',
               lambda m: m.group(1) + img_html(url(title), alt, HERO, "100vw", eager=True), s, count=1)
    big = re.search(r'art-hero-img-full"><img src="([^"]+)"', s).group(1)
    for pat in (r'(<meta content=")[^"]*(" property="og:image"/>)',
                r'(<meta content=")[^"]*(" name="twitter:image"/>)'):
        s = re.sub(pat, lambda m: m.group(1) + big + m.group(2), s, count=1)
    s = re.sub(r'(<link rel="preload" as="image" href=")[^"]*"[^>]*/>',
               lambda m: m.group(1) + big + '" fetchpriority="high"/>', s, count=1)
    return s

def main():
    for page, plan in PLAN.items():
        p = ROOT / page
        s = orig = p.read_text(encoding="utf-8")
        if plan["hero"]:
            s = set_hero(s, plan["hero"])

        hs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>.*?</h2>', s))
        # figures already sitting in each section, so a slot REPLACES rather than stacks
        existing = {}
        for m in re.finditer(r'<figure class="art-inline-img"[^>]*>.*?</figure>', s, re.S):
            si = sum(1 for h in hs if h.start() < m.start()) - 1
            existing.setdefault(si, []).append(m.group(0))

        ins = []
        for si, title, cap in plan["place"]:
            if si >= len(hs):
                print(f"  ! {page}: no section {si}"); continue
            if existing.get(si):
                s = s.replace(existing[si].pop(0), figure(title, cap), 1)
            else:
                start = hs[si].end()
                nxt = hs[si + 1].start() if si + 1 < len(hs) else len(s)
                pm = re.search(r"</p>", s[start:nxt])
                ins.append((start + pm.end() if pm else start, title, cap))
        for off, title, cap in sorted(ins, reverse=True):
            s = s[:off] + figure(title, cap) + s[off:]

        if s != orig:
            p.write_text(s, encoding="utf-8")
            print(f"  ✓ {page.replace('public/','')}  hero={'set' if plan['hero'] else '—'}  "
                  f"verified images={len(plan['place'])}")

if __name__ == "__main__":
    main()
