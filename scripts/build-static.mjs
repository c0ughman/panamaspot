#!/usr/bin/env node
/* Post-build cleanup for the static export.

   Walks `out/` and rewrites every HTML file:
     1. Removes Next.js runtime: <script src="/_next/...">, inline
        self.__next_f.push(...) chunks, preload/prefetch/modulepreload
        links pointing at /_next assets.
     2. Strips React streaming markers (<!--$-->, <!--/$-->, <!--?-->, etc.).
     3. Fixes <html lang> on /es/ pages (the root layout always emits
        lang="en"; the HtmlLang client component patched it at runtime,
        but the runtime is now gone).
     4. Injects <script src="/app.js" defer></script> for the vanilla-JS
        interactivity bundle.
     5. Injects the GA4 tag + <script src="/analytics.js" defer>, and then
        asserts that every page got it. This is the only place analytics is
        installed — Next-rendered pages, the raw article HTML copied from
        public/, and the funnels all pass through here, so coverage is
        structural rather than something anyone has to remember.

   Run with: node scripts/build-static.mjs
*/

import { readdir, readFile, writeFile, stat, rm, unlink } from "node:fs/promises";
import { readFileSync, existsSync } from "node:fs";
import { join, relative, basename } from "node:path";

const ROOT = new URL("../out/", import.meta.url).pathname;
const APP_JS_TAG = '<script src="/app.js" defer></script>';
const ANALYTICS_JS_TAG = '<script src="/analytics.js" defer></script>';
const GA_MARKER = "PS-ANALYTICS";

/* `next build` loads .env.local itself, but this is a separate node process,
   so it has to do the same. Real environment variables always win — that is
   what Netlify and CI supply. */
function loadDotEnv() {
  for (const file of [".env.local", ".env"]) {
    let raw;
    try {
      raw = readFileSync(new URL(`../${file}`, import.meta.url), "utf8");
    } catch {
      continue;
    }
    for (const line of raw.split("\n")) {
      const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/);
      if (!m) continue;
      const [, key, rawVal] = m;
      if (key in process.env) continue;
      const quoted = /^(["'])(.*)\1$/.exec(rawVal);
      process.env[key] = quoted ? quoted[2] : rawVal.replace(/\s+#.*$/, "");
    }
  }
}

loadDotEnv();

const GA_ID = (process.env.NEXT_PUBLIC_GA_ID || "").trim();

if (GA_ID && !/^G-[A-Z0-9]+$/i.test(GA_ID)) {
  console.error(
    `NEXT_PUBLIC_GA_ID is set to "${GA_ID}", which is not a GA4 measurement ID.\n` +
      `Expected the G-XXXXXXXXXX form (a Google Ads AW- id or a GTM- container id will not work here).`,
  );
  process.exit(1);
}

async function* walkHtml(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) yield* walkHtml(full);
    else if (entry.isFile() && entry.name.endsWith(".html")) yield full;
  }
}

