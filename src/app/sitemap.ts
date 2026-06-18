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

    // ── Boquete deep-dive articles (EN ↔ ES pairs) ───────────────────────────
    {
      url: `${siteConfig.url}/articles/hikes-in-boquete`,
      lastModified: new Date("2026-06-01"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/hikes-in-boquete`,
          es: `${siteConfig.url}/es/articles/senderos-en-boquete-guia-completa`,
          "x-default": `${siteConfig.url}/articles/hikes-in-boquete`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/senderos-en-boquete-guia-completa`,
      lastModified: new Date("2026-06-01"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/hikes-in-boquete`,
          es: `${siteConfig.url}/es/articles/senderos-en-boquete-guia-completa`,
          "x-default": `${siteConfig.url}/articles/hikes-in-boquete`,
        },
      },
    },
    {
      url: `${siteConfig.url}/articles/things-to-do-in-boquete-panama`,
      lastModified: new Date("2026-06-01"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/things-to-do-in-boquete-panama`,
          es: `${siteConfig.url}/es/articles/que-hacer-en-boquete-guia-completa`,
          "x-default": `${siteConfig.url}/articles/things-to-do-in-boquete-panama`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/que-hacer-en-boquete-guia-completa`,
      lastModified: new Date("2026-06-01"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/things-to-do-in-boquete-panama`,
          es: `${siteConfig.url}/es/articles/que-hacer-en-boquete-guia-completa`,
          "x-default": `${siteConfig.url}/articles/things-to-do-in-boquete-panama`,
        },
      },
    },
    {
      url: `${siteConfig.url}/articles/tours-in-boquete-panama`,
      lastModified: new Date("2026-06-01"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/tours-in-boquete-panama`,
          es: `${siteConfig.url}/es/articles/tours-en-boquete-panama`,
          "x-default": `${siteConfig.url}/articles/tours-in-boquete-panama`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/tours-en-boquete-panama`,
      lastModified: new Date("2026-06-01"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/tours-in-boquete-panama`,
          es: `${siteConfig.url}/es/articles/tours-en-boquete-panama`,
          "x-default": `${siteConfig.url}/articles/tours-in-boquete-panama`,
        },
      },
    },

    // ── El Valle deep-dive articles (EN ↔ ES pairs) ──────────────────────────
    {
      url: `${siteConfig.url}/articles/hikes-el-valle-de-anton`,
      lastModified: new Date("2026-06-02"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/hikes-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/senderos-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/hikes-el-valle-de-anton`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/senderos-el-valle-de-anton`,
      lastModified: new Date("2026-06-02"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/hikes-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/senderos-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/hikes-el-valle-de-anton`,
        },
      },
    },
    {
      url: `${siteConfig.url}/articles/things-to-do-el-valle-de-anton`,
      lastModified: new Date("2026-06-02"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/things-to-do-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/que-hacer-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/things-to-do-el-valle-de-anton`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/que-hacer-el-valle-de-anton`,
      lastModified: new Date("2026-06-02"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/things-to-do-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/que-hacer-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/things-to-do-el-valle-de-anton`,
        },
      },
    },
    {
      url: `${siteConfig.url}/articles/tours-en-el-valle-de-anton`,
      lastModified: new Date("2026-06-02"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/tours-en-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/tours-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/tours-en-el-valle-de-anton`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/tours-el-valle-de-anton`,
      lastModified: new Date("2026-06-02"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/tours-en-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/tours-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/tours-en-el-valle-de-anton`,
        },
      },
    },
  ];
}
