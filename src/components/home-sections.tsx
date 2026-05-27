import Link from "next/link";
import { CategoryRow } from "@/components/category-row";

/* Shared, locale-agnostic building blocks for the home pages.
   The English home (src/app/page.tsx) and the Spanish home
   (src/app/es/page.tsx) each supply their own localized data and copy;
   these components only handle presentation. */

// ── Pexels photo helper ──────────────────────────────────────────────────────
export const pexels = (id: number, w = 1200) =>
  `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${w}`;

export type Tint = "jungle" | "terra" | "sky" | "sand" | "ink";
export type CardImg = { kind: "photo"; src: string } | { kind: "tint"; cls: Tint };
export type IconKey = "region" | "activity" | "destination";

export type Card = {
  title: string;
  tag: string;
  img: CardImg;
  href?: string;
  /** Grayscale image + non-interactive card (no lift hover). */
  comingSoon?: boolean;
};

export function CategorySection({
  id,
  title,
  link,
  icon,
  cards,
}: {
  id: string;
  title: string;
  link: string;
  icon: IconKey;
  cards: Card[];
}) {
  return (
    <section className="cat-section" id={id}>
      <div className="container">
        <div className="cat-section-head">
          <h2>{title}</h2>
          <span className="cat-section-link cat-section-link--muted">{link}</span>
        </div>

        <CategoryRow>
            {cards.map((card) => (
              <CategoryCard key={card.title} icon={icon} {...card} />
            ))}
        </CategoryRow>
      </div>
    </section>
  );
}

function CategoryCard({
  title,
  tag,
  img,
  href,
  comingSoon,
  icon,
}: Card & { icon: IconKey }) {
  const isSoon = comingSoon ?? !href;
  const content = (
    <>
      {img.kind === "photo" ? (
        <div
          className="imgph photo"
          style={{ backgroundImage: `url('${img.src}')` }}
        />
      ) : (
        <div className={`imgph ${img.cls}`} />
      )}
      <div className="cat-card-body">
        <span className="cat-card-title">{title}</span>
        <span className="cat-card-tag">
          <CardIcon kind={icon} />
          {tag}
        </span>
      </div>
    </>
  );

  if (href && !isSoon) {
    return (
      <Link href={href} className="cat-card">
        {content}
      </Link>
    );
  }

  return (
    <div
      className={`cat-card cat-card--static${isSoon ? " cat-card--soon" : ""}`}
      aria-label={`${title} — ${tag}`}
    >
      {content}
    </div>
  );
}

function CardIcon({ kind }: { kind: IconKey }) {
  switch (kind) {
    case "region":
      return (
        <svg
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.2"
          strokeLinejoin="round"
          aria-hidden="true"
          width="11"
          height="11"
        >
          <path d="M6 1.4 C 3.6 1.4, 2.2 3.2, 2.2 5 C 2.2 7.4, 6 10.6, 6 10.6 C 6 10.6, 9.8 7.4, 9.8 5 C 9.8 3.2, 8.4 1.4, 6 1.4 Z" />
          <circle cx="6" cy="5" r="1.4" />
        </svg>
      );
    case "activity":
      return (
        <svg
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.2"
          strokeLinejoin="round"
          aria-hidden="true"
          width="11"
          height="11"
        >
          <path d="M1.5 9.6 L4.2 4.4 L6.4 6.8 L9 3 L10.5 9.6 Z" />
        </svg>
      );
    case "destination":
      return (
        <svg
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.2"
          aria-hidden="true"
          width="11"
          height="11"
        >
          <circle cx="6" cy="6" r="3.6" />
          <circle cx="6" cy="6" r="1" fill="currentColor" stroke="none" />
        </svg>
      );
  }
}
