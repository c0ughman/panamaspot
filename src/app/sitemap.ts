import type { MetadataRoute } from "next";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { siteConfig } from "@/lib/site-config";
import { pageImages } from "./page-images";

export const dynamic = "force-static";

/**
 * XML-escape a URL before it goes into the sitemap.
 *
 * Next interpolates these values raw — in
 * next/dist/.../metadata/resolve-route-data.js the line is literally
 * `<image:loc>${image}</image:loc>` with no escaping anywhere in the file — so
 * any `&` in a URL produces malformed XML. Our Pexels heroes carry
 * `?auto=compress&cs=tinysrgb&w=…`, which put 212 bare ampersands in the
 * sitemap and made Search Console reject the whole file ("unable to read your
 * Sitemap … Line 54"). An XML parser stops at the first one.
 *
 * Escaping here rather than in page-images.ts keeps that file clean data; this
 * is the only place it is rendered as XML.
 */
const xmlSafe = (u: string) =>
  u
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");

const safeImages = (urls: readonly string[] | undefined) =>
  urls?.map(xmlSafe);

/**
 * lastmod = the page's own article:modified_time (2026-11 SEO pass).
 *
 * The dates below were typed by hand per batch and drifted: 72 guides told Google they were older
 * than the date on the page itself, and the homepages used the build time, so every deploy claimed
 * a change. Google stops trusting lastmod that is wrong that often. Each guide's date now comes from
 * its own <meta property="article:modified_time">; pages without one (hubs, homepages) keep the
 * date set here. Bump HOME_UPDATED / hubsLastMod only when their content really changes.
 */
const HOME_UPDATED = new Date("2026-11-08");
const TRUST_UPDATED = new Date("2026-11-08"); // bump when About/Contact/Privacy really change
function pageModified(url: string): Date | undefined {
  const path = url.slice(siteConfig.url.length).replace(/^\//, "");
  if (!path) return undefined;
  try {
    const html = readFileSync(join(process.cwd(), "public", `${path}.html`), "utf8");
    const m =
      html.match(/<meta[^>]*property="article:modified_time"[^>]*content="([^"]+)"/) ??
      html.match(/<meta[^>]*content="([^"]+)"[^>]*property="article:modified_time"/);
    const d = m ? new Date(m[1]) : undefined;
    return d && !Number.isNaN(d.getTime()) ? d : undefined;
  } catch {
    return undefined;
  }
}

export default function sitemap(): MetadataRoute.Sitemap {
  return entries().map((e) => ({ ...e, lastModified: pageModified(e.url) ?? e.lastModified }));
}

