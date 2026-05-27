/* ============================================================================
   El Valle de Antón — destination guide (GREEN theme)
   Built from the green template (articles/bocas-del-toro). Same layout and
   sections, green palette via data-theme="green"; different subject + photos.
   ========================================================================== */

import type { Metadata } from "next";
import Link from "next/link";
import { buildMetadata } from "@/lib/seo";
import { articleJsonLd, breadcrumbJsonLd, faqPageJsonLd, jsonLdScript } from "@/lib/jsonld";
import { ReadingProgress } from "@/components/reading-progress";
import { ArticleHero } from "@/components/article-hero";
import { ArticleToc } from "@/components/article-toc";
import { FaqItem } from "@/components/faq-item";
import { SiteFooter } from "@/components/site-footer";
import { HtmlLang } from "@/components/html-lang";

const pexels = (id: number, w = 1600) =>
  `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${w}`;

const SLUG = "el-valle-de-anton";
const HERO_IMAGE = pexels(30774416, 2000);

const ARTICLE = {
  slug: SLUG,
  locale: "en" as "en" | "es",
  seoTitle: "El Valle de Antón Travel Guide: Hikes, Hot Springs & Markets",
  title: "El Valle de Antón — a green town that lives inside an extinct volcano.",
  description:
    "A complete guide to El Valle de Antón, the town inside a volcanic crater: how to get there, when to go, where to stay, and what to do — from La India Dormida to the Sunday market.",
  section: "Destinations",
  publishedAt: "2026-05-26",
  modifiedAt: "2026-05-26",
  author: "Mariela Ortiz-Saavedra",
  breadcrumb: ["Coclé", "Highland towns", "El Valle de Antón"],
  heroTags: ["Highlands", "Day trip", "Updated · May 2026"],
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
  { src: pexels(14714541), caption: "The valley floor from the crater rim", feature: true },
  { src: pexels(30774409), caption: "The ridgeline trail of La India Dormida" },
  { src: pexels(7823008), caption: "First light over the green hills" },
  { src: pexels(4956963), caption: "Cloud catching on the peaks" },
  { src: pexels(30774398), caption: "Slow mornings in the town cafés" },
] as const;

const HIGHLIGHTS = [
  { stat: "1", title: "Town in a crater", body: "El Valle sits on the floor of an extinct volcano — one of the few inhabited volcanic craters anywhere, ringed by green walls on every side." },
  { stat: "2.5 hr", title: "From the capital", body: "A direct bus from Panama City's Albrook terminal, or an easy drive off the Interamericana — close enough for a long day trip." },
  { stat: "$3", title: "Cheap to explore", body: "Most of the headline sights — the India Dormida hike and the hot springs — cost about three dollars to enter." },
] as const;

