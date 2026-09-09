#!/usr/bin/env python3
"""
meta-language-check.py — fail the site if an article talks about search engines,
the competitive landscape, or the content brief instead of talking about Panama.

The 2026-09 batch shipped with 29 sentences naming the SERP ("Ningún competidor
en el SERP explica esto"), the People Also Ask box, and "los demás resultados de
búsqueda", plus 60-odd more positioning each page against its competitors. A
traveller reading that is being told about our marketing, not about the country.
This catches the whole family so it cannot come back in the next batch.

Two severities:

  HARD   — never acceptable in anything a reader or a crawler sees. Exits 1.
  SOFT   — the "most guides skip this" register. It IS the house voice and is
           allowed, but a page that leans on it three times reads as a broken
           record, so the check caps it at 2 per page.

Scope: every string a human or Google actually reads — body prose, <title>,
meta and og descriptions, alt text, figcaptions, and the string VALUES inside
JSON-LD. Property names inside JSON-LD are skipped on purpose: ImageObject
carries a legitimate `keywords` field and that is structured data, not copy.

    python3 scripts/meta-language-check.py           # report + exit code
    python3 scripts/meta-language-check.py --list    # every hit, with context
"""
import re, sys, glob, json, html, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent

HARD = {
 "SERP / results page":
   r'\bSERPs?\b|p[áa]gina de resultados|resultados de b[úu]squeda|search results?\b'
   r'|primera p[áa]gina de Google|first page of Google',
 "People Also Ask":
   r'People Also Ask|\bPAA\b|otras preguntas de los usuarios|preguntas relacionadas',
 "search engine named":
   r'motor(?:es)? de b[úu]squeda|search engines?\b|buscador(?:es)?\b',
 "searches as a signal":
   r'b[úu]squedas relacionadas|b[úu]squedas de Google|La b[úu]squeda de "'
   r'|domina cada b[úu]squeda|b[úu]squedas m[áa]s frecuentes|t[ée]rminos de b[úu]squeda'
   r'|search volume|search intent|intenci[óo]n de b[úu]squeda|lo que la gente busca',
 "SEO craft":
   r'\bSEO\b|posicionamiento|posicionar|rankear|indexaci[óo]n|featured snippet'
   r'|fragmento destacado|tr[áa]fico org[áa]nico|organic traffic|palabras? clave'
   r'|\bkeywords?\b|long[- ]tail keyword|domain authority|autoridad de dominio|backlink',
 "competitors":
   r'competidor\w*|\bcompetitors\b|(?<!price[- ])(?<!cost[- ])\bcompetitor\b',
 "on-page furniture":
   r'meta ?descripci[óo]n|\bmeta description\b|title tag|\balt text\b|texto alternativo'
   r'|schema markup|rich snippet',
 "content brief":
   r'seg[úu]n el brief|content brief|topic cluster|pillar page|p[áa]gina pilar|content gap'
   r'|vac[íi]o de contenido|buyer persona|audiencia objetivo|target audience|p[úu]blico objetivo'
   r'|word count|conteo de palabras|\bE-?E-?A-?T\b',
 "assistant artefacts":
   r'as an AI|como (?:un )?modelo de lenguaje|language model'
   r'|(?:^|[.!?]\s+)Certainly[ ,!]'
   r'|Aqu[íi] tienes (?:un|el|la) (?:art[íi]culo|gu[íi]a)|As requested|seg[úu]n lo solicitado',
 "placeholders":
   r'\bTODO\b|\bTBD\b|lorem ipsum|\[insert|\[insertar|\bPLACEHOLDER\b|\{\{',
}

# These must match case exactly: TODO is a placeholder, "todo" is the Spanish
# word for "everything" and appears on nearly every page; likewise "Certainly,"
# as an assistant opener vs "almost certainly," in ordinary prose.
CASE_SENSITIVE = {"assistant artefacts", "placeholders"}

