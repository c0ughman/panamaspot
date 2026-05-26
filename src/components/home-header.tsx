import Link from "next/link";
import { LangToggle } from "@/components/lang-toggle";

export type Locale = "en" | "es";

/* Header nav, localized per language. English points at the root tree,
   Spanish at the /es tree. Add new nav items in both maps. */
const NAV: Record<Locale, { label: string; href: string }[]> = {
  en: [
    { label: "Destinations", href: "/#cat-regions" },
    { label: "Eco-tourism", href: "/#cat-activities" },
    { label: "Guides", href: "/articles/sendero-los-quetzales" },
    { label: "Plan a trip", href: "/#cat-destinations" },
  ],
  es: [
    { label: "Destinos", href: "/es#cat-regions" },
    { label: "Ecoturismo", href: "/es#cat-activities" },
    { label: "Guías", href: "/es#cat-destinations" },
    { label: "Planifica tu viaje", href: "/es#cat-destinations" },
  ],
};

const SEARCH_LABEL: Record<Locale, string> = {
  en: "Search guides",
  es: "Buscar guías",
};

export function HomeHeader({
  locale = "en",
  enHref,
  esHref,
}: {
  locale?: Locale;
  /* Optional explicit language-switch targets (for pages without a simple
     prefix counterpart, e.g. articles). Defaults to prefix mapping. */
  enHref?: string;
  esHref?: string;
}) {
  const home = locale === "es" ? "/es" : "/";
  return (
    <header className="home-header">
      <div className="home-header-inner container">
        <Link href={home} className="home-brand">
          <span className="brand-mark" />
          Panama<span style={{ color: "var(--terra)" }}>spot</span>
        </Link>
        <nav className="home-nav">
          {NAV[locale].map((item) => (
            <Link key={item.label} href={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="home-header-right">
          <div className="home-search" role="search" aria-hidden="true">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <circle cx="11" cy="11" r="7" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <span className="home-search-label">{SEARCH_LABEL[locale]}</span>
            <kbd>⌘K</kbd>
          </div>
          <LangToggle enHref={enHref} esHref={esHref} />
        </div>
      </div>
    </header>
  );
}