function stripNextRuntime(html) {
  // External script tags pointing at /_next/.
  html = html.replace(
    /<script\b[^>]*\bsrc=["'][^"']*\/_next\/[^"']*["'][^>]*><\/script>/g,
    "",
  );

  // Inline self.__next_f.push(...) chunks (the streamed React payload).
  html = html.replace(
    /<script\b[^>]*>\s*\(?self\.__next_f\s*=[\s\S]*?<\/script>/g,
    "",
  );
  html = html.replace(
    /<script\b[^>]*>\s*self\.__next_f\.push\([\s\S]*?\)<\/script>/g,
    "",
  );

  // preload / prefetch / modulepreload links into /_next.
  html = html.replace(
    /<link\b[^>]*\bhref=["'][^"']*\/_next\/[^"']*["'][^>]*\brel=["'](?:preload|prefetch|modulepreload)["'][^>]*>/g,
    "",
  );
  html = html.replace(
    /<link\b[^>]*\brel=["'](?:preload|prefetch|modulepreload)["'][^>]*\bhref=["'][^"']*\/_next\/[^"']*["'][^>]*>/g,
    "",
  );

  // React streaming / suspense comment markers (<!--$-->, <!--/$-->, <!--?-->, <!--$!-->, etc.).
  html = html.replace(/<!--\$!?-->/g, "");
  html = html.replace(/<!--\/\$-->/g, "");
  html = html.replace(/<!--\?-->/g, "");

  return html;
}

function fixSpanishLang(html, relPath) {
  if (!relPath.startsWith("es/") && relPath !== "es.html") return html;
  return html.replace(/<html([^>]*?)\blang="en"/i, '<html$1lang="es"');
}

/* Body font, self-hosted (2026-11 SEO pass). The Google Fonts stylesheet was render-blocking on
   every guide and hub (~1.1 s on mobile in Lighthouse): the browser had to reach two more hosts
   before it could paint. Hanken Grotesk is a variable font (OFL), so one file per subset covers
   400-700; latin + latin-ext cover English and Spanish. Same family name, so page CSS and the
   hubs' document.fonts.load() calls keep working unchanged. Done here, not in the page sources,
   because several generators write those heads and any of them could bring the link back. */
const GOOGLE_HANKEN =
  '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&display=swap">';
const LOCAL_HANKEN =
  '<link rel="preload" as="font" type="font/woff2" href="/fonts/HankenGrotesk-latin.woff2" crossorigin>' +
  "<style>" +
  "@font-face{font-family:'Hanken Grotesk';font-style:normal;font-weight:400 700;font-display:swap;" +
  "src:url(/fonts/HankenGrotesk-latin-ext.woff2) format('woff2');" +
  "unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}" +
  "@font-face{font-family:'Hanken Grotesk';font-style:normal;font-weight:400 700;font-display:swap;" +
  "src:url(/fonts/HankenGrotesk-latin.woff2) format('woff2');" +
  "unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}" +
  "</style>";
const GOOGLE_PRECONNECTS =
  /<link rel="preconnect" href="https:\/\/fonts\.googleapis\.com"><link rel="preconnect" href="https:\/\/fonts\.gstatic\.com" crossorigin>\n?/;

function selfHostFonts(html) {
  if (!html.includes(GOOGLE_HANKEN)) return html;
  html = html.replace(GOOGLE_HANKEN, LOCAL_HANKEN);
  // The preconnects only served Google Fonts; drop them if nothing else on the page uses Google Fonts.
  if (!html.includes("fonts.googleapis.com/css")) html = html.replace(GOOGLE_PRECONNECTS, "");
  return html;
}

/* Robots meta normalisation (2026-11 SEO pass).
   - Indexable pages also allow large image previews in Search and Discover (Google's default
     without it is a small thumbnail). Half the guides had it, half didn't.
   - The 404 pages got Next's own noindex AND the layout's "index, follow"; keep only the noindex. */
function normaliseRobots(html, relPath) {
  if (relPath === "404.html" || relPath === "_not-found.html") {
    return html.replace(/<meta name="robots" content="index, follow"\/>/, "");
  }
  return html.replace(
    /(<meta\b[^>]*?)content="index, ?follow"([^>]*name="robots"[^>]*>)|(<meta name="robots" )content="index, ?follow"/,
    (m, a, b, c) => (c ? `${c}content="index, follow, max-image-preview:large"` : `${a}content="index, follow, max-image-preview:large"${b}`),
  );
}

/* Responsive copies for big photos shown small (2026-11 SEO pass). scripts/make_img_variants.py writes
   <name>-w480.webp / -w960.webp and lists them in scripts/img-variants.json. Lazy <img> tags without a
   srcset get one, with sizes="auto, 100vw": Chrome sizes it from the rendered box; browsers without
   sizes=auto use 100vw and fetch what they fetched before. */
const VARIANTS = (() => {
  try {
    return JSON.parse(readFileSync(new URL("./img-variants.json", import.meta.url), "utf8"));
  } catch {
    return {};
  }
})();

function addImageVariants(html) {
  return html.replace(/<img\b[^>]*>/g, (tag) => {
    if (tag.includes("srcset=") || !tag.includes('loading="lazy"')) return tag;
    const m = tag.match(/\ssrc="((?:https:\/\/panamaspot\.com)?(\/images\/[^"]+)\.webp)"/);
    const v = m && VARIANTS[`${m[2]}.webp`];
    if (!v) return tag;
    const prefix = m[1].slice(0, -5);
    const set = [...v.variants.map((w) => `${prefix}-w${w}.webp ${w}w`), `${m[1]} ${v.w}w`].join(", ");
    return tag.replace(/\s?\/?>$/, ` srcset="${set}" sizes="auto, 100vw"$&`);
  });
}

