/* End-to-end check: click real CTAs in a real browser and inspect what the
   page actually pushed into dataLayer. googletagmanager.com is blocked so the
   real GA library never drains the queue — what we read is exactly what our
   code emitted. */
import puppeteer from "puppeteer-core";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { join, extname } from "node:path";

const OUT = new URL("../out/", import.meta.url).pathname;
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css" };

const server = createServer(async (req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0]);
  if (p.endsWith("/")) p += "index.html";
  if (!extname(p)) p += ".html";               // mirrors the Netlify rewrite
  try {
    const buf = await readFile(join(OUT, p));
    res.writeHead(200, { "content-type": TYPES[extname(p)] || "application/octet-stream" });
    res.end(buf);
  } catch { res.writeHead(404); res.end("nope"); }
});
await new Promise((r) => server.listen(0, r));
const base = `http://localhost:${server.address().port}`;

const browser = await puppeteer.launch({ executablePath: CHROME, headless: "new" });
const page = await browser.newPage();
await page.setRequestInterception(true);
page.on("request", (r) =>
  /googletagmanager\.com|google-analytics\.com|fonts\.g/.test(r.url()) ? r.abort() : r.continue(),
);

// Stop every navigation so a click never leaves the page under test.
await page.evaluateOnNewDocument(() => {
  document.addEventListener("click", (e) => e.preventDefault(), true);
});

const results = [];
async function clickAndRead(url, selector, label) {
  await page.goto(base + url, { waitUntil: "domcontentloaded" });
  await page.evaluate(() => { window.dataLayer = window.dataLayer || []; window.dataLayer.length = 0; });
  const found = await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) return false;
    el.click();
    return true;
  }, selector);
  if (!found) { results.push({ label, ok: false, note: `selector matched nothing: ${selector}` }); return; }
  const events = await page.evaluate(() =>
    (window.dataLayer || [])
      .map((a) => Array.from(a))
      .filter((a) => a[0] === "event")
      .map((a) => ({ name: a[1], params: a[2] })),
  );
  results.push({ label, ok: true, events });
}

const A = "/articles/things-to-do-in-boquete-panama";
await clickAndRead(A, ".evb-banner a[href^='/funnels/']", "article · banner");
await clickAndRead(A, ".evb-offer-foot a[href^='/funnels/']", "article · offer");
await clickAndRead(A, ".evb-rail a[href^='/funnels/']", "article · rail");
await clickAndRead(A, ".evb-closer a[href^='/funnels/']", "article · closer");
await clickAndRead("/articles/el-valle-de-anton-with-kids", "p > a[href^='/funnels/']", "article · inline prose");
await clickAndRead("/es/articles/que-hacer-en-boquete-guia-completa", ".evb-banner a[href^='/funnels/']", "ES article · banner");
await clickAndRead("/funnels/evalley_boquete", "a[href^='https://wa.me/']", "funnel EN · whatsapp (Ads page)");
await clickAndRead("/funnels/evalley_boquete_es", "a[href^='https://wa.me/']", "funnel ES · whatsapp (no Ads tag)");

for (const r of results) {
  console.log(`\n▸ ${r.label}`);
  if (!r.ok) { console.log(`   ✗ ${r.note}`); continue; }
  if (!r.events.length) { console.log("   ✗ no events fired"); continue; }
  for (const e of r.events) console.log(`   ${e.name}  ${JSON.stringify(e.params)}`);
}

await browser.close();
server.close();
