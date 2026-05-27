/* ============================================================================
   Ciudad de Panamá — guía de destino (tema AZUL) · versión en español
   Traducción de articles/panama-city. Misma estructura, estilos e imágenes;
   solo cambia el texto (español) y locale="es" (vive en /es/articles/…).
   ========================================================================== */

import type { Metadata } from "next";
import Link from "next/link";
import { buildMetadata } from "@/lib/seo";
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
  locale: "es" as "en" | "es",
  seoTitle: "Guía de Ciudad de Panamá: Casco Viejo, el Canal y Qué Hacer",
  title: "Ciudad de Panamá — donde un casco antiguo del siglo XVI vigila un horizonte de cristal.",
  description:
    "Una guía completa de la Ciudad de Panamá: cómo llegar, cuándo ir, dónde hospedarte y qué vale la pena — desde el casco antiguo, Patrimonio de la Humanidad, hasta el canal que la construyó.",
  section: "Destinos",
  publishedAt: "2026-05-26",
  modifiedAt: "2026-05-26",
  author: "Mariela Ortiz-Saavedra",
  breadcrumb: ["Provincia de Panamá", "Capital", "Ciudad de Panamá"],
  heroTags: ["Capital", "Guía de ciudad", "Actualizado · Mayo 2026"],
} as const;

const TOC_ITEMS = [
  { id: "s1", n: "01", label: "Por qué ir" },
  { id: "s2", n: "02", label: "Cómo llegar" },
  { id: "s3", n: "03", label: "Cuándo visitar" },
  { id: "s4", n: "04", label: "Dónde hospedarse" },
  { id: "s5", n: "05", label: "Qué hacer" },
  { id: "s6", n: "06", label: "Antes de ir" },
  { id: "s7", n: "07", label: "Preguntas" },
];

const GALLERY = [
  { src: pexels(2666249), caption: "El horizonte del Pacífico desde la bahía", feature: true },
  { src: pexels(18118099), caption: "La Avenida Balboa iluminada de noche" },
  { src: pexels(5864401), caption: "Palmeras y rascacielos, lado a lado" },
  { src: pexels(2146686), caption: "Atardecer sobre el distrito financiero" },
  { src: pexels(13110362), caption: "La ciudad desde el aire" },
] as const;

const HIGHLIGHTS = [
  { stat: "1519", title: "La más antigua del Pacífico", body: "Panamá Viejo fue la primera ciudad europea en la costa del Pacífico de América — sus ruinas siguen en pie en el extremo este de la ciudad." },
  { stat: "80 km", title: "Construida por el canal", body: "El Canal de Panamá va de la ciudad al Caribe; las Esclusas de Miraflores quedan a un corto trayecto del centro." },
  { stat: "1.º", title: "El metro de Centroamérica", body: "El primer sistema de metro de la región, sumado a las apps de transporte, hace fácil cruzar una ciudad extensa." },
] as const;

const FAQ_ITEMS = [
  {
    question: "¿Es segura la Ciudad de Panamá para visitantes?",
    answer:
      "Las principales zonas turísticas —Casco Viejo, el área bancaria, la Cinta Costera y Amador— están bien vigiladas y se caminan sin problema de día y de noche. Usa el sentido común de cualquier gran ciudad por la noche, no exhibas objetos de valor y evita barrios como El Chorrillo y Curundú salvo que tengas un motivo local para estar ahí.",
  },
  {
    question: "¿Cuántos días necesito?",
    answer:
      "De tres a cuatro. Dedica un día completo a recorrer Casco Viejo a pie, medio día al Canal de Panamá y al malecón, y el resto a Panamá Viejo, el Biomuseo o una excursión de un día a la selva o a las playas del Pacífico.",
  },
  {
    question: "¿Cómo me muevo por la ciudad?",
    answer:
      "El metro y las apps de transporte son baratos y confiables; el casco antiguo se recorre entero a pie. El tráfico es pesado en hora pico, así que planifica los trayectos al canal y al aeropuerto en torno a él.",
  },
  {
    question: "¿Puedo visitar el Canal de Panamá?",
    answer:
      "Sí. El centro de visitantes de las Esclusas de Miraflores queda a unos 20 minutos de Casco Viejo y tiene miradores y un museo. Ve a media mañana o al final de la tarde para ver los barcos cruzando las esclusas.",
  },
] as const;

