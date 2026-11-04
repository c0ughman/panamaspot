"""Build the editable copy sheet: the real E-Valley CTA blocks (same markup + CSS as build.py, real photos),
one block per row, every text editable, WhatsApp messages listed separately under each version.

Writes <OUT>/evalley-cta-copy.html plus <OUT>/img/* and <OUT>/fonts/* to publish alongside it.
Usage: python3 design/evalley-cta/make_sheet.py <out_dir>
"""
import base64
import copy as cp
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = Path(sys.argv[1]).resolve()
(OUT / "img").mkdir(parents=True, exist_ok=True)
(OUT / "fonts").mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("ctabuild", HERE / "build.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

ORDER = [("boquete-en", "Boquete · English"), ("boquete-es", "Boquete · Español"),
         ("elvalle-en", "El Valle · English"), ("elvalle-es", "El Valle · Español")]
BLOCKS = [("banner", "1 · Banner", "End of the first section · article column, 760 px"),
          ("offer", "2 · Three rides", "End of the third section · article column, 760 px"),
          ("rail", "3 · Right column card", "Under “Need to know” · right column, 280 px"),
          ("closer", "4 · Closer", "After the photo gallery · full width")]
WA_FIELDS = [("wa_msg", "Every button, card and photo")]

tokens = {}


def tokenize(obj, key, path=""):
    if isinstance(obj, dict):
        return {k: tokenize(v, key, f"{path}.{k}" if path else k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [tokenize(v, key, f"{path}.{i}") for i, v in enumerate(obj)]
    if isinstance(obj, str) and obj and not path.endswith("wa_msg") and path not in ("wa_number", "label"):
        t = f"ZZK{len(tokens)}ZZ"
        tokens[t] = (key, path, obj)
        return t
    return obj


images = {}


def localize(src):
    """Inline a site image as a data: URI, resized for the sheet (relative files did not render in the viewer)."""
    if src not in images:
        dst = OUT / "img" / (Path(src).stem + ".webp")
        subprocess.run(["magick", str(ROOT / "public" / src.lstrip("/")), "-resize", "1000x1000>", "-quality", "72", str(dst)], check=True)
        images[src] = "data:image/webp;base64," + base64.b64encode(dst.read_bytes()).decode()
    return images[src]


rows = []
base_copy = json.loads((HERE / "copy.json").read_text())
for key, label in ORDER:
    B.COPY[key] = tokenize(cp.deepcopy(B.COPY[key]), key)
    bl = B.blocks(key)
    out = []
    for bid, bname, where in BLOCKS:
        h = bl[bid]
        h = re.sub(r'\s(?:href|target|rel|data-ev|tabindex)="[^"]*"', "", h)  # links are inert in the sheet
        h = re.sub(r'src="(/images/[^"]+)"', lambda m: f'src="{localize(m.group(1))}"', h)
        h = h.replace('loading="lazy"', 'loading="eager"')
        # tokens inside tags (aria-label etc.) -> plain text; in text -> editable spans
        h = re.sub(r"<[^>]+>", lambda m: re.sub(r"ZZK\d+ZZ", lambda t: tokens[t.group(0)][2], m.group(0)), h)
        h = re.sub(r"ZZK\d+ZZ", lambda t: f'<span class="ek" data-v="{tokens[t.group(0)][0]}" data-k="{tokens[t.group(0)][1]}" contenteditable="plaintext-only" spellcheck="true"></span>', h)
        h = re.sub(r'(<span class="ev-av" aria-hidden="true">)[^<]*(</span>)', lambda m: m.group(1) + base_copy[key]["closer"]["review_name"][:1].upper() + m.group(2), h)
        out.append(f'<div class="row r-{bid}"><div class="row-h"><h3>{bname}</h3><span>{where}</span></div><div class="stage s-{bid}">{h}</div></div>')
    wa = "".join(f'<li><span class="wl">{n}</span><span class="ek wm" data-v="{key}" data-k="{p}" contenteditable="plaintext-only" spellcheck="true"></span><a class="wt" data-wa="{key}|{p}" target="_blank" rel="noopener">Test ↗</a></li>' for p, n in WA_FIELDS)
    rid = key
    rows.append(f'''<section class="ver" id="{rid}"><div class="ver-h"><h2>{label}</h2><span>WhatsApp +{B.COPY[key]["wa_number"]}</span></div>
{"".join(out)}
<div class="row"><div class="row-h"><h3>WhatsApp message</h3><span>The one pre-filled text that opens from every button, card and photo in this version</span></div><ul class="walist">{wa}</ul></div>
<div class="notes"><label for="n-{rid}">Notes for Claude · {label}</label><textarea id="n-{rid}" data-notes="{key}" placeholder="Anything that isn't a direct text change: tone, what to cut, what to add…"></textarea></div>
</section>''')

for f in ["GildaC-450.woff2", "GildaC-550.woff2", "GildaC-650.woff2", "GildaC-700.woff2"]:
    shutil.copy(ROOT / "public/fonts" / f, OUT / "fonts" / f)

base = json.loads((HERE / "copy.json").read_text())
tpl = (HERE / "sheet_template.html").read_text()
for f in ["GildaC-450", "GildaC-550", "GildaC-650", "GildaC-700"]:
    tpl = tpl.replace(f'url("fonts/{f}.woff2")', f'url("data:font/woff2;base64,{base64.b64encode((OUT / "fonts" / (f + ".woff2")).read_bytes()).decode()}")')
page = (tpl.replace("/*__CTA_CSS__*/", B.CSS)
           .replace("<!--__ROWS__-->", "\n".join(rows))
           .replace("__COPY__", json.dumps(base, ensure_ascii=False).replace("</", "<\\/")))
(OUT / "evalley-cta-copy.html").write_text(page)
print("wrote", OUT / "evalley-cta-copy.html", "|", len(images), "images,", len(tokens), "editable fields")
