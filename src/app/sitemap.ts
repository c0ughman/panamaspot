import type { MetadataRoute } from "next";
import { siteConfig } from "@/lib/site-config";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  return [
    {
      url: siteConfig.url,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${siteConfig.url}/articles/sendero-los-quetzales`,
      lastModified: new Date("2026-05-03"),
      changeFrequency: "monthly",
      priority: 0.8,
    },
  ];
}
