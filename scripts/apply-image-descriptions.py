#!/usr/bin/env python3
"""
apply-image-descriptions.py — real alt text and visible captions, written from
looking at the photographs.

Until now alt text was inherited from whatever the generator guessed and the
gallery carried captions describing things its stock photos did not show. Every
image on the reviewed pages was downloaded and described from the actual pixels;
this applies those descriptions three ways:

  alt=          what is visibly in the frame (the accessibility + image-search
                signal). Never names a place unless the place is identifiable.
  <figcaption>  now VISIBLE under body images and back on the gallery tiles.
                Google uses the text nearest an image to understand it, and a
                caption is the strongest such signal after alt.
  JSON-LD       enrich-images.py picks the caption up from the DOM afterwards.

The inline caption rule was `clip:rect(0,0,0,0)` (screen-reader only). It is
replaced with a real caption style, so the description is on the page.

    python3 scripts/apply-image-descriptions.py
"""
import re, sys, json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SP = pathlib.Path("/private/tmp/claude-501/-Users-coughman-Desktop-clients-panamaspot/"
                  "2d649bcc-9d5c-41b2-b5cf-757f26f5512d/scratchpad")

PAGES = ["best-time-to-visit-panama","boat-charter-panama","cayos-zapatillas-snorkelling-bocas-del-toro",
 "how-to-get-to-bocas-del-toro","red-frog-beach-bocas-del-toro","renting-a-car-in-panama",
 "starfish-beach-bocas-del-toro-playa-estrella-guide","which-bocas-del-toro-island-to-stay-on",
 "san-blas-islands-panama-guna-yala-guide","san-blas-sailing-panama-to-colombia",
 "pearl-islands-panama-guide","is-panama-safe"]

# visible caption, replacing the screen-reader-only rule
CAPTION_CSS = (
 ".art-inline-img figcaption{margin-top:10px;font-family:var(--mono);font-size:12.5px;"
 "line-height:1.5;color:var(--ink-mute);letter-spacing:.01em;max-width:68ch}"
 ".art-gallery-grid figcaption{z-index:2;color:#fff;letter-spacing:.02em;"
 "background:linear-gradient(#0000,#000000b8);padding:28px 14px 12px;font-size:11.5px;"
 "line-height:1.4;position:absolute;bottom:0;left:0;right:0}")

def load():
    """filename -> description, then re-key onto the image URL."""
    desc = {}
    for b in (1, 2, 3):
        f = SP / f"desc_batch{b}.json"
        if f.exists():
            desc.update(json.loads(f.read_text(encoding="utf-8")))
    idx = json.loads((SP / "imgindex.json").read_text(encoding="utf-8"))
    by_key = {}
    for fname, meta in idx.items():
        d = desc.get(fname)
        if d:
            by_key[meta["key"]] = d
    return by_key

def key_of(url):
    """One key per PHOTO, not per rendered width — a Wikimedia file appears as
    /960px-Name.jpg inline and /1280px-Name.jpg as the hero, and Pexels varies
    its ?w=. Both must resolve to the same description."""
    u = url.replace("&amp;", "&")
    u = re.sub(r"[?&]w=\d+", "", u)
    u = re.sub(r"/\d+px-([^/]+)$", r"/\1", u)
    return u

def main():
    D = load()
    print(f"descriptions loaded: {len(D)}")
    missing = set()
    for slug in PAGES:
        p = ROOT / "public" / "articles" / f"{slug}.html"
        s = orig = p.read_text(encoding="utf-8")

        # 1. alt on every image inside the article (skip related cards + credits)
        def set_alt(m):
            tag = m.group(0)
            sm = re.search(r'src="([^"]+)"', tag)
            if not sm:
                return tag
            d = D.get(key_of(sm.group(1)))
            if not d:
                missing.add(key_of(sm.group(1))); return tag
            a = html.escape(d["alt"], quote=True)
            if 'alt="' in tag:
                return re.sub(r'alt="[^"]*"', f'alt="{a}"', tag, count=1)
            return tag.replace("<img ", f'<img alt="{a}" ', 1)

        head, sep, tail = s.partition("<!--RELATED-MODULE-->")
        head = re.sub(r"<img\b[^>]*>", set_alt, head)
        s = head + sep + tail

        # 2. body figures: caption text under the image
        def set_fig(m):
            fig = m.group(0)
            sm = re.search(r'src="([^"]+)"', fig)
            d = D.get(key_of(sm.group(1))) if sm else None
            if not d:
                return fig
            cap = html.escape(d["caption"])
            if "<figcaption>" in fig:
                return re.sub(r"<figcaption>.*?</figcaption>", f"<figcaption>{cap}</figcaption>", fig, flags=re.S)
            return fig.replace("</figure>", f"<figcaption>{cap}</figcaption></figure>")
        s = re.sub(r'<figure class="art-inline-img"[^>]*>.*?</figure>', set_fig, s, flags=re.S)

        # 3. gallery tiles: captions back, with the real descriptions
        g = re.search(r'<div class="art-gallery-grid">(.*?)</div></div></section>', s, re.S)
        if g:
            inner = g.group(1)
            for fig in re.findall(r"<figure[^>]*>.*?</figure>", inner, re.S):
                sm = re.search(r'src="([^"]+)"', fig)
                d = D.get(key_of(sm.group(1))) if sm else None
                if not d:
                    continue
                cap = html.escape(d["caption"])
                new = (re.sub(r"<figcaption>.*?</figcaption>", f"<figcaption>{cap}</figcaption>", fig, flags=re.S)
                       if "<figcaption>" in fig
                       else fig.replace("</figure>", f"<figcaption>{cap}</figcaption></figure>"))
                inner = inner.replace(fig, new, 1)
            s = s[:g.start(1)] + inner + s[g.end(1):]

        # 4. make the inline caption visible
        s = re.sub(r"\.art-inline-img figcaption\{[^}]*\}", "", s)
        s = re.sub(r"\.art-gallery-grid figcaption\{[^}]*\}", "", s)
        if CAPTION_CSS not in s:
            s = s.replace("</style>", CAPTION_CSS + "</style>", 1)

        if s != orig:
            p.write_text(s, encoding="utf-8")
            print(f"  ✓ {slug}")
    if missing:
        print(f"\n  ! {len(missing)} image(s) had no description:")
        for k in sorted(missing)[:12]:
            print("     ", k[-70:])

if __name__ == "__main__":
    main()
