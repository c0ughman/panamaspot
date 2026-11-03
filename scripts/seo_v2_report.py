#!/usr/bin/env python3
"""Render reports/seo-v2-audit.json (from seo_v2_audit.py) as reports/seo-v2-audit.html."""
import json, html, collections, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "reports/seo-v2-audit.json").read_text())
P = D["pages"]
N = len(P)
esc = html.escape

CATS = ["Indexability & URL", "Head tags", "Hreflang", "Structured data", "Headings & outline", "Content", "Images", "Links", "Performance", "Live site"]

# per check aggregate
agg = collections.defaultdict(lambda: collections.Counter())
fails = collections.defaultdict(list)
for u, p in P.items():
    for c in p["checks"]:
        k = (c["cat"], c["id"])
        agg[k][c["status"]] += 1
        if c["status"] in ("fail", "warn"):
            fails[k].append((p["rel"], c["msg"], c["detail"]))


def score(counter):
    s = counter["pass"] + .5 * counter["warn"]
    n = counter["pass"] + counter["warn"] + counter["fail"]
    return s / n if n else 1


cat_tot = collections.defaultdict(collections.Counter)
for (cat, cid), c in agg.items():
    cat_tot[cat].update(c)
page_cat = {u: collections.defaultdict(collections.Counter) for u in P}
for u, p in P.items():
    for c in p["checks"]:
        page_cat[u][c["cat"]][c["status"]] += 1
overall = score(sum(cat_tot.values(), collections.Counter()))
tot = sum(cat_tot.values(), collections.Counter())


def pages_hit(*ids):
    s = set()
    for (cat, cid), lst in fails.items():
        if cid in ids:
            s.update(r for r, _, _ in lst)
    return len(s)


IL = D["interlinks"]
il_kinds = collections.Counter(x["kind"] for x in IL)
il_pages = len({x["from"] for x in IL if x["kind"] == "New guides list"})
orphans = [p["rel"] for p in P.values() if not p["inbound"]]
weak = sorted(((p["inbound"].get("body", 0), p["rel"]) for p in P.values()))

