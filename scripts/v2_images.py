#!/usr/bin/env python3
"""
v2_images.py - self-host and right-size every photo on the V2 guide pages.

Each <img> gets a role from where it sits, and each role gets one file sized for how it is shown:
  hero    960/1280/1920 wide, cropped to at most 4:3 around the page's focus (CSS: center 44%)
  wide    in-article figure: 16:9, 1280 wide (the frame is a 16:9 cover crop already)
  gallery photo band: fits in 1400x1400, no crop
  tile    "More guides" bento: fits in 900x900
  stamp   "Read next" stamp: 4:5, 360x450
  card    footer destination card: 16:13, 640x520
  share   og:image: 1200x630 JPEG from the hero, at the same focus
Files land in public/images/v2/<name>-<role>[-<w>].webp, named after the photo (not a hash), shared by
every page that uses the same photo. Pexels/Booqable hotlinks are downloaded once into a cache dir.

    python3 scripts/v2_images.py <download_dir> [--dry]
    python3 scripts/v2_images.py <download_dir> --page=articles/x.html [--page=...]   # only these pages; photos already in /images/v2 are left alone
"""
import re, sys, json, html, time, threading, hashlib, pathlib, subprocess, urllib.request, urllib.error, urllib.parse, concurrent.futures, collections
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
OUT = PUB / "images/v2"
SITE = "https://panamaspot.com"
DL = pathlib.Path(sys.argv[1])
DRY = "--dry" in sys.argv
ONLY = {a.split("=", 1)[1] for a in sys.argv if a.startswith("--page=")}
Q = 76

ROLE_OF = [("hero-img", "hero"), ("stamp", "stamp"), ("fc", "card"), ("fig", "wide"), ("gal", "gallery"), ("bt", "tile")]


def slug(s, n=7):
    s = urllib.parse.unquote(s)
    s = s.replace("_2C", ",").replace("_28", "(").replace("_29", ")").replace("__", "_")
    s = s.translate(str.maketrans("áéíóúñüÁÉÍÓÚÑÜ", "aeiounuAEIOUNU"))
    w = [x for x in re.split(r"[^a-zA-Z0-9]+", s.lower()) if x and x not in ("jpg", "jpeg", "webp", "png", "file")]
    return "-".join(w[:n]) or "photo"


def family(src):
    """Group key for one photo across its width variants and page folders."""
    u = urllib.parse.urlparse(src if "://" in src else SITE + src)
    if "pexels" in u.netloc:
        return "pexels-" + re.search(r"/photos/(\d+)", u.path).group(1)
    if u.netloc not in ("panamaspot.com", ""):
        if "wikimedia" in u.netloc:  # one photo at any width: Wikimedia file names are unique
            return "ext-" + hashlib.md5(re.sub(r"^\d+px-", "", pathlib.PurePosixPath(u.path).name).encode()).hexdigest()[:8]
        return "ext-" + hashlib.md5(u.path.encode()).hexdigest()[:8]  # other hosts reuse names like upload.jpeg
    name = pathlib.PurePosixPath(u.path).name
    if "/images/guides/" in u.path:
        name = re.sub(r"^[0-9a-f]{8}-", "", name)
        name = re.sub(r"^\d+px-", "", name)
        return "g:" + name
    return "l:" + u.path


class ImgScan(HTMLParser):
    """Offsets of every <img> plus the classes of its open ancestors."""
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.lines = [0]
        for line in src.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))
        self.stack, self.imgs = [], []
        self.feed(src)

    def off(self):
        l, c = self.getpos()
        return self.lines[l - 1] + c

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            self.imgs.append((self.off(), a, [c for _, c in self.stack]))
            return
        if tag in ("br", "meta", "link", "source", "input", "hr", "wbr"):
            return
        self.stack.append((tag, a.get("class") or ""))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def role_for(attrs, anc):
    cls = (attrs.get("class") or "").split()
    if "hero-img" in cls: return "hero"
    for c in reversed(anc):
        cs = c.split()
        for key, role in ROLE_OF[1:]:
            if key in cs: return role
    return "gallery"


def dims(f):
    out = subprocess.run(["magick", "identify", "-format", "%w %h", str(f) + "[0]"], capture_output=True, text=True).stdout.split()
    return int(out[0]), int(out[1])


