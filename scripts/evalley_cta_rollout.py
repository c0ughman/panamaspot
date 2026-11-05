"""Put the approved E-Valley Bikes CTA blocks on V2 guides about Boquete or El Valle.

Copy, images and markup come from design/evalley-cta (copy.json + build.py), so the live blocks are
exactly what the user approved in the copy sheet. Four placements per page:
  banner (end of section 1), offer (end of section 3), rail (under "Need to know", which keeps 3 bullets),
  closer (after the photo gallery).
Every link opens WhatsApp with one pre-filled message per region + language, rel="sponsored noopener".
A small click listener sends a GA4 event `evalley_whatsapp_click` {placement, region, page_lang}.

Idempotent: everything it adds sits between evx markers and is stripped before re-inserting.
Refuses to ship a review marked unverified.

Usage:
  python3 scripts/evalley_cta_rollout.py --list          # show which pages qualify
  python3 scripts/evalley_cta_rollout.py [--dry]         # apply (or preview counts)
  python3 scripts/evalley_cta_rollout.py --strip         # remove all blocks again
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "public"
spec = importlib.util.spec_from_file_location("ctabuild", ROOT / "design/evalley-cta/build.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

REGION_BY_CRUMB = {"Boquete": "boquete", "El Valle de Antón": "elvalle"}
# National round-ups whose breadcrumb is El Valle get the El Valle blocks (user decision 2026-11-05).
NATIONAL = set()
M = {k: (f"<!--evx:{k}-->", "<!--/evx-->") for k in ("banner", "offer", "rail", "closer")}
CSS_M = ("<!--evx:css-->", "<!--/evx:css-->")
CSS_FILE = PUB / "css/evalley-cta.css"
CSS_HREF = "/css/evalley-cta.css"
# non-blocking: the blocks never sit in the first screen, so the page paints without waiting for this file
CSS_TAG = ('<link rel="stylesheet" href="' + CSS_HREF + '" media="print" onload="this.media=\'all\';window.dispatchEvent(new Event(\'resize\'))">'
           '<noscript><link rel="stylesheet" href="' + CSS_HREF + '"></noscript>')
JS_M = ("<!--evx:js-->", "<!--/evx:js-->")
TRACK = """<script>document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[data-ev]");if(!a||typeof gtag!=="function")return;var x=a.closest(".evx");gtag("event","evalley_whatsapp_click",{placement:a.getAttribute("data-ev"),region:x&&x.classList.contains("ev-valle")?"el-valle":"boquete",page_lang:document.documentElement.lang||"",link_url:a.href,transport_type:"beacon"});});</script>"""


def crumb(html):
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        for g in (d.get("@graph", [d]) if isinstance(d, dict) else d):
            if isinstance(g, dict) and g.get("@type") == "BreadcrumbList":
                names = [i.get("name") for i in g.get("itemListElement", [])]
                return names[1] if len(names) > 2 else ""
    return ""


def pages():
    out = []
    for f in sorted(PUB.glob("articles/*.html")) + sorted(PUB.glob("es/articles/*.html")):
        rel = str(f.relative_to(PUB))
        html = f.read_text()
        if '<header class="hero">' not in html or rel in NATIONAL:
            continue
        region = REGION_BY_CRUMB.get(crumb(html))
        if region:
            out.append((f, rel, f"{region}-{'es' if rel.startswith('es/') else 'en'}"))
    return out


def minify(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip() + "\n"


def strip(html):
    for a, b in list(M.values()) + [CSS_M, JS_M, ("/* evx:css */", "/* /evx:css */")]:  # last pair: old inline CSS
        html = re.sub(re.escape(a) + r".*?" + re.escape(b) + r"\n?", "", html, flags=re.S)
    return html


def apply(html, key):
    if not B.COPY[key]["closer"].get("review_verified"):
        raise SystemExit(f"{key}: review is not verified; refusing to publish it")
    html = strip(html)
    bl = {k: f"{M[k][0]}{v}{M[k][1]}" for k, v in B.blocks(key).items()}
    html = html.replace("</head>", CSS_M[0] + CSS_TAG + CSS_M[1] + "\n</head>", 1)
    starts = [m.start() for m in re.finditer(r'<section class="sec"', html)]
    if len(starts) < 4:
        raise ValueError("fewer than 4 sections")
    # offer before section 4, banner before section 2 (later position first)
    html = html[:starts[3]] + bl["offer"] + "\n" + html[starts[3]:]
    html = html[:starts[1]] + bl["banner"] + "\n" + html[starts[1]:]
    i = html.index('<div class="know">')
    k = html.index("</ul>", i)
    lis = re.findall(r"<li>.*?</li>", html[i:k], re.S)
    if len(lis) > B.KNOW_MAX:
        ul = html.index("<ul>", i) + len("<ul>")
        html = html[:ul] + "".join(lis[:B.KNOW_MAX]) + html[k:]
    j = html.index("</div>", html.index("</ul>", i)) + len("</div>")
    html = html[:j] + bl["rail"] + "\n" + html[j:]
    g = html.find('<section class="band gband">')
    if g >= 0:
        j = html.index("</section>", g) + len("</section>")
    else:  # no gallery: put the closer right before the footer
        j = html.index("<footer")
    html = html[:j] + bl["closer"] + "\n" + html[j:]
    html = html.replace("</body>", f"{JS_M[0]}{TRACK}{JS_M[1]}\n</body>", 1)
    return html


if __name__ == "__main__":
    args = set(sys.argv[1:])
    ps = pages()
    if "--list" in args:
        for _, rel, key in ps:
            print(f"{key:11} {rel}")
        print(len(ps), "pages")
        sys.exit()
    if "--strip" not in args and "--dry" not in args:
        CSS_FILE.parent.mkdir(exist_ok=True)
        CSS_FILE.write_text("/* E-Valley Bikes partner blocks. Generated by scripts/evalley_cta_rollout.py from design/evalley-cta/build.py; do not edit. */\n" + minify(B.CSS))
    only = [x.split("=", 1)[1] for x in args if x.startswith("--page=")]
    if only:
        ps = [t for t in ps if t[1] in only]
    n = 0
    for f, rel, key in ps:
        html = f.read_text()
        new = strip(html) if "--strip" in args else apply(html, key)
        if new != html:
            n += 1
            if "--dry" not in args:
                f.write_text(new)
    print(("would change" if "--dry" in args else "changed"), n, "of", len(ps), "pages")
