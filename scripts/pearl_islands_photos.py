"""Replace the generic stock photos on the Pearl Islands guide with real, geotagged photos from Wikimedia Commons (user's request, 2026-11-05).
Text of the article is untouched; photos, captions, credits, image schema and share image change.
  python3 scripts/pearl_islands_photos.py <download_dir>
"""
import html, json, re, subprocess, sys, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / "public"; OUT = P / "images/v2"; DL = Path(sys.argv[1]); DL.mkdir(parents=True, exist_ok=True)
PAGE = P / "articles/pearl-islands-panama-guide.html"; SITE = "https://panamaspot.com"
LIC = {"CC BY 2.0": "https://creativecommons.org/licenses/by/2.0/", "CC BY-SA 3.0": "https://creativecommons.org/licenses/by-sa/3.0/", "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/", "CC0": "https://creativecommons.org/publicdomain/zero/1.0/", "FAL": "https://artlibre.org/licence/lal/en/"}
C = "Contadora"
PH = {
 "hero": ("Playa_Blanca,_Saboga,_Panama_(Unsplash).jpg", 3654, 5480, "Rowan Heuvel", "CC0", "Playa Blanca, Isla Saboga", "Palm trees lean over the sand at Playa Blanca on Isla Saboga, in the Pearl Islands.", "playa-blanca-saboga"),
 "air": ("Contadora_Panama_(26456479012).jpg", 2643, 3526, "dronepicr", "CC BY 2.0", "Isla Contadora from the air", "Roads, houses and beaches on Isla Contadora, seen from the air.", "contadora-aerial"),
 "isle": ("Contadora_Perleninseln_(25945898883).jpg", 2139, 3809, "dronepicr", "CC BY 2.0", "Island in the Pearl Islands", "A low green island ringed by shallow water in the Pearl Islands, seen from the air.", "pearl-islands-aerial"),
 "wreck": ("Contadora_beach_wreck_(26641664812).jpg", 2176, 3874, "dronepicr", "CC BY 2.0", "Wreck on the beach, Contadora", "A wrecked white passenger boat lies stranded on a long sandy beach on Isla Contadora.", "contadora-beach-wreck"),
 "coral": ("Porites_lobata,_isla_Saboga.jpg", 2736, 3648, "Ryan McMinds", "CC BY 2.0", "Porites lobata coral, Isla Saboga", "Close-up of a lumpy Porites lobata coral on the reef at Isla Saboga.", "porites-lobata-saboga"),
 "saboga": ("Isla_de_Saboga_La_Mochila.jpg", 1832, 3264, "Fany McGhan and Laurie Batista", "CC BY-SA 3.0", "Shoreline, Isla Saboga", "A wave breaks on the shore of Isla Saboga behind the silhouette of a tree.", "isla-saboga-shore"),
 "road": ("Main_Boulevardmin_Contadora.jpg", 1536, 2048, "Aworld196", "CC BY-SA 4.0", "Main road, Contadora", "Shops and parked golf carts along the main road on Isla Contadora.", "contadora-main-road"),
 "beach": ("Contadora_beach_wreck_(26734778685).jpg", 2992, 3992, "dronepicr", "CC BY 2.0", "Long beach, Contadora", "A long curve of sand and green water on Isla Contadora, with the wrecked boat in the distance.", "contadora-long-beach"),
 "cove": ("Wyspa_Contadora,_Archipelag_Wysp_Perłowych,_Panama.jpg", 2112, 2816, "Katarzyna Sierocińska", "FAL", "Cove, Contadora", "A sandy cove below white houses on Isla Contadora.", "contadora-cove"),
 "strand": ("Strand_in_Contadora_(27117318015).jpg", 1871, 2495, "dronepicr", "CC BY 2.0", "Empty beach, Contadora", "A wide, empty beach at low tide on Isla Contadora.", "contadora-empty-beach"),
 "casaya": ("Playa_Casaya_La_Mochila.jpg", 1832, 3264, "Fany McGhan M. and Laurie Batista", "CC BY-SA 3.0", "Playa Casaya, Isla Casaya", "The pale strip of Playa Casaya on the horizon, seen from the sea off Isla Casaya.", "playa-casaya"),
 "pavona": ("Pavona_gigantea,_Panamá.jpg", 2585, 3447, "Ryan McMinds", "CC BY 2.0", "Pavona gigantea coral, Pearl Islands", "A rounded Pavona gigantea coral on a reef in the Pearl Islands.", "pavona-gigantea-pearl-islands"),
}
FIG = ["air", "isle", "wreck", "saboga"]   # replace the four stock figures, in order
GAL = ["beach", "cove", "strand", "casaya", "pavona"]
HERO_FOCUS = 62


