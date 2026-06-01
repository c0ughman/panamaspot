import pp from "puppeteer-core";
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const sets = {
  "panama-city": [2666249, 19620790, 2474690, 20323097, 17477516, 14840824, 5864401, 14840760, 14840678, 14465475, 14840814, 2146686, 6369345, 15088493, 18118137, 10550029, 18118099, 13110362, 16164835, 19651145, 12495663, 33803478, 31769772],
  "el-valle": [30774416, 30774409, 30774387, 18077651, 30774398, 18117801, 30774401, 30774413, 6943251, 4956963, 11896081, 13938241, 16053611, 8094200, 6982804, 14714541, 7823008, 5988866, 18343797, 19789146, 2918139, 3603874, 9566563, 10343761, 9246451],
};
const b = await pp.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
for (const [name, ids] of Object.entries(sets)) {
  const cells = ids.map((id) => `<figure><img src="https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=360"><figcaption>${id}</figcaption></figure>`).join("");
  const html = `<!doctype html><meta charset=utf-8><style>body{margin:0;background:#fff;font-family:Arial;display:grid;grid-template-columns:repeat(4,1fr);gap:4px}figure{margin:0;position:relative}img{width:100%;height:150px;object-fit:cover;display:block}figcaption{position:absolute;top:4px;left:4px;background:#000;color:#fff;font-size:16px;font-weight:bold;padding:2px 6px}</style>${cells}`;
  const p = await b.newPage();
  await p.setViewport({ width: 1200, height: 1000 });
  await p.setContent(html, { waitUntil: "networkidle0", timeout: 60000 });
  await p.screenshot({ path: `/tmp/contact-${name}.png`, fullPage: true });
  await p.close();
  console.log("wrote /tmp/contact-" + name + ".png");
}
await b.close();
