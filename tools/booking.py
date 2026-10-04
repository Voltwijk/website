# Een gesprek plannen op de hele site, aangesloten op het Voltwijk CRM (geen Cal.com meer).
# - Elke link of knop met data-book="huis|bel|scan" (of leeg) opent een venster:
#   postcode -> per regio de juiste vorm (zelfde regel als het CRM en de welkomstmail):
#     thuisregio  = adviseur aan huis; de klant geeft alleen een voorkeur (ochtend, middag of flexibel), wij stellen momenten voor;
#     daarbuiten  = telefonisch adviesgesprek; de klant kiest direct een dagdeel op de eerstvolgende werkdagen;
#   -> naam, telefoon, e-mail -> Netlify-formulier 'gesprek' -> via de webhook als lead in het CRM.
# - Na een verstuurd formulier (batterijcalculator, offerte, contact) komt hetzelfde keuzeblok in de bevestiging: één tik stuurt
#   het formulier 'voorkeur', dat het CRM bij de bestaande aanvraag zet. Gebruik: window.vwVoorkeur(element, gegevens).
# - Thuisregio: tools/thuisregio.txt (kopie van public/assets/thuisregio.js in het CRM; daar opnieuw maken met scripts/thuisregio.mjs).
# - Een aanvraag wordt in Google Analytics gemeten als 'afspraak_gepland' (alleen met toestemming).
# Gebruik:  python3 tools/booking.py        (uit = python3 tools/booking.py uit)
import glob, os, re, sys
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
OFF = len(sys.argv) > 1 and sys.argv[1] == 'uit'
REGIO = open('tools/thuisregio.txt', encoding='utf-8').read().strip()
assert re.fullmatch(r'[\d,-]+', REGIO), 'tools/thuisregio.txt klopt niet'

ICONS = {
    'huis': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/></svg>',
    'bel': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    'wa': '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2.1-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5 2.5 1 3 .8 3.6.7.6-.1 1.8-.7 2-1.5.2-.7.2-1.4.2-1.5-.1-.1-.3-.2-.6-.3zM12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2z"/></svg>',
}
JS_ICONS = ','.join("%s:'%s'" % (k, v) for k, v in ICONS.items())

