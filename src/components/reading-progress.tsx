"use client";

import { useEffect, useRef } from "react";

export function ReadingProgress() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const onScroll = () => {
      const el = ref.current;
      if (!el) return;
      const h = document.documentElement;
      const pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
      el.style.width = `${pct}%`;
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return <div ref={ref} className="read-progress" />;
}
