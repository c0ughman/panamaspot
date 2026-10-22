#!/usr/bin/env node
/*
 * indexnow.mjs — tell Bing (and every other IndexNow engine: Yandex, Seznam,
 * Naver…) that pages are new or changed, instead of waiting for a recrawl.
 * ChatGPT search draws on Bing's index, so this is also the fast lane there.
 *
 *   node scripts/indexnow.mjs                 # every URL in the live sitemap
 *   node scripts/indexnow.mjs <url> [<url>…]  # just these
 *
 * Run it AFTER Netlify has deployed: IndexNow fetches the key file from the
 * live site to prove we own it, so the script checks that first and stops if
 * the key isn't being served.
 */
const HOST = "panamaspot.com";
const KEY = "791a0243869cc609199c40fcbd98599b"; // public/<KEY>.txt holds the same string
const KEY_URL = `https://${HOST}/${KEY}.txt`;

const live = await fetch(KEY_URL);
if (!live.ok || (await live.text()).trim() !== KEY) {
  console.error(`Key file not live at ${KEY_URL} (HTTP ${live.status}). Deploy first.`);
  process.exit(1);
}

let urls = process.argv.slice(2);
if (urls.length === 0) {
  const xml = await (await fetch(`https://${HOST}/sitemap.xml`)).text();
  urls = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].replaceAll("&amp;", "&"));
}
urls = [...new Set(urls)].filter((u) => new URL(u).hostname === HOST);
if (urls.length === 0) {
  console.error("No URLs to submit.");
  process.exit(1);
}

const res = await fetch("https://api.indexnow.org/indexnow", {
  method: "POST",
  headers: { "Content-Type": "application/json; charset=utf-8" },
  body: JSON.stringify({ host: HOST, key: KEY, keyLocation: KEY_URL, urlList: urls }),
});
// 200 = accepted, 202 = accepted, key validation pending. Anything else is a failure.
console.log(`IndexNow: HTTP ${res.status} for ${urls.length} URLs`);
if (res.status !== 200 && res.status !== 202) {
  console.error(await res.text());
  process.exit(1);
}
