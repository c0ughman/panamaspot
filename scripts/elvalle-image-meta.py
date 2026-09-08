#!/usr/bin/env python3
"""
elvalle-image-meta.py — resolve every image named in scripts/elvalle-image-plan.json
and record what the rest of the pipeline needs to render and credit it.

Two sinks, both idempotent and additive:
  scripts/commons-verified.json  file title -> {url, w, h, lic, artist}
                                 (image-credits.py reads licence + photographer here)
  scripts/img-dims.json          url/path -> {w, h}
                                 (img_cap.py reads this to width-cap safely and to
                                  emit width/height so the images cause no CLS)

Wikimedia dimensions come from the Commons imageinfo API; local /images/... files
are measured with `magick identify`; Pexels images already in img-dims.json are
left alone (build-img-dims.py owns those).

    python3 scripts/elvalle-image-meta.py
"""
import json, re, pathlib, subprocess, urllib.parse, urllib.request, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "scripts" / "elvalle-image-plan.json").read_text(encoding="utf-8"))
VER = ROOT / "scripts" / "commons-verified.json"
DIMS = ROOT / "scripts" / "img-dims.json"
UA = {"User-Agent": "PanamaSpot-image-tooling/1.0 (https://panamaspot.com)"}


def plan_keys():
    keys = []
    for page, spec in PLAN.items():
        if page.startswith("_"):
            continue
        entries = [spec["hero"]] + list(spec["sections"].values())
        keys += [e[0] for e in entries]
    return list(dict.fromkeys(keys))


def commons_info(titles):
    """title -> {url, w, h, lic, artist} from the Commons imageinfo API."""
    out = {}
    for i in range(0, len(titles), 20):
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "titles": "|".join(titles[i:i + 20]),
            "prop": "imageinfo", "iiprop": "url|size|extmetadata",
        })
        req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q, headers=UA)
        data = json.loads(urllib.request.urlopen(req, timeout=60).read())
        for pg in (data.get("query", {}).get("pages") or {}).values():
            if "missing" in pg:
                print(f"  !! not on Commons: {pg['title']}")
                continue
            ii = (pg.get("imageinfo") or [{}])[0]
            em = ii.get("extmetadata", {})
            artist = re.sub(r"<[^>]+>", "", (em.get("Artist") or {}).get("value", "")).strip()
            out[pg["title"]] = {
                "url": (ii.get("url") or "").split("?")[0],
                "w": ii.get("width"), "h": ii.get("height"),
                "lic": (em.get("LicenseShortName") or {}).get("value", ""),
                "artist": re.sub(r"\s+", " ", artist),
            }
        time.sleep(0.2)
    return out


def local_dims(path):
    p = ROOT / "public" / path.lstrip("/")
    if not p.exists():
        print(f"  !! missing local file: {path}")
        return None
    r = subprocess.run(["magick", "identify", "-format", "%w %h", str(p) + "[0]"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  !! could not measure {path}: {r.stderr.strip()[:120]}")
        return None
    w, h = r.stdout.split()
    return {"w": int(w), "h": int(h)}


def main():
    ver = json.loads(VER.read_text(encoding="utf-8")) if VER.exists() else {}
    dims = json.loads(DIMS.read_text(encoding="utf-8")) if DIMS.exists() else {}

    keys = plan_keys()
    titles = [k for k in keys if k.startswith("File:")]
    locals_ = [k for k in keys if k.startswith("/images/")]

    info = commons_info(titles)
    for title, v in info.items():
        ver[title[5:]] = v            # commons-verified.json is keyed without "File:"
        if v["url"] and v["w"]:
            dims[v["url"]] = {"w": v["w"], "h": v["h"]}

    for path in locals_:
        d = local_dims(path)
        if d:
            dims[path] = d

    VER.write_text(json.dumps(ver, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    DIMS.write_text(json.dumps(dims, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  commons-verified.json: {len(ver)} files ({len(info)} resolved this run)")
    print(f"  img-dims.json:         {len(dims)} entries")
    missing = [t for t in titles if t not in info]
    if missing:
        print("  UNRESOLVED:", missing)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
