/* ============================================================================
   El Valle de Antón — guía de destino (tema VERDE) · versión en español
   Traducción de articles/el-valle-de-anton. Misma estructura, estilos e
   imágenes; solo cambia el texto (español) y locale="es" (/es/articles/…).
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

const SLUG = "el-valle-de-anton";
const HERO_IMAGE = pexels(30774416, 2000);

const ARTICLE = {
  slug: SLUG,
  locale: "es" as "en" | "es",
  seoTitle: "Guía de El Valle de Antón: Senderos, Aguas Termales y Mercados",
  title: "El Valle de Antón — un pueblo verde que vive dentro de un volcán extinto.",
  description:
    "Una guía completa de El Valle de Antón, el pueblo dentro de un cráter volcánico: cómo llegar, cuándo ir, dónde hospedarte y qué hacer — desde La India Dormida hasta el mercado dominical.",
  section: "Destinos",
  publishedAt: "2026-05-26",
  modifiedAt: "2026-05-26",
  author: "Mariela Ortiz-Saavedra",
  breadcrumb: ["Coclé", "Pueblos de montaña", "El Valle de Antón"],
  heroTags: ["Montañas", "Excursión de un día", "Actualizado · Mayo 2026"],
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
  { src: pexels(14714541), caption: "El fondo del valle desde el borde del cráter", feature: true },
  { src: pexels(30774409), caption: "El filo de la cresta de La India Dormida" },
  { src: pexels(7823008), caption: "Primera luz sobre las colinas verdes" },
  { src: pexels(4956963), caption: "Nubes atrapadas en los picos" },
  { src: pexels(30774398), caption: "Mañanas lentas en los cafés del pueblo" },
] as const;

const HIGHLIGHTS = [
  { stat: "1", title: "Un pueblo en un cráter", body: "El Valle se asienta en el fondo de un volcán extinto — uno de los pocos cráteres volcánicos habitados del mundo, rodeado de paredes verdes por todos lados." },
  { stat: "2.5 h", title: "Desde la capital", body: "Un bus directo desde la terminal de Albrook en Ciudad de Panamá, o un trayecto fácil saliendo de la Interamericana — lo bastante cerca para una excursión larga de un día." },
  { stat: "$3", title: "Barato de explorar", body: "La mayoría de los atractivos principales —la caminata a La India Dormida y las aguas termales— cuestan unos tres dólares la entrada." },
] as const;

const FAQ_ITEMS = [
  {
    question: "¿Excursión de un día o pasar la noche?",
    answer:
      "Ambas funcionan. El Valle se puede hacer como una excursión larga de un día desde Ciudad de Panamá —dos horas y media por trayecto— pero una noche te permite alcanzar el mercado dominical temprano y caminar antes del calor del mediodía sin apuros.",
  },
  {
    question: "¿Es difícil la caminata a La India Dormida?",
    answer:
      "Es corta —unos 3 km ida y vuelta, cerca de dos horas— pero empinada por tramos. El sendero de $3 te premia con petroglifos antiguos, pequeñas cascadas y vistas desde la cresta sobre todo el cráter. Usa buen calzado y lleva agua.",
  },
  {
    question: "¿Cuándo es el mercado?",
    answer:
      "El mercado de artesanías y productos de El Valle abre a diario, pero es más grande y animado las mañanas de domingo, de 7 a 14 — vendedores indígenas ofrecen orquídeas, canastas, cerámica, molas y fruta fresca.",
  },
  {
    question: "¿De verdad uno puede meterse a las aguas termales?",
    answer:
      "Sí. Los pozos termales son piscinas de agua mineral tibia (unos $3, con mascarilla de barro para hacértela tú mismo). Son más tibias que calientes —el volcán está extinto hace mucho— pero el barro mineral es lo que vale la pena.",
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

      {/* data-theme="green" → acento y pop verdes, fondo crema. */}
      <main className="article-page" data-theme="green">
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
                  El Valle de Antón — un pueblo verde que vive dentro de un{" "}
                  <em>volcán extinto.</em>
                </h1>
                <p className="art-dek">
                  A dos horas de Ciudad de Panamá, el mayor cráter volcánico
                  habitado del mundo esconde cascadas, aguas termales, un mercado
                  dominical y el aire fresco que la capital quisiera tener.
                </p>

                <div className="art-byline">
                  <div className="byline-photo">M</div>
                  <div className="byline-meta">
                    <div className="name">{ARTICLE.author}</div>
                    <div className="role">
                      Reportera de campo · Coclé · 14 años sobre el terreno
                    </div>
                  </div>
                  <div className="byline-stats">
                    <span>
                      <strong>8 min</strong> de lectura
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
                  <span className="v">Coclé</span>
                </div>
                <div className="fact-row">
                  <span className="k">Entorno</span>
                  <span className="v">Cráter volcánico</span>
                </div>
                <div className="fact-row">
                  <span className="k">Altitud</span>
                  <span className="v">~600 m</span>
                </div>
                <div className="fact-row">
                  <span className="k">Cómo llegar</span>
                  <span className="v">2.5 h desde la ciudad</span>
                </div>
                <div className="fact-row">
                  <span className="k">Hospedaje</span>
                  <span className="v">1–2 noches</span>
                </div>
                <div className="fact-row">
                  <span className="k">Idioma</span>
                  <span className="v">ES / EN</span>
                </div>
                <div className="fact-rating">
                  <span className="lbl">Costo</span>
                  <Bar on={2} />
                  <span className="lbl">Multitudes</span>
                  <Bar on={3} />
                  <span className="lbl">Naturaleza</span>
                  <Bar on={5} />
                  <span className="lbl">Para familias</span>
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
                La carretera sube desde el calor de la costa, toma una curva larga
                y te deja en el fondo de un volcán. Las paredes se levantan verdes
                por todos lados; el aire baja diez grados; y un pueblito de
                jardines y mercados dominicales sigue con su semana.
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
                El Valle es la escapada de montaña más fácil desde Ciudad de
                Panamá — uno de los pocos pueblos del mundo construidos dentro de
                un cráter volcánico. Es fresco, verde y caminable, con una
                caminata por la cresta, pozos de agua mineral tibia, un famoso
                mercado de artesanías y hasta una ranita dorada que no verás en
                ningún otro lugar de la Tierra.
              </p>

              <div className="callout">
                <span className="label">Nota de campo · Hazlo coincidir con el domingo</span>
                El mercado de artesanías es más grande y mejor el domingo por la
                mañana. Llega el sábado por la noche y podrás recorrer el mercado
                temprano, y luego caminar antes de que el sol del mediodía
                encuentre el fondo del cráter.
              </div>

              <figure className="fig">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(30774401)}')` }}
                />
                <figcaption>
                  <span>
                    <strong>La carretera de entrada.</strong> La subida
                    serpenteante desde la Interamericana te deja directo en el
                    fondo del cráter.
                  </span>
                </figcaption>
              </figure>

              <h2 id="s2">
                <span className="num">Sección 02</span>Cómo llegar
              </h2>

              <p>
                Es un trayecto fácil desde la capital. Hay buses directos que
                salen de la terminal de Albrook, en Ciudad de Panamá, hacia el
                centro del pueblo, o puedes manejar la Interamericana hacia el
                oeste y girar tierra adentro pasando San Carlos para la subida
                panorámica hasta el cráter.
              </p>

              <table className="compare">
                <thead>
                  <tr>
                    <th>Ruta de entrada</th>
                    <th>Desde</th>
                    <th>Costo</th>
                    <th>Tiempo</th>
                    <th>Comodidad</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Bus directo</td>
                    <td>Terminal de Albrook</td>
                    <td>$4.25</td>
                    <td>~2.5 h</td>
                    <td>
                      <span className="pill good">Lo más barato</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Manejar</td>
                    <td>Ciudad de Panamá</td>
                    <td>$25–$40 gasolina</td>
                    <td>~2 h</td>
                    <td>
                      <span className="pill good">Flexible</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Tour de un día</td>
                    <td>Ciudad de Panamá</td>
                    <td>$90–$140</td>
                    <td>Día completo</td>
                    <td>
                      <span className="pill mid">Guiado</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Traslado privado</td>
                    <td>Ciudad de Panamá</td>
                    <td>$120+ dividido</td>
                    <td>~2 h</td>
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
                La estación seca —de mediados de diciembre a abril— es la ventana
                confiable para caminatas despejadas por la cresta. Los fines de
                semana se llenan de gente de la ciudad que sube por el aire, los
                baños de barro y el mercado; ve entre semana para tranquilidad, o
                el domingo para el mercado en pleno apogeo.
              </p>

              <h2 id="s4">
                <span className="num">Sección 04</span>Dónde hospedarse
              </h2>

              <p>
                Elige tu base según el ánimo. Quédate en el pueblo para caminar al
                mercado y a los cafés; sube al borde del cráter por las vistas, el
                canto de los pájaros y un poco más de calma.
              </p>

              <ul>
                <li>
                  <strong>En el pueblo:</strong> hostales y hoteles pequeños,
                  caminables al mercado y a los restaurantes.
                </li>
                <li>
                  <strong>En el borde:</strong> cabañas con jardín y eco-lodges
                  con vistas sobre el fondo del cráter.
                </li>
                <li>
                  <strong>En las afueras:</strong> algunos retiros de bienestar
                  construidos en torno al clima fresco y a las aguas termales.
                </li>
              </ul>

              <h2 id="s5">
                <span className="num">Sección 05</span>Qué hacer
              </h2>

              <p>
                Camina el filo de La India Dormida pasando petroglifos y cascadas;
                relájate y date una mascarilla de barro en los pozos termales;
                recorre el mercado dominical de artesanías; y conoce a la ranita
                dorada panameña, en peligro de extinción, en el centro de
                conservación El Níspero.
              </p>

              {/* BENTO EN COLUMNA */}
              <div className="prose-bento">
                <div className="pb-tile pb-img pb-tall">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(18117801)}')` }}
                  />
                  <span className="pb-cap">El sendero de la cresta de La India Dormida</span>
                </div>
                <div className="pb-tile pb-accent">
                  <span className="pb-stat">~3 km</span>
                  <span className="pb-label">hasta las vistas del borde del cráter</span>
                </div>
                <div className="pb-tile pb-outline">
                  <h4>Pozos termales</h4>
                  <p>Piscinas de agua mineral tibia y una mascarilla de barro casera.</p>
                </div>
              </div>

              <h2 id="s6">
                <span className="num">Sección 06</span>Antes de ir
              </h2>

              <p>
                Lo básico: hace bastante más fresco que en la costa, así que lleva
                una capa ligera; carga billetes pequeños para las entradas de $3 y
                el mercado; y usa calzado de verdad para los senderos. El agua del
                grifo es segura, y el domingo es el día clave para planificar.
              </p>

              {/* PANEL EN COLUMNA */}
              <div className="prose-panel">
                <h4>Lista para el día en el cráter</h4>
                <ul>
                  <li>Una capa ligera — el fondo del cráter es más fresco que la costa.</li>
                  <li>Billetes pequeños para las entradas de $3 al sendero y a los pozos termales.</li>
                  <li>Calzado adecuado para el sendero empinado y a veces embarrado de La India Dormida.</li>
                  <li>Salir temprano el domingo para ver el mercado en su mejor momento.</li>
                </ul>
              </div>
            </article>

            {/* ===== TARJETAS INFORMATIVAS ===== */}
            <aside className="aside">
              <div className="aside-card">
                <h5>Mejor época · vista de 12 meses</h5>
                {(
                  [
                    ["Ene", "17°/27°", "go"],
                    ["Feb", "17°/28°", "go"],
                    ["Mar", "18°/29°", "go"],
                    ["Abr", "18°/29°", "go"],
                    ["May", "18°/27°", "maybe"],
                    ["Jun", "18°/26°", "maybe"],
                    ["Jul", "18°/26°", "maybe"],
                    ["Ago", "18°/26°", "maybe"],
                    ["Sep", "17°/26°", "skip"],
                    ["Oct", "17°/25°", "skip"],
                    ["Nov", "17°/26°", "skip"],
                    ["Dic", "17°/27°", "go"],
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
                <div className="stat">$70</div>
                <p>
                  Habitación de hostal, comidas locales, entradas al sendero y a
                  los pozos termales. No incluye el bus o auto desde Ciudad de
                  Panamá.
                </p>
              </div>

              <div className="aside-card">
                <h5>Verificado localmente por</h5>
                <p style={{ fontSize: 18, lineHeight: 1.3, marginBottom: 12 }}>
                  Lía Smith, guía naturalista y residente de muchos años de El
                  Valle
                </p>
                <p style={{ fontSize: 12 }}>Revisado: 12 de mayo de 2026</p>
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
              <p>Las paredes del cráter, el sendero de la cresta y el pueblo abajo — en cinco fotos.</p>
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
                La capital sube los domingos por el mercado, los baños de barro y
                el aire. Luego baja de nuevo — y el valle exhala.
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
              <span className="eyebrow">Alrededor del valle</span>
              <h2>Más de El Valle</h2>
            </div>
            <div className="home-bento-grid">
              <div className="bento-card b1">
                <div className="bento-img-top">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(16053611)}')` }}
                  />
                </div>
                <div className="bento-body">
                  <span className="b-tag">Aire libre</span>
                  <h3>Senderos hacia el borde del cráter</h3>
                  <p>
                    La India Dormida es la caminata estrella, pero las paredes
                    verdes alrededor esconden cascadas y senderos más tranquilos
                    también.
                  </p>
                </div>
              </div>

              <div className="bento-card b2">
                <span className="b-tag">Desde el valle</span>
                <blockquote>
                  La gente sube por el día y empieza a preguntar cuánto costaría
                  una casita en el fondo del cráter. Es esa clase de lugar.
                </blockquote>
                <cite>— Lía Smith · El Valle</cite>
              </div>

              <div className="bento-card b3">
                <div
                  className="imgph photo"
                  style={{ backgroundImage: `url('${pexels(9566563)}')` }}
                />
                <div className="bento-overlay">
                  <span className="b-tag">Fauna</span>
                  <h3>La ranita dorada</h3>
                </div>
              </div>

              <div className="bento-card b4">
                <span className="b-tag">Planifica</span>
                <h3>Planifica una excursión de un día desde Ciudad de Panamá.</h3>
                <span className="bento-arrow">Próximamente</span>
              </div>

              <div className="bento-card b5">
                <div className="bento-split-img">
                  <div
                    className="imgph photo"
                    style={{ backgroundImage: `url('${pexels(18343797)}')` }}
                  />
                </div>
                <div className="bento-split-body">
                  <span className="b-tag">Dónde hospedarse</span>
                  <h3>Cabañas y eco-lodges</h3>
                  <p>
                    Cabañas con jardín en el fondo del cráter y lodges en el borde
                    cambian el calor de la ciudad por noches frescas y tranquilas.
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
