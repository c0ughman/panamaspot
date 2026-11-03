#!/usr/bin/env python3
"""
interlink_v2.py - natural in-text links from the older guides to the V2 guides.

    python3 scripts/interlink_v2.py prepare <outdir> [n_chunks]   # score pairs, write agent task files
    python3 scripts/interlink_v2.py apply <outdir> [--dry]         # validate agent decisions, edit pages
    python3 scripts/interlink_v2.py strip                          # remove the bolted-on "New guides" lists

Relevance of (old page -> V2 page), same language only:
    0.45 x text similarity (TF-IDF cosine of the article text, normalised per target)
  + 0.25 x same region (breadcrumb hub; 0.5 when the target is nationwide)
  + 0.30 x the old page's prose already mentions the target's subject (curated phrases)
Pairs scoring >= MIN_SCORE are kept: up to 3 per old page by score, then topped up so every
target has at least 2 sources when relevant ones exist. Agents then decide where (and whether)
each link fits; `apply` accepts only edits whose anchor text exists verbatim.
"""
import re, sys, json, math, html, hashlib, pathlib, collections, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
HUBS = {"articles/boquete", "articles/el-valle-de-anton", "articles/panama-city", "articles/bocas-del-toro",
        "es/articles/boquete", "es/articles/el-valle-de-anton", "es/articles/panama-city"}
MIN_SCORE, PER_SOURCE, MIN_PER_TARGET, MAX_PER_SOURCE = 0.50, 3, 2, 4

