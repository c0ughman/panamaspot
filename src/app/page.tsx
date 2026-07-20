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
const BOQUETE = "/articles/things-to-do-in-boquete-panama";
const PANAMA_CITY = "/articles/panama-city";
const EL_VALLE = "/articles/things-to-do-el-valle-de-anton";

const BOQUETE_HIKES = "/articles/hikes-in-boquete";
const BOQUETE_TODO = "/articles/things-to-do-in-boquete-panama";
const BOQUETE_TOURS = "/articles/tours-in-boquete-panama";
const BOQUETE_COFFEE = "/articles/boquete-coffee-farm-tour";
const BOQUETE_CALDERA = "/articles/caldera-hot-springs-boquete";
const BOQUETE_WATERFALLS = "/articles/lost-waterfalls-boquete-hiking-guide";
const EV_HIKES = "/articles/hikes-el-valle-de-anton";
const EV_TODO = "/articles/things-to-do-el-valle-de-anton";
const EV_TOURS = "/articles/tours-en-el-valle-de-anton";
const EV_CHORRO = "/articles/chorro-el-macho-waterfall-el-valle-de-anton";
const EV_DAY_TRIP = "/articles/el-valle-day-trip-from-panama-city";
const EV_INDIA = "/articles/india-dormida-hike-el-valle-de-anton";

const BOCAS_PHOTO = pexels(2038744);
const BOQUETE_PHOTO = pexels(2380342);
const PANAMA_CITY_PHOTO = pexels(14840814);
const EL_VALLE_PHOTO = pexels(30774416);

// ── Data ─────────────────────────────────────────────────────────────────────

