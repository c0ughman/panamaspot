import type { MetadataRoute } from "next";
import { siteConfig } from "@/lib/site-config";

export const dynamic = "force-static";

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
    {
      url: `${siteConfig.url}/articles/panama-city`,
      lastModified: new Date("2026-05-26"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/panama-city`,
          es: `${siteConfig.url}/es/articles/panama-city`,
        },
      },
    },
    {
      url: `${siteConfig.url}/articles/el-valle-de-anton`,
      lastModified: new Date("2026-05-26"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/el-valle-de-anton`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/panama-city`,
      lastModified: new Date("2026-05-26"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/panama-city`,
          es: `${siteConfig.url}/es/articles/panama-city`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/el-valle-de-anton`,
      lastModified: new Date("2026-05-26"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/el-valle-de-anton`,
        },
      },
    },
  ];
}
