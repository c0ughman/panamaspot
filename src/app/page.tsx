import type { Metadata } from "next";
import Link from "next/link";
import { buildMetadata } from "@/lib/seo";
import { siteConfig } from "@/lib/site-config";
import { HomeHeader } from "@/components/home-header";
import { HeroParallax } from "@/components/hero-parallax";

export const metadata: Metadata = buildMetadata({
  title: `${siteConfig.name} — The complete guide to traveling in Panama`,
  description:
    "In-depth guides, itineraries, and local insight for tourism, eco-tourism, and internal travel across Panama. Cloud forests, Caribbean islands, colonial cities and beyond.",
  path: "/",
});

// ── Pexels photo helpers ─────────────────────────────────────────────────────
// All photos sourced from Pexels and selected to be Panama-specific where
// possible (or close-match tropical/jungle imagery where no exact Panama photo
// was available).
const pexels = (id: number, w = 1200) =>
  `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${w}`;

// Placeholder — replace with video later
const HERO_BG = pexels(2474690, 2400); // Coastline

// Reused across bento + various cards
const BOCAS_PHOTO = pexels(2038744); // Bocas — beach house on stilts at sunset
const GUNA_PHOTO = pexels(31416948); // Guna Yala — secluded island in clear Caribbean

// ── Data ─────────────────────────────────────────────────────────────────────

type Tint = "jungle" | "terra" | "sky" | "sand" | "ink";
type CardImg = { kind: "photo"; src: string } | { kind: "tint"; cls: Tint };
type IconKey = "region" | "activity" | "destination";

type Card = {
  title: string;
  tag: string;
  img: CardImg;
  href: string;
};

const REGIONS: Card[] = [
  { title: "Caribbean Coast", tag: "28 guides", img: { kind: "photo", src: pexels(14185535) }, href: "#" }, // Bocas wooden houses
  { title: "Pacific Side", tag: "22 guides", img: { kind: "photo", src: pexels(34205250) }, href: "#" }, // Panama Bay aerial
  { title: "Chiriquí Highlands", tag: "31 guides", img: { kind: "photo", src: pexels(2918139) }, href: "#" }, // mountain valley with river
  { title: "Panama City", tag: "19 guides", img: { kind: "photo", src: pexels(2666249) }, href: "#" }, // Panama City skyline + waterfront
  { title: "Azuero Peninsula", tag: "14 guides", img: { kind: "photo", src: pexels(36601635) }, href: "#" }, // beach with palms + sailboats
  { title: "Pacific Islands", tag: "11 guides", img: { kind: "photo", src: pexels(4766708) }, href: "#" }, // Contadora Island Panama
  { title: "Comarca Territories", tag: "9 guides", img: { kind: "photo", src: pexels(9122911) }, href: "#" }, // Guna Yala palms
];

const ACTIVITIES: Card[] = [
  { title: "Hiking & Trails", tag: "31 guides", img: { kind: "photo", src: pexels(10343761) }, href: "#" }, // jungle path Panama rainforest
  { title: "Wildlife & Birding", tag: "28 guides", img: { kind: "photo", src: pexels(9566563) }, href: "#" }, // sloth in green leaves
  { title: "Surf & Dive", tag: "19 guides", img: { kind: "photo", src: pexels(33757647) }, href: "#" }, // surfers with forest backdrop
  { title: "Food & Coffee", tag: "22 guides", img: { kind: "photo", src: pexels(30658818) }, href: "#" }, // ripe red coffee cherries on Arabica plant
  { title: "Eco-tourism", tag: "34 guides", img: { kind: "photo", src: pexels(3603874) }, href: "#" }, // vibrant tropical rainforest vegetation
  { title: "Cities & Culture", tag: "18 guides", img: { kind: "photo", src: pexels(23910182) }, href: "#" }, // colorful hats Casco Viejo street
  { title: "Islands & Beaches", tag: "26 guides", img: { kind: "photo", src: pexels(8951333) }, href: "#" }, // palm trees on shore with clear waters
];

