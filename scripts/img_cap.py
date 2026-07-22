#!/usr/bin/env python3
"""
img_cap.py — shared image width-capping helpers (SEO audit C3 / LCP).

Wikimedia now serves thumbnails ONLY at a fixed set of bucket widths, and a
bucket width >= the image's original width returns HTTP 400. So we:
  - look up each original's real width in scripts/img-dims.json, and
  - pick the largest allowed bucket that is <= the target AND < the original.
If the original is already <= the target we leave it untouched.

Pexels URLs carry their own ?w=; we just rewrite that number to the target.

wm_original() reverses a capped Wikimedia thumb URL back to its original file
URL so the credits collector can still derive the Commons filename/licence.

Targets used by the generators:  hero=1280, gallery/inline/bento=960, card=500.
"""
import json, re, pathlib

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_DIMS = json.loads((_ROOT/"scripts"/"img-dims.json").read_text()) if (_ROOT/"scripts"/"img-dims.json").exists() else {}

BUCKETS = [250, 500, 960, 1280, 1920]

HERO, GALLERY, CARD = 1280, 960, 500

_WM_ORIG = re.compile(r"^(https://upload\.wikimedia\.org/wikipedia/commons/)([0-9a-f]/[0-9a-f]{2})/([^/?#]+)$")
_WM_THUMB = re.compile(r"^(https://upload\.wikimedia\.org/wikipedia/commons/)thumb/([0-9a-f]/[0-9a-f]{2})/([^/]+)/\d+px-[^/?#]+$")

def cap(url, target):
    """Return a width-capped URL (plain &, not HTML-escaped)."""
    u = url.replace("&amp;", "&")
    if "images.pexels.com" in u:
        return re.sub(r"([?&]w=)\d+", lambda m: m.group(1) + str(target), u)
    m = _WM_ORIG.match(u)
    if not m:
        return u  # already a thumb, or a non-cappable host
    base, hashpath, fname = m.groups()
    d = _DIMS.get(u)
    if not d:
        return u  # unknown dims → don't risk a 400
    ow = d["w"]
    if ow <= target:
        return u  # already small enough
    cands = [b for b in BUCKETS if b <= target and b < ow]
    if not cands:
        return u
    return f"{base}thumb/{hashpath}/{fname}/{max(cands)}px-{fname}"

def wm_original(url):
    """Reverse a capped Wikimedia thumb URL back to the original file URL."""
    u = url.replace("&amp;", "&")
    m = _WM_THUMB.match(u)
    if m:
        return f"{m.group(1)}{m.group(2)}/{m.group(3)}"
    return u

def _esc(u):
    return u.replace("&", "&amp;")

def rendered_dims(url):
    """Actual (width, height) of the *rendered* (capped) image at `url`, for
    ImageObject width/height. None if unknown."""
    u = url.replace("&amp;", "&")
    m = re.search(r"/(\d+)px-[^/]+$", u)          # Wikimedia thumb: width in the path
    if m:
        w = int(m.group(1)); d = _DIMS.get(wm_original(u))
        return (w, round(d["h"] * w / d["w"])) if d else None
    if "images.pexels.com" in u:
        wm = re.search(r"[?&]w=(\d+)", u); w = int(wm.group(1)) if wm else None
        d = _DIMS.get(re.sub(r"([?&]w=)\d+", r"\g<1>1600", u))
        return (w, round(d["h"] * w / d["w"])) if (w and d) else None
    d = _DIMS.get(u)                               # original / local
    return (d["w"], d["h"]) if d else None

def srcset(url):
    """A responsive srcset string offering every safe width below the original
    (Wikimedia buckets / Pexels ?w=). Empty string if we can't build one."""
    u = url.replace("&amp;", "&")
    if "images.pexels.com" in u:
        base1600 = re.sub(r"([?&]w=)\d+", r"\g<1>1600", u)
        d = _DIMS.get(base1600) or _DIMS.get(u)
        ow = d["w"] if d else 1600
        widths = [w for w in (400, 700, 960, 1280, 1600) if w <= ow]
        if len(widths) < 2:
            return ""
        return ", ".join(f"{_esc(re.sub(r'([?&]w=)[0-9]+', lambda m: m.group(1)+str(w), u))} {w}w"
                         for w in widths)
    orig = wm_original(u)
    mo = _WM_ORIG.match(orig)
    if not mo:
        return ""
    base, hashpath, fname = mo.groups()
    d = _DIMS.get(orig)
    if not d:
        return ""
    widths = [b for b in BUCKETS if b < d["w"]]
    if len(widths) < 2:
        return ""
    return ", ".join(f"{base}thumb/{hashpath}/{fname}/{w}px-{fname} {w}w" for w in widths)

def img_html(url, alt, target, sizes, eager=False, style="width:100%;height:100%;object-fit:cover;display:block"):
    """A complete responsive <img> element: capped src, srcset+sizes, intrinsic
    width/height (no CLS), lazy/eager loading. `alt` is used verbatim (already
    HTML-escaped by the caller when it comes from a caption)."""
    src = cap(url, target)
    ss = srcset(url)
    dims = capped_dims(url, target)
    wh = f' width="{dims[0]}" height="{dims[1]}"' if dims else ""
    ssattr = f' srcset="{ss}" sizes="{sizes}"' if ss else ""
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{_esc(src)}" alt="{alt}"{wh}{ssattr} {load} decoding="async" '
            f'style="{style}">')

def capped_dims(url, target):
    """Return (w, h) the image will render at once capped to `target`, or None."""
    u = url.replace("&amp;", "&")
    if "images.pexels.com" in u:
        d = _DIMS.get(u)
        if not d:
            return None
        if d["w"] <= target:
            return d["w"], d["h"]
        return target, round(d["h"] * target / d["w"])
    d = _DIMS.get(wm_original(u))
    if not d:
        return None
    ow, oh = d["w"], d["h"]
    if ow <= target:
        return ow, oh
    cands = [b for b in BUCKETS if b <= target and b < ow]
    w = max(cands) if cands else ow
    return w, round(oh * w / ow)