# ───────── the findings, worst first (counts come from the data) ─────────
F = [
    ("high", "Old pages link to the new guides only through a bolted-on list",
     f"{il_kinds['New guides list']} of the {len(IL)} links the older guides gained point from a \"New guides\" list pasted above \"Related guides\" on {il_pages} pages; none sit inside a sentence. It reads as a link dump and passes little topical context.",
     "Remove the list. Add 1–3 links per old page inside the paragraph where the topic comes up, with descriptive anchor text.", len(IL) and il_pages),
    ("high", f"{len(orphans)} new pages have no inbound links at all",
     "Only the sitemap points to " + ", ".join(o.split('/')[-1].replace('.html', '') for o in orphans) + ". Google discovers them, but nothing passes them authority, and readers can't reach them.",
     "Link each from its hub and from 2–3 related guides, and add them to the footer directory.", len(orphans)),
    ("high", "Every page also answers at a .html address",
     "/articles/x.html returns 200 instead of redirecting to /articles/x on the live site. The canonical contains it, but it is a duplicate URL for crawlers and analytics.",
     "Redirect *.html to the clean URL (Netlify pretty URLs, or a _redirects rule).", pages_hit("variant-html")),
    ("high", "Self-hosted photos are heavy",
     "Most pages carry images over 350KB (up to ~830KB for a 1280px webp), several MB per page in total. Lazy-loading hides some of it, but it costs LCP on mobile and crawl budget.",
     "Re-encode at quality ~72, cap content images at 1600px, and serve srcset for in-article photos.", pages_hit("file-weight", "local-image-bytes")),
    ("med", "Share images are the wrong shape, with no size or alt",
     "Half the og:images are portrait or square (e.g. 1280×1922), so Facebook, WhatsApp and LinkedIn crop them badly. No page declares og:image:width/height or og:image:alt.",
     "Generate a 1200×630 crop per page and add the three meta tags.", pages_hit("og-image-size", "og-image-dims")),
    ("med", "Sitemap is behind the pages",
     f"{pages_hit('sitemap-hreflang-match')} pages with an EN/ES twin have no hreflang alternates in the sitemap, and the 4 rewritten pages still carry their old lastmod.",
     "Feed the pairs and dates in sitemap.ts from the pages themselves.", pages_hit("sitemap-hreflang-match", "sitemap-lastmod")),
    ("med", "English guides send readers into Spanish pages mid-text",
     f"{pages_hit('no-cross-language-body-links')} pages link from the article text to /es/ pages (e.g. the Albrook bus guide) where no English page exists.",
     "Link only within the language; where the topic has no page, drop the link or write the page.", pages_hit("no-cross-language-body-links")),
    ("med", "Heading outline: skipped levels and template headings",
     f"{pages_hit('no-level-skips')} pages jump H2→H4 (the numbered steps use h4). Every page puts 9+ template H2/H3s outside the article (At a glance, On this page, In pictures, footer).",
     "Make step titles h3 and template titles plain text (p/div with the same class).", pages_hit("no-level-skips", "template-headings")),
    ("med", "Health, money and visa pages have no named author",
     "Stem cells, healthcare, residency, buying property and retiring are credited to the Organization \"PanamaSpot\" (\"Panama Spot editors\" in the byline). Google weighs authorship heavily on these topics.",
     "Add a real author or reviewer page (ties into the About page) and use a Person in the schema.", pages_hit("author-person")),
    ("low", "Gallery photos are still hotlinked from Pexels",
     "Every page loads 2–6 gallery images from images.pexels.com. They all respond today, but you don't control them and they bypass your image pipeline.",
     "Download, convert to webp and self-host, like the heroes.", pages_hit("self-hosted")),
    ("low", "FAQ schema text has stray spaces",
     "Answers read \"Coclé province , a town\": citation markers were stripped from the schema copy but the space before them stayed.",
     "Collapse whitespace before punctuation when building FAQPage.", pages_hit("faq-text-clean")),
    ("low", "Some titles and descriptions get truncated",
     f"{pages_hit('title-pixels', 'title-length')} titles run past ~600px and {pages_hit('desc-length')} descriptions past 160 characters.",
     "Trim to the limit, keeping the keyword at the front.", pages_hit("title-pixels", "desc-length", "title-length")),
    ("low", "H1 copies the title word for word",
     f"On {pages_hit('h1-not-title-copy')} pages the H1 and <title> are identical, a wasted chance at a second phrasing of the query.",
     "Vary one of them (the pattern most pages already use).", pages_hit("h1-not-title-copy")),
    ("low", "Hanken Grotesk loads from Google Fonts, render-blocking",
     "GildaC is self-hosted and preloaded; the body font still waits on a fonts.googleapis.com stylesheet.",
     "Self-host Hanken woff2 like GildaC.", pages_hit("third-party-fonts")),
    ("low", "Fake search box and a duplicated menu link",
     "\"Search guides\" is a <span> that does nothing, and \"Destinations\" and \"Guides\" both go to /#cat-regions.",
     "Build a small static search or remove it; point Guides somewhere else.", pages_hit("no-dead-ui")),
    ("low", "Image file names are hashes and encoded strings",
     "e.g. 6b4a3f8d-1280px-Chorro_Marcho_EL_Valle_Panama_03.webp. File names are a small image-search signal.",
     "Rename to short descriptive slugs when re-encoding.", pages_hit("descriptive-filenames")),
    ("low", "A few insecure or weak links",
     f"{pages_hit('external-https')} pages link to http:// sources; {pages_hit('body-links-min')} pages have fewer than 5 in-text internal links.",
     "Switch to https; add contextual links where thin.", pages_hit("external-https", "body-links-min")),
]

