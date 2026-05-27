/* ============================================================================
   PAGE TEMPLATE — "Destination guide"  (GREEN theme)
   ----------------------------------------------------------------------------
   This is the blue template (src/app/articles/sendero-los-quetzales/page.tsx)
   duplicated and re-skinned green, on a different subject (Bocas del Toro). It
   proves the same skeleton handles a totally different place + palette.

   The ONLY structural difference from the blue page is on <main>:
       <main className="article-page" data-theme="green">
   That one attribute swaps the CSS tokens — green --accent, amber --pop, and a
   plain beige background instead of the white→cream gradient. Everything else
   is identical, so read the blue file for the full per-section documentation.

   Sections, in order:
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

const pexels = (id: number, w = 1600) =>
  `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${w}`;

/* ════════════════════════════════════════════════════════════════════════
   CONFIG
   ════════════════════════════════════════════════════════════════════════ */
const SLUG = "bocas-del-toro";
const HERO_IMAGE = pexels(2038744, 2000);

const ARTICLE = {
  slug: SLUG,
  // LOCALE — "en" (root, /articles/…) or "es" (/es/articles/…). Drives the
  // header/footer language, og:locale, schema inLanguage and <html lang>.
  locale: "en" as "en" | "es",
  // seoTitle → the <title> tag. Keep it keyword-led and ~60 chars for search.
  seoTitle: "Bocas del Toro Travel Guide: Islands, Things to Do & Tips",
  // title → the visible <h1>. Can be more narrative/editorial than seoTitle.
  title: "Bocas del Toro — nine islands that keep island time, on purpose.",
  description:
    "A complete guide to Bocas del Toro, Panama's Caribbean archipelago: how to get there, when to go, where to stay across the islands, and what's worth doing on the water.",
  // articleSection → topic/category for Article schema.
  section: "Destinations",
  publishedAt: "2026-05-26",
  modifiedAt: "2026-05-26",
  breadcrumb: ["Caribbean", "Islands", "Bocas del Toro"],
  heroTags: ["Caribbean", "Destination guide", "Updated · May 2026"],
} as const;

const TOC_ITEMS = [
  { id: "s1", n: "01", label: "Why go" },
  { id: "s2", n: "02", label: "Getting there" },
  { id: "s3", n: "03", label: "When to visit" },
  { id: "s4", n: "04", label: "Where to stay" },
  { id: "s5", n: "05", label: "What to do" },
  { id: "s6", n: "06", label: "Know before you go" },
  { id: "s7", n: "07", label: "FAQ" },
];

const GALLERY = [
  { src: pexels(14185535), caption: "Stilted cabins over turquoise water", feature: true },
  { src: pexels(4766708), caption: "Mangrove channels between the islands" },
  { src: pexels(33757647), caption: "Caribbean reef breaks, year-round" },
  { src: pexels(8951333), caption: "Empty beaches a boat ride away" },
  { src: pexels(4171716), caption: "Slow water, slower afternoons" },
] as const;

const HIGHLIGHTS = [
  { stat: "9", title: "Islands to roam", body: "The archipelago is a cluster of nine main islands and dozens of cays — every dock is a different day trip." },
  { stat: "~25 min", title: "By air from the capital", body: "Small flights drop you onto Isla Colón; the alternative is a long bus-plus-boat haul across the country." },
  { stat: "$$", title: "Backpacker-friendly", body: "One of Panama's better-value spots — water taxis are cheap and rooms run from hostel dorms to over-water suites." },
] as const;

