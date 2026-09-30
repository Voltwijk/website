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
def pkg_rows():
    return ''.join(
        f'<div class="bk-alt" data-pkg="{p["id"]}"><div><b>{p["kwh"]} kWh</b> + {p["kw"]} kW hybride omvormer<small>{p["fase"]} aansluiting</small></div>'
        f'<span>{eur(p["prijs"])}</span></div>' for p in PAKKETTEN)

SECTION = '''<!--vw-batterijkeuze-->
<style>
.bk{background:var(--surface-tint,#F4F7F4);}
.bk .wrap{padding-top:80px;padding-bottom:80px;}
.bk-grid{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:28px;margin-top:28px;align-items:start;}
.bk-q{background:var(--surface,#fff);border:1px solid var(--border,#E3E8E4);border-radius:22px;padding:26px 26px 10px;}
.bk-step{padding-bottom:22px;margin-bottom:22px;border-bottom:1px solid var(--border,#E3E8E4);}
.bk-step:last-child{border-bottom:0;margin-bottom:0;}
.bk-step h3{font-size:17px;display:flex;gap:10px;align-items:center;}
.bk-step h3 i{font-style:normal;width:26px;height:26px;border-radius:50%;background:var(--dark,#10201F);color:#fff;font-size:13px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;}
.bk-hint{font-size:13px;color:var(--ink-faint,#6B7A76);margin:6px 0 0 36px;line-height:1.5;}
.bk-row{display:flex;align-items:center;gap:14px;margin:14px 0 0 36px;flex-wrap:wrap;}
.bk-num{display:flex;align-items:center;border:1.5px solid var(--border,#E3E8E4);border-radius:14px;overflow:hidden;background:#fff;}
.bk-num button{width:44px;height:46px;border:0;background:none;font-size:22px;font-weight:700;color:var(--ink,#10201F);cursor:pointer;}
.bk-num button:hover{background:var(--surface-tint,#F4F7F4);}
.bk-num input{width:70px;height:46px;border:0;text-align:center;font:700 19px 'Bricolage Grotesque',system-ui,sans-serif;color:var(--ink,#10201F);-moz-appearance:textfield;}
.bk-num input::-webkit-outer-spin-button,.bk-num input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0;}
.bk-unit{font-size:14px;color:var(--ink-soft,#3F4F4B);font-weight:600;}
.bk-range{width:100%;max-width:420px;accent-color:var(--primary,#0F6E6B);}
.bk-chips{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 0 36px;}
.bk-chip{border:1.5px solid var(--border,#E3E8E4);background:#fff;border-radius:999px;padding:8px 14px;font-size:13.5px;font-weight:700;color:var(--ink-soft,#3F4F4B);cursor:pointer;}
.bk-chip[aria-pressed="true"]{border-color:var(--primary,#0F6E6B);background:var(--primary,#0F6E6B);color:#fff;}
.bk-res{position:sticky;top:90px;background:var(--dark,#10201F);color:#fff;border-radius:22px;padding:26px;box-shadow:0 30px 60px -30px rgba(16,32,31,.6);}
.bk-res .lbl{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--mint,#6FD6C8);}
.bk-res h3{font-size:26px;color:#fff;margin-top:8px;line-height:1.15;}
.bk-res .sub{font-size:14px;color:rgba(255,255,255,.72);margin-top:4px;}
.bk-price{display:flex;align-items:baseline;gap:10px;margin-top:16px;flex-wrap:wrap;}
.bk-price b{font:700 40px/1 'Bricolage Grotesque',system-ui,sans-serif;color:#fff;}
.bk-price span{font-size:13px;color:rgba(255,255,255,.72);}
.bk-why{list-style:none;margin:18px 0 0;padding:16px 0 0;border-top:1px solid rgba(255,255,255,.14);display:flex;flex-direction:column;gap:10px;font-size:14px;line-height:1.5;color:rgba(255,255,255,.88);}
.bk-why li{display:flex;gap:10px;}.bk-why li:before{content:"✓";color:var(--mint,#6FD6C8);font-weight:800;}
.bk-inc{font-size:13px;color:rgba(255,255,255,.7);margin-top:14px;line-height:1.55;}
.bk-cta{display:flex;flex-direction:column;gap:10px;margin-top:20px;}
.bk-cta .btn-primary{background:var(--mint,#6FD6C8);color:var(--dark,#10201F);text-align:center;text-decoration:none;border:0;cursor:pointer;font-size:15px;}
.bk-cta .bk-sec{background:none;border:1.5px solid rgba(255,255,255,.35);color:#fff;border-radius:999px;padding:12px 18px;font-weight:800;font-size:14px;cursor:pointer;text-decoration:none;text-align:center;}
.bk-form{margin-top:18px;padding-top:16px;border-top:1px solid rgba(255,255,255,.14);display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.bk-form[hidden]{display:none;}
.bk-form b.t{grid-column:1/-1;font-size:15px;color:#fff;}
.bk-form label{display:flex;flex-direction:column;gap:4px;font-size:12px;font-weight:700;color:rgba(255,255,255,.7);min-width:0;}
.bk-form label.full{grid-column:1/-1;}
.bk-form input{width:100%;box-sizing:border-box;border:1.5px solid rgba(255,255,255,.25);background:rgba(255,255,255,.06);color:#fff;border-radius:12px;padding:11px 12px;font:inherit;font-size:15px;}
.bk-form input:focus{outline:none;border-color:var(--mint,#6FD6C8);}
.bk-form .btn-primary{grid-column:1/-1;background:var(--mint,#6FD6C8);color:var(--dark,#10201F);border:0;cursor:pointer;font-size:15px;margin-top:4px;}
.bk-form p{grid-column:1/-1;font-size:12.5px;line-height:1.5;color:rgba(255,255,255,.65);margin:0;}
.bk-err{grid-column:1/-1;background:#FDECEC;color:#8A1F1F;border-radius:10px;padding:10px 12px;font-size:13px;}
.bk-ok{margin-top:18px;padding:16px;border-radius:14px;background:rgba(111,214,200,.14);outline:1.5px solid var(--mint,#6FD6C8);font-size:14px;line-height:1.55;color:rgba(255,255,255,.9);}
.bk-ok b{display:block;color:#fff;font-size:17px;margin-bottom:4px;}
.bk-alts{margin-top:22px;padding-top:16px;border-top:1px solid rgba(255,255,255,.14);}
.bk-alts > div:first-child{font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:rgba(255,255,255,.6);margin-bottom:8px;}
.bk-alt{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:9px 10px;border-radius:12px;font-size:13.5px;color:rgba(255,255,255,.85);cursor:pointer;}
.bk-alt small{display:block;color:rgba(255,255,255,.55);font-size:12px;}
.bk-alt span{font-weight:800;white-space:nowrap;}
.bk-alt:hover{background:rgba(255,255,255,.06);}
.bk-alt.is-on{background:rgba(111,214,200,.16);outline:1.5px solid var(--mint,#6FD6C8);}
.bk-note{font-size:12.5px;color:var(--ink-faint,#6B7A76);margin-top:16px;line-height:1.55;max-width:760px;}
@media (max-width:900px){.bk-form{grid-template-columns:1fr;}.bk-grid{grid-template-columns:minmax(0,1fr);}.bk-q,.bk-res{padding:20px;}.bk-range{flex:1 1 180px;min-width:0;}.bk-res{position:static;}.bk-row,.bk-chips,.bk-hint{margin-left:0;}.bk .wrap{padding-top:56px;padding-bottom:56px;}}
</style>
<section class="bk" id="batterijkeuze" aria-labelledby="bk-title">
 <div class="wrap">
  <div class="pill">Batterijkeuzehulp</div>
  <h2 id="bk-title" style="font-size:clamp(26px,3.6vw,36px);margin-top:12px;max-width:720px;">Welke thuisbatterij past bij jou?</h2>
  <p style="font-size:16px;color:var(--ink-soft);margin-top:10px;max-width:640px;line-height:1.6;">Beantwoord vier vragen. Je ziet direct welke batterij we je adviseren, met de vaste prijs inclusief installatie.</p>
  <div class="bk-grid">
   <form class="bk-q" id="bkForm" onsubmit="return false">
    <div class="bk-step">
     <h3><i>1</i>Hoeveel zonnepanelen heb je?</h3>
     <div class="bk-row"><div class="bk-num"><button type="button" data-d="-1" aria-label="Eén paneel minder">−</button><input id="bkPanelen" type="number" min="0" max="60" value="12" inputmode="numeric" aria-label="Aantal zonnepanelen"><button type="button" data-d="1" aria-label="Eén paneel meer">+</button></div><span class="bk-unit">panelen</span></div>
     <div class="bk-chips"><button type="button" class="bk-chip" data-panelen="0">Nog geen panelen</button><button type="button" class="bk-chip" data-panelen="12">Weet ik niet precies</button></div>
    </div>
    <div class="bk-step">
     <h3><i>2</i>Hoeveel stroom verbruik je per jaar?</h3>
     <p class="bk-hint">Staat op je jaarafrekening. Weet je het niet? Kies je huishouden.</p>
     <div class="bk-row"><input class="bk-range" id="bkVerbruik" type="range" min="1000" max="10000" step="100" value="3500" aria-label="Jaarverbruik in kWh"><b id="bkVerbruikTxt" style="font:700 19px 'Bricolage Grotesque',system-ui,sans-serif;min-width:110px;">3.500 kWh</b></div>
     <div class="bk-chips"><button type="button" class="bk-chip" data-verbruik="2500">1–2 personen</button><button type="button" class="bk-chip" data-verbruik="3500">3–4 personen</button><button type="button" class="bk-chip" data-verbruik="4500">5 of meer</button></div>
    </div>
    <div class="bk-step">
     <h3><i>3</i>Welke aansluiting heb je?</h3>
     <p class="bk-hint">Kijk in je meterkast: één hoofdschakelaar is 1-fase, drie naast elkaar (of "3x25A" op de meter) is 3-fase.</p>
     <div class="bk-chips" role="group" aria-label="Aansluiting"><button type="button" class="bk-chip" data-fase="1" aria-pressed="true">1-fase</button><button type="button" class="bk-chip" data-fase="3" aria-pressed="false">3-fase</button><button type="button" class="bk-chip" data-fase="?" aria-pressed="false">Weet ik niet</button></div>
    </div>
    <div class="bk-step">
     <h3><i>4</i>Heb je (straks) een van deze?</h3>
     <div class="bk-chips" role="group" aria-label="Extra verbruikers"><button type="button" class="bk-chip" data-extra="ev" aria-pressed="false">Elektrische auto</button><button type="button" class="bk-chip" data-extra="wp" aria-pressed="false">Warmtepomp</button><button type="button" class="bk-chip" data-extra="dyn" aria-pressed="false">Dynamisch energiecontract</button></div>
    </div>
   </form>
   <aside class="bk-res" aria-live="polite">
    <div class="lbl">Ons advies voor jou</div>
    <h3 id="bkNaam">Thuisbatterij 16 kWh</h3>
    <div class="sub" id="bkSub">met 6 kW hybride omvormer · 1-fase</div>
    <div class="bk-price"><b id="bkPrijs">€ 4.600</b><span>vaste prijs, inclusief installatie en btw</span></div>
    <ul class="bk-why" id="bkWhy"></ul>
    <p class="bk-inc"><b style="color:#fff;">Inbegrepen:</b> batterij en hybride omvormer, montage en bekabeling, aansluiten op een eigen groep in de meterkast, instellen van de app en uitleg bij oplevering.</p>
    <div class="bk-cta"><button type="button" class="btn-primary" id="bkKies">Vraag deze batterij aan →</button><a href="#" class="bk-sec" data-book="huis">Liever eerst een gratis adviesgesprek</a></div>
    <form class="bk-form" id="bkAanvraag" hidden novalidate>
     <b class="t" id="bkFormTitel">Je aanvraag</b>
     <label class="full">Naam<input name="naam" autocomplete="name" required></label>
     <label>Telefoon<input name="telefoon" type="tel" autocomplete="tel" inputmode="tel" required></label>
     <label>E-mail<input name="email" type="email" autocomplete="email" required></label>
     <label>Postcode<input name="postcode" autocomplete="postal-code" required></label>
     <label>Huisnummer<input name="huisnummer" autocomplete="address-line2" required></label>
     <input name="bot-field" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;">
     <button type="submit" class="btn-primary">Verstuur aanvraag →</button>
     <p>Je betaalt nu niets. We bellen je om je meterkast te checken (een paar foto's is genoeg) en plannen samen de installatiedatum. Pas na onze bevestiging volgt de aanbetaling van € 350, die van de totaalprijs afgaat.</p>
    </form>
    <div class="bk-alts"><div>Alle batterijen</div>''' + pkg_rows() + '''</div>
   </aside>
  </div>
  <p class="bk-note">Het advies is een indicatie op basis van gemiddelden: ongeveer 360 kWh per zonnepaneel per jaar, en zo'n 55% van je verbruik 's avonds en 's nachts. Bij de installatie kijken we samen naar je jaarafrekening, je dak en je meterkast. Is er meerwerk nodig, zoals een extra groep of een lange kabelroute, dan hoor je dat altijd vooraf.</p>
 </div>
</section>
<script>
(function(){
  var sec = document.getElementById('batterijkeuze'); if(!sec) return;
  // na de hero plaatsen (de productpagina wordt door renderProduct opgebouwd)
  var hero = document.querySelector('#view-product .p-hero');
  if(hero && hero.nextSibling !== sec) hero.parentNode.insertBefore(sec, hero.nextSibling);
  document.querySelectorAll('#view-product .p-hero a[href="#calculator"]').forEach(function(a){ a.setAttribute('href', '#batterijkeuze'); });
  var P = window.VW_BAT_PKGS || [], $ = function(id){ return document.getElementById(id); };
  var st = { panelen:12, verbruik:3500, fase:'1', extra:{ev:false, wp:false, dyn:false}, keuze:null };
  var fmt = function(n){ return Math.round(n).toLocaleString('nl-NL'); };
  var pkg = function(id){ return P.filter(function(p){ return p.id === id; })[0]; };
  function advies(){
    var pv = st.panelen * 360, dag = st.verbruik / 365;
    var over = Math.max(0, pv / 365 * 1.7 - dag * 0.45), avond = dag * 0.55;
    var extra = st.extra.ev || st.extra.wp || st.extra.dyn;
    var id = st.fase === '3' ? 'bat16-3' : ((st.panelen >= 10 || st.verbruik >= 3000 || extra || over > 8 || avond > 7) ? 'bat16-1' : 'bat10');
    var w = [];
    if(st.panelen > 0){
      w.push('Je ' + st.panelen + ' panelen wekken naar schatting ' + fmt(pv) + ' kWh per jaar op. Op een zonnige dag houd je ongeveer ' + fmt(over) + ' kWh over.');
    } else {
      w.push('Zonder zonnepanelen laadt de batterij op uren dat stroom goedkoop is. Dat werkt het best met een dynamisch energiecontract.');
    }
    w.push('\\'s Avonds en \\'s nachts gebruik je ongeveer ' + fmt(avond) + ' kWh per dag. Die stroom haal je dan uit je batterij in plaats van van het net.');
    if(id === 'bat16-3') w.push('Je hebt een 3-fase aansluiting. De 8 kW omvormer verdeelt het vermogen over alle drie de fasen.');
    else if(id === 'bat16-1') w.push('Met 16 kWh heb je ruimte voor je avondverbruik' + (st.extra.ev ? ', het laden van je auto' : '') + (st.extra.wp ? ', je warmtepomp' : '') + (st.extra.dyn ? ' en slim laden op goedkope uren' : '') + ', ook als je verbruik de komende jaren groeit.');
    else w.push('Je verbruik is bescheiden. 10 kWh vangt je avondverbruik ruim op, zonder dat je betaalt voor opslag die je niet gebruikt.');
    if(st.fase === '?') w.push('Je aansluiting controleren we vooraf. Blijkt die 3-fase, dan adviseren we de 16 kWh met 8 kW omvormer (' + '€ ' + fmt(pkg('bat16-3').prijs) + ').');
    if(st.extra.wp && st.fase !== '3' && st.verbruik >= 6000) w.push('Met een warmtepomp en dit verbruik kan een 3-fase aansluiting slim zijn. Dat bespreken we graag.');
    return { id:id, why:w };
  }
  function render(){
    var a = advies(), id = st.keuze || a.id, p = pkg(id); if(!p) return;
    $('bkNaam').textContent = 'Thuisbatterij ' + p.kwh + ' kWh';
    $('bkSub').textContent = 'met ' + p.kw + ' kW hybride omvormer · ' + p.fase;
    $('bkPrijs').textContent = '€ ' + fmt(p.prijs);
    $('bkFormTitel').textContent = 'Aanvraag: ' + p.kwh + ' kWh + ' + p.kw + ' kW (' + p.fase + ') · € ' + fmt(p.prijs);
    $('bkWhy').innerHTML = (st.keuze && st.keuze !== a.id ? ['Je koos zelf deze batterij. Op basis van je antwoorden adviseren we de ' + pkg(a.id).kwh + ' kWh met ' + pkg(a.id).kw + ' kW omvormer.'] : a.why).map(function(t){ return '<li>' + t + '</li>'; }).join('');
    sec.querySelector('.lbl').textContent = (st.keuze && st.keuze !== a.id) ? 'Jouw keuze' : 'Ons advies voor jou';
    sec.querySelectorAll('.bk-alt').forEach(function(el){ el.classList.toggle('is-on', el.getAttribute('data-pkg') === id); });
    $('bkVerbruikTxt').textContent = fmt(st.verbruik) + ' kWh';
    $('bkPanelen').value = st.panelen; $('bkVerbruik').value = st.verbruik;
    sec.querySelectorAll('[data-fase]').forEach(function(b){ b.setAttribute('aria-pressed', String(b.getAttribute('data-fase') === st.fase)); });
    sec.querySelectorAll('[data-extra]').forEach(function(b){ b.setAttribute('aria-pressed', String(st.extra[b.getAttribute('data-extra')])); });
    sec.querySelectorAll('[data-verbruik]').forEach(function(b){ b.setAttribute('aria-pressed', String(+b.getAttribute('data-verbruik') === st.verbruik)); });
    return id;
  }
  var touched = false;
  function change(){ st.keuze = null; render(); if(!touched && window.gtag){ touched = true; gtag('event', 'batterij_keuzehulp_start'); } }
  sec.addEventListener('click', function(e){
    var t = e.target.closest('button,[data-pkg]'); if(!t) return;
    if(t.hasAttribute('data-d')){ st.panelen = Math.max(0, Math.min(60, st.panelen + (+t.getAttribute('data-d')))); change(); }
    else if(t.hasAttribute('data-panelen')){ st.panelen = +t.getAttribute('data-panelen'); change(); }
    else if(t.hasAttribute('data-verbruik')){ st.verbruik = +t.getAttribute('data-verbruik'); change(); }
    else if(t.hasAttribute('data-fase')){ st.fase = t.getAttribute('data-fase'); change(); }
    else if(t.hasAttribute('data-extra')){ var k = t.getAttribute('data-extra'); st.extra[k] = !st.extra[k]; change(); }
    else if(t.hasAttribute('data-pkg')){ st.keuze = t.getAttribute('data-pkg'); render(); }
  });
  $('bkPanelen').addEventListener('input', function(){ var v = parseInt(this.value, 10); st.panelen = isNaN(v) ? 0 : Math.max(0, Math.min(60, v)); st.keuze = null; render(); });
  $('bkVerbruik').addEventListener('input', function(){ st.verbruik = +this.value; change(); });
  // de oude rekentool is hier niet meer nodig: alles loopt via de keuzehulp
  var calc = $('calculator');
  if(calc){ var box = calc.closest('.blk-light'); (box && box.children.length === 1 ? box : calc).style.display = 'none'; }
  document.querySelectorAll('a[href="#calculator"]').forEach(function(a){ a.setAttribute('href', '#batterijkeuze'); });
  var form = $('bkAanvraag');
  $('bkKies').addEventListener('click', function(){
    var id = render(); if(window.vwSetBat) window.vwSetBat(id);
    if(window.gtag) gtag('event', 'batterij_gekozen', { pakket:id, waarde:pkg(id).prijs });
    form.hidden = false; this.style.display = 'none';
    form.scrollIntoView({behavior:'smooth', block:'center'}); setTimeout(function(){ form.elements.naam.focus({preventScroll:true}); }, 350);
  });
  form.addEventListener('input', function(){ var o = form.querySelector('.bk-err'); if(o) o.remove(); });
  form.addEventListener('submit', function(e){
    e.preventDefault();
    var old = form.querySelector('.bk-err'); if(old) old.remove();
    var v = function(n){ return (form.elements[n].value || '').trim(); };
    var fout = !v('naam') ? 'Vul je naam in.' : !/^[+0-9 ()-]{10,}$/.test(v('telefoon')) ? 'Vul een geldig telefoonnummer in.' : !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v('email')) ? 'Vul een geldig e-mailadres in.' : !/^\d{4}\s?[a-zA-Z]{2}$/.test(v('postcode')) ? 'Vul je postcode in, bijvoorbeeld 4762 AS.' : !v('huisnummer') ? 'Vul je huisnummer in.' : '';
    if(fout){ var er = document.createElement('div'); er.className = 'bk-err'; er.textContent = fout; form.querySelector('button[type=submit]').insertAdjacentElement('beforebegin', er); return; }
    var id = st.keuze || advies().id, p = pkg(id), d = new Date();
    var nr = 'VW-' + String(d.getFullYear()).slice(2) + ('0' + (d.getMonth() + 1)).slice(-2) + ('0' + d.getDate()).slice(-2) + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();
    var label = 'Thuisbatterij ' + p.kwh + ' kWh + ' + p.kw + ' kW omvormer (' + p.fase + ')';
    var ex = ['ev','wp','dyn'].filter(function(k){ return st.extra[k]; }).map(function(k){ return {ev:'elektrische auto', wp:'warmtepomp', dyn:'dynamisch contract'}[k]; });
    var fd = new FormData();
    var velden = { 'form-name':'bestelling', 'bot-field':v('bot-field'), ordernummer:nr, naam:v('naam'), email:v('email'), telefoon:v('telefoon'),
      adres:'huisnummer ' + v('huisnummer'), postcode:v('postcode').toUpperCase(), plaats:'', huistype:'', producten:label,
      prijsregels:label + ' € ' + fmt(p.prijs), totaalprijs:'€ ' + fmt(p.prijs), aanbetaling:'€ 350', installatiedatum:'in overleg', technische_check:'Telefonisch',
      opmerking:'Batterijkeuzehulp: ' + st.panelen + ' panelen, ' + fmt(st.verbruik) + ' kWh/jaar, aansluiting ' + (st.fase === '?' ? 'onbekend' : st.fase + '-fase') + (ex.length ? ', ' + ex.join(', ') : '') + (st.keuze && st.keuze !== advies().id ? ' (zelf gekozen, advies was ' + advies().id + ')' : ''),
      akkoord:'aanvraag', pagina:location.pathname };
    Object.keys(velden).forEach(function(k){ fd.append(k, velden[k]); });
    var btn = form.querySelector('button[type=submit]'), txt = btn.innerHTML; btn.disabled = true; btn.innerHTML = 'Versturen…';
    fetch('/', {method:'POST', body:fd}).then(function(r){
      if(!r.ok) throw new Error(r.status);
      try{ if(window.vwTrack) vwTrack('bestelling_aangevraagd', {value:p.prijs, currency:'EUR', producten:'batterij', pagina:location.pathname}); else if(window.gtag) gtag('event', 'bestelling_aangevraagd', {value:p.prijs, currency:'EUR'}); }catch(x){}
      var ok = document.createElement('div'); ok.className = 'bk-ok';
      ok.innerHTML = '<b>Aanvraag ontvangen</b>Bedankt, ' + v('naam').split(' ')[0].replace(/[<>&"]/g, '') + '. We bellen je op ' + v('telefoon').replace(/[<>&"]/g, '') + ' om je meterkast te checken en een installatiedatum te plannen. Je aanvraagnummer is ' + nr + '.';
      form.replaceWith(ok); sec.querySelector('.bk-cta .bk-sec').style.display = 'none';
    }).catch(function(){
      btn.disabled = false; btn.innerHTML = txt;
      var er = document.createElement('div'); er.className = 'bk-err';
      er.innerHTML = 'Versturen lukte niet. Bel ons op <a href="tel:+31853335687" style="color:inherit;font-weight:700;">085 333 56 87</a> of app via <a href="https://wa.me/31853335687" style="color:inherit;font-weight:700;">WhatsApp</a>.';
      btn.insertAdjacentElement('beforebegin', er);
    });
  });
  render();
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
            s = re.sub(r'("price":")\d+(")', lambda m: m.group(1) + str(VANAF) + m.group(2), s)
            s = s.rstrip('\n') + '\n' + SECTION + '\n'
        if s != o:
            open(f, 'w', encoding='utf-8').write(s); changed += 1
    print(f'battery.py: {changed} pagina\'s bijgewerkt; pakketten: ' + ', '.join(f"{p['kwh']} kWh/{p['kw']} kW {p['fase']} {eur(p['prijs'])}" for p in PAKKETTEN))

if __name__ == '__main__':
    main()
