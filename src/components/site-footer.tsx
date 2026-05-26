import Link from "next/link";
import type { ReactNode } from "react";

function FooterText({ children }: { children: ReactNode }) {
  return <span className="footer-link-muted">{children}</span>;
}

export function SiteFooter() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="home-cta-inner-merged">
          <h2>
            Every corner of the <em>isthmus</em>, written by people who live
            here.
          </h2>
          <Link href="/#cat-regions" className="home-cta-btn">
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
              <li><FooterText>Panama City</FooterText></li>
              <li><FooterText>Bocas del Toro</FooterText></li>
              <li><FooterText>San Blas / Guna Yala</FooterText></li>
              <li><FooterText>Boquete &amp; Chiriquí</FooterText></li>
              <li><FooterText>Azuero Peninsula</FooterText></li>
              <li><FooterText>Coiba &amp; the Pacific</FooterText></li>
              <li><FooterText>The Darién</FooterText></li>
            </ul>
          </div>
          <div>
            <h4>By topic</h4>
            <ul>
              <li><FooterText>Eco-tourism</FooterText></li>
              <li><FooterText>Itineraries</FooterText></li>
              <li><FooterText>Wildlife &amp; birding</FooterText></li>
              <li><FooterText>Food &amp; coffee</FooterText></li>
              <li><FooterText>Surf &amp; dive</FooterText></li>
              <li><FooterText>Practical info</FooterText></li>
            </ul>
          </div>
          <div>
            <h4>About</h4>
            <ul>
              <li><FooterText>Our writers</FooterText></li>
              <li><FooterText>Editorial standards</FooterText></li>
              <li><FooterText>Work with us</FooterText></li>
              <li><FooterText>Press &amp; partners</FooterText></li>
              <li><FooterText>Contact</FooterText></li>
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
