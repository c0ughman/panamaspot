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
  logo: "/logo.png",
  // No social accounts exist yet. Only add a handle or profile here once it is real and owned by Panamá Spot.
  twitterHandle: undefined as string | undefined,
  // Public profiles for Organization `sameAs`. Add real URLs as they go live.
  sameAs: [] as string[],
} as const;

export type SiteConfig = typeof siteConfig;