WIKI_LOCK = threading.Lock()   # Wikimedia throttles parallel or rapid downloads: one at a time, with a pause


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 1000: return dest
    req = urllib.request.Request(url, headers={"User-Agent": "PanamaSpotImageCopy/1.0 (https://panamaspot.com)"})
    wiki = "wikimedia.org" in url
    for wait in (0, 6, 20, 45):
        if wait: time.sleep(wait)
        try:
            if wiki:
                with WIKI_LOCK:
                    time.sleep(1.2)
                    with urllib.request.urlopen(req, timeout=60) as r: data = r.read()
            else:
                with urllib.request.urlopen(req, timeout=60) as r: data = r.read()
            dest.write_bytes(data)
            return dest
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500: raise
    raise RuntimeError("gave up on " + url)


def fetch_wikimedia(srcs, dest):
    """The largest standard size Wikimedia will give for this photo; if none comes, the size the page already uses."""
    if dest.exists() and dest.stat().st_size > 1000: return dest
    thumb = next((u for u in sorted(srcs) if "/thumb/" in u), None)
    tries = [re.sub(r"/\d+px-", f"/{w}px-", thumb) for w in (1920, 1280)] if thumb else []
    for u in tries + sorted(srcs, key=lambda x: -int((re.search(r"/(\d+)px-", x) or [0, 0])[1])):
        try:
            return fetch(u, dest)
        except (urllib.error.HTTPError, RuntimeError):
            continue
    raise RuntimeError("no size available for " + sorted(srcs)[0])


