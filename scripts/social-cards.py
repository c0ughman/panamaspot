#!/usr/bin/env python3
"""social-cards.py — give portrait heroes a landscape card for social sharing.

Every article declares twitter:card=summary_large_image, which asks Facebook,
X, LinkedIn and WhatsApp to render the og:image in a 1.91:1 frame. They do that
by centre-cropping whatever they are given. A hero that is portrait — the Las
Nubes plate is 1100x1954, the Chorro Las Mozas falls is 1280x1922 — loses two
thirds of its height to that crop, and the subject usually goes with it.

So: render a real 1200x630 card for any hero whose aspect is under 1.2, taking
the band the page's own object-position already nominates as the interesting
part. A hero with no object-position is centred, which is what the browser
does too.

Landscape heroes are left alone. A 3:2 photograph loses about a fifth of its
height to the 1.91:1 frame, which is the normal cost of social cropping and
not worth a second file.

    python3 scripts/social-cards.py            # build cards, rewrite the meta
    python3 scripts/social-cards.py --check    # report only, change nothing

Run after elvalle-image-pass.py (it reads the hero the pass wrote) and before
build-page-images.py. Idempotent: cards are regenerated from the source each
time and the meta tags are replaced, not appended.

Ordering trap: seo-finalize.py re-derives og:image:width/height from the hero
and would put the portrait dimensions back. If both are run, this one runs
last. (seo-finalize.py is also pinned to EDIT_DATE 2026-07-20 and will regress
dateModified, so it is not part of the routine image pipeline.)
"""
import re, sys, json, pathlib, subprocess, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "scripts/elvalle-image-plan.json").read_text(encoding="utf-8"))
CARD_W, CARD_H = 1200, 630
MIN_AR = 1.2          # below this the social crop starts eating the subject
OUTDIR = ROOT / "public/images/social"
CACHE = ROOT / ".cache/social-src"
CHECK = "--check" in sys.argv


def og(s, prop):
    m = re.search(rf'<meta content="([^"]*)" property="{re.escape(prop)}"', s)
    return m.group(1) if m else None


def fetch(url):
    """Remote heroes (Wikimedia, Pexels) have to come down before they can be
    cropped. Cached so a re-run does not re-hit the servers, which rate-limit."""
    CACHE.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9._-]", "_", url)[-120:]
    p = CACHE / name
    if not p.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "panamaspot-social-cards/1.0"})
        p.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    return p


def vertical_focus(pos):
    """object-position's second value as a fraction. 'center 55%' -> 0.55."""
    if not pos:
        return 0.5
    parts = pos.split()
    if len(parts) < 2:
        return 0.5
    v = parts[1].strip()
    if v.endswith("%"):
        return float(v[:-1]) / 100
    return {"top": 0.0, "center": 0.5, "bottom": 1.0}.get(v, 0.5)


def build(src_path, focus, out):
    """Scale to the card width, then take a CARD_H band centred on `focus`."""
    w, h = subprocess.run(["magick", "identify", "-format", "%w %h", str(src_path)],
                          capture_output=True, text=True, check=True).stdout.split()
    w, h = int(w), int(h)
    scaled_h = round(h * CARD_W / w)
    if scaled_h <= CARD_H:
        # Already wide enough once scaled — a plain resize is the whole job.
        subprocess.run(["magick", str(src_path), "-resize", f"{CARD_W}x{CARD_H}^",
                        "-gravity", "center", "-extent", f"{CARD_W}x{CARD_H}",
                        "-quality", "82", str(out)], check=True)
        return
    top = round(focus * scaled_h - CARD_H / 2)
    top = max(0, min(top, scaled_h - CARD_H))       # keep the band inside the image
    subprocess.run(["magick", str(src_path), "-resize", f"{CARD_W}x",
                    "-crop", f"{CARD_W}x{CARD_H}+0+{top}", "+repage",
                    "-quality", "82", str(out)], check=True)


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    changed = 0
    for page, spec in PLAN.items():
        if page.startswith("_"):
            continue
        p = ROOT / page
        s = p.read_text(encoding="utf-8")
        url = og(s, "og:image")
        ow, oh = og(s, "og:image:width"), og(s, "og:image:height")
        if not (url and ow and oh):
            continue
        ar = int(ow) / int(oh)
        if ar >= MIN_AR:
            continue
        slug = page.split("/")[-1][:-5]
        hero = spec["hero"]
        focus = vertical_focus(hero[2] if len(hero) > 2 else None)
        print(f"  {slug:46s} {ow}x{oh} ar={ar:.2f} focus={focus:.0%}")
        if CHECK:
            continue
        raw = url.replace("&amp;", "&")
        src = (ROOT / "public" / raw.replace("https://panamaspot.com/", "")
               if raw.startswith("https://panamaspot.com/") else fetch(raw))
        out = OUTDIR / f"{slug}-og.webp"
        build(src, focus, out)
        card = f"https://panamaspot.com/images/social/{out.name}"
        s = re.sub(r'<meta content="[^"]*" property="og:image"/>',
                   f'<meta content="{card}" property="og:image"/>', s)
        s = re.sub(r'<meta content="[^"]*" name="twitter:image"/>',
                   f'<meta content="{card}" name="twitter:image"/>', s)
        s = re.sub(r'<meta content="[^"]*" property="og:image:width"/>',
                   f'<meta content="{CARD_W}" property="og:image:width"/>', s)
        s = re.sub(r'<meta content="[^"]*" property="og:image:height"/>',
                   f'<meta content="{CARD_H}" property="og:image:height"/>', s)
        p.write_text(s, encoding="utf-8")
        changed += 1
    print(f"\n{changed} social cards written" if not CHECK else "\n(check only)")


if __name__ == "__main__":
    main()
