"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { HomeHeader, type Locale } from "@/components/home-header";

export function HeroParallax({
  bgImage,
  locale = "en",
  subtitle = "The complete guide to traveling in Panama — nine provinces, three coasts, written by people who live here.",
  ctaLabel = "Start exploring →",
  ctaHref = "#cat-regions",
}: {
  bgImage: string;
  locale?: Locale;
  subtitle?: string;
  ctaLabel?: string;
  ctaHref?: string;
}) {
  const sectionRef = useRef<HTMLElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const [hasBackground, setHasBackground] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (!sectionRef.current) return;

      const scrollTop = window.scrollY;
      const offset = scrollTop * 0.4;

      sectionRef.current.style.backgroundPosition = `center ${offset}px`;

      const threshold = window.innerHeight * 0.1;
      setHasBackground(scrollTop > threshold);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <section
      ref={sectionRef}
      className="home-hero"
      style={{
        backgroundImage: `url('${bgImage}')`,
      }}
    >
      {/* Hidden img so the browser preloader discovers and prioritises the hero LCP image */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={bgImage} alt="" aria-hidden="true" fetchPriority="high"
        style={{ position: "absolute", width: 1, height: 1, opacity: 0, pointerEvents: "none" }} />
      <div
        ref={headerRef}
        className={`header-wrapper ${hasBackground ? "has-background" : ""}`}
      >
        <HomeHeader locale={locale} />
      </div>
      <div className="home-hero-content container">
        <h1 className="home-hero-title">
          Panam<em>á</em>
          <span className="hero-accent">.</span>
        </h1>
        <p className="home-hero-sub">{subtitle}</p>
        <Link href={ctaHref} className="home-hero-btn">
          {ctaLabel}
        </Link>
      </div>
    </section>
  );
}
