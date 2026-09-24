// Controleert alle pagina's op desktop en mobiel: onzichtbare inhoud, lege stukken, horizontaal scrollen,
// kapotte ankers/afbeeldingen, 4xx-responses en JS-fouten. Start eerst een lokale server op poort 8765.
// Gebruik: node tools/qa-site.js /tmp
const { chromium } = (()=>{try{return require('playwright')}catch(e){return require('/opt/node22/lib/node_modules/playwright')}})();
const fs=require('fs');const {execSync}=require('child_process');
(async()=>{const b=await chromium.launch();const out=process.argv[2];
const files=fs.readdirSync(require('path').join(__dirname,'..')).filter(f=>f.endsWith('.html'));const issues=[];
for(const [W,H,tag] of [[1280,900,'D'],[390,844,'M']]){
for(const f of files){const u=f==='index.html'?'/':'/'+f.slice(0,-5);
 const p=await b.newPage({viewport:{width:W,height:H}});
 await p.addInitScript(()=>{try{localStorage.setItem('vwConsent','{"v":1}');sessionStorage.setItem('vwWaSeen','1')}catch(e){}});
 await p.route(/fonts\.(googleapis|gstatic)|trustindex/,r=>r.abort());
 p.on('pageerror',e=>issues.push(`${tag} ${u} JS ${e.message}`));
 p.on('response',r=>{if(r.status()>=400)issues.push(`${tag} ${u} HTTP ${r.status()} ${r.url()}`)});
 await p.goto('http://127.0.0.1:8765'+u,{waitUntil:'load'});
 const TH=await p.evaluate(()=>document.documentElement.scrollHeight);
 for(let y=0;y<TH;y+=Math.round(H*0.6)){await p.evaluate(y=>window.scrollTo(0,y),y);await p.waitForTimeout(50);}
 await p.waitForTimeout(1000);
 const r=await p.evaluate(()=>{const res={hidden:[],overflow:0,anchors:[],broken:[]};
   res.overflow=document.documentElement.scrollWidth-window.innerWidth;
   for(const el of document.querySelectorAll('body *')){ if(el.closest('#waWidget,#vwCookie,.mobile-nav-panel,script,style,template,details:not([open]) > *:not(summary)'))continue;
     const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden')continue;
     if(parseFloat(cs.opacity)<0.05){const rc=el.getBoundingClientRect(); if(rc.width>60&&rc.height>30&&el.innerText&&el.innerText.trim().length>10) res.hidden.push((el.className||el.tagName).toString().slice(0,50)+': '+el.innerText.trim().slice(0,50));}}
   for(const a of document.querySelectorAll('a[href^="#"]')){const h=a.getAttribute('href').slice(1);if(h&&!document.getElementById(h))res.anchors.push(h);}
   for(const i of document.images){if(i.complete&&i.naturalWidth===0)res.broken.push(i.src);}
   return res;});
 if(r.hidden.length) issues.push(`${tag} ${u} HIDDEN ${[...new Set(r.hidden)].slice(0,4).join(' || ')}`);
 if(r.overflow>2) issues.push(`${tag} ${u} OVERFLOW-X ${r.overflow}px`);
 if(r.anchors.length) issues.push(`${tag} ${u} BAD-ANCHOR ${r.anchors.join(',')}`);
 if(r.broken.length) issues.push(`${tag} ${u} BROKEN-IMG ${r.broken.join(',')}`);
 if(tag==='D'){ await p.evaluate(()=>window.scrollTo(0,0)); await p.waitForTimeout(200);
   await p.screenshot({path:`${out}/qa.png`,fullPage:true});
   const blank=execSync(`python3 -c "
from PIL import Image,ImageStat
im=Image.open('${out}/qa.png').convert('L');w,h=im.size;s=[]
for y in range(0,h-450,450):
  st=ImageStat.Stat(im.crop((0,y,w,y+450))).stddev[0]
  if st<2.5: s.append(y)
print(s)"`).toString().trim(); if(blank!=='[]') issues.push(`D ${u} BLANK-AREA at y=${blank} (h=${TH})`);}
 await p.close();}}
console.log(issues.length?issues.join('\n'):'NO ISSUES');await b.close();})();
