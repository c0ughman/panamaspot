import type { Metadata } from "next";
import { siteConfig } from "./site-config";

type BuildMetadataInput = {
  title: string;
  description: string;
  path?: string;
  ogImage?: string;
  noindex?: boolean;
  absoluteTitle?: boolean;
  type?: "website" | "article";
  publishedTime?: string;
  modifiedTime?: string;
  authors?: string[];
  ogLocale?: string;
  /* hreflang alternates, e.g. { "en": "/", "es": "/es" } — values are paths. */
  languages?: Record<string, string>;
};

export function buildMetadata({
  title,
  description,
  path = "/",
  ogImage,
  noindex = false,
  absoluteTitle = false,
  type = "website",
  publishedTime,
  modifiedTime,
  authors,
  ogLocale,
  languages,
}: BuildMetadataInput): Metadata {
  const url = `${siteConfig.url}${path.startsWith("/") ? path : `/${path}`}`;
  const image = ogImage || siteConfig.defaultOgImage;
  const abs = (p: string) => `${siteConfig.url}${p.startsWith("/") ? p : `/${p}`}`;

  return {
    title: absoluteTitle ? { absolute: title } : title,
    description,
    alternates: {
      canonical: url,
      ...(languages
        ? {
            languages: Object.fromEntries(
              Object.entries(languages).map(([lang, p]) => [lang, abs(p)]),
            ),
          }
        : {}),
    },
    robots: noindex
      ? { index: false, follow: false }
      : { index: true, follow: true },
    openGraph: {
      type,
      url,
      title,
      description,
      siteName: siteConfig.name,
      locale: ogLocale || siteConfig.locale,
      images: [{ url: image }],
      ...(type === "article" && publishedTime ? { publishedTime } : {}),
      ...(type === "article" && modifiedTime ? { modifiedTime } : {}),
      ...(type === "article" && authors ? { authors } : {}),
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [image],
      site: siteConfig.twitterHandle,
    },
  };
}