const DESTINATIONS: Card[] = [
  { title: "Bocas del Toro", tag: "Caribbean · 14 guides", img: { kind: "photo", src: BOCAS_PHOTO }, href: "/articles/sendero-los-quetzales" },
  { title: "Guna Yala", tag: "Comarca · 11 guides", img: { kind: "photo", src: GUNA_PHOTO }, href: "/articles/sendero-los-quetzales" },
  { title: "Boquete", tag: "Highlands · 18 guides", img: { kind: "photo", src: pexels(2380342) }, href: "/articles/sendero-los-quetzales" }, // rainforest stream Panama
  { title: "Casco Viejo", tag: "UNESCO · 22 guides", img: { kind: "photo", src: pexels(19620790) }, href: "#" }, // colonial street with cars
  { title: "Pedasí", tag: "Azuero · 9 guides", img: { kind: "photo", src: pexels(18976053) }, href: "#" }, // aerial island town in sea
  { title: "Coiba", tag: "Marine · 8 guides", img: { kind: "photo", src: pexels(4171716) }, href: "#" }, // small house with palms turquoise island
  { title: "The Darién", tag: "Wild · 7 guides", img: { kind: "photo", src: pexels(36105293) }, href: "#" }, // dense jungle with sunlit foliage
];

// ── Component ────────────────────────────────────────────────────────────────

export default function Home() {
  return (
    <>
      {/* ===== HERO ===== */}
      <HeroParallax bgImage={HERO_BG} />


      {/* ===== CATEGORIES ===== */}
      <CategorySection
        id="cat-regions"
        title="Where in Panama?"
        link="All 9 provinces →"
        icon="region"
        cards={REGIONS}
      />
      <CategorySection
        id="cat-activities"
        title="What will you do?"
        link="All 14 activities →"
        icon="activity"
        cards={ACTIVITIES}
      />
      <CategorySection
        id="cat-destinations"
        title="Where to go first?"
        link="All 47 spots →"
        icon="destination"
        cards={DESTINATIONS}
      />

      {/* ===== BENTO ===== */}
      <section className="home-bento">
        <div className="container">
          <div className="home-bento-head">
            <h2>Seven Panamas,<br />one isthmus.</h2>
            <Link href="#" className="cat-section-link">Explore all →</Link>
          </div>

          <div className="home-bento-grid">
            {/* B1 — image hero with text BELOW */}
            <Link href="/articles/sendero-los-quetzales" className="bento-card b1">
              <div className="bento-img-top">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${BOCAS_PHOTO}')` }}
                />
              </div>
              <div className="bento-body">
                <span className="b-tag">Caribbean · 14 guides</span>
                <h3>Bocas del Toro — nine islands, slow boats, sloths</h3>
                <p>
                  Surfers&rsquo; capital of the Caribbean coast, Afro-Antillean kitchens,
                  and the country&rsquo;s easiest place to wake up on the water. Where
                  to stay, which islands to skip, and how to read the weather.
                </p>
              </div>
            </Link>

            {/* B2 — text-only quote */}
            <div className="bento-card b2">
              <span className="b-tag">From the country</span>
              <blockquote>
                We don&rsquo;t have one country here. We have a coast that faces
                Cuba, a coast that faces Ecuador, and a mountain range between
                them that hides whatever it wants to hide.
              </blockquote>
              <cite>— Iván Bethancourt · Almirante</cite>
            </div>

            {/* B3 — pure image with overlay */}
            <Link href="/articles/sendero-los-quetzales" className="bento-card b3">
              <div
                className="imgph photo"
                style={{ backgroundImage: `url('${pexels(5374189)}')` }}
              />
              <div className="bento-overlay">
                <span className="b-tag">Indigenous · Sea</span>
                <h3>Guna Yala</h3>
              </div>
            </Link>

            {/* B4 — text-only dark CTA */}
            <Link href="#cta" className="bento-card b4">
              <span className="b-tag">→ Plan a trip</span>
              <h3>Build a custom Panama itinerary in 10 minutes.</h3>
              <span className="bento-arrow">Get started</span>
            </Link>

            {/* B5 — split: image left, text right */}
            <Link href="/articles/sendero-los-quetzales" className="bento-card b5">
              <div className="bento-split-img">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(9246451)}')` }}
                />
              </div>
              <div className="bento-split-body">
                <span className="b-tag">Highlands · 31 guides</span>
                <h3>Chiriquí — cloud forest, coffee, Volcán Barú</h3>
                <p>
                  The country&rsquo;s only summit you can climb in a day, plus the
                  Geisha farms that change how you taste coffee.
                </p>
              </div>
            </Link>
          </div>
        </div>
      </section>

    </>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

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
          <Link href="#" className="cat-section-link">{link}</Link>
        </div>

        <div className="cat-row-wrap">
          <button type="button" className="cat-arrow prev" aria-label="Previous">‹</button>
          <div className="cat-row">
            {cards.map((card) => (
              <CategoryCard key={card.title} icon={icon} {...card} />
            ))}
          </div>
          <button type="button" className="cat-arrow next" aria-label="Next">›</button>
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
  return (
    <Link href={href} className="cat-card">
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
    </Link>
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
