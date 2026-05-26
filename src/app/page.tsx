import type { Metadata } from "next";
import Link from "next/link";
import { buildMetadata } from "@/lib/seo";
import { siteConfig } from "@/lib/site-config";
import { HeroParallax } from "@/components/hero-parallax";

export const metadata: Metadata = buildMetadata({
  title: `${siteConfig.name} — The complete guide to traveling in Panama`,
  description:
    "In-depth guides, itineraries, and local insight for tourism, eco-tourism, and internal travel across Panama. Cloud forests, Caribbean islands, colonial cities and beyond.",
  path: "/",
  absoluteTitle: true,
});

// ── Pexels photo helpers ─────────────────────────────────────────────────────
const pexels = (id: number, w = 1200) =>
  `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${w}`;

const HERO_BG = pexels(2474690, 2400);
const BOCAS_PHOTO = pexels(2038744);
const GUNA_PHOTO = pexels(31416948);
const QUETZAL_TRAIL = "/articles/sendero-los-quetzales";

// ── Data ─────────────────────────────────────────────────────────────────────

type Tint = "jungle" | "terra" | "sky" | "sand" | "ink";
type CardImg = { kind: "photo"; src: string } | { kind: "tint"; cls: Tint };
type IconKey = "region" | "activity" | "destination";

type Card = {
  title: string;
  tag: string;
  img: CardImg;
  href?: string;
};

const REGIONS: Card[] = [
  { title: "Caribbean Coast", tag: "Coming soon", img: { kind: "photo", src: pexels(14185535) } },
  { title: "Pacific Side", tag: "Coming soon", img: { kind: "photo", src: pexels(34205250) } },
  { title: "Chiriquí Highlands", tag: "Coming soon", img: { kind: "photo", src: pexels(2918139) } },
  { title: "Panama City", tag: "Coming soon", img: { kind: "photo", src: pexels(2666249) } },
  { title: "Azuero Peninsula", tag: "Coming soon", img: { kind: "photo", src: pexels(36601635) } },
  { title: "Pacific Islands", tag: "Coming soon", img: { kind: "photo", src: pexels(4766708) } },
  { title: "Comarca Territories", tag: "Coming soon", img: { kind: "photo", src: pexels(9122911) } },
];

const ACTIVITIES: Card[] = [
  { title: "Hiking & Trails", tag: "1 guide", img: { kind: "photo", src: pexels(10343761) }, href: QUETZAL_TRAIL },
  { title: "Wildlife & Birding", tag: "Coming soon", img: { kind: "photo", src: pexels(9566563) } },
  { title: "Surf & Dive", tag: "Coming soon", img: { kind: "photo", src: pexels(33757647) } },
  { title: "Food & Coffee", tag: "Coming soon", img: { kind: "photo", src: pexels(30658818) } },
  { title: "Eco-tourism", tag: "1 guide", img: { kind: "photo", src: pexels(3603874) }, href: QUETZAL_TRAIL },
  { title: "Cities & Culture", tag: "Coming soon", img: { kind: "photo", src: pexels(23910182) } },
  { title: "Islands & Beaches", tag: "Coming soon", img: { kind: "photo", src: pexels(8951333) } },
];

const DESTINATIONS: Card[] = [
  { title: "Bocas del Toro", tag: "Coming soon", img: { kind: "photo", src: BOCAS_PHOTO } },
  { title: "Guna Yala", tag: "Coming soon", img: { kind: "photo", src: GUNA_PHOTO } },
  { title: "Boquete", tag: "Featured guide", img: { kind: "photo", src: pexels(2380342) }, href: QUETZAL_TRAIL },
  { title: "Casco Viejo", tag: "Coming soon", img: { kind: "photo", src: pexels(19620790) } },
  { title: "Pedasí", tag: "Coming soon", img: { kind: "photo", src: pexels(18976053) } },
  { title: "Coiba", tag: "Coming soon", img: { kind: "photo", src: pexels(4171716) } },
  { title: "The Darién", tag: "Coming soon", img: { kind: "photo", src: pexels(36105293) } },
];