solid = sorted([(cat, cid) for (cat, cid), c in agg.items() if c["pass"] == N], key=lambda x: CATS.index(x[0]) if x[0] in CATS else 99)
LABEL = {  # plain names for the checks shown in the "solid" list and tables
    "robots-index": "Indexable (no noindex)", "canonical-self": "Canonical points to itself", "canonical-single": "One canonical tag",
    "canonical-https-apex": "Canonical on https apex", "slug-format": "Clean lowercase slugs", "jsonld-valid": "JSON-LD parses",
    "has-Article": "Article schema", "has-BreadcrumbList": "Breadcrumb schema", "has-WebPage": "WebPage schema",
    "faq-matches-visible": "FAQ schema = visible FAQ", "one-h1": "Exactly one H1", "toc-anchors-resolve": "Contents links work",
    "unique-ids": "No duplicate ids", "no-broken-internal": "No broken internal links", "alt-attribute": "Every image has alt",
    "alt-content-images": "Content images have real alt text", "hero-img-tag": "Hero is a real <img>", "hero-priority": "Hero loads first",
    "hreflang-self": "Self hreflang", "hreflang-x-default": "x-default", "hreflang-reciprocal": "Twins link back",
    "html-lang": "html lang correct", "title-unique": "Unique titles", "desc-unique": "Unique descriptions", "live-200": "Live: 200 OK",
    "live-deployed": "Live = repo", "live-canonical": "Live canonical", "live-ga": "GA4 on the live page", "in-sitemap": "In the sitemap",
    "local-files-exist": "No missing image files", "body-language": "Text in the page's language", "ui-language": "UI strings translated",
    "citations-resolve": "Citations resolve", "no-placeholders": "No placeholder text",
}

SEV = {"high": ("#c2410c", "#fdebe1", "Fix first"), "med": ("#a16207", "#fbf1d9", "Fix soon"), "low": ("#475569", "#eef1f5", "Tidy up")}


def bar(c, w=160):
    n = c["pass"] + c["warn"] + c["fail"] or 1
    seg = lambda k, col: f'<i style="width:{c[k] / n * 100:.2f}%;background:{col}"></i>' if c[k] else ""
    return f'<span class="sb" style="width:{w}px">{seg("pass", "#6fbf8e")}{seg("warn", "#f2c46d")}{seg("fail", "#ec7a6a")}</span>'


def color(sc):
    return "#5fb383" if sc >= .9 else "#9ccc7a" if sc >= .8 else "#f2c46d" if sc >= .65 else "#ec8a6a"


