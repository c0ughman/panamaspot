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

def build_block(urls, lang):
    title = "Créditos de imágenes" if lang == "es" else "Image credits"
    eyebrow = "Créditos" if lang == "es" else "Credits"
    intro = ("Fotografías bajo licencia Creative Commons, vía Wikimedia Commons. "
             "Toca cualquier título para ver la fuente original."
             if lang == "es" else
             "Photographs licensed under Creative Commons, via Wikimedia Commons. "
             "Tap any title to view the original source.")
    items = []
    for u in urls:
        key = u.replace("&amp;", "&")
        lic  = html.escape(LICENSE.get(key, ""))
        who  = html.escape(artist_of(key))
        name = html.escape(pretty_name(u))
        page = html.escape(commons_page(u))
        items.append(f'<li><a href="{page}" target="_blank" rel="noopener nofollow">{name}</a>'
                     f'<span class="ic-meta">{who} · {lic}</span></li>')
    return (f'<!--IMGCREDITS-->{CSS}<section class="img-credits"><div class="img-credits-wrap">'
            f'<span class="ic-eyebrow">{eyebrow}</span><h2>{title}</h2>'
            f'<p class="ic-sub">{intro}</p><ul>{"".join(items)}</ul>'
            f'</div></section><!--/IMGCREDITS-->')

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
