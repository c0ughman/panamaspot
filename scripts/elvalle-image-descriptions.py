#!/usr/bin/env python3
"""
elvalle-image-descriptions.py — describe every photograph on the El Valle batch,
on the page and in the markup, so the images are indexable in their own right.

Three things, from scripts/elvalle-image-facts.json (written after viewing every
file, so the words match the pixels):

  1. GALLERY TILES get a <figcaption> carrying the short subject·place label.
     The inline figures already carry the long descriptive caption; using the
     short form here means the text nearest each image is different in the two
     places it appears rather than duplicated.

  2. A "Sobre estas fotos" / "About these photographs" block replaces the old
     credits list at the foot of the page. Every image on the page is listed in
     document order with what it shows, where it was taken, who took it and
     under what licence — including the site's own photographs, which the
     credits block skipped because they need no attribution.

  3. Article JSON-LD ImageObjects gain contentLocation (the place the photograph
     actually shows, with its postal address) and keywords. caption, name,
     description, creator, license and acquireLicensePage are already set by
     enrich-images.py; this adds the location, which is the part that tells
     Google what the picture is OF rather than who owns it.

Note on image sitemaps: <image:caption> and <image:title> are deliberately NOT
added. Google announced in 2022 that it ignores every image-sitemap tag except
<image:loc>, so they would be effort spent on a dead signal. The on-page caption,
the alt text and the ImageObject are the live ones.

Run after enrich-images.py and image-credits.py, before build-page-images.py:

    python3 scripts/elvalle-image-descriptions.py

Idempotent: the block is wrapped in <!--IMGDESC-->…<!--/IMGDESC--> and rebuilt.
"""
import re, json, html, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import wm_original

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "scripts/elvalle-image-plan.json").read_text(encoding="utf-8"))
FACTS = json.loads((ROOT / "scripts/elvalle-image-facts.json").read_text(encoding="utf-8"))
VER = json.loads((ROOT / "scripts/commons-verified.json").read_text(encoding="utf-8"))
ARTIST = json.loads((ROOT / "scripts/image-artists.json").read_text(encoding="utf-8"))

BASE = "https://panamaspot.com"

T = {
 "es": {"eyebrow": "Las fotos", "title": "Sobre estas fotos",
        "sub": "Qué muestra cada fotografía de esta página, dónde se tomó y quién la tomó. "
               "Toca el título para ver el archivo original.",
        "own": "Fotografía de PanamaSpot", "where": "Dónde", "lic": "Licencia"},
 "en": {"eyebrow": "The photographs", "title": "About these photographs",
        "sub": "What each photograph on this page shows, where it was taken and who took it. "
               "Tap a title to see the original file.",
        "own": "PanamaSpot photograph", "where": "Where", "lic": "Licence"},
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
 # The batch CSS gradient tops out at 72% black, which loses white text on the
 # bright tiles (market roofs, pineapple crates). Deepen it and add a shadow.
 '.art-gallery-grid figcaption{z-index:2;background:linear-gradient(to top,'
 'rgba(0,0,0,.88) 0%,rgba(0,0,0,.72) 42%,rgba(0,0,0,.34) 74%,rgba(0,0,0,0) 100%);'
 'padding:34px 14px 11px;text-shadow:0 1px 3px rgba(0,0,0,.75);line-height:1.35}'
 '</style>')


# ─────────────────────────────────────────────────────────── key resolution
def plan_index():
    """rendered-url -> plan key, so a page's <img> can be matched to its facts."""
    idx = {}
    for page, spec in PLAN.items():
        if page.startswith("_"):
            continue
        for k, *_ in [spec["hero"]] + list(spec["sections"].values()):
            if k.startswith("File:"):
                idx[VER[k[5:]]["url"]] = k
            else:
                idx[k] = k
    return idx

PIDX = plan_index()

def key_for(src):
    u = src.replace("&amp;", "&")
    if "upload.wikimedia.org" in u:
        return PIDX.get(wm_original(u))
    if "images.pexels.com" in u:
        bare = re.sub(r"[?&]w=\d+", "", u)
        for k in PIDX:
            if k.startswith("http") and re.sub(r"[?&]w=\d+", "", k) == bare:
                return k
        return None
    return PIDX.get(u.replace(BASE, ""))

def lic_url(lic):
    l = (lic or "").strip().lower()
    if l in ("cc0", "cc0 1.0"):
        return "https://creativecommons.org/publicdomain/zero/1.0/"
    m = re.match(r"cc by(-sa)?\s*([0-9]\.[0-9])", l)
    return f"https://creativecommons.org/licenses/by{m.group(1) or ''}/{m.group(2)}/" if m else None

def commons_page(key):
    from urllib.parse import quote
    return "https://commons.wikimedia.org/wiki/File:" + quote(key[5:].replace(" ", "_"))

def pexels_page(key):
    m = re.search(r"/photos/(\d+)/", key)
    return f"https://www.pexels.com/photo/{m.group(1)}/" if m else "https://www.pexels.com/license/"

