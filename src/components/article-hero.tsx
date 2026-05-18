"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { HomeHeader } from "@/components/home-header";

export function ArticleHero({
  bgImage,
  children,
}: {
  bgImage: string;
  children?: ReactNode;
}) {
  const sectionRef = useRef<HTMLElement>(null);
  const imgRef = useRef<HTMLDivElement>(null);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    // Measure hero height once after mount; re-measure on resize
    let heroHeight = sectionRef.current?.offsetHeight ?? 0;

    const onResize = () => {
      heroHeight = sectionRef.current?.offsetHeight ?? 0;
    };

    const onScroll = () => {
      // Switch to white bar at midpoint through the hero
      setScrolled(window.scrollY >= heroHeight / 2);

      // Parallax: translate image downward at 40% of scroll speed
      if (imgRef.current) {
        imgRef.current.style.transform = `translateY(${window.scrollY * 0.4}px)`;
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
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
        <HomeHeader />
      </div>
      {children}
    </section>
  );
}
