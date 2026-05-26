import type { Metadata } from "next";
import Link from "next/link";
import { buildMetadata } from "@/lib/seo";
import { webPageJsonLd, jsonLdScript } from "@/lib/jsonld";
import { HeroParallax } from "@/components/hero-parallax";
import { SiteFooter } from "@/components/site-footer";
import { CategorySection, pexels, type Card } from "@/components/home-sections";

const HERO_BG = pexels(2474690, 2400);

export const metadata: Metadata = buildMetadata({
  title: "Panama Travel Guide: Destinations, Things to Do & Local Tips",
  description:
    "Plan your trip to Panama with in-depth guides to its beaches, cloud forests, islands and cities — where to go, when to visit, and what to do, from people who live here.",
  path: "/",
  absoluteTitle: true,
  ogImage: HERO_BG,
  languages: { en: "/", es: "/es", "x-default": "/" },
});
const BOCAS_PHOTO = pexels(2038744);
const GUNA_PHOTO = pexels(31416948);
const QUETZAL_TRAIL = "/articles/sendero-los-quetzales";

// ── Data ─────────────────────────────────────────────────────────────────────

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
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={jsonLdScript(
          webPageJsonLd({
            path: "/",
            name: "Panama Travel Guide",
            description:
              "In-depth guides, itineraries and local insight for travel across Panama — beaches, cloud forests, islands and cities.",
            locale: "en",
            primaryImage: HERO_BG,
          }),
        )}
      />

      <HeroParallax bgImage={HERO_BG} locale="en" />

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

      <SiteFooter locale="en" />
    </>
  );
}