def place_of(f):
    p = {"@type": "Place", "name": f["place"]}
    addr = {"@type": "PostalAddress", "addressCountry": f.get("country", "PA")}
    if f.get("locality"): addr["addressLocality"] = f["locality"]
    if f.get("region"):   addr["addressRegion"] = f["region"]
    p["address"] = addr
    return p


# ─────────────────────────────────────────────────────────────── page edits
def gallery_captions(s, lang):
    """One <figcaption> per gallery tile, carrying the short label."""
    m = re.search(r'<div class="art-gallery-grid">', s)
    if not m:
        return s, 0
    start = m.end()
    end = s.find("</div></section>", start)
    if end == -1:
        end = s.find("</div></div></section>", start)
    if end == -1:
        return s, 0
    seg, n = s[start:end], 0

    def fix(fm):
        nonlocal n
        fig = fm.group(0)
        src = re.search(r'<img[^>]*\bsrc="([^"]+)"', fig)
        if not src:
            return fig
        k = key_for(src.group(1))
        f = FACTS.get(k) if k else None
        if not f:
            return fig
        lab = f.get("label_en" if lang == "en" else "label", f["label"])
        cap = f'<figcaption>{html.escape(lab, quote=True)}</figcaption>'
        fig = re.sub(r'<figcaption>.*?</figcaption>', '', fig, flags=re.S)
        n += 1
        return fig[: fig.rfind("</figure>")] + cap + "</figure>"

    seg = re.sub(r'<figure[^>]*>.*?</figure>', fix, seg, flags=re.S)
    return s[:start] + seg + s[end:], n


def desc_block(s, lang):
    """Every image on the page, in document order, described and credited."""
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
        if not k or k in seen:
            continue
        f = FACTS.get(k)
        if not f:
            continue
        seen.add(k)
        lab = html.escape(f.get("label_en" if lang == "en" else "label", f["label"]), quote=True)
        dsc = html.escape(f.get("desc_en" if lang == "en" else "desc", f["desc"]), quote=True)
        if k.startswith("File:"):
            rec = VER[k[5:]]
            who = re.split(r"\s+from\s+", (rec.get("artist") or ARTIST.get(rec["url"], "") or "").strip())[0].strip()
            lic, lu = rec.get("lic", ""), lic_url(rec.get("lic", ""))
            licpart = f'<a href="{lu}" target="_blank" rel="noopener nofollow">{html.escape(lic)}</a>' if lu else html.escape(lic)
            credit = f'{html.escape(who or "Wikimedia Commons")} · {licpart}'
            title = f'<a href="{commons_page(k)}" target="_blank" rel="noopener nofollow">{lab}</a>'
        elif k.startswith("http"):
            credit = f'Pexels · <a href="{pexels_page(k)}" target="_blank" rel="noopener nofollow">' \
                     + ("Licencia Pexels" if lang == "es" else "Pexels License") + "</a>"
            title = lab
        else:
            credit = t["own"]
            title = lab
        items.append(
          f'<li><span class="id-t">{title}</span><p class="id-d">{dsc}</p>'
          f'<span class="id-m"><b>{t["where"]}:</b> {html.escape(f["place"])} · {credit}</span></li>')

    if not items:
        return s
    block = (f'<!--IMGDESC-->{CSS}<section class="img-desc"><div class="img-desc-wrap">'
             f'<span class="id-eyebrow">{t["eyebrow"]}</span><h2>{t["title"]}</h2>'
             f'<p class="id-sub">{t["sub"]}</p><ol>{"".join(items)}</ol>'
             f'</div></section><!--/IMGDESC-->')
    s = re.sub(r"(?s)<!--IMGCREDITS-->.*?<!--/IMGCREDITS-->", "", s)
    s = re.sub(r"(?s)<!--IMGDESC-->.*?<!--/IMGDESC-->", "", s)
    return (s.replace("</main>", block + "</main>", 1) if "</main>" in s
            else s.replace("</body>", block + "</body>", 1))


def schema_locations(s, lang):
    """contentLocation + keywords on each Article ImageObject."""
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
            k = key_for(io.get("contentUrl", "") or io.get("url", ""))
            f = FACTS.get(k) if k else None
            if not f:
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
    total_g = total_d = 0
    for page, spec in PLAN.items():
        if page.startswith("_"):
            continue
        p = ROOT / page
        s = p.read_text(encoding="utf-8")
        lang = spec.get("lang", "es")
        s, ng = gallery_captions(s, lang)
        s = desc_block(s, lang)
        s = schema_locations(s, lang)
        nd = len(re.findall(r'<li><span class="id-t">', s))
        p.write_text(s, encoding="utf-8")
        print(f"  {page.split('/')[-1][:-5]:52s} gallery {ng:2d} · described {nd:2d} · {lang}")
        total_g += ng; total_d += nd
    print(f"\n  {total_g} gallery captions, {total_d} described images")


if __name__ == "__main__":
    main()
