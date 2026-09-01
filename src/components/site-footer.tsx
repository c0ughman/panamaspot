import Link from "next/link";
import type { ReactNode } from "react";
import type { Locale } from "@/components/home-header";

/* A destination becomes a real link once it has a hub page; everything else
   stays inert text until the content exists. */
type FooterItem = string | readonly [label: string, href: string];

function FooterEntry({ item }: { item: FooterItem }) {
  if (typeof item === "string") {
    return <span className="footer-link-muted">{item}</span>;
  }
  const [label, href] = item;
  return <Link href={href}>{label}</Link>;
}

/* Footer copy, localized. Rendered per-page (not in the root layout) so each
   locale's pages get the matching language — pass locale="es" on /es pages. */
const COPY = {
  en: {
    home: "/",
    cta: (
      <>
        Every corner of the <em>isthmus</em>, written by people who live here.
      </>
    ),
    ctaBtn: "Start exploring →",
    tagline:
      "Independent travel journalism, written and edited by people who live in Panama. Eight provinces, three indigenous comarcas, one obsession.",
    destinations: "Destinations",
    destinationItems: [
      ["El Valle de Antón", "/articles/el-valle-de-anton"],
      ["Panama City", "/articles/panama-city"],
      ["Bocas del Toro", "/articles/bocas-del-toro"],
      "San Blas / Guna Yala",
      ["Boquete & Chiriquí", "/articles/boquete"],
      "Azuero Peninsula",
      "Coiba & the Pacific",
      "The Darién",
    ] as readonly FooterItem[],
    topic: "By topic",
    topicItems: [
      "Eco-tourism",
      "Itineraries",
      "Wildlife & birding",
      "Food & coffee",
      "Surf & dive",
      "Practical info",
    ],
    about: "About",
    aboutItems: [
      "Our writers",
      "Editorial standards",
      "Work with us",
      "Press & partners",
      "Contact",
    ],
    rights: "© 2026 Panamaspot · Panamá City, RP",
  },
  es: {
    home: "/es",
    cta: (
      <>
        Cada rincón del <em>istmo</em>, escrito por quienes vivimos aquí.
      </>
    ),
    ctaBtn: "Empieza a explorar →",
    tagline:
      "Periodismo de viajes independiente, escrito y editado por quienes vivimos en Panamá. Ocho provincias, tres comarcas indígenas, una obsesión.",
    destinations: "Destinos",
    destinationItems: [
      ["El Valle de Antón", "/es/articles/el-valle-de-anton"],
      ["Ciudad de Panamá", "/es/articles/panama-city"],
      "Bocas del Toro",
      ["San Blas / Guna Yala", "/es/articles/san-blas-guna-yala-guia-tours-islas"],
      ["Boquete y Chiriquí", "/es/articles/boquete"],
      "Península de Azuero",
      ["Coiba y el Pacífico", "/es/articles/isla-coiba-buceo-parque-nacional"],
      "El Darién",
    ] as readonly FooterItem[],
    topic: "Por tema",
    topicItems: [
      "Ecoturismo",
      "Itinerarios",
      "Fauna y aves",
      "Comida y café",
      "Surf y buceo",
      "Información práctica",
    ],
    about: "Nosotros",
    aboutItems: [
      "Nuestros autores",
      "Estándares editoriales",
      "Trabaja con nosotros",
      "Prensa y socios",
      "Contacto",
    ],
    rights: "© 2026 Panamaspot · Ciudad de Panamá, RP",
  },
} as const;

export function SiteFooter({ locale = "en" }: { locale?: Locale }) {
  const t = COPY[locale];
  return (
    <footer className="footer">
      <div className="container">
        <div className="home-cta-inner-merged">
          <h2>{t.cta}</h2>
          <Link href={`${t.home}#cat-regions`} className="home-cta-btn">
            {t.ctaBtn}
          </Link>
        </div>
        <div className="footer-cta-rule" />
      </div>

      <div className="container">
        <div className="footer-inner">
          <div>
            <div className="footer-brand">
              Panama<span style={{ color: "var(--terra)" }}>spot</span>
            </div>
            <p className="footer-tag">{t.tagline}</p>
          </div>
          <div>
            <h4>{t.destinations}</h4>
            <ul>
              {t.destinationItems.map((item) => (
                <li key={typeof item === "string" ? item : item[0]}>
                  <FooterEntry item={item} />
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4>{t.topic}</h4>
            <ul>
              {t.topicItems.map((item) => (
                <li key={item}>
                  <FooterEntry item={item} />
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4>{t.about}</h4>
            <ul>
              {t.aboutItems.map((item) => (
                <li key={item}>
                  <FooterEntry item={item} />
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <span>{t.rights}</span>
          <span>Hecho en el istmo · Made on the isthmus</span>
        </div>
      </div>
    </footer>
  );
}