css = """
:root{--bg:#f8f4ee;--card:#fff;--ink:#1d2433;--muted:#6b7180;--line:#ebe5dc;--navy:#0b2a5b;--tint:#edf1f7}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 Inter,system-ui,sans-serif}
.w{max-width:1180px;margin:0 auto;padding:0 20px}
header{padding:48px 0 28px}h1{font-size:34px;line-height:1.15;margin:0 0 8px;letter-spacing:-.02em}
h2{font-size:22px;margin:0 0 6px;letter-spacing:-.01em}h3{font-size:16px;margin:0}
.sub{color:var(--muted);max-width:75ch}
.card{background:var(--card);border-radius:18px;box-shadow:0 0 0 1px var(--line);padding:24px;margin:18px 0}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.kpi{background:var(--tint);border-radius:14px;padding:16px}
.kpi b{display:block;font-size:28px;letter-spacing:-.02em;color:var(--navy)}.kpi span{font-size:13px;color:var(--muted)}
@media(max-width:800px){.kpis{grid-template-columns:repeat(2,1fr)}}
.cats{display:grid;gap:10px;margin-top:14px}.cat{display:grid;grid-template-columns:190px 1fr 56px;gap:14px;align-items:center;font-size:14px}
.track{height:12px;border-radius:99px;background:#f1ece4;overflow:hidden}.track i{display:block;height:100%;border-radius:99px}
.cat em{font-style:normal;font-weight:700;text-align:right}
.f{display:grid;grid-template-columns:96px 1fr 120px;gap:16px;padding:16px 0;border-top:1px solid var(--line)}
.f:first-of-type{border-top:0}.pill{display:inline-block;font:700 12px/1 Inter;padding:6px 10px;border-radius:99px}
.f p{margin:4px 0 0;color:#3a4150}.f .fix{color:var(--muted);font-size:14px}.f .n{text-align:right;font-size:13px;color:var(--muted)}
.f .n b{display:block;font-size:22px;color:var(--ink)}
@media(max-width:800px){.f{grid-template-columns:1fr}.f .n{text-align:left}}
.ok{columns:3;column-gap:24px;font-size:14px;padding:0;margin:10px 0 0;list-style:none}.ok li{break-inside:avoid;padding:3px 0}
.ok li::before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:#5fb383;margin-right:8px}
@media(max-width:800px){.ok{columns:1}}
table{width:100%;border-collapse:collapse;font-size:14px}th{text-align:left;color:var(--muted);font-weight:600;font-size:12.5px;padding:8px 6px;border-bottom:1px solid var(--line)}
td{padding:8px 6px;border-bottom:1px solid var(--line);vertical-align:top}
.sb{display:inline-flex;height:10px;border-radius:99px;overflow:hidden;background:#f1ece4;vertical-align:middle}.sb i{display:block;height:100%}
details summary{cursor:pointer;list-style:none}details summary::-webkit-details-marker{display:none}
details .lst{font-size:13px;color:#3a4150;margin:8px 0 2px;padding-left:0;list-style:none;max-height:260px;overflow:auto}
details .lst li{padding:3px 0;border-top:1px dashed var(--line)}
.legend{display:flex;gap:16px;font-size:13px;color:var(--muted);margin:6px 0 10px}.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.mx{overflow-x:auto}.mx table{min-width:900px}.mx td.c{width:68px;text-align:center;font-weight:700;font-size:12.5px;color:#1d2433}
.mx td.pg{font-size:13px;max-width:340px}.mx tr:hover td{background:#fbf8f3}
.il{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:800px){.il{grid-template-columns:1fr}}
.hb{display:grid;grid-template-columns:150px 1fr 40px;gap:10px;align-items:center;font-size:13.5px;margin:6px 0}
.ex{background:#fbf8f3;border-radius:12px;padding:14px 16px;font-size:13.5px;color:#3a4150}
.outline{font-size:12.5px;line-height:1.5;color:#3a4150;margin:6px 0}.outline .t{color:#a0a6b2}
.small{font-size:13px;color:var(--muted)}
"""

out = []
w = out.append
w(f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
  f"<title>V2 guides: technical SEO audit</title><link rel='preconnect' href='https://fonts.googleapis.com'>"
  f"<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap' rel='stylesheet'><style>{css}</style></head><body>")
w("<div class='w'><header><h1>V2 guides: technical SEO audit</h1>"
  f"<p class='sub'>{N} pages in the new template (50 new, 4 rewritten), checked by <code>scripts/seo_v2_audit.py</code>: "
  f"{len(agg)} different checks across {len(CATS)} areas, {sum(tot.values()):,} results in total, plus live requests to panamaspot.com. "
  f"Generated {D['generated'][:10]}. Findings were spot-checked by hand on sample pages; checks that misfired were fixed before this run.</p></header>")

# KPIs
w("<div class='card'><div class='kpis'>")
for v, lab in ((f"{overall:.0%}", "overall score (warn = half)"), (N, "pages audited"), (f"{sum(tot.values()):,}", "check results"),
               (tot["fail"], "failures"), (tot["warn"], "warnings")):
    w(f"<div class='kpi'><b>{v}</b><span>{lab}</span></div>")
