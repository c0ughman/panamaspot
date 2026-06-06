import type { Metadata } from "next";
import Link from "next/link";
import { buildMetadata } from "@/lib/seo";
import { webPageJsonLd, jsonLdScript } from "@/lib/jsonld";
import { HeroParallax } from "@/components/hero-parallax";
import { SiteFooter } from "@/components/site-footer";
import { HtmlLang } from "@/components/html-lang";
import { CategorySection, pexels, type Card } from "@/components/home-sections";

const HERO_BG = pexels(2474690, 2400);

export const metadata: Metadata = buildMetadata({
  title: "Guía de Viajes de Panamá: Destinos, Qué Hacer y Consejos Locales",
  description:
    "Planifica tu viaje a Panamá con guías a fondo de sus playas, bosques nubosos, islas y ciudades: a dónde ir, cuándo visitar y qué hacer, escritas por quienes vivimos aquí.",
  path: "/es",
  absoluteTitle: true,
  ogLocale: "es_PA",
  ogImage: HERO_BG,
  languages: { en: "/", es: "/es", "x-default": "/" },
});

const PANAMA_CITY = "/es/articles/panama-city";
const EL_VALLE = "/es/articles/el-valle-de-anton";

const BOQUETE_SENDEROS = "/es/articles/senderos-en-boquete-guia-completa.html";
const BOQUETE_QH = "/es/articles/que-hacer-en-boquete-guia-completa.html";
const BOQUETE_TOURS_ES = "/es/articles/tours-en-boquete-panama.html";
const EV_SENDEROS = "/es/articles/senderos-el-valle-de-anton.html";
const EV_QH = "/es/articles/que-hacer-el-valle-de-anton.html";
const EV_TOURS_ES = "/es/articles/tours-el-valle-de-anton.html";

const BOCAS_PHOTO = pexels(2038744);
const BOQUETE_PHOTO = pexels(2380342);
const PANAMA_CITY_PHOTO = pexels(14840814);
const EL_VALLE_PHOTO = pexels(30774416);
const GUNA_PHOTO = pexels(31416948);

// ── Datos ──────────────────────────────────────────────────────────────────

const REGIONS: Card[] = [
  { title: "Ciudad de Panamá", tag: "Guía", img: { kind: "photo", src: PANAMA_CITY_PHOTO }, href: PANAMA_CITY },
  { title: "El Valle de Antón", tag: "Guía", img: { kind: "photo", src: EL_VALLE_PHOTO }, href: EL_VALLE },
  { title: "Bocas del Toro", tag: "Próximamente", img: { kind: "photo", src: BOCAS_PHOTO }, comingSoon: true },
  { title: "Boquete", tag: "Próximamente", img: { kind: "photo", src: BOQUETE_PHOTO }, comingSoon: true },
  { title: "Guna Yala", tag: "Próximamente", img: { kind: "photo", src: GUNA_PHOTO }, comingSoon: true },
  { title: "Casco Viejo", tag: "Próximamente", img: { kind: "photo", src: pexels(19620790) }, comingSoon: true },
  { title: "Pedasí", tag: "Próximamente", img: { kind: "photo", src: pexels(18976053) }, comingSoon: true },
  { title: "Coiba", tag: "Próximamente", img: { kind: "photo", src: pexels(4171716) }, comingSoon: true },
  { title: "El Darién", tag: "Próximamente", img: { kind: "photo", src: pexels(36105293) }, comingSoon: true },
];

const ACTIVITIES: Card[] = [
  { title: "Ciudades y Cultura", tag: "Guía", img: { kind: "photo", src: pexels(23910182) }, href: PANAMA_CITY },
  { title: "Senderismo", tag: "Guía", img: { kind: "photo", src: pexels(10343761) }, href: EL_VALLE },
  { title: "Ecoturismo", tag: "Guía", img: { kind: "photo", src: pexels(3603874) }, href: EL_VALLE },
  { title: "Fauna y Aves", tag: "Próximamente", img: { kind: "photo", src: pexels(9566563) }, comingSoon: true },
  { title: "Surf y Buceo", tag: "Próximamente", img: { kind: "photo", src: pexels(33757647) }, comingSoon: true },
  { title: "Comida y Café", tag: "Próximamente", img: { kind: "photo", src: pexels(30658818) }, comingSoon: true },
  { title: "Islas y Playas", tag: "Próximamente", img: { kind: "photo", src: pexels(8951333) }, comingSoon: true },
];

