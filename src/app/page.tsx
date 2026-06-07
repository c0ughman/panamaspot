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

const BOCAS = "/articles/bocas-del-toro";
const BOQUETE = "/articles/sendero-los-quetzales";
const PANAMA_CITY = "/articles/panama-city";
const EL_VALLE = "/articles/el-valle-de-anton";

const BOQUETE_HIKES = "/articles/hikes-in-boquete";
const BOQUETE_TODO = "/articles/things-to-do-in-boquete-panama";
const BOQUETE_TOURS = "/articles/tours-in-boquete-panama";
const EV_HIKES = "/articles/hikes-el-valle-de-anton";
const EV_TODO = "/articles/things-to-do-el-valle-de-anton";
const EV_TOURS = "/articles/tours-en-el-valle-de-anton";

const BOCAS_PHOTO = pexels(2038744);
const BOQUETE_PHOTO = pexels(2380342);
const PANAMA_CITY_PHOTO = pexels(14840814);
const EL_VALLE_PHOTO = pexels(30774416);
const GUNA_PHOTO = pexels(31416948);

// ── Data ─────────────────────────────────────────────────────────────────────

const REGIONS: Card[] = [
  { title: "Bocas del Toro", tag: "Guide", img: { kind: "photo", src: BOCAS_PHOTO }, href: BOCAS },
  { title: "Boquete", tag: "Guide", img: { kind: "photo", src: BOQUETE_PHOTO }, href: BOQUETE },
  { title: "Panama City", tag: "Guide", img: { kind: "photo", src: PANAMA_CITY_PHOTO }, href: PANAMA_CITY },
  { title: "El Valle de Antón", tag: "Guide", img: { kind: "photo", src: EL_VALLE_PHOTO }, href: EL_VALLE },
  { title: "Guna Yala", tag: "Coming soon", img: { kind: "photo", src: GUNA_PHOTO }, comingSoon: true },
  { title: "Casco Viejo", tag: "Coming soon", img: { kind: "photo", src: pexels(19620790) }, comingSoon: true },
  { title: "Pedasí", tag: "Coming soon", img: { kind: "photo", src: pexels(18976053) }, comingSoon: true },
  { title: "Coiba", tag: "Coming soon", img: { kind: "photo", src: pexels(4171716) }, comingSoon: true },
  { title: "The Darién", tag: "Coming soon", img: { kind: "photo", src: pexels(36105293) }, comingSoon: true },
];

const ACTIVITIES: Card[] = [
  { title: "Hiking & Trails", tag: "Guide", img: { kind: "photo", src: pexels(10343761) }, href: BOQUETE },
  { title: "Wildlife & Birding", tag: "Guide", img: { kind: "photo", src: pexels(9566563) }, href: EL_VALLE },
  { title: "Surf & Dive", tag: "Guide", img: { kind: "photo", src: pexels(33757647) }, href: BOCAS },
  { title: "Food & Coffee", tag: "Guide", img: { kind: "photo", src: pexels(30658818) }, href: BOQUETE },
  { title: "Eco-tourism", tag: "Guide", img: { kind: "photo", src: pexels(3603874) }, href: EL_VALLE },
  { title: "Cities & Culture", tag: "Guide", img: { kind: "photo", src: pexels(23910182) }, href: PANAMA_CITY },
  { title: "Islands & Beaches", tag: "Guide", img: { kind: "photo", src: pexels(8951333) }, href: BOCAS },
  { title: "Markets & Town Life", tag: "Coming soon", img: { kind: "photo", src: pexels(7823008) }, comingSoon: true },
];

const BOQUETE_GUIDES: Card[] = [
  { title: "Best Hikes in Boquete", tag: "Hiking", img: { kind: "photo", src: "/images/hikes-boquete.webp" }, href: BOQUETE_HIKES },
  { title: "Things to Do in Boquete", tag: "Guide", img: { kind: "photo", src: "/images/things-to-do-boquete.webp" }, href: BOQUETE_TODO },
  { title: "Tours in Boquete", tag: "Tours", img: { kind: "photo", src: "/images/tours-boquete.webp" }, href: BOQUETE_TOURS },
];

const EL_VALLE_GUIDES: Card[] = [
  { title: "Best Hikes in El Valle", tag: "Hiking", img: { kind: "photo", src: "/images/hikes-el-valle.webp" }, href: EV_HIKES },
  { title: "Things to Do in El Valle", tag: "Guide", img: { kind: "photo", src: "/images/things-to-do-el-valle.webp" }, href: EV_TODO },
  { title: "Tours in El Valle", tag: "Tours", img: { kind: "photo", src: "/images/tours-el-valle.webp" }, href: EV_TOURS },
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
        link="Browse destinations"
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
        id="cat-boquete"
        title="Explore Boquete"
        link="All Boquete guides"
        icon="activity"
        cards={BOQUETE_GUIDES}
      />
      <CategorySection
        id="cat-el-valle"
        title="Explore El Valle de Antón"
        link="All El Valle guides"
        icon="activity"
        cards={EL_VALLE_GUIDES}
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
              Field reports from the ground
            </span>
          </div>

          <div className="home-bento-grid">
            <Link href={BOCAS} className="bento-card b1">
              <div className="bento-img-top">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${BOCAS_PHOTO}')` }}
                />
              </div>
              <div className="bento-body">
                <span className="b-tag">Caribbean · Guide</span>
                <h3>Bocas del Toro — nine islands, slow boats, sloths</h3>
                <p>
                  Surfers&rsquo; capital of the Caribbean coast, Afro-Antillean kitchens,
                  and the country&rsquo;s easiest place to wake up on the water.
                </p>
              </div>
            </Link>

            <div className="bento-card b2">
              <span className="b-tag">From the country</span>
              <blockquote>
                We don&rsquo;t have one country here. We have a coast that faces
                Cuba, a coast that faces Ecuador, and a mountain range between
                them that hides whatever it wants to hide.
              </blockquote>
              <cite>— Almirante, Bocas del Toro</cite>
            </div>

            <Link href={PANAMA_CITY} className="bento-card b3">
              <div
                className="imgph photo"
                style={{ backgroundImage: `url('${PANAMA_CITY_PHOTO}')` }}
              />
              <div className="bento-overlay">
                <span className="b-tag">Capital · Guide</span>
                <h3>Panama City</h3>
              </div>
            </Link>

            <Link href={EL_VALLE} className="bento-card b4">
              <span className="b-tag">Highlands · Guide</span>
              <h3>El Valle de Antón — a town inside an extinct volcano.</h3>
              <span className="bento-arrow">Read the guide →</span>
            </Link>

            <Link href={BOQUETE} className="bento-card b5">
              <div className="bento-split-img">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${BOQUETE_PHOTO}')` }}
                />
              </div>
              <div className="bento-split-body">
                <span className="b-tag">Highlands · Guide</span>
                <h3>Boquete — cloud forest, coffee, Volcán Barú</h3>
                <p>
                  The highland town that runs on coffee, rivers, and fog — plus
                  the country&rsquo;s best day hikes from town.
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
