/* PanamaSpot — GA4 interaction tracking.

   Loaded with `defer` on every page by scripts/build-static.mjs, alongside
   the inline gtag bootstrap that same script injects into <head>.

   Two events, both deliberately custom-named so they read clearly in GA4:

     funnel_click    — someone clicked an in-article CTA through to a funnel
     whatsapp_click  — someone clicked a wa.me link, on a funnel or an article

   Page identity (type, language, slug, destination) is baked into
   window.__PS_PAGE__ at build time rather than parsed from the URL here, so
   the two places that need it cannot drift apart.

   Note on the funnels: they carry their own delegated wa.me listener for the
   Google Ads conversion, which calls preventDefault() and holds navigation.
   This listener does NOT interfere — preventDefault stops the navigation,
   not the dispatch, so both handlers run on the same click. gtag sends via
   sendBeacon, which survives the navigation that follows. */
(function () {
  "use strict";

  var page = window.__PS_PAGE__ || { type: "other", lang: "en", slug: null, dest: null };

  function send(name, params) {
    if (typeof window.gtag !== "function") return; // analytics disabled or blocked
    params.content_lang = page.lang;
    params.page_type = page.type;
    // gtag serialises null as an empty string, which GA4 stores as a real
    // (blank) dimension value — a stray empty row in every breakdown. Drop
    // the key instead so the parameter is simply absent.
    for (var k in params) {
      if (params[k] === null || params[k] === undefined || params[k] === "") delete params[k];
    }
    window.gtag("event", name, params);
  }

  /* Which CTA block the link sits in. Order matters: `.evb-closer` and the
     rail/offer/banner blocks are all nested inside or beside `.evb-cta`, so
     the specific containers have to be tested before the generic one. */
  function placementOf(el) {
    if (el.closest(".evb-rail")) return "rail";
    if (el.closest(".evb-closer")) return "closer";
    if (el.closest(".evb-offer")) return "offer";
    if (el.closest(".evb-banner")) return "banner";
    if (el.closest(".evb-cta")) return "cta";
    return "inline"; // a plain prose link inside the article body
  }

  /* evalley_boquete_es -> boquete. Keeps Spanish and English funnels for the
     same destination groupable, while funnel_slug stays exact. */
  function destinationOf(slug) {
    if (!slug) return "unknown";
    if (slug.indexOf("boquete") !== -1) return "boquete";
    if (slug.indexOf("elvalle") !== -1) return "elvalle";
    return "other";
  }

  function funnelSlugFromHref(href) {
    var m = href.match(/\/funnels\/([^/?#]+?)(?:\.html)?(?:[?#]|$)/);
    return m ? m[1] : null;
  }

  document.addEventListener(
    "click",
    function (e) {
      var target = e.target;
      if (!target || !target.closest) return;

      var link = target.closest("a[href]");
      if (!link) return;

      var href = link.getAttribute("href") || "";

      // ── Article CTA → funnel ────────────────────────────────────────────
      if (href.indexOf("/funnels/") === 0) {
        var slug = funnelSlugFromHref(href);
        send("funnel_click", {
          funnel_slug: slug,
          funnel_dest: destinationOf(slug),
          placement: placementOf(link),
          article_slug: page.slug,
        });
        return;
      }

      // ── Anything → WhatsApp ─────────────────────────────────────────────
      if (href.indexOf("https://wa.me/") === 0) {
        send("whatsapp_click", {
          source_page: page.type, // funnel | article | home | other
          funnel_slug: page.type === "funnel" ? page.slug : null,
          funnel_dest: page.dest || destinationOf(page.slug),
          article_slug: page.type === "article" ? page.slug : null,
          // The CTA blocks only exist on articles; on a funnel this would
          // always fall through to a meaningless "inline".
          placement: page.type === "article" ? placementOf(link) : null,
          // Funnels carry ~10 WhatsApp buttons each and no markup to tell
          // them apart. The button's own label is the one stable handle we
          // have for which of them people actually press.
          link_text: (link.textContent || "").trim().slice(0, 80) || null,
        });
      }
    },
    false
  );
})();
