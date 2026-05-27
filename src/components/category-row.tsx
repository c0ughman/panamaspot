"use client";

import { useRef, type ReactNode } from "react";

export function CategoryRow({ children }: { children: ReactNode }) {
  const rowRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: -1 | 1) => {
    const row = rowRef.current;
    if (!row) return;

    const firstCard = row.querySelector<HTMLElement>(".cat-card");
    const gap = 14;
    const step = firstCard ? firstCard.offsetWidth + gap : row.clientWidth;

    row.scrollBy({ left: direction * step, behavior: "smooth" });
  };

  return (
    <div className="cat-row-wrap">
      <button
        type="button"
        className="cat-arrow prev"
        aria-label="Previous"
        onClick={() => scroll(-1)}
      >
        ‹
      </button>
      <div className="cat-row" ref={rowRef}>
        {children}
      </div>
      <button
        type="button"
        className="cat-arrow next"
        aria-label="Next"
        onClick={() => scroll(1)}
      >
        ›
      </button>
    </div>
  );
}