# What counts as "the old page already talks about this". Accent- and case-insensitive.
MENTIONS = {
 "articles/best-waterfalls-in-panama-where-to-see-several": ["waterfalls in panama", "panama's waterfalls", "waterfalls around the country", "best waterfalls", "waterfall"],
 "articles/birding-el-valle-de-anton-trails-lodges-season": ["birding", "birdwatching", "bird-watching", "birders", "canopy lodge", "birds"],
 "articles/boquete-flower-and-coffee-fair-visitor-guide": ["flower and coffee fair", "flower fair", "feria de las flores", "coffee and flowers festival", "flowers and coffee", "flower festival", "the feria"],
 "articles/boquete-to-bocas-del-toro-shuttle-bus-timing": ["bocas del toro", "to bocas", "from boquete", "shuttle"],
 "articles/boquete-with-kids-family-guide": ["with kids", "children", "families", "family"],
 "articles/buying-property-in-panama-as-a-foreigner": ["buying property", "buy property", "real estate", "buy a house", "buying a home", "residential property"],
 "articles/chorro-las-mozas-swimming-falls-el-valle": ["las mozas"],
 "articles/contadora-ferry-from-panama-city": ["contadora", "pearl islands", "ferry"],
 "articles/diving-in-panama": ["diving", "scuba", "dive", "coiba", "portobelo", "snorkel"],
 "articles/el-pianista-trail-boquete": ["pianista"],
 "articles/el-valle-de-anton-hot-springs-prices-hours-getting-there": ["hot springs", "thermal pools", "pozos termales", "thermal", "mud bath", "mud mask"],
 "articles/geisha-coffee-boquete-where-to-taste": ["geisha", "gesha"],
 "articles/healthcare-in-panama-for-foreigners": ["healthcare", "health care", "hospital", "health insurance", "medical"],
 "articles/hiking-in-panama-best-trails": ["hiking in panama", "hikes in panama", "trails in panama", "best hikes", "hiking"],
 "articles/panama-all-inclusive-resorts": ["all-inclusive", "all inclusive", "beach resort", "resort"],
 "articles/panama-canal-boat-tours": ["transit", "boat tour", "by boat", "through the locks", "partial transit", "full transit", "canal tour"],
 "articles/panama-residency-visas": ["residency", "pensionado", "friendly nations", "visa", "retirees"],
 "articles/panama-surf-camps": ["surf camp", "surfing", "surf", "santa catalina"],
 "articles/piedra-pintada-painted-rock-el-valle-de-anton": ["piedra pintada", "painted rock", "petroglyph"],
 "articles/pipeline-trail-boquete-quetzal-hike": ["pipeline"],
 "articles/playa-venao-panama": ["venao", "azuero", "pedasí", "pedasi"],
 "articles/retiring-in-panama": ["retire", "retirees", "retirement", "retiring", "expat", "foreign residents"],
 "articles/san-blas-islands-panama-guna-yala-guide": ["san blas", "guna yala", "guna"],
 "articles/san-blas-tours-from-panama-city": ["san blas", "guna yala"],
 "articles/stem-cell-therapy-in-panama": ["stem cell", "medical tourism"],
 "articles/volcan-baru-national-park-entry-facts-active": ["national park", "active volcano", "is it active", "eruption", "dormant", "park entrance", "ranger station"],
 "articles/where-to-eat-el-valle-de-anton": ["restaurant", "where to eat", "lunch", "dinner", "eat"],
 "articles/where-to-eat-in-boquete": ["restaurant", "where to eat", "lunch", "dinner", "eat", "café", "cafe"],
 "articles/where-to-stay-in-panama-city": ["where to stay", "hotel", "stay in panama city", "a night in the city", "overnight"],
 "articles/which-bocas-del-toro-island-to-stay-on": ["where to stay", "which island", "isla colón", "isla colon", "bastimentos", "hotel", "stay on"],
 "es/articles/avistamiento-de-aves-el-valle-de-anton": ["aves", "avistamiento", "pájaros", "pajaros", "observación de aves", "birdwatching"],
 "es/articles/bajo-mono-boquete-circuito-y-senderos": ["bajo mono"],
 "es/articles/canopy-en-boquete-tree-trek-y-opciones": ["canopy", "tree trek", "tirolesa", "tirolina", "zipline"],
 "es/articles/cascadas-el-valle-de-anton-como-llegar": ["cascadas", "cascada", "chorro"],
 "es/articles/cascadas-en-panama-mejores-como-llegar": ["cascadas de panamá", "cascadas en panamá", "cascadas del país", "cascadas"],
 "es/articles/cascadas-perdidas-boquete-ruta-precio": ["cascadas perdidas", "lost waterfalls", "tres cascadas"],
 "es/articles/cerro-gaital-cara-iguana-rutas-dificultad": ["gaital", "cara iguana"],
 "es/articles/cerro-la-silla-sendero-amanecer-el-valle": ["la silla", "amanecer"],
 "es/articles/donde-dormir-en-boquete-hoteles-cabanas-hospedaje": ["dónde dormir", "donde dormir", "hotel", "hospedaje", "cabaña", "alojamiento", "quedarse"],
 "es/articles/el-valle-de-anton-con-ninos-familia": ["niños", "ninos", "familia", "familias"],
 "es/articles/el-valle-de-anton-en-un-dia-itinerario": ["en un día", "un solo día", "día completo", "de un día", "itinerario"],
 "es/articles/fin-de-semana-el-valle-de-anton-2-dias": ["fin de semana", "dos días", "2 días", "una noche"],
 "es/articles/hoteles-en-casco-viejo": ["hotel", "hospedarse", "dónde dormir", "alojamiento", "casco viejo", "casco antiguo"],
 "es/articles/isla-coiba-buceo-parque-nacional": ["buceo", "bucear", "coiba", "snorkel"],
 "es/articles/lugares-turisticos-chiriqui": ["chiriquí", "chiriqui", "lugares turísticos", "provincia"],
 "es/articles/lugares-turisticos-de-cocle": ["coclé", "cocle", "lugares turísticos", "provincia"],
 "es/articles/miradores-de-boquete-vistas-sin-subir-baru": ["mirador", "miradores", "vista panorámica", "vistas"],
 "es/articles/miradores-el-valle-de-anton": ["mirador", "miradores", "vista panorámica", "vistas"],
 "es/articles/restaurantes-y-cafeterias-en-boquete": ["restaurante", "dónde comer", "cafetería", "almorzar", "cenar", "comer"],
 "es/articles/san-blas-guna-yala-guia-tours-islas": ["san blas", "guna yala", "guna"],
 "es/articles/senderismo-en-panama-mejores-senderos-ciudad": ["senderismo", "senderos de panamá", "caminatas", "parque metropolitano", "camino de cruces", "sendero"],
 "es/articles/sendero-el-pianista-boquete-ruta-dificultad": ["pianista"],
 "es/articles/sendero-los-quetzales-quetzal-boquete": ["los quetzales", "quetzal"],
 "es/articles/tour-de-cafe-boquete-fincas-precios-reservar": ["tour de café", "fincas de café", "finca de café", "café", "cafetal"],
}

