#!/usr/bin/env python3
"""Thuisbatterij: de drie pakketten, de batterijkeuzehulp op /product-batterij en de prijs in de calculator.

Draai vanuit de repo-root: python3 tools/battery.py   (zit ook in tools/publish.sh; veilig om vaker te draaien)

Wat het doet, in alle *.html:
- zet de pakketten en de gekozen batterij klaar voor de calculator (window.VW_BAT);
- de calculator rekent de batterij met de echte pakketprijs (zonder woningtoeslag) en toont het pakket bij naam;
- PRODUCTS.batterij (hero, specificaties, prijs) komt overeen met de pakketten.
Op product-batterij.html komt daarnaast de keuzehulp "Welke thuisbatterij past bij jou?".
Prijzen wijzigen? Pas alleen PAKKETTEN hieronder aan en draai het script (en tools/prerender-products.js).
"""
import glob, json, os, re, sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# id, capaciteit (kWh), omvormer (kW), fase, prijs (incl. installatie en btw)
PAKKETTEN = [
    {'id': 'bat10',   'kwh': 10, 'kw': 5, 'fase': '1-fase', 'prijs': 4200},
    {'id': 'bat16-1', 'kwh': 16, 'kw': 6, 'fase': '1-fase', 'prijs': 4600},
    {'id': 'bat16-3', 'kwh': 16, 'kw': 8, 'fase': '3-fase', 'prijs': 5700},
]
STANDAARD = 'bat16-1'  # wat de calculator toont als de bezoeker nog niets koos
VANAF = min(p['prijs'] for p in PAKKETTEN)

def eur(n): return '€ ' + f'{n:,}'.replace(',', '.')
for p in PAKKETTEN:
    p['naam'] = f"{p['kwh']} kWh + {p['kw']} kW hybride omvormer"
    p['label'] = f"Thuisbatterij {p['kwh']} kWh + {p['kw']} kW omvormer ({p['fase']})"

CFG = ('<script id="vw-bat-cfg">window.VW_BAT_PKGS=' + json.dumps(PAKKETTEN, ensure_ascii=False) +
       ';(function(){var k=null;try{k=localStorage.getItem("vw_bat")}catch(e){}'
       'var d=' + json.dumps(STANDAARD) + ';var f=function(id){return window.VW_BAT_PKGS.filter(function(p){return p.id===id})[0]};'
       'window.VW_BAT=f(k)||f(d);'
       'window.vwSetBat=function(id){var p=f(id);if(!p)return;window.VW_BAT=p;try{localStorage.setItem("vw_bat",id)}catch(e){}};})();</script>')

# calcCompute: batterij met pakketprijs, zonder woningtoeslag
OLD_PRICE = "    var price = Math.round((CALC_BASE[id]*mult)/10)*10;\n    return {id:id, label:PRODUCTS[id].name, price:price};"
NEW_PRICE = ("    var bat = (id==='batterij' && window.VW_BAT) ? window.VW_BAT : null;\n"
             "    var price = bat ? bat.prijs : Math.round((CALC_BASE[id]*mult)/10)*10;\n"
             "    return {id:id, label:(bat ? bat.label : PRODUCTS[id].name), price:price};")

PRODUCT_FIELDS = {
    'headline': "Een thuisbatterij van 10 of 16 kWh, inclusief installatie — vanaf " + eur(VANAF) + ".",
    'bullets': ["10 of 16 kWh opslag met hybride omvormer, voor 1-fase én 3-fase aansluitingen",
                "Vaste prijs inclusief installatie: je weet vooraf precies wat je betaalt",
                "Geïnstalleerd door ons eigen team, klaar voor het einde van salderen in 2027"],
    'cta': 'Bereken welke batterij past',
    'price': 'vanaf ' + eur(VANAF),
    'specs': [['Capaciteit', '10 of 16 kWh'], ['Omvormer', '5, 6 of 8 kW hybride'], ['Aansluiting', '1-fase of 3-fase'],
              ['Prijs', eur(PAKKETTEN[0]['prijs']) + ' – ' + eur(PAKKETTEN[-1]['prijs']) + ' incl. installatie'],
              ['Garantie', '10 jaar'], ['App-koppeling', 'Ja']],
}

