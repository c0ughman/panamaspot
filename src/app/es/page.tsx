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
const EL_VALLE = "/es/articles/que-hacer-el-valle-de-anton";

const BOQUETE_SENDEROS = "/es/articles/senderos-en-boquete-guia-completa";
const BOQUETE_QH = "/es/articles/que-hacer-en-boquete-guia-completa";
const BOQUETE_TOURS_ES = "/es/articles/tours-en-boquete-panama";
const BOQUETE_AGUAS = "/es/articles/aguas-termales-caldera-boquete";
const BOQUETE_ALQUILER = "/es/articles/alquiler-de-bicicletas-boquete";
const BOQUETE_COMO_LLEGAR = "/es/articles/como-llegar-a-boquete-sin-carro";
const EV_SENDEROS = "/es/articles/senderos-el-valle-de-anton";
const EV_QH = "/es/articles/que-hacer-el-valle-de-anton";
const EV_TOURS_ES = "/es/articles/tours-el-valle-de-anton";
const EV_CASCADA = "/es/articles/cascada-chorro-el-macho-el-valle-de-anton";
const EV_DESDE_CIUDAD = "/es/articles/el-valle-de-anton-desde-ciudad-de-panama";
const EV_INDIA_ES = "/es/articles/sendero-india-dormida-el-valle-de-anton";

const BOCAS_PHOTO = pexels(2038744);
const BOQUETE_PHOTO = pexels(2380342);
const PANAMA_CITY_PHOTO = pexels(14840814);
const EL_VALLE_PHOTO = pexels(30774416);

// ── Datos ──────────────────────────────────────────────────────────────────