function injectAppJs(html) {
  if (html.includes(APP_JS_TAG)) return html;
  if (html.includes("</body>")) return html.replace("</body>", `${APP_JS_TAG}</body>`);
  return html + APP_JS_TAG;
}

/* Everything GA4 needs to know about a page, derived once from its output
   path so the gtag config and analytics.js read the same values instead of
   each re-parsing the URL at runtime. */
const HUB_SLUGS = {
  "el-valle-de-anton": "elvalle",
  boquete: "boquete",
  "panama-city": "panama-city",
  "bocas-del-toro": "bocas",
  "san-blas": "san-blas",
};

function pageIdentity(relPath) {
  const clean = relPath.replace(/\.html$/, "");

  if (clean.startsWith("funnels/")) {
    const slug = clean.slice("funnels/".length);
    return {
      type: "funnel",
      lang: /_es(?:_|$)/.test(slug) ? "es" : "en",
      slug,
      dest: slug.includes("boquete")
        ? "boquete"
        : slug.includes("elvalle")
          ? "elvalle"
          : "other",
    };
  }

  const isEs = clean === "es" || clean.startsWith("es/");
  const lang = isEs ? "es" : "en";
  const path = isEs ? clean.replace(/^es\/?/, "") : clean;

  if (path.startsWith("articles/")) {
    const slug = path.slice("articles/".length);
    // Destination hubs are a distinct page type (a curated cluster index, not
    // a guide). Separating them here lets GA4 report hub vs article without
    // anyone having to remember a slug list at query time.
    const dest = HUB_SLUGS[slug];
    if (dest) return { type: "hub", lang, slug, dest };
    return { type: "article", lang, slug, dest: null };
  }
  if (path === "" || path === "index") {
    return { type: "home", lang, slug: null, dest: null };
  }
  return { type: "other", lang, slug: null, dest: null };
}

/* The funnels already load gtag.js for the Google Ads conversion tag. On
   those pages GA4 reuses that loader and only adds its own config command —
   one library request, two destinations, no double-counted page views. */
function analyticsSnippet(identity, sharesAdsLoader) {
  const loader = sharesAdsLoader
    ? "<!-- gtag.js is already loaded on this page for Google Ads; GA4 shares that loader. -->"
    : `<script async src="https://www.googletagmanager.com/gtag/js?id=${GA_ID}"></script>`;
  const jsCommand = sharesAdsLoader ? "" : "gtag('js', new Date());\n";

  return (
    `<!-- ${GA_MARKER}: injected by scripts/build-static.mjs — edit there, not here -->\n` +
    `${loader}\n` +
    `<script>\n` +
    `window.__PS_PAGE__ = ${JSON.stringify(identity)};\n` +
    `window.dataLayer = window.dataLayer || [];\n` +
    `function gtag(){dataLayer.push(arguments);}\n` +
    jsCommand +
    `gtag('config', '${GA_ID}', {page_type: ${JSON.stringify(identity.type)}, content_lang: ${JSON.stringify(identity.lang)}});\n` +
    `</script>\n` +
    `<!-- /${GA_MARKER} -->`
  );
}

function injectAnalytics(html, relPath) {
  if (!GA_ID) return html;
  if (html.includes(GA_MARKER)) return html; // already injected — stay idempotent

  const sharesAdsLoader = /googletagmanager\.com\/gtag\/js/.test(html);
  const head = analyticsSnippet(pageIdentity(relPath), sharesAdsLoader);

  // Into <head> so the page view fires early; the loader is async either way.
  html = html.includes("</head>")
    ? html.replace("</head>", `${head}\n</head>`)
    : `${head}\n${html}`;

  if (!html.includes(ANALYTICS_JS_TAG)) {
    html = html.includes("</body>")
      ? html.replace("</body>", `${ANALYTICS_JS_TAG}</body>`)
      : html + ANALYTICS_JS_TAG;
  }

  return html;
}

