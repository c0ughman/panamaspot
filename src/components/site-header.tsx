import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="topbar">
      <div className="container topbar-inner">
        <Link href="/" className="brand">
          <span className="brand-mark" />
          Panama<span style={{ color: "var(--terra)" }}>spot</span>
        </Link>
        <nav className="nav">
          <Link href="/#destinations">Destinations</Link>
          <Link href="/#eco">Eco-tourism</Link>
          <Link href="/#itineraries">Itineraries</Link>
          <Link href="/articles/sendero-los-quetzales">Guides</Link>
          <Link href="/#">Plan a trip</Link>
        </nav>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <div className="search-pill">
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
            <span>Search 240+ guides</span>
            <kbd>⌘K</kbd>
          </div>
          <Link href="/#" className="nav-cta">
            EN / ES
          </Link>
        </div>
      </div>
    </header>
  );
}
