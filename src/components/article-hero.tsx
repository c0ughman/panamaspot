"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { HomeHeader, type Locale } from "@/components/home-header";

export function ArticleHero({
  bgImage,
  children,
  locale = "en",
  enHref: enHrefProp,
  esHref: esHrefProp,
}: {
  bgImage: string;
  children?: ReactNode;
  locale?: Locale;
  /* Explicit language-switch targets. Pass the counterpart article URL when a
     translation exists; otherwise the toggle falls back to the other locale's
     home page. */
  enHref?: string;
  esHref?: string;
}) {
  const enHref = enHrefProp ?? (locale === "es" ? "/" : undefined);
  const esHref = esHrefProp ?? (locale === "en" ? "/es" : undefined);
  const sectionRef = useRef<HTMLElement>(null);
  const imgRef = useRef<HTMLDivElement>(null);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      // Measure the hero live so timing/layout never leaves us with a stale
      // (or zero) height. Switch to the white bar past the hero's midpoint.
      const heroHeight =
        sectionRef.current?.offsetHeight ?? window.innerHeight * 0.4;
      setScrolled(window.scrollY >= heroHeight * 0.5);

      // Parallax: translate image downward at 40% of scroll speed
      if (imgRef.current) {
        imgRef.current.style.transform = `translateY(${window.scrollY * 0.4}px)`;
      }
    };

    onScroll(); // set the correct state on mount
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <section ref={sectionRef} className="art-hero-section">
      <div
        ref={imgRef}
        className="art-hero-img-full"
        style={{ backgroundImage: `url('${bgImage}')` }}
      />
      <div className={`art-header-bar${scrolled ? " scrolled" : ""}`}>
        <HomeHeader locale={locale} enHref={enHref} esHref={esHref} />
      </div>
      {children}
    </section>
  );
}
