import { siteConfig } from "./site-config";

const langTag = (locale?: string) => (locale === "es" ? "es-PA" : "en-US");
const abs = (p: string) =>
  p.startsWith("http") ? p : `${siteConfig.url}${p.startsWith("/") ? p : `/${p}`}`;

const ORG_ID = `${siteConfig.url}/#organization`;
const SITE_ID = `${siteConfig.url}/#website`;

export function organizationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": ORG_ID,
    name: siteConfig.name,
    url: siteConfig.url,
    logo: {
      "@type": "ImageObject",
      url: abs(siteConfig.logo),
      width: 512,
      height: 512,
    },
    ...(siteConfig.sameAs?.length ? { sameAs: siteConfig.sameAs } : {}),
  };
}

export function websiteJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": SITE_ID,
    name: siteConfig.name,
    url: siteConfig.url,
    publisher: { "@id": ORG_ID },
  };
}

type WebPageInput = {
  path: string;
  name: string;
  description: string;
  locale?: string;
  primaryImage?: string;
};

export function webPageJsonLd({
  path,
  name,
  description,
  locale,
  primaryImage,
}: WebPageInput) {
  const url = abs(path);
  return {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": `${url}#webpage`,
    url,
    name,
    description,
    inLanguage: langTag(locale),
    isPartOf: { "@id": SITE_ID },
    ...(primaryImage
      ? {
          primaryImageOfPage: {
            "@type": "ImageObject",
            url: abs(primaryImage),
          },
        }
      : {}),
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
      item: abs(item.path),
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
  locale?: string;
  section?: string;
};

export function articleJsonLd({
  headline,
  description,
  path,
  image,
  datePublished,
  dateModified,
  authorName = siteConfig.name,
  locale,
  section,
}: ArticleJsonLdInput) {
  const url = abs(path);
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    "@id": `${url}#article`,
    headline,
    description,
    image: image ? [abs(image)] : undefined,
    datePublished,
    dateModified: dateModified || datePublished,
    inLanguage: langTag(locale),
    isAccessibleForFree: true,
    ...(section ? { articleSection: section } : {}),
    author: { "@type": "Person", name: authorName },
    publisher: { "@id": ORG_ID },
    mainEntityOfPage: { "@type": "WebPage", "@id": `${url}#webpage` },
  };
}

type FaqItem = { question: string; answer: string };

export function faqPageJsonLd(items: FaqItem[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map(({ question, answer }) => ({
      "@type": "Question",
      name: question,
      acceptedAnswer: {
        "@type": "Answer",
        text: answer,
      },
    })),
  };
}

export function jsonLdScript(data: object) {
  return {
    __html: JSON.stringify(data).replace(/</g, "\\u003c"),
  };
}