export default function Home() {
  return (
    <>
      <HeroParallax bgImage={HERO_BG} />

      <CategorySection
        id="cat-regions"
        title="Where in Panama?"
        link="Browse by region"
        icon="region"
        cards={REGIONS}
      />
      <CategorySection
        id="cat-activities"
        title="What will you do?"
        link="Browse by activity"
        icon="activity"
        cards={ACTIVITIES}
      />
      <CategorySection
        id="cat-destinations"
        title="Where to go first?"
        link="Browse destinations"
        icon="destination"
        cards={DESTINATIONS}
      />

      <section className="home-bento">
        <div className="container">
          <div className="home-bento-head">
            <h2>
              Seven Panamas,
              <br />
              one isthmus.
            </h2>
            <span className="cat-section-link cat-section-link--muted">
              More guides coming soon
            </span>
          </div>

          <div className="home-bento-grid">
            <div className="bento-card b1">
              <div className="bento-img-top">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${BOCAS_PHOTO}')` }}
                />
              </div>
              <div className="bento-body">
                <span className="b-tag">Caribbean · Coming soon</span>
                <h3>Bocas del Toro — nine islands, slow boats, sloths</h3>
                <p>
                  Surfers&rsquo; capital of the Caribbean coast, Afro-Antillean kitchens,
                  and the country&rsquo;s easiest place to wake up on the water.
                </p>
              </div>
            </div>

            <div className="bento-card b2">
              <span className="b-tag">From the country</span>
              <blockquote>
                We don&rsquo;t have one country here. We have a coast that faces
                Cuba, a coast that faces Ecuador, and a mountain range between
                them that hides whatever it wants to hide.
              </blockquote>
              <cite>— Iván Bethancourt · Almirante</cite>
            </div>

            <div className="bento-card b3">
              <div
                className="imgph photo"
                style={{ backgroundImage: `url('${pexels(5374189)}')` }}
              />
              <div className="bento-overlay">
                <span className="b-tag">Indigenous · Coming soon</span>
                <h3>Guna Yala</h3>
              </div>
            </div>

            <div className="bento-card b4">
              <span className="b-tag">Itineraries · Coming soon</span>
              <h3>Build a custom Panama itinerary in 10 minutes.</h3>
              <span className="bento-arrow">Coming soon</span>
            </div>

            <Link href={QUETZAL_TRAIL} className="bento-card b5">
              <div className="bento-split-img">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(9246451)}')` }}
                />
              </div>
              <div className="bento-split-body">
                <span className="b-tag">Highlands · Featured guide</span>
                <h3>Chiriquí — cloud forest, coffee, Volcán Barú</h3>
                <p>
                  Start with our field report on Sendero Los Quetzales — the
                  country&rsquo;s most famous day hike.
                </p>
              </div>
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}

function CategorySection({
  id,
  title,
  link,
  icon,
  cards,
}: {
  id: string;
  title: string;
  link: string;
  icon: IconKey;
  cards: Card[];
}) {
  return (
    <section className="cat-section" id={id}>
      <div className="container">
        <div className="cat-section-head">
          <h2>{title}</h2>
          <span className="cat-section-link cat-section-link--muted">{link}</span>
        </div>

        <div className="cat-row-wrap">
          <button type="button" className="cat-arrow prev" aria-label="Previous">
            ‹
          </button>
          <div className="cat-row">
            {cards.map((card) => (
              <CategoryCard key={card.title} icon={icon} {...card} />
            ))}
          </div>
          <button type="button" className="cat-arrow next" aria-label="Next">
            ›
          </button>
        </div>
      </div>
    </section>
  );
}

function CategoryCard({
  title,
  tag,
  img,
  href,
  icon,
}: Card & { icon: IconKey }) {
  const content = (
    <>
      {img.kind === "photo" ? (
        <div
          className="imgph photo"
          style={{ backgroundImage: `url('${img.src}')` }}
        />
      ) : (
        <div className={`imgph ${img.cls}`} />
      )}
      <div className="cat-card-body">
        <span className="cat-card-title">{title}</span>
        <span className="cat-card-tag">
          <CardIcon kind={icon} />
          {tag}
        </span>
      </div>
    </>
  );

  if (href) {
    return (
      <Link href={href} className="cat-card">
        {content}
      </Link>
    );
  }

  return (
    <div className="cat-card cat-card--static" aria-label={`${title} — coming soon`}>
      {content}
    </div>
  );
}

function CardIcon({ kind }: { kind: IconKey }) {
  switch (kind) {
    case "region":
      return (
        <svg
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.2"
          strokeLinejoin="round"
          aria-hidden="true"
          width="11"
          height="11"
        >
          <path d="M6 1.4 C 3.6 1.4, 2.2 3.2, 2.2 5 C 2.2 7.4, 6 10.6, 6 10.6 C 6 10.6, 9.8 7.4, 9.8 5 C 9.8 3.2, 8.4 1.4, 6 1.4 Z" />
          <circle cx="6" cy="5" r="1.4" />
        </svg>
      );
    case "activity":
      return (
        <svg
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.2"
          strokeLinejoin="round"
          aria-hidden="true"
          width="11"
          height="11"
        >
          <path d="M1.5 9.6 L4.2 4.4 L6.4 6.8 L9 3 L10.5 9.6 Z" />
        </svg>
      );
    case "destination":
      return (
        <svg
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.2"
          aria-hidden="true"
          width="11"
          height="11"
        >
          <circle cx="6" cy="6" r="3.6" />
          <circle cx="6" cy="6" r="1" fill="currentColor" stroke="none" />
        </svg>
      );
  }
}
