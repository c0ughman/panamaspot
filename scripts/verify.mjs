import puppeteer from "puppeteer-core";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const BASE = "http://localhost:3000";
const PAGES = [
  ["en-home", "/"],
  ["es-home", "/es"],
  ["blue-article", "/articles/sendero-los-quetzales"],
  ["green-article", "/articles/bocas-del-toro"],
];

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: "new",
  args: ["--no-sandbox", "--window-size=1440,900"],
});

for (const [name, path] of PAGES) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  const errors = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  page.on("pageerror", (e) => errors.push("PAGEERROR: " + e.message));

  await page.goto(BASE + path, { waitUntil: "domcontentloaded", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1200));

  const headerSel = path.startsWith("/articles") ? ".art-header-bar" : ".header-wrapper";

  const top = await page.evaluate((sel) => {
    const h = document.querySelector(sel);
    const p = document.querySelector(".read-progress");
    return {
      headerBg: h ? getComputedStyle(h).backgroundColor : "NO_HEADER",
      progressExists: !!p,
      progressTop: p ? getComputedStyle(p).top : null,
      progressBg: p ? getComputedStyle(p).backgroundColor : null,
      htmlLang: document.documentElement.lang,
      h1: document.querySelector("h1")?.innerText?.slice(0, 60),
    };
  }, headerSel);

  await page.evaluate(() => window.scrollTo(0, 700));
  await new Promise((r) => setTimeout(r, 400));

  const scrolled = await page.evaluate((sel) => {
    const h = document.querySelector(sel);
    const p = document.querySelector(".read-progress");
    return {
      headerBg: h ? getComputedStyle(h).backgroundColor : "NO_HEADER",
      headerClass: h ? h.className : "",
      progressWidth: p ? p.getBoundingClientRect().width : null,
    };
  }, headerSel);

  await page.screenshot({ path: `/tmp/shot-${name}.png` });

  console.log(`\n=== ${name} (${path}) ===`);
  console.log("  htmlLang:", top.htmlLang, "| h1:", JSON.stringify(top.h1));
  console.log("  TOP   headerBg:", top.headerBg);
  console.log("  SCROLL headerBg:", scrolled.headerBg, "| class:", scrolled.headerClass);
  console.log("  progress exists:", top.progressExists, "| top:", top.progressTop, "| bg:", top.progressBg, "| scrolledWidth:", scrolled.progressWidth);
  if (errors.length) console.log("  CONSOLE ERRORS:", errors.slice(0, 5));
  await page.close();
}

await browser.close();
console.log("\nScreenshots written to /tmp/shot-*.png");
