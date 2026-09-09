#!/usr/bin/env python3
"""place-las-nubes-hero.py — put the Las Nubes shrimp photograph on the hero of
Dónde comer en El Valle de Antón.

Supplied by the site owner, shot by Gina B and published on TripAdvisor. It is
not a Commons or Pexels file, so it does not go through commons-verified.json:
it is converted to a local webp under /images/el-valle/ and credited by hand in
scripts/image-artists.json, the same route the site's own photographs take.

    python3 scripts/place-las-nubes-hero.py "tripadvisor-images/el valle/las-nubes-shrimp.jpg"

Then re-run the pipeline from elvalle-image-pass.py.
"""
import sys, json, shutil, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tripadvisor-images/el valle/las-nubes-shrimp.jpg"
KEY = "/images/el-valle/lasnubes-camarones.webp"
OUT = ROOT / KEY.lstrip("/")
PAGE = "public/es/articles/donde-comer-en-el-valle-de-anton.html"

if not SRC.exists():
    raise SystemExit(f"not found: {SRC}\nSave the photo there first.")

# The hero renders in a wide letterbox; the source is tall portrait, so the crop
# is driven from the top third where the shrimp and the pasta sit.
OUT.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["magick", str(SRC), "-resize", "1600x", "-quality", "82",
                str(OUT)], check=True)
w, h = subprocess.run(["magick", "identify", "-format", "%w %h", str(OUT)],
                      capture_output=True, text=True, check=True).stdout.split()
print(f"wrote {KEY} at {w}x{h}")

CAP = ("Camarones a la plancha sobre pasta en Restaurante Las Nubes — el tramo "
       "alto de la carta de El Valle.")
DESC = "Camarones grandes a la plancha con perejil, servidos sobre pasta en Las Nubes."

def edit(path, fn):
    p = ROOT / path
    d = json.loads(p.read_text(encoding="utf-8"))
    fn(d)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def plan(d):
    # object-position keeps the plate in frame when the hero letterboxes a
    # portrait source; without it the crop lands on the tabletop.
    d[PAGE]["hero"] = [KEY, CAP, "center 38%"]
edit("scripts/elvalle-image-plan.json", plan)

def facts(d):
    d[KEY] = {"label": "Camarones a la plancha · Restaurante Las Nubes",
              "label_en": None, "desc": DESC, "desc_en": None,
              "place": "Restaurante Las Nubes", "locality": "El Valle de Antón",
              "region": "Coclé", "country": "PA"}
edit("scripts/elvalle-image-facts.json", facts)

# image-artists.json is keyed by Commons URL and only consulted for files that
# came through image-selections.json. A photograph we host ourselves but did not
# take needs image-thirdparty.json, which enrich-images.py checks before the
# fallback that would otherwise credit anything under /images/ to PanamaSpot.
def artists(d):
    d[KEY] = {"name": "Gina B", "credit": "Gina B / TripAdvisor"}
tp = ROOT / "scripts/image-thirdparty.json"
if not tp.exists():
    tp.write_text("{}\n", encoding="utf-8")
edit("scripts/image-thirdparty.json", artists)

print("plan, facts and credit updated — now run the pipeline")
