#!/usr/bin/env python3
"""
boquete-image-descriptions.py — describe every photograph on the 2026-09 batch,
on the page and in the markup, so the images are indexable in their own right.

The El Valle batch got this treatment in 58f7083 / b0605f9; this is the same
thing for Boquete, driven by scripts/boquete-image-facts.json (written after
looking at all 52 files, so the words match the pixels).

Four things:

  1. alt=          the literal description of the frame. This is the
                   accessibility signal and the strongest image-search signal.
  2. <figcaption>  the same sentence, VISIBLE in grey under every body photo and
                   on every gallery tile. The site stylesheet ships
                   .art-inline-img figcaption as screen-reader-only, so until now
                   the description under each in-article photo reached screen
                   readers and nobody else.
  3. A "About these photographs" / "Sobre estas fotos" block at the foot of the
     page, replacing the old credits list: every image in document order with
     what it shows, where it was taken, who took it and under what licence —
     including our own photographs, which the credits block skipped because they
     need no attribution.
  4. Article JSON-LD ImageObjects gain contentLocation and keywords, which is the
     part that says what the picture is OF rather than who owns it.

Unlike the El Valle script this one needs no plan file: the keys are derived
from what each page actually renders, so adding or swapping a photo needs only
a new entry in the facts file.

Image sitemaps deliberately get nothing new: Google ignores every image-sitemap
tag except <image:loc>, so caption/title there would be a dead signal.

Run after enrich-images.py, before build-page-images.py:

    python3 scripts/boquete-image-descriptions.py

Idempotent: the block is wrapped in <!--IMGDESC-->…<!--/IMGDESC--> and rebuilt.
"""
import re, json, html, pathlib, sys
from urllib.parse import quote

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import wm_original

ROOT = pathlib.Path(__file__).resolve().parent.parent
FACTS = json.loads((ROOT / "scripts/boquete-image-facts.json").read_text(encoding="utf-8"))
VER = json.loads((ROOT / "scripts/commons-verified.json").read_text(encoding="utf-8"))
_tp = ROOT / "scripts/image-thirdparty.json"
LOCAL = json.loads(_tp.read_text(encoding="utf-8")) if _tp.exists() else {}
URL2TITLE = {m["url"]: t for t, m in VER.items()}
BASE = "https://panamaspot.com"

PAGES = {
 "public/articles/best-time-to-visit-boquete.html": "en",
 "public/articles/boquete-bike-rental.html": "en",
 "public/articles/boquete-cycling-routes.html": "en",
 "public/articles/boquete-hot-springs-caldera-vs-los-pozos.html": "en",
 "public/articles/panama-city-to-boquete.html": "en",
 "public/articles/quetzal-season-boquete-when-where-to-see-resplendent-quetzal.html": "en",
 "public/articles/where-to-stay-in-boquete.html": "en",
 "public/es/articles/boquete-con-ninos-guia-familiar.html": "es",
 "public/es/articles/cuanto-cuesta-boquete-presupuesto-semana.html": "es",
 "public/es/articles/el-volcan-baru-esta-activo.html": "es",
 "public/es/articles/feria-de-las-flores-y-del-cafe-boquete.html": "es",
 "public/es/articles/mi-jardin-es-su-jardin-boquete.html": "es",
 "public/articles/best-time-to-visit-panama.html": "en",
 "public/articles/boat-charter-panama.html": "en",
 "public/articles/cayos-zapatillas-snorkelling-bocas-del-toro.html": "en",
 "public/articles/how-to-get-to-bocas-del-toro.html": "en",
 "public/articles/is-panama-safe.html": "en",
 "public/articles/pearl-islands-panama-guide.html": "en",
 "public/articles/red-frog-beach-bocas-del-toro.html": "en",
 "public/articles/renting-a-car-in-panama.html": "en",
 "public/articles/san-blas-islands-panama-guna-yala-guide.html": "en",
 "public/articles/san-blas-sailing-panama-to-colombia.html": "en",
 "public/articles/starfish-beach-bocas-del-toro-playa-estrella-guide.html": "en",
 "public/articles/which-bocas-del-toro-island-to-stay-on.html": "en",
}