async function processFile(path) {
  const original = await readFile(path, "utf8");
  const relPath = relative(ROOT, path);
  let html = original;
  html = stripNextRuntime(html);
  html = fixSpanishLang(html, relPath);
  html = selfHostFonts(html);
  html = normaliseRobots(html, relPath);
  html = addImageVariants(html);
  html = addTrustLinks(html);
  html = enrichOrganization(html);
  html = injectAppJs(html);
  html = injectAnalytics(html, relPath);
  if (html !== original) await writeFile(path, html, "utf8");
  return {
    path: relPath,
    changed: html !== original,
    before: original.length,
    after: html.length,
    tagged: html.includes(GA_MARKER) && html.includes(ANALYTICS_JS_TAG),
  };
}

/* Walk every file under out/ and decide whether it's dead weight from the
   Next.js runtime that we can delete now that the HTML references are gone. */
async function* walkAll(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) yield* walkAll(full);
    else if (entry.isFile()) yield full;
  }
}

function isDeadWeight(absPath) {
  const rel = relative(ROOT, absPath);
  const name = basename(absPath);
  // Streaming/server-component payload artifacts that sit next to each page.
  if (name.startsWith("__next.") && name.endsWith(".txt")) return true;
  // The companion index.txt next to every index.html (React Flight payload).
  // robots.txt and sitemap.xml live at the root and are NOT named index.txt.
  if (name === "index.txt") return true;
  // Same payload for flat pages (es.txt next to es.html, _not-found.txt…). These were publicly
  // served and crawlable. robots.txt and verification files have no .html twin, so they stay.
  if (name.endsWith(".txt") && existsSync(absPath.slice(0, -4) + ".html")) return true;
  // _next/static/chunks/*.js — the JS we stripped references to.
  if (rel.startsWith("_next/static/chunks/") && name.endsWith(".js")) return true;
  // Build-manifest folders: _next/static/<build-id>/{_buildManifest.js,...}.
  // These only contain .js manifests describing chunks we already deleted.
  if (/^_next\/static\/[^/]+\/_(build|ssg|clientMiddleware)Manifest\.js$/.test(rel)) {
    return true;
  }
  return false;
}

async function purgeEmptyDirs(dir) {
  /* Recursively delete now-empty directories left behind by the file purge. */
  const entries = await readdir(dir, { withFileTypes: true });
  for (const e of entries) {
    if (e.isDirectory()) await purgeEmptyDirs(join(dir, e.name));
  }
  if (dir === ROOT.replace(/\/$/, "")) return;
  const after = await readdir(dir);
  if (after.length === 0) await rm(dir, { recursive: true, force: true });
}

/* The homepages are designed and built outside Next (design/hub-home/build_previews.py writes
   site-pages/index.html and site-pages/es.html). Next still renders /, /es and their <head>, so the
   title, description, robots, canonical, hreflang, Open Graph and JSON-LD stay defined in one place
   (src/app/layout.tsx and the page metadata). Here the designed page replaces the Next page and takes
   those SEO tags from it, into its <!--SEO-HEAD--> slot. */
const SITE_PAGES = new URL("../site-pages/", import.meta.url).pathname;
const SEO_TAG = /<title>[\s\S]*?<\/title>|<script type="application\/ld\+json">[\s\S]*?<\/script>|<meta\b[^>]*>|<link\b[^>]*>/g;

function seoHead(nextHtml) {
  const head = nextHtml.slice(0, nextHtml.indexOf("</head>"));
  const keep = [];
  for (const m of head.matchAll(SEO_TAG)) {
    const t = m[0];
    if (t.startsWith("<meta") && /charset|name="viewport"|next-size-adjust/i.test(t)) continue;
    if (t.startsWith("<link") && !/rel="(?:canonical|alternate|icon)"/.test(t)) continue;
    keep.push(t);
  }
  return keep.join("");
}

