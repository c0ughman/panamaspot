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
