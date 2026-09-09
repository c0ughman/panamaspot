#!/usr/bin/env python3
"""
image-credits.py — add a per-page "Image credits" block.

CC BY / CC BY-SA images legally require crediting the photographer. Because the
gallery/bento images carry no caption and the inline captions are description-
only, every page gets one consolidated credits section listing each CC-licensed
Wikimedia image on that page (hero, inline, gallery and bento), with the
photographer, licence and a link to the Commons file page. Public-domain, CC0
and Pexels images need no attribution and are omitted.

Idempotent: the block is wrapped in <!--IMGCREDITS-->…<!--/IMGCREDITS--> and
inserted right before </main>; a re-run strips the old block and rebuilds it.

Run after image-swap.py / image-swap-sections.py:
    python3 scripts/image-credits.py
"""
import re, json, glob, pathlib, html, urllib.parse, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import wm_original

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEL  = json.loads((ROOT/"scripts"/"image-selections.json").read_text())["selections"]
ARTIST = json.loads((ROOT/"scripts"/"image-artists.json").read_text()) if (ROOT/"scripts"/"image-artists.json").exists() else {}

# url (plain, &) -> licence, from the selections file
LICENSE = {}
for c in SEL.values():
    if c.get("hero"): LICENSE[c["hero"]["url"]] = c["hero"].get("license", "")
    for it in c["use"]: LICENSE[it["url"]] = it.get("license", "")

# Images sourced later, straight from Commons (scripts/place-verified-images.py)
# are not in image-selections.json, so their licence and photographer come from
# the Commons metadata captured alongside them. Without this their CC BY / BY-SA
# attribution would silently never render.
_VER = ROOT/"scripts"/"commons-verified.json"
if _VER.exists():
    for _t, _v in json.loads(_VER.read_text(encoding="utf-8")).items():
        LICENSE[_v["url"]] = _v.get("lic", "")
        ARTIST[_v["url"]] = _v.get("artist", "")

def needs_credit(lic): return (lic or "").lower().startswith("cc by")

def commons_page(url):
    fname = url.split("/")[-1]                       # already percent-encoded
    return "https://commons.wikimedia.org/wiki/File:" + fname

def artist_of(url):
    a = re.split(r"\s+from\s+", (ARTIST.get(url, "") or "").strip())[0].strip()
    a = re.sub(r"\s+", " ", a)
    return a or "Unknown"

def pretty_name(url):
    fname = urllib.parse.unquote(url.split("/")[-1])
    return re.sub(r"\.(jpe?g|png|gif)$", "", fname, flags=re.I).replace("_", " ")

CSS = ('<style id="img-credits-css">'
       '.img-credits{padding:52px 24px;border-top:1px solid var(--border-light);background:var(--cream)}'
       '.img-credits-wrap{max-width:1040px;margin:0 auto}'
       '.img-credits .ic-eyebrow{letter-spacing:.14em;text-transform:uppercase;color:var(--terra);'
       'font-size:11px;font-weight:600;font-family:var(--mono);display:block;margin-bottom:10px}'
       '.img-credits h2{font-family:var(--sans);color:var(--ink);font-size:23px;font-weight:600;'
       'letter-spacing:-.01em;margin:0 0 4px;line-height:1.15}'
       '.img-credits .ic-sub{color:var(--ink-mute);font-size:14px;margin:0 0 22px;max-width:60ch}'
       '.img-credits ul{list-style:none;margin:0;padding:0;display:grid;'
       'grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:0 48px}'
       '.img-credits li{padding:13px 0;border-top:1px solid var(--border-light);font-size:13px;line-height:1.45}'
       '.img-credits li a{color:var(--ink);text-decoration:none;font-weight:500}'
       '.img-credits li a:hover{text-decoration:underline}'
       '.img-credits .ic-meta{display:block;color:var(--ink-mute);font-family:var(--mono);'
       'font-size:11px;letter-spacing:.01em;margin-top:3px}'
       '@media(max-width:600px){.img-credits{padding:40px 20px}.img-credits h2{font-size:20px}}'
       '</style>')

PEXELS_LICENSE = "https://www.pexels.com/license/"

def pexels_id(url):
    m = re.search(r"/photos/(\d+)/", url)
    return m.group(1) if m else None

def pexels_page(url):
    pid = pexels_id(url)
    return f"https://www.pexels.com/photo/{pid}/" if pid else PEXELS_LICENSE