/* Trust pages (2026-11-08): About, Contact and Privacy in both languages, built by
   design/hub-home/build_previews.py into public/. Every footer's "Panama Spot" column links them,
   and every PanamaSpot Organization node in JSON-LD points at the policies they publish, so Google
   can connect each guide to its publisher's editorial, corrections and funding statements.
   Done here so it covers every generator's pages (guides, hubs, homepages, trust pages). */
const TRUST_LINKS = {
  Home: '<li><a href="/about">About</a></li><li><a href="/contact">Contact</a></li><li><a href="/privacy">Privacy</a></li>',
  Inicio: '<li><a href="/es/sobre-nosotros">Sobre nosotros</a></li><li><a href="/es/contacto">Contacto</a></li><li><a href="/es/privacidad">Privacidad</a></li>',
};
const FOOT_COL = /(<div><h4>Panam[aá] Spot<\/h4><ul><li><a href="[^"]*">(Home|Inicio)<\/a><\/li>)(?!<li><a href="\/(?:about|es\/sobre-nosotros)")/;
function addTrustLinks(html) {
  return html.replace(FOOT_COL, (m, open, home) => open + TRUST_LINKS[home]);
}

const SITE_URL = "https://panamaspot.com";
const ORG_POLICIES = {
  publishingPrinciples: `${SITE_URL}/about#how-we-make`,
  correctionsPolicy: `${SITE_URL}/about#corrections`,
  ownershipFundingInfo: `${SITE_URL}/about#independence`,
  actionableFeedbackPolicy: `${SITE_URL}/contact`,
};
function enrichOrganization(html) {
  return html.replace(/(<script\b[^>]*type="application\/ld\+json"[^>]*>)([\s\S]*?)(<\/script>)/g, (m, open, json, close) => {
    let data;
    try {
      data = JSON.parse(json);
    } catch {
      return m;
    }
    let hit = false;
    const walk = (n) => {
      if (Array.isArray(n)) return n.forEach(walk);
      if (!n || typeof n !== "object") return;
      if (n["@type"] === "Organization" && /^panam[aá] ?spot$/i.test(n.name || "")) {
        for (const [k, v] of Object.entries(ORG_POLICIES)) if (!(k in n)) { n[k] = v; hit = true; }
        if (!("url" in n)) { n.url = SITE_URL; hit = true; }
      }
      Object.values(n).forEach(walk);
    };
    walk(data);
    return hit ? open + JSON.stringify(data) + close : m;
  });
}

/* The designed 404 (site-pages/404.html) replaces Next's not-found page. It already carries its own
   noindex <head>; Netlify serves out/404.html for every unknown English URL. */
async function swap404() {
  const designed = join(SITE_PAGES, "404.html");
  if (!existsSync(designed)) return;
  await writeFile(join(ROOT, "404.html"), readFileSync(designed, "utf8"), "utf8");
  console.log("404 page swapped in from site-pages/404.html.");
}

async function swapHomepages() {
  for (const name of ["index.html", "es.html"]) {
    const designed = readFileSync(join(SITE_PAGES, name), "utf8");
    const nextPage = await readFile(join(ROOT, name), "utf8");
    const head = seoHead(nextPage);
    if (!designed.includes("<!--SEO-HEAD-->") || !/rel="canonical"/.test(head) || !/<title>/.test(head)) {
      console.error(`\n✗ Homepage swap failed for ${name}: missing SEO slot, canonical or title.`);
      process.exit(1);
    }
    await writeFile(join(ROOT, name), designed.replace("<!--SEO-HEAD-->", head), "utf8");
  }
  console.log("Homepages swapped in from site-pages/ with the Next <head> SEO tags.");
}