w("</div><div class='cats'>")
for cat in CATS:
    if cat not in cat_tot: continue
    sc = score(cat_tot[cat])
    w(f"<div class='cat'><span>{cat}</span><span class='track'><i style='width:{sc * 100:.1f}%;background:{color(sc)}'></i></span><em>{sc:.0%}</em></div>")
w("</div></div>")

# Findings
w("<div class='card'><h2>What to fix, in order</h2><p class='small'>Each finding: what is wrong, then what to do. The number is how many of the "
  f"{N} pages it touches.</p>")
for sev, title, why, fix, n in F:
    col, bg, lab = SEV[sev]
    w(f"<div class='f'><div><span class='pill' style='color:{col};background:{bg}'>{lab}</span></div>"
      f"<div><h3>{esc(title)}</h3><p>{esc(why)}</p><p class='fix'>→ {esc(fix)}</p></div>"
      f"<div class='n'><b>{n if isinstance(n, int) else ''}</b>{'pages' if sev != 'high' or 'list' not in title else 'old pages'}</div></div>")
w("</div>")

# Solid
w(f"<div class='card'><h2>What is already solid</h2><p class='small'>Checks that pass on all {N} pages.</p><ul class='ok'>")
for cat, cid in solid:
    w(f"<li>{esc(LABEL.get(cid, cid.replace('-', ' ')))}</li>")
w("</ul></div>")

# Interlinking
w("<div class='card'><h2>Interlinking: how the older guides point to the new ones</h2>"
  f"<p class='sub'>Every link to a V2 page that the older guides gained since the last pre-V2 commit (8aa8866, 22 Oct), classified by where it was placed.</p><div class='il'><div>")
mx = max(il_kinds.values()) if il_kinds else 1
for k, v in il_kinds.most_common():
    colr = "#ec8a6a" if k == "New guides list" else "#6fbf8e" if k in ("in a sentence",) else "#9fb3d1"
    w(f"<div class='hb'><span>{esc(k)}</span><span class='track'><i style='width:{v / mx * 100:.1f}%;background:{colr}'></i></span><b>{v}</b></div>")
w("<div class='hb'><span>in a sentence</span><span class='track'><i style='width:0'></i></span><b>0</b></div>" if "in a sentence" not in il_kinds else "")
ex = next((x for x in IL if x["kind"] == "New guides list"), None)
grp = [x for x in IL if ex and x["from"] == ex["from"] and x["kind"] == "New guides list"]
w("<p class='small'>\"header\" = the EN/ES switch on an old page, now pointing to its new twin. That part is right.</p></div><div>")
if ex:
    w(f"<div class='ex'><b>What the list looks like</b> on {esc(ex['from'])}, above \"Related guides\":<br><br><i>Keep exploring · New guides</i><ul>"
      + "".join(f"<li>{esc(x['anchor'])}</li>" for x in grp) + "</ul>No sentence and no reason given: the same block on "
      f"{il_pages} pages.</div>")
w("</div></div><h3 style='margin-top:22px'>In-text links each new page receives from other guides</h3><p class='small'>Body links only (not footer, menus or cards). Under 2 is weak.</p>")
for n_, rel in weak[:16]:
    w(f"<div class='hb'><span title='{esc(rel)}'>{esc(rel.split('/')[-1][:24])}</span><span class='track'><i style='width:{min(100, n_ / 10 * 100):.0f}%;background:{'#ec8a6a' if n_ < 2 else '#f2c46d' if n_ < 4 else '#6fbf8e'}'></i></span><b>{n_}</b></div>")
w("<p class='small'>The 16 weakest shown. Orphans (no inbound link anywhere): " + (", ".join(esc(o) for o in orphans) or "none") + ".</p></div>")

# Per-check tables
w("<div class='card'><h2>Every check, by area</h2><div class='legend'><span><i style='background:#6fbf8e'></i>pass</span>"
  "<span><i style='background:#f2c46d'></i>warning</span><span><i style='background:#ec7a6a'></i>fail</span><span>Click a row for the pages.</span></div>")