def main():
    DL.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pages = [f for f in sorted(list((PUB / "articles").glob("*.html")) + list((PUB / "es/articles").glob("*.html")))
             if '<header class="hero">' in f.read_text(encoding="utf-8")
             and (not ONLY or str(f.relative_to(PUB)) in ONLY)]
    uses = []                                   # (page, offset, attrs, role, family)
    fam_srcs = collections.defaultdict(set)
    fam_alt = {}
    fam_focus = {}
    for f in pages:
        s = f.read_text(encoding="utf-8")
        for off, a, anc in ImgScan(s).imgs:
            if ONLY and "/images/v2/" in a.get("src", ""): continue
            srcs = [a.get("src", "")] + [x.strip().split(" ")[0] for x in (a.get("srcset") or "").split(",") if x.strip()]
            fam = family(a.get("src", ""))
            role = role_for(a, anc)
            uses.append((f, off, a, role, fam))
            if role == "hero":
                fm = re.search(r"object-position:\s*center\s+(\d+)%", a.get("style") or "")
                fam_focus[fam] = int(fm.group(1)) / 100 if fm else .44
            for x in srcs:
                if x: fam_srcs[fam].add(html.unescape(x))
            if a.get("alt"): fam_alt.setdefault(fam, a["alt"])
    # masters: the largest local variant, or a download
    masters, names = {}, {}
    def master_of(fam):
        srcs = fam_srcs[fam]
        if fam.startswith("pexels-"):
            pid = fam.split("-")[1]
            return fetch(f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=2400", DL / f"{fam}.jpg")
        if fam.startswith("ext-"):
            u = sorted(srcs)[0]
            dest = DL / (fam + pathlib.PurePosixPath(urllib.parse.urlparse(u).path).suffix)
            return fetch_wikimedia(srcs, dest) if "wikimedia" in u else fetch(u, dest)
        best, bw = None, -1
        for u in srcs:
            p = PUB / urllib.parse.unquote(urllib.parse.urlparse(u if "://" in u else SITE + u).path).lstrip("/")
            if p.exists():
                w = dims(p)[0]
                if w > bw: best, bw = p, w
        if fam.startswith("g:"):        # the same photo may sit in other page folders at a larger width
            base = fam[2:]
            for p in PUB.glob(f"images/guides/*/*{base}"):
                if re.sub(r"^\d+px-", "", re.sub(r"^[0-9a-f]{8}-", "", p.name)) == base:
                    w = dims(p)[0]
                    if w > bw: best, bw = p, w
        return best
    with concurrent.futures.ThreadPoolExecutor(3) as ex:
        for fam, m in zip(list(fam_srcs), ex.map(master_of, list(fam_srcs))):
            masters[fam] = m
    missing = [f for f, m in masters.items() if m is None]
    assert not missing, missing
    taken = {}
    for fam, m in masters.items():
        if fam.startswith(("pexels-", "ext-")):
            n = slug(fam_alt.get(fam, fam), 6) + "-" + fam.split("-")[-1][:8]
        else:
            n = slug(pathlib.Path(fam.split(":", 1)[1]).stem, 7)
        h = hashlib.md5(m.read_bytes()).hexdigest()[:6]
        if n in taken and taken[n] != h: n = f"{n}-{h}"
        taken[n] = h
        names[fam] = n
    # jobs
    jobs = {}
    def want(fam, role, w=None):
        n = names[fam]
        fn = f"{n}-{role}" + (f"-{w}" if w else "") + ".webp"
        jobs[fn] = (fam, role, w)
        return "/images/v2/" + fn
    plan = []
    for f, off, a, role, fam in uses:
        if role == "hero":
            plan.append((f, off, a, role, fam, {w: want(fam, "hero", w) for w in (960, 1280, 1920)}))
        else:
            plan.append((f, off, a, role, fam, want(fam, role)))

    def run(fn):
        fam, role, w = jobs[fn]
        out = OUT / fn
        if out.exists() and role != "hero": return fn, dims(out)
        src = str(masters[fam]) + "[0]"
        W, H = dims(masters[fam])
        def crop(ar, fy=.5):
            if W / H < ar:                       # too tall: crop height
                ch = int(W / ar); y = int(max(0, min(H - ch, H * fy - ch / 2)))
                return ["-crop", f"{W}x{ch}+0+{y}", "+repage"]
            cw = int(H * ar); x = (W - cw) // 2
            return ["-crop", f"{cw}x{H}+{x}+0", "+repage"]
        if role == "hero":
            ops = (crop(4 / 3, fam_focus.get(fam, .44)) if W / H < 4 / 3 else []) + ["-resize", f"{w}x>"]
        elif role == "wide":
            ops = crop(16 / 9) + ["-resize", "1280x>"]
        elif role == "gallery":
            ops = ["-resize", "1400x1400>"]
        elif role == "tile":
            ops = ["-resize", "900x900>"]
        elif role == "stamp":
            ops = crop(4 / 5) + ["-resize", "360x450>"]
        elif role == "card":
            ops = crop(16 / 13) + ["-resize", "640x520>"]
        if not DRY:
            subprocess.run(["magick", src, "-auto-orient", *ops, "-strip", "-quality", str(Q), "-define", "webp:method=6", str(out)], check=True)
        return fn, dims(out) if out.exists() else (0, 0)
    out_dims = {}
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        for fn, d in ex.map(run, sorted(jobs)):
            out_dims[fn] = d
    # share images: hero master, 1200x630 at the hero focus
    share = {}
    for f, off, a, role, fam, new in plan:
        if role != "hero": continue
        pslug = f.stem
        dest = PUB / "images/social" / f"{pslug}-share.jpg"
        W, H = dims(masters[fam])
        ar = 1200 / 630
        if W / H < ar:
            fy = fam_focus.get(fam, .44)
            ch = int(W / ar); y = int(max(0, min(H - ch, H * fy - ch / 2))); cr = f"{W}x{ch}+0+{y}"
        else:
            cw = int(H * ar); cr = f"{cw}x{H}+{(W - cw) // 2}+0"
        if not DRY:
            subprocess.run(["magick", str(masters[fam]) + "[0]", "-auto-orient", "-crop", cr, "+repage", "-resize", "1200x630!",
                            "-strip", "-quality", "82", "-interlace", "Plane", str(dest)], check=True)
        share[f] = ("/images/social/" + dest.name, a.get("alt", ""))
    # rewrite pages
    url_map = {}                                 # every old URL form -> new path, for schema/meta strings
    by_page = collections.defaultdict(list)
    for item in plan: by_page[item[0]].append(item)
    pri = {"hero": 0, "wide": 1, "gallery": 2, "tile": 3, "card": 4, "stamp": 5}
    for f, items in by_page.items():
        s = f.read_text(encoding="utf-8")
        page_map = {}
        for (pf, off, a, role, fam, new) in sorted(items, key=lambda x: -x[1]):
            end = s.index(">", off) + 1
            tag = s[off:end]
            if role == "hero":
                big = new[1920]; ws = sorted(new)
                srcset = ", ".join(f"{SITE}{new[w]} {out_dims[new[w].split('/')[-1]][0]}w" for w in ws)
                if ' srcset="' in tag:
                    tag2 = re.sub(r'\ssrcset="[^"]*"', f' srcset="{srcset}"', tag)
                else:
                    tag2 = tag.replace("<img ", f'<img srcset="{srcset}" sizes="100vw" ', 1)
                tag2 = re.sub(r'\ssrc="[^"]*"', f' src="{SITE}{new[1280]}"', tag2)
                d = out_dims[new[1280].split("/")[-1]]
                main_new = new[1920]
            else:
                tag2 = re.sub(r'\ssrc="[^"]*"', f' src="{SITE}{new}"', tag)
                tag2 = re.sub(r'\ssrcset="[^"]*"', "", tag2)
                d = out_dims[new.split("/")[-1]]
                main_new = new
            tag2 = re.sub(r'\s(width|height)="[^"]*"', "", tag2)
            tag2 = tag2[:-2] + f' width="{d[0]}" height="{d[1]}"/>' if tag2.endswith("/>") else tag2[:-1] + f' width="{d[0]}" height="{d[1]}">'
            s = s[:off] + tag2 + s[end:]
            for x in fam_srcs[fam]:
                cur = page_map.get(x)
                if cur is None or pri[role] < cur[1]:
                    page_map[x] = (SITE + main_new, pri[role])
        # preload = hero
        hero = [it for it in items if it[3] == "hero"][0]
        hn = hero[5]
        s = re.sub(r'<link rel="preload" as="image" href="[^"]*"(?: imagesrcset="[^"]*")?',
                   f'<link rel="preload" as="image" href="{SITE}{hn[1280]}" imagesrcset="' +
                   ", ".join(f"{SITE}{hn[w]} {out_dims[hn[w].split('/')[-1]][0]}w" for w in sorted(hn)) + '"', s)
        # remaining references (JSON-LD, meta): old URL strings -> new
        for old, (newu, _) in sorted(page_map.items(), key=lambda kv: -len(kv[0])):
            olds = {old, old.replace("&", "&amp;")}
            if old.startswith("/"): olds |= {SITE + old}
            if old.startswith(SITE): olds |= {old[len(SITE):]}
            for o in sorted(olds, key=len, reverse=True):
                s = s.replace(f'"{o}"', f'"{newu}"')
        # any other size of a moved photo still named in schema or metadata
        def moved(m):
            fam = family(html.unescape(m[0]))
            return next((nu for o, (nu, _) in page_map.items() if family(o) == fam), m[0])
        s = re.sub(r'https://(?:images\.pexels\.com/photos|upload\.wikimedia\.org/wikipedia)/[^"\s\\]+', moved, s)
        # share image
        sp, salt = share[f]
        surl = SITE + sp
        s = re.sub(r'<meta content="[^"]*" property="og:image"/>', f'<meta content="{surl}" property="og:image"/>', s)
        s = re.sub(r'<meta content="[^"]*" property="og:image:(?:width|height|alt|type)"/>', "", s)
        s = s.replace(f'<meta content="{surl}" property="og:image"/>',
                      f'<meta content="{surl}" property="og:image"/><meta content="image/jpeg" property="og:image:type"/>'
                      f'<meta content="1200" property="og:image:width"/><meta content="630" property="og:image:height"/>'
                      f'<meta content="{html.escape(html.unescape(salt))}" property="og:image:alt"/>', 1)
        s = re.sub(r'<meta content="[^"]*" name="twitter:image"/>', f'<meta content="{surl}" name="twitter:image"/>', s)
        if 'name="twitter:image:alt"' not in s:
            s = s.replace(f'<meta content="{surl}" name="twitter:image"/>', f'<meta content="{surl}" name="twitter:image"/><meta content="{html.escape(html.unescape(salt))}" name="twitter:image:alt"/>', 1)
        if not DRY:
            f.write_text(s, encoding="utf-8")
        url_map[f] = page_map
    tot_new = sum((OUT / fn).stat().st_size for fn in jobs if (OUT / fn).exists())
    print(f"{len(pages)} pages, {len(uses)} <img>, {len(masters)} photos, {len(jobs)} files written ({tot_new / 1e6:.1f} MB), {len(share)} share images")
    json.dump({"names": names, "masters": {k: str(v) for k, v in masters.items()}}, open(DL / "map.json", "w"), indent=1)


if __name__ == "__main__":
    main()
