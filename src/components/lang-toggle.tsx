"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

/* EN / ES switcher in the header.
   English lives at the root (/, /articles/…); Spanish under /es.

   By default the switch is structural — it maps the current path to its
   counterpart by adding/removing the /es prefix (so / ⇄ /es). Pages whose
   counterpart isn't a simple prefix swap (e.g. articles, which are written
   separately per language, not translated) pass explicit `enHref`/`esHref`
   so the toggle points somewhere real instead of a 404.

   prefetch is disabled: these are rare clicks and we don't want Next
   prefetching a counterpart URL that may not exist. */
export function LangToggle({
  enHref,
  esHref,
}: {
  enHref?: string;
  esHref?: string;
}) {
  const pathname = usePathname() || "/";
  const isES = pathname === "/es" || pathname.startsWith("/es/");

  const normalized = pathname.replace(/^\/es(?=\/|$)/, "") || "/";
  const en = enHref ?? normalized;
  const es = esHref ?? (normalized === "/" ? "/es" : `/es${normalized}`);

  return (
    <div className="home-lang home-lang--toggle">
      <Link
        href={en}
        prefetch={false}
        className={`lang-opt${isES ? "" : " active"}`}
        aria-current={isES ? undefined : "true"}
        hrefLang="en"
      >
        EN
      </Link>
      <span className="lang-sep" aria-hidden="true">
        /
      </span>
      <Link
        href={es}
        prefetch={false}
        className={`lang-opt${isES ? " active" : ""}`}
        aria-current={isES ? "true" : undefined}
        hrefLang="es"
      >
        ES
      </Link>
    </div>
  );
}
