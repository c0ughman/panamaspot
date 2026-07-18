/* ============================================================================
   Panama City — destination guide (BLUE theme)
   Built from the blue "destination guide" template. Same layout and sections;
   different subject + photos. The green sibling (articles/bocas-del-toro)
   documents the shared section structure.
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

const SLUG = "panama-city";
const HERO_IMAGE = pexels(14840814, 2000);

const ARTICLE = {
  slug: SLUG,
  locale: "en" as "en" | "es",
  seoTitle: "Panama City Travel Guide: Casco Viejo, the Canal & What to Do",
  title: "Panama City — where a 16th-century old town keeps watch over a skyline of glass.",
  description:
    "A complete guide to Panama City: how to get there, when to go, where to stay, and what's worth your time — from the UNESCO old quarter to the canal that built it.",
  section: "Destinations",
  publishedAt: "2026-05-26",
  modifiedAt: "2026-05-26",
  breadcrumb: ["Panamá Province", "Capital", "Panama City"],
  heroTags: ["Capital", "City guide", "Updated · May 2026"],
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
  { src: pexels(2666249), caption: "The Pacific skyline from the bay", feature: true },
  { src: pexels(18118099), caption: "Avenida Balboa lit up after dark" },
  { src: pexels(5864401), caption: "Palms and high-rises, side by side" },
  { src: pexels(2146686), caption: "Twilight over the financial district" },
  { src: pexels(13110362), caption: "The city from the air" },
] as const;

const HIGHLIGHTS = [
  { stat: "1519", title: "Oldest on the Pacific", body: "Panamá Viejo was the first European city on the Pacific coast of the Americas — its ruins still stand on the city's eastern edge." },
  { stat: "80 km", title: "Built by the canal", body: "The Panama Canal runs from the city to the Caribbean; the Miraflores Locks are a short trip from downtown." },
  { stat: "1st", title: "Central America's metro", body: "The region's first metro system, plus cheap ride-share, makes a sprawling city surprisingly easy to cross." },
] as const;

const FAQ_ITEMS = [
  {
    question: "Is Panama City safe for visitors?",
    answer:
      "The main tourist areas — Casco Viejo, the banking district, Cinta Costera and Amador — are well patrolled and fine to walk by day and evening. Use normal big-city sense at night, keep valuables low-key, and skip neighborhoods like El Chorrillo and Curundú unless you have a local reason to be there.",
  },
  {
    question: "How many days do I need?",
    answer:
      "Three to four. Give a full day to Casco Viejo on foot, half a day to the Panama Canal and the waterfront, and the rest to Panamá Viejo, the Biomuseo, or a day trip to the rainforest or the Pacific beaches.",
  },
  {
    question: "How do I get around?",
    answer:
      "The Metro and ride-share apps are cheap and reliable; the old town is walkable end to end. Traffic is heavy at rush hour, so plan canal and airport runs around it.",
  },
  {
    question: "Can I visit the Panama Canal?",
    answer:
      "Yes. The Miraflores Locks visitor center is about 20 minutes from Casco Viejo and has viewing decks and a museum. Go mid-morning or late afternoon to catch ships actually transiting the locks.",
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

      <main className="article-page">
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
                  Panama City — where a 16th-century old town keeps watch over a{" "}
                  <em>skyline of glass.</em>
                </h1>
                <p className="art-dek">
                  Latin America&rsquo;s most vertical capital wears its history on
                  its sleeve: a UNESCO old quarter, the canal that built it, and a
                  Pacific skyline that never quite stops growing.
                </p>

                <div className="art-byline">
                  <div className="byline-photo">P</div>
                  <div className="byline-meta">
                    <div className="name">{siteConfig.name}</div>
                    <div className="role">
                      Editorial · Panama City
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
                  <span className="v">Panamá Province</span>
                </div>
                <div className="fact-row">
                  <span className="k">Founded</span>
                  <span className="v">1519</span>
                </div>
                <div className="fact-row">
                  <span className="k">Getting there</span>
                  <span className="v">PTY · Tocumen</span>
                </div>
                <div className="fact-row">
                  <span className="k">Best months</span>
                  <span className="v">Dec–Apr</span>
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
                  <Bar on={3} />
                  <span className="lbl">Crowds</span>
                  <Bar on={4} />
                  <span className="lbl">Nightlife</span>
                  <Bar on={5} />
                  <span className="lbl">Culture</span>
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
                You land, and the city hits you in two registers at once: a wall
                of glass towers along the bay, and somewhere behind them, a low
                cluster of tile roofs that has been there for 350 years. Panama
                City is a capital that never picked a single century to live in.
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
                It&rsquo;s the most cosmopolitan capital in Central America, and
                the only one with a UNESCO-listed old town, a world-changing canal,
                and a skyline to rival Miami — all within a few kilometres of each
                other. Add a serious food-and-rooftop scene and rainforest you can
                reach before lunch, and a few days fill themselves.
              </p>

              <div className="callout">
                <span className="label">Field note · Base in the old town</span>
                Sleep in Casco Viejo if you can. It&rsquo;s walkable, safe, and
                puts the prettiest part of the city outside your door at night —
                when the day-trippers have gone and the rooftops open up.
              </div>

              <figure className="fig">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(19620790)}')` }}
                />
                <figcaption>
                  <span>
                    <strong>Casco Viejo.</strong> The restored colonial quarter is
                    the city&rsquo;s historic heart — and its most walkable corner.
                  </span>
                </figcaption>
              </figure>

              <h2 id="s2">
                <span className="num">Section 02</span>Getting there
              </h2>

              <p>
                Tocumen International (PTY) is the biggest hub in the region, so
                getting here is the easy part. From the airport it&rsquo;s about
                30–45 minutes into town by taxi or ride-share, or a longer but
                cheap ride on the Metro and a connecting bus.
              </p>

              <table className="compare">
                <thead>
                  <tr>
                    <th>From the airport</th>
                    <th>Mode</th>
                    <th>Cost</th>
                    <th>Time</th>
                    <th>Comfort</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Ride-share</td>
                    <td>Uber / app</td>
                    <td>$18–$30</td>
                    <td>30–45 min</td>
                    <td>
                      <span className="pill good">Easiest</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Airport taxi</td>
                    <td>Official desk</td>
                    <td>$30–$40</td>
                    <td>30–45 min</td>
                    <td>
                      <span className="pill good">Simple</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Metro + bus</td>
                    <td>Line 2 + transfer</td>
                    <td>$1.25</td>
                    <td>60–80 min</td>
                    <td>
                      <span className="pill mid">Cheapest</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Hotel shuttle</td>
                    <td>Pre-booked</td>
                    <td>$25–$45</td>
                    <td>30–45 min</td>
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
                The dry season — roughly mid-December to April — brings the
                clearest, least humid days, and that&rsquo;s when the city feels
                its best for walking Casco Viejo and the waterfront. January and
                February are especially pleasant. The green season is hotter and
                wetter but quieter and cheaper.
              </p>

              <h2 id="s4">
                <span className="num">Section 04</span>Where to stay
              </h2>

              <p>
                Pick your base by mood. The old town trades convenience for
                atmosphere; the modern districts trade charm for skyline views and
                easy business logistics.
              </p>

              <ul>
                <li>
                  <strong>Casco Viejo:</strong> boutique hotels in restored
                  mansions, walkable, best for atmosphere and nightlife.
                </li>
                <li>
                  <strong>Marbella &amp; Obarrio:</strong> modern, central, close
                  to dining and the banking district.
                </li>
                <li>
                  <strong>Punta Pacífica &amp; Avenida Balboa:</strong> high-rise
                  hotels with ocean views and waterfront walks.
                </li>
              </ul>

              <h2 id="s5">
                <span className="num">Section 05</span>What to do
              </h2>

              <p>
                Walk the four plazas of{" "}
                <Link href="/articles/casco-viejo-panama-walking-guide">
                  Casco Viejo
                </Link>{" "}
                and duck into Iglesia de San José to see its golden altar;
                watch a ship rise through the{" "}
                <Link href="/articles/panama-canal-tour-miraflores-locks-visitor-guide">
                  Miraflores Locks
                </Link>
                ; stroll or cycle the Cinta Costera at sunset; and end the
                night on a rooftop bar above the old town.
              </p>

              {/* IN-COLUMN BENTO */}
              <div className="prose-bento">
                <div className="pb-tile pb-img pb-tall">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(18118137)}')` }}
                  />
                  <span className="pb-cap">The bay and causeway after dark</span>
                </div>
                <div className="pb-tile pb-accent">
                  <span className="pb-stat">4</span>
                  <span className="pb-label">historic plazas to walk</span>
                </div>
                <div className="pb-tile pb-outline">
                  <h4>Rooftop bars</h4>
                  <p>Hidden atop old-town mansions, with skyline views.</p>
                </div>
              </div>

              <h2 id="s6">
                <span className="num">Section 06</span>Know before you go
              </h2>

              <p>
                The basics that save a trip: the city runs on US dollars, ride-share
                is everywhere, and the heat is real — pace your walking and carry
                water. Tap water is safe to drink. Tipping around 10% is standard
                in restaurants.
              </p>

              {/* IN-COLUMN PANEL */}
              <div className="prose-panel">
                <h4>City essentials</h4>
                <ul>
                  <li>US dollars are the currency — small bills help with taxis.</li>
                  <li>Use the Metro and ride-share apps to beat the traffic.</li>
                  <li>Keep valuables low-key and stick to the patrolled areas at night.</li>
                  <li>Pack light layers — it&rsquo;s hot and humid year-round.</li>
                </ul>
              </div>
            </article>

            {/* ===== INFO-CARD RAIL ===== */}
            <aside className="aside">
              <div className="aside-card">
                <h5>Best time · 12-month view</h5>
                {(
                  [
                    ["Jan", "24°/31°", "go"],
                    ["Feb", "24°/32°", "go"],
                    ["Mar", "25°/32°", "go"],
                    ["Apr", "25°/32°", "go"],
                    ["May", "24°/31°", "maybe"],
                    ["Jun", "24°/31°", "maybe"],
                    ["Jul", "24°/31°", "maybe"],
                    ["Aug", "24°/31°", "maybe"],
                    ["Sep", "24°/31°", "skip"],
                    ["Oct", "23°/30°", "skip"],
                    ["Nov", "23°/30°", "skip"],
                    ["Dec", "24°/31°", "go"],
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
                <div className="stat">$110</div>
                <p>
                  Mid-range room, meals out, ride-share and a paid attraction.
                  Excludes the flight into Tocumen.
                </p>
              </div>

              <div className="aside-card">
                <h5>Reviewed on the ground</h5>
                <p style={{ fontSize: 18, lineHeight: 1.3, marginBottom: 12 }}>
                  Licensed city guides and longtime residents in the capital
                </p>
                <p style={{ fontSize: 12 }}>Reviewed: May 18, 2026</p>
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
              <p>Old town, new town, and the bay between them — in five frames.</p>
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
                Panama City is two cities pretending to be one — the old one that
                still remembers the pirates, and the glass one that forgot them on
                purpose.
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
              <span className="eyebrow">Around the capital</span>
              <h2>More of Panama City</h2>
            </div>
            <div className="home-bento-grid">
              <div className="bento-card b1">
                <div className="bento-img-top">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(14465475)}')` }}
                  />
                </div>
                <div className="bento-body">
                  <span className="b-tag">After dark</span>
                  <h3>A skyline that works late</h3>
                  <p>
                    The banking district, the rooftops above Casco Viejo, and a
                    waterfront that lights up along Avenida Balboa.
                  </p>
                </div>
              </div>

              <div className="bento-card b2">
                <span className="b-tag">From the capital</span>
                <blockquote>
                  Everyone says they&rsquo;re here for the canal. They stay for the
                  old town, the ceviche, and the rooftops.
                </blockquote>
                <cite>— Casco Viejo</cite>
              </div>

              <div className="bento-card b3">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(33803478)}')` }}
                />
                <div className="bento-overlay">
                  <span className="b-tag">Nightlife</span>
                  <h3>Rooftops &amp; bars</h3>
                </div>
              </div>

              <Link href="/articles/panama-city-itinerary-3-days" className="bento-card b4">
                <span className="b-tag">Plan</span>
                <h3>Build a 3-day Panama City itinerary.</h3>
                <span className="bento-arrow">Read the itinerary →</span>
              </Link>

              <Link href="/articles/panama-canal-tour-miraflores-locks-visitor-guide" className="bento-card b5">
                <div className="bento-split-img">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(20323097)}')` }}
                  />
                </div>
                <div className="bento-split-body">
                  <span className="b-tag">The Canal</span>
                  <h3>Miraflores Locks</h3>
                  <p>
                    Watch container ships rise and fall through the locks from the
                    visitor decks, a short trip from downtown.
                  </p>
                </div>
              </Link>
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
