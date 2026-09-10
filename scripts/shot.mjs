// shot.mjs — screenshot built pages, to check image crops with your own eyes.
//
// The hero box is 140% tall and pinned at top:-20%, so a sky-heavy photograph
// can render as nothing but sky and no amount of reading the markup tells you.
// Likewise a HEIC converted without -auto-orient looks fine in the file listing
// and sideways on the page. Look at the page.
//
//   npx serve out -l 4321
//   node scripts/shot.mjs /articles/foo=/tmp/foo.png [more...]
//   node scripts/shot.mjs --el /articles/foo=/tmp/x.png ".art-inline-img.is-map"
import pp from "puppeteer-core";
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const args = process.argv.slice(2);
const elMode = args[0] === "--el";
const jobs = elMode ? [args[1]] : args;
const sel = elMode ? args[2] : null;
const b = await pp.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
for (const job of jobs) {
  const [url, out] = job.split("=");
  const p = await b.newPage();
  await p.setViewport({ width: 1440, height: 900 });
  await p.goto("http://localhost:4321" + url, { waitUntil: "networkidle2", timeout: 60000 });
  if (sel) await p.evaluate(s => document.querySelector(s)?.scrollIntoView({ block: "center" }), sel);
  await new Promise(r => setTimeout(r, sel ? 1500 : 900));   // let lazy images load
  const el = sel ? await p.$(sel) : null;
  await (el || p).screenshot({ path: out });
  console.log("shot", out);
  await p.close();
}
await b.close();