T = {
 "es": {"eyebrow": "Las fotos", "title": "Sobre estas fotos",
        "sub": "Qué muestra cada fotografía de esta página, dónde se tomó y quién la tomó. "
               "Toca el título para ver el archivo original.",
        "own": "Fotografía de PanamaSpot", "where": "Dónde"},
 "en": {"eyebrow": "The photographs", "title": "About these photographs",
        "sub": "What each photograph on this page shows, where it was taken and who took it. "
               "Tap a title to see the original file.",
        "own": "PanamaSpot photograph", "where": "Where"},
}

CSS = ('<style id="img-desc-css">'
 '.img-desc{padding:52px 24px;border-top:1px solid var(--border-light);background:var(--cream)}'
 '.img-desc-wrap{max-width:1040px;margin:0 auto}'
 '.img-desc .id-eyebrow{letter-spacing:.14em;text-transform:uppercase;color:var(--terra);'
 'font-size:11px;font-weight:600;font-family:var(--mono);display:block;margin-bottom:10px}'
 '.img-desc h2{font-family:var(--sans);color:var(--ink);font-size:23px;font-weight:600;'
 'letter-spacing:-.01em;margin:0 0 4px;line-height:1.15}'
 '.img-desc .id-sub{color:var(--ink-mute);font-size:14px;margin:0 0 24px;max-width:62ch}'
 '.img-desc ol{list-style:none;margin:0;padding:0;display:grid;gap:0}'
 '.img-desc li{padding:16px 0;border-top:1px solid var(--border-light)}'
 '.img-desc .id-t{font-weight:600;font-size:14.5px;color:var(--ink);display:block;margin-bottom:5px}'
 '.img-desc .id-t a{color:inherit;text-decoration:none}'
 '.img-desc .id-t a:hover{text-decoration:underline}'
 '.img-desc .id-d{margin:0;font-size:14px;line-height:1.55;color:var(--ink-soft);max-width:78ch}'
 '.img-desc .id-m{display:block;margin-top:6px;color:var(--ink-mute);font-family:var(--mono);'
 'font-size:11px;letter-spacing:.01em}'
 '.img-desc .id-m b{font-weight:500;color:var(--ink-soft)}'
 '@media(max-width:600px){.img-desc{padding:40px 20px}.img-desc h2{font-size:20px}}'
 # the site stylesheet hides the inline caption; `figure.art-inline-img` outscores
 # the bare class selector, so this wins wherever the <style> lands.
 'figure.art-inline-img figcaption{position:static;width:auto;height:auto;'
 'margin:12px 0 0;padding:0;overflow:visible;clip:auto;white-space:normal;'
 'color:var(--ink-mute);font-size:13px;line-height:1.5;max-width:68ch}'
 '.art-gallery-grid figcaption{z-index:2;background:linear-gradient(to top,'
 'rgba(0,0,0,.88) 0%,rgba(0,0,0,.72) 42%,rgba(0,0,0,.34) 74%,rgba(0,0,0,0) 100%);'
 'padding:34px 14px 11px;text-shadow:0 1px 3px rgba(0,0,0,.75);line-height:1.35}'
 '</style>')


def key_for(src):
    """A rendered <img src> back to its facts key."""
    u = src.replace("&amp;", "&")
    if "upload.wikimedia.org" in u:
        t = URL2TITLE.get(wm_original(u))
        return "File:" + t if t else None
    if "images.pexels.com" in u:
        return re.sub(r"[?&]w=\d+", "", u)
    u = u.replace(BASE, "")
    return u if u.startswith("/images/") else None


def txt(f, field, lang):
    return f.get(field + ("_en" if lang == "en" else ""), f[field])