BLOCK = '''<!-- vw-cal:start -->
<style>
.vwb-ov{position:fixed;inset:0;z-index:9999;background:rgba(8,32,31,.62);display:flex;align-items:center;justify-content:center;padding:20px;opacity:0;transition:opacity .2s;}
.vwb-ov.open{opacity:1;}
.vwb-panel{background:#fff;border-radius:24px;width:100%;max-width:620px;max-height:calc(100vh - 40px);display:flex;flex-direction:column;overflow:hidden;box-shadow:0 40px 90px -30px rgba(0,0,0,.55);}
.vwb-head{display:flex;align-items:center;gap:14px;padding:18px 22px;border-bottom:1px solid #E6ECEA;}
.vwb-head b{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:19px;color:#10201F;flex:1;line-height:1.25;}
.vwb-x{background:#F1F5F4;border:none;border-radius:999px;cursor:pointer;color:#10201F;width:38px;height:38px;font-size:22px;line-height:1;flex-shrink:0;}
.vwb-body{overflow:auto;flex:1 1 auto;min-height:0;-webkit-overflow-scrolling:touch;padding:24px 24px 26px;font-family:'Nunito Sans',system-ui,sans-serif;color:#233532;}
.vwg h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:22px;line-height:1.2;color:#10201F;margin:0 0 6px;letter-spacing:-.01em;}
.vwg p{margin:0 0 16px;font-size:15px;line-height:1.55;color:#3F4F4C;}
.vwg .vwg-eb{display:inline-block;font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#0F6E6B;background:#D6EAE8;border-radius:999px;padding:4px 10px;margin-bottom:12px;}
.vwg-chips{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:4px 0 14px;}
.vwg-chips.n4{grid-template-columns:repeat(2,minmax(0,1fr));}
.vwg-chip{display:flex;flex-direction:column;align-items:center;gap:2px;padding:14px 8px;border-radius:16px;border:2px solid #D5E3E0;background:#fff;cursor:pointer;font-family:inherit;color:#10201F;transition:border-color .15s,transform .15s,box-shadow .15s;}
.vwg-chip:hover,.vwg-chip:focus-visible{border-color:#0F6E6B;transform:translateY(-2px);box-shadow:0 14px 28px -20px rgba(15,110,107,.8);outline:none;}
.vwg-chip b{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:16px;}
.vwg-chip span{font-size:12.5px;color:#5B6A67;}
.vwg-chip[aria-pressed="true"]{border-color:#0F6E6B;background:#EAF5F3;}
.vwg-alt{background:none;border:none;padding:0;color:#0F6E6B;font:800 14px 'Nunito Sans',system-ui,sans-serif;cursor:pointer;text-decoration:underline;text-underline-offset:3px;}
.vwg-f{display:grid;gap:12px;margin:6px 0 14px;}
.vwg-f label{display:grid;gap:5px;font-size:13.5px;font-weight:800;color:#10201F;}
.vwg-f input,.vwg-f textarea{font:16px 'Nunito Sans',system-ui,sans-serif;padding:12px 14px;border:1.5px solid #CFDCD9;border-radius:12px;color:#10201F;background:#fff;width:100%;box-sizing:border-box;}
.vwg-f input:focus,.vwg-f textarea:focus{outline:none;border-color:#0F6E6B;box-shadow:0 0 0 3px rgba(15,110,107,.15);}
.vwg-row{display:grid;grid-template-columns:1fr 120px;gap:10px;}
.vwg-go{width:100%;border:none;border-radius:999px;background:#0F6E6B;color:#fff;font:800 15.5px 'Nunito Sans',system-ui,sans-serif;padding:15px 20px;cursor:pointer;}
.vwg-go:hover{background:#0B5956;}
.vwg-go:disabled{opacity:.6;cursor:default;}
.vwg-err{color:#B42318;font-size:14px;font-weight:700;margin:-4px 0 12px;}
.vwg-sum{display:flex;gap:10px;align-items:center;background:#F3EFE6;border-radius:14px;padding:12px 14px;margin:0 0 16px;font-size:14px;color:#10201F;}
.vwg-sum b{font-weight:800;}
.vwg-sum button{margin-left:auto;}
.vwg-wa{display:flex;align-items:center;gap:10px;margin-top:14px;padding:12px 14px;border-radius:14px;background:#EAF8EF;color:#10201F;text-decoration:none;font-size:14px;line-height:1.4;}
.vwg-wa svg{color:#1FA855;flex-shrink:0;}
.vwg-wa b{font-weight:800;}
.vwg-small{font-size:12.5px;color:#6B7A77;margin:12px 0 0;text-align:center;}
.vwg-ok{text-align:center;padding:10px 0 4px;}
.vwg-ok .vwg-tick{width:56px;height:56px;border-radius:999px;background:#0F6E6B;color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:10px;}
.vwg-steps{display:grid;gap:10px;text-align:left;margin:16px 0 0;}
.vwg-steps div{display:flex;gap:12px;align-items:flex-start;font-size:14.5px;line-height:1.5;}
.vwg-steps i{font-style:normal;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:700;color:#0F6E6B;font-size:18px;min-width:26px;}
.vwb-after{margin-top:14px;padding:18px;border-radius:18px;background:#fff;border:1px solid #E6ECEA;text-align:left;width:100%;box-sizing:border-box;}
.vwb-after .vwg h3{font-size:19px;}
.vwb-btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}
.vwb-pre{margin-top:18px;}
.vwb-pre b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:16px;color:#10201F;}
.vwb-pre small{display:block;font-size:13px;color:#54615F;margin-top:4px;}
.vwb-btns button{display:inline-flex;align-items:center;gap:7px;border:2px solid #0F6E6B;background:#fff;color:#0F6E6B;border-radius:999px;padding:9px 14px;font:800 13.5px 'Nunito Sans',system-ui,sans-serif;cursor:pointer;}
.vwb-btns button:first-child{background:#0F6E6B;color:#fff;}
.vwb-btns svg{width:17px;height:17px;}
body.vwb-lock{overflow:hidden;}
@media (max-width:720px){
  .vwb-ov{padding:0;align-items:stretch;}
  .vwb-panel{max-height:none;height:100%;border-radius:0;}
  .vwb-head{padding:14px 16px;}
  .vwb-body{padding:20px 16px;}
  .vwg-chips{grid-template-columns:1fr 1fr;}
  .vwg-chips .vwg-chip:last-child:nth-child(odd){grid-column:1 / -1;}
  .vwb-btns button{flex:1 1 100%;justify-content:center;}
}
</style>
<script>
(function(){
  var REGIO = '__REGIO__', IC = {__ICONS__}, WA = '31853335687', lead = {}, ov = null;
  var DAG = ['zondag','maandag','dinsdag','woensdag','donderdag','vrijdag','zaterdag'];
  function esc(s){ return String(s||'').replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function track(name, p){ try{ if(window.vwTrack) vwTrack(name, p); }catch(e){} }
  function pc4(pc){ var m = /^(\\d{4})/.exec(String(pc||'').replace(/\\s/g,'')); return m ? +m[1] : 0; }
  /* Zelfde regel als het CRM: binnen 50 km van Zevenbergen of 40 km van Capelle a/d IJssel = adviseur aan huis */
  function regio(pc){ var n = pc4(pc); if(!n) return ''; return REGIO.split(',').some(function(x){ var r = x.split('-'), a = +r[0], b = +(r[1] || r[0]); return n >= a && n <= b; }) ? 'thuis' : 'telefonisch'; }
  function product(){ var m = /(batterij|zonnepanelen|warmtepomp|airco|boiler|laadpaal|meterkast|energiescan)/.exec(location.pathname); return m ? (m[1] === 'batterij' ? 'thuisbatterij' : m[1]) : ''; }
  function werkdagen(n){ var d = new Date(), uit = []; d.setHours(12,0,0,0);
    while(uit.length < n){ d.setDate(d.getDate() + 1); if(d.getDay() % 6){ var morgen = uit.length === 0 && (d - new Date()) < 2 * 864e5;
      uit.push({kort: morgen ? 'Morgen' : DAG[d.getDay()].charAt(0).toUpperCase() + DAG[d.getDay()].slice(1), lang: (morgen ? 'morgen ' : '') + DAG[d.getDay()] + ' ' + d.getDate() + '/' + (d.getMonth() + 1)}); } }
    return uit; }
  // Onthoud gegevens uit een verstuurd formulier, zodat we ze niet opnieuw vragen.
  document.addEventListener('submit', function(e){
    var f = e.target; if(!f || !f.querySelectorAll || (f.closest && f.closest('.vwg'))) return;
    f.querySelectorAll('input,textarea').forEach(function(el){
      if(el.type === 'hidden' || el.name === 'bot-field' || !el.value) return;
      var k = el.name || ({email:'email', tel:'telefoon', text:'naam'})[el.type];
      if(k === 'naam' || k === 'email' || k === 'telefoon' || k === 'postcode' || k === 'huisnummer') lead[k] = el.value.trim();
    });
  }, true);
  function post(naam, velden){
    var v = Object.assign({'form-name': naam, 'bot-field': '', pagina: location.pathname, product: product()}, velden);
    var bd = Object.keys(v).map(function(k){ return encodeURIComponent(k) + '=' + encodeURIComponent(v[k] == null ? '' : v[k]); }).join('&');
    return fetch('/', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:bd}).then(function(r){ if(!r.ok) throw new Error(r.status); });
  }
  function waLink(t){ return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(t); }

  /* ---------- het planblok (in het venster of in een bevestiging) ---------- */
  function Plan(el, o){
    var s = {stap: '', vorm: '', voorkeur: '', k: o.k || '', na: !!o.na, info: Object.assign({}, lead, o.info || {})};
    function keuzeVorm(){ var r = regio(s.info.postcode); if(s.k === 'bel') return 'telefonisch'; if(s.k === 'huis' || s.k === 'scan') return r === 'telefonisch' ? 'buiten' : 'thuis'; return r === 'telefonisch' ? 'telefonisch' : 'thuis'; }
    function render(){
      var h = '';
      if(s.stap === 'postcode'){
        h = '<span class="vwg-eb">Gratis &amp; vrijblijvend</span><h3>' + (s.k === 'scan' ? 'Plan je gratis energiescan' : 'Plan je gratis adviesgesprek') + '</h3><p>Vul je postcode in. Dan zie je meteen of een adviseur bij je langskomt of dat we je bellen.</p>' +
          '<form class="vwg-f" data-vwp="pc" novalidate><div class="vwg-row"><label>Postcode<input name="postcode" autocomplete="postal-code" placeholder="1234 AB" value="' + esc(s.info.postcode) + '" required></label><label>Huisnr.<input name="huisnummer" inputmode="numeric" value="' + esc(s.info.huisnummer) + '"></label></div>' +
          '<div class="vwg-err" hidden></div><button type="submit" class="vwg-go">Verder →</button></form>';
      } else if(s.stap === 'keuze'){
        var thuis = s.vorm === 'thuis', buiten = s.vorm === 'buiten';
        if(thuis) h = '<span class="vwg-eb">' + (s.na ? 'Nog één ding' : 'Adviseur aan huis') + '</span><h3>' + (s.k === 'scan' ? 'Wanneer komt de energiescan jou uit?' : 'Wanneer komt een adviseur jou het best uit?') + '</h3>' +
          '<p>Een adviseur komt bij je langs en kijkt samen met jou naar je woning, meterkast en verbruik (ongeveer een uur). Geef je voorkeur door: wij stellen een paar momenten voor.</p>' +
          '<div class="vwg-chips">' + [['Ochtend','9:00 – 12:00'],['Middag','12:00 – 17:00'],['Flexibel','elk moment']].map(function(c){ return '<button type="button" class="vwg-chip" data-vwp-k="' + c[0] + '"><b>' + c[0] + '</b><span>' + c[1] + '</span></button>'; }).join('') + '</div>' +
          (s.k === 'scan' ? '' : '<button type="button" class="vwg-alt" data-vwp="tel">Liever telefonisch? Dan bellen we je</button>');
        else {
          var w = werkdagen(2);
          h = '<span class="vwg-eb">' + (s.na ? 'Nog één ding' : 'Telefonisch adviesgesprek') + '</span><h3>Wanneer zullen we je bellen?</h3>' +
            (buiten ? '<p>Je woont net buiten de regio waar onze adviseurs langskomen. Geen probleem: we doen het adviesgesprek telefonisch. Net zo compleet, en daarna krijg je je plan met vaste prijs.</p>'
              : '<p>Een adviseur belt je en neemt in een half uur je situatie door. Daarna krijg je je persoonlijke plan met vaste prijs. Kies een moment:</p>') +
            '<div class="vwg-chips n4">' + [[w[0],'ochtend'],[w[0],'middag'],[w[1],'ochtend'],[w[1],'middag']].map(function(c){ return '<button type="button" class="vwg-chip" data-vwp-k="' + esc(c[0].lang + ', ' + c[1]) + '"><b>' + c[0].kort + '</b><span>' + c[1] + '</span></button>'; }).join('') + '</div>' +
            '<button type="button" class="vwg-alt" data-vwp="ander">Ander moment?</button>' + (s.vorm === 'telefonisch' && regio(s.info.postcode) === 'thuis' ? ' &nbsp;·&nbsp; <button type="button" class="vwg-alt" data-vwp="huis">Liever een adviseur aan huis</button>' : '');
        }
        h += '<a class="vwg-wa" href="' + waLink('Hallo Voltwijk! ' + (s.info.naam ? 'Ik ben ' + s.info.naam + '. ' : '') + 'Ik wil graag een adviesgesprek plannen. Het beste kan ik op: ') + '" target="_blank" rel="noopener">' + IC.wa + '<span><b>Liever via WhatsApp?</b> App ons, dan plannen we het samen.</span></a>';
      } else if(s.stap === 'ander'){
        h = '<h3>Welk moment past jou?</h3><p>Schrijf het op zoals je wilt, bijvoorbeeld "dinsdag na 18:00" of "liefst in de lunchpauze".</p>' +
          '<form class="vwg-f" data-vwp="ander" novalidate><label>Jouw moment<input name="moment" placeholder="Bijv. donderdag na 17:00" required></label><div class="vwg-err" hidden></div><button type="submit" class="vwg-go">Verder →</button></form>';
      } else if(s.stap === 'gegevens'){
        h = '<div class="vwg-sum">' + (s.vorm === 'thuis' ? IC.huis : IC.bel) + '<span><b>' + (s.vorm === 'thuis' ? (s.k === 'scan' ? 'Energiescan aan huis' : 'Adviseur aan huis') : 'We bellen je') + '</b> · ' + esc(s.voorkeur) + '</span><button type="button" class="vwg-alt" data-vwp="terug">Wijzig</button></div>' +
          '<h3>Bijna klaar</h3><p>Waar kunnen we je bereiken? Je krijgt direct een bevestiging per mail.</p>' +
          '<form class="vwg-f" data-vwp="geg" novalidate><p hidden><label>Niet invullen <input name="bot-field"></label></p><label>Naam<input name="naam" autocomplete="name" value="' + esc(s.info.naam) + '" required></label>' +
          '<label>Telefoonnummer<input name="telefoon" type="tel" autocomplete="tel" inputmode="tel" value="' + esc(s.info.telefoon) + '" required></label>' +
          '<label>E-mailadres<input name="email" type="email" autocomplete="email" value="' + esc(s.info.email) + '" required></label>' +
          '<div class="vwg-err" hidden></div><button type="submit" class="vwg-go">Gesprek aanvragen →</button></form><p class="vwg-small">Gratis en vrijblijvend. We gebruiken je gegevens alleen voor deze aanvraag (<a href="/privacybeleid" style="color:inherit;">privacybeleid</a>).</p>';
      } else if(s.stap === 'klaar'){
        var vn = String(s.info.naam || '').split(' ')[0], th = s.vorm === 'thuis';
        h = '<div class="vwg-ok"><div class="vwg-tick">✓</div><h3>' + (vn ? 'Top, ' + esc(vn) + '!' : 'Top!') + ' We hebben je voorkeur.</h3><p style="margin:0;">' + (th ? 'Binnen één werkdag krijg je van ons een voorstel met een paar momenten. Kies er één en het staat vast.' : 'We bellen je ' + esc(s.voorkeur) + '. Je krijgt een bevestiging per mail.') + '</p></div>' +
          '<div class="vwg-steps"><div><i>01</i><span>' + (th ? 'Wij stellen momenten voor en jij kiest. Je krijgt een bevestiging met alles op een rij.' : 'We bellen je op het gekozen moment. Duurt ongeveer een half uur.') + '</span></div>' +
          '<div><i>02</i><span>Tip: leg je jaarafrekening van stroom en gas klaar. Dan rekenen we met jouw cijfers.</span></div>' +
          '<div><i>03</i><span>Na het gesprek krijg je je persoonlijke plan met vaste prijs. Je zit nergens aan vast.</span></div></div>' +
          '<a class="vwg-wa" href="' + waLink('Hallo Voltwijk! ' + (s.info.naam ? 'Ik ben ' + s.info.naam + '. ' : '') + 'Hier alvast een foto van mijn meterkast:') + '" target="_blank" rel="noopener">' + IC.wa + '<span><b>Nog sneller?</b> Stuur alvast een foto van je meterkast via WhatsApp.</span></a>';
      }
      el.innerHTML = '<div class="vwg">' + h + '</div>';
      var f = el.querySelector('form input:not([type=hidden])'); if(f && !o.inline) setTimeout(function(){ try{ f.focus(); }catch(e){} }, 50);
    }
    function fout(msg){ var e = el.querySelector('.vwg-err'); if(e){ e.textContent = msg; e.hidden = !msg; } }
    function versturen(btn){
      var vorm = s.vorm === 'thuis' ? (s.k === 'scan' ? 'Energiescan aan huis' : 'Adviseur aan huis') : 'Telefonisch adviesgesprek';
      var velden = {naam: s.info.naam, email: s.info.email, telefoon: s.info.telefoon, postcode: s.info.postcode || '', huisnummer: s.info.huisnummer || '', gesprek: vorm, voorkeur: s.voorkeur};
      if(btn){ btn.disabled = true; btn.textContent = 'Versturen…'; }
      post(s.na ? 'voorkeur' : 'gesprek', velden).then(function(){
        track('afspraak_gepland', {soort: s.vorm === 'thuis' ? 'huis' : 'bel', pagina: location.pathname}); s.stap = 'klaar'; render();
      }).catch(function(){ if(btn){ btn.disabled = false; btn.textContent = 'Opnieuw proberen'; } fout('Versturen lukte niet. Bel ons op 085 333 56 87 of app via WhatsApp.'); });
    }
    function gekozen(v){
      s.voorkeur = v;
      if(s.na && (s.info.email || s.info.telefoon)){ el.querySelectorAll('.vwg-chip').forEach(function(c){ c.disabled = true; c.setAttribute('aria-pressed', String(c.getAttribute('data-vwp-k') === v)); }); versturen(null); }
      else { s.stap = 'gegevens'; render(); }
    }
    el.addEventListener('click', function(e){
      var c = e.target.closest('[data-vwp-k]'); if(c){ gekozen(c.getAttribute('data-vwp-k')); return; }
      var a = e.target.closest('[data-vwp]'); if(!a || a.tagName === 'FORM') return;
      var w = a.getAttribute('data-vwp');
      if(w === 'tel'){ s.vorm = 'telefonisch'; s.stap = 'keuze'; render(); }
      else if(w === 'huis'){ s.vorm = 'thuis'; s.stap = 'keuze'; render(); }
      else if(w === 'ander'){ s.stap = 'ander'; render(); }
      else if(w === 'terug'){ s.stap = 'keuze'; render(); }
    });
    el.addEventListener('submit', function(e){
      var f = e.target.closest('form[data-vwp]'); if(!f) return; e.preventDefault();
      var v = function(n){ return f.elements[n] ? String(f.elements[n].value || '').trim() : ''; }, w = f.getAttribute('data-vwp');
      if(w === 'pc'){ var pc = v('postcode').toUpperCase().replace(/\\s+/g, ''); if(!/^\\d{4}([A-Z]{2})?$/.test(pc)){ fout('Vul je postcode in, bijvoorbeeld 4761 AB.'); return; }
        s.info.postcode = pc.length === 6 ? pc.slice(0,4) + ' ' + pc.slice(4) : pc; s.info.huisnummer = v('huisnummer'); lead.postcode = s.info.postcode; lead.huisnummer = s.info.huisnummer;
        s.vorm = keuzeVorm(); s.stap = 'keuze'; track('afspraak_regio', {regio: regio(s.info.postcode)}); render(); }
      else if(w === 'ander'){ if(!v('moment')){ fout('Schrijf een moment op.'); return; } gekozen(v('moment')); }
      else if(w === 'geg'){
        if(v('bot-field')) return;
        var m = !v('naam') ? 'Vul je naam in.' : !/^[+0-9 ()-]{10,}$/.test(v('telefoon')) ? 'Vul een geldig telefoonnummer in.' : !/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(v('email')) ? 'Vul een geldig e-mailadres in.' : '';
        if(m){ fout(m); return; } fout('');
        s.info.naam = lead.naam = v('naam'); s.info.telefoon = lead.telefoon = v('telefoon'); s.info.email = lead.email = v('email');
        versturen(f.querySelector('.vwg-go'));
      }
    });
    s.vorm = keuzeVorm();
    s.stap = (s.k === 'bel' || s.info.postcode) ? 'keuze' : 'postcode';
    render();
  }

  /* ---------- venster ---------- */
  function close(){ if(!ov) return; ov.classList.remove('open'); document.body.classList.remove('vwb-lock'); var o = ov; ov = null; setTimeout(function(){ o.remove(); }, 200); }
  function open(k){
    if(k === 'video') k = 'bel';
    if(!ov){
      ov = document.createElement('div'); ov.className = 'vwb-ov';
      ov.innerHTML = '<div class="vwb-panel" role="dialog" aria-modal="true" aria-labelledby="vwbTitle"><div class="vwb-head"><b id="vwbTitle"></b><button type="button" class="vwb-x" aria-label="Sluiten">×</button></div><div class="vwb-body"></div></div>';
      ov.addEventListener('click', function(e){ if(e.target === ov || e.target.closest('.vwb-x')) close(); });
      document.body.appendChild(ov); document.body.classList.add('vwb-lock');
      requestAnimationFrame(function(){ ov && ov.classList.add('open'); });
    }
    ov.querySelector('#vwbTitle').textContent = k === 'scan' ? 'Gratis energiescan' : 'Gratis adviesgesprek';
    var body = ov.querySelector('.vwb-body'), n = body.cloneNode(false); body.replaceWith(n);
    Plan(n, {k: k || ''});
    track('afspraak_start', {soort: k || 'kies', pagina: location.pathname});
  }
  window.vwBook = open;
  /* Na een verstuurde aanvraag: keuzeblok in de bevestiging. info = {naam, email, telefoon, postcode, huisnummer} */
  window.vwVoorkeur = function(el, info){ if(!el) return; Object.assign(lead, info || {}); Plan(el, {na: true, inline: true, info: info || {}}); };
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') close(); });
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('[data-book]'); if(!a) return;
    e.preventDefault(); open(a.getAttribute('data-book'));
  });
  // Na een verstuurde offerte- of contactaanvraag: direct de voorkeur voor het gesprek laten kiezen.
  function addAfter(block){
    if(block.querySelector('.vwb-after') || !/^(leadCalc|leadContact)$/.test(block.id)) return;
    var s = block.querySelector('.lead-success'); if(!s) return;
    var d = document.createElement('div'); d.className = 'vwb-after';
    s.style.flexWrap = 'wrap'; s.appendChild(d); window.vwVoorkeur(d, {});
  }
  // In de oude prijscalculator: direct (ook zonder formulier) een gesprek kunnen aanvragen.
  function addPre(){
    var b = document.getElementById('leadCalc');
    if(!b || b.getAttribute('data-sent') === '1' || b.querySelector('.vwb-pre')) return;
    var d = document.createElement('div'); d.className = 'vwb-after vwb-pre';
    d.innerHTML = '<b>Liever eerst even praten?</b><small>Vraag een gratis adviesgesprek aan: een adviseur aan huis of telefonisch, zonder verplichtingen.</small><div class="vwb-btns">' +
      '<button type="button" data-book="huis">' + IC.huis + 'Adviseur aan huis</button><button type="button" data-book="bel">' + IC.bel + 'Bel mij</button></div>';
    b.appendChild(d);
  }
  new MutationObserver(function(ms){
    ms.forEach(function(m){
      if(m.type === 'attributes'){ if(m.target.getAttribute('data-sent') === '1'){ var pre = m.target.querySelector('.vwb-pre'); if(pre) pre.remove(); addAfter(m.target); } }
      else addPre();
    });
  }).observe(document.documentElement, {subtree: true, childList: true, attributes: true, attributeFilter: ['data-sent']});
  addPre();
})();
</script>
<!-- vw-cal:end -->'''.replace('__REGIO__', REGIO).replace('__ICONS__', JS_ICONS)