def build_block(urls, lang):
    es = lang == "es"
    title   = "Créditos de imágenes" if es else "Image credits"
    eyebrow = "Créditos" if es else "Credits"
    intro = ("Todas las fotografías de esta página, con su fuente y licencia. "
             "Toca cualquier título para ver el original."
             if es else
             "Every photograph on this page, with its source and licence. "
             "Tap any title to view the original.")
    items = []
    for kind, u in urls:
        if kind == "wm":
            lic  = html.escape(LICENSE.get(u, "") or ("Public domain" if es is None else "Wikimedia Commons"))
            who  = html.escape(artist_of(u))
            name = html.escape(pretty_name(u))
            page = html.escape(commons_page(u))
            meta = f"{who} · {lic}" if lic else who
        else:
            pid  = pexels_id(u)
            name = html.escape(f"Pexels photo {pid}" if pid else "Pexels photo")
            page = html.escape(pexels_page(u))
            # Pexels does not expose the photographer without an API key, so the
            # credit names the source and links to the photo's own page, where
            # the photographer is shown.
            meta = "Pexels · " + ("Licencia Pexels" if es else "Pexels License")
        items.append(f'<li><a href="{page}" target="_blank" rel="noopener nofollow">{name}</a>'
                     f'<span class="ic-meta">{meta}</span></li>')
    return (f'<!--IMGCREDITS-->{CSS}<section class="img-credits"><div class="img-credits-wrap">'
            f'<span class="ic-eyebrow">{eyebrow}</span><h2>{title}</h2>'
            f'<p class="ic-sub">{intro}</p><ul>{"".join(items)}</ul>'
            f'</div></section><!--/IMGCREDITS-->')

def collect(s):
    """Every image the page renders, de-duplicated, hero first.

    This used to return only CC BY / CC BY-SA Wikimedia files, on the reasoning
    that those are the ones that legally REQUIRE attribution. The client wants
    every photograph credited, so public-domain and CC0 Commons files and the
    Pexels stock are listed too — credited to their source, since crediting
    only some images reads as though the rest are the site's own work.

    Returns a list of (kind, key) where kind is "wm" or "px".
    """
    main = re.search(r"(?s)<main\b.*?</main>", s)
    body = main.group(0) if main else s
    for pat in (r"(?s)<!--RELATED-MODULE-->.*?<!--/RELATED-MODULE-->",
                r"(?s)<!--IMGCREDITS-->.*?<!--/IMGCREDITS-->",
                r'(?s)<aside class="evb-rail".*?</aside>'):
        body = re.sub(pat, "", body)

    seen, out = set(), []
    for u in re.findall(r'<img[^>]*\bsrc="([^"]+)"', body):
        u = u.replace("&amp;", "&")
        if "upload.wikimedia.org" in u:
            key = wm_original(u); kind = "wm"
        elif "images.pexels.com" in u:
            key = re.sub(r"[?&]w=\d+", "", u); kind = "px"
        else:
            continue                      # the site's own artwork needs no credit
        if key in seen:
            continue
        seen.add(key); out.append((kind, key))
    return out

def process(page):
    p = ROOT/page
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"<!--IMGCREDITS-->.*?<!--/IMGCREDITS-->", "", s, flags=re.S)  # idempotent
    lang = "es" if "/es/" in page else "en"
    if "<!--IMGDESC-->" in s:
        # elvalle-image-descriptions.py owns the foot of this page: its block
        # describes AND credits every image, including the site's own, so a
        # credits list alongside it would repeat the same photographs.
        p.write_text(s, encoding="utf-8"); print(f"  – {page}  (IMGDESC block owns credits)"); return
    urls = collect(s)
    if not urls:
        p.write_text(s, encoding="utf-8"); print(f"  – {page}  (no CC images)"); return
    block = build_block(urls, lang)
    if "</main>" in s:
        s = s.replace("</main>", block + "</main>", 1)
    else:
        s = s.replace("</body>", block + "</body>", 1)
    p.write_text(s, encoding="utf-8")
    print(f"  ✓ {page}  credited {len(urls)} images  [{lang}]")

def main():
    # every article page, not just the selection set — CC BY images now appear
    # on pages image-selections.json never knew about.
    pages = sorted(glob.glob("public/articles/*.html") + glob.glob("public/es/articles/*.html"))
    for page in dict.fromkeys(pages):
        process(page)

if __name__ == "__main__":
    main()
