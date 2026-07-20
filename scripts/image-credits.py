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
import re, json, pathlib, html, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEL  = json.loads((ROOT/"scripts"/"image-selections.json").read_text())["selections"]
ARTIST = json.loads((ROOT/"scripts"/"image-artists.json").read_text()) if (ROOT/"scripts"/"image-artists.json").exists() else {}

# url (plain, &) -> licence, from the selections file
LICENSE = {}
for c in SEL.values():
    if c.get("hero"): LICENSE[c["hero"]["url"]] = c["hero"].get("license", "")
    for it in c["use"]: LICENSE[it["url"]] = it.get("license", "")

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

def build_block(urls, lang):
    title = "Créditos de imágenes" if lang == "es" else "Image credits"
    intro = ("Fotografías bajo licencia Creative Commons vía Wikimedia Commons."
             if lang == "es" else
             "Photographs licensed under Creative Commons via Wikimedia Commons.")
    photo = "Foto" if lang == "es" else "Photo"
    items = []
    for u in urls:
        lic = LICENSE.get(u.replace("&amp;", "&"), "")
        who = html.escape(artist_of(u.replace("&amp;", "&")))
        name = html.escape(pretty_name(u))
        page = html.escape(commons_page(u))
        items.append(f'<li>{photo}: {who} — <a href="{page}" target="_blank" rel="noopener nofollow">{name}</a>, {html.escape(lic)}</li>')
    css = ('<style id="img-credits-css">.img-credits{border-top:1px solid rgba(0,0,0,.12);'
           'margin-top:40px;padding-top:20px;font-size:13px;opacity:.75}'
           '.img-credits h2{font-size:15px;margin:0 0 6px}.img-credits p{margin:0 0 10px}'
           '.img-credits ul{margin:0;padding-left:18px;line-height:1.6}'
           '.img-credits a{color:inherit}</style>')
    return (f'<!--IMGCREDITS-->{css}<section class="img-credits"><div class="container">'
            f'<h2>{title}</h2><p>{intro}</p><ul>{"".join(items)}</ul></div></section><!--/IMGCREDITS-->')

def collect(s):
    """All CC-BY* Wikimedia image URLs present on the page, de-duplicated, in
    document order (hero first, then body/gallery/bento)."""
    seen, out = set(), []
    for u in re.findall(r"https://upload\.wikimedia\.org/[^'\"]+", s):
        key = u.replace("&amp;", "&")
        if key in seen:
            continue
        if needs_credit(LICENSE.get(key, "")):
            seen.add(key); out.append(u)
    return out

def process(page):
    p = ROOT/page
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"<!--IMGCREDITS-->.*?<!--/IMGCREDITS-->", "", s, flags=re.S)  # idempotent
    lang = "es" if "/es/" in page else "en"
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
    pages = []
    for c in SEL.values():
        pages += c["pages"]
    for page in dict.fromkeys(pages):
        process(page)

if __name__ == "__main__":
    main()
