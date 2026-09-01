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
import { readFileSync } from "node:fs";
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

async function main() {
  try {
    await stat(ROOT);
  } catch {
    console.error(`out/ not found — run \`next build\` first.`);
    process.exit(1);
  }

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
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