def js_str(s): return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"
def js_list(l): return '[' + ','.join(js_list(x) if isinstance(x, list) else js_str(x) for x in l) + ']'

def patch_products(s):
    m = re.search(r"(var PRODUCTS = \{\s*batterij: \{)(.*?)(\n  \},\n  zonnepanelen:)", s, re.S)
    if not m: return s
    body = m.group(2)
    body = re.sub(r"headline:'(?:[^'\\]|\\.)*'", lambda _: 'headline:' + js_str(PRODUCT_FIELDS['headline']), body, count=1)
    body = re.sub(r"bullets:\[.*?\],\n", lambda _: 'bullets:' + js_list(PRODUCT_FIELDS['bullets']) + ',\n', body, count=1, flags=re.S)
    body = re.sub(r"cta:'(?:[^'\\]|\\.)*'", lambda _: 'cta:' + js_str(PRODUCT_FIELDS['cta']), body, count=1)
    body = re.sub(r"price:'(?:[^'\\]|\\.)*'", lambda _: 'price:' + js_str(PRODUCT_FIELDS['price']), body, count=1)
    body = re.sub(r"specs:\[\[.*?\]\],\n", lambda _: 'specs:' + js_list(PRODUCT_FIELDS['specs']) + ',\n', body, count=1, flags=re.S)
    return s[:m.start(2)] + body + s[m.end(2):]

