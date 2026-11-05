"""Every guide's share image (og:image and twitter:image) must be its hero photo.
Compares the pictures themselves: the hero, cropped to the share shape, against the share image, both shrunk to 48x25.
  python3 scripts/check_share_images.py [--page=articles/x ...]     exits 1 if any page fails
"""
import html, re, subprocess, sys, urllib.request, urllib.error
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / "public"
CACHE = Path("/tmp") / "ps-share-check"; CACHE.mkdir(exist_ok=True)
only = {a.split("=", 1)[1] for a in sys.argv if a.startswith("--page=")}


def local(u):
    u = html.unescape(u)
    path = u.replace("https://panamaspot.com", "")
    if path.startswith("/"):
        f = P / path.split("?")[0].lstrip("/")
        return f if f.exists() else None
    dest = CACHE / re.sub(r"[^\w.]+", "_", u)[-120:]
    if not dest.exists():
        req = urllib.request.Request(u, headers={"User-Agent": "PanamaSpot share-image check (panamaspot.com)"})
        import time
        for wait in (1, 5, 15, 40):
            time.sleep(wait)
            try:
                dest.write_bytes(urllib.request.urlopen(req, timeout=60).read()); break
            except urllib.error.HTTPError as e:
                if e.code != 429: raise
    return dest


def small(f, crop, y=50, zoom=1.0):
    """Shrink to 48x25 grey. With crop, cut the 1200:630 band whose centre sits y% down the photo."""
    ops = []
    if crop:
        w, h = map(int, subprocess.run(["magick", "identify", "-format", "%w %h", str(f) + "[0]"], capture_output=True, text=True).stdout.split())
        if w / h < 1200 / 630:
            w2 = int(w / zoom); x0 = (w - w2) // 2; w = w2
            ch = int(w * 630 / 1200); top = int(max(0, min(h - ch, h * y / 100 - ch / 2))); ops = ["-crop", f"{w}x{ch}+{x0}+{top}", "+repage"]
        else:
            cw = int(h * 1200 / 630); ops = ["-crop", f"{cw}x{h}+{(w - cw) // 2}+0", "+repage"]
    args = ["magick", str(f) + "[0]", "-auto-orient", *ops, "-resize", "48x25!", "-colorspace", "gray", "-depth", "8", "gray:-"]
    return subprocess.run(args, capture_output=True, check=True).stdout


def diff(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


bad = 0; n = 0
for f in sorted(P.glob("articles/*.html")) + sorted(P.glob("es/articles/*.html")):
    rel = str(f.relative_to(P))[:-5]
    if only and rel not in only: continue
    h = f.read_text(errors="ignore")
    hero = re.search(r'<img\b[^>]*class="hero-img"[^>]*>', h) or re.search(r'(?:art-hero-img-full|hub-hero-img)"[^>]*>\s*<img\b[^>]*>', h)
    og = re.search(r'<meta content="([^"]+)" property="og:image"/?>', h) or re.search(r'<meta property="og:image" content="([^"]+)"', h)
    tw = re.search(r'<meta content="([^"]+)" name="twitter:image"/?>', h) or re.search(r'<meta name="twitter:image" content="([^"]+)"', h)
    n += 1; why = []
    if not hero or not og: why.append("no hero or no og:image")
    else:
        hs = re.search(r'\bsrc="([^"]+)"', hero[0])[1]
        if tw and tw[1] != og[1]: why.append("twitter:image differs from og:image")
        same = lambda u: html.unescape(u).replace("https://panamaspot.com", "")
        if same(hs) == same(og[1]): continue_ok = True
        else: continue_ok = False
        try:
            if continue_ok: raise StopIteration
            hf, of = local(hs), local(og[1])
            if not hf or not of: why.append("file missing")
            else:
                # crop when the share image is the 1200x630 shape; a plain hero URL is compared whole
                is_share = subprocess.run(["magick", "identify", "-format", "%w %h", str(of) + "[0]"], capture_output=True, text=True).stdout.split() == ["1200", "630"]
                target = small(of, False) if is_share else small(of, True)
                d = min(diff(small(hf, True, y, z), target) for y in (20, 35, 44, 50, 55, 65, 75, 80) for z in (1.0, 1.25, 1.5))
                if d > 28: why.append(f"share image is not the hero photo (difference {d:.0f})")
        except StopIteration:
            pass
        except Exception as e:
            why.append(f"could not check: {e}")
    if why:
        bad += 1; print("FAIL", rel, "::", "; ".join(why))
print(f"{n - bad} of {n} pages: share image is the hero photo")
sys.exit(1 if bad else 0)