const FAQ_ITEMS = [
  {
    question: "How do I get between the islands?",
    answer:
      "Water taxis. They run constantly between the main town on Isla Colón and the other islands for a few dollars a hop — no need to book ahead for the common routes.",
  },
  {
    question: "How many days should I plan?",
    answer:
      "Three to four nights. The town is worth a day, but the archipelago rewards a slower pace — give yourself time for a beach day, a snorkel trip, and at least one island you can't reach in a rush.",
  },
  {
    question: "Is the water always clear?",
    answer:
      "It varies by island and season. The Caribbean side is clearest in the drier spells; after heavy rain, runoff can cloud the channels near the mangroves for a day or two.",
  },
  {
    question: "Is English spoken?",
    answer:
      "Yes, widely — Bocas has a strong Afro-Antillean heritage and English (and Guari-Guari creole) is common alongside Spanish.",
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

      {/* data-theme="green" → green accent + pop, plain cream background. */}
      <main className="article-page" data-theme="green">
        <ReadingProgress />

        {/* ===== HERO ===== */}
        <ArticleHero bgImage={HERO_IMAGE} locale={ARTICLE.locale}>
          <div className="art-hero-pills">
            {ARTICLE.heroTags.map((tag) => (
              <span key={tag} className="art-hero-tag">
                {tag}
              </span>
            ))}
          </div>
        </ArticleHero>

        {/* ===== HEAD + FACT CARD ===== */}
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
                  Bocas del Toro — nine islands that keep{" "}
                  <em>island time, on purpose.</em>
                </h1>
                <p className="art-dek">
                  Panama&rsquo;s Caribbean archipelago runs on water taxis and
                  warm afternoons. Here is how to reach it, when to come, and how
                  to spread your days across the islands.
                </p>

                <div className="art-byline">
                  <div className="byline-photo">P</div>
                  <div className="byline-meta">
                    <div className="name">{siteConfig.name}</div>
                    <div className="role">
                      Editorial · Caribbean coast
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

              <aside className="fact-card">
                <h4>At a glance</h4>
                <div className="fact-row">
                  <span className="k">Region</span>
                  <span className="v">Caribbean</span>
                </div>
                <div className="fact-row">
                  <span className="k">Islands</span>
                  <span className="v">9 main</span>
                </div>
                <div className="fact-row">
                  <span className="k">Getting there</span>
                  <span className="v">~25 min flight</span>
                </div>
                <div className="fact-row">
                  <span className="k">Best months</span>
                  <span className="v">Feb–Apr · Sep</span>
                </div>
                <div className="fact-row">
                  <span className="k">Stay</span>
                  <span className="v">3–4 nights</span>
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
                  <span className="lbl">Beaches</span>
                  <Bar on={5} />
                  <span className="lbl">Nightlife</span>
                  <Bar on={4} />
                </div>
              </aside>
            </div>
          </div>
        </section>

        {/* ===== BODY ===== */}
        <div className="container">
          <div className="art-body">
            <ArticleToc items={TOC_ITEMS} />

            <article className="prose">
              <p className="lede">
                Bocas runs on water. You arrive, you drop your bag, and within an
                hour you&rsquo;ve learned the only schedule that matters here is
                the next water taxi — and that it leaves more or less whenever the
                boat is full.
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
                The archipelago is the easy Caribbean: warm water, a string of
                islands you hop by boat, Afro-Antillean kitchens, and a town that
                stays up late. It&rsquo;s the country&rsquo;s most relaxed place
                to wake up on the water — and one of its best values.
              </p>

              <div className="callout">
                <span className="label">Field note · Base smart</span>
                Sleep in the main town for the boats and the nightlife, or on a
                quieter island for the calm — but don&rsquo;t split your stay too
                thin. Moving every night eats the days you came for.
              </div>

              <figure className="fig">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(14185535)}')` }}
                />
                <figcaption>
                  <span>
                    <strong>Over-water cabins.</strong> Half the lodgings here sit
                    on stilts above the shallows.
                  </span>
                </figcaption>
              </figure>

              <h2 id="s2">
                <span className="num">Section 02</span>Getting there
              </h2>

              <p>
                The quick way is to fly: small planes from Panama City land on
                Isla Colón in well under an hour. The overland route is cheaper
                but long — a bus across the country to Almirante, then a short
                boat across the lagoon.
              </p>

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
                    <td>Direct flight</td>
                    <td>Panama City</td>
                    <td>$120–$180</td>
                    <td>~25 min</td>
                    <td>
                      <span className="pill good">Easiest</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Bus + water taxi</td>
                    <td>Albrook terminal</td>
                    <td>$30–$35</td>
                    <td>10–11 hrs</td>
                    <td>
                      <span className="pill mid">Long haul</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Via David</td>
                    <td>Chiriquí</td>
                    <td>$15 + boat</td>
                    <td>4–5 hrs</td>
                    <td>
                      <span className="pill mid">Scenic</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Water taxi hops</td>
                    <td>Almirante</td>
                    <td>$6</td>
                    <td>30 min</td>
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
                The Caribbean side keeps its own weather. The clearest, driest
                stretches are usually February–April and a short window around
                September. The rest of the year sees more rain, but it tends to
                pass quickly. The month-by-month panel is in the right rail.
              </p>

              <h2 id="s4">
                <span className="num">Section 04</span>Where to stay
              </h2>

              <p>
                Choose your island, then your vibe. The main town has the boats,
                bars, and budget rooms; the outer islands trade convenience for
                quiet water and better snorkeling off the dock.
              </p>

              <ul>
                <li>
                  <strong>Isla Colón (town):</strong> hostels and guesthouses,
                  walkable, closest to the boats, from about $15 a dorm bed.
                </li>
                <li>
                  <strong>Bastimentos &amp; Carenero:</strong> over-water cabins
                  and small lodges, calmer, roughly $60–$200.
                </li>
                <li>
                  <strong>Outer cays:</strong> a few remote eco-lodges — book
                  well ahead and plan your boat transfers.
                </li>
              </ul>

              <h2 id="s5">
                <span className="num">Section 05</span>What to do
              </h2>

              <p>
                Snorkel the reefs, surf the breaks, kayak the mangroves, or just
                island-hop with no fixed plan. The gallery below is a quick taste;
                the highlight cards under it cover the logistics.
              </p>

              {/* IN-COLUMN BENTO — compact accent mosaic (see blue template). */}
              <div className="prose-bento">
                <div className="pb-tile pb-img pb-tall">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(33757647)}')` }}
                  />
                  <span className="pb-cap">Reef breaks &amp; snorkel spots</span>
                </div>
                <div className="pb-tile pb-accent">
                  <span className="pb-stat">9</span>
                  <span className="pb-label">islands to hop</span>
                </div>
                <div className="pb-tile pb-outline">
                  <h4>Mangrove runs</h4>
                  <p>Kayak the calm channels between the cays.</p>
                </div>
              </div>

              <h2 id="s6">
                <span className="num">Section 06</span>Know before you go
              </h2>

              <p>
                The basics: carry small bills for water taxis, bring reef-safe
                sunscreen, and don&rsquo;t count on fast internet. Drink bottled
                or filtered water on the outer islands. Afternoon rain is normal
                — keep your plans flexible and your electronics dry.
              </p>

              {/* IN-COLUMN PANEL — accent-tinted checklist (see blue template). */}
              <div className="prose-panel">
                <h4>Island essentials</h4>
                <ul>
                  <li>Small bills for water taxis between the islands.</li>
                  <li>Reef-safe sunscreen — the reefs are close and shallow.</li>
                  <li>A dry bag for boat hops and afternoon rain.</li>
                  <li>Bottled or filtered water on the outer cays.</li>
                </ul>
              </div>
            </article>

            <aside className="aside">
              {/* BEST-TIME CALENDAR */}
              <div className="aside-card">
                <h5>Best time · 12-month view</h5>
                {(
                  [
                    ["Jan", "24°/30°", "maybe"],
                    ["Feb", "24°/31°", "go"],
                    ["Mar", "24°/31°", "go"],
                    ["Apr", "25°/31°", "go"],
                    ["May", "25°/31°", "maybe"],
                    ["Jun", "24°/30°", "skip"],
                    ["Jul", "24°/30°", "skip"],
                    ["Aug", "24°/31°", "maybe"],
                    ["Sep", "24°/31°", "go"],
                    ["Oct", "24°/30°", "skip"],
                    ["Nov", "24°/30°", "skip"],
                    ["Dec", "24°/30°", "maybe"],
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

              {/* STAT CARD */}
              <div className="aside-card">
                <h5>Typical daily budget</h5>
                <div className="stat">$60</div>
                <p>
                  Guesthouse room, local meals, water taxis, and a snorkel trip.
                  Excludes the flight or bus into Bocas.
                </p>
              </div>

              {/* CREDIBILITY CARD */}
              <div className="aside-card">
                <h5>Reviewed on the ground</h5>
                <p style={{ fontSize: 18, lineHeight: 1.3, marginBottom: 12 }}>
                  Boat captains and longtime residents on Isla Colón
                </p>
                <p style={{ fontSize: 12 }}>Reviewed: May 12, 2026</p>
              </div>
            </aside>
          </div>
        </div>

        {/* ===== GALLERY ===== */}
        <section className="art-section">
          <div className="container">
            <div className="art-section-head">
              <span className="eyebrow">In pictures</span>
              <h2>What it actually looks like</h2>
              <p>Town, water, and the islands a taxi-boat away — in five frames.</p>
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

        {/* ===== STATEMENT ===== full-bleed rich-text beat (see blue template) */}
        <section className="art-statement">
          <div className="container">
            <div className="art-statement-inner">
              <blockquote>
                Nobody hurries in Bocas, and after a day you stop trying to. The
                boats leave when they leave; the afternoon rain comes and goes;
                you learn to like the gaps.
              </blockquote>
              <cite>— from the field notebook</cite>
            </div>
          </div>
        </section>

        {/* ===== HIGHLIGHT CARDS ===== */}
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

        {/* ===== BENTO ===== */}
        <section className="art-section">
          <div className="container">
            <div className="art-section-head">
              <span className="eyebrow">Around the archipelago</span>
              <h2>More of Bocas</h2>
            </div>
            <div className="home-bento-grid">
              <div className="bento-card b1">
                <div className="bento-img-top">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(33757647)}')` }}
                  />
                </div>
                <div className="bento-body">
                  <span className="b-tag">Water</span>
                  <h3>Reefs, breaks, and mangrove runs</h3>
                  <p>
                    Snorkel the coral gardens, paddle the mangroves, or chase the
                    Caribbean swell — all a short boat ride from town.
                  </p>
                </div>
              </div>

              <div className="bento-card b2">
                <span className="b-tag">From the islands</span>
                <blockquote>
                  The boat leaves when the boat is full. You can fight it for a
                  day, and then you join everyone else and slow down.
                </blockquote>
                <cite>— Isla Colón</cite>
              </div>

              <div className="bento-card b3">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(8951333)}')` }}
                />
                <div className="bento-overlay">
                  <span className="b-tag">Beaches</span>
                  <h3>Red Frog &amp; beyond</h3>
                </div>
              </div>

              <div className="bento-card b4">
                <span className="b-tag">Plan</span>
                <h3>Map a 4-day island-hop.</h3>
                <span className="bento-arrow">Coming soon</span>
              </div>

              <div className="bento-card b5">
                <div className="bento-split-img">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(4766708)}')` }}
                  />
                </div>
                <div className="bento-split-body">
                  <span className="b-tag">Slow travel</span>
                  <h3>Mangroves &amp; cays</h3>
                  <p>
                    Beyond the main islands, a maze of mangrove channels and
                    near-empty cays rewards anyone willing to hire a boat.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ===== FAQ ===== */}
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

function Bar({ on }: { on: number }) {
  return (
    <span className="bar">
      {[0, 1, 2, 3, 4].map((i) => (
        <i key={i} className={i < on ? "on" : ""} />
      ))}
    </span>
  );
}
