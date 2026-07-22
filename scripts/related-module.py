#!/usr/bin/env python3
"""
related-module.py — on the NEW guide pages, replace the "More to see / Across
the region" bento with a 3-card "Related guides" showcase. Each card reuses the
existing bento styling (b1 = image-top+body, b3 = image+overlay, b5 = split
image+body) but is now a LINK to a topically related article, showing that
article's hero image + (shortened) title + dek. This kills the image/text
mismatch for good and adds 3 internal links per page.

Relatedness = same region cluster + same language (falls back to same-language
sibling guides to always fill 3). Only the new (image-selections) pages are
rewritten; the original hikes/tours cluster keeps its hand-authored bento.

Idempotent: re-running rebuilds the same module. Run after restore-bento /
image pipeline, before committing.
    python3 scripts/related-module.py
"""
import re, json, glob, html, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import img_cap as ic

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEL = json.loads((ROOT/"scripts"/"image-selections.json").read_text())["selections"]

NEW = set()
for c in SEL.values():
    NEW.update(c["pages"])

ALL = sorted(glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html"))

CN = {"boquete": ("Boquete", "Boquete"), "elvalle": ("El Valle", "El Valle"),
      "panamacity": ("Panama City", "Ciudad de Panamá"), "bocas": ("Bocas del Toro", "Bocas del Toro"),
      "coiba": ("Coiba", "Coiba"), "guna": ("Guna Yala", "Guna Yala"), "other": ("Panama", "Panamá")}
HUB = ("things-to-do", "que-hacer", "hikes", "senderos", "tours", "travel-guide",
       "guia-completa", "itinerario", "island-hopping")

def cluster(name):
    n = name.lower()
    if any(k in n for k in ("boquete", "volcan-baru", "caldera", "lerida", "chiriqui")): return "boquete"
    if "el-valle" in n or "valle-de-anton" in n: return "elvalle"
    if any(k in n for k in ("casco-viejo", "panama-city", "ciudad-de-panama", "amador",
                            "canal", "cinta-costera", "day-trip")): return "panamacity"
    if "bocas" in n: return "bocas"
    if "coiba" in n: return "coiba"
    if "san-blas" in n or "guna-yala" in n: return "guna"
    return "other"

def rel_url(path):
    p = path.replace("public", "", 1)
    return re.sub(r"\.html$", "", p)

def short_title(t, n=52):
    t = re.sub(r"\s+", " ", t).strip()
    if ":" in t and len(t) > n:
        t = t.split(":")[0].strip()
    if len(t) > n:
        t = t[:n].rsplit(" ", 1)[0] + "…"
    return t

def short_dek(d, n=96):
    d = re.sub(r"\s+", " ", d).strip()
    return (d[:n].rsplit(" ", 1)[0] + "…") if len(d) > n else d

def card_hero(og):
    if "images.pexels.com" in og:
        return re.sub(r"([?&]w=)\d+", r"\g<1>700", og), ic.capped_dims(re.sub(r"([?&]w=)\d+", r"\g<1>1600", og), 700)
    orig = ic.wm_original(og)
    return ic.cap(orig, 500), ic.capped_dims(orig, 500)

def meta(path):
    s = pathlib.Path(path).read_text()
    lang = "es" if "/es/" in path else "en"
    og = re.search(r'<meta content="([^"]+)" property="og:image"/>', s).group(1)
    h1 = re.search(r'<h1 class="art-title">(.*?)</h1>', s, re.S)
    dek = re.search(r'<p class="art-dek">(.*?)</p>', s, re.S)
    title = re.sub(r"<[^>]+>", "", h1.group(1)) if h1 else ""
    dektxt = re.sub(r"<[^>]+>", "", dek.group(1)) if dek else ""
    return {"path": path, "url": rel_url(path), "lang": lang, "cluster": cluster(pathlib.Path(path).name),
            "hero": og, "title": html.unescape(title), "dek": html.unescape(dektxt)}

META = {p: meta(p) for p in ALL}

def related_for(path):
    me = META[path]
    same = [m for m in META.values() if m["lang"] == me["lang"] and m["path"] != path]
    def score(m):
        s = 0
        if m["cluster"] == me["cluster"]: s += 10
        if any(k in pathlib.Path(m["path"]).name for k in HUB): s += 2
        return -s  # ascending sort → higher score first
    same.sort(key=lambda m: (score(m), m["path"]))
    return same[:3]

def card(m, cls, lang, with_dek):
    hero, dims = card_hero(m["hero"])
    src = hero.replace("&", "&amp;")
    wh = f' width="{dims[0]}" height="{dims[1]}"' if dims else ""
    title = html.escape(short_title(m["title"]))
    tag = html.escape(CN[m["cluster"]][1 if lang == "es" else 0])
    alt = html.escape(m["title"])
    img = (f'<div class="imgph photo"><img src="{src}" alt="{alt}" loading="lazy"{wh} '
           f'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block"></div>')
    dek = f'<p>{html.escape(short_dek(m["dek"]))}</p>' if with_dek else ""
    if cls == "b1":
        return (f'<a class="bento-card b1" href="{m["url"]}"><div class="bento-img-top">{img}</div>'
                f'<div class="bento-body"><span class="b-tag">{tag}</span><h3>{title}</h3>{dek}</div></a>')
    if cls == "b3":
        return (f'<a class="bento-card b3" href="{m["url"]}">{img}'
                f'<div class="bento-overlay"><span class="b-tag">{tag}</span><h3>{title}</h3></div></a>')
    return (f'<a class="bento-card b5" href="{m["url"]}"><div class="bento-split-img">{img}</div>'
            f'<div class="bento-split-body"><span class="b-tag">{tag}</span><h3>{title}</h3>{dek}</div></a>')

def build_section(path):
    lang = META[path]["lang"]
    rel = related_for(path)
    if len(rel) < 3:
        return None
    eyebrow = "Sigue explorando" if lang == "es" else "Keep exploring"
    heading = "Guías relacionadas" if lang == "es" else "Related guides"
    cards = card(rel[0], "b1", lang, True) + card(rel[1], "b3", lang, False) + card(rel[2], "b5", lang, True)
    return (f'<section class="art-section"><div class="container"><div class="art-section-head">'
            f'<span class="eyebrow">{eyebrow}</span><h2>{heading}</h2></div>'
            f'<div class="home-bento-grid">{cards}</div></div></section>')

def process(path):
    s = pathlib.Path(path).read_text()
    new_sec = build_section(path)
    if not new_sec:
        print(f"  ! <3 related: {path}"); return
    wrapped = "<!--RELATED-MODULE-->" + new_sec + "<!--/RELATED-MODULE-->"
    rm = re.search(r"<!--RELATED-MODULE-->.*?<!--/RELATED-MODULE-->", s, re.S)
    if rm:                                   # re-run: replace the existing module
        s = s[:rm.start()] + wrapped + s[rm.end():]
    else:                                    # first run: replace the old bento section
        m = re.search(r'<div class="home-bento-grid">', s)
        if not m:
            print(f"  – no bento: {path}"); return
        sec_start = s.rfind("<section", 0, m.start())
        sec_end = s.find("</section>", m.start()) + len("</section>")
        s = s[:sec_start] + wrapped + s[sec_end:]
    pathlib.Path(path).write_text(s)
    r = related_for(path)
    print(f"  ✓ {pathlib.Path(path).name}  → {[pathlib.Path(x['path']).name[:20] for x in r]}")

def main():
    for p in sorted(NEW):
        process(p)

if __name__ == "__main__":
    main()
