#!/usr/bin/env python3
"""
gallery-to-inline.py — spread each page's gallery photos through its body text,
and drop the gallery's visible captions.

The 2026-09 batch shipped every photo in one "In pictures" grid at the foot of
the article, with a written caption burned over each tile. Two problems: the
body text runs thousands of words with no pictures in it at all, and the
captions describe things the stock photos do not actually show.

So, per page:
  - each gallery photo is ALSO placed inline, after the first paragraph of the
    section it best matches (caption text scored against the section's heading
    and opening paragraph), following the placement the older pages use;
  - inline figures keep a visually-hidden <figcaption> — that is the existing
    site pattern (`.art-inline-img figcaption` is clipped sr-only), so the alt
    and caption still serve screen readers and image search;
  - the gallery's own <figcaption> elements are removed, since those are the
    visible ones that do not match.

The pages need `.art-inline-img` rules, which the batch never carried; they are
copied verbatim from the older template.

Idempotent: inserted figures carry data-inlined="1" and are stripped first.
    python3 scripts/gallery-to-inline.py [--only SUBSTR]
"""
import re, sys, html, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from img_cap import img_html, GALLERY

SIZES_INLINE = "(max-width: 768px) 100vw, 768px"
# The batch is the 36 commits bfe949b..ed86ba4. Pin BOTH ends: using ..HEAD
# would sweep in every later commit and re-run over the older pages, which
# already carry their own inline figures and hand-authored gallery captions.
BATCH_FROM, BATCH_TO = "bfe949b", "ed86ba4"

INLINE_CSS = (
    ".art-inline-img{margin:56px 0;position:relative}"
    ".art-inline-img .imgph{height:416px;border-radius:18px}"
    ".art-inline-img figcaption{position:absolute;width:1px;height:1px;padding:0;"
    "margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}"
    "@media(max-width:640px){.art-inline-img .imgph{height:300px}}"
)

STOP = set("""a an and are as at be by for from has have how in into is it its of on or
that the their they this to was were what when where which who will with your you our
not but if then than there here about over under more most some any can could would
should also just very much many one two three each per its it's""".split())

def words(t):
    return {w for w in re.findall(r"[a-záéíóúñü]{4,}", t.lower()) if w not in STOP}

def gallery_items(s):
    """(img_tag, caption_text) for each figure in the gallery grid, in order."""
    g = re.search(r'<div class="art-gallery-grid">(.*?)</div></div></section>', s, re.S)
    if not g:
        return [], None
    out = []
    for fig in re.findall(r"<figure[^>]*>.*?</figure>", g.group(1), re.S):
        im = re.search(r"<img\b[^>]*>", fig)
        cap = re.search(r"<figcaption>(.*?)</figcaption>", fig, re.S)
        if im:
            out.append((im.group(0), re.sub(r"<[^>]+>", "", cap.group(1)).strip() if cap else ""))
    return out, g

def sections(s):
    """(heading_text, insert_offset) per <h2 id="sN">, insert after its first </p>."""
    hs = list(re.finditer(r'<h2[^>]*id="s\d+"[^>]*>(.*?)</h2>', s, re.S))
    out = []
    for i, h in enumerate(hs):
        nxt = hs[i + 1].start() if i + 1 < len(hs) else len(s)
        body = s[h.end():nxt]
        pm = re.search(r"</p>", body)
        text = re.sub(r"<[^>]+>", " ", h.group(1)) + " " + re.sub(r"<[^>]+>", " ", body[:900])
        out.append((text, h.end() + pm.end() if pm else h.end()))
    return out

def assign(caps, secs):
    """Greedy best-match: each photo to its highest-scoring free section."""
    scored = []
    for ci, c in enumerate(caps):
        cw = words(c)
        for si, (t, _) in enumerate(secs):
            scored.append((len(cw & words(t)), -abs(ci - si), ci, si))
    scored.sort(reverse=True)
    pairs, usedc, useds = {}, set(), set()
    for _, _, ci, si in scored:
        if ci in usedc or si in useds:
            continue
        pairs[ci] = si; usedc.add(ci); useds.add(si)
    # anything unmatched goes in the next free section, in order
    free = [i for i in range(len(secs)) if i not in useds]
    for ci in range(len(caps)):
        if ci not in pairs and free:
            pairs[ci] = free.pop(0)
    return pairs

def build(img_tag, caption):
    src = re.search(r'src="([^"]+)"', img_tag).group(1).replace("&amp;", "&")
    alt = re.search(r'alt="([^"]*)"', img_tag)
    alt = alt.group(1) if alt else html.escape(caption)
    img = img_html(src, alt, GALLERY, SIZES_INLINE)
    cap = f"<figcaption>{html.escape(caption)}</figcaption>" if caption else ""
    return (f'<figure class="art-inline-img" data-inlined="1">'
            f'<div class="imgph photo">{img}</div>{cap}</figure>')

def process(path):
    p = pathlib.Path(path)
    s = orig = p.read_text(encoding="utf-8")

    s = re.sub(r'<figure class="art-inline-img" data-inlined="1">.*?</figure>', "", s, flags=re.S)

    items, g = gallery_items(s)
    if not items:
        return None
    secs = sections(s)
    if not secs:
        return None

    caps = [c for _, c in items]
    pairs = assign(caps, secs)

    # insert end-to-start so earlier offsets stay valid
    ins = sorted(((secs[si][1], ci) for ci, si in pairs.items()), reverse=True)
    for off, ci in ins:
        s = s[:off] + build(items[ci][0], caps[ci]) + s[off:]

    # strip the gallery's visible captions (recompute: offsets moved)
    g2 = re.search(r'<div class="art-gallery-grid">(.*?)</div></div></section>', s, re.S)
    if g2:
        cleaned = re.sub(r"<figcaption>.*?</figcaption>", "", g2.group(1), flags=re.S)
        s = s[:g2.start(1)] + cleaned + s[g2.end(1):]

    if ".art-inline-img{" not in s:
        s = s.replace("</style>", INLINE_CSS + "</style>", 1)

    if s != orig:
        p.write_text(s, encoding="utf-8")
    return len(ins)

def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    files = [f for f in subprocess.run(["git", "diff", "--name-only", f"{BATCH_FROM}..{BATCH_TO}"],
                                       cwd=ROOT, capture_output=True, text=True).stdout.split()
             if f.endswith(".html")]
    n = tot = 0
    for f in files:
        if only and only not in f:
            continue
        r = process(ROOT / f)
        if r:
            n += 1; tot += r
            print(f"  ✓ {f.replace('public/','')}  {r} inline")
    print(f"\n{n} pages, {tot} images placed inline; gallery captions removed")

if __name__ == "__main__":
    main()
