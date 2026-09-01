#!/usr/bin/env python3
"""Make a self-contained copy of a hub page for sharing as an Artifact.

Inlines every image (local files and remote URLs alike) as a data: URI, then
strips the document scaffolding, because the Artifact host supplies its own.
Usage: python3 scripts/build-hub-preview.py <src.html> <out.html>
"""
import base64, mimetypes, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0"}
cache = {}

def datauri(u):
    if u in cache:
        return cache[u]
    try:
        if u.startswith(("http://", "https://")):
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                data = r.read()
                mt = r.headers.get_content_type()
            src = "remote"
        else:
            f = ROOT / "public" / u.lstrip("/")
            if not f.exists():
                print(f"  MISSING {u}"); cache[u] = u; return u
            data = f.read_bytes()
            mt = "image/webp" if f.suffix.lower() == ".webp" else (mimetypes.guess_type(str(f))[0] or "image/jpeg")
            src = "local"
    except Exception as e:
        print(f"  FAILED  {u[:60]} -> {e}"); cache[u] = u; return u
    cache[u] = f"data:{mt};base64," + base64.b64encode(data).decode()
    print(f"  {src:6} {len(data)//1024:5} KB  {u.split('/')[-1][:52]}")
    return cache[u]

def main(src, out):
    h = Path(src).read_text(encoding="utf8")
    h = re.sub(r'(<img[^>]+src=")([^"]+)(")',
               lambda m: m.group(1) + datauri(m.group(2)) + m.group(3), h)
    h = re.sub(r"(background-image:url\(')([^']+)('\))",
               lambda m: m.group(1) + datauri(m.group(2)) + m.group(3), h)
    h = re.sub(r'<link[^>]+rel="icon"[^>]*>', "", h)
    head = h[h.index("<head") + h[h.index("<head"):].index(">") + 1 : h.index("</head>")]
    body = h[re.search(r"<body[^>]*>", h).end() : h.rindex("</body>")]
    frag = re.sub(r'<meta (charset|name="viewport")[^>]*>', "",
                  head.strip() + "\n" + body.strip(), flags=re.I)
    Path(out).write_text(frag, encoding="utf8")
    print(f"  -> {out}  {len(frag)/1048576:.2f} MB\n")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
