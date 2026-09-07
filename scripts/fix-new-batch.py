#!/usr/bin/env python3
"""
fix-new-batch.py — repair the 2026-09 batch of 36 generated SEO pages.

These pages were published without going through the normal post-processing
pipeline, so they carry four template artefacts that the pipeline would have
resolved. This script fixes the things the pipeline itself cannot:

  1. DEAD IMAGES   five Pexels photo IDs return HTTP 404; swap each for a
                   verified-live photo of the same subject (caption adjusted
                   where the replacement shows something different).
  2. STRAY HERO    every page carries the template's leftover
                   <img src="/images/things-to-do-el-valle.webp">, which the
                   `.art-hero-img-full img` rule paints straight over the
                   page's real background-image. Removing it lets
                   convert-legacy-heroes.py promote the background to a real
                   <img> the normal way.
  3. HREFLANG      every page declares itself an alternate of
                   things-to-do-el-valle-de-anton. Rewrite to self-reference,
                   pairing only genuine EN↔ES translations.
  4. DEAD LINKS    five in-prose links to article slugs that do not exist.

Idempotent — safe to re-run. Run BEFORE convert-legacy-heroes.py / imgify.py.
    python3 scripts/fix-new-batch.py
"""
import re, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from img_cap import rendered_dims

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://panamaspot.com"
BATCH_BASE = "bfe949b"          # last commit before the 36-page batch

# ── 1. dead Pexels photos → live replacements ────────────────────────────────
# new_caption is set only where the replacement depicts something different
# from the original caption; None keeps the caption already on the page.
DEAD_IMAGES = {
    "724892": [
        ("panama-city-to-boquete",   "21222910", None),
        ("where-to-stay-in-boquete", "37341529", None),
    ],
    "27178287": [("el-valle-de-anton-vs-boquete", "11112892", None)],
    "1030322":  [("san-blas-islands-panama-guna-yala-guide", "3954301",
                  "Anchored off the uninhabited cays of the northwestern comarca — "
                  "the clearest water and least-visited reefs in Guna Yala")],
    "11688796": [("boquete-bike-rental", "5988866",
                  "The mountain road climbing north through Boquete&#x27;s coffee and "
                  "vegetable farms — the main cycling route out of town.")],
    "27973276": [("donde-comer-en-el-valle-de-anton", "25391622",
                  "Puestos de comida en el mercado público de El Valle de Antón, "
                  "abiertos desde temprano sobre la Calle Principal.")],
}

# ── 3. genuine EN↔ES translation pairs ───────────────────────────────────────
# Conservative on purpose: a wrong pair tells Google two different articles are
# the same page. Anything not listed here self-references only.
PAIRS = [
    ("articles/where-to-stay-in-el-valle-de-anton", "es/articles/donde-dormir-el-valle-de-anton"),
    ("articles/how-to-get-to-bocas-del-toro",       "es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama"),
    ("articles/san-blas-islands-panama-guna-yala-guide", "es/articles/san-blas-guna-yala-guia-tours-islas"),
    ("articles/boquete-bike-rental",                "es/articles/alquiler-de-bicicletas-boquete"),
]

# ── 4. in-prose links to slugs that do not exist ─────────────────────────────
DEAD_LINKS = {
    "/articles/things-to-do-boquete-panama": "/articles/things-to-do-in-boquete-panama",
    "/articles/boquete-things-to-do":        "/articles/things-to-do-in-boquete-panama",
    "/es/articles/que-hacer-boquete":        "/es/articles/que-hacer-en-boquete-guia-completa",
    # no e-bike article exists in ES; the funnel is the right destination
    "/es/articles/e-valley-bikes-el-valle-de-anton": "/funnels/evalley_elvalle_es",
}

STRAY_HERO = re.compile(
    r'(<div class="art-hero-img-full"[^>]*>)\s*<img[^>]*src="/images/things-to-do-el-valle\.webp"[^>]*>\s*(?=</div>)')

def batch_files():
    out = subprocess.run(["git", "diff", "--name-only", f"{BATCH_BASE}..HEAD"],
                         cwd=ROOT, capture_output=True, text=True).stdout.split()
    return [ROOT / f for f in out if f.endswith(".html")]

def url_for(path):
    return "/" + path.relative_to(ROOT / "public").as_posix()[:-5]

def fix_dead_images(path, s):
    slug = path.stem
    n = 0
    for old_id, targets in DEAD_IMAGES.items():
        for target_slug, new_id, new_cap in targets:
            if target_slug != slug:
                continue
            before = s
            s = s.replace(f"pexels-photo-{old_id}.jpeg", f"pexels-photo-{new_id}.jpeg")
            s = s.replace(f"photos/{old_id}/", f"photos/{new_id}/")
            if new_cap and s != before:
                # retarget the caption that follows this image
                s = re.sub(
                    r'(pexels-photo-%s\.jpeg[^"]*"[^>]*></div><figcaption>)(.*?)(</figcaption>)' % new_id,
                    lambda m: m.group(1) + new_cap + m.group(3), s, count=1, flags=re.S)
            if s != before:
                n += 1
    return s, n

