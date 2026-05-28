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

   Run with: node scripts/build-static.mjs
*/

import { readdir, readFile, writeFile, stat, rm, unlink } from "node:fs/promises";
import { join, relative, basename, dirname } from "node:path";

const ROOT = new URL("../out/", import.meta.url).pathname;
const APP_JS_TAG = '<script src="/app.js" defer></script>';

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

async function processFile(path) {
  const original = await readFile(path, "utf8");
  const relPath = relative(ROOT, path);
  let html = original;
  html = stripNextRuntime(html);
  html = fixSpanishLang(html, relPath);
  html = injectAppJs(html);
  if (html !== original) await writeFile(path, html, "utf8");
  return { path: relPath, changed: html !== original, before: original.length, after: html.length };
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
  for await (const file of walkHtml(ROOT)) {
    const r = await processFile(file);
    total += 1;
    if (r.changed) {
      changed += 1;
      bytesSaved += r.before - r.after;
    }
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
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
