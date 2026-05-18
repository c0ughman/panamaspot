export const siteConfig = {
  name: "PanamaSpot",
  shortName: "PanamaSpot",
  description:
    "The definitive guide to Panama tourism — destinations, neighborhoods, activities, and travel guides written to be the best answer on the web.",
  url:
    process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, "") ||
    "https://panamaspot.com",
  locale: "en_US",
  defaultOgImage: "/og-default.jpg",
  twitterHandle: "@panamaspot",
} as const;

export type SiteConfig = typeof siteConfig;
