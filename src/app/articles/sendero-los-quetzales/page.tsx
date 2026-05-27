/* ============================================================================
   PAGE TEMPLATE — "Destination guide"  (BLUE theme)
   ----------------------------------------------------------------------------
   This file is the master template every generated guide is copied from.
   It is intentionally generic: nothing here is specific to one kind of place,
   so the same skeleton works for a town, an island, a park, a neighborhood…

   HOW TO GENERATE A NEW PAGE
     1. Copy this whole file to  src/app/articles/<your-slug>/page.tsx
     2. Edit the CONFIG block (title, hero, facts) and the section data
        (TOC_ITEMS, GALLERY, HIGHLIGHTS, FAQ_ITEMS, BENTO copy).
     3. Add the slug to src/app/sitemap.ts.
     4. For a green page instead of blue, see the sibling template
        src/app/articles/bocas-del-toro/page.tsx (it sets data-theme="green").

   THEME
     The look is driven by CSS tokens on <main className="article-page">:
       --accent  primary color (headings, callout rule, card borders)
       --pop     lively secondary (section numbers, links, FAQ toggles)
     Blue is the default. The green page overrides them with data-theme="green".

   SECTIONS BELOW, in order:
     HERO · HEAD + FACT CARD · BODY (TOC / prose / info-card rail) ·
     GALLERY · HIGHLIGHT CARDS · BENTO · FAQ
   ========================================================================== */

import type { Metadata } from "next";
import Link from "next/link";
import { buildMetadata } from "@/lib/seo";
import { siteConfig } from "@/lib/site-config";
import { articleJsonLd, breadcrumbJsonLd, faqPageJsonLd, jsonLdScript } from "@/lib/jsonld";
import { ReadingProgress } from "@/components/reading-progress";
import { ArticleHero } from "@/components/article-hero";
import { ArticleToc } from "@/components/article-toc";
import { FaqItem } from "@/components/faq-item";
import { SiteFooter } from "@/components/site-footer";
import { HtmlLang } from "@/components/html-lang";

/* ── Pexels photo helper — swap IDs for the real photos of your subject. ── */
const pexels = (id: number, w = 1600) =>
  `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${w}`;

/* ════════════════════════════════════════════════════════════════════════
   CONFIG — the per-page knobs. Edit these first when generating a new page.
   ════════════════════════════════════════════════════════════════════════ */
const SLUG = "sendero-los-quetzales";
const HERO_IMAGE = pexels(2380342, 2000);

const ARTICLE = {
  slug: SLUG,
  // LOCALE — "en" (root, /articles/…) or "es" (/es/articles/…). Drives the
  // header/footer language, og:locale, schema inLanguage and <html lang>.
  locale: "en" as "en" | "es",
  // seoTitle → the <title> tag. Keep it keyword-led and ~60 chars for search.
  seoTitle: "Boquete Travel Guide: Things to Do, When to Go & Where to Stay",
  // title → the visible <h1>. Can be more narrative/editorial than seoTitle.
  title: "Boquete — the highland town that runs quietly on coffee, rivers, and fog.",
  description:
    "A complete guide to Boquete, Panama's mountain town in the Chiriquí highlands: how to get there, when to go, where to stay, and what's worth your time once you arrive.",
  // articleSection → topic/category for Article schema.
  section: "Destinations",
  publishedAt: "2026-05-03",
  modifiedAt: "2026-05-26",
  breadcrumb: ["Chiriquí", "Highland towns", "Boquete"],
  heroTags: ["Highlands", "Destination guide", "Updated · May 2026"],
} as const;

/* ── TOC — one entry per <h2 id="…"> below. Drives the sticky left rail. ── */
const TOC_ITEMS = [
  { id: "s1", n: "01", label: "Why go" },
  { id: "s2", n: "02", label: "Getting there" },
  { id: "s3", n: "03", label: "When to visit" },
  { id: "s4", n: "04", label: "Where to stay" },
  { id: "s5", n: "05", label: "What to do" },
  { id: "s6", n: "06", label: "Know before you go" },
  { id: "s7", n: "07", label: "FAQ" },
];

