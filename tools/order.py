# Online bestellen vanuit de prijscalculator (stap 3 -> "Bestel direct").
# De klant vult gegevens in, doet een technische check (foto's uploaden of een videocheck) en kiest een
# installatiedatum. De aanvraag gaat naar Netlify Forms ("bestelling"); de bestelling is pas definitief na onze
# orderbevestiging. Daarna betaalt de klant de aanbetaling (via een betaallink), de rest na de installatie.
# Gebruik:  python3 tools/order.py          (uit: python3 tools/order.py uit)
# Installatiedatum:
#  - CAL = True: de klant kiest een echte dag in de Cal.com-agenda CAL_LINK (ma-vr, max. 3 per dag, pas na 6 dagen;
#    die regels staan in Cal.com). Na het boeken wordt de bestelling met die datum verstuurd.
#  - CAL = False: de klant kiest een voorkeursdag (werkdagen, vanaf DAGEN_VOORUIT), die wij bevestigen.
# SCHOUW: producten waarvoor we eerst komen kijken voordat de datum definitief is.
import glob, os, re, sys
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
OFF = len(sys.argv) > 1 and sys.argv[1] == 'uit'
AANBETALING = 350
DAGEN_VOORUIT = 6
DAGEN_KEUZE = 15
CAL = False
CAL_LINK = 'voltwijk/installatie'
SCHOUW = ['zonnepanelen', 'warmtepomp']