function entries(): MetadataRoute.Sitemap {
  const now = HOME_UPDATED;
  // The two homepages are language equivalents → declare them as hreflang
  // alternates of each other so Google serves the right one per market.
  const homeAlternates = {
    languages: {
      en: siteConfig.url,
      es: `${siteConfig.url}/es`,
      "x-default": siteConfig.url,
    },
  };

  // The 2026-07 batch of guide pages (image + SEO refresh). `hero` is the
  // width-capped LCP image, surfaced as an <image:image> entry for image SEO.
  // `pair` sets reciprocal hreflang alternates for the true EN↔ES translations;
  // single-language guides list only themselves (self + x-default).
  const guidesLastMod = new Date("2026-07-20");
  const guide = (
    path: string,
    hero: string,
    pair?: { en: string; es: string },
  ): MetadataRoute.Sitemap[number] => ({
    url: `${siteConfig.url}/${path}`,
    lastModified: guidesLastMod,
    changeFrequency: "monthly",
    priority: 0.8,
    // hero first, then the rest of the page's images (Google Images
    // indexes what the sitemap declares, and these pages carry 7-12 each)
    images: safeImages(pageImages[`/${path}`]) ?? [xmlSafe(hero)],
    ...(pair
      ? {
          alternates: {
            languages: {
              en: `${siteConfig.url}/${pair.en}`,
              es: `${siteConfig.url}/${pair.es}`,
              "x-default": `${siteConfig.url}/${pair.en}`,
            },
          },
        }
      : {}),
  });

  // The 2026-09 batch of 36 generated guides. Same shape as `guide`, its own
  // lastModified so the older batch is not falsely re-dated.
  const sepLastMod = new Date("2026-09-04");
  // The twelve Boquete guides were reworked on 2026-09-10 — new photography,
  // captions, alt text, credits blocks and interlinking. Dating them 09-04
  // alongside the untouched half of the batch understates the change and gives
  // crawlers no reason to come back for it.
  const boqueteLastMod = new Date("2026-09-10");
  const REWORKED = new Set([
    "articles/best-time-to-visit-boquete",
    "articles/boquete-bike-rental",
    "articles/boquete-cycling-routes",
    "articles/boquete-hot-springs-caldera-vs-los-pozos",
    "articles/panama-city-to-boquete",
    "articles/quetzal-season-boquete-when-where-to-see-resplendent-quetzal",
    "articles/where-to-stay-in-boquete",
    "es/articles/boquete-con-ninos-guia-familiar",
    "es/articles/cuanto-cuesta-boquete-presupuesto-semana",
    "es/articles/el-volcan-baru-esta-activo",
    "es/articles/feria-de-las-flores-y-del-cafe-boquete",
    "es/articles/mi-jardin-es-su-jardin-boquete",
  ]);
  const sepGuide = (
    path: string,
    hero: string,
    pair?: { en: string; es: string },
  ): MetadataRoute.Sitemap[number] => ({
    ...guide(path, hero, pair),
    lastModified: REWORKED.has(path) ? boqueteLastMod : sepLastMod,
  });

  // Destination hubs — curated indexes of a whole cluster. Higher priority than
  // an individual guide because they are the entry point Google should prefer.
  const hubsLastMod = new Date("2026-11-07"); // rebuilt with new content at the 2026-11-07 launch
  const hub = (
    en: string,
    es: string,
    hero: string,
  ): MetadataRoute.Sitemap[number][] =>
    [en, es].map((path) => ({
      url: `${siteConfig.url}/${path}`,
      lastModified: hubsLastMod,
      changeFrequency: "weekly" as const,
      priority: 0.9,
      // hero first, then the rest of the page's images (Google Images
    // indexes what the sitemap declares, and these pages carry 7-12 each)
    images: safeImages(pageImages[`/${path}`]) ?? [xmlSafe(hero)],
      alternates: {
        languages: {
          en: `${siteConfig.url}/${en}`,
          es: `${siteConfig.url}/${es}`,
          "x-default": `${siteConfig.url}/${en}`,
        },
      },
    }));

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
    // Trust pages (live 2026-11-08): About, Contact, Privacy, each an EN/ES hreflang pair.
    ...([
      ["about", "es/sobre-nosotros"],
      ["contact", "es/contacto"],
      ["privacy", "es/privacidad"],
    ] as const).flatMap(([en, es]) => {
      const alternates = {
        languages: {
          en: `${siteConfig.url}/${en}`,
          es: `${siteConfig.url}/${es}`,
          "x-default": `${siteConfig.url}/${en}`,
        },
      };
      return [en, es].map((path) => ({
        url: `${siteConfig.url}/${path}`,
        lastModified: TRUST_UPDATED,
        changeFrequency: "yearly" as const,
        priority: 0.4,
        alternates,
      }));
    }),
    {
      // Bocas is a destination hub like the other three, but English-only for
      // now (the Spanish cluster is a single article), so it cannot use hub()
      // — that helper emits an EN/ES pair.
      url: `${siteConfig.url}/articles/bocas-del-toro`,
      lastModified: hubsLastMod,
      changeFrequency: "weekly",
      priority: 0.9,
      images: safeImages(pageImages["/articles/bocas-del-toro"]),
    },
    {
      // San Blas hub (2026-11-07): English-only like Bocas, indexes the three San Blas guides.
      url: `${siteConfig.url}/articles/san-blas`,
      lastModified: new Date("2026-11-07"),
      changeFrequency: "weekly",
      priority: 0.9,
      images: safeImages(pageImages["/articles/san-blas"]),
    },
    // ── Destination hubs ────────────────────────────────────────────────────
    ...hub(
      "articles/panama-city",
      "es/articles/panama-city",
      "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=2400",
    ),
    ...hub(
      "articles/el-valle-de-anton",
      "es/articles/el-valle-de-anton",
      `${siteConfig.url}/images/el-valle/elvalle-crater-hero.webp`,
    ),
    ...hub(
      "articles/boquete",
      "es/articles/boquete",
      `${siteConfig.url}/images/boquete/boquete-hills.webp`,
    ),

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

    // ── Caldera Hot Springs (EN ↔ ES pair) ───────────────────────────────────
    {
      url: `${siteConfig.url}/articles/caldera-hot-springs-boquete`,
      lastModified: new Date("2026-06-24"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/caldera-hot-springs-boquete`,
          es: `${siteConfig.url}/es/articles/aguas-termales-caldera-boquete`,
          "x-default": `${siteConfig.url}/articles/caldera-hot-springs-boquete`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/aguas-termales-caldera-boquete`,
      lastModified: new Date("2026-06-24"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/caldera-hot-springs-boquete`,
          es: `${siteConfig.url}/es/articles/aguas-termales-caldera-boquete`,
          "x-default": `${siteConfig.url}/articles/caldera-hot-springs-boquete`,
        },
      },
    },

    // ── Chorro El Macho Waterfall (EN ↔ ES pair) ─────────────────────────────
    {
      url: `${siteConfig.url}/articles/chorro-el-macho-waterfall-el-valle-de-anton`,
      lastModified: new Date("2026-06-21"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/chorro-el-macho-waterfall-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/cascada-chorro-el-macho-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/chorro-el-macho-waterfall-el-valle-de-anton`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/cascada-chorro-el-macho-el-valle-de-anton`,
      lastModified: new Date("2026-06-23"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/chorro-el-macho-waterfall-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/cascada-chorro-el-macho-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/chorro-el-macho-waterfall-el-valle-de-anton`,
        },
      },
    },

    // ── El Valle Day Trip from Panama City (EN ↔ ES pair) ────────────────────
    {
      url: `${siteConfig.url}/articles/el-valle-day-trip-from-panama-city`,
      lastModified: new Date("2026-06-23"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/el-valle-day-trip-from-panama-city`,
          es: `${siteConfig.url}/es/articles/el-valle-de-anton-desde-ciudad-de-panama`,
          "x-default": `${siteConfig.url}/articles/el-valle-day-trip-from-panama-city`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/el-valle-de-anton-desde-ciudad-de-panama`,
      lastModified: new Date("2026-06-24"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/el-valle-day-trip-from-panama-city`,
          es: `${siteConfig.url}/es/articles/el-valle-de-anton-desde-ciudad-de-panama`,
          "x-default": `${siteConfig.url}/articles/el-valle-day-trip-from-panama-city`,
        },
      },
    },

    // ── India Dormida Hike (EN ↔ ES pair) ────────────────────────────────────
    {
      url: `${siteConfig.url}/articles/india-dormida-hike-el-valle-de-anton`,
      lastModified: new Date("2026-06-19"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/india-dormida-hike-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/sendero-india-dormida-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/india-dormida-hike-el-valle-de-anton`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/sendero-india-dormida-el-valle-de-anton`,
      lastModified: new Date("2026-06-20"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/india-dormida-hike-el-valle-de-anton`,
          es: `${siteConfig.url}/es/articles/sendero-india-dormida-el-valle-de-anton`,
          "x-default": `${siteConfig.url}/articles/india-dormida-hike-el-valle-de-anton`,
        },
      },
    },

    // ── Single-language guides (no translation pair) ─────────────────────────
    {
      url: `${siteConfig.url}/articles/boquete-coffee-farm-tour`,
      lastModified: new Date("2026-06-24"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/boquete-coffee-farm-tour`,
          es: `${siteConfig.url}/es/articles/tour-de-cafe-boquete-fincas-precios-reservar`,
          "x-default": `${siteConfig.url}/articles/boquete-coffee-farm-tour`,
        },
      },
    },
    {
      url: `${siteConfig.url}/articles/lost-waterfalls-boquete-hiking-guide`,
      lastModified: new Date("2026-06-24"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/lost-waterfalls-boquete-hiking-guide`,
          es: `${siteConfig.url}/es/articles/cascadas-perdidas-boquete-ruta-precio`,
          "x-default": `${siteConfig.url}/articles/lost-waterfalls-boquete-hiking-guide`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/alquiler-de-bicicletas-boquete`,
      lastModified: new Date("2026-06-24"),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: {
        languages: {
          en: `${siteConfig.url}/articles/boquete-bike-rental`,
          es: `${siteConfig.url}/es/articles/alquiler-de-bicicletas-boquete`,
          "x-default": `${siteConfig.url}/articles/boquete-bike-rental`,
        },
      },
    },
    {
      url: `${siteConfig.url}/es/articles/como-llegar-a-boquete-sin-carro`,
      lastModified: new Date("2026-06-24"),
      changeFrequency: "monthly",
      priority: 0.8,
    },

    // ── Overhauled guide pages (2026-07 image + SEO refresh) ─────────────────
    guide(
      "articles/volcan-baru-hike-sunrise-summit-guide",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Volcan_Baru_up_close_and_clouded.jpg/1280px-Volcan_Baru_up_close_and_clouded.jpg",
      { en: "articles/volcan-baru-hike-sunrise-summit-guide", es: "es/articles/volcan-baru-como-subir-cima-panama" },
    ),
    guide(
      "es/articles/volcan-baru-como-subir-cima-panama",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Volcan_Baru_up_close_and_clouded.jpg/1280px-Volcan_Baru_up_close_and_clouded.jpg",
      { en: "articles/volcan-baru-hike-sunrise-summit-guide", es: "es/articles/volcan-baru-como-subir-cima-panama" },
    ),
    guide(
      "articles/boquete-travel-guide",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Aerial_view_of_Boquete%2C_Panama.jpg/1280px-Aerial_view_of_Boquete%2C_Panama.jpg",
      { en: "articles/boquete-travel-guide", es: "es/articles/boquete-panama-guia-completa-itinerario" },
    ),
    guide(
      "es/articles/boquete-panama-guia-completa-itinerario",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Aerial_view_of_Boquete%2C_Panama.jpg/1280px-Aerial_view_of_Boquete%2C_Panama.jpg",
      { en: "articles/boquete-travel-guide", es: "es/articles/boquete-panama-guia-completa-itinerario" },
    ),
    guide(
      "articles/el-valle-de-anton-with-kids",
      "https://images.pexels.com/photos/12861718/pexels-photo-12861718.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/el-valle-de-anton-with-kids", es: "es/articles/el-valle-de-anton-con-ninos-familia" },
    ),
    guide(
      "es/articles/zoologico-el-nispero-el-valle-de-anton",
      "https://images.pexels.com/photos/12861718/pexels-photo-12861718.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "articles/amador-causeway-biomuseo-guide",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Causeway_de_Amador_17-12-14.jpg/1280px-Causeway_de_Amador_17-12-14.jpg",
    ),
    guide(
      "articles/bocas-del-toro-island-hopping-guide",
      "https://images.pexels.com/photos/30826590/pexels-photo-30826590.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "articles/casco-viejo-panama-walking-guide",
      "https://images.pexels.com/photos/18049699/pexels-photo-18049699.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "articles/cerro-gaital-cara-iguana-hike-el-valle",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Anton_Valle_foothills_-_Flickr_-_gailhampshire.jpg/1280px-Anton_Valle_foothills_-_Flickr_-_gailhampshire.jpg",
      { en: "articles/cerro-gaital-cara-iguana-hike-el-valle", es: "es/articles/cerro-gaital-cara-iguana-rutas-dificultad" },
    ),
    guide(
      "articles/day-trips-from-panama-city",
      "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "articles/el-valle-de-anton-waterfalls",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/ChorroMachoElValle.jpg/1280px-ChorroMachoElValle.jpg",
      { en: "articles/el-valle-de-anton-waterfalls", es: "es/articles/cascadas-el-valle-de-anton-como-llegar" },
    ),
    guide(
      "articles/finca-lerida-los-quetzales-trail-birdwatching-boquete",
      "https://images.pexels.com/photos/16017280/pexels-photo-16017280.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "articles/panama-canal-tour-miraflores-locks-visitor-guide",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Panama_Canal_Gatun_Locks.jpg/1280px-Panama_Canal_Gatun_Locks.jpg",
    ),
    guide(
      "articles/panama-city-itinerary-3-days",
      "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "es/articles/aguas-termales-el-valle-de-anton",
      "https://images.pexels.com/photos/920270/pexels-photo-920270.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/el-valle-de-anton-hot-springs-prices-hours-getting-there", es: "es/articles/aguas-termales-el-valle-de-anton" },
    ),
    guide(
      "es/articles/canopy-el-valle-de-anton-cabalgatas-aventura",
      "https://images.pexels.com/photos/28518788/pexels-photo-28518788.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "es/articles/casco-viejo-restaurantes-donde-comer-beber-hospedarse",
      "https://images.pexels.com/photos/18049699/pexels-photo-18049699.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo",
      "https://images.pexels.com/photos/5005136/pexels-photo-5005136.jpeg?auto=compress&cs=tinysrgb&w=1600",
    ),
    guide(
      "es/articles/isla-coiba-buceo-parque-nacional",
      "https://panamaspot.com/images/v2/snowflake-in-panama-2072311431-hero-1920.webp",
      { en: "articles/diving-in-panama", es: "es/articles/isla-coiba-buceo-parque-nacional" },
    ),
    guide(
      "es/articles/que-hacer-en-ciudad-de-panama",
      "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "es/articles/rafting-boquete-rio-chiriqui",
      "https://images.pexels.com/photos/36791113/pexels-photo-36791113.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "es/articles/san-blas-guna-yala-guia-tours-islas",
      "https://panamaspot.com/images/v2/x-diadup-kuna-yala-panam-c3-a1-hero-1920.webp",
      { en: "articles/san-blas-islands-panama-guna-yala-guide", es: "es/articles/san-blas-guna-yala-guia-tours-islas" },
    ),
    guide(
      "es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama",
      "https://images.pexels.com/photos/16146741/pexels-photo-16146741.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/how-to-get-to-bocas-del-toro", es: "es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama" },
    ),

    // ── 2026-09 batch (36 generated guides) ─────────────────────────────────
    sepGuide(
      "articles/best-time-to-visit-boquete",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/best-time-to-visit-panama",
      "https://images.pexels.com/photos/33803480/pexels-photo-33803480.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/boat-charter-panama",
      "https://images.pexels.com/photos/3754442/pexels-photo-3754442.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/boquete-bike-rental",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/boquete-bike-rental", es: "es/articles/alquiler-de-bicicletas-boquete" },
    ),
    sepGuide(
      "articles/boquete-cycling-routes",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/boquete-hot-springs-caldera-vs-los-pozos",
      "https://images.pexels.com/photos/37245214/pexels-photo-37245214.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/cayos-zapatillas-snorkelling-bocas-del-toro",
      "https://images.pexels.com/photos/6149489/pexels-photo-6149489.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/el-valle-de-anton-itinerary-one-day",
      "https://images.pexels.com/photos/30774409/pexels-photo-30774409.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/el-valle-de-anton-itinerary-one-day", es: "es/articles/el-valle-de-anton-en-un-dia-itinerario" },
    ),
    sepGuide(
      "articles/el-valle-de-anton-vs-boquete",
      "https://images.pexels.com/photos/35526169/pexels-photo-35526169.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/how-to-get-to-bocas-del-toro",
      "https://images.pexels.com/photos/16116492/pexels-photo-16116492.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/how-to-get-to-bocas-del-toro", es: "es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama" },
    ),
    sepGuide(
      "articles/is-panama-safe",
      "https://images.pexels.com/photos/33803476/pexels-photo-33803476.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/panama-city-to-boquete",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/pearl-islands-panama-guide",
      "https://images.pexels.com/photos/36601640/pexels-photo-36601640.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/quetzal-season-boquete-when-where-to-see-resplendent-quetzal",
      "https://images.pexels.com/photos/25489548/pexels-photo-25489548.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/red-frog-beach-bocas-del-toro",
      "https://images.pexels.com/photos/12831912/pexels-photo-12831912.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/renting-a-car-in-panama",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/san-blas-islands-panama-guna-yala-guide",
      "https://images.pexels.com/photos/36601640/pexels-photo-36601640.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/san-blas-islands-panama-guna-yala-guide", es: "es/articles/san-blas-guna-yala-guia-tours-islas" },
    ),
    sepGuide(
      "articles/san-blas-sailing-panama-to-colombia",
      "https://images.pexels.com/photos/36117831/pexels-photo-36117831.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/starfish-beach-bocas-del-toro-playa-estrella-guide",
      "https://images.pexels.com/photos/30032075/pexels-photo-30032075.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "articles/where-to-stay-in-boquete",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/where-to-stay-in-boquete", es: "es/articles/donde-dormir-en-boquete-hoteles-cabanas-hospedaje" },
    ),
    sepGuide(
      "articles/where-to-stay-in-el-valle-de-anton",
      "https://images.pexels.com/photos/13058771/pexels-photo-13058771.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/where-to-stay-in-el-valle-de-anton", es: "es/articles/donde-dormir-el-valle-de-anton" },
    ),
    sepGuide(
      "articles/which-bocas-del-toro-island-to-stay-on",
      "https://images.pexels.com/photos/33990238/pexels-photo-33990238.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/boquete-con-ninos-guia-familiar",
      "https://images.pexels.com/photos/35106208/pexels-photo-35106208.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/boquete-with-kids-family-guide", es: "es/articles/boquete-con-ninos-guia-familiar" },
    ),
    sepGuide(
      "es/articles/bus-albrook-el-valle-de-anton-horarios-precios",
      "https://images.pexels.com/photos/30774387/pexels-photo-30774387.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/chorro-las-mozas-pozas-el-valle-de-anton",
      "https://images.pexels.com/photos/17231782/pexels-photo-17231782.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/chorro-las-mozas-swimming-falls-el-valle", es: "es/articles/chorro-las-mozas-pozas-el-valle-de-anton" },
    ),
    sepGuide(
      "es/articles/cuanto-cuesta-boquete-presupuesto-semana",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/donde-comer-en-el-valle-de-anton",
      "https://images.pexels.com/photos/33703911/pexels-photo-33703911.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/where-to-eat-el-valle-de-anton", es: "es/articles/donde-comer-en-el-valle-de-anton" },
    ),
    sepGuide(
      "es/articles/donde-dormir-el-valle-de-anton",
      "https://images.pexels.com/photos/30774387/pexels-photo-30774387.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/where-to-stay-in-el-valle-de-anton", es: "es/articles/donde-dormir-el-valle-de-anton" },
    ),
    sepGuide(
      "es/articles/el-volcan-baru-esta-activo",
      "https://images.pexels.com/photos/37245225/pexels-photo-37245225.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/volcan-baru-national-park-entry-facts-active", es: "es/articles/el-volcan-baru-esta-activo" },
    ),
    sepGuide(
      "es/articles/feria-de-las-flores-y-del-cafe-boquete",
      "https://images.pexels.com/photos/29207117/pexels-photo-29207117.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/boquete-flower-and-coffee-fair-visitor-guide", es: "es/articles/feria-de-las-flores-y-del-cafe-boquete" },
    ),
    sepGuide(
      "es/articles/mariposario-el-valle-de-anton",
      "https://images.pexels.com/photos/7200711/pexels-photo-7200711.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/mercado-el-valle-de-anton",
      "https://images.pexels.com/photos/15101211/pexels-photo-15101211.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/mi-jardin-es-su-jardin-boquete",
      "https://images.pexels.com/photos/18543358/pexels-photo-18543358.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/piedra-pintada-el-valle-de-anton",
      "https://images.pexels.com/photos/39056910/pexels-photo-39056910.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/piedra-pintada-painted-rock-el-valle-de-anton", es: "es/articles/piedra-pintada-el-valle-de-anton" },
    ),
    sepGuide(
      "es/articles/precios-horarios-el-valle-de-anton",
      "https://images.pexels.com/photos/30774387/pexels-photo-30774387.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/tours-en-bicicleta-el-valle-de-anton",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    // ── PS-V2 guides (managed by ps_launch.py) ──
    {
      ...guide(
        "articles/buying-property-in-panama-as-a-foreigner",
        "https://panamaspot.com/images/v2/panama-city-panama-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/panama-residency-visas",
        "https://panamaspot.com/images/v2/the-skyline-of-panama-city-s-17477516-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/retiring-in-panama",
        "https://panamaspot.com/images/v2/boquete-houseclouds-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/stem-cell-therapy-in-panama",
        "https://panamaspot.com/images/v2/te-with-induced-pluripotent-stem-cells-46291373491-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/healthcare-in-panama-for-foreigners",
        "https://panamaspot.com/images/v2/doctor-nurse-patient-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/san-blas-tours-from-panama-city",
        "https://panamaspot.com/images/v2/caba-c3-b1as-guna-yala-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/contadora-ferry-from-panama-city",
        "https://panamaspot.com/images/v2/islaperico-causeway-amador-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/panama-surf-camps",
        "https://panamaspot.com/images/v2/surferriomarbeachpanama-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/diving-in-panama",
        "https://panamaspot.com/images/v2/king-cotton-2058177216-hero-1920.webp",
      { en: "articles/diving-in-panama", es: "es/articles/isla-coiba-buceo-parque-nacional" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/playa-venao-panama",
        "https://panamaspot.com/images/v2/panam-c3-a1-playa-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/panama-all-inclusive-resorts",
        "https://panamaspot.com/images/v2/playa-de-kobbe-la-mochila-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/where-to-stay-in-panama-city",
        "https://panamaspot.com/images/v2/panama-city-panama-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/hoteles-en-casco-viejo",
        "https://panamaspot.com/images/v2/casco-viejo-panama-city-panama-54319827771-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/panama-canal-boat-tours",
        "https://panamaspot.com/images/v2/container-vessel-hs-mozart-gatun-lake-panama-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/sendero-los-quetzales-quetzal-boquete",
        "https://panamaspot.com/images/v2/al-in-los-quetzales-national-park-photo-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/hiking-in-panama-best-trails",
        "https://panamaspot.com/images/v2/rope-bridge-near-cerro-el-macho-waterfall-hero-1920.webp",
      { en: "articles/hiking-in-panama-best-trails", es: "es/articles/senderismo-en-panama-mejores-senderos-ciudad" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/sendero-el-pianista-boquete-ruta-dificultad",
        "https://panamaspot.com/images/v2/c3-ba-and-the-mountain-city-of-hero-1920.webp",
      { en: "articles/el-pianista-trail-boquete", es: "es/articles/sendero-el-pianista-boquete-ruta-dificultad" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/senderismo-en-panama-mejores-senderos-ciudad",
        "https://panamaspot.com/images/v2/toed-sloth-cerro-ancon-panama-city-48454787316-hero-1920.webp",
      { en: "articles/hiking-in-panama-best-trails", es: "es/articles/senderismo-en-panama-mejores-senderos-ciudad" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/el-pianista-trail-boquete",
        "https://panamaspot.com/images/v2/c3-ba-and-the-mountain-city-of-hero-1920.webp",
      { en: "articles/el-pianista-trail-boquete", es: "es/articles/sendero-el-pianista-boquete-ruta-dificultad" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/pipeline-trail-boquete-quetzal-hike",
        "https://panamaspot.com/images/v2/quetzales-trail-baru-volcano-national-park-panama-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/cerro-gaital-cara-iguana-rutas-dificultad",
        "https://panamaspot.com/images/v2/iguana-iguana-hero-1920.webp",
      { en: "articles/cerro-gaital-cara-iguana-hike-el-valle", es: "es/articles/cerro-gaital-cara-iguana-rutas-dificultad" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/cascadas-perdidas-boquete-ruta-precio",
        "https://panamaspot.com/images/v2/wasserfall-bei-boquete-26701686043-hero-1920.webp",
      { en: "articles/lost-waterfalls-boquete-hiking-guide", es: "es/articles/cascadas-perdidas-boquete-ruta-precio" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/cerro-la-silla-sendero-amanecer-el-valle",
        "https://panamaspot.com/images/v2/valle-de-ant-c3-b3n-la-mochila-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/canopy-en-boquete-tree-trek-y-opciones",
        "https://panamaspot.com/images/v2/boquete-zipline-rider-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/birding-el-valle-de-anton-trails-lodges-season",
        "https://panamaspot.com/images/v2/ed-honeycreeper-cyanerpes-cyaneus-carneipes-male-2-hero-1920.webp",
      { en: "articles/birding-el-valle-de-anton-trails-lodges-season", es: "es/articles/avistamiento-de-aves-el-valle-de-anton" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/tour-de-cafe-boquete-fincas-precios-reservar",
        "https://panamaspot.com/images/v2/finca-lerida-boquete-panama-hero-1920.webp",
      { en: "articles/boquete-coffee-farm-tour", es: "es/articles/tour-de-cafe-boquete-fincas-precios-reservar" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/avistamiento-de-aves-el-valle-de-anton",
        "https://panamaspot.com/images/v2/lemon-rumped-tanager-ramphocelus-icteronotus-male-hero-1920.webp",
      { en: "articles/birding-el-valle-de-anton-trails-lodges-season", es: "es/articles/avistamiento-de-aves-el-valle-de-anton" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/geisha-coffee-boquete-where-to-taste",
        "https://panamaspot.com/images/v2/clusters-of-ripe-red-coffee-cherries-14776857-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/el-valle-de-anton-hot-springs-prices-hours-getting-there",
        "https://panamaspot.com/images/v2/steam-rises-over-a-bed-of-920270-hero-1920.webp",
      { en: "articles/el-valle-de-anton-hot-springs-prices-hours-getting-there", es: "es/articles/aguas-termales-el-valle-de-anton" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/boquete-flower-and-coffee-fair-visitor-guide",
        "https://panamaspot.com/images/v2/rvn06957-hero-1920.webp",
      { en: "articles/boquete-flower-and-coffee-fair-visitor-guide", es: "es/articles/feria-de-las-flores-y-del-cafe-boquete" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/boquete-to-bocas-del-toro-shuttle-bus-timing",
        "https://panamaspot.com/images/v2/bocas-del-toro-water-taxis-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/bajo-mono-boquete-circuito-y-senderos",
        "https://panamaspot.com/images/v2/outside-dining-sunset-los-molinos-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/el-valle-de-anton-con-ninos-familia",
        "https://panamaspot.com/images/v2/four-children-stand-on-a-sandy-5036679-hero-1920.webp",
      { en: "articles/el-valle-de-anton-with-kids", es: "es/articles/el-valle-de-anton-con-ninos-familia" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/boquete-with-kids-family-guide",
        "https://panamaspot.com/images/v2/four-children-stand-on-a-sandy-5036679-hero-1920.webp",
      { en: "articles/boquete-with-kids-family-guide", es: "es/articles/boquete-con-ninos-guia-familiar" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/el-valle-de-anton-en-un-dia-itinerario",
        "https://panamaspot.com/images/v2/house-and-landscape-el-valle-02-hero-1920.webp",
      { en: "articles/el-valle-de-anton-itinerary-one-day", es: "es/articles/el-valle-de-anton-en-un-dia-itinerario" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/fin-de-semana-el-valle-de-anton-2-dias",
        "https://panamaspot.com/images/v2/a-two-story-hotel-with-wood-13058771-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/donde-dormir-en-boquete-hoteles-cabanas-hospedaje",
        "https://panamaspot.com/images/v2/boquete-houseclouds-hero-1920.webp",
      { en: "articles/where-to-stay-in-boquete", es: "es/articles/donde-dormir-en-boquete-hoteles-cabanas-hospedaje" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/restaurantes-y-cafeterias-en-boquete",
        "https://panamaspot.com/images/v2/outside-dining-sunset-los-molinos-hero-1920.webp",
      { en: "articles/where-to-eat-in-boquete", es: "es/articles/restaurantes-y-cafeterias-en-boquete" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/where-to-eat-in-boquete",
        "https://panamaspot.com/images/v2/restaurant-dining-sunset-los-molinos-hero-1920.webp",
      { en: "articles/where-to-eat-in-boquete", es: "es/articles/restaurantes-y-cafeterias-en-boquete" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/where-to-eat-el-valle-de-anton",
        "https://panamaspot.com/images/v2/lasnubes-camarones-hero-1920.webp",
      { en: "articles/where-to-eat-el-valle-de-anton", es: "es/articles/donde-comer-en-el-valle-de-anton" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/volcan-baru-national-park-entry-facts-active",
        "https://panamaspot.com/images/v2/volcan-baru-up-close-and-clouded-hero-1920.webp",
      { en: "articles/volcan-baru-national-park-entry-facts-active", es: "es/articles/el-volcan-baru-esta-activo" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/lugares-turisticos-chiriqui",
        "https://panamaspot.com/images/v2/puesta-de-sol-la-mochila-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/best-waterfalls-in-panama-where-to-see-several",
        "https://panamaspot.com/images/v2/chorro-marcho-el-valle-panama-03-hero-1920.webp",
      { en: "articles/best-waterfalls-in-panama-where-to-see-several", es: "es/articles/cascadas-en-panama-mejores-como-llegar" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/miradores-de-boquete-vistas-sin-subir-baru",
        "https://panamaspot.com/images/v2/view-from-restaurant-covered-los-molinos-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/cascadas-en-panama-mejores-como-llegar",
        "https://panamaspot.com/images/v2/chorro-marcho-el-valle-panama-03-hero-1920.webp",
      { en: "articles/best-waterfalls-in-panama-where-to-see-several", es: "es/articles/cascadas-en-panama-mejores-como-llegar" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/cascadas-el-valle-de-anton-como-llegar",
        "https://panamaspot.com/images/v2/el-macho-falls-panoramio-hero-1920.webp",
      { en: "articles/el-valle-de-anton-waterfalls", es: "es/articles/cascadas-el-valle-de-anton-como-llegar" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/lugares-turisticos-de-cocle",
        "https://panamaspot.com/images/v2/an-bautista-por-el-sismo-de-7-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/piedra-pintada-painted-rock-el-valle-de-anton",
        "https://panamaspot.com/images/v2/petroglifoelvalle-hero-1920.webp",
      { en: "articles/piedra-pintada-painted-rock-el-valle-de-anton", es: "es/articles/piedra-pintada-el-valle-de-anton" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "articles/chorro-las-mozas-swimming-falls-el-valle",
        "https://panamaspot.com/images/v2/a-waterfall-falls-into-a-amber-34937418-hero-1920.webp",
      { en: "articles/chorro-las-mozas-swimming-falls-el-valle", es: "es/articles/chorro-las-mozas-pozas-el-valle-de-anton" },
      ),
      lastModified: new Date("2026-11-03"),
    },
    {
      ...guide(
        "es/articles/miradores-el-valle-de-anton",
        "https://panamaspot.com/images/v2/el-valle-1-1066c4-hero-1920.webp",
      ),
      lastModified: new Date("2026-11-03"),
    },
    // ── /PS-V2 guides ──
  ];
}