const REGIONS: Card[] = [
  { title: "Ciudad de Panamá", tag: "Guía", img: { kind: "photo", src: PANAMA_CITY_PHOTO }, href: PANAMA_CITY },
  { title: "El Valle de Antón", tag: "Guía", img: { kind: "photo", src: EL_VALLE_PHOTO }, href: EL_VALLE },
  { title: "Bocas del Toro", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/16146741/pexels-photo-16146741.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama" },
  { title: "Boquete", tag: "Guía", img: { kind: "photo", src: BOQUETE_PHOTO }, href: BOQUETE_QH },
  { title: "Guna Yala", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/30271300/pexels-photo-30271300.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/san-blas-guna-yala-guia-tours-islas" },
  { title: "Casco Viejo", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/18049699/pexels-photo-18049699.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/casco-viejo-restaurantes-donde-comer-beber-hospedarse" },
  { title: "Coiba", tag: "Guía", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Gnathanodon_speciosus.jpg/500px-Gnathanodon_speciosus.jpg" }, href: "/es/articles/isla-coiba-buceo-parque-nacional" },
];

const ACTIVITIES: Card[] = [
  { title: "Ciudades y Cultura", tag: "Guía", img: { kind: "photo", src: pexels(23910182) }, href: PANAMA_CITY },
  { title: "Senderismo", tag: "Guía", img: { kind: "photo", src: pexels(10343761) }, href: EL_VALLE },
  { title: "Ecoturismo", tag: "Guía", img: { kind: "photo", src: pexels(3603874) }, href: EL_VALLE },
  { title: "Fauna y Aves", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/12861718/pexels-photo-12861718.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/zoologico-el-nispero-el-valle-de-anton" },
  { title: "Surf y Buceo", tag: "Guía", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Gnathanodon_speciosus.jpg/500px-Gnathanodon_speciosus.jpg" }, href: "/es/articles/isla-coiba-buceo-parque-nacional" },
  { title: "Comida y Café", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/18049699/pexels-photo-18049699.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/casco-viejo-restaurantes-donde-comer-beber-hospedarse" },
  { title: "Islas y Playas", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/30271300/pexels-photo-30271300.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/san-blas-guna-yala-guia-tours-islas" },
];

const BOQUETE_GUIAS: Card[] = [
  { title: "Mejores Senderos en Boquete", tag: "Senderismo", img: { kind: "photo", src: "/images/hikes-boquete.webp" }, href: BOQUETE_SENDEROS },
  { title: "Qué Hacer en Boquete", tag: "Guía", img: { kind: "photo", src: "/images/things-to-do-boquete.webp" }, href: BOQUETE_QH },
  { title: "Tours en Boquete", tag: "Tours", img: { kind: "photo", src: "/images/boquete/boquete-clouds.webp" }, href: BOQUETE_TOURS_ES },
  { title: "Aguas Termales de Caldera", tag: "Guía", img: { kind: "photo", src: "/images/boquete/boquete-river2.webp" }, href: BOQUETE_AGUAS },
  { title: "Alquiler de Bicicletas", tag: "Tours", img: { kind: "photo", src: "/images/boquete/boquete-ebike-trail.webp" }, href: BOQUETE_ALQUILER },
  { title: "Cómo Llegar a Boquete", tag: "Guía", img: { kind: "photo", src: "/images/boquete/boquete-hills.webp" }, href: BOQUETE_COMO_LLEGAR },
  { title: "Subir al Volcán Barú", tag: "Senderismo", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Volcan_Baru_up_close_and_clouded.jpg/500px-Volcan_Baru_up_close_and_clouded.jpg" }, href: "/es/articles/volcan-baru-como-subir-cima-panama" },
  { title: "Guía Completa de Boquete", tag: "Guía", img: { kind: "photo", src: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Aerial_view_of_Boquete%2C_Panama.jpg/500px-Aerial_view_of_Boquete%2C_Panama.jpg" }, href: "/es/articles/boquete-panama-guia-completa-itinerario" },
  { title: "Rafting Río Chiriquí", tag: "Tours", img: { kind: "photo", src: "https://images.pexels.com/photos/36791113/pexels-photo-36791113.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/rafting-boquete-rio-chiriqui" },
];

const EL_VALLE_GUIAS: Card[] = [
  { title: "Senderos en El Valle", tag: "Senderismo", img: { kind: "photo", src: "/images/el-valle/elvalle-shrine.webp" }, href: EV_SENDEROS },
  { title: "Qué Hacer en El Valle", tag: "Guía", img: { kind: "photo", src: "/images/things-to-do-el-valle.webp" }, href: EV_QH },
  { title: "Tours en El Valle", tag: "Tours", img: { kind: "photo", src: "/images/tours-el-valle.webp" }, href: EV_TOURS_ES },
  { title: "Cascada Chorro El Macho", tag: "Guía", img: { kind: "photo", src: "/images/el-valle/elvalle-elmachowaterfall.webp" }, href: EV_CASCADA },
  { title: "El Valle desde Ciudad de Panamá", tag: "Guía", img: { kind: "photo", src: "/images/el-valle/elvalle-panorama.webp" }, href: EV_DESDE_CIUDAD },
  { title: "Sendero India Dormida", tag: "Senderismo", img: { kind: "photo", src: "/images/el-valle/elvalle-indiadormida.webp" }, href: EV_INDIA_ES },
  { title: "Aguas Termales de El Valle", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/920270/pexels-photo-920270.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/aguas-termales-el-valle-de-anton" },
  { title: "Canopy y Aventura", tag: "Tours", img: { kind: "photo", src: "https://images.pexels.com/photos/28518788/pexels-photo-28518788.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/canopy-el-valle-de-anton-cabalgatas-aventura" },
  { title: "Zoológico El Níspero", tag: "Familia", img: { kind: "photo", src: "https://images.pexels.com/photos/12861718/pexels-photo-12861718.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/zoologico-el-nispero-el-valle-de-anton" },
];

const PANAMA_CITY_GUIAS: Card[] = [
  { title: "Qué Hacer en la Ciudad", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/que-hacer-en-ciudad-de-panama" },
  { title: "Casco Viejo: Restaurantes", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/18049699/pexels-photo-18049699.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/casco-viejo-restaurantes-donde-comer-beber-hospedarse" },
  { title: "Cinta Costera y Mercado", tag: "Guía", img: { kind: "photo", src: "https://images.pexels.com/photos/5005136/pexels-photo-5005136.jpeg?auto=compress&cs=tinysrgb&w=700" }, href: "/es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo" },
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
        id="cat-ciudad-panama"
        title="Explora Ciudad de Panamá"
        link="Todas las guías de la ciudad"
        icon="activity"
        cards={PANAMA_CITY_GUIAS}
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
