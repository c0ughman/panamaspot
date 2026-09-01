#!/usr/bin/env python3
"""faq-add.py — stage 2, item 8.

The roadmap listed ~12 zero-click questions to answer. Auditing the pages first
found that eleven of them are already answered — the FAQ wording just differs
from the query wording ("¿Cuánto cuesta la entrada?" answers "precio",
"¿A qué hora abre?" answers "horario"). Adding duplicates would have made the
pages worse, so only the genuine gap is filled here.

The gap: "el volcan baru esta activo" — 62 impressions, position 9.8, zero
clicks. Both Barú pages discuss volcanic status in the body but neither
surfaces it as a question, so it never wins the snippet.

Each answer is taken from the page it is added to. Adds to the visible FAQ and
the FAQPage JSON-LD together, so they cannot disagree. Idempotent.
"""
import html as H
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ADDITIONS = {
 "articles/volcan-baru-hike-sunrise-summit-guide": (
   "Is Volcán Barú still active?",
   "Volcán Barú is classified as dormant, not extinct — it last erupted roughly "
   "500 years ago, around 1500 AD. There is no current eruption risk to hikers, "
   "and the summit trail is open year-round. The real hazards on the mountain are "
   "cold and exposure at 3,474 m, not volcanic activity."),
 "es/articles/volcan-baru-como-subir-cima-panama": (
   "¿El Volcán Barú está activo?",
   "El Barú es un estratovolcán potencialmente activo, no extinto. Su última "
   "erupción significativa fue alrededor del año 1500 d.C. No hay riesgo eruptivo "
   "actual para quienes suben, y el sendero está abierto todo el año. El peligro "
   "real en la montaña es el frío y la exposición a 3.474 m, no la actividad volcánica."),
}


def add_visible(html, q, a):
    """Insert one collapsed FAQ item at the top of the existing FAQ list."""
    m = re.search(r'<div class="faq"[^>]*>', html)
    if not m:
        return html, False
    item = (f'<div class="faq-item"><button type="button" class="faq-q" '
            f'aria-expanded="false">{H.escape(q)}</button>'
            f'<div class="faq-a">{H.escape(a)}</div></div>')
    return html[:m.end()] + item + html[m.end():], True


def add_schema(html, q, a):
    """Add the same Q&A to the FAQPage JSON-LD block."""
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        raw = m.group(1)
        if '"FAQPage"' not in raw:
            continue
        data = json.loads(raw)
        entities = data.get("mainEntity", [])
        if any(e.get("name") == q for e in entities):
            return html, False
        entities.insert(0, {"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}})
        data["mainEntity"] = entities
        new = json.dumps(data, ensure_ascii=False)
        return html[:m.start(1)] + new + html[m.end(1):], True
    return html, False


def main():
    for path, (q, a) in ADDITIONS.items():
        p = ROOT / "public" / (path + ".html")
        h = p.read_text(encoding="utf8")
        if q in h:
            print(f"  already present, skipping  {path}")
            continue
        h, ok_v = add_visible(h, q, a)
        h, ok_s = add_schema(h, q, a)
        if not (ok_v and ok_s):
            print(f"  FAILED (visible={ok_v} schema={ok_s})  {path}")
            continue
        p.write_text(h, encoding="utf8")
        print(f"  added FAQ + schema  {path}")
        print(f"      Q: {q}")


if __name__ == "__main__":
    main()
