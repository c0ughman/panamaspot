import pp from "puppeteer-core";
const CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const pages=[["pc","/es/articles/panama-city"],["ev","/es/articles/el-valle-de-anton"]];
const b=await pp.launch({executablePath:CHROME,headless:"new",args:["--no-sandbox","--window-size=1440,900"]});
for(const [name,path] of pages){
  const p=await b.newPage(); await p.setViewport({width:1440,height:900});
  const bad=[];
  p.on("response",r=>{const u=r.url();if(r.status()>=400&&!u.includes("favicon"))bad.push(r.status()+" "+u.slice(0,60))});
  await p.goto("http://localhost:3000"+path,{waitUntil:"domcontentloaded",timeout:30000});
  await new Promise(r=>setTimeout(r,2500));
  const info=await p.evaluate(()=>({lang:document.documentElement.lang,theme:document.querySelector("main.article-page")?.getAttribute("data-theme")||"(blue)",h1:document.querySelector("h1")?.innerText.slice(0,40),tiles:document.querySelectorAll(".imgph.photo").length}));
  await p.evaluate(()=>window.scrollTo(0,700)); await new Promise(r=>setTimeout(r,400));
  await p.screenshot({path:`/tmp/es-${name}.png`});
  console.log(`${path} -> lang:${info.lang} theme:${info.theme} tiles:${info.tiles} h1:"${info.h1}" bad:${bad.length?bad.join(","):"none"}`);
  await p.close();
}
await b.close();
