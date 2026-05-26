"use client";

import { useEffect } from "react";

/* Sets <html lang> for the current page. The root layout renders lang="en"
   statically (English is the default tree); Spanish pages render this with
   lang="es" so the document language is correct. hreflang + og:locale in the
   <head> carry the same signal for crawlers that read the raw HTML. */
export function HtmlLang({ lang }: { lang: string }) {
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);
  return null;
}
