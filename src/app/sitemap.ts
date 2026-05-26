import type { MetadataRoute } from "next";
import { siteConfig } from "@/lib/site-config";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  // The two homepages are language equivalents → declare them as hreflang
  // alternates of each other so Google serves the right one per market.
  const homeAlternates = {
    languages: {
      en: siteConfig.url,
      es: `${siteConfig.url}/es`,
      "x-default": siteConfig.url,
    },
  };
  return [
    {
      url: siteConfig.url,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 1,
      alternates: homeAlternates,
    },
    {
      url: `${siteConfig.url}/es`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 1,
      alternates: homeAlternates,
    },
    {
      url: `${siteConfig.url}/articles/sendero-los-quetzales`,
      lastModified: new Date("2026-05-26"),
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${siteConfig.url}/articles/bocas-del-toro`,
      lastModified: new Date("2026-05-26"),
      changeFrequency: "monthly",
      priority: 0.8,
    },
  ];
}
