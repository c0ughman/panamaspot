import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { buildMetadata } from "@/lib/seo";
import { siteConfig } from "@/lib/site-config";
import { articleJsonLd, breadcrumbJsonLd, faqPageJsonLd, jsonLdScript } from "@/lib/jsonld";
import { ReadingProgress } from "@/components/reading-progress";
import { ArticleHero } from "@/components/article-hero";
import { ArticleToc } from "@/components/article-toc";
import { FaqItem } from "@/components/faq-item";

const SLUG = "sendero-los-quetzales";

const HERO_IMAGE =
  "https://images.pexels.com/photos/2380342/pexels-photo-2380342.jpeg?auto=compress&cs=tinysrgb&w=2000";

const ARTICLE = {
  slug: SLUG,
  title: "The Quetzal Trail at dawn — and the four hours that almost broke us.",
  description:
    "A complete trail report on Sendero Los Quetzales, Panama's most famous hike. River crossings, weather windows, transport logistics, and the precise moment we lost the path.",
  publishedAt: "2026-05-03",
  modifiedAt: "2026-05-03",
  author: "Mariela Ortiz-Saavedra",
} as const;

const TOC_ITEMS = [
  { id: "s1", n: "01", label: "Why this trail, why now" },
  { id: "s2", n: "02", label: "Getting to the trailhead" },
  { id: "s3", n: "03", label: "Direction: Cerro Punta or Boquete?" },
  { id: "s4", n: "04", label: "What to pack" },
  { id: "s5", n: "05", label: "The walk, kilometer by kilometer" },
  { id: "s6", n: "06", label: "Wildlife — and the quetzal question" },
  { id: "s7", n: "07", label: "Where to sleep, either end" },
  { id: "s8", n: "08", label: "FAQ" },
];

const FAQ_ITEMS = [
  {
    question: "Can I do the Quetzal Trail without a guide?",
    answer:
      "Yes — and most experienced hikers do. The trail is signposted in both Spanish and English, and the second river crossing has a cable. That said: if it's your first multi-hour hike in cloud forest, hire a guide for the first two kilometers (~$25) just to see how the trail markers work. After the saddle the path is obvious.",
  },
  {
    question: "Is the trail open in rainy season?",
    answer:
      "Officially yes, practically no. From mid-May to mid-November the second river crossing becomes unpredictable, and the upper trail fogs in by 8 a.m. We don't recommend it.",
  },
  {
    question: "How fit do I need to be?",
    answer:
      "If you can walk for six hours with a small pack and 1,420 m of net descent, you can walk this trail. The first 2.4 km is the only sustained climb — after that it's gradually downhill, with two short uphill sections.",
  },
  {
    question: "Is there cell service?",
    answer:
      "No. Download the offline map from the AllTrails app or the Maps.me Panama bundle before you start. There is sporadic Movistar signal in the first kilometer and at the very end near Bajo Mono — nothing in between.",
  },
  {
    question: "What's the permit and how do I get it?",
    answer:
      "$5 per person, paid in cash at the Las Nubes ranger station the morning of your hike. You don't need to reserve. The station opens at 5:30 a.m. in dry season.",
  },
  {
    question: "Can I hike with kids?",
    answer:
      "Yes, with caveats. Kids 10+ who are comfortable walking for six hours will be fine in dry season. Below that age, do the shorter Las Nubes loop instead — same forest, two hours, no river crossings.",
  },
] as const;

