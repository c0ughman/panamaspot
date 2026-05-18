"use client";

import { useEffect, useState } from "react";

type TocItem = { id: string; n: string; label: string };

export function ArticleToc({ items }: { items: TocItem[] }) {
  const [active, setActive] = useState(items[0]?.id ?? null);

  useEffect(() => {
    const onScroll = () => {
      let cur: string | null = null;
      for (const item of items) {
        const el = document.getElementById(item.id);
        if (!el) continue;
        const top = el.getBoundingClientRect().top;
        if (top < 200) cur = item.id;
      }
      if (cur) setActive(cur);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [items]);

  const onClick = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    const target = document.getElementById(id);
    if (!target) return;
    const y = target.getBoundingClientRect().top + window.pageYOffset - 80;
    window.scrollTo({ top: y, behavior: "smooth" });
  };

  return (
    <aside className="toc">
      <h5>In this guide</h5>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <a
              href={`#${item.id}`}
              className={active === item.id ? "active" : ""}
              onClick={(e) => onClick(e, item.id)}
            >
              <span className="n">{item.n}</span>
              <span>{item.label}</span>
            </a>
          </li>
        ))}
      </ul>
      <div className="toc-share">
        <button type="button">↗ &nbsp;Share guide</button>
        <button type="button">⬇ &nbsp;Save offline</button>
        <button type="button">🖶 &nbsp;Print version</button>
      </div>
    </aside>
  );
}