const REGIONS: Card[] = [
  { title: "Bocas del Toro", tag: "Guide", img: { kind: "photo", src: BOCAS_PHOTO }, href: BOCAS },
  { title: "Boquete", tag: "Guide", img: { kind: "photo", src: BOQUETE_PHOTO }, href: BOQUETE },
  { title: "Panama City", tag: "Guide", img: { kind: "photo", src: PANAMA_CITY_PHOTO }, href: PANAMA_CITY },
  { title: "El Valle de Antón", tag: "Guide", img: { kind: "photo", src: EL_VALLE_PHOTO }, href: EL_VALLE },
  { title: "Casco Viejo", tag: "Guide", img: { kind: "photo", src: "https://images.pexels.com/photos/18049699/pexels-photo-18049699.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/articles/casco-viejo-panama-walking-guide" },
];

const ACTIVITIES: Card[] = [
  { title: "Hiking & Trails", tag: "Guide", img: { kind: "photo", src: pexels(10343761) }, href: BOQUETE },
  { title: "Wildlife & Birding", tag: "Guide", img: { kind: "photo", src: pexels(9566563) }, href: EL_VALLE },
  { title: "Surf & Dive", tag: "Guide", img: { kind: "photo", src: pexels(33757647) }, href: BOCAS },
  { title: "Food & Coffee", tag: "Guide", img: { kind: "photo", src: pexels(30658818) }, href: BOQUETE },
  { title: "Eco-tourism", tag: "Guide", img: { kind: "photo", src: pexels(3603874) }, href: EL_VALLE },
  { title: "Cities & Culture", tag: "Guide", img: { kind: "photo", src: pexels(23910182) }, href: PANAMA_CITY },
  { title: "Islands & Beaches", tag: "Guide", img: { kind: "photo", src: "https://images.pexels.com/photos/30826590/pexels-photo-30826590.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/articles/bocas-del-toro-island-hopping-guide" },
];

const BOQUETE_GUIDES: Card[] = [
  { title: "Best Hikes in Boquete", tag: "Hiking", img: { kind: "photo", src: "/images/hikes-boquete.webp" }, href: BOQUETE_HIKES },
  { title: "Things to Do in Boquete", tag: "Guide", img: { kind: "photo", src: "/images/things-to-do-boquete.webp" }, href: BOQUETE_TODO },
  { title: "Tours in Boquete", tag: "Tours", img: { kind: "photo", src: "/images/boquete/boquete-clouds.webp" }, href: BOQUETE_TOURS },
  { title: "Lost Waterfalls", tag: "Hiking", img: { kind: "photo", src: "/images/boquete/boquete-manmadewaterfall.webp" }, href: BOQUETE_WATERFALLS },
  { title: "Coffee Farm Tours", tag: "Guide", img: { kind: "photo", src: pexels(7761601) }, href: BOQUETE_COFFEE },
  { title: "Caldera Hot Springs", tag: "Guide", img: { kind: "photo", src: "/images/boquete/boquete-river2.webp" }, href: BOQUETE_CALDERA },
  { title: "Volcán Barú Sunrise Hike", tag: "Hiking", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Volcan_Baru_up_close_and_clouded.jpg/500px-Volcan_Baru_up_close_and_clouded.jpg" }, href: "/articles/volcan-baru-hike-sunrise-summit-guide" },
  { title: "Boquete Travel Guide", tag: "Guide", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Aerial_view_of_Boquete%2C_Panama.jpg/500px-Aerial_view_of_Boquete%2C_Panama.jpg" }, href: "/articles/boquete-travel-guide" },
  { title: "Finca Lérida Birdwatching", tag: "Wildlife", img: { kind: "photo", src: "https://images.pexels.com/photos/16017280/pexels-photo-16017280.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/articles/finca-lerida-los-quetzales-trail-birdwatching-boquete" },
];

const EL_VALLE_GUIDES: Card[] = [
  { title: "Best Hikes in El Valle", tag: "Hiking", img: { kind: "photo", src: "/images/hikes-el-valle.webp" }, href: EV_HIKES },
  { title: "Things to Do in El Valle", tag: "Guide", img: { kind: "photo", src: "/images/things-to-do-el-valle.webp" }, href: EV_TODO },
  { title: "Tours in El Valle", tag: "Tours", img: { kind: "photo", src: "/images/tours-el-valle.webp" }, href: EV_TOURS },
  { title: "Chorro El Macho Waterfall", tag: "Guide", img: { kind: "photo", src: "/images/el-valle/elvalle-elmachowaterfall.webp" }, href: EV_CHORRO },
  { title: "El Valle Day Trip", tag: "Guide", img: { kind: "photo", src: "/images/el-valle/elvalle-panorama.webp" }, href: EV_DAY_TRIP },
  { title: "India Dormida Hike", tag: "Hiking", img: { kind: "photo", src: "/images/el-valle/elvalle-indiadormida.webp" }, href: EV_INDIA },
  { title: "El Valle Waterfalls", tag: "Guide", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/ChorroMachoElValle.jpg/500px-ChorroMachoElValle.jpg" }, href: "/articles/el-valle-de-anton-waterfalls" },
  { title: "Cerro Gaital & Cara Iguana", tag: "Hiking", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Anton_Valle_foothills_-_Flickr_-_gailhampshire.jpg/500px-Anton_Valle_foothills_-_Flickr_-_gailhampshire.jpg" }, href: "/articles/cerro-gaital-cara-iguana-hike-el-valle" },
  { title: "El Valle With Kids", tag: "Family", img: { kind: "photo", src: "https://images.pexels.com/photos/12861718/pexels-photo-12861718.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/articles/el-valle-de-anton-with-kids" },
];

const PANAMA_CITY_GUIDES: Card[] = [
  { title: "Panama City in 3 Days", tag: "Itinerary", img: { kind: "photo", src: "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/articles/panama-city-itinerary-3-days" },
  { title: "Casco Viejo Walking Guide", tag: "Guide", img: { kind: "photo", src: "https://images.pexels.com/photos/18049699/pexels-photo-18049699.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/articles/casco-viejo-panama-walking-guide" },
  { title: "Panama Canal & Miraflores", tag: "Guide", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Panama_Canal_Gatun_Locks.jpg/500px-Panama_Canal_Gatun_Locks.jpg" }, href: "/articles/panama-canal-tour-miraflores-locks-visitor-guide" },
  { title: "Amador Causeway & Biomuseo", tag: "Guide", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Causeway_de_Amador_17-12-14.jpg/500px-Causeway_de_Amador_17-12-14.jpg" }, href: "/articles/amador-causeway-biomuseo-guide" },
  { title: "Best Day Trips From the City", tag: "Day trips", img: { kind: "photo", src: "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/articles/day-trips-from-panama-city" },
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
        id="cat-panama-city"
        title="Explore Panama City"
        link="All Panama City guides"
        icon="activity"
        cards={PANAMA_CITY_GUIDES}
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