# ---------- de keuzehulp (alleen op product-batterij.html) ----------
# Eén kaart, één vraag per scherm; daarna het advies, dan de aanvraag (eigen scherm), dan de bevestiging.
SECTION = '''<!--vw-batterijkeuze-->
<style>
.bk{background:var(--surface-tint,#F4F7F4);}
.bk .wrap{padding-top:80px;padding-bottom:80px;}
.bk-head{text-align:center;max-width:640px;margin:0 auto;}
.bk-head p{font-size:16px;color:var(--ink-soft,#3F4F4B);margin-top:10px;line-height:1.6;}
.bk-card{max-width:680px;margin:32px auto 0;background:var(--surface,#fff);border:1px solid var(--border,#E3E8E4);border-radius:24px;padding:28px 32px 32px;box-shadow:0 30px 60px -40px rgba(16,32,31,.35);scroll-margin-top:90px;}
.bk-top{display:flex;justify-content:space-between;align-items:center;min-height:24px;font-size:13px;font-weight:700;color:var(--ink-faint,#6B7A76);}
.bk-back{background:none;border:0;padding:0;font:inherit;font-weight:700;color:var(--primary,#0F6E6B);cursor:pointer;}
.bk-back[hidden]{display:block;visibility:hidden;}
.bk-bar{height:4px;border-radius:4px;background:var(--border,#E3E8E4);margin-top:12px;overflow:hidden;}
.bk-bar i{display:block;height:100%;width:20%;background:var(--primary,#0F6E6B);border-radius:4px;transition:width .3s ease;}
.bk-screen{display:none;padding-top:26px;min-height:300px;}
.bk-screen.is-on{display:block;animation:bkIn .25s ease;}
@keyframes bkIn{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:none;}}
.bk-screen h3{font-size:clamp(21px,2.6vw,25px);line-height:1.25;}
.bk-screen .bk-lead{font-size:14.5px;color:var(--ink-soft,#3F4F4B);margin-top:6px;line-height:1.5;}
.bk-opts{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:22px;}
.bk-opt{display:flex;flex-direction:column;align-items:flex-start;gap:3px;text-align:left;background:#fff;border:1.5px solid var(--border,#E3E8E4);border-radius:16px;padding:16px 18px;font:inherit;font-size:16px;font-weight:800;color:var(--ink,#10201F);cursor:pointer;transition:border-color .15s,background .15s;}
.bk-opt small{font-size:13px;font-weight:500;color:var(--ink-faint,#6B7A76);line-height:1.4;}
.bk-opt:hover{border-color:var(--primary,#0F6E6B);}
.bk-opt[aria-pressed="true"]{border-color:var(--primary,#0F6E6B);background:var(--surface-tint,#F4F7F4);box-shadow:inset 0 0 0 1px var(--primary,#0F6E6B);}
.bk-go{display:block;width:100%;margin-top:22px;border:0;border-radius:999px;padding:16px 20px;background:var(--primary,#0F6E6B);color:#fff;font:inherit;font-size:16px;font-weight:800;cursor:pointer;text-align:center;}
.bk-go:hover{filter:brightness(1.08);}
.bk-lbl{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--primary,#0F6E6B);}
.bk-name{font-size:clamp(26px,3.4vw,32px);margin:6px 0 0;line-height:1.15;}
.bk-sub{font-size:15px;color:var(--ink-soft,#3F4F4B);margin-top:4px;}
.bk-price{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-top:18px;padding:16px 18px;border-radius:16px;background:var(--surface-tint,#F4F7F4);}
.bk-price b{font:700 38px/1 'Bricolage Grotesque',system-ui,sans-serif;color:var(--ink,#10201F);}
.bk-price span{font-size:13.5px;color:var(--ink-soft,#3F4F4B);}
.bk-why{list-style:none;margin:18px 0 0;padding:0;display:flex;flex-direction:column;gap:9px;font-size:15px;line-height:1.5;color:var(--ink-soft,#3F4F4B);}
.bk-why li{display:flex;gap:10px;}.bk-why li:before{content:"✓";color:var(--primary,#0F6E6B);font-weight:800;}
.bk-inc{font-size:13.5px;color:var(--ink-faint,#6B7A76);margin-top:14px;line-height:1.55;}
.bk-links{display:flex;justify-content:center;flex-wrap:wrap;gap:6px 20px;margin-top:14px;font-size:14px;}
.bk-links a,.bk-links button{background:none;border:0;padding:0;font:inherit;font-weight:700;color:var(--primary,#0F6E6B);text-decoration:underline;cursor:pointer;}
.bk-sum{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:12px 16px;border-radius:14px;background:var(--surface-tint,#F4F7F4);font-size:14px;color:var(--ink-soft,#3F4F4B);}
.bk-sum b{color:var(--ink,#10201F);white-space:nowrap;}
.bk-fields{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px;}
.bk-fields label{display:flex;flex-direction:column;gap:5px;font-size:13px;font-weight:700;color:var(--ink-soft,#3F4F4B);min-width:0;}
.bk-fields label.full{grid-column:1/-1;}
.bk-fields input{width:100%;box-sizing:border-box;border:1.5px solid var(--border,#E3E8E4);border-radius:12px;padding:12px 14px;font:inherit;font-size:16px;color:var(--ink,#10201F);background:#fff;}
.bk-fields input:focus{outline:none;border-color:var(--primary,#0F6E6B);}
.bk-small{font-size:13px;color:var(--ink-faint,#6B7A76);line-height:1.55;margin-top:12px;text-align:center;}
.bk-err{margin-top:14px;background:#FDECEC;color:#8A1F1F;border-radius:10px;padding:10px 12px;font-size:13.5px;}
.bk-ok{text-align:center;padding-top:20px;}
.bk-ok .ic{width:56px;height:56px;border-radius:50%;background:var(--primary,#0F6E6B);color:#fff;font-size:28px;font-weight:800;display:inline-flex;align-items:center;justify-content:center;}
.bk-ok p{font-size:15.5px;color:var(--ink-soft,#3F4F4B);line-height:1.6;margin:10px auto 0;max-width:460px;}
.bk-note{font-size:12.5px;color:var(--ink-faint,#6B7A76);margin:16px auto 0;line-height:1.55;max-width:680px;text-align:center;}
@media (max-width:640px){.bk .wrap{padding-top:56px;padding-bottom:56px;}.bk-card{padding:20px 18px 24px;border-radius:20px;}.bk-opts{grid-template-columns:minmax(0,1fr);}.bk-fields .m-full{grid-column:1/-1;}.bk-opt{padding:14px 16px;}.bk-screen{min-height:0;}}
</style>
<section class="bk" id="batterijkeuze" aria-labelledby="bk-title">
 <div class="wrap">
  <div class="bk-head">
   <div class="pill">Batterijkeuzehulp</div>
   <h2 id="bk-title" style="font-size:clamp(26px,3.6vw,36px);margin-top:12px;">Welke thuisbatterij past bij jou?</h2>
   <p>Vier korte vragen. Daarna zie je direct welke batterij we adviseren, met de vaste prijs inclusief installatie.</p>
  </div>
  <div class="bk-card" id="bkCard">
   <div class="bk-top"><button type="button" class="bk-back" id="bkBack" hidden>← Vorige</button><span id="bkCount">Vraag 1 van 4</span></div>
   <div class="bk-bar" id="bkBar"><i></i></div>

   <div class="bk-screen is-on" data-s="1">
    <h3>Heb je zonnepanelen?</h3>
    <div class="bk-opts">
     <button type="button" class="bk-opt" data-k="panelen" data-v="0">Nee, nog niet<small>De batterij laadt dan op goedkope uren</small></button>
     <button type="button" class="bk-opt" data-k="panelen" data-v="6">Ja, tot 8 panelen</button>
     <button type="button" class="bk-opt" data-k="panelen" data-v="12">Ja, 9 tot 15 panelen</button>
     <button type="button" class="bk-opt" data-k="panelen" data-v="18">Ja, 16 of meer</button>
    </div>
   </div>

   <div class="bk-screen" data-s="2">
    <h3>Met hoeveel mensen woon je?</h3>
    <p class="bk-lead">Zo schatten we je stroomverbruik in.</p>
    <div class="bk-opts">
     <button type="button" class="bk-opt" data-k="verbruik" data-v="2200">1 persoon<small>ongeveer 2.200 kWh per jaar</small></button>
     <button type="button" class="bk-opt" data-k="verbruik" data-v="2900">2 personen<small>ongeveer 2.900 kWh per jaar</small></button>
     <button type="button" class="bk-opt" data-k="verbruik" data-v="3700">3 of 4 personen<small>ongeveer 3.700 kWh per jaar</small></button>
     <button type="button" class="bk-opt" data-k="verbruik" data-v="4800">5 of meer<small>ongeveer 4.800 kWh per jaar</small></button>
    </div>
   </div>

   <div class="bk-screen" data-s="3">
    <h3>Welke aansluiting heb je?</h3>
    <p class="bk-lead">Kijk even in je meterkast.</p>
    <div class="bk-opts">
     <button type="button" class="bk-opt" data-k="fase" data-v="1">1-fase<small>Eén hoofdschakelaar</small></button>
     <button type="button" class="bk-opt" data-k="fase" data-v="3">3-fase<small>Drie hoofdschakelaars naast elkaar, of "3x25A" op de meter</small></button>
     <button type="button" class="bk-opt" data-k="fase" data-v="?" style="grid-column:1/-1;">Weet ik niet<small>Geen probleem, dat checken we samen</small></button>
    </div>
   </div>

   <div class="bk-screen" data-s="4">
    <h3>Heb je (straks) een van deze?</h3>
    <p class="bk-lead">Kies wat van toepassing is.</p>
    <div class="bk-opts">
     <button type="button" class="bk-opt" data-x="ev" aria-pressed="false">Elektrische auto</button>
     <button type="button" class="bk-opt" data-x="wp" aria-pressed="false">Warmtepomp</button>
     <button type="button" class="bk-opt" data-x="dyn" aria-pressed="false">Dynamisch energiecontract</button>
     <button type="button" class="bk-opt" data-x="geen" aria-pressed="false">Nee, geen van deze</button>
    </div>
    <button type="button" class="bk-go" id="bkToRes">Bekijk mijn advies →</button>
   </div>

   <div class="bk-screen" data-s="res" aria-live="polite">
    <div class="bk-lbl">Ons advies voor jou</div>
    <h3 class="bk-name" id="bkNaam">Thuisbatterij 16 kWh</h3>
    <div class="bk-sub" id="bkSub">met 6 kW hybride omvormer · 1-fase</div>
    <div class="bk-price"><b id="bkPrijs">€ 4.600</b><span>vaste prijs, inclusief installatie en btw</span></div>
    <ul class="bk-why" id="bkWhy"></ul>
    <p class="bk-inc"><b>Inbegrepen:</b> batterij en hybride omvormer, montage en bekabeling, aansluiten op een eigen groep in de meterkast, instellen van de app en uitleg bij oplevering.</p>
    <button type="button" class="bk-go" id="bkKies">Vraag deze batterij aan →</button>
    <div class="bk-links"><a href="#" data-book="huis">Liever eerst een gratis adviesgesprek</a><button type="button" id="bkOpnieuw">Opnieuw beginnen</button></div>
   </div>

   <div class="bk-screen" data-s="form">
    <div class="bk-sum"><span id="bkSumNaam">Thuisbatterij 16 kWh + 6 kW (1-fase)</span><b id="bkSumPrijs">€ 4.600</b></div>
    <h3 style="margin-top:20px;">Waar mogen we je bereiken?</h3>
    <form id="bkAanvraag" novalidate>
     <div class="bk-fields">
      <label class="full">Naam<input name="naam" autocomplete="name" required></label>
      <label class="m-full">Telefoon<input name="telefoon" type="tel" autocomplete="tel" inputmode="tel" required></label>
      <label class="m-full">E-mail<input name="email" type="email" autocomplete="email" required></label>
      <label>Postcode<input name="postcode" autocomplete="postal-code" required></label>
      <label>Huisnummer<input name="huisnummer" required></label>
     </div>
     <input name="bot-field" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;">
     <button type="submit" class="bk-go">Verstuur aanvraag →</button>
     <p class="bk-small">Je betaalt nu niets. We bellen je om je meterkast te checken en plannen samen de installatiedatum. Pas na onze bevestiging volgt een aanbetaling van € 350, die van de totaalprijs afgaat.</p>
    </form>
   </div>

   <div class="bk-screen bk-ok" data-s="ok">
    <div class="ic">✓</div>
    <h3 style="margin-top:14px;">Aanvraag ontvangen</h3>
    <p id="bkOkTxt"></p>
   </div>
  </div>
  <p class="bk-note">Het advies is een indicatie op basis van gemiddelden: ongeveer 360 kWh per zonnepaneel per jaar en zo'n 55% van je verbruik 's avonds en 's nachts. Bij de installatie kijken we samen naar je jaarafrekening en je meterkast. Is er meerwerk nodig, dan hoor je dat altijd vooraf.</p>
 </div>
</section>
<script>
(function(){
  var sec = document.getElementById('batterijkeuze'); if(!sec) return;
  // na de hero plaatsen (de productpagina wordt door renderProduct opgebouwd)
  var hero = document.querySelector('#view-product .p-hero');
  if(hero && hero.nextSibling !== sec) hero.parentNode.insertBefore(sec, hero.nextSibling);
  // de oude rekentool is hier niet meer nodig: alles loopt via de keuzehulp
  var calc = document.getElementById('calculator');
  if(calc){ var box = calc.closest('.blk-light'); (box && box.children.length === 1 ? box : calc).style.display = 'none'; }
  document.querySelectorAll('a[href="#calculator"]').forEach(function(a){ a.setAttribute('href', '#batterijkeuze'); });

  var P = window.VW_BAT_PKGS || [], $ = function(id){ return document.getElementById(id); };
  var st = { panelen:null, verbruik:null, fase:null, extra:{ev:false, wp:false, dyn:false} };
  var fmt = function(n){ return Math.round(n).toLocaleString('nl-NL'); };
  var pkg = function(id){ return P.filter(function(p){ return p.id === id; })[0]; };
  var esc = function(t){ return String(t).replace(/[<>&"]/g, ''); };
  var card = $('bkCard'), hist = [], cur = '1', started = false;

  function show(s, back){
    if(!back) hist.push(cur);
    cur = s;
    sec.querySelectorAll('.bk-screen').forEach(function(el){ el.classList.toggle('is-on', el.getAttribute('data-s') === s); });
    var n = {'1':1, '2':2, '3':3, '4':4}[s];
    $('bkCount').textContent = n ? 'Vraag ' + n + ' van 4' : (s === 'res' ? 'Jouw advies' : s === 'form' ? 'Aanvraag' : '');
    $('bkBar').firstChild.style.width = (n ? n * 20 : s === 'res' ? 90 : 100) + '%';
    $('bkBack').hidden = s === '1' || s === 'ok';
    var r = card.getBoundingClientRect(); if(r.top < 0 || r.top > window.innerHeight * .6) card.scrollIntoView({behavior:'smooth', block:'start'});
  }
  function advies(){
    var pv = st.panelen * 360, dag = st.verbruik / 365;
    var over = Math.max(0, pv / 365 * 1.7 - dag * 0.45), avond = dag * 0.55;
    var extra = st.extra.ev || st.extra.wp || st.extra.dyn;
    var id = st.fase === '3' ? 'bat16-3' : ((st.verbruik < 2500 && st.panelen < 10 && !extra) ? 'bat10' : 'bat16-1');
    var w = [];
    if(st.panelen > 0) w.push('Op een zonnige dag houd je ongeveer ' + fmt(over) + ' kWh zonnestroom over. Die sla je op in plaats van terug te leveren.');
    else w.push('Zonder zonnepanelen laadt de batterij op uren dat stroom goedkoop is.');
    w.push('\\'s Avonds en \\'s nachts gebruik je ongeveer ' + fmt(avond) + ' kWh per dag. Dat haal je dan uit je batterij.');
    if(id === 'bat16-3') w.push('De 8 kW omvormer verdeelt het vermogen over alle drie de fasen.');
    else if(id === 'bat16-1') w.push(extra ? 'Met 16 kWh heb je ook ruimte voor ' + [st.extra.ev && 'je auto', st.extra.wp && 'je warmtepomp', st.extra.dyn && 'slim laden op goedkope uren'].filter(Boolean).join(' en ') + '.' : 'Met 16 kWh heb je ook ruimte als je verbruik de komende jaren groeit.');
    else w.push('10 kWh vangt je avondverbruik ruim op, zonder te betalen voor opslag die je niet gebruikt.');
    if(st.fase === '?') w.push('Je aansluiting checken we vooraf. Is die 3-fase, dan wordt het de 16 kWh met 8 kW omvormer (€ ' + fmt(pkg('bat16-3').prijs) + ').');
    return { id:id, why:w };
  }
  function toonAdvies(){
    var a = advies(), p = pkg(a.id); if(!p) return;
    $('bkNaam').textContent = 'Thuisbatterij ' + p.kwh + ' kWh';
    $('bkSub').textContent = 'met ' + p.kw + ' kW hybride omvormer · ' + p.fase;
    $('bkPrijs').textContent = '€ ' + fmt(p.prijs);
    $('bkWhy').innerHTML = a.why.map(function(t){ return '<li>' + t + '</li>'; }).join('');
    $('bkSumNaam').textContent = 'Thuisbatterij ' + p.kwh + ' kWh + ' + p.kw + ' kW (' + p.fase + ')';
    $('bkSumPrijs').textContent = '€ ' + fmt(p.prijs);
    if(window.vwSetBat) window.vwSetBat(a.id);
    if(window.gtag) gtag('event', 'batterij_advies', { pakket:a.id, waarde:p.prijs });
    show('res');
  }

  sec.addEventListener('click', function(e){
    var t = e.target.closest('.bk-opt'); if(!t) return;
    if(!started && window.gtag){ started = true; gtag('event', 'batterij_keuzehulp_start'); }
    if(t.hasAttribute('data-k')){
      var k = t.getAttribute('data-k'), v = t.getAttribute('data-v');
      st[k] = k === 'fase' ? v : +v;
      t.parentNode.querySelectorAll('.bk-opt').forEach(function(b){ b.setAttribute('aria-pressed', String(b === t)); });
      setTimeout(function(){ show({panelen:'2', verbruik:'3', fase:'4'}[k]); }, 180);
    } else {
      var x = t.getAttribute('data-x');
      if(x === 'geen'){ st.extra = {ev:false, wp:false, dyn:false}; }
      else st.extra[x] = !st.extra[x];
      var any = st.extra.ev || st.extra.wp || st.extra.dyn;
      t.parentNode.querySelectorAll('[data-x]').forEach(function(b){ var y = b.getAttribute('data-x'); b.setAttribute('aria-pressed', String(y === 'geen' ? (x === 'geen' && !any) : st.extra[y])); });
    }
  });
  $('bkToRes').addEventListener('click', toonAdvies);
  $('bkBack').addEventListener('click', function(){ if(hist.length) show(hist.pop(), true); });
  $('bkOpnieuw').addEventListener('click', function(){ hist = []; show('1', true); });
  $('bkKies').addEventListener('click', function(){
    var id = advies().id; if(window.gtag) gtag('event', 'batterij_gekozen', { pakket:id, waarde:pkg(id).prijs });
    show('form'); setTimeout(function(){ try{ $('bkAanvraag').elements.naam.focus({preventScroll:true}); }catch(x){} }, 300);
  });

  var form = $('bkAanvraag');
  form.addEventListener('input', function(){ var o = form.querySelector('.bk-err'); if(o) o.remove(); });
  form.addEventListener('submit', function(e){
    e.preventDefault();
    var old = form.querySelector('.bk-err'); if(old) old.remove();
    var v = function(n){ return (form.elements[n].value || '').trim(); };
    var btn = form.querySelector('button[type=submit]');
    var fout = !v('naam') ? 'Vul je naam in.' : !/^[+0-9 ()-]{10,}$/.test(v('telefoon')) ? 'Vul een geldig telefoonnummer in.' : !/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(v('email')) ? 'Vul een geldig e-mailadres in.' : !/^\\d{4}\\s?[a-zA-Z]{2}$/.test(v('postcode')) ? 'Vul je postcode in, bijvoorbeeld 4762 AS.' : !v('huisnummer') ? 'Vul je huisnummer in.' : '';
    if(fout){ var er = document.createElement('div'); er.className = 'bk-err'; er.textContent = fout; btn.insertAdjacentElement('beforebegin', er); return; }
    var id = advies().id, p = pkg(id), d = new Date();
    var nr = 'VW-' + String(d.getFullYear()).slice(2) + ('0' + (d.getMonth() + 1)).slice(-2) + ('0' + d.getDate()).slice(-2) + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();
    var label = 'Thuisbatterij ' + p.kwh + ' kWh + ' + p.kw + ' kW omvormer (' + p.fase + ')';
    var ex = ['ev','wp','dyn'].filter(function(k){ return st.extra[k]; }).map(function(k){ return {ev:'elektrische auto', wp:'warmtepomp', dyn:'dynamisch contract'}[k]; });
    var velden = { 'form-name':'bestelling', 'bot-field':v('bot-field'), ordernummer:nr, naam:v('naam'), email:v('email'), telefoon:v('telefoon'),
      adres:'huisnummer ' + v('huisnummer'), postcode:v('postcode').toUpperCase(), plaats:'', huistype:'', producten:label,
      prijsregels:label + ' € ' + fmt(p.prijs), totaalprijs:'€ ' + fmt(p.prijs), aanbetaling:'€ 350', installatiedatum:'in overleg', technische_check:'Telefonisch',
      opmerking:'Batterijkeuzehulp: ' + (st.panelen ? 'ca. ' + st.panelen + ' panelen' : 'geen panelen') + ', ca. ' + fmt(st.verbruik) + ' kWh/jaar, aansluiting ' + (st.fase === '?' ? 'onbekend' : st.fase + '-fase') + (ex.length ? ', ' + ex.join(', ') : ''),
      akkoord:'aanvraag', pagina:location.pathname };
    var fd = new FormData(); Object.keys(velden).forEach(function(k){ fd.append(k, velden[k]); });
    var txt = btn.innerHTML; btn.disabled = true; btn.innerHTML = 'Versturen…';
    fetch('/', {method:'POST', body:fd}).then(function(r){
      if(!r.ok) throw new Error(r.status);
      try{ if(window.vwTrack) vwTrack('bestelling_aangevraagd', {value:p.prijs, currency:'EUR', producten:'batterij', pagina:location.pathname}); else if(window.gtag) gtag('event', 'bestelling_aangevraagd', {value:p.prijs, currency:'EUR'}); }catch(x){}
      $('bkOkTxt').innerHTML = 'Bedankt, ' + esc(v('naam').split(' ')[0]) + '. We bellen je op ' + esc(v('telefoon')) + ' om je meterkast te checken en een installatiedatum te plannen.<br><small>Je aanvraagnummer is ' + nr + '.</small>';
      hist = []; show('ok', true);
    }).catch(function(){
      btn.disabled = false; btn.innerHTML = txt;
      var er = document.createElement('div'); er.className = 'bk-err';
      er.innerHTML = 'Versturen lukte niet. Bel ons op <a href="tel:+31853335687" style="color:inherit;font-weight:700;">085 333 56 87</a> of app via <a href="https://wa.me/31853335687" style="color:inherit;font-weight:700;">WhatsApp</a>.';
      btn.insertAdjacentElement('beforebegin', er);
    });
  });
})();
</script>
<!--/vw-batterijkeuze-->'''