async function main() {
  try {
    await stat(ROOT);
  } catch {
    console.error(`out/ not found — run \`next build\` first.`);
    process.exit(1);
  }

  await swapHomepages();
  await swap404();

  let total = 0;
  let changed = 0;
  let bytesSaved = 0;
  const untagged = [];
  for await (const file of walkHtml(ROOT)) {
    const r = await processFile(file);
    total += 1;
    if (r.changed) {
      changed += 1;
      bytesSaved += r.before - r.after;
    }
    if (!r.tagged) untagged.push(r.path);
  }
  const kb = (bytesSaved / 1024).toFixed(1);
  console.log(`Cleaned ${changed}/${total} HTML files — ${kb} KB removed from HTML.`);

  let deleted = 0;
  let purgedBytes = 0;
  for await (const file of walkAll(ROOT)) {
    if (!isDeadWeight(file)) continue;
    const s = await stat(file);
    purgedBytes += s.size;
    await unlink(file);
    deleted += 1;
  }
  await purgeEmptyDirs(ROOT.replace(/\/$/, ""));
  const purgedKb = (purgedBytes / 1024).toFixed(1);
  console.log(`Purged ${deleted} runtime artifacts — ${purgedKb} KB removed from disk.`);

  /* Analytics coverage is asserted, not assumed. A page that silently ships
     without the tag is invisible for weeks; a failed build is obvious now. */
  if (!GA_ID) {
    console.warn(
      `\n⚠  NEXT_PUBLIC_GA_ID is not set — no analytics injected into ${total} pages.\n` +
        `   Set it in .env.local for local builds, and in the Netlify UI for deploys.`,
    );
  } else if (untagged.length) {
    console.error(
      `\n✗ Analytics missing from ${untagged.length}/${total} pages:\n` +
        untagged.map((p) => `    ${p}`).join("\n"),
    );
    process.exit(1);
  } else {
    console.log(`Analytics ${GA_ID} verified on ${total}/${total} pages.`);
  }

  assertSitemapIsWellFormed();
  await assertShareImagesExist();
  await redirectHtmlVariants();
}

/* /articles/x.html, /index.html and /es.html answered 200 as duplicates of their clean URLs
   (the canonical tag already pointed Google at the clean one). Netlify redirect rules can't match
   "*.html", so write one forced 301 per page. Forced (!) is required because the .html file
   exists; the clean URL itself matches no rule, so there is no loop. Funnels are left alone:
   Google Ads final URLs may use their .html form, and netlify.toml rewrites /funnels/:slug. */
async function redirectHtmlVariants() {
  const rules = ["/index.html  /  301!", "/es.html  /es  301!"];
  for (const p of ["about", "contact", "privacy", "es/sobre-nosotros", "es/contacto", "es/privacidad"]) rules.push(`/${p}.html  /${p}  301!`);
  for (const dir of ["articles", "es/articles"]) {
    for (const name of (await readdir(join(ROOT, dir))).sort()) {
      if (name.endsWith(".html")) rules.push(`/${dir}/${name}  /${dir}/${name.slice(0, -5)}  301!`);
    }
  }
  const file = join(ROOT, "_redirects");
  const current = existsSync(file) ? readFileSync(file, "utf8") : "";
  const MARK = "# .html variants -> clean URLs (generated by scripts/build-static.mjs)";
  const base = current.split(MARK)[0].trimEnd();
  // Last of all: unknown Spanish URLs get the Spanish 404 (it only applies when no file matches).
  const tail = "\n# Spanish 404 for unknown /es/ URLs (must stay last)\n/es/*  /es/404.html  404\n";
  await writeFile(file, `${base}\n\n${MARK}\n${rules.join("\n")}\n${tail}`);
  console.log(`Redirects: ${rules.length} .html variants -> clean URLs.`);
}

/* Every og:image must ship. .gitignore excludes public/images/**\/*.jpg, so a share card that is not
   force-added exists locally but 404s on Netlify: in 2026-11 eleven guides shared on WhatsApp and
   Facebook with no picture and nothing noticed. On Netlify the file is simply absent, so fail there. */
async function assertShareImagesExist() {
  const missing = [];
  for await (const file of walkHtml(ROOT)) {
    const html = await readFile(file, "utf8");
    const m = html.match(/<meta[^>]*property="og:image"[^>]*content="https:\/\/panamaspot\.com(\/[^"?]+)"|<meta[^>]*content="https:\/\/panamaspot\.com(\/[^"?]+)"[^>]*property="og:image"/);
    const path = m && (m[1] || m[2]);
    if (path && !existsSync(join(ROOT, decodeURIComponent(path)))) missing.push(`${relative(ROOT, file)} → ${path}`);
  }
  if (missing.length) {
    console.error(`\n✗ ${missing.length} share images (og:image) are missing from the build:\n` + missing.map((x) => `    ${x}`).join("\n") +
      `\n  If they exist locally, they are probably git-ignored: git add -f public/images/...`);
    process.exit(1);
  }
  console.log("Share images (og:image) present for every page.");
}

