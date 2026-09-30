// Maakt alle downloadbestanden van het brandbook (/merk/kit): print-PDF's, PNG-voorbeelden en logo-PNG's.
// Start eerst een lokale server op de repo-root (poort 8765), dan: node tools/brandkit/render.cjs
const { chromium } = (() => { try { return require('playwright'); } catch (e) { return require('/opt/node22/lib/node_modules/playwright'); } })();
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..'), KIT = path.join(ROOT, 'merk', 'kit');
const BASE = process.env.BASE || 'http://127.0.0.1:8765';
const out = (...p) => path.join(KIT, ...p);

(async () => {
  const b = await chromium.launch();
  const ready = async (p) => { await p.waitForSelector('[data-ready]', { timeout: 20000 }); };

  // 1. Brochure en flyer: print-PDF met 3 mm afloop + JPG per pagina
  for (const [file, name, dir] of [['brochure.html', 'voltwijk-brochure-a5', 'brochure'], ['flyer.html', 'voltwijk-flyer-thuisbatterij-a5', 'flyer']]) {
    const p = await b.newPage({ viewport: { width: 640, height: 900 }, deviceScaleFactor: 2.4 });
    await p.goto(`${BASE}/merk/${file}`); await ready(p);
    const pgs = await p.$$('.pg');
    for (let i = 0; i < pgs.length; i++) await pgs[i].screenshot({ path: out(dir, `${name}-pagina-${i + 1}.jpg`), type: 'jpeg', quality: 88 });
    await p.pdf({ path: out(dir, `${name}-drukklaar.pdf`), width: '154mm', height: '216mm', printBackground: true, preferCSSPageSize: true });
    await p.close();
  }

  // 2. Visitekaartjes: drukklare PDF (voor + achter, 3 mm afloop) en PNG's met ronde hoeken
  const team = 'naam=Team%20Voltwijk&functie=Advies%20en%20installatie';
  for (const v of ['a', 'b', 'c']) {
    const p = await b.newPage({ viewport: { width: 800, height: 600 } });
    await p.goto(`${BASE}/merk/render-kaartjes.html?v=${v}&print=1&b=3&${team}`); await ready(p);
    await p.pdf({ path: out('visitekaartjes', `voltwijk-visitekaartje-${v}-drukklaar.pdf`), width: '91mm', height: '61mm', printBackground: true, preferCSSPageSize: true });
    await p.close();
    for (const side of ['front', 'back']) {
      const q = await b.newPage({ viewport: { width: 800, height: 600 }, deviceScaleFactor: 4 });
      await q.goto(`${BASE}/merk/render-kaartjes.html?v=${v}&side=${side}&${team}`); await ready(q);
      await (await q.$('.vwc')).screenshot({ path: out('visitekaartjes', `voltwijk-visitekaartje-${v}-${side === 'front' ? 'voor' : 'achter'}.png`), omitBackground: true });
      await q.close();
    }
  }

  // 3. Logo's als PNG (transparant), in twee formaten
  const logos = fs.readdirSync(out('logo')).filter(f => f.endsWith('.svg'));
  for (const f of logos) {
    const svg = fs.readFileSync(out('logo', f), 'utf8');
    const wide = !/beeldmerk|icoon/.test(f);
    for (const w of wide ? [800, 2400] : [512, 1500]) {
      const p = await b.newPage({ viewport: { width: w + 40, height: w + 40 } });
      await p.setContent(`<html><body style="margin:0;background:transparent"><div id="l" style="width:${w}px;line-height:0">${svg.replace('<svg', '<svg width="100%" style="display:block;height:auto"')}</div></body></html>`);
      await (await p.$('#l')).screenshot({ path: out('logo', f.replace('.svg', `-${w}px.png`)), omitBackground: true });
      await p.close();
    }
  }

  // 4. Logo voor de e-mailhandtekening (150 x 24 px weergave, 2x scherp)
  {
    const svg = fs.readFileSync(out('logo', 'voltwijk-logo-kleur.svg'), 'utf8');
    const p = await b.newPage({ viewport: { width: 400, height: 100 }, deviceScaleFactor: 2 });
    await p.setContent(`<html><body style="margin:0;background:transparent"><div id="l" style="width:150px;height:24px;display:flex;align-items:center">${svg.replace('<svg', '<svg width="150" style="display:block;height:auto"')}</div></body></html>`);
    await (await p.$('#l')).screenshot({ path: out('mail', 'voltwijk-logo-mail.png'), omitBackground: true });
    await p.close();
  }
  await b.close();
  console.log('Merkkit bijgewerkt in merk/kit');
})().catch(e => { console.error(e); process.exit(1); });