REGION_ALIAS = {"ciudad de panamá": "panama city", "panama city": "panama city", "boquete": "boquete", "el valle de antón": "el valle",
                "bocas del toro": "bocas", "san blas & the islands": "islands"}
STOP = set("""the and of to in a is it for on that with as at by from this be are you or an your can if not but its it's
there their they was have has more most one two which when where what who will about also into than then them out
el la los las de del y en un una que es por con para al lo se su sus como más o no son hay muy pero si ya este esta""".split())


def strip_acc(s):
    return s.translate(str.maketrans("áéíóúñüÁÉÍÓÚÑÜ", "aeiounuAEIOUNU"))


def words(t):
    return [w for w in re.findall(r"[a-záéíóúñü]+", t.lower()) if w not in STOP and len(w) > 2]


def visible(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def article_region(src):
    """(start, end) of the article body in raw HTML, for old (article.prose) and V2 (article#article) pages."""
    m = re.search(r'<article\b[^>]*>', src)
    if not m: return None
    end = src.find("</article>", m.end())
    return m.end(), end


def paragraphs(src):
    """Prose paragraphs in the article region: [(k, start, end, inner_html)] with byte offsets of the inner HTML.
    Skips paragraphs inside CTA blocks, quotes, cards and FAQ answers."""
    reg = article_region(src)
    if not reg: return []
    a, b = reg
    body = src[a:b]
    out = []
    for k, m in enumerate(re.finditer(r"<p(\s[^>]*)?>(.*?)</p>", body, re.S)):
        pre = body[:m.start()]
        opened = re.findall(r'<(div|aside|section|blockquote|figure)\b[^>]*class="([^"]*)"', pre)
        # cheap ancestor test: the nearest unclosed classed container
        depth = []
        for t in re.finditer(r'<(/?)(div|aside|section|blockquote|figure|details)\b([^>]*)>', pre):
            if t.group(1):
                if depth: depth.pop()
            else:
                c = re.search(r'class="([^"]*)"', t.group(3))
                depth.append((t.group(2), c.group(1) if c else ""))
        bad = any(re.search(r"evb|cta|quote|card|faq|stat|kicker|highlight|banner|offer|rail|caption", c) or tag in ("blockquote", "figure", "details")
                  for tag, c in depth)
        if bad: continue
        out.append((k, a + m.start(2), a + m.end(2), m.group(2)))
    return out


def section_heading(src, pos):
    hs = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", src[:pos], re.S))
    return re.sub(r"^(Section|Sección)\s*\d+", "", visible(hs[-1].group(1))) if hs else ""


class Pg:
    def __init__(self, f):
        self.f = f
        self.rel = f.relative_to(PUB).as_posix()[:-5]
        self.src = f.read_text(encoding="utf-8")
        self.lang = "es" if self.rel.startswith("es/") else "en"
        self.v2 = '<header class="hero">' in self.src
        m = re.search(r'"@type":\s*"BreadcrumbList".*?"itemListElement":\s*(\[.*?\])\s*\}', self.src, re.S)
        try:
            crumbs = [i["name"] for i in json.loads(m.group(1))]
        except Exception:
            crumbs = []
        self.region = REGION_ALIAS.get(crumbs[1].lower(), "national") if len(crumbs) > 2 else "national"
        t = re.search(r"<title>(.*?)</title>", self.src, re.S)
        self.title = visible(t.group(1)) if t else ""
        h = re.search(r"<h1[^>]*>(.*?)</h1>", self.src, re.S)
        self.h1 = visible(h.group(1)) if h else ""
        d = re.search(r'<meta content="([^"]*)" name="description"', self.src) or re.search(r'name="description" content="([^"]*)"', self.src)
        self.desc = html.unescape(d.group(1)) if d else ""
        reg = article_region(self.src)
        self.text = visible(self.src[reg[0]:reg[1]]) if reg else ""
        self.paras = paragraphs(self.src)
        lead = re.search(r'<p class="(?:lead|dek)"[^>]*>(.*?)</p>', self.src, re.S)
        self.lead = visible(lead.group(1)) if lead else (visible(self.paras[0][3]) if self.paras else "")


def tfidf(pages):
    df = collections.Counter()
    tf = {}
    for p in pages:
        c = collections.Counter(words(p.text))
        tf[p.rel] = c
        df.update(c.keys())
    n = len(pages)
    vec = {}
    for p in pages:
        v = {w: (1 + math.log(c)) * math.log(n / df[w]) for w, c in tf[p.rel].items() if df[w] < n * .6}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1
        vec[p.rel] = {w: x / norm for w, x in v.items()}
    return vec


def cos(a, b):
    if len(a) > len(b): a, b = b, a
    return sum(x * b.get(w, 0) for w, x in a.items())


def mentions_in(text, phrases):
    t = strip_acc(text.lower())
    return [ph for ph in phrases if re.search(r"(?<![a-z])" + re.escape(strip_acc(ph.lower())) + r"(?![a-z])", t)]


def prepare(outdir, n_chunks=3):
    outdir = pathlib.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    pages = [Pg(f) for f in sorted(list((PUB / "articles").glob("*.html")) + list((PUB / "es/articles").glob("*.html")))]
    by = {p.rel: p for p in pages}
    targets = [p for p in pages if p.v2]
    sources = [p for p in pages if not p.v2 and p.rel not in HUBS]
    missing = [t.rel for t in targets if t.rel not in MENTIONS]
    assert not missing, missing
    vec = {}
    for lang in ("en", "es"):
        vec.update(tfidf([p for p in pages if p.lang == lang]))
    rows = []
    for t in targets:
        cands = [s for s in sources if s.lang == t.lang]
        sims = {s.rel: cos(vec[s.rel], vec[t.rel]) for s in cands}
        mx = max(sims.values()) or 1
        for s in cands:
            body_now = re.sub(r"<!--PS-V2-LINKS-->.*?<!--/PS-V2-LINKS-->", "", s.src, flags=re.S)
            reg = article_region(body_now)
            if f'href="/{t.rel}"' in body_now[reg[0]:reg[1]]:
                continue                      # already linked in the text
            prose = " ".join(visible(p[3]) for p in s.paras)
            found = mentions_in(prose, MENTIONS[t.rel])
            region = 1.0 if s.region == t.region else (0.5 if "national" in (s.region, t.region) else 0.0)
            score = .45 * sims[s.rel] / mx + .25 * region + .30 * (1.0 if found else 0.0)
            rows.append(dict(source=s.rel, target=t.rel, score=round(score, 3), sim=round(sims[s.rel] / mx, 3), region=region, mentions=found))
    rows.sort(key=lambda r: -r["score"])
    chosen, per_src, per_tgt = [], collections.Counter(), collections.Counter()
    for r in rows:
        if r["score"] >= MIN_SCORE and per_src[r["source"]] < PER_SOURCE:
            chosen.append(r); per_src[r["source"]] += 1; per_tgt[r["target"]] += 1
    for t in targets:
        for r in [r for r in rows if r["target"] == t.rel and r not in chosen]:
            if per_tgt[t.rel] >= MIN_PER_TARGET: break
            if r["score"] >= MIN_SCORE - .1 and per_src[r["source"]] < MAX_PER_SOURCE:
                chosen.append(r); per_src[r["source"]] += 1; per_tgt[t.rel] += 1
    # tasks: one per pair, with the best candidate paragraphs from the source
    tasks = []
    for i, r in enumerate(sorted(chosen, key=lambda r: (r["source"], -r["score"]))):
        s, t = by[r["source"]], by[r["target"]]
        tv = vec[t.rel]
        scored = []
        for k, a, b, inner in s.paras:
            txt = visible(inner)
            if len(txt.split()) < 18 or f'href="/{t.rel}"' in inner: continue
            m = mentions_in(txt, MENTIONS[t.rel])
            pv = collections.Counter(words(txt))
            sim = sum(tv.get(w, 0) for w in pv)
            scored.append((len(m) * 2 + sim * 10, k, txt, m, section_heading(s.src, a)))
        scored.sort(key=lambda x: -x[0])
        cand = [{"pid": k, "section": sec, "mentions": m, "text": txt} for _, k, txt, m, sec in scored[:4]]
        if not cand: continue
        tasks.append({"task": f"T{i:03d}", "lang": s.lang, "source": "/" + s.rel, "source_title": s.h1,
                      "target": "/" + t.rel, "target_title": t.h1, "target_summary": t.desc,
                      "target_lead": t.lead[:600], "relevance": r["score"], "candidates": cand})
    # balanced chunks, keeping each source page in one chunk
    groups = collections.defaultdict(list)
    for tk in tasks: groups[tk["source"]].append(tk)
    chunks = [[] for _ in range(n_chunks)]
    for src in sorted(groups, key=lambda g: -len(groups[g])):
        min(chunks, key=len).extend(groups[src])
    for j, c in enumerate(chunks):
        (outdir / f"tasks_{j + 1}.json").write_text(json.dumps(c, ensure_ascii=False, indent=1))
    (outdir / "pairs.json").write_text(json.dumps({"chosen": chosen, "all": rows[:4000]}, ensure_ascii=False, indent=1))
    cov = collections.Counter(r["target"] for r in chosen)
    print(f"{len(rows)} scored pairs, {len(chosen)} chosen, {len(tasks)} tasks in {n_chunks} files")
    print("targets with <2 chosen sources:", [t.rel for t in targets if cov[t.rel] < 2])
    return tasks


# ───────────────────────── apply ─────────────────────────
def wrap_once(inner, anchor, href):
    """Wrap the first occurrence of `anchor` that sits in plain text (not in a tag, not inside <a>)."""
    toks = re.split(r"(<[^>]+>)", inner)
    in_a = 0
    for i, t in enumerate(toks):
        if t.startswith("<"):
            if re.match(r"<a\b", t): in_a += 1
            elif t.startswith("</a"): in_a = max(0, in_a - 1)
            continue
        if in_a: continue
        for cand in (anchor, html.escape(anchor, quote=False)):
            j = t.find(cand)
            if j >= 0:
                toks[i] = t[:j] + f'<a href="{href}">{cand}</a>' + t[j + len(cand):]
                return "".join(toks)
    return None


def linkify(sentence, href):
    m = re.search(r"\[\[(.+?)\]\]", sentence)
    if not m or sentence.count("[[") != 1: return None
    return html.escape(sentence[:m.start()], quote=False) + f'<a href="{href}">{html.escape(m.group(1), quote=False)}</a>' + html.escape(sentence[m.end():], quote=False)


def apply(outdir, dry=False):
    outdir = pathlib.Path(outdir)
    tasks = {}
    for f in sorted(outdir.glob("tasks_*.json")):
        for t in json.loads(f.read_text()): tasks[t["task"]] = t
    decisions = []
    for f in sorted(outdir.glob("decisions_*.json")):
        decisions += json.loads(f.read_text())
    log = collections.Counter()
    report = []
    edits = collections.defaultdict(list)          # file -> [(start, end, new_inner, extra_after)]
    for d in decisions:
        t = tasks.get(d.get("task"))
        act = d.get("action")
        if not t or act == "skip":
            log["skip"] += 1; report.append({**(d or {}), "status": "skipped"}); continue
        f = PUB / (t["source"].lstrip("/") + ".html")
        src = f.read_text(encoding="utf-8")
        paras = {k: (a, b, inner) for k, a, b, inner in paragraphs(src)}
        pid = d.get("pid")
        if pid not in paras:
            log["bad-pid"] += 1; report.append({**d, "status": "rejected: unknown paragraph"}); continue
        a, b, inner = paras[pid]
        if f'href="{t["target"]}"' in src[article_region(src)[0]:article_region(src)[1]] or any(e[4] == t["target"] for e in edits[f]):
            log["dup"] += 1; report.append({**d, "status": "rejected: target already linked"}); continue
        if any(e[0] == a for e in edits[f]) and act == "wrap":
            pass
        new_inner, after = None, ""
        if act == "wrap":
            new_inner = wrap_once(inner, d.get("anchor", ""), t["target"])
            if not new_inner or len(d.get("anchor", "").split()) > 9:
                log["bad-anchor"] += 1; report.append({**d, "status": "rejected: anchor not found verbatim"}); continue
        elif act == "add_sentence":
            sent = linkify(d.get("sentence", "").strip(), t["target"])
            if not sent or len(d["sentence"].split()) > 40:
                log["bad-sentence"] += 1; report.append({**d, "status": "rejected: sentence malformed"}); continue
            new_inner = inner.rstrip() + " " + sent
        elif act == "add_paragraph":
            para = linkify(d.get("paragraph", "").strip(), t["target"])
            if not para or len(d["paragraph"].split()) > 70:
                log["bad-paragraph"] += 1; report.append({**d, "status": "rejected: paragraph malformed"}); continue
            new_inner, after = inner, f"<p>{para}</p>"
        else:
            log["unknown"] += 1; continue
        edits[f].append((a, b, new_inner, after, t["target"]))
        log[act] += 1
        report.append({**d, "status": "applied", "source": t["source"], "target": t["target"]})
    for f, es in edits.items():
        src = f.read_text(encoding="utf-8")
        # several edits may hit the same paragraph: chain them on the latest inner HTML
        by_start = collections.defaultdict(list)
        for e in es: by_start[(e[0], e[1])].append(e)
        for (a, b), lst in sorted(by_start.items(), key=lambda x: -x[0][0]):
            inner = src[a:b]
            afters = ""
            for _, _, new_inner, after, tgt in lst:
                if new_inner != inner and inner in new_inner:
                    inner = new_inner                    # appended sentence
                elif new_inner != src[a:b]:
                    # wrap computed on the original; redo it on the current inner
                    anchor = re.search(r'<a href="' + re.escape(tgt) + r'">(.*?)</a>', new_inner).group(1)
                    inner = wrap_once(inner, html.unescape(anchor), tgt) or inner
                afters += after
            close = src.find("</p>", b) + 4
            src = src[:a] + inner + src[b:close] + afters + src[close:]
        if not dry:
            f.write_text(src, encoding="utf-8")
    (outdir / "applied.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(dict(log), "files edited:", len(edits), "(dry run)" if dry else "")


def strip():
    n = 0
    for f in sorted(list((PUB / "articles").glob("*.html")) + list((PUB / "es/articles").glob("*.html"))):
        s = f.read_text(encoding="utf-8")
        s2 = re.sub(r"<!--PS-V2-LINKS-->.*?<!--/PS-V2-LINKS-->", "", s, flags=re.S)
        if s2 != s:
            f.write_text(s2, encoding="utf-8"); n += 1
    print("removed the New guides list from", n, "pages")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prepare": prepare(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
    elif cmd == "apply": apply(sys.argv[2], "--dry" in sys.argv)
    elif cmd == "strip": strip()