export const metadata: Metadata = buildMetadata({
  title: ARTICLE.seoTitle,
  description: ARTICLE.description,
  path: `/es/articles/${ARTICLE.slug}`,
  ogImage: HERO_IMAGE,
  type: "article",
  publishedTime: ARTICLE.publishedAt,
  modifiedTime: ARTICLE.modifiedAt,
  authors: [ARTICLE.author],
  ogLocale: "es_PA",
  languages: {
    en: `/articles/${ARTICLE.slug}`,
    es: `/es/articles/${ARTICLE.slug}`,
  },
});

export default function ArticlePage() {
  const path = `/es/articles/${ARTICLE.slug}`;

  const jsonLd = [
    breadcrumbJsonLd([
      { name: "Inicio", path: "/es" },
      { name: ARTICLE.breadcrumb[ARTICLE.breadcrumb.length - 1], path },
    ]),
    articleJsonLd({
      headline: ARTICLE.title,
      description: ARTICLE.description,
      path,
      image: HERO_IMAGE,
      datePublished: ARTICLE.publishedAt,
      dateModified: ARTICLE.modifiedAt,
      authorName: ARTICLE.author,
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

      <HtmlLang lang="es" />

      <main className="article-page">
        <ReadingProgress />

        {/* ===== HERO ===== */}
        <ArticleHero
          bgImage={HERO_IMAGE}
          locale={ARTICLE.locale}
          enHref={`/articles/${ARTICLE.slug}`}
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
            <nav className="breadcrumb" aria-label="Ruta de navegación">
              <Link href="/es">Inicio</Link>
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
                  Ciudad de Panamá — donde un casco antiguo del siglo XVI vigila un{" "}
                  <em>horizonte de cristal.</em>
                </h1>
                <p className="art-dek">
                  La capital más vertical de Latinoamérica lleva su historia a
                  flor de piel: un casco antiguo declarado Patrimonio de la
                  Humanidad, el canal que la construyó y un horizonte del Pacífico
                  que nunca deja de crecer.
                </p>

                <div className="art-byline">
                  <div className="byline-photo">M</div>
                  <div className="byline-meta">
                    <div className="name">{ARTICLE.author}</div>
                    <div className="role">
                      Reportera de campo · Panamá · 14 años sobre el terreno
                    </div>
                  </div>
                  <div className="byline-stats">
                    <span>
                      <strong>9 min</strong> de lectura
                    </span>
                    <span>
                      <time dateTime={ARTICLE.modifiedAt}>
                        <strong>26 may</strong> · 2026
                      </time>
                    </span>
                  </div>
                </div>
              </div>

              <aside className="fact-card">
                <h4>De un vistazo</h4>
                <div className="fact-row">
                  <span className="k">Región</span>
                  <span className="v">Provincia de Panamá</span>
                </div>
                <div className="fact-row">
                  <span className="k">Fundada</span>
                  <span className="v">1519</span>
                </div>
                <div className="fact-row">
                  <span className="k">Cómo llegar</span>
                  <span className="v">PTY · Tocumen</span>
                </div>
                <div className="fact-row">
                  <span className="k">Mejores meses</span>
                  <span className="v">Dic–Abr</span>
                </div>
                <div className="fact-row">
                  <span className="k">Hospedaje</span>
                  <span className="v">3–4 noches</span>
                </div>
                <div className="fact-row">
                  <span className="k">Idioma</span>
                  <span className="v">ES / EN</span>
                </div>
                <div className="fact-rating">
                  <span className="lbl">Costo</span>
                  <Bar on={3} />
                  <span className="lbl">Multitudes</span>
                  <Bar on={4} />
                  <span className="lbl">Vida nocturna</span>
                  <Bar on={5} />
                  <span className="lbl">Cultura</span>
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
                Aterrizas, y la ciudad te golpea en dos registros a la vez: un
                muro de torres de cristal a lo largo de la bahía y, en algún lugar
                detrás de ellas, un grupo bajo de techos de teja que lleva ahí 350
                años. La Ciudad de Panamá es una capital que nunca eligió un solo
                siglo para vivir.
              </p>

              <p>
                Esta guía asume que nunca has estado. Está hecha para responder
                las preguntas que de verdad tendrás, en el orden en que las
                tendrás — y para dejar fuera el relleno.
              </p>

              <h2 id="s1">
                <span className="num">Sección 01</span>Por qué ir
              </h2>

              <p>
                Es la capital más cosmopolita de Centroamérica, y la única con un
                casco antiguo declarado Patrimonio de la Humanidad, un canal que
                cambió el mundo y un horizonte que rivaliza con el de Miami — todo
                a pocos kilómetros entre sí. Súmale una escena seria de
                gastronomía y azoteas, y selva que alcanzas antes del almuerzo, y
                los días se llenan solos.
              </p>

              <div className="callout">
                <span className="label">Nota de campo · Hospédate en el casco antiguo</span>
                Duerme en Casco Viejo si puedes. Es caminable, seguro, y pone la
                parte más bonita de la ciudad frente a tu puerta de noche — cuando
                los visitantes de paso se han ido y abren las azoteas.
              </div>

              <figure className="fig">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(19620790)}')` }}
                />
                <figcaption>
                  <span>
                    <strong>Casco Viejo.</strong> El barrio colonial restaurado es
                    el corazón histórico de la ciudad — y su rincón más caminable.
                  </span>
                </figcaption>
              </figure>

              <h2 id="s2">
                <span className="num">Sección 02</span>Cómo llegar
              </h2>

              <p>
                El Aeropuerto Internacional de Tocumen (PTY) es el mayor centro de
                conexiones de la región, así que llegar es lo fácil. Del
                aeropuerto al centro son unos 30 a 45 minutos en taxi o transporte
                por app, o un trayecto más largo pero barato en el metro y un bus
                de enlace.
              </p>

              <table className="compare">
                <thead>
                  <tr>
                    <th>Desde el aeropuerto</th>
                    <th>Medio</th>
                    <th>Costo</th>
                    <th>Tiempo</th>
                    <th>Comodidad</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Transporte por app</td>
                    <td>Uber / app</td>
                    <td>$18–$30</td>
                    <td>30–45 min</td>
                    <td>
                      <span className="pill good">Lo más fácil</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Taxi del aeropuerto</td>
                    <td>Mostrador oficial</td>
                    <td>$30–$40</td>
                    <td>30–45 min</td>
                    <td>
                      <span className="pill good">Simple</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Metro + bus</td>
                    <td>Línea 2 + transbordo</td>
                    <td>$1.25</td>
                    <td>60–80 min</td>
                    <td>
                      <span className="pill mid">Lo más barato</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Traslado del hotel</td>
                    <td>Reservado</td>
                    <td>$25–$45</td>
                    <td>30–45 min</td>
                    <td>
                      <span className="pill good">Puerta a puerta</span>
                    </td>
                  </tr>
                </tbody>
              </table>

              <h2 id="s3">
                <span className="num">Sección 03</span>Cuándo visitar
              </h2>

              <p>
                La estación seca —de mediados de diciembre a abril— trae los días
                más despejados y menos húmedos, y es cuando la ciudad se disfruta
                mejor para caminar Casco Viejo y el malecón. Enero y febrero son
                especialmente agradables. La estación verde es más calurosa y
                lluviosa, pero más tranquila y económica.
              </p>

              <h2 id="s4">
                <span className="num">Sección 04</span>Dónde hospedarse
              </h2>

              <p>
                Elige tu base según el ánimo. El casco antiguo cambia comodidad
                por ambiente; los distritos modernos cambian encanto por vistas al
                horizonte y logística fácil para negocios.
              </p>

              <ul>
                <li>
                  <strong>Casco Viejo:</strong> hoteles boutique en mansiones
                  restauradas, caminable, ideal por su ambiente y vida nocturna.
                </li>
                <li>
                  <strong>Marbella y Obarrio:</strong> modernos, céntricos, cerca
                  de restaurantes y del área bancaria.
                </li>
                <li>
                  <strong>Punta Pacífica y Avenida Balboa:</strong> hoteles de
                  altura con vistas al mar y paseos junto al agua.
                </li>
              </ul>

              <h2 id="s5">
                <span className="num">Sección 05</span>Qué hacer
              </h2>

              <p>
                Recorre las cuatro plazas de Casco Viejo y entra a la Iglesia de
                San José a ver su altar de oro; mira un barco subir por las
                Esclusas de Miraflores; pasea o pedalea por la Cinta Costera al
                atardecer; y cierra la noche en una azotea sobre el casco antiguo.
              </p>

              {/* BENTO EN COLUMNA */}
              <div className="prose-bento">
                <div className="pb-tile pb-img pb-tall">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(18118137)}')` }}
                  />
                  <span className="pb-cap">La bahía y la calzada al anochecer</span>
                </div>
                <div className="pb-tile pb-accent">
                  <span className="pb-stat">4</span>
                  <span className="pb-label">plazas históricas para caminar</span>
                </div>
                <div className="pb-tile pb-outline">
                  <h4>Bares en azoteas</h4>
                  <p>Escondidos sobre mansiones del casco, con vistas al horizonte.</p>
                </div>
              </div>

              <h2 id="s6">
                <span className="num">Sección 06</span>Antes de ir
              </h2>

              <p>
                Lo básico que salva un viaje: la ciudad funciona con dólares
                estadounidenses, el transporte por app está en todas partes y el
                calor es real — dosifica tus caminatas y lleva agua. El agua del
                grifo es segura para beber. Dejar propina de alrededor del 10% es
                lo habitual en restaurantes.
              </p>

              {/* PANEL EN COLUMNA */}
              <div className="prose-panel">
                <h4>Esenciales de ciudad</h4>
                <ul>
                  <li>El dólar estadounidense es la moneda — los billetes pequeños ayudan con los taxis.</li>
                  <li>Usa el metro y las apps de transporte para esquivar el tráfico.</li>
                  <li>Mantén tus objetos de valor discretos y quédate en las zonas vigiladas de noche.</li>
                  <li>Empaca capas ligeras — hace calor y humedad todo el año.</li>
                </ul>
              </div>
            </article>

            {/* ===== TARJETAS INFORMATIVAS ===== */}
            <aside className="aside">
              <div className="aside-card">
                <h5>Mejor época · vista de 12 meses</h5>
                {(
                  [
                    ["Ene", "24°/31°", "go"],
                    ["Feb", "24°/32°", "go"],
                    ["Mar", "25°/32°", "go"],
                    ["Abr", "25°/32°", "go"],
                    ["May", "24°/31°", "maybe"],
                    ["Jun", "24°/31°", "maybe"],
                    ["Jul", "24°/31°", "maybe"],
                    ["Ago", "24°/31°", "maybe"],
                    ["Sep", "24°/31°", "skip"],
                    ["Oct", "23°/30°", "skip"],
                    ["Nov", "23°/30°", "skip"],
                    ["Dic", "24°/31°", "go"],
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
                  ● ir &nbsp; ● precaución &nbsp; ● evitar
                </p>
              </div>

              <div className="aside-card">
                <h5>Presupuesto diario típico</h5>
                <div className="stat">$110</div>
                <p>
                  Habitación de gama media, comidas fuera, transporte por app y
                  una atracción de pago. No incluye el vuelo a Tocumen.
                </p>
              </div>

              <div className="aside-card">
                <h5>Verificado localmente por</h5>
                <p style={{ fontSize: 18, lineHeight: 1.3, marginBottom: 12 }}>
                  Carlos Mendoza, guía de ciudad con licencia y residente de toda
                  la vida de la capital
                </p>
                <p style={{ fontSize: 12 }}>Revisado: 18 de mayo de 2026</p>
              </div>
            </aside>
          </div>
        </div>

        {/* ===== GALERÍA ===== */}
        <section className="art-section">
          <div className="container">
            <div className="art-section-head">
              <span className="eyebrow">En imágenes</span>
              <h2>Cómo se ve de verdad</h2>
              <p>Casco antiguo, ciudad nueva y la bahía entre ambos — en cinco fotos.</p>
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

        {/* ===== FRASE DESTACADA ===== */}
        <section className="art-statement">
          <div className="container">
            <div className="art-statement-inner">
              <blockquote>
                La Ciudad de Panamá son dos ciudades que fingen ser una — la
                vieja, que todavía recuerda a los piratas, y la de cristal, que
                los olvidó a propósito.
              </blockquote>
              <cite>— del cuaderno de campo</cite>
            </div>
          </div>
        </section>

        {/* ===== TARJETAS DESTACADAS ===== */}
        <section className="art-section tint">
          <div className="container">
            <div className="art-section-head">
              <span className="eyebrow">En resumen</span>
              <h2>Tres cosas que debes saber</h2>
            </div>
            <div className="art-highlights-grid">
              {HIGHLIGHTS.map((card) => (
                <div key={card.title} className="art-highlight-card">
                  <span className="kicker">Bueno saberlo</span>
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
              <span className="eyebrow">Alrededor de la capital</span>
              <h2>Más de la Ciudad de Panamá</h2>
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
                  <span className="b-tag">Al anochecer</span>
                  <h3>Un horizonte que trasnocha</h3>
                  <p>
                    El área bancaria, las azoteas sobre Casco Viejo y un malecón
                    que se ilumina a lo largo de la Avenida Balboa.
                  </p>
                </div>
              </div>

              <div className="bento-card b2">
                <span className="b-tag">Desde la capital</span>
                <blockquote>
                  Todos dicen que vienen por el canal. Se quedan por el casco
                  antiguo, el ceviche y las azoteas.
                </blockquote>
                <cite>— Iván Bethancourt · Casco Viejo</cite>
              </div>

              <div className="bento-card b3">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(33803478)}')` }}
                />
                <div className="bento-overlay">
                  <span className="b-tag">Vida nocturna</span>
                  <h3>Azoteas y bares</h3>
                </div>
              </div>

              <div className="bento-card b4">
                <span className="b-tag">Planifica</span>
                <h3>Arma un itinerario de 3 días por la Ciudad de Panamá.</h3>
                <span className="bento-arrow">Próximamente</span>
              </div>

              <div className="bento-card b5">
                <div className="bento-split-img">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(20323097)}')` }}
                  />
                </div>
                <div className="bento-split-body">
                  <span className="b-tag">El Canal</span>
                  <h3>Esclusas de Miraflores</h3>
                  <p>
                    Mira los buques portacontenedores subir y bajar por las
                    esclusas desde los miradores, a poco trayecto del centro.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ===== PREGUNTAS FRECUENTES ===== */}
        <section className="art-section tint">
          <div className="container">
            <div className="art-section-head">
              <span className="eyebrow">Preguntas</span>
              <h2>Antes de reservar</h2>
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