/* ── GALLERY — real photos. First item renders large (the "feature" tile). ── */
const GALLERY = [
  { src: pexels(2918139), caption: "The Caldera valley at first light", feature: true },
  { src: pexels(30658818), caption: "Single-origin coffee, grown on the slopes" },
  { src: pexels(3603874), caption: "Cloud forest on the edge of town" },
  { src: pexels(9566563), caption: "Highland birdlife, year-round" },
  { src: pexels(9246451), caption: "Trailheads start where the streets end" },
] as const;

/* ── HIGHLIGHTS — full-width "good to know" cards. Big number + short note. ── */
const HIGHLIGHTS = [
  { stat: "1,200 m", title: "Eternal spring", body: "The elevation keeps days mild and nights cool all year — locals call it the land of eternal spring." },
  { stat: "≈1 hr", title: "From the airport", body: "David (DAV) is the gateway; the drive up into the highlands takes about an hour on a good road." },
  { stat: "$$", title: "Mid-range value", body: "Comfortable without being expensive — most travelers spend $60–110 a day including a room." },
] as const;

/* ── FAQ — question/answer pairs. Also emitted as FAQPage structured data. ── */
const FAQ_ITEMS = [
  {
    question: "Do I need a car?",
    answer:
      "Not in town — Boquete is walkable and colectivos run the main loop for about a dollar. A car helps if you want to reach trailheads, coffee farms, or the higher viewpoints on your own schedule.",
  },
  {
    question: "How many days should I plan?",
    answer:
      "Two to three nights is the sweet spot: one day to settle and walk the town, one for the outdoors, and one for a coffee tour or a slower morning.",
  },
  {
    question: "Is it cold?",
    answer:
      "Cool, not cold. Days sit in the low 20s°C and nights can drop to the low teens. Bring a light layer and a rain shell — the highlands make their own weather.",
  },
  {
    question: "Is English spoken?",
    answer:
      "Widely, in hotels and tour offices. A few words of Spanish still go a long way at markets and with drivers.",
  },
] as const;

export const metadata: Metadata = buildMetadata({
  title: ARTICLE.seoTitle,
  description: ARTICLE.description,
  path: `/articles/${ARTICLE.slug}`,
  ogImage: HERO_IMAGE,
  type: "article",
  publishedTime: ARTICLE.publishedAt,
  modifiedTime: ARTICLE.modifiedAt,
  authors: [siteConfig.name],
  ogLocale: ARTICLE.locale === "es" ? "es_PA" : undefined,
});