# Allowed, but not more than twice on one page.
SOFT = (r'most guides|almost no guide|almost every guide|every guide|other guides'
        r'|no other guide|guides? on the internet|la mayor[íi]a de las gu[íi]as'
        r'|casi ninguna gu[íi]a|ninguna gu[íi]a|casi todas las gu[íi]as|otras gu[íi]as'
        r'|las gu[íi]as (?:omiten|dispersan|listan|mencionan|raramente)|gu[íi]as (?:online|en internet)')
SOFT_MAX = 2

SCRIPT = re.compile(r'<script.*?</script>|<style.*?</style>', re.S)


def surfaces(path):
    """(where, text) for every string a reader or a crawler sees."""
    s = pathlib.Path(path).read_text(encoding='utf-8', errors='replace')
    out = []
    a = re.search(r'(?s)<article\b.*?</article>', s)
    if a:
        body = re.sub(r'(?s)<!--EVB-CTA:[a-z]+-->.*?<!--/EVB-CTA:[a-z]+-->', ' ', a.group(0))
        out.append(('prose', html.unescape(re.sub(r'<[^>]+>', ' ', body))))
    for pat, label in ((r'<title>(.*?)</title>', 'title'),
                       (r'<meta content="([^"]*)" name="description"/>', 'meta-desc'),
                       (r'<meta content="([^"]*)" property="og:description"/>', 'og-desc'),
                       (r'<img[^>]*\balt="([^"]*)"', 'alt'),
                       (r'<figcaption>(.*?)</figcaption>', 'caption')):
        for m in re.finditer(pat, s, re.S):
            out.append((label, html.unescape(re.sub(r'<[^>]+>', ' ', m.group(1)))))
    for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if isinstance(v, str) and k in ('name', 'description', 'caption',
                                                    'text', 'headline', 'abstract'):
                        out.append(('schema:' + k, v))
                    else:
                        walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(d)
    return out


def main():
    show = "--list" in sys.argv
    files = sorted(glob.glob(str(ROOT / "public/articles/*.html")) +
                   glob.glob(str(ROOT / "public/es/articles/*.html")))
    hard = collections.defaultdict(list)
    soft = collections.Counter()
    soft_re = re.compile(SOFT)

    for f in files:
        slug = pathlib.Path(f).stem
        for where, text in surfaces(f):
            t = re.sub(r'\s+', ' ', text)
            for label, pat in HARD.items():
                flags = 0 if label in CASE_SENSITIVE else re.I
                for m in re.finditer(pat, t, flags):
                    hard[label].append((slug, where, m.group(0),
                                        t[max(0, m.start() - 90):m.end() + 90].strip()))
            if where == 'prose':
                soft[slug] += len(soft_re.findall(t))

    print(f"scanned {len(files)} article pages\n")
    print("HARD — never acceptable")
    total = 0
    for label in HARD:
        seen, uniq = set(), []
        for slug, where, mt, ctx in hard[label]:
            k = (slug, mt, ctx[:60])
            if k not in seen:
                seen.add(k); uniq.append((slug, where, mt, ctx))
        total += len(uniq)
        mark = "  " if not uniq else "!!"
        print(f"  {mark} {label:24s} {len(uniq)}")
        if show:
            for slug, where, mt, ctx in uniq:
                print(f"        [{where}] {slug} «{mt}»\n           …{ctx[:150]}…")

    over = {s: n for s, n in soft.items() if n > SOFT_MAX}
    print(f"\nSOFT — house voice, capped at {SOFT_MAX} per page")
    print(f"     {sum(soft.values())} instances on {len([s for s in soft if soft[s]])} pages;"
          f" over the cap: {len(over)}")
    for s, n in sorted(over.items(), key=lambda kv: -kv[1]):
        print(f"  !! {s} — {n}")

    if total or over:
        print(f"\nFAIL — {total} hard hits, {len(over)} pages over the soft cap")
        return 1
    print("\nPASS — no page talks about search results, competitors or the brief")
    return 0


if __name__ == "__main__":
    sys.exit(main())
