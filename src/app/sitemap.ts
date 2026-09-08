import type { MetadataRoute } from "next";
import { siteConfig } from "@/lib/site-config";
import { pageImages } from "./page-images";

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
    images: pageImages[`/${path}`] ?? [hero],
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
  const sepGuide = (
    path: string,
    hero: string,
    pair?: { en: string; es: string },
  ): MetadataRoute.Sitemap[number] => ({
    ...guide(path, hero, pair),
    lastModified: sepLastMod,
  });

  // Destination hubs — curated indexes of a whole cluster. Higher priority than
  // an individual guide because they are the entry point Google should prefer.
  const hubsLastMod = new Date("2026-08-31");
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
    images: pageImages[`/${path}`] ?? [hero],
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
    {
      url: `${siteConfig.url}/articles/bocas-del-toro`,
      lastModified: new Date("2026-05-26"),
      changeFrequency: "monthly",
      priority: 0.8,
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
    },
    {
      url: `${siteConfig.url}/articles/lost-waterfalls-boquete-hiking-guide`,
      lastModified: new Date("2026-06-24"),
      changeFrequency: "monthly",
      priority: 0.8,
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
      { en: "articles/el-valle-de-anton-with-kids", es: "es/articles/zoologico-el-nispero-el-valle-de-anton" },
    ),
    guide(
      "es/articles/zoologico-el-nispero-el-valle-de-anton",
      "https://images.pexels.com/photos/12861718/pexels-photo-12861718.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/el-valle-de-anton-with-kids", es: "es/articles/zoologico-el-nispero-el-valle-de-anton" },
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
    ),
    guide(
      "articles/day-trips-from-panama-city",
      "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    guide(
      "articles/el-valle-de-anton-waterfalls",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/ChorroMachoElValle.jpg/1280px-ChorroMachoElValle.jpg",
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
      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Gnathanodon_speciosus.jpg/1280px-Gnathanodon_speciosus.jpg",
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
      "https://images.pexels.com/photos/30271300/pexels-photo-30271300.jpeg?auto=compress&cs=tinysrgb&w=1280",
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
    ),
    sepGuide(
      "es/articles/bus-albrook-el-valle-de-anton-horarios-precios",
      "https://images.pexels.com/photos/30774387/pexels-photo-30774387.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/chorro-las-mozas-pozas-el-valle-de-anton",
      "https://images.pexels.com/photos/17231782/pexels-photo-17231782.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/cuanto-cuesta-boquete-presupuesto-semana",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/donde-comer-en-el-valle-de-anton",
      "https://images.pexels.com/photos/33703911/pexels-photo-33703911.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/donde-dormir-el-valle-de-anton",
      "https://images.pexels.com/photos/30774387/pexels-photo-30774387.jpeg?auto=compress&cs=tinysrgb&w=1280",
      { en: "articles/where-to-stay-in-el-valle-de-anton", es: "es/articles/donde-dormir-el-valle-de-anton" },
    ),
    sepGuide(
      "es/articles/el-volcan-baru-esta-activo",
      "https://images.pexels.com/photos/37245225/pexels-photo-37245225.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/feria-de-las-flores-y-del-cafe-boquete",
      "https://images.pexels.com/photos/29207117/pexels-photo-29207117.jpeg?auto=compress&cs=tinysrgb&w=1280",
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
    ),
    sepGuide(
      "es/articles/precios-horarios-el-valle-de-anton",
      "https://images.pexels.com/photos/30774387/pexels-photo-30774387.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
    sepGuide(
      "es/articles/tours-en-bicicleta-el-valle-de-anton",
      "https://images.pexels.com/photos/30774401/pexels-photo-30774401.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
  ];
}