export function generateStaticParams() {
  return [{ slug: SLUG }];
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  if (slug !== SLUG) {
    return buildMetadata({
      title: "Article not found",
      description: "This guide could not be found.",
      path: `/articles/${slug}`,
      noindex: true,
    });
  }
  return buildMetadata({
    title: ARTICLE.title,
    description: ARTICLE.description,
    path: `/articles/${ARTICLE.slug}`,
    ogImage: HERO_IMAGE,
    type: "article",
    publishedTime: ARTICLE.publishedAt,
    modifiedTime: ARTICLE.modifiedAt,
    authors: [ARTICLE.author],
  });
}

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  if (slug !== SLUG) notFound();

  const path = `/articles/${ARTICLE.slug}`;

  const jsonLd = [
    breadcrumbJsonLd([
      { name: "Home", path: "/" },
      { name: "Sendero Los Quetzales", path },
    ]),
    articleJsonLd({
      headline: ARTICLE.title,
      description: ARTICLE.description,
      path,
      image: HERO_IMAGE,
      datePublished: ARTICLE.publishedAt,
      dateModified: ARTICLE.modifiedAt,
      authorName: ARTICLE.author,
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

      <ReadingProgress />

      {/* ===== HERO ===== */}
      <ArticleHero bgImage={HERO_IMAGE}>
        <div className="art-hero-pills">
          <span className="art-hero-tag">Eco-tourism</span>
          <span className="art-hero-tag">Field report</span>
          <span className="art-hero-tag">Trail guide</span>
          <span className="art-hero-tag">Updated · May 2026</span>
        </div>
      </ArticleHero>

      {/* ===== HEAD ===== */}
      <section className="art-head-section">
        <div className="container">
          <nav className="breadcrumb" aria-label="Breadcrumb">
            <Link href="/">Home</Link>
            <span className="sep">/</span>
            <span>Chiriquí</span>
            <span className="sep">/</span>
            <span>Hiking guides</span>
            <span className="sep">/</span>
            <span>Sendero Los Quetzales</span>
          </nav>

          <div className="art-head">
            <div>
              <h1 className="art-title">
                The Quetzal Trail at <em>dawn</em> — and the four hours that
                almost broke us.
              </h1>
              <p className="art-dek">
                A complete trail report on Sendero Los Quetzales, Panama&rsquo;s
                most photographed hike — including the river crossings the
                guidebooks forget and the precise moment we lost the path.
              </p>

              <div className="art-byline">
                <div className="byline-photo">M</div>
                <div className="byline-meta">
                  <div className="name">Mariela Ortiz-Saavedra</div>
                  <div className="role">
                    Field reporter · Chiriquí · 14 years on the ground
                  </div>
                </div>
                <div className="byline-stats">
                  <span>
                    <strong>14 min</strong> read
                  </span>
                  <span>
                    <time dateTime="2026-05-03">
                      <strong>May 03</strong> · 2026
                    </time>
                  </span>
                  <span>
                    <strong>Cerro Punta → Boquete</strong>
                  </span>
                </div>
              </div>
            </div>

            <aside className="fact-card">
              <h4>Trail at a glance</h4>
              <div className="fact-row">
                <span className="k">Distance</span>
                <span className="v">9.5 km</span>
              </div>
              <div className="fact-row">
                <span className="k">Elevation gain</span>
                <span className="v">+650 m</span>
              </div>
              <div className="fact-row">
                <span className="k">Elevation loss</span>
                <span className="v">−1,420 m</span>
              </div>
              <div className="fact-row">
                <span className="k">Time</span>
                <span className="v">5–7 hrs</span>
              </div>
              <div className="fact-row">
                <span className="k">High point</span>
                <span className="v">2,560 m</span>
              </div>
              <div className="fact-row">
                <span className="k">Best months</span>
                <span className="v">Jan–Apr</span>
              </div>
              <div className="fact-row">
                <span className="k">Permit</span>
                <span className="v">$5 · ANAM</span>
              </div>
              <div className="fact-rating">
                <span className="lbl">Difficulty</span>
                <Bar on={3} />
                <span className="lbl">Crowds</span>
                <Bar on={2} />
                <span className="lbl">Wildlife</span>
                <Bar on={5} />
                <span className="lbl">Solo-friendly</span>
                <Bar on={2} />
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
              At 5:42 a.m. the air at Las Nubes is the kind of cold that
              doesn&rsquo;t argue. The ranger hands us a map photocopied so
              many times the contour lines have become a suggestion. He asks if
              we have a whistle. We don&rsquo;t. He gives us one. &ldquo;Stay
              on the right at the second crossing,&rdquo; he says. &ldquo;The
              left one looks like the trail. It is not the trail.&rdquo;
            </p>

            <p>
              The Sendero Los Quetzales — the Quetzal Trail — is the hike
              everyone tells you about when you mention Panama. It runs 9.5
              kilometers across the saddle between the town of Cerro Punta and
              the town of Boquete, threading through a sliver of cloud forest
              inside Volcán Barú National Park. It is, on paper, a half-day
              walk. In practice, it is a full course in how cloud forests
              behave.
            </p>

            <p>
              This is the version of the guide we wish we&rsquo;d had on the
              way in. It assumes you have never set foot on the trail. It
              assumes you&rsquo;d like to leave it without phoning a relative.
            </p>

            <h2 id="s1">
              <span className="num">Section 01</span>Why this trail, why now
            </h2>

            <p>
              Panama&rsquo;s protected areas cover roughly 30% of the
              country&rsquo;s land, but most of it is functionally inaccessible
              of it is functionally inaccessible without a guide and a permit.
              The Quetzal Trail is the rare exception: a well-marked,
              day-walkable corridor through primary cloud forest, with two real
              towns at either end and public buses to both.
            </p>

            <p>
              It is also one of the few places on earth where a casual hiker can
              plausibly see a <strong>resplendent quetzal</strong> — the bird
              that gives the trail its name — without binoculars, without a
              guide, and without standing still for three hours. We saw one. We
              will get to that.
            </p>

            <div className="callout">
              <span className="label">Field note · Why May matters</span>
              Dry season in the Chiriquí highlands runs roughly mid-December to
              mid-May. After May 15, the trail is still open, but the second
              river crossing rises fast and the upper ridge fogs in by 9 a.m.
              If you are reading this in late April or early May, your window
              is closing.
            </div>

            <figure className="fig">
              <div className="imgph jungle">
                <div className="label">Sendero Los Quetzales · upper trail</div>
              </div>
              <figcaption>
                <span>
                  <strong>Cloud forest at the saddle.</strong> Conditions shift rapidly in the upper sections.
                </span>
              </figcaption>
            </figure>

            <h2 id="s2">
              <span className="num">Section 02</span>Getting to the trailhead
            </h2>

            <p>
              There is no direct flight to Cerro Punta. The nearest airport is
              David (DAV), one hour from Boquete and two hours from Cerro
              Punta. From Panama City, Air Panama and Copa run two daily
              flights for $89–$140 one-way; the bus from Albrook terminal is
              $19 and takes 7 hours overnight.
            </p>

            <p>
              Once in Chiriquí, your two trailheads are <strong>Las Nubes</strong>{" "}
              (Cerro Punta side, 2,200 m) and{" "}
              <strong>El Respingo / Bajo Mono</strong> (Boquete side, 1,800 m).
              Both are reachable by colectivo for $2–$5 from their respective
              town squares. We recommend a 4×4 only if you&rsquo;d like to
              drive yourself the final 4 km; the road is fine but loose.
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
                  <td>Air Panama PTY → DAV</td>
                  <td>Panama City</td>
                  <td>$89–$140</td>
                  <td>1 h flight + 2 h drive</td>
                  <td>
                    <span className="pill good">Good</span>
                  </td>
                </tr>
                <tr>
                  <td>Copa direct PTY → DAV</td>
                  <td>Panama City</td>
                  <td>$110–$165</td>
                  <td>1 h flight + 2 h drive</td>
                  <td>
                    <span className="pill good">Good</span>
                  </td>
                </tr>
                <tr>
                  <td>Overnight Padafront bus</td>
                  <td>Albrook</td>
                  <td>$19</td>
                  <td>7 hours</td>
                  <td>
                    <span className="pill mid">Cold AC</span>
                  </td>
                </tr>
                <tr>
                  <td>Self-drive from PTY</td>
                  <td>Panama City</td>
                  <td>$60–$90 fuel</td>
                  <td>6.5 hours</td>
                  <td>
                    <span className="pill mid">Long</span>
                  </td>
                </tr>
                <tr>
                  <td>Shuttle (private)</td>
                  <td>Boquete</td>
                  <td>$140 split 4-way</td>
                  <td>—</td>
                  <td>
                    <span className="pill good">Door-to-door</span>
                  </td>
                </tr>
              </tbody>
            </table>

            <h2 id="s3">
              <span className="num">Section 03</span>Direction matters more
              than you think
            </h2>

            <p>
              Walk it from <strong>Cerro Punta to Boquete</strong>. Every
              guidebook will tell you this and every guidebook is correct. You
              start 400 meters higher than you finish, which means you spend
              the day descending into warmer air. The other direction is a
              1,420 m climb that ends in fog.
            </p>

            <figure className="fig">
              <div className="imgph jungle">
                <div className="label">Elevation profile · west → east</div>
              </div>
              <figcaption>
                <span>
                  <strong>Elevation profile.</strong> Cerro Punta (2,200m) to Boquete (1,430m) — 9.5 km descent.
                </span>
              </figcaption>
            </figure>

            <p className="pullquote">
              The trail does not lose you on the climb. It loses you in the
              third hour, when you are 220 meters past the second river and
              your legs and your map have stopped agreeing on which way is
              east.
              <cite>— from the field notebook, day three</cite>
            </p>

            <h3>The two river crossings, explained</h3>

            <p>
              You will cross the Río Caldera twice, and they are not
              equivalent. The first crossing, around km 4.2, is a narrow
              channel with a fixed cable and a log bridge that has been there
              since 2019. It is fine in any weather you should be hiking in.
            </p>

            <p>
              The second crossing, at km 5.8, is the one. There is no bridge.
              In dry season it is calf-deep and twelve meters wide; after rain
              it can become impassable inside an hour.{" "}
              <strong>
                This is the crossing the ranger was warning us about.
              </strong>{" "}
              Take the right channel, not the left — the left looks like a
              continuation of the trail, but it dead-ends at a slide above a
              30-meter drop. Several rescues a year happen here.
            </p>

            <div className="callout warning">
              <span className="label">Hard rule · River II</span>
              If the second crossing is above your knees or moving fast enough
              that you cannot see your feet, turn around. The trail is not
              worth it. Cerro Punta is closer than Boquete from this point and
              the bus is still running.
            </div>

            <figure className="fig">
              <div className="imgph jungle">
                <div className="label">Río Caldera · second crossing</div>
              </div>
              <figcaption>
                <span>
                  <strong>Río Caldera, second crossing.</strong> Look for the
                  cable on the right bank.
                </span>
                <span>Km 5.8 · 2,180 m</span>
              </figcaption>
            </figure>

            <h2 id="s4">
              <span className="num">Section 04</span>What to pack — and what to
              leave
            </h2>

            <p>
              Cloud forest packing is its own specialty. You will be cold at
              the start, hot in the middle, wet by the end, and you cannot
              reliably layer in a downpour. Here is the kit we used:
            </p>

            <figure className="fig">
              <div className="imgph terra">
                <div className="label">Packing for cloud forest</div>
              </div>
              <figcaption>
                <span>
                  <strong>Trail day essentials.</strong> Lightweight layers and proper footwear are critical.
                </span>
              </figcaption>
            </figure>

            <ul>
              <li>
                <strong>Footwear:</strong> Trail runners with aggressive lugs
                over hiking boots. Boots take two days to dry; trail runners
                take four hours.
              </li>
              <li>
                <strong>Rain shell:</strong> Yes, even in dry season. The
                forest makes its own weather.
              </li>
              <li>
                <strong>Two liters of water:</strong> No reliable filter points
                after Las Nubes ranger station.
              </li>
              <li>
                <strong>Snacks:</strong> Two stops. We bought hojaldras at the
                Cerro Punta market — $1.50 a stack and they survive being
                squashed.
              </li>
              <li>
                <strong>Whistle:</strong> Free at the ranger station. Take one.
              </li>
              <li>
                <strong>Headlamp:</strong> If you are starting at first light,
                you are starting in the dark.
              </li>
              <li>
                <strong>Cash:</strong> $20 in small bills covers permit, snack
                stop, and the colectivo at the far end.
              </li>
            </ul>

            <h2 id="s5">
              <span className="num">Section 05</span>The walk, kilometer by
              kilometer
            </h2>

            <p>
              What follows is the trail as we walked it on April 18, 2026,
              leaving Las Nubes at 5:55 a.m. and reaching Bajo Mono at 12:43
              p.m. — a touch under seven hours, with two long stops.
            </p>

            <h3>Km 0–2.4 · Las Nubes to the saddle</h3>

            <p>
              The climb. 360 meters of elevation in 2.4 kilometers,
              switchbacking through the upper-elevation oak forest. You are
              still under canopy here but the trees are thin enough that the
              sky shows through. This is the coldest stretch of the day and
              where every quetzal sighting we have ever heard about happens.
            </p>

            <h3>Km 2.4–5.8 · The contouring middle</h3>

            <p>
              You are now on the eastern side of the saddle and dropping
              slowly through closed-canopy cloud forest. Bromeliads everywhere;
              the ground is wet even when it hasn&rsquo;t rained. The trail is
              mostly obvious but braids in three places — when in doubt, take
              the path with footprints, not the path with the most light.
            </p>

            <h3>Km 5.8–9.5 · The descent into Boquete</h3>

            <p>
              After the second river, the gradient steepens and the forest
              opens. You&rsquo;ll start to hear traffic from the Bajo Mono road
              by km 8. The last kilometer is on jeep track, which is a relief
              or an insult depending on your knees. Bajo Mono colectivos run
              every 20 minutes back to Boquete town for $2.
            </p>

            <figure className="fig">
              <div className="imgph sky">
                <div className="label">Trail map · Sendero Los Quetzales</div>
              </div>
              <figcaption>
                <span>
                  <strong>Route overview.</strong> Cerro Punta to Boquete with key points marked: saddle, river crossings, and waypoints.
                </span>
                <span>Approx · not for navigation</span>
              </figcaption>
            </figure>

            <h2 id="s6">
              <span className="num">Section 06</span>The wildlife — and the
              quetzal question
            </h2>

            <p>
              The trail is named for the resplendent quetzal (
              <em>Pharomachrus mocinno</em>), and you are most likely to see
              one between February and May, between 6 a.m. and 8 a.m., in the
              upper third of the trail. We saw a male at 7:18 a.m. on a small
              rise about 1.6 km in. He was sitting still on a low branch,
              eating a wild avocado. He stayed for forty seconds.
            </p>

            <figure className="fig">
              <div className="imgph jungle">
                <div className="label">Resplendent quetzal · endemic to cloud forest</div>
              </div>
              <figcaption>
                <span>
                  <strong>The resplendent quetzal.</strong> Early morning is prime viewing time in the upper forest.
                </span>
              </figcaption>
            </figure>

            <p>
              Other things you will probably see: black guans, Talamanca
              hummingbirds, agoutis, a great deal of mud. Other things you
              will probably not see but might: pumas (rare), Baird&rsquo;s
              tapirs (very rare), spectacled bears (vanishingly rare).
            </p>

            <h2 id="s7">
              <span className="num">Section 07</span>Where to sleep, either end
            </h2>

            <p>
              If you are walking west-to-east, sleep in{" "}
              <strong>Cerro Punta</strong> the night before and{" "}
              <strong>Boquete</strong> the night after. Two beds, one trail.
              Cerro Punta is small and quiet — Hostal Cielito Sur ($45) and
              Cabañas Los Quetzales ($120) are the two we&rsquo;d recommend.
              Boquete is larger and louder — a full Boquete sleeping guide is
              coming soon.
            </p>

            <figure className="fig">
              <div className="imgph sky">
                <div className="label">Boquete town · trail exit</div>
              </div>
              <figcaption>
                <span>
                  <strong>Boquete, Chiriquí.</strong> The perfect place to recover after the hike.
                </span>
              </figcaption>
            </figure>

            <h2 id="s8">
              <span className="num">Section 08</span>FAQ
            </h2>

            <div className="faq">
              <FaqItem
                defaultOpen
                q="Can I do the Quetzal Trail without a guide?"
                a={
                  <>
                    Yes — and most experienced hikers do. The trail is
                    signposted in both Spanish and English, and the second
                    river crossing has a cable. That said: if it&rsquo;s your
                    first multi-hour hike in cloud forest, hire a guide for the
                    first two kilometers (~$25) just to see how the trail
                    markers work. After the saddle the path is obvious.
                  </>
                }
              />
              <FaqItem
                q="Is the trail open in rainy season?"
                a="Officially yes, practically no. From mid-May to mid-November the second river crossing becomes unpredictable, and the upper trail fogs in by 8 a.m. We don't recommend it."
              />
              <FaqItem
                q="How fit do I need to be?"
                a="If you can walk for six hours with a small pack and 1,420 m of net descent, you can walk this trail. The first 2.4 km is the only sustained climb — after that it's gradually downhill, with two short uphill sections."
              />
              <FaqItem
                q="Is there cell service?"
                a="No. Download the offline map from the AllTrails app or the Maps.me Panama bundle before you start. There is sporadic Movistar signal in the first kilometer and at the very end near Bajo Mono — nothing in between."
              />
              <FaqItem
                q="What's the permit and how do I get it?"
                a="$5 per person, paid in cash at the Las Nubes ranger station the morning of your hike. You don't need to reserve. The station opens at 5:30 a.m. in dry season."
              />
              <FaqItem
                q="Can I hike with kids?"
                a="Yes, with caveats. Kids 10+ who are comfortable walking for six hours will be fine in dry season. Below that age, do the shorter Las Nubes loop instead — same forest, two hours, no river crossings."
              />
            </div>

          </article>

          <aside className="aside">
            <div className="aside-card">
              <h5>Best time · 12-month view</h5>
              {(
                [
                  ["Jan", "12°/22°", "go"],
                  ["Feb", "11°/23°", "go"],
                  ["Mar", "12°/24°", "go"],
                  ["Apr", "13°/24°", "go"],
                  ["May", "14°/23°", "maybe"],
                  ["Jun", "15°/22°", "skip"],
                  ["Jul", "15°/22°", "skip"],
                  ["Aug", "15°/22°", "skip"],
                  ["Sep", "14°/22°", "skip"],
                  ["Oct", "14°/22°", "skip"],
                  ["Nov", "13°/22°", "maybe"],
                  ["Dec", "12°/22°", "go"],
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
                  fontFamily: "var(--mono)",
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
              <h5>Total budget · solo, 1 day</h5>
              <div className="stat">$87</div>
              <p>
                Trail permit, transport from Boquete, two meals, one night each
                side. Excludes Panama City flight.
              </p>
            </div>

            <div
              className="aside-card"
              style={{
                background: "var(--ink)",
                color: "var(--bg)",
                borderColor: "var(--ink)",
              }}
            >
              <h5
                style={{
                  color: "oklch(70% 0.04 75)",
                  borderColor: "oklch(30% 0 0)",
                }}
              >
                Plan this trip
              </h5>
              <p
                style={{
                  color: "oklch(85% 0.03 75)",
                  marginBottom: 0,
                  fontFamily: "var(--mono)",
                  fontSize: 11,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                }}
              >
                7-day Chiriquí itineraries coming soon
              </p>
            </div>

            <div className="aside-card">
              <h5>Locally vetted by</h5>
              <p
                style={{
                  fontFamily: "var(--serif)",
                  fontSize: 18,
                  lineHeight: 1.3,
                  marginBottom: 12,
                }}
              >
                Carlos Mendoza, ANAM-certified guide &amp; 22-year Boquete
                resident
              </p>
              <p style={{ fontSize: 12 }}>Reviewed: April 28, 2026</p>
            </div>
          </aside>
        </div>
      </div>
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
