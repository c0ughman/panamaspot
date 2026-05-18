import type { Metadata } from "next";
import { siteConfig } from "./site-config";

type BuildMetadataInput = {
  title: string;
  description: string;
  path?: string;
  ogImage?: string;
  noindex?: boolean;
  type?: "website" | "article";
  publishedTime?: string;
  modifiedTime?: string;
  authors?: string[];
};

export function buildMetadata({
  title,
  description,
  path = "/",
  ogImage,
  noindex = false,
  type = "website",
  publishedTime,
  modifiedTime,
  authors,
}: BuildMetadataInput): Metadata {
  const url = `${siteConfig.url}${path.startsWith("/") ? path : `/${path}`}`;
  const image = ogImage || siteConfig.defaultOgImage;

  return {
    title,
    description,
    alternates: { canonical: url },
    robots: noindex
      ? { index: false, follow: false }
      : { index: true, follow: true },
    openGraph: {
      type,
      url,
      title,
      description,
      siteName: siteConfig.name,
      locale: siteConfig.locale,
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
