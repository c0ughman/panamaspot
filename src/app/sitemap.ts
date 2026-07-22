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
    images: [hero],
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
    ),
    guide(
      "es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama",
      "https://images.pexels.com/photos/16146741/pexels-photo-16146741.jpeg?auto=compress&cs=tinysrgb&w=1280",
    ),
  ];
}