def lic_url(lic):
    l = (lic or "").strip().lower()
    if l in ("cc0", "cc0 1.0"):
        return "https://creativecommons.org/publicdomain/zero/1.0/"
    if l.startswith("public domain"):
        return None
    m = re.match(r"cc by(-sa)?\s*([0-9]\.[0-9])", l)
    return f"https://creativecommons.org/licenses/by{m.group(1) or ''}/{m.group(2)}/" if m else None


def commons_page(key):
    return "https://commons.wikimedia.org/wiki/File:" + quote(key[5:].replace(" ", "_"))


def place_of(f):
    p = {"@type": "Place", "name": f["place"]}
    addr = {"@type": "PostalAddress", "addressCountry": "PA"}
    if f.get("locality"): addr["addressLocality"] = f["locality"]
    if f.get("region"):   addr["addressRegion"] = f["region"]
    p["address"] = addr
    return p


def caption_and_alt(s, lang):
    """Same sentence as alt and as the visible caption, on body figures and
    gallery tiles alike."""
    n = 0

    def fix(fm):
        nonlocal n
        fig = fm.group(0)
        src = re.search(r'<img[^>]*\bsrc="([^"]+)"', fig)
        if not src:
            return fig
        f = FACTS.get(key_for(src.group(1)) or "")
        if not f:
            return fig
        d = html.escape(txt(f, "desc", lang), quote=True)
        fig = re.sub(r'alt="[^"]*"', f'alt="{d}"', fig, count=1)
        if "<figcaption>" in fig:
            fig = re.sub(r'<figcaption>.*?</figcaption>', f'<figcaption>{d}</figcaption>', fig, flags=re.S)
        else:
            fig = fig[: fig.rfind("</figure>")] + f'<figcaption>{d}</figcaption></figure>'
        n += 1
        return fig

    s = re.sub(r'<figure[^>]*class="art-inline-img[^"]*"[^>]*>.*?</figure>', fix, s, flags=re.S)

    g = re.search(r'<div class="art-gallery-grid">', s)
    if g:
        start = g.end()
        end = s.find("</div></div></section>", start)
        if end == -1:
            end = s.find("</div></section>", start)
        if end != -1:
            seg = re.sub(r'<figure[^>]*>.*?</figure>', fix, s[start:end], flags=re.S)
            s = s[:start] + seg + s[end:]

    # the hero is not a <figure>; it still wants real alt text
    hm = re.search(r'(art-hero-img-full"><img[^>]*\bsrc=")([^"]+)(")', s)
    if hm:
        f = FACTS.get(key_for(hm.group(2)) or "")
        if f:
            d = html.escape(txt(f, "desc", lang), quote=True)
            head = s[:hm.end()]
            tail = s[hm.end():]
            close = tail.find(">")
            tag = re.sub(r'alt="[^"]*"', f'alt="{d}"', tail[:close], count=1)
            s = head + tag + tail[close:]
            n += 1
    return s, n