/* The sitemap is generated by Next, which interpolates every URL into the XML
   RAW — `<image:loc>${image}</image:loc>`, no escaping. Our Pexels heroes carry
   `?auto=compress&cs=tinysrgb&w=…`, so 212 bare ampersands shipped and Search
   Console refused the whole file ("unable to read your Sitemap … Line 54").
   Nobody noticed for weeks because nothing ever parsed it. Now the build does. */
function assertSitemapIsWellFormed() {
  const file = join(ROOT, "sitemap.xml");
  let xml;
  try {
    xml = readFileSync(file, "utf8");
  } catch {
    console.error("\n✗ out/sitemap.xml was not generated.");
    process.exit(1);
  }

  // Bare ampersands are the failure mode Next actually produces.
  const bare = [...xml.matchAll(/&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)/g)];
  if (bare.length) {
    const line = xml.slice(0, bare[0].index).split("\n").length;
    console.error(
      `\n✗ sitemap.xml has ${bare.length} unescaped "&" — invalid XML, ` +
        `Search Console will reject it. First at line ${line}.\n` +
        `   Escape URLs in src/app/sitemap.ts (xmlSafe).`,
    );
    process.exit(1);
  }

  // Tags must nest and close. A cheap well-formedness check without a parser
  // dependency: every <url> closes, and counts of the elements we emit match.
  const pairs = [["url", "url"], ["loc", "loc"], ["image:image", "image:image"]];
  for (const [open, close] of pairs) {
    const o = (xml.match(new RegExp(`<${open}>`, "g")) || []).length;
    const c = (xml.match(new RegExp(`</${close}>`, "g")) || []).length;
    if (o !== c) {
      console.error(`\n✗ sitemap.xml: ${o} <${open}> but ${c} </${close}>.`);
      process.exit(1);
    }
  }
  const urls = (xml.match(/<url>/g) || []).length;
  const imgs = (xml.match(/<image:image>/g) || []).length;
  console.log(`Sitemap well-formed: ${urls} URLs, ${imgs} images, 0 unescaped entities.`);
}

