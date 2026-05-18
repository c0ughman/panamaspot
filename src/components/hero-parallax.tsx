"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { HomeHeader } from "@/components/home-header";

export function HeroParallax({ bgImage }: { bgImage: string }) {
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
      <div
        ref={headerRef}
        className={`header-wrapper ${hasBackground ? "has-background" : ""}`}
      >
        <HomeHeader />
      </div>
      <div className="home-hero-content container">
        <h1 className="home-hero-title">
          Panam<em>á</em>
          <span className="hero-accent">.</span>
        </h1>
        <p className="home-hero-sub">
          The complete guide to traveling in Panama — nine provinces, three
          coasts, written by people who live here.
        </p>
        <Link href="#cat-regions" className="home-hero-btn">
          Start exploring →
        </Link>
      </div>
    </section>
  );
}