def fix_hreflang(path, s, pair_map):
    url = url_for(path)
    lang = "es" if url.startswith("/es/") else "en"
    twin = pair_map.get(url.lstrip("/"))
    if twin:
        en = BASE + ("/" + twin if lang == "es" else url)
        es = BASE + (url if lang == "es" else "/" + twin)
        tags = (f'<link href="{en}" hreflang="en" rel="alternate"/>'
                f'<link href="{es}" hreflang="es" rel="alternate"/>'
                f'<link href="{en}" hreflang="x-default" rel="alternate"/>')
    else:
        self_url = BASE + url
        tags = (f'<link href="{self_url}" hreflang="{lang}" rel="alternate"/>'
                f'<link href="{self_url}" hreflang="x-default" rel="alternate"/>')
    # drop every existing alternate link, then re-insert after the canonical
    s = re.sub(r'<link[^>]*hreflang="[^"]*"[^>]*/?>', "", s)
    m = re.search(r'<link[^>]*rel="canonical"[^>]*/?>', s)
    if not m:
        raise SystemExit(f"  !! no canonical in {path.name}")
    return s[:m.end()] + tags + s[m.end():]

def fix_links(s):
    n = 0
    for bad, good in DEAD_LINKS.items():
        c = s.count(f'href="{bad}"')
        if c:
            s = s.replace(f'href="{bad}"', f'href="{good}"'); n += c
    return s, n

def fix_og_image(path, s):
    """og:image:alt/width/height + twitter:image:alt, matching the hero.

    Runs only once the hero is a real <img> (i.e. after
    convert-legacy-heroes.py), so a second pass of this script fills them in.
    og:image stays at the 1600px variant crawlers prefer; the width/height
    reported are that variant's, not the 1280px one the page renders.
    """
    hm = re.search(r'art-hero-img-full"><img[^>]*>', s)
    if not hm:
        return s, 0
    tag = hm.group(0)
    am = re.search(r'\balt="([^"]*)"', tag)
    if not am:
        return s, 0
    alt = am.group(1)
    om = re.search(r'<meta content="([^"]*)" property="og:image"/>', s)
    if not om:
        return s, 0
    dims = rendered_dims(om.group(1))
    extra = f'<meta content="{alt}" property="og:image:alt"/>'
    if dims:
        extra += (f'<meta content="{dims[0]}" property="og:image:width"/>'
                  f'<meta content="{dims[1]}" property="og:image:height"/>')
    for pat in (r'<meta content="[^"]*" property="og:image:alt"/>',
                r'<meta content="[^"]*" property="og:image:width"/>',
                r'<meta content="[^"]*" property="og:image:height"/>',
                r'<meta content="[^"]*" name="twitter:image:alt"/>'):
        s = re.sub(pat, "", s)
    om = re.search(r'<meta content="[^"]*" property="og:image"/>', s)
    s = s[:om.end()] + extra + s[om.end():]
    tm = re.search(r'<meta content="[^"]*" name="twitter:image"/>', s)
    if tm:
        s = s[:tm.end()] + f'<meta content="{alt}" name="twitter:image:alt"/>' + s[tm.end():]
    return s, 1


def main():
    files = batch_files()
    pair_map = {}
    for en, es in PAIRS:
        pair_map[en] = es
        pair_map[es] = en
    # the ES sides of two pairs are pre-existing pages — they need the
    # reciprocal tag too, or the pairing is one-way and Google ignores it.
    extra = [ROOT / "public" / p / "" for p in []]
    targets = list(files)
    for en, es in PAIRS:
        p = ROOT / "public" / (es + ".html")
        if p.exists() and p not in targets:
            targets.append(p)

    tot = {"img": 0, "hero": 0, "links": 0, "hreflang": 0, "og": 0}
    for p in sorted(targets):
        s = orig = p.read_text(encoding="utf-8")
        is_batch = p in files
        if is_batch:
            s, ni = fix_dead_images(p, s)
            tot["img"] += ni
            s, nh = STRAY_HERO.subn(r"\1", s)
            tot["hero"] += nh
            s, nl = fix_links(s)
            tot["links"] += nl
            s, no = fix_og_image(p, s)
            tot["og"] += no
        s2 = fix_hreflang(p, s, pair_map)
        if s2 != s:
            tot["hreflang"] += 1
        s = s2
        if s != orig:
            p.write_text(s, encoding="utf-8")
            print(f"  ✓ {p.relative_to(ROOT)}")
    print(f"\ndead images swapped : {tot['img']}")
    print(f"stray heroes removed: {tot['hero']}")
    print(f"dead links fixed    : {tot['links']}")
    print(f"hreflang rewritten  : {tot['hreflang']}")
    print(f"og:image tags set   : {tot['og']}")

if __name__ == "__main__":
    main()