const BOQUETE_GUIAS: Card[] = [
  { title: "Mejores Senderos en Boquete", tag: "Senderismo", img: { kind: "photo", src: "/images/hikes-boquete.jpg" }, href: BOQUETE_SENDEROS },
  { title: "Qué Hacer en Boquete", tag: "Guía", img: { kind: "photo", src: "/images/things-to-do-boquete.HEIC" }, href: BOQUETE_QH },
  { title: "Tours en Boquete", tag: "Tours", img: { kind: "photo", src: "/images/tours-boquete.jpeg.webp" }, href: BOQUETE_TOURS_ES },
];

const EL_VALLE_GUIAS: Card[] = [
  { title: "Senderos en El Valle", tag: "Senderismo", img: { kind: "photo", src: "/images/hikes-el-valle.jpg" }, href: EV_SENDEROS },
  { title: "Qué Hacer en El Valle", tag: "Guía", img: { kind: "photo", src: "/images/things-to-do-el-valle.jpg" }, href: EV_QH },
  { title: "Tours en El Valle", tag: "Tours", img: { kind: "photo", src: "/images/tours-el-valle.jpg" }, href: EV_TOURS_ES },
];

export default function HomeEs() {
  return (
    <>
      <HtmlLang lang="es" />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={jsonLdScript(
          webPageJsonLd({
            path: "/es",
            name: "Guía de Viajes de Panamá",
            description:
              "Guías a fondo, itinerarios y conocimiento local para viajar por Panamá: playas, bosques nubosos, islas y ciudades.",
            locale: "es",
            primaryImage: HERO_BG,
          }),
        )}
      />

      <HeroParallax
        bgImage={HERO_BG}
        locale="es"
        subtitle="La guía completa para viajar por Panamá — nueve provincias, tres costas, escrita por quienes vivimos aquí."
        ctaLabel="Empieza a explorar →"
        ctaHref="#cat-regions"
      />

      <CategorySection
        id="cat-regions"
        title="¿En qué parte de Panamá?"
        link="Explora destinos"
        icon="region"
        cards={REGIONS}
      />
      <CategorySection
        id="cat-activities"
        title="¿Qué vas a hacer?"
        link="Explora por actividad"
        icon="activity"
        cards={ACTIVITIES}
      />
      <CategorySection
        id="cat-boquete"
        title="Explora Boquete"
        link="Todas las guías de Boquete"
        icon="activity"
        cards={BOQUETE_GUIAS}
      />
      <CategorySection
        id="cat-el-valle"
        title="Explora El Valle de Antón"
        link="Todas las guías de El Valle"
        icon="activity"
        cards={EL_VALLE_GUIAS}
      />

      <section className="home-bento">
        <div className="container">
          <div className="home-bento-head">
            <h2>
              Siete Panamás,
              <br />
              un istmo.
            </h2>
            <span className="cat-section-link cat-section-link--muted">
              Reportajes desde el terreno
            </span>
          </div>

          <div className="home-bento-grid">
            <div className="bento-card b1 bento-card--soon">
              <div className="bento-img-top">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${BOCAS_PHOTO}')` }}
                />
              </div>
              <div className="bento-body">
                <span className="b-tag">Caribe · Próximamente</span>
                <h3>Bocas del Toro — nueve islas, lanchas lentas, perezosos</h3>
                <p>
                  La capital del surf en el Caribe, cocinas afroantillanas y el
                  lugar más fácil del país para despertar sobre el agua.
                </p>
              </div>
            </div>

            <div className="bento-card b2">
              <span className="b-tag">Desde el país</span>
              <blockquote>
                Aquí no tenemos un solo país. Tenemos una costa que mira a Cuba,
                una costa que mira a Ecuador, y una cordillera en medio que
                esconde lo que le da la gana.
              </blockquote>
              <cite>— Almirante, Bocas del Toro</cite>
            </div>

            <Link href={PANAMA_CITY} className="bento-card b3">
              <div
                className="imgph photo"
                style={{ backgroundImage: `url('${PANAMA_CITY_PHOTO}')` }}
              />
              <div className="bento-overlay">
                <span className="b-tag">Capital · Guía</span>
                <h3>Ciudad de Panamá</h3>
              </div>
            </Link>

            <Link href={EL_VALLE} className="bento-card b4">
              <span className="b-tag">Tierras altas · Guía</span>
              <h3>El Valle de Antón — un pueblo dentro de un volcán extinto.</h3>
              <span className="bento-arrow">Leer la guía →</span>
            </Link>

            <div className="bento-card b5 bento-card--soon">
              <div className="bento-split-img">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${BOQUETE_PHOTO}')` }}
                />
              </div>
              <div className="bento-split-body">
                <span className="b-tag">Tierras altas · Próximamente</span>
                <h3>Boquete — bosque nuboso, café, Volcán Barú</h3>
                <p>
                  El pueblo de montaña que vive del café, los ríos y la neblina —
                  la guía en español llega pronto.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <SiteFooter locale="es" />
    </>
  );
}
