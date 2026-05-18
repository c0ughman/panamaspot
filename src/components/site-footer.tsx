import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="home-cta-inner-merged">
          <h2>
            Every corner of the <em>isthmus</em>, written by people who live
            here.
          </h2>
          <Link href="#cat-regions" className="home-cta-btn">
            Start exploring →
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
            <p className="footer-tag">
              Independent travel journalism, written and edited by people who
              live in Panama. Eight provinces, three indigenous comarcas, one
              obsession.
            </p>
          </div>
          <div>
            <h4>Destinations</h4>
            <ul>
              <li><Link href="/#">Panama City</Link></li>
              <li><Link href="/#">Bocas del Toro</Link></li>
              <li><Link href="/#">San Blas / Guna Yala</Link></li>
              <li><Link href="/#">Boquete &amp; Chiriquí</Link></li>
              <li><Link href="/#">Azuero Peninsula</Link></li>
              <li><Link href="/#">Coiba &amp; the Pacific</Link></li>
              <li><Link href="/#">The Darién</Link></li>
            </ul>
          </div>
          <div>
            <h4>By topic</h4>
            <ul>
              <li><Link href="/#eco">Eco-tourism</Link></li>
              <li><Link href="/#itineraries">Itineraries</Link></li>
              <li><Link href="/#">Wildlife &amp; birding</Link></li>
              <li><Link href="/#">Food &amp; coffee</Link></li>
              <li><Link href="/#">Surf &amp; dive</Link></li>
              <li><Link href="/#">Practical info</Link></li>
            </ul>
          </div>
          <div>
            <h4>About</h4>
            <ul>
              <li><Link href="/#">Our writers</Link></li>
              <li><Link href="/#">Editorial standards</Link></li>
              <li><Link href="/#">Work with us</Link></li>
              <li><Link href="/#">Press &amp; partners</Link></li>
              <li><Link href="/#">Contact</Link></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© 2026 Panamaspot · Panamá City, RP</span>
          <span>Hecho en el istmo · Made on the isthmus</span>
        </div>
      </div>
    </footer>
  );
}