BLOCK = r'''<!-- vw-order:start -->
<form name="bestelling" data-netlify="true" netlify-honeypot="bot-field" hidden enctype="multipart/form-data">
  <input name="bot-field"><input name="ordernummer"><input name="naam"><input name="email"><input name="telefoon">
  <input name="adres"><input name="postcode"><input name="plaats"><input name="huistype"><input name="producten">
  <input name="prijsregels"><input name="totaalprijs"><input name="aanbetaling"><input name="installatiedatum"><input name="technische_check">
  <input type="file" name="foto_meterkast"><input type="file" name="foto_plek"><textarea name="opmerking"></textarea>
  <input name="akkoord"><input name="pagina">
</form>
<style>
.vwo-cta{margin-top:26px;padding:22px;border-radius:18px;border:2px solid var(--primary);background:#fff;}
.vwo-cta b.t{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:19px;color:var(--ink);}
.vwo-cta ul{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:6px;font-size:13.5px;color:var(--ink-soft);}
.vwo-cta li{display:flex;gap:8px;align-items:flex-start;}
.vwo-cta li:before{content:"✓";color:var(--primary);font-weight:800;}
.vwo-cta .btn-primary{width:100%;justify-content:center;white-space:normal;text-align:center;line-height:1.3;margin-top:16px;padding:15px 22px;font-size:15px;}
.vwo h3{font-size:24px;margin:10px 0 0;}
.vwo .sub{font-size:14px;color:var(--ink-soft);margin-top:6px;line-height:1.55;}
.vwo fieldset{border:none;padding:0;margin:26px 0 0;}
.vwo legend{display:flex;align-items:center;gap:10px;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:700;font-size:17px;color:var(--ink);padding:0;margin-bottom:12px;}
.vwo legend span{width:26px;height:26px;border-radius:999px;background:var(--primary);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:13px;}
.vwo .g2{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.vwo .g3{display:grid;grid-template-columns:2fr 1fr 1.3fr;gap:10px;margin-top:10px;}
.vwo input[type=text],.vwo input[type=email],.vwo input[type=tel],.vwo textarea{width:100%;box-sizing:border-box;border:1.5px solid var(--border);border-radius:12px;padding:12px 14px;font:inherit;font-size:14.5px;background:#fff;color:var(--ink);}
.vwo input:focus,.vwo textarea:focus{outline:2px solid var(--primary);outline-offset:1px;border-color:var(--primary);}
.vwo .g2 + .g2{margin-top:10px;}
.vwo-weeks{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;}
.vwo-weeks label,.vwo-chk label.opt{position:relative;display:block;cursor:pointer;}
.vwo-weeks input,.vwo-chk input[type=radio]{position:absolute;opacity:0;pointer-events:none;}
.vwo-weeks span{display:block;text-align:center;border:2px solid var(--border);border-radius:14px;padding:10px 6px;font-size:12.5px;color:var(--ink-soft);line-height:1.35;background:#fff;}
.vwo-weeks span b{display:block;font-size:14.5px;color:var(--ink);}
.vwo-weeks input:checked + span,.vwo-chk input:checked + span{border-color:var(--primary);background:var(--surface-tint);}
.vwo-weeks input:focus-visible + span,.vwo-chk input:focus-visible + span{outline:2px solid var(--primary);outline-offset:2px;}
.vwo-note{font-size:12.5px;color:var(--ink-faint);margin-top:8px;line-height:1.5;}
.vwo-chk{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.vwo-chk span{display:block;border:2px solid var(--border);border-radius:14px;padding:12px 14px;font-size:13px;color:var(--ink-soft);line-height:1.45;background:#fff;height:100%;box-sizing:border-box;}
.vwo-chk span b{display:block;font-size:14.5px;color:var(--ink);margin-bottom:2px;}
.vwo-files{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;}
.vwo-files label{display:flex;flex-direction:column;gap:6px;border:1.5px dashed #BFD3CF;border-radius:14px;padding:14px;font-size:13px;color:var(--ink-soft);cursor:pointer;background:#fff;}
.vwo-files label b{color:var(--ink);font-size:14px;}
.vwo-files input{font-size:12.5px;max-width:100%;}
.vwo-ok{display:flex;gap:10px;align-items:flex-start;font-size:13px;color:var(--ink-soft);line-height:1.5;margin-top:22px;}
.vwo-ok input{margin-top:3px;width:18px;height:18px;flex-shrink:0;accent-color:var(--primary);}
.vwo-ok a{color:var(--primary);font-weight:700;}
.vwo .btn-primary.go{width:100%;justify-content:center;white-space:normal;text-align:center;margin-top:18px;padding:16px 22px;font-size:15.5px;}
.vwo-back{background:none;border:none;color:var(--primary);font:inherit;font-weight:800;font-size:13.5px;cursor:pointer;padding:0;}
.vwo-pay{margin-top:14px;padding:14px 16px;border-radius:14px;background:var(--surface-tint);font-size:13.5px;color:var(--ink-soft);line-height:1.5;}
.vwo-pay b{color:var(--ink);}
.vwo-cal{min-height:520px;margin-top:16px;border:1px solid var(--border);border-radius:16px;overflow:hidden;background:#fff;position:relative;}
.vwo-err{font-size:13px;color:#C6402E;margin-top:10px;}
.vwo-done{text-align:left;}
.vwo-done .nr{display:inline-block;margin-top:10px;font-size:13px;font-weight:800;color:var(--primary);background:var(--pill-bg);border-radius:999px;padding:6px 12px;}
.vwo-steps{display:grid;gap:10px;margin-top:20px;}
.vwo-steps div{display:flex;gap:12px;align-items:flex-start;background:#fff;border:1px solid var(--border);border-radius:14px;padding:14px;font-size:14px;color:var(--ink-soft);line-height:1.5;}
.vwo-steps b{color:var(--ink);}
.vwo-steps i{font-style:normal;width:26px;height:26px;border-radius:999px;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800;flex-shrink:0;}
@media (max-width:640px){
  .vwo .g2,.vwo .g3,.vwo-chk,.vwo-files{grid-template-columns:1fr;}
  .vwo-weeks{grid-template-columns:repeat(3,minmax(0,1fr));}
}
</style>
<script>
(function(){
  if(typeof renderCalc !== 'function' || !document.getElementById('calcCard')) return;
  var MIN = __MIN__, N = __N__, SCHOUW = __SCHOUW__, PAY = __PAY__, CAL = __CAL__, CAL_LINK = '__CAL_LINK__';
  var DAG = ['zo','ma','di','wo','do','vr','za'], DAGL = ['zondag','maandag','dinsdag','woensdag','donderdag','vrijdag','zaterdag'];
  var MND = ['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'];
  var order = {};
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function days(){
    var d = new Date(); d.setHours(0,0,0,0); d.setDate(d.getDate() + MIN);
    var out = [];
    while(out.length < N){
      if(d.getDay() > 0 && d.getDay() < 6) out.push({d: DAG[d.getDay()], n: d.getDate() + ' ' + MND[d.getMonth()], val: DAGL[d.getDay()] + ' ' + d.getDate() + ' ' + MND[d.getMonth()] + ' ' + d.getFullYear()});
      d.setDate(d.getDate() + 1);
    }
    return out;
  }
  function fmtIso(iso){ var d = new Date(iso); return isNaN(d) ? iso : DAGL[d.getDay()] + ' ' + d.getDate() + ' ' + MND[d.getMonth()] + ' ' + d.getFullYear(); }
  function needsSchouw(){ return calcState.producten.some(function(p){ return SCHOUW.indexOf(p) > -1; }); }
  function prefill(k){
    if(order[k]) return order[k];
    var b = document.getElementById('leadCalc'); if(!b) return '';
    var el = b.querySelector(k === 'email' ? 'input[type=email]' : k === 'telefoon' ? 'input[type=tel]' : 'input[type=text]');
    return el ? el.value : '';
  }
  function ctaHtml(){
    var s = needsSchouw();
    return '<div class="vwo-cta"><b class="t">Direct bestellen</b><ul>' +
      '<li>Kies zelf je installatiedatum</li>' +
      '<li>Je betaalt nu niets. Na onze orderbevestiging betaal je € ' + PAY + ' aanbetaling, de rest pas na de installatie</li>' +
      '<li>' + (s ? 'Bij zonnepanelen en warmtepompen komen we eerst kort kijken; daarna ligt je datum vast' : 'Technische check via een paar foto’s of een korte videocall') + '</li>' +
      '</ul><button type="button" class="btn-primary" onclick="calcGoStep(4)">Bestel direct en kies je installatiedatum →</button></div>';
  }
  function formHtml(){
    var r = calcCompute(), wk = days(), s = needsSchouw();
    return '<div class="vwo"><button type="button" class="vwo-back" onclick="calcGoStep(3)">← Terug naar je prijs</button>' +
      '<h3 class="vw-heading">Bestel je installatie</h3>' +
      '<p class="sub">Totaal <b>€ ' + calcFmt(r.total) + '</b> inclusief installatie. Je betaalt nu niets: we checken je situatie en sturen binnen 1 werkdag je orderbevestiging.</p>' +
      '<form id="vwOrder" onsubmit="return vwOrderSubmit(this);" novalidate>' +
      '<fieldset><legend><span>1</span>Je gegevens</legend>' +
        '<div class="g2"><input type="text" name="naam" required placeholder="Voor- en achternaam" autocomplete="name" value="' + esc(prefill('naam')) + '"><input type="tel" name="telefoon" required placeholder="Telefoonnummer" autocomplete="tel" value="' + esc(prefill('telefoon')) + '"></div>' +
        '<input type="email" name="email" required placeholder="E-mailadres" autocomplete="email" style="margin-top:10px;" value="' + esc(prefill('email')) + '">' +
        '<div class="g3"><input type="text" name="adres" required placeholder="Straat en huisnummer" autocomplete="street-address" value="' + esc(order.adres) + '"><input type="text" name="postcode" required placeholder="Postcode" autocomplete="postal-code" value="' + esc(order.postcode || calcState.postcode) + '"><input type="text" name="plaats" required placeholder="Plaats" autocomplete="address-level2" value="' + esc(order.plaats) + '"></div>' +
      '</fieldset>' +
      (CAL ? '' : '<fieldset><legend><span>2</span>Kies je installatiedatum</legend><div class="vwo-weeks">' +
        wk.map(function(w, i){ return '<label><input type="radio" name="installatiedatum" value="' + esc(w.val) + '"' + ((order.installatiedatum ? order.installatiedatum === w.val : i === 0) ? ' checked' : '') + '><span><b>' + w.d + '</b>' + w.n + '</span></label>'; }).join('') +
        '</div><div class="vwo-note">' + (s ? 'Zonnepanelen of warmtepomp in je bestelling: we komen eerst kort kijken. Je gekozen dag houden we voor je vast.' : 'Je voorkeursdag. We bevestigen hem in je orderbevestiging.') + '</div>' +
      '</fieldset>') +
      '<fieldset><legend><span>' + (CAL ? 2 : 3) + '</span>Technische check</legend><div class="vwo-chk">' +
        '<label class="opt"><input type="radio" name="technische_check" value="Foto’s geüpload" ' + (order.technische_check !== 'Videocheck' ? 'checked' : '') + ' onchange="vwOrderChk(this)"><span><b>Foto’s uploaden</b>Van je meterkast en de plek waar het moet komen. Het snelst.</span></label>' +
        '<label class="opt"><input type="radio" name="technische_check" value="Videocheck" ' + (order.technische_check === 'Videocheck' ? 'checked' : '') + ' onchange="vwOrderChk(this)"><span><b>Korte videocheck</b>Je plant na het bestellen een videogesprek van 30 minuten.</span></label>' +
      '</div><div class="vwo-files"' + (order.technische_check === 'Videocheck' ? ' hidden' : '') + '>' +
        '<label><b>Foto van je meterkast</b>Deur open, hele kast in beeld<input type="file" name="foto_meterkast" accept="image/*"></label>' +
        '<label><b>Foto van de plek</b>Waar het product moet komen<input type="file" name="foto_plek" accept="image/*"></label>' +
      '</div></fieldset>' +
      '<fieldset><legend><span>' + (CAL ? 3 : 4) + '</span>Nog iets dat we moeten weten? <small style="font-weight:400;font-size:13px;color:var(--ink-faint);">(optioneel)</small></legend>' +
        '<textarea name="opmerking" rows="3" placeholder="Bijvoorbeeld: meterkast zit in de trapkast, of we hebben al 12 zonnepanelen.">' + esc(order.opmerking) + '</textarea></fieldset>' +
      '<input type="text" name="bot-field" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px;" aria-hidden="true">' +
      '<label class="vwo-ok"><input type="checkbox" name="akkoord" value="ja" required><span>Ik ga akkoord met de <a href="/algemene-voorwaarden" target="_blank">algemene voorwaarden</a> en het <a href="/privacybeleid" target="_blank">privacybeleid</a>. Mijn bestelling is pas definitief na de orderbevestiging van Voltwijk.</span></label>' +
      '<div class="vwo-pay"><b>Betalen:</b> nu niets. Na de orderbevestiging betaal je <b>€ ' + PAY + ' aanbetaling</b> via een iDEAL-betaallink. Het restant van € ' + calcFmt(Math.max(0, r.total - PAY)) + ' betaal je na de installatie.</div>' +
      '<button type="submit" class="btn-primary go">' + (CAL ? 'Volgende: kies je installatiedatum →' : 'Bestelling aanvragen →') + '</button>' +
      '<div class="vwo-note" style="text-align:center;">Je betaalt nu niets · bevestiging binnen 1 werkdag</div>' +
      '</form></div>';
  }
  function doneHtml(){
    var video = order.technische_check === 'Videocheck';
    return '<div class="vwo vwo-done"><div class="pill">Bestelling ontvangen</div><h3 class="vw-heading">Bedankt ' + esc((order.naam || '').split(' ')[0]) + ', we gaan voor je aan de slag!</h3>' +
      '<div class="nr">Ordernummer ' + esc(order.ordernummer) + '</div>' +
      '<p class="sub" style="margin-top:14px;">Je orderbevestiging sturen we naar ' + esc(order.email) + '. ' + (order.installatiedatum && order.installatiedatum !== 'In overleg' ? 'Installatie: <b>' + esc(order.installatiedatum) + '</b>.' : 'We plannen je installatiedatum samen met je in.') + '</p>' +
      '<div class="vwo-steps">' +
        '<div><i>1</i><span><b>Technische check.</b> ' + (video ? 'Plan hieronder je videocheck van 30 minuten.' : 'We bekijken je foto’s. Missen we iets, dan bellen of appen we je.') + '</span></div>' +
        '<div><i>2</i><span><b>Orderbevestiging binnen 1 werkdag,</b> met de betaallink voor je aanbetaling van € ' + PAY + '.</span></div>' +
        '<div><i>3</i><span><b>Installatie door ons eigen team.</b> Het restant betaal je pas als alles werkt.</span></div>' +
      '</div>' +
      (video ? '<button type="button" class="btn-primary" data-book="video" style="margin-top:18px;">Plan je videocheck →</button>' : '') +
      '<div style="margin-top:18px;font-size:13.5px;color:var(--ink-soft);">Vragen? Bel <a href="tel:+31853335687" style="color:var(--primary);font-weight:700;">085 333 56 87</a> of <a href="https://wa.me/31853335687" style="color:var(--primary);font-weight:700;">app ons</a>.</div></div>';
  }
  document.addEventListener('input', function(e){ var f = e.target.form; if(f && f.id === 'vwOrder'){ var er = f.querySelector('.vwo-err'); if(er) er.remove(); } });
  document.addEventListener('change', function(e){ var f = e.target.form; if(f && f.id === 'vwOrder'){ var er = f.querySelector('.vwo-err'); if(er) er.remove(); } });
  window.vwOrderChk = function(el){
    var f = el.form.querySelector('.vwo-files'); if(f) f.hidden = el.value === 'Videocheck';
  };
  function shrink(file){
    return new Promise(function(res){
      if(!file || !file.size) return res(null);
      if(!/^image\//.test(file.type) || file.size < 900000) return res(file);
      var img = new Image(), url = URL.createObjectURL(file);
      img.onload = function(){
        var s = Math.min(1, 1800 / Math.max(img.width, img.height)), c = document.createElement('canvas');
        c.width = Math.round(img.width * s); c.height = Math.round(img.height * s);
        c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url);
        c.toBlob(function(b){ res(b ? new File([b], file.name.replace(/\.\w+$/, '') + '.jpg', {type:'image/jpeg'}) : file); }, 'image/jpeg', 0.82);
      };
      img.onerror = function(){ res(file); };
      img.src = url;
    });
  }
  window.vwOrderSubmit = function(form){
    var err = form.querySelector('.vwo-err'); if(err) err.remove();
    var bad = [].filter.call(form.querySelectorAll('[required]'), function(el){ return el.type === 'checkbox' ? !el.checked : !el.value.trim() || (el.type === 'email' && !/^\S+@\S+\.\S+$/.test(el.value)); });
    if(bad.length){
      bad[0].focus();
      var e = document.createElement('div'); e.className = 'vwo-err';
      e.textContent = bad[0].type === 'checkbox' ? 'Vink het akkoord aan om je bestelling te versturen.' : 'Vul alle gegevens in (naam, telefoon, e-mail en adres).';
      form.querySelector('.go').insertAdjacentElement('afterend', e); return false;
    }
    [].forEach.call(form.elements, function(el){ if(el.name && el.type !== 'file' && (el.type !== 'radio' || el.checked)) order[el.name] = el.value.trim(); });
    order.files = order.technische_check === 'Videocheck' ? [] : ['foto_meterkast', 'foto_plek'].map(function(n){ var i = form.querySelector('input[name="' + n + '"]'); return {n: n, f: i && i.files[0]}; });
    if(CAL){ calcState.step = 5; renderCalc(); scrollCard(); return false; }
    send(form.querySelector('.go'));
    return false;
  };
  function scrollCard(){ var c = document.getElementById('calcCard'); if(c) c.scrollIntoView({behavior: 'smooth', block: 'start'}); }
  function send(btn){
    var r = calcCompute(), d = new Date();
    order.ordernummer = order.ordernummer || 'VW-' + String(d.getFullYear()).slice(2) + ('0' + (d.getMonth() + 1)).slice(-2) + ('0' + d.getDate()).slice(-2) + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();
    var fd = new FormData();
    fd.append('form-name', 'bestelling');
    ['ordernummer','naam','email','telefoon','adres','postcode','plaats','installatiedatum','technische_check','opmerking','akkoord','bot-field'].forEach(function(k){ fd.append(k, order[k] || ''); });
    var hs = (typeof CALC_HOUSE !== 'undefined' ? CALC_HOUSE : []).filter(function(h){ return h.id === calcState.huistype; })[0];
    fd.append('huistype', hs ? hs.label : (calcState.huistype || ''));
    fd.append('producten', r.items.map(function(it){ return it.label; }).join(', '));
    fd.append('prijsregels', r.items.map(function(it){ return it.label + ' € ' + calcFmt(it.price); }).concat(r.subsidie ? ['Subsidie warmtepomp −€ ' + calcFmt(r.subsidie)] : [], r.bundleKorting ? ['Bundelkorting −€ ' + calcFmt(r.bundleKorting)] : []).join(' | '));
    fd.append('totaalprijs', '€ ' + calcFmt(r.total));
    fd.append('aanbetaling', '€ ' + PAY);
    fd.append('pagina', location.pathname);
    var label = btn ? btn.innerHTML : ''; if(btn){ btn.disabled = true; btn.style.opacity = '.7'; btn.innerHTML = 'Versturen…'; }
    Promise.all((order.files || []).map(function(x){ return shrink(x.f).then(function(f){ if(f) fd.append(x.n, f, f.name); }); }))
      .then(function(){ return fetch('/', {method: 'POST', body: fd}); })
      .then(function(res){
        if(!res.ok) throw new Error(res.status);
        try{ if(window.vwTrack) vwTrack('bestelling_aangevraagd', {value: r.total, currency: 'EUR', producten: r.items.map(function(it){ return it.id; }).join(','), pagina: location.pathname}); }catch(e){}
        calcState.step = 6; renderCalc(); scrollCard();
      })
      .catch(function(){
        if(btn){ btn.disabled = false; btn.style.opacity = ''; btn.innerHTML = label; }
        var e = document.createElement('div'); e.className = 'vwo-err';
        e.innerHTML = 'Versturen lukte niet. Bel ons op <a href="tel:+31853335687" style="color:inherit;font-weight:700;">085 333 56 87</a> of app via <a href="https://wa.me/31853335687" style="color:inherit;font-weight:700;">WhatsApp</a>. Je gegevens zijn nog niet verstuurd.';
        var host = document.getElementById('calcCard'); var at = btn || (host && host.querySelector('.vwo h3'));
        if(at) at.insertAdjacentElement('afterend', e);
      });
  }
  function calHtml(){
    return '<div class="vwo"><button type="button" class="vwo-back" onclick="calcGoStep(4)">← Terug naar je gegevens</button>' +
      '<h3 class="vw-heading">Kies je installatiedatum</h3>' +
      '<p class="sub">Kies een dag die jou uitkomt (maandag t/m vrijdag). Zodra je een dag kiest, versturen we je bestelling.</p>' +
      '<div class="vwo-cal" id="vwoCal"><div class="vwb-load" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--ink-faint);font-weight:600;">Agenda laden…</div></div>' +
      '<div class="vwo-note">Lukt het kiezen niet? <button type="button" class="vwo-back" id="vwoSkip">Verstuur je bestelling zonder datum</button>, dan plannen we samen een dag in.</div></div>';
  }
  var calN = 0;
  function mountCal(){
    if(!window.Cal){
      (function (C, A, L) { var p = function (a, ar) { a.q.push(ar); }; var d = C.document; C.Cal = C.Cal || function () { var cal = C.Cal; var ar = arguments; if (!cal.loaded) { cal.ns = {}; cal.q = cal.q || []; d.head.appendChild(d.createElement("script")).src = A; cal.loaded = true; } if (ar[0] === L) { var api = function () { p(api, arguments); }; var namespace = ar[1]; api.q = api.q || []; if (typeof namespace === "string") { cal.ns[namespace] = cal.ns[namespace] || api; p(cal.ns[namespace], ar); p(cal, ["initNamespace", namespace]); } else p(cal, ar); return; } p(cal, ar); }; })(window, "https://app.cal.com/embed/embed.js", "init");
    }
    var ns = 'vwo' + (++calN), r = calcCompute(), sent = false;
    Cal('init', ns, {origin: 'https://cal.com'});
    Cal.ns[ns]('inline', {elementOrSelector: '#vwoCal', calLink: CAL_LINK, layout: 'month_view', config: {theme: 'light', name: order.naam || '', email: order.email || '',
      notes: 'Bestelling via website: ' + r.items.map(function(it){ return it.label; }).join(', ') + ' (totaal € ' + calcFmt(r.total) + '). Adres: ' + [order.adres, order.postcode, order.plaats].join(' ') + '. Tel: ' + (order.telefoon || '')}});
    Cal.ns[ns]('ui', {theme: 'light', layout: 'month_view', cssVarsPerTheme: {light: {'cal-brand': '#0F6E6B'}}});
    var done = function(e){
      if(sent) return; sent = true;
      var m = JSON.stringify((e && e.detail && e.detail.data) || {}).match(/\d{4}-\d{2}-\d{2}T[\d:.]+Z?/);
      order.installatiedatum = m ? fmtIso(m[0]) : 'Geboekt in Cal.com';
      try{ if(window.vwTrack) vwTrack('installatie_gepland', {pagina: location.pathname}); }catch(err){}
      send(null);
    };
    Cal.ns[ns]('on', {action: 'bookingSuccessfulV2', callback: done});
    Cal.ns[ns]('on', {action: 'bookingSuccessful', callback: done});
    Cal.ns[ns]('on', {action: 'linkReady', callback: function(){ var l = document.querySelector('#vwoCal .vwb-load'); if(l) l.remove(); }});
    var skip = document.getElementById('vwoSkip');
    if(skip) skip.addEventListener('click', function(){ order.installatiedatum = 'In overleg'; skip.disabled = true; send(null); });
  }
  var base = renderCalc;
  window.renderCalc = renderCalc = function(){
    var card = document.getElementById('calcCard');
    if(calcState.step >= 4 && card){
      if(!calcState.producten.length){ calcState.step = 2; return base(); }
      base.call(this, 3);
      var left = card.querySelector('.calc-grid > div');
      if(left) left.innerHTML = calcState.step === 6 ? doneHtml() : calcState.step === 5 ? calHtml() : formHtml();
      if(calcState.step === 5) mountCal();
      return;
    }
    base();
    if(calcState.step === 3 && card){
      var box = card.querySelector('#leadCalc'); box = box && box.parentNode;
      if(box && !card.querySelector('.vwo-cta')){
        box.insertAdjacentHTML('beforebegin', ctaHtml());
        var h = box.querySelector('.vw-heading'); if(h) h.textContent = 'Liever eerst een offerte?';
      }
    }
  };
  // Kaart opnieuw tekenen zodat de bestelknop ook meteen verschijnt als stap 3 al openstaat
  if(calcState.step === 3) renderCalc();
})();
</script>
<!-- vw-order:end -->'''

BLOCK = (BLOCK.replace('__MIN__', str(DAGEN_VOORUIT)).replace('__N__', str(DAGEN_KEUZE)).replace('__SCHOUW__', repr(SCHOUW))
         .replace('__PAY__', str(AANBETALING)).replace('__CAL__', 'true' if CAL else 'false').replace('__CAL_LINK__', CAL_LINK))

n = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    s2 = re.sub(r'\n?<!-- vw-order:start -->.*?<!-- vw-order:end -->', '', s, flags=re.S)
    if not OFF and 'id="calcCard"' in s2:
        s2 = s2.rstrip('\n') + '\n' + BLOCK + '\n'
    if s2 != s: open(f, 'w', encoding='utf-8').write(s2); n += 1
print(('Online bestellen verwijderd van' if OFF else 'Online bestellen op'), n, "pagina's")
