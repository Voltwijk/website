// Zet de door JavaScript gerenderde productinhoud ook als statische HTML in
// product-*.html, zodat Google (en bezoekers) direct de inhoud zien en de
// pagina niet verspringt tijdens het laden.
// Gebruik: start een lokale server in de repo-root (poort 8765) en draai
//   node tools/prerender-products.js
// Draai dit opnieuw na elke wijziging aan PRODUCTS of de productlayout.
const fs = require('fs');
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
const ROOT = path.join(__dirname, '..');
const BASE = process.env.BASE || 'http://127.0.0.1:8765';
(async () => {
  const files = fs.readdirSync(ROOT).filter(f => /^product-.*\.html$/.test(f));
  const b = await chromium.launch();
  for (const f of files) {
    const file = path.join(ROOT, f);
    let src = fs.readFileSync(file, 'utf8');
    // eerst leegmaken, zodat we renderen vanuit de bron en niet vanuit een oude prerender
    src = src.replace(/<div id="view-product">[\s\S]*?<!--\/prerender--><\/div>/, '<div id="view-product"></div>');
    fs.writeFileSync(file, src);
    const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
    await p.route(/fonts\.(googleapis|gstatic)|trustindex/, r => r.abort());
    await p.goto(BASE + '/' + f.replace(/\.html$/, ''), { waitUntil: 'load' });
    await p.waitForSelector('#view-product > *');
    let html = await p.$eval('#view-product', el => el.innerHTML);
    await p.close();
    html = html.replace(/\s+is-visible/g, '').replace(/ class=""/g, '');
    src = src.replace('<div id="view-product"></div>', '<div id="view-product"><!--prerender-->' + html + '<!--/prerender--></div>');
    fs.writeFileSync(file, src);
    console.log('prerendered', f, html.length, 'bytes');
  }
  await b.close();
})();