for cat in CATS:
    ks = sorted([k for k in agg if k[0] == cat], key=lambda k: (score(agg[k]), k[1]))
    if not ks: continue
    sc = score(cat_tot[cat])
    w(f"<details style='margin:10px 0'{' open' if sc < .85 else ''}><summary><h3 style='display:inline'>{cat}</h3> "
      f"<span class='small'>· {len(ks)} checks · {sc:.0%}</span></summary><table><tr><th>Check</th><th>Results</th><th>Pass</th><th>Warn</th><th>Fail</th><th>Example</th></tr>")
    for k in ks:
        c = agg[k]
        if c["pass"] + c["warn"] + c["fail"] == 0:
            continue
        lst = fails.get(k, [])
        exm = esc(lst[0][1][:90]) if lst else ""
        body = "".join(f"<li><b>{esc(r.split('/')[-1])}</b> {esc(m[:160])} <span class='small'>{esc(d[:160])}</span></li>" for r, m, d in lst)
        name = esc(LABEL.get(k[1], k[1].replace("-", " ")))
        row = f"<td>{name}</td><td>{bar(c, 120)}</td><td>{c['pass']}</td><td>{c['warn']}</td><td>{c['fail']}</td><td class='small'>{exm}</td>"
        if lst:
            w(f"<tr><td colspan=6 style='padding:0'><details><summary><table><tr>{row}</tr></table></summary><ul class='lst'>{body}</ul></details></td></tr>")
        else:
            w(f"<tr>{row}</tr>")
    w("</table></details>")
w("</div>")

# Page matrix
w("<div class='card'><h2>Page by page</h2><p class='small'>Score per area (warn = half). Click a page for its issues and heading outline.</p><div class='mx'><table><tr><th>Page</th>"
  + "".join(f"<th>{c.split(' ')[0]}</th>" for c in CATS) + "</tr>")
for u, p in sorted(P.items(), key=lambda kv: score(sum(page_cat[kv[0]].values(), collections.Counter()))):
    cells = ""
    for cat in CATS:
        c = page_cat[u].get(cat)
        if not c or c["pass"] + c["warn"] + c["fail"] == 0:
            cells += "<td class='c'>–</td>"; continue
        sc = score(c)
        cells += f"<td class='c' style='background:{color(sc)}33'>{sc:.0%}</td>"
    issues = [c for c in p["checks"] if c["status"] in ("fail", "warn")]
    iss = "".join(f"<li><b style='color:{'#c2410c' if c['status'] == 'fail' else '#a16207'}'>{c['status']}</b> [{esc(c['cat'])}] {esc(c['msg'][:170])}</li>" for c in issues)
    ol = "".join(f"<div style='padding-left:{(lvl - 1) * 16}px'>{'<span class=t>' if where == 'template' else ''}H{lvl} {esc(t)}{'</span>' if where == 'template' else ''}</div>" for lvl, t, where in p["outline"])
    w(f"<tr><td class='pg'><details><summary><b>{esc(p['rel'].split('/')[-1].replace('.html', ''))}</b><br><span class='small'>{p['lang'].upper()} · {p['words']:,} words · {len(issues)} issues</span></summary>"
      f"<ul class='lst'>{iss}</ul><div class='outline'><b>Outline</b> <span class='t'>(grey = template headings outside the article)</span>{ol}</div></details></td>{cells}</tr>")
w("</table></div></div>")

w(f"<p class='small' style='margin:24px 0 48px'>Re-run: <code>python3 scripts/seo_v2_audit.py && python3 scripts/seo_v2_report.py</code>. "
  f"Live sitemap: {D['sitemap_count']} URLs. Hotlinked images checked: {len(D['ext_images'])}, all answering {', '.join(map(str, sorted(set(D['ext_images'].values()), key=str)))}.</p></div></body></html>")
(ROOT / "reports/seo-v2-audit.html").write_text("".join(out))
print("wrote reports/seo-v2-audit.html")