def main():
    changed = 0
    for f in sorted(glob.glob('*.html')):
        s = open(f, encoding='utf-8').read(); o = s
        s = re.sub(r'<script id="vw-bat-cfg">.*?</script>\n?', '', s, flags=re.S)
        if 'var PRODUCTS = {' in s or 'CALC_BASE' in s:
            s = s.replace('<meta charset="utf-8">\n', '<meta charset="utf-8">\n' + CFG + '\n', 1)
        s = s.replace(OLD_PRICE, NEW_PRICE)
        s = re.sub(r'batterij:\d+(, zonnepanelen:)', lambda m: f'batterij:{VANAF}{m.group(1)}', s)
        s = patch_products(s)
        s = s.replace('€ 3.499', eur(VANAF)).replace('€&nbsp;3.499', eur(VANAF).replace(' ', '&nbsp;'))
        if f == 'product-batterij.html':
            s = re.sub(r'\n?<!--vw-batterijkeuze-->.*?<!--/vw-batterijkeuze-->', '', s, flags=re.S)
            s = s.rstrip('\n') + '\n' + SECTION + '\n'
        if s != o:
            open(f, 'w', encoding='utf-8').write(s); changed += 1
    print(f'battery.py: {changed} pagina\'s bijgewerkt; pakketten: ' + ', '.join(f"{p['kwh']} kWh/{p['kw']} kW {p['fase']} {eur(p['prijs'])}" for p in PAKKETTEN))

if __name__ == '__main__':
    main()