def fetch(k):
    name = PH[k][0]; dest = DL / f"{k}.jpg"
    if dest.exists() and dest.stat().st_size > 1000: return dest
    q = "https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url&iiurlwidth=1920&titles=" + urllib.request.quote("File:" + name)
    ua = {"User-Agent": "PanamaSpotImageCopy/1.0 (https://panamaspot.com)"}
    info = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=ua), timeout=60))
    ii = next(iter(info["query"]["pages"].values()))["imageinfo"][0]
    for wait in (1.5, 8, 25):
        time.sleep(wait)
        try:
            dest.write_bytes(urllib.request.urlopen(urllib.request.Request(ii["thumburl"], headers=ua), timeout=90).read()); return dest
        except Exception as e: err = e
    raise SystemExit(f"{name}: {err}")


def mk(src, dst, *ops, q=76):
    subprocess.run(["magick", str(src) + "[0]", "-auto-orient", *ops, "-strip", "-quality", str(q), "-define", "webp:method=6", str(dst)], check=True)


def dims(f):
    return subprocess.run(["magick", "identify", "-format", "%w %h", str(f) + "[0]"], capture_output=True, text=True).stdout.split()


M = {k: fetch(k) for k in PH}
S = {k: PH[k][7] for k in PH}
for w in (960, 1280, 1920): mk(M["hero"], OUT / f"{S['hero']}-hero-{w}.webp", "-resize", f"{w}x>")
mk(M["hero"], OUT / f"{S['hero']}-tile.webp", "-resize", "900x900>")
mk(M["hero"], OUT / f"{S['hero']}-stamp.webp", "-resize", "360x450^", "-gravity", "center", "-extent", "360x450")
mk(M["hero"], OUT / f"{S['hero']}-card.webp", "-resize", "640x520^", "-gravity", "center", "-extent", "640x520")
for k in FIG + ["coral", "road"]: mk(M[k], OUT / f"{S[k]}-wide.webp", "-resize", "1280x720^", "-gravity", "center", "-extent", "1280x720")
for k in GAL: mk(M[k], OUT / f"{S[k]}-gallery.webp", "-resize", "1400x1400>")
w, h_ = map(int, dims(M["hero"]))
ch = int(w * 630 / 1200); top = max(0, min(h_ - ch, int(h_ * HERO_FOCUS / 100 - ch / 2)))
subprocess.run(["magick", str(M["hero"]) + "[0]", "-auto-orient", "-crop", f"{w}x{ch}+0+{top}", "+repage", "-resize", "1200x630!", "-strip", "-quality", "82", "-interlace", "Plane", str(P / "images/social/pearl-islands-panama-guide-share.jpg")], check=True)

h = PAGE.read_text()
E = lambda s: html.escape(s, quote=True)
U = lambda k, role: f"{SITE}/images/v2/{S[k]}-{role}.webp"
alt = lambda k: PH[k][6]
def fig(k, role="wide"):
    a, b = dims(OUT / f"{S[k]}-{role}.webp")
    return f'<figure class="fig"><img sizes="(max-width: 768px) 100vw, 768px" alt="{E(alt(k))}" loading="lazy" decoding="async" src="{U(k, role)}" width="{a}" height="{b}"/><figcaption>{html.escape(alt(k), quote=False)} <span class="cr">{html.escape(PH[k][3], quote=False)} · {PH[k][4]}</span></figcaption></figure>'
# figures
old = re.findall(r'<figure class="fig">.*?</figure>', h, re.S); assert len(old) == 4, len(old)
for o, k in zip(old, FIG): h = h.replace(o, fig(k), 1)
h = h.replace(fig("wreck"), fig("wreck") + "\n\n" + fig("coral"), 1)
m = re.search(r'<h2>Practicalities[^<]*</h2>\s*', h); assert m
h = h[:m.end()] + fig("road") + "\n\n" + h[m.end():]
# gallery
gal = ""
for k in GAL:
    a, b = dims(OUT / f"{S[k]}-gallery.webp")
    gal += f'<figure><img class="ph" sizes="(max-width: 900px) 50vw, 25vw" alt="{E(alt(k))}" loading="lazy" decoding="async" src="{U(k, "gallery")}" width="{a}" height="{b}"/><figcaption>{html.escape(alt(k), quote=False)}</figcaption></figure>'