/* The index behind the search box: every guide, written fresh on each build so a new page can never be missing. */
async function buildSearchIndex() {
  const decode = (t) => t.replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&nbsp;/g, " ").replace(/\s+/g, " ").trim();
  const entries = [];
  for (const dir of ["articles", "es/articles"]) {
    for (const name of await readdir(join(ROOT, dir))) {
      if (!name.endsWith(".html")) continue;
      const html = await readFile(join(ROOT, dir, name), "utf8");
      const body = html.replace(/<style[\s\S]*?<\/style>|<script[\s\S]*?<\/script>/g, "");
      const h1 = /<h1[^>]*>([\s\S]*?)<\/h1>/.exec(body);
      const desc = /<meta content="([^"]*)" name="description"/.exec(html) || /<meta name="description" content="([^"]*)"/.exec(html);
      const trail = /"@type":\s*"BreadcrumbList"[\s\S]*?"position":\s*2,[\s\S]*?"name":\s*"([^"]*)"[\s\S]*?"position":\s*3/.exec(html);
      const main = /<(?:article|main)\b[\s\S]*/.exec(body);
      const h2s = main ? [...main[0].matchAll(/<h2\b[^>]*>([\s\S]*?)<\/h2>/g)].map((m) => decode(m[1])).filter((t) => t.length < 90) : [];
      // A very small picture for the result row: our own thumbnail, or a small size from the photo's CDN.
      const heroTag = /<img\b[^>]*class="hero-img"[^>]*>/.exec(html) || /art-hero-img-full"[^>]*>\s*<img\b[^>]*>/.exec(html) || /hub-hero-img"[^>]*>\s*<img\b[^>]*>/.exec(html);
      const heroSrc = heroTag ? (/\bsrc="([^"]+)"/.exec(heroTag[0]) || [])[1] || "" : "";
      const thumbName = `${dir.startsWith("es") ? "es-" : ""}${name.replace(/\.html$/, "")}.webp`;
      let thumb = "";
      if (await stat(join(ROOT, "images/thumbs", thumbName)).catch(() => null)) thumb = `/images/thumbs/${thumbName}`;
      else if (heroSrc.includes("images.pexels.com")) thumb = `${heroSrc.split("?")[0]}?auto=compress&cs=tinysrgb&w=112&h=112&fit=crop`;
      else if (/upload\.wikimedia\.org\/.*\/thumb\//.test(heroSrc)) thumb = heroSrc.replace(/\/\d+px-/, "/250px-");
      else if (heroSrc.includes("upload.wikimedia.org")) thumb = heroSrc.replace(/\/commons\/(\w\/\w\w\/)([^/?]+).*$/, "/commons/thumb/$1$2/250px-$2");
      entries.push({
        i: thumb,
        u: `/${dir}/${name.replace(/\.html$/, "")}`,
        l: dir.startsWith("es") ? "es" : "en",
        t: decode(h1 ? h1[1] : name),
        d: decode(desc ? desc[1] : ""),
        r: trail ? decode(trail[1]) : "",
        h: h2s.slice(0, 14).join(" · "),
      });
    }
  }
  await writeFile(join(ROOT, "search-index.json"), JSON.stringify(entries));
  console.log(`Search index: ${entries.length} guides.`);
  await writeLlmsTxt(entries);
}

/* llms.txt (llmstxt.org): a plain-Markdown map of the site for AI assistants and their crawlers,
   rebuilt from the same entries as the search index so it can never go stale. It grants nothing by
   itself; access is robots.txt (User-agent: * / Allow: /), which already lets every crawler in. */
const HUB_ORDER = ["panama-city", "boquete", "el-valle-de-anton", "bocas-del-toro", "san-blas"];
async function writeLlmsTxt(entries) {
  const SITE = "https://panamaspot.com";
  const line = (e) => `- [${e.t}](${SITE}${e.u})${e.d ? `: ${e.d}` : ""}`;
  const slug = (e) => e.u.split("/").pop();
  const section = (lang) => {
    const mine = entries.filter((e) => e.l === lang);
    const hubs = HUB_ORDER.map((h) => mine.find((e) => slug(e) === h)).filter(Boolean);
    const byRegion = new Map();
    for (const e of mine) {
      if (hubs.includes(e)) continue;
      const r = e.r || (lang === "es" ? "Panamá" : "Panama");
      if (!byRegion.has(r)) byRegion.set(r, []);
      byRegion.get(r).push(e);
    }
    let out = `\n## ${lang === "es" ? "Guías por destino (español)" : "Destination guides (English)"}\n\n` + hubs.map(line).join("\n") + "\n";
    for (const [r, list] of [...byRegion].sort((a, b) => b[1].length - a[1].length)) {
      out += `\n## ${r}${lang === "es" ? " (español)" : ""}\n\n` + list.sort((a, b) => a.t.localeCompare(b.t)).map(line).join("\n") + "\n";
    }
    return out;
  };
  const txt =
    "# Panamá Spot\n\n" +
    "> Independent travel guides to Panama, in English and Spanish: where to go, how to get there, what it costs and when to visit. " +
    "Destinations covered in depth: Panama City, Boquete and the Chiriquí highlands, El Valle de Antón, Bocas del Toro and San Blas (Guna Yala).\n\n" +
    `AI assistants and search tools are welcome to read, cite and link to these guides. Please link to the guide you use. Homepages: ${SITE} (English), ${SITE}/es (español). Sitemap: ${SITE}/sitemap.xml\n` +
    section("en") + section("es");
  await writeFile(join(ROOT, "llms.txt"), txt);
  console.log(`llms.txt: ${entries.length} guides listed.`);
}

main().then(buildSearchIndex).catch((err) => {
  console.error(err);
  process.exit(1);
});