# Blok op de contactpagina, direct onder de contactkanalen
SECTION = '''<!-- vw-cal-sectie:start -->
      <div class="ct-book reveal" id="afspraak" style="scroll-margin-top:96px;">
        <div>
          <div class="pill">Gratis &amp; vrijblijvend</div>
          <h2 style="font-size:clamp(24px,3vw,30px);margin-top:14px;">Plan je gratis adviesgesprek</h2>
          <p style="font-size:14.5px;color:var(--ink-soft);margin-top:8px;line-height:1.55;max-width:560px;">In onze regio komt een adviseur bij je langs, daarbuiten bellen we je. Na het gesprek krijg je je persoonlijke plan met vaste prijs.</p>
        </div>
        <div class="ct-book-grid">
          <a class="ct-bk" href="#afspraak" data-book="huis"><span class="ct-bk-ic">%(huis)s</span><b>Adviseur aan huis</b><span>Ongeveer een uur · we kijken samen naar je woning, meterkast en verbruik</span><em>Geef je voorkeur door →</em></a>
          <a class="ct-bk" href="#afspraak" data-book="bel"><span class="ct-bk-ic">%(bel)s</span><b>Telefonisch adviesgesprek</b><span>Ongeveer een half uur · we bellen je op het moment dat jou uitkomt</span><em>Kies een moment →</em></a>
          <a class="ct-bk" href="https://wa.me/31853335687?text=Hallo%%20Voltwijk!%%20Ik%%20wil%%20graag%%20een%%20adviesgesprek%%20plannen." target="_blank" rel="noopener"><span class="ct-bk-ic">%(wa)s</span><b>Via WhatsApp</b><span>App ons wanneer het jou uitkomt, dan plannen we het samen</span><em>App ons →</em></a>
        </div>
      </div>
      <style>
        .ct-book{margin-top:28px;padding:30px;border-radius:24px;background:#fff;border:1px solid var(--border);}
        .ct-book-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:22px;}
        .ct-bk{display:flex;flex-direction:column;gap:8px;padding:20px;border-radius:18px;border:2px solid var(--border);text-decoration:none;color:var(--ink);transition:border-color .15s,transform .15s,box-shadow .15s;}
        .ct-bk:hover,.ct-bk:focus-visible{border-color:var(--primary);transform:translateY(-2px);box-shadow:0 18px 34px -24px rgba(15,110,107,.7);outline:none;}
        .ct-bk .ct-bk-ic{width:44px;height:44px;border-radius:14px;background:var(--surface-tint);color:var(--primary);display:flex;align-items:center;justify-content:center;}
        .ct-bk b{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:17px;}
        .ct-bk span{font-size:13.5px;color:var(--ink-faint);line-height:1.5;}
        .ct-bk em{font-style:normal;font-weight:800;font-size:13.5px;color:var(--primary);margin-top:auto;padding-top:4px;}
        @media (max-width:760px){ .ct-book{padding:22px 18px;} .ct-book-grid{grid-template-columns:1fr;gap:10px;} }
      </style>
<!-- vw-cal-sectie:end -->''' % ICONS

n = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    s2 = re.sub(r'\n?<!-- vw-cal:start -->.*?<!-- vw-cal:end -->', '', s, flags=re.S)
    s2 = re.sub(r'\n?<!-- vw-cal-sectie:start -->.*?<!-- vw-cal-sectie:end -->', '', s2, flags=re.S)
    if not OFF:
        s2 = s2.rstrip('\n') + '\n' + BLOCK + '\n'
    if not OFF and f == 'contact.html':
        anchor = '      </div>\n    </div>\n\n    <div class="wrap" style="padding-top:88px;padding-bottom:88px;">'
        assert anchor in s2, 'ankerpunt contactpagina niet gevonden'
        s2 = s2.replace(anchor, '      </div>\n' + SECTION + anchor[len('      </div>'):], 1)
    if s2 != s: open(f, 'w', encoding='utf-8').write(s2); n += 1
print(('Gesprek plannen verwijderd' if OFF else 'Gesprek plannen (aangesloten op het CRM) op') + ' ' + str(n) + " pagina's")