def desc_block(s, lang):
    main = re.search(r"(?s)<main\b.*?</main>", s)
    body = main.group(0) if main else s
    for pat in (r"(?s)<!--RELATED-MODULE-->.*?<!--/RELATED-MODULE-->",
                r"(?s)<!--IMGCREDITS-->.*?<!--/IMGCREDITS-->",
                r"(?s)<!--IMGDESC-->.*?<!--/IMGDESC-->",
                r'(?s)<aside class="evb-rail".*?</aside>'):
        body = re.sub(pat, "", body)

    t, seen, items = T[lang], set(), []
    for src in re.findall(r'<img[^>]*\bsrc="([^"]+)"', body):
        k = key_for(src)
        if not k or k in seen or k not in FACTS:
            continue
        seen.add(k)
        f = FACTS[k]
        lab = html.escape(txt(f, "label", lang), quote=True)
        dsc = html.escape(txt(f, "desc", lang), quote=True)
        if k.startswith("File:"):
            rec = VER[k[5:]]
            who = re.split(r"\s+from\s+", (rec.get("artist") or "").strip())[0].strip()
            lic, lu = rec.get("lic", ""), lic_url(rec.get("lic", ""))
            licpart = (f'<a href="{lu}" target="_blank" rel="noopener nofollow">{html.escape(lic)}</a>'
                       if lu else html.escape(lic))
            credit = f'{html.escape(who or "Wikimedia Commons")} · {licpart}'
            title = f'<a href="{commons_page(k)}" target="_blank" rel="noopener nofollow">{lab}</a>'
        elif k.startswith("http"):
            # stock: no location to state, and the licence needs no attribution
            m = re.search(r"/photos/(\d+)/", k)
            page = f"https://www.pexels.com/photo/{m.group(1)}/" if m else "https://www.pexels.com/license/"
            credit = ('Pexels · <a href="%s" target="_blank" rel="noopener nofollow">%s</a>'
                      % (page, "Licencia Pexels" if lang == "es" else "Pexels License"))
            title = lab
        elif k in LOCAL:
            credit = html.escape(LOCAL[k]["credit"]); title = lab
        else:
            credit = t["own"]; title = lab
        # a stock photograph has no place we can honestly state
        where = (f'<b>{t["where"]}:</b> {html.escape(f["place"])} · ' if f.get("place") else "")
        items.append(
          f'<li><span class="id-t">{title}</span><p class="id-d">{dsc}</p>'
          f'<span class="id-m">{where}{credit}</span></li>')

    if not items:
        return s, 0
    block = (f'<!--IMGDESC-->{CSS}<section class="img-desc"><div class="img-desc-wrap">'
             f'<span class="id-eyebrow">{t["eyebrow"]}</span><h2>{t["title"]}</h2>'
             f'<p class="id-sub">{t["sub"]}</p><ol>{"".join(items)}</ol>'
             f'</div></section><!--/IMGDESC-->')
    s = re.sub(r"(?s)<!--IMGCREDITS-->.*?<!--/IMGCREDITS-->", "", s)
    s = re.sub(r"(?s)<!--IMGDESC-->.*?<!--/IMGDESC-->", "", s)
    s = (s.replace("</main>", block + "</main>", 1) if "</main>" in s
         else s.replace("</body>", block + "</body>", 1))
    return s, len(items)


def schema_locations(s):
    def fix(block):
        try:
            d = json.loads(block)
        except json.JSONDecodeError:
            return block
        if d.get("@type") != "Article" or not isinstance(d.get("image"), list):
            return block
        touched = False
        for io in d["image"]:
            if not isinstance(io, dict):
                continue
            f = FACTS.get(key_for(io.get("contentUrl", "") or io.get("url", "")) or "")
            if not f:
                continue
            if not f.get("place"):
                continue
            io["contentLocation"] = place_of(f)
            kw = [f["place"]]
            if f.get("locality") and f["locality"] not in kw: kw.append(f["locality"])
            if f.get("region"): kw.append(f["region"])
            io["keywords"] = ", ".join(kw)
            touched = True
        return json.dumps(d, ensure_ascii=False) if touched else block

    return re.sub(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)',
                  lambda m: m.group(1) + fix(m.group(2)) + m.group(3), s, flags=re.S)


def main():
    tot_c = tot_d = 0
    for page, lang in PAGES.items():
        p = ROOT / page
        s = p.read_text(encoding="utf-8")
        s, nc = caption_and_alt(s, lang)
        s, nd = desc_block(s, lang)
        s = schema_locations(s)
        p.write_text(s, encoding="utf-8")
        print(f"  {page.split('/')[-1][:-5]:56s} captions {nc:2d} · described {nd:2d} · {lang}")
        tot_c += nc; tot_d += nd
    print(f"\n  {tot_c} captions/alts written, {tot_d} images described")


if __name__ == "__main__":
    main()
