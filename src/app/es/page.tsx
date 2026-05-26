import type { Metadata } from "next";
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
const BOCAS_PHOTO = pexels(2038744);
const GUNA_PHOTO = pexels(31416948);

// ── Datos ──────────────────────────────────────────────────────────────────
// Aún no hay artículos en español, así que todas las tarjetas van como
// "Próximamente" (sin enlace). Cuando existan guías en /es/articles/…,
// añade el href correspondiente, igual que en la home en inglés.

const REGIONS: Card[] = [
  { title: "Costa Caribe", tag: "Próximamente", img: { kind: "photo", src: pexels(14185535) } },
  { title: "Lado Pacífico", tag: "Próximamente", img: { kind: "photo", src: pexels(34205250) } },
  { title: "Tierras Altas de Chiriquí", tag: "Próximamente", img: { kind: "photo", src: pexels(2918139) } },
  { title: "Ciudad de Panamá", tag: "Próximamente", img: { kind: "photo", src: pexels(2666249) } },
  { title: "Península de Azuero", tag: "Próximamente", img: { kind: "photo", src: pexels(36601635) } },
  { title: "Islas del Pacífico", tag: "Próximamente", img: { kind: "photo", src: pexels(4766708) } },
  { title: "Comarcas Indígenas", tag: "Próximamente", img: { kind: "photo", src: pexels(9122911) } },
];

const ACTIVITIES: Card[] = [
  { title: "Senderismo", tag: "Próximamente", img: { kind: "photo", src: pexels(10343761) } },
  { title: "Fauna y Aves", tag: "Próximamente", img: { kind: "photo", src: pexels(9566563) } },
  { title: "Surf y Buceo", tag: "Próximamente", img: { kind: "photo", src: pexels(33757647) } },
  { title: "Comida y Café", tag: "Próximamente", img: { kind: "photo", src: pexels(30658818) } },
  { title: "Ecoturismo", tag: "Próximamente", img: { kind: "photo", src: pexels(3603874) } },
  { title: "Ciudades y Cultura", tag: "Próximamente", img: { kind: "photo", src: pexels(23910182) } },
  { title: "Islas y Playas", tag: "Próximamente", img: { kind: "photo", src: pexels(8951333) } },
];

const DESTINATIONS: Card[] = [
  { title: "Bocas del Toro", tag: "Próximamente", img: { kind: "photo", src: BOCAS_PHOTO } },
  { title: "Guna Yala", tag: "Próximamente", img: { kind: "photo", src: GUNA_PHOTO } },
  { title: "Boquete", tag: "Próximamente", img: { kind: "photo", src: pexels(2380342) } },
  { title: "Casco Viejo", tag: "Próximamente", img: { kind: "photo", src: pexels(19620790) } },
  { title: "Pedasí", tag: "Próximamente", img: { kind: "photo", src: pexels(18976053) } },
  { title: "Coiba", tag: "Próximamente", img: { kind: "photo", src: pexels(4171716) } },
  { title: "El Darién", tag: "Próximamente", img: { kind: "photo", src: pexels(36105293) } },
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
        link="Explora por región"
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
        id="cat-destinations"
        title="¿Por dónde empezar?"
        link="Explora destinos"
        icon="destination"
        cards={DESTINATIONS}
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
              Más guías próximamente
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
              <cite>— Iván Bethancourt · Almirante</cite>
            </div>

            <div className="bento-card b3">
              <div
                className="imgph photo"
                style={{ backgroundImage: `url('${pexels(5374189)}')` }}
              />
              <div className="bento-overlay">
                <span className="b-tag">Indígena · Próximamente</span>
                <h3>Guna Yala</h3>
              </div>
            </div>

            <div className="bento-card b4">
              <span className="b-tag">Itinerarios · Próximamente</span>
              <h3>Crea un itinerario de Panamá en 10 minutos.</h3>
              <span className="bento-arrow">Próximamente</span>
            </div>

            <div className="bento-card b5">
              <div className="bento-split-img">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(9246451)}')` }}
                />
              </div>
              <div className="bento-split-body">
                <span className="b-tag">Tierras altas · Próximamente</span>
                <h3>Chiriquí — bosque nuboso, café, Volcán Barú</h3>
                <p>
                  El bosque nuboso, el café de altura y el Volcán Barú — nuestra
                  guía de Chiriquí llega pronto.
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
