import pp from "puppeteer-core";
const CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const pages=[["panama-city","/articles/panama-city"],["el-valle","/articles/el-valle-de-anton"]];
const b=await pp.launch({executablePath:CHROME,headless:"new",args:["--no-sandbox","--window-size=1440,900"]});
for(const [name,path] of pages){
  const p=await b.newPage(); await p.setViewport({width:1440,height:900});
  const bad=[];
  p.on("response",r=>{const u=r.url();if(r.status()>=400&&!u.includes("favicon"))bad.push(r.status()+" "+u.slice(0,70))});
  p.on("pageerror",e=>bad.push("ERR "+e.message));
  await p.goto("http://localhost:3000"+path,{waitUntil:"domcontentloaded",timeout:30000});
  await new Promise(r=>setTimeout(r,2500));
  const info=await p.evaluate(()=>{
    const imgs=[...document.querySelectorAll(".imgph.photo")].map(e=>getcomputedStyleBg(e)).filter(Boolean);
    function getcomputedStyleBg(){return null}
    const bgEls=[...document.querySelectorAll(".imgph.photo")];
    return {
      theme: document.querySelector("main.article-page")?.getAttribute("data-theme")||"(blue)",
      h1: document.querySelector("h1")?.innerText.slice(0,55),
      title: document.title,
      photoTiles: bgEls.length,
      progressBg: getComputedStyle(document.querySelector(".read-progress")).backgroundColor,
    };
  });
  await p.evaluate(()=>window.scrollTo(0,800)); await new Promise(r=>setTimeout(r,500));
  await p.screenshot({path:`/tmp/new-${name}.png`});
  await p.evaluate(()=>window.scrollTo(0,0)); await new Promise(r=>setTimeout(r,300));
  await p.screenshot({path:`/tmp/new-${name}-top.png`});
  console.log(`\n=== ${name} ===`);
  console.log("  theme:",info.theme,"| photoTiles:",info.photoTiles,"| progressBg:",info.progressBg);
  console.log("  title:",info.title);
  console.log("  h1:",info.h1);
  console.log("  bad requests:",bad.length?bad.join(" | "):"none");
  await p.close();
}
await b.close();
