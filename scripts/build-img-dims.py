#!/usr/bin/env python3
"""
build-img-dims.py — resolve the real pixel dimensions of every image referenced
by scripts/image-selections.json and write them to scripts/img-dims.json.

Why: Wikimedia no longer serves arbitrary-width thumbnails — only a fixed set of
bucket widths, and asking for a bucket >= the original width returns HTTP 400.
To width-cap safely (see scripts/img_cap.py) we must know each original's width;
we also reuse the dimensions for accurate og:image:width/height.

- Wikimedia originals: dimensions come from the Commons imageinfo API (batched).
- Pexels images: the served JPEG is probed and its SOF marker parsed (no deps).

Idempotent + incremental: existing entries are kept; only missing URLs are
fetched. Re-run any time image-selections.json changes:
    python3 scripts/build-img-dims.py
"""
import json, re, glob, pathlib, urllib.parse, urllib.request, struct, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEL  = json.loads((ROOT/"scripts"/"image-selections.json").read_text())["selections"]
OUT  = ROOT/"scripts"/"img-dims.json"
UA   = {"User-Agent": "PanamaSpot-image-tooling/1.0 (https://panamaspot.com)"}

def all_urls():
    urls = []
    for c in SEL.values():
        if c.get("hero"): urls.append(c["hero"]["url"])
        for it in c["use"]: urls.append(it["url"])
    # Also every Pexels image actually rendered on a page (the older non-SEL
    # pages), normalized to the ?w=1600 key that img_cap's srcset/dims use.
    for p in glob.glob(str(ROOT/"public"/"articles"/"*.html")) + glob.glob(str(ROOT/"public"/"es"/"articles"/"*.html")):
        s = pathlib.Path(p).read_text()
        found = re.findall(r"background-image:url\('([^']+)'\)", s) + re.findall(r'<img[^>]*\bsrc="([^"]+)"', s)
        for u in found:
            u = u.replace("&amp;", "&")
            if "images.pexels.com" in u:
                urls.append(re.sub(r"([?&]w=)\d+", r"\g<1>1600", u))
    return list(dict.fromkeys(u.replace("&amp;", "&") for u in urls))

def wm_filename(url):
    m = re.match(r"^https://upload\.wikimedia\.org/wikipedia/commons/[0-9a-f]/[0-9a-f]{2}/([^/?#]+)$", url)
    return urllib.parse.unquote(m.group(1)) if m else None

def fetch_wikimedia(urls, dims):
    files = {}
    for u in urls:
        f = wm_filename(u)
        if f and u not in dims:
            files["File:" + f] = u
    titles = list(files)
    for i in range(0, len(titles), 40):
        batch = titles[i:i+40]
        q = urllib.parse.urlencode({
            "action": "query", "prop": "imageinfo", "iiprop": "size",
            "titles": "|".join(batch), "format": "json",
        })
        req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q, headers=UA)
        data = json.loads(urllib.request.urlopen(req, timeout=40).read())
        pages = data.get("query", {}).get("pages", {})
        # map normalized title -> requested title
        norm = {n["to"]: n["from"] for n in data.get("query", {}).get("normalized", [])}
        for pg in pages.values():
            title = pg.get("title")
            orig = norm.get(title, title)
            info = pg.get("imageinfo")
            if orig in files and info:
                dims[files[orig]] = {"w": info[0]["width"], "h": info[0]["height"]}

def jpeg_size(data):
    i = 2
    while i < len(data):
        if data[i] != 0xFF: i += 1; continue
        marker = data[i+1]
        if marker in (0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF):
            h, w = struct.unpack(">HH", data[i+5:i+9]); return w, h
        seg = struct.unpack(">H", data[i+2:i+4])[0]; i += 2 + seg
    return None

def png_size(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24]); return w, h
    return None

def fetch_pexels(urls, dims):
    for u in urls:
        if "images.pexels.com" not in u or u in dims: continue
        try:
            req = urllib.request.Request(u, headers=UA)
            raw = urllib.request.urlopen(req, timeout=40).read(200000)
            sz = png_size(raw) or jpeg_size(raw)
            if sz: dims[u] = {"w": sz[0], "h": sz[1]}
        except Exception as e:
            print(f"  ! pexels probe failed {u}: {e}")

def main():
    dims = json.loads(OUT.read_text()) if OUT.exists() else {}
    urls = all_urls()
    fetch_wikimedia(urls, dims)
    fetch_pexels(urls, dims)
    OUT.write_text(json.dumps(dims, indent=1, ensure_ascii=False))
    missing = [u for u in urls if u not in dims]
    print(f"dims: {len(dims)} known, {len(missing)} missing of {len(urls)} urls")
    for u in missing: print("  missing:", u)

if __name__ == "__main__":
    main()
