import Link from "next/link";

export function HomeHeader() {
  return (
    <header className="home-header">
      <div className="home-header-inner container">
        <Link href="/" className="home-brand">
          <span className="brand-mark" />
          Panama<span style={{ color: "var(--terra)" }}>spot</span>
        </Link>
        <nav className="home-nav">
          <Link href="#cat-regions">Destinations</Link>
          <Link href="#cat-activities">Eco-tourism</Link>
          <Link href="/articles/sendero-los-quetzales">Guides</Link>
          <Link href="#cta">Plan a trip</Link>
        </nav>
        <div className="home-header-right">
          <div className="home-search" role="search">
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
            <span className="home-search-label">Search guides</span>
            <kbd>⌘K</kbd>
          </div>
          <Link href="#" className="home-lang">EN / ES</Link>
        </div>
      </div>
    </header>
  );
}