const FAQ_ITEMS = [
  {
    question: "Day trip or overnight?",
    answer:
      "Both work. El Valle is doable as a long day trip from Panama City — two and a half hours each way — but a night lets you catch the Sunday market early and hike before the midday heat without rushing.",
  },
  {
    question: "Is the India Dormida hike hard?",
    answer:
      "It's short — about 3 km round trip, roughly two hours — but steep in places. The $3 trail rewards you with ancient petroglyphs, small waterfalls, and ridge-top views over the whole crater. Wear proper shoes and bring water.",
  },
  {
    question: "When is the market?",
    answer:
      "El Valle's handicraft and produce market runs daily but is biggest and liveliest on Sunday mornings, roughly 7 a.m. to 2 p.m. — indigenous vendors sell orchids, baskets, ceramics, molas and fresh fruit.",
  },
  {
    question: "Can you actually soak in the hot springs?",
    answer:
      "Yes. The pozos termales are warm mineral pools (about $3, including a do-it-yourself mud facial). They're more warm than hot — the volcano is long extinct — but the mineral mud is the point.",
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
  authors: [ARTICLE.author],
  ogLocale: ARTICLE.locale === "es" ? "es_PA" : undefined,
  languages: {
    en: `/articles/${ARTICLE.slug}`,
    es: `/es/articles/${ARTICLE.slug}`,
  },
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
      authorName: ARTICLE.author,
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
        <ArticleHero
          bgImage={HERO_IMAGE}
          locale={ARTICLE.locale}
          esHref={`/es/articles/${ARTICLE.slug}`}
        >
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
                  El Valle de Antón — a green town that lives inside an{" "}
                  <em>extinct volcano.</em>
                </h1>
                <p className="art-dek">
                  Two hours from Panama City, the world&rsquo;s largest inhabited
                  volcanic crater hides waterfalls, hot springs, a Sunday market,
                  and the cool air the capital wishes it had.
                </p>

                <div className="art-byline">
                  <div className="byline-photo">M</div>
                  <div className="byline-meta">
                    <div className="name">{ARTICLE.author}</div>
                    <div className="role">
                      Field reporter · Coclé · 14 years on the ground
                    </div>
                  </div>
                  <div className="byline-stats">
                    <span>
                      <strong>8 min</strong> read
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
                  <span className="v">Coclé</span>
                </div>
                <div className="fact-row">
                  <span className="k">Setting</span>
                  <span className="v">Volcanic crater</span>
                </div>
                <div className="fact-row">
                  <span className="k">Elevation</span>
                  <span className="v">~600 m</span>
                </div>
                <div className="fact-row">
                  <span className="k">Getting there</span>
                  <span className="v">2.5 hr from city</span>
                </div>
                <div className="fact-row">
                  <span className="k">Stay</span>
                  <span className="v">1–2 nights</span>
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
                  <Bar on={5} />
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
                The road climbs out of the coastal heat, takes a long curve, and
                drops you onto the floor of a volcano. The walls go up green on
                every side; the air turns ten degrees cooler; and a small town of
                gardens and Sunday markets gets on with its week.
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
                El Valle is the easiest mountain escape from Panama City — one of
                the few towns anywhere built inside a volcanic crater. It&rsquo;s
                cool, green, and walkable, with a ridge hike, warm mineral pools, a
                famous handicraft market, and even a tiny golden frog you won&rsquo;t
                see anywhere else on earth.
              </p>

              <div className="callout">
                <span className="label">Field note · Time it for Sunday</span>
                The handicraft market is busiest and best on Sunday morning. Arrive
                Saturday night and you can hit the market early, then hike before
                the midday sun finds the crater floor.
              </div>

              <figure className="fig">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(30774401)}')` }}
                />
                <figcaption>
                  <span>
                    <strong>The road in.</strong> The winding climb off the
                    Interamericana drops you straight onto the crater floor.
                  </span>
                </figcaption>
              </figure>

              <h2 id="s2">
                <span className="num">Section 02</span>Getting there
              </h2>

              <p>
                It&rsquo;s an easy run from the capital. Direct buses leave Panama
                City&rsquo;s Albrook terminal for the center of town, or you can
                drive the Interamericana west and turn inland past San Carlos for
                the scenic climb up to the crater.
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
                    <td>Direct bus</td>
                    <td>Albrook terminal</td>
                    <td>$4.25</td>
                    <td>~2.5 hrs</td>
                    <td>
                      <span className="pill good">Cheapest</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Self-drive</td>
                    <td>Panama City</td>
                    <td>$25–$40 fuel</td>
                    <td>~2 hrs</td>
                    <td>
                      <span className="pill good">Flexible</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Day tour</td>
                    <td>Panama City</td>
                    <td>$90–$140</td>
                    <td>Full day</td>
                    <td>
                      <span className="pill mid">Guided</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Private transfer</td>
                    <td>Panama City</td>
                    <td>$120+ split</td>
                    <td>~2 hrs</td>
                    <td>
                      <span className="pill good">Door-to-door</span>
                    </td>
                  </tr>
                </tbody>
              </table>

              <h2 id="s3">
                <span className="num">Section 03</span>When to visit
              </h2>

              <p>
                The dry season — roughly mid-December to April — is the reliable
                window for clear ridge hikes. Weekends fill with city folk up for
                the air, the mud baths and the market; come midweek for quiet, or
                Sunday for the market in full swing.
              </p>

              <h2 id="s4">
                <span className="num">Section 04</span>Where to stay
              </h2>

              <p>
                Choose your base by mood. Stay in town to walk to the market and
                cafés; climb the crater rim for views and birdsong and a little
                more quiet.
              </p>

              <ul>
                <li>
                  <strong>In town:</strong> guesthouses and small hotels, walkable
                  to the market and restaurants.
                </li>
                <li>
                  <strong>Up the rim:</strong> garden cabins and eco-lodges with
                  views over the crater floor.
                </li>
                <li>
                  <strong>On the edges:</strong> a few wellness retreats built
                  around the cool climate and the hot springs.
                </li>
              </ul>

              <h2 id="s5">
                <span className="num">Section 05</span>What to do
              </h2>

              <p>
                Hike the ridgeline of La India Dormida past petroglyphs and
                waterfalls; soak and mud-mask in the pozos termales; browse the
                Sunday handicraft market; and meet the endangered Panamanian golden
                frog at the El Níspero conservation center.
              </p>

              {/* IN-COLUMN BENTO */}
              <div className="prose-bento">
                <div className="pb-tile pb-img pb-tall">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(18117801)}')` }}
                  />
                  <span className="pb-cap">La India Dormida ridge trail</span>
                </div>
                <div className="pb-tile pb-accent">
                  <span className="pb-stat">~3 km</span>
                  <span className="pb-label">to the crater-rim views</span>
                </div>
                <div className="pb-tile pb-outline">
                  <h4>Pozos termales</h4>
                  <p>Warm mineral pools and a do-it-yourself mud facial.</p>
                </div>
              </div>

              <h2 id="s6">
                <span className="num">Section 06</span>Know before you go
              </h2>

              <p>
                The basics: it&rsquo;s noticeably cooler than the coast, so bring a
                light layer; carry small bills for the $3 entries and the market;
                and wear real shoes for the trails. Tap water is fine, and Sunday
                is the day to plan around.
              </p>

              {/* IN-COLUMN PANEL */}
              <div className="prose-panel">
                <h4>Crater-day checklist</h4>
                <ul>
                  <li>A light layer — the crater floor is cooler than the coast.</li>
                  <li>Small bills for the $3 trail and hot-spring entries.</li>
                  <li>Proper shoes for the steep, sometimes-muddy India Dormida trail.</li>
                  <li>An early start on Sunday to catch the market at its best.</li>
                </ul>
              </div>
            </article>

            {/* ===== INFO-CARD RAIL ===== */}
            <aside className="aside">
              <div className="aside-card">
                <h5>Best time · 12-month view</h5>
                {(
                  [
                    ["Jan", "17°/27°", "go"],
                    ["Feb", "17°/28°", "go"],
                    ["Mar", "18°/29°", "go"],
                    ["Apr", "18°/29°", "go"],
                    ["May", "18°/27°", "maybe"],
                    ["Jun", "18°/26°", "maybe"],
                    ["Jul", "18°/26°", "maybe"],
                    ["Aug", "18°/26°", "maybe"],
                    ["Sep", "17°/26°", "skip"],
                    ["Oct", "17°/25°", "skip"],
                    ["Nov", "17°/26°", "skip"],
                    ["Dec", "17°/27°", "go"],
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

              <div className="aside-card">
                <h5>Typical daily budget</h5>
                <div className="stat">$70</div>
                <p>
                  Guesthouse room, local meals, trail and hot-spring entries.
                  Excludes the bus or car from Panama City.
                </p>
              </div>

              <div className="aside-card">
                <h5>Locally vetted by</h5>
                <p style={{ fontSize: 18, lineHeight: 1.3, marginBottom: 12 }}>
                  Lía Smith, naturalist guide &amp; longtime El Valle resident
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
              <p>The crater walls, the ridge trail, and the town below — in five frames.</p>
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

        {/* ===== STATEMENT ===== */}
        <section className="art-statement">
          <div className="container">
            <div className="art-statement-inner">
              <blockquote>
                The capital drives up on Sundays for the market, the mud baths, and
                the air. Then it drives back down — and the valley exhales.
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
              <span className="eyebrow">Around the valley</span>
              <h2>More of El Valle</h2>
            </div>
            <div className="home-bento-grid">
              <div className="bento-card b1">
                <div className="bento-img-top">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(16053611)}')` }}
                  />
                </div>
                <div className="bento-body">
                  <span className="b-tag">Outdoors</span>
                  <h3>Trails up the crater rim</h3>
                  <p>
                    La India Dormida is the headline hike, but the green walls all
                    around hide waterfalls and quieter paths too.
                  </p>
                </div>
              </div>

              <div className="bento-card b2">
                <span className="b-tag">From the valley</span>
                <blockquote>
                  People come up for the day and start asking what a little house
                  on the crater floor would cost. It&rsquo;s that kind of place.
                </blockquote>
                <cite>— Lía Smith · El Valle</cite>
              </div>

              <div className="bento-card b3">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(9566563)}')` }}
                />
                <div className="bento-overlay">
                  <span className="b-tag">Wildlife</span>
                  <h3>The golden frog</h3>
                </div>
              </div>

              <div className="bento-card b4">
                <span className="b-tag">Plan</span>
                <h3>Plan a day trip from Panama City.</h3>
                <span className="bento-arrow">Coming soon</span>
              </div>

              <div className="bento-card b5">
                <div className="bento-split-img">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(18343797)}')` }}
                  />
                </div>
                <div className="bento-split-body">
                  <span className="b-tag">Where to stay</span>
                  <h3>Cabins &amp; eco-lodges</h3>
                  <p>
                    Garden cabins on the crater floor and lodges up the rim trade
                    the city heat for cool, quiet nights.
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