export default function ArticlePage() {
  const path = `/articles/${ARTICLE.slug}`;

  const jsonLd = [
    breadcrumbJsonLd([
      { name: ARTICLE.locale === "es" ? "Inicio" : "Home", path: ARTICLE.locale === "es" ? "/es" : "/" },
      { name: ARTICLE.breadcrumb[ARTICLE.breadcrumb.length - 1], path },
    ]),
    articleJsonLd({
      headline: ARTICLE.title,
      description: ARTICLE.description,
      path,
      image: HERO_IMAGE,
      datePublished: ARTICLE.publishedAt,
      dateModified: ARTICLE.modifiedAt,
      locale: ARTICLE.locale,
      section: ARTICLE.section,
    }),
    faqPageJsonLd([...FAQ_ITEMS]),
  ];

  return (
    <>
      {jsonLd.map((data, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={jsonLdScript(data)}
        />
      ))}

      {ARTICLE.locale === "es" && <HtmlLang lang="es" />}

      {/* The theme lives here. Blue = no data-theme. Green = data-theme="green". */}
      <main className="article-page">
        <ReadingProgress />

        {/* ===== HERO ============================================================
            Full-bleed parallax photo with floating tag pills. Per page: the
            HERO_IMAGE and ARTICLE.heroTags. */}
        <ArticleHero bgImage={HERO_IMAGE} locale={ARTICLE.locale}>
          <div className="art-hero-pills">
            {ARTICLE.heroTags.map((tag) => (
              <span key={tag} className="art-hero-tag">
                {tag}
              </span>
            ))}
          </div>
        </ArticleHero>

        {/* ===== HEAD ============================================================
            Breadcrumb, headline, dek, byline, and the FACT CARD on the right.
            The FACT CARD is an "at a glance" info panel — generic key/value rows
            plus rating bars. Reuse it for any subject; just change the labels. */}
        <section className="art-head-section">
          <div className="container">
            <nav className="breadcrumb" aria-label="Breadcrumb">
              <Link href="/">Home</Link>
              {ARTICLE.breadcrumb.map((crumb) => (
                <span key={crumb} style={{ display: "contents" }}>
                  <span className="sep">/</span>
                  <span>{crumb}</span>
                </span>
              ))}
            </nav>

            <div className="art-head">
              <div>
                <h1 className="art-title">
                  Boquete — the highland town that runs quietly on{" "}
                  <em>coffee, rivers, and fog.</em>
                </h1>
                <p className="art-dek">
                  Panama&rsquo;s favorite mountain escape sits in a green bowl an
                  hour above the heat. Here is how to reach it, when to come, and
                  what actually earns a place on your days.
                </p>

                <div className="art-byline">
                  <div className="byline-photo">P</div>
                  <div className="byline-meta">
                    <div className="name">{siteConfig.name}</div>
                    <div className="role">
                      Editorial · Chiriquí highlands
                    </div>
                  </div>
                  <div className="byline-stats">
                    <span>
                      <strong>9 min</strong> read
                    </span>
                    <span>
                      <time dateTime={ARTICLE.modifiedAt}>
                        <strong>May 26</strong> · 2026
                      </time>
                    </span>
                  </div>
                </div>
              </div>

              {/* FACT CARD — sticky "at a glance" panel. Rows are free-form
                  key/value; the rating bars are 0–5 (see <Bar/> at the bottom). */}
              <aside className="fact-card">
                <h4>At a glance</h4>
                <div className="fact-row">
                  <span className="k">Region</span>
                  <span className="v">Chiriquí</span>
                </div>
                <div className="fact-row">
                  <span className="k">Elevation</span>
                  <span className="v">1,200 m</span>
                </div>
                <div className="fact-row">
                  <span className="k">Getting there</span>
                  <span className="v">1 hr from DAV</span>
                </div>
                <div className="fact-row">
                  <span className="k">Best months</span>
                  <span className="v">Dec–Apr</span>
                </div>
                <div className="fact-row">
                  <span className="k">Stay</span>
                  <span className="v">2–3 nights</span>
                </div>
                <div className="fact-row">
                  <span className="k">Language</span>
                  <span className="v">ES / EN</span>
                </div>
                <div className="fact-rating">
                  <span className="lbl">Cost</span>
                  <Bar on={2} />
                  <span className="lbl">Crowds</span>
                  <Bar on={3} />
                  <span className="lbl">Nature</span>
                  <Bar on={5} />
                  <span className="lbl">Family-friendly</span>
                  <Bar on={4} />
                </div>
              </aside>
            </div>
          </div>
        </section>

        {/* ===== BODY ============================================================
            Three columns: sticky TOC · prose · info-card rail.
            The PROSE column is where the long-form copy lives. It can contain
            any mix of: paragraphs, <h2 id>/<h3> headings, .callout boxes,
            .fig figures, .pullquote, .compare tables, and lists. */}
        <div className="container">
          <div className="art-body">
            <ArticleToc items={TOC_ITEMS} />

            <article className="prose">
              {/* LEDE — first paragraph; the drop-cap is automatic. */}
              <p className="lede">
                You feel Boquete before you see it. The road climbs out of the
                David heat, the air turns to something you&rsquo;d describe as
                green, and somewhere around the last bend the valley opens into a
                bowl of coffee farms, flower gardens, and a river that never
                quite stops being loud.
              </p>

              <p>
                This guide assumes you have never been. It is built to answer the
                questions you&rsquo;ll actually have, in the order you&rsquo;ll
                have them — and to leave out the filler.
              </p>

              <h2 id="s1">
                <span className="num">Section 01</span>Why go
              </h2>

              <p>
                Boquete is the easiest highland in Panama to fall for. It is cool
                year-round, walkable, and surrounded by more to do than a long
                weekend can hold: cloud-forest trails, single-origin coffee,
                white-water on the Chiriquí Viejo, and some of the best birding
                in Central America.
              </p>

              {/* CALLOUT — a highlighted tip/aside. Use plain for info, add
                  className="callout warning" for a caution box. */}
              <div className="callout">
                <span className="label">Field note · The shoulder months</span>
                The crowds peak around the January coffee-and-flower fair. Come a
                few weeks on either side and you get the same weather with half
                the traffic and easier rooms.
              </div>

              {/* FIGURE — a single captioned image. Use .imgph.photo for a real
                  photo; the tinted .imgph variants are placeholders. */}
              <figure className="fig">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(2918139)}')` }}
                />
                <figcaption>
                  <span>
                    <strong>The valley from above.</strong> Coffee terraces give
                    way to cloud forest on the higher slopes.
                  </span>
                </figcaption>
              </figure>

              <h2 id="s2">
                <span className="num">Section 02</span>Getting there
              </h2>

              <p>
                The gateway is David (DAV), the regional capital. From Panama
                City it&rsquo;s a short flight or an overnight bus; from David
                it&rsquo;s about an hour up into the hills by car, shuttle, or
                the cheap-and-cheerful public bus.
              </p>

              {/* COMPARE TABLE — generic options compared across columns.
                  Reuse for transport, tours, room types, anything ranked.
                  Pills: .good / .mid / .bad. */}
              <table className="compare">
                <thead>
                  <tr>
                    <th>Route in</th>
                    <th>From</th>
                    <th>Cost</th>
                    <th>Time</th>
                    <th>Comfort</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Flight + shuttle</td>
                    <td>Panama City</td>
                    <td>$110–$165</td>
                    <td>1 h + 1 h</td>
                    <td>
                      <span className="pill good">Easiest</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Overnight bus</td>
                    <td>Albrook terminal</td>
                    <td>$19</td>
                    <td>7 hours</td>
                    <td>
                      <span className="pill mid">Cold AC</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Self-drive</td>
                    <td>Panama City</td>
                    <td>$60–$90 fuel</td>
                    <td>6.5 hours</td>
                    <td>
                      <span className="pill mid">Long</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Public bus up</td>
                    <td>David</td>
                    <td>$2</td>
                    <td>1 hour</td>
                    <td>
                      <span className="pill good">Cheap</span>
                    </td>
                  </tr>
                </tbody>
              </table>

              <h2 id="s3">
                <span className="num">Section 03</span>When to visit
              </h2>

              <p>
                The dry season — roughly mid-December to mid-April — is the
                reliable window for clear mornings and open trails. The green
                season is quieter and cheaper, with afternoon rain you can plan
                around. The month-by-month panel in the right rail breaks it
                down.
              </p>

              <h2 id="s4">
                <span className="num">Section 04</span>Where to stay
              </h2>

              <p>
                Pick your base by mood. Town puts you steps from cafés and tour
                offices; the valley roads above town trade walkability for views
                and birdsong. A short, honest range:
              </p>

              <ul>
                <li>
                  <strong>In town:</strong> small guesthouses and hostels, easy
                  to reach on foot, from about $40.
                </li>
                <li>
                  <strong>Up the valley:</strong> garden lodges and cabins with
                  the views, roughly $90–$160.
                </li>
                <li>
                  <strong>On a farm:</strong> a handful of coffee estates rent
                  rooms — quiet, memorable, book ahead.
                </li>
              </ul>

              <h2 id="s5">
                <span className="num">Section 05</span>What to do
              </h2>

              <p>
                More than fits a weekend. Walk a cloud-forest trail in the
                morning, tour a coffee farm after lunch, soak in the hot springs,
                or chase the resplendent quetzal with a guide. The gallery below
                is a quick taste; the highlight cards under it cover the
                logistics.
              </p>

              {/* IN-COLUMN BENTO — a compact accent mosaic to break up the text.
                  Mix a photo tile, a solid-accent stat tile, and an outlined
                  text tile. Drop it anywhere inside the prose column. */}
              <div className="prose-bento">
                <div className="pb-tile pb-img pb-tall">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(10343761)}')` }}
                  />
                  <span className="pb-cap">Cloud-forest trails from town</span>
                </div>
                <div className="pb-tile pb-accent">
                  <span className="pb-stat">10+</span>
                  <span className="pb-label">marked trails nearby</span>
                </div>
                <div className="pb-tile pb-outline">
                  <h4>Coffee tours</h4>
                  <p>Farm-to-cup tastings on the slopes most mornings.</p>
                </div>
              </div>

              <h2 id="s6">
                <span className="num">Section 06</span>Know before you go
              </h2>

              <p>
                The basics that save a trip: bring a rain layer regardless of
                season, carry small bills for buses and markets, and download an
                offline map — signal thins out fast once you leave town. Tap
                water is fine. Tipping is appreciated, not expected.
              </p>

              {/* IN-COLUMN PANEL — accent-tinted checklist. Reuse for key
                  takeaways, essentials, or do/don't lists. */}
              <div className="prose-panel">
                <h4>Pack-and-go checklist</h4>
                <ul>
                  <li>A light rain shell — the highlands make their own weather.</li>
                  <li>Small bills for buses, markets, and colectivos.</li>
                  <li>An offline map; the signal thins out past town.</li>
                  <li>A warm layer for cool highland evenings.</li>
                </ul>
              </div>
            </article>

            {/* INFO-CARD RAIL — the "informative cards" on the right. Each is an
                .aside-card. Reuse the pattern for any small panel: a calendar,
                a budget figure, a credibility note, a mini-checklist. */}
            <aside className="aside">
              {/* BEST-TIME CALENDAR — 12 rows of [month, temp, status].
                  status drives the dot color: go / maybe / skip. */}
              <div className="aside-card">
                <h5>Best time · 12-month view</h5>
                {(
                  [
                    ["Jan", "13°/24°", "go"],
                    ["Feb", "13°/25°", "go"],
                    ["Mar", "14°/26°", "go"],
                    ["Apr", "15°/26°", "go"],
                    ["May", "16°/25°", "maybe"],
                    ["Jun", "16°/24°", "skip"],
                    ["Jul", "16°/24°", "skip"],
                    ["Aug", "16°/24°", "skip"],
                    ["Sep", "15°/24°", "skip"],
                    ["Oct", "15°/23°", "skip"],
                    ["Nov", "14°/23°", "maybe"],
                    ["Dec", "13°/24°", "go"],
                  ] as [string, string, "go" | "maybe" | "skip"][]
                ).map(([month, temp, status]) => (
                  <div key={month} className="weather-row">
                    <span className="month">{month}</span>
                    <span className="temp">{temp}</span>
                    <span className={`dot ${status}`} />
                  </div>
                ))}
                <p
                  style={{
                    marginTop: 14,
                    fontSize: 10,
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    color: "var(--ink-mute)",
                  }}
                >
                  ● go &nbsp; ● caution &nbsp; ● skip
                </p>
              </div>

              {/* STAT CARD — one big number plus a sentence of context. */}
              <div className="aside-card">
                <h5>Typical daily budget</h5>
                <div className="stat">$85</div>
                <p>
                  Mid-range room, local meals, transport, and one paid activity.
                  Excludes the flight or bus into Chiriquí.
                </p>
              </div>

              {/* CREDIBILITY CARD — who checked this. Good for E-E-A-T / trust. */}
              <div className="aside-card">
                <h5>Reviewed on the ground</h5>
                <p style={{ fontSize: 18, lineHeight: 1.3, marginBottom: 12 }}>
                  Certified guides and longtime residents in Boquete
                </p>
                <p style={{ fontSize: 12 }}>Reviewed: April 28, 2026</p>
              </div>
            </aside>
          </div>
        </div>

        {/* ===== GALLERY =========================================================
            Full-width photo grid. First item is the large feature tile; the
            rest fill the row. Data comes from GALLERY at the top of the file. */}
        <section className="art-section">
          <div className="container">
            <div className="art-section-head">
              <span className="eyebrow">In pictures</span>
              <h2>What it actually looks like</h2>
              <p>A walk through town and the slopes above it, in five frames.</p>
            </div>
            <div className="art-gallery-grid">
              {GALLERY.map((photo) => (
                <figure key={photo.src} className={"feature" in photo && photo.feature ? "feature" : undefined}>
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${photo.src}')` }}
                  />
                  <figcaption>{photo.caption}</figcaption>
                </figure>
              ))}
            </div>
          </div>
        </section>

        {/* ===== STATEMENT ======================================================
            A full-bleed "rich text" beat — the same role the gallery plays, but
            words instead of photos. Swap its position with the gallery or any
            other full-width section to vary the column / full-width rhythm. */}
        <section className="art-statement">
          <div className="container">
            <div className="art-statement-inner">
              <blockquote>
                The highlands keep their own clock. The fog comes up the valley
                most afternoons like it has somewhere to be, and the whole town
                slows to watch it.
              </blockquote>
              <cite>— from the field notebook</cite>
            </div>
          </div>
        </section>

        {/* ===== HIGHLIGHT CARDS =================================================
            Full-width informative cards. The `.tint` on the section gives it a
            faint accent wash so it reads as its own band. Data: HIGHLIGHTS. */}
        <section className="art-section tint">
          <div className="container">
            <div className="art-section-head">
              <span className="eyebrow">The short version</span>
              <h2>Three things to know</h2>
            </div>
            <div className="art-highlights-grid">
              {HIGHLIGHTS.map((card) => (
                <div key={card.title} className="art-highlight-card">
                  <span className="kicker">Good to know</span>
                  <div className="stat">{card.stat}</div>
                  <h3>{card.title}</h3>
                  <p>{card.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ===== BENTO ===========================================================
            A varied "mosaic" of cards for related links / highlights — same
            markup as the homepage bento, retinted to the page theme. Mix image
            tiles (b1/b3/b5), a quote (b2), and a text CTA (b4). */}
        <section className="art-section">
          <div className="container">
            <div className="art-section-head">
              <span className="eyebrow">Around the valley</span>
              <h2>More of Chiriquí</h2>
            </div>
            <div className="home-bento-grid">
              {/* b1 — image-top card with text below */}
              <div className="bento-card b1">
                <div className="bento-img-top">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(10343761)}')` }}
                  />
                </div>
                <div className="bento-body">
                  <span className="b-tag">Outdoors</span>
                  <h3>Cloud-forest trails on the doorstep</h3>
                  <p>
                    From gentle river loops to the famous high-country crossing,
                    the trailheads start where the streets end.
                  </p>
                </div>
              </div>

              {/* b2 — pull-quote tile */}
              <div className="bento-card b2">
                <span className="b-tag">From the valley</span>
                <blockquote>
                  You come for a weekend and start pricing the cost of staying.
                  Everyone here did exactly that once.
                </blockquote>
                <cite>— Bajo Boquete</cite>
              </div>

              {/* b3 — image tile with overlay caption */}
              <div className="bento-card b3">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(30658818)}')` }}
                />
                <div className="bento-overlay">
                  <span className="b-tag">Coffee</span>
                  <h3>Farm tours</h3>
                </div>
              </div>

              {/* b4 — text CTA tile */}
              <div className="bento-card b4">
                <span className="b-tag">Plan</span>
                <h3>Build a 3-day Chiriquí itinerary.</h3>
                <span className="bento-arrow">Coming soon</span>
              </div>

              {/* b5 — split image/text card */}
              <div className="bento-card b5">
                <div className="bento-split-img">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(9566563)}')` }}
                  />
                </div>
                <div className="bento-split-body">
                  <span className="b-tag">Wildlife</span>
                  <h3>Birding &amp; the quetzal</h3>
                  <p>
                    The highlands are one of the most reliable places on earth to
                    see a resplendent quetzal — go early, with a guide.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ===== FAQ =============================================================
            Accordion of common questions. Also emitted as FAQPage JSON-LD up
            top, so keep FAQ_ITEMS and these in sync (they share the same data). */}
        <section className="art-section tint">
          <div className="container">
            <div className="art-section-head">
              <span className="eyebrow">Questions</span>
              <h2>Before you book</h2>
            </div>
            <div className="faq" style={{ margin: 0, padding: 0 }}>
              {FAQ_ITEMS.map((item, i) => (
                <FaqItem
                  key={item.question}
                  defaultOpen={i === 0}
                  q={item.question}
                  a={item.answer}
                />
              ))}
            </div>
          </div>
        </section>
      </main>

      <SiteFooter locale={ARTICLE.locale} />
    </>
  );
}

/* ── Rating bar — fills `on` of 5 cells. Used in the FACT CARD. ── */
function Bar({ on }: { on: number }) {
  return (
    <span className="bar">
      {[0, 1, 2, 3, 4].map((i) => (
        <i key={i} className={i < on ? "on" : ""} />
      ))}
    </span>
  );
}
