import puppeteer from "puppeteer-core";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: "new",
  args: ["--no-sandbox", "--force-device-scale-factor=2"],
});

// ── OG image: 1200×630, navy brand card ─────────────────────────────────────
const og = `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;box-sizing:border-box}
  html,body{width:1200px;height:630px}
  body{
    background:linear-gradient(135deg,#072357 0%,#03133a 100%);
    color:#fff;font-family:Georgia,'Times New Roman',serif;
    display:flex;flex-direction:column;justify-content:center;
    padding:90px;position:relative;overflow:hidden;
  }
  .bar{position:absolute;top:0;left:0;width:14px;height:100%;background:#da121a}
  .kicker{font-family:-apple-system,Helvetica,Arial,sans-serif;font-size:22px;
    letter-spacing:.32em;text-transform:uppercase;color:#a8b8d4;margin-bottom:26px;font-weight:600}
  .word{font-size:150px;line-height:.95;letter-spacing:-.02em}
  .word .dot{color:#da121a}
  .tag{font-family:-apple-system,Helvetica,Arial,sans-serif;font-size:34px;
    color:#cdd6e8;margin-top:30px;max-width:880px;line-height:1.3}
</style></head><body>
  <div class="bar"></div>
  <div class="kicker">Panamaspot</div>
  <div class="word">Panam&aacute;<span class="dot">.</span></div>
  <div class="tag">The complete guide to traveling in Panama — destinations, eco-tourism &amp; itineraries.</div>
</body></html>`;

const ogPage = await browser.newPage();
await ogPage.setViewport({ width: 1200, height: 630, deviceScaleFactor: 1 });
await ogPage.setContent(og, { waitUntil: "networkidle0" });
await ogPage.screenshot({ path: "public/og-default.jpg", type: "jpeg", quality: 90 });
await ogPage.close();

// ── Logo: 512×512, square wordmark on white ─────────────────────────────────
const logo = `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;box-sizing:border-box}
  html,body{width:512px;height:512px}
  body{background:#fff;display:flex;align-items:center;justify-content:center}
  .mark{display:flex;flex-direction:column;align-items:center;gap:18px}
  .sq{width:120px;height:120px;border-radius:26px;background:#072357;
    display:flex;align-items:center;justify-content:center;
    box-shadow:inset -16px -16px 0 0 rgba(218,18,26,.22)}
  .sq span{font-family:Georgia,serif;font-size:78px;color:#fff;line-height:1}
  .wm{font-family:Georgia,serif;font-size:46px;color:#072357;letter-spacing:-.01em}
  .wm b{color:#da121a;font-weight:400}
</style></head><body>
  <div class="mark">
    <div class="sq"><span>P</span></div>
    <div class="wm">Panama<b>spot</b></div>
  </div>
</body></html>`;

const logoPage = await browser.newPage();
await logoPage.setViewport({ width: 512, height: 512, deviceScaleFactor: 1 });
await logoPage.setContent(logo, { waitUntil: "networkidle0" });
await logoPage.screenshot({ path: "public/logo.png", type: "png" });
await logoPage.close();

await browser.close();
console.log("Wrote public/og-default.jpg and public/logo.png");
