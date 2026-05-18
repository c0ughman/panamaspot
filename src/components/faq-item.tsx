"use client";

import { useState } from "react";

export function FaqItem({
  q,
  a,
  defaultOpen = false,
}: {
  q: string;
  a: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className={`faq-item ${open ? "open" : ""}`}>
      <button
        type="button"
        className="faq-q"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        {q}
      </button>
      <div className="faq-a">{a}</div>
    </div>
  );
}