h, c = re.subn(r'(<div class="gal">).*?(</div></section>)', lambda mm: mm[1] + gal + mm[2], h, count=1, flags=re.S); assert c == 1
# hero and preload
srcset = ", ".join(f"{U('hero', 'hero-' + str(w))} {dims(OUT / (S['hero'] + '-hero-' + str(w) + '.webp'))[0]}w" for w in (960, 1280, 1920))
a, b = dims(OUT / f"{S['hero']}-hero-1280.webp")
tag = f'<img fetchpriority="high" loading="eager" decoding="async" class="hero-img" srcset="{srcset}" sizes="100vw" alt="{E(alt("hero"))}" src="{U("hero", "hero-1280")}" width="{a}" height="{b}" style="object-position:center {HERO_FOCUS}%"/>'
h, c = re.subn(r'<img\b[^>]*class="hero-img"[^>]*>', lambda mm: tag, h, count=1); assert c == 1
h, c = re.subn(r'<link rel="preload" as="image"[^>]*>', lambda mm: f'<link rel="preload" as="image" href="{U("hero", "hero-1280")}" imagesrcset="{srcset}" imagesizes="100vw" fetchpriority="high"/>', h, count=1); assert c == 1
h = re.sub(r'<meta content="[^"]*" property="og:image:alt"/>', lambda mm: f'<meta content="{E(alt("hero"))}" property="og:image:alt"/>', h)
h = re.sub(r'<meta content="[^"]*" name="twitter:image:alt"/>', lambda mm: f'<meta content="{E(alt("hero"))}" name="twitter:image:alt"/>', h)
# credits
ALL = ["hero"] + FIG[:3] + ["coral", "saboga", "road"] + GAL
def li(k):
    n, _, _, art, lic, title, d, _ = PH[k]
    return (f'<li><div><span class="id-t"><a href="https://commons.wikimedia.org/wiki/File:{urllib.request.quote(n)}" target="_blank" rel="noopener nofollow">{html.escape(title, quote=False)}</a></span>'
            f'<p class="id-d">{html.escape(d, quote=False)}</p><span class="src-domain">{html.escape(art, quote=False)} · {lic}</span></div></li>')
h, c = re.subn(r'(<div class="refs img-refs">.*?<ul class="src-list">).*?(</ul>)', lambda mm: mm[1] + "".join(li(k) for k in ALL) + mm[2], h, count=1, flags=re.S); assert c == 1
# schema: the same photos, with their real licence and creator
def obj(k, role, first=False):
    n, _, _, art, lic, title, d, _ = PH[k]
    a, b = dims(OUT / f"{S[k]}-{role}.webp")
    return {"@type": "ImageObject", "contentUrl": U(k, role), "url": U(k, role), "width": int(a), "height": int(b), "caption": d, "license": LIC[lic], "acquireLicensePage": "https://commons.wikimedia.org/wiki/File:" + urllib.request.quote(n), "creator": {"@type": "Person", "name": art}, "creditText": f"{art} / {lic}", "name": title, "description": d, "representativeOfPage": first}
imgs = [obj("hero", "hero-1920", True)] + [obj(k, "wide") for k in FIG[:3] + ["coral", "saboga", "road"]] + [obj(k, "gallery") for k in GAL]
def ld(mm):
    d = json.loads(mm[1])
    if d.get("@type") == "Article": d["image"] = imgs
    if d.get("@type") == "WebPage" and "primaryImageOfPage" in d: d["primaryImageOfPage"]["url"] = U("hero", "hero-1920")
    if d.get("@type") == "TouristDestination" and d.get("image"): d["image"] = U("hero", "hero-1920")
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"
h = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, h, flags=re.S)
PAGE.write_text(h)
# cards on other guides that point at this page
n = 0
for f in sorted(P.glob("articles/*.html")) + sorted(P.glob("es/articles/*.html")):
    t = f.read_text(errors="ignore"); t0 = t
    def card(mm):
        role = "tile" if mm[1].startswith("bt") else "card" if mm[1] == "fc" else "stamp"
        return re.sub(r'src="[^"]+"( width="\d+" height="\d+")?', f'src="{U("hero", role)}"', mm[0], count=1)
    t = re.sub(r'<a class="(sf|bt[^"]*|fc)" href="/articles/pearl-islands-panama-guide">.{0,240}?src="[^"]+"(?: width="\d+" height="\d+")?', card, t, flags=re.S)
    if t != t0: f.write_text(t); n += 1
ts = ROOT / "src/app/page-images.ts"; s = ts.read_text()
urls = [U("hero", "hero-1280")] + [U(k, "wide") for k in FIG[:3] + ["coral", "saboga", "road"]] + [U(k, "gallery") for k in GAL]
s, c = re.subn(r'  "/articles/pearl-islands-panama-guide": \[\n.*?\n  \],\n', lambda mm: '  "/articles/pearl-islands-panama-guide": [\n' + "".join(f'    "{u}",\n' for u in urls) + "  ],\n", s, flags=re.S); assert c == 1
ts.write_text(s)
print(f"{len(ALL)} real photos on the page; cards updated on {n} other guides")
