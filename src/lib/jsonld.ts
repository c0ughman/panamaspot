import { siteConfig } from "./site-config";

export function organizationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: siteConfig.name,
    url: siteConfig.url,
    logo: `${siteConfig.url}/logo.png`,
  };
}

export function websiteJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: siteConfig.name,
    url: siteConfig.url,
    potentialAction: {
      "@type": "SearchAction",
      target: `${siteConfig.url}/search?q={search_term_string}`,
      "query-input": "required name=search_term_string",
    },
  };
}

type BreadcrumbItem = { name: string; path: string };

export function breadcrumbJsonLd(items: BreadcrumbItem[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: `${siteConfig.url}${item.path}`,
    })),
  };
}

type ArticleJsonLdInput = {
  headline: string;
  description: string;
  path: string;
  image?: string;
  datePublished: string;
  dateModified?: string;
  authorName?: string;
};

export function articleJsonLd({
  headline,
  description,
  path,
  image,
  datePublished,
  dateModified,
  authorName = siteConfig.name,
}: ArticleJsonLdInput) {
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline,
    description,
    image: image ? [`${siteConfig.url}${image}`] : undefined,
    datePublished,
    dateModified: dateModified || datePublished,
    author: { "@type": "Organization", name: authorName },
    publisher: {
      "@type": "Organization",
      name: siteConfig.name,
      logo: { "@type": "ImageObject", url: `${siteConfig.url}/logo.png` },
    },
    mainEntityOfPage: { "@type": "WebPage", "@id": `${siteConfig.url}${path}` },
  };
}

export function jsonLdScript(data: object) {
  return {
    __html: JSON.stringify(data).replace(/</g, "\\u003c"),
  };
}
