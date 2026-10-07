#!/usr/bin/env python3
# Vriendendeal: delen zonder bestanden.
# - /vriendendeal?c=CODE&n=Naam  : de link die vrienden krijgen. Bij delen in WhatsApp/Facebook toont hij één afbeelding
#   (images/vriendendeal-og.jpg, via seo.py) en stuurt de bezoeker meteen door naar /thuisbatterij-berekenen met de code,
#   waar de vriendenkorting (tools/funnel.py, VRIENDENKORTING) vanzelf in de prijs zit.
# - /deel?c=CODE&n=Naam          : de persoonlijke deelpagina voor de ambassadeur: uitleg en knoppen voor WhatsApp, Facebook,
#   LinkedIn, delen via de telefoon en link kopiëren.
# Beide pagina's staan op noindex (niet in Google of de sitemap). Veilig om opnieuw te draaien: python3 tools/vriendendeal.py
import json, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from funnel import VRIENDENKORTING  # noqa: E402
from battery import PAKKETTEN  # noqa: E402

K = VRIENDENKORTING
eur = lambda n: '€\u00a0' + f'{int(n):,}'.replace(',', '.')
P = {p['id']: p['prijs'] - K for p in PAKKETTEN}
BELONING = 200

HEAD = '''<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><meta name="description" content="%s"><meta name="robots" content="noindex"><link rel="canonical" href="https://voltwijk.nl/%s"><link rel="icon" href="/merk/kit/logo/voltwijk-app-icoon.svg">
<style>
@font-face{font-family:'Bricolage Grotesque';src:url(/fonts/bricolage-grotesque-v9-latin.woff2) format('woff2');font-weight:400 800;font-display:swap}
@font-face{font-family:'Nunito Sans';src:url(/fonts/nunito-sans-v19-latin.woff2) format('woff2');font-weight:400 900;font-display:swap}
:root{--dark:#10201F;--teal:#0F6E6B;--mint:#6FD6C8;--coral:#FF6B5B;--bg:#F4F7F4;--tint:#E4F0EF;--ink:#233532;--mute:#5E706C}
*{box-sizing:border-box;margin:0;padding:0} body{font-family:'Nunito Sans',system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.5}
h1,h2,.d{font-family:'Bricolage Grotesque',system-ui,sans-serif;letter-spacing:-.015em;color:var(--dark)}
.w{max-width:620px;margin:0 auto;padding:22px 16px 40px}
.k{background:#fff;border-radius:20px;padding:20px;margin-top:14px;box-shadow:0 14px 34px -26px rgba(16,32,31,.5)}
.ey{font-size:12px;font-weight:900;letter-spacing:.14em;text-transform:uppercase;color:var(--teal)}
</style></head><body>'''

def vriendendeal():
    t = f'{eur(K)} vriendenkorting op je thuisbatterij | Voltwijk'
    d = f'Via een vriend: 16 kWh thuisbatterij voor {eur(P["bat16-1"])}, alles inbegrepen (na btw-teruggave). Bekijk je aanbod en plan direct in.'
    return HEAD % (t, d, 'vriendendeal') + f'''<div class="w" style="text-align:center;padding-top:60px">
  <img src="/merk/kit/logo/voltwijk-logo-kleur.svg" alt="Voltwijk" style="height:34px">
  <h1 style="font-size:28px;margin-top:28px">{eur(K)} vriendenkorting op je thuisbatterij</h1>
  <p style="margin-top:10px;color:var(--mute)">Je wordt doorgestuurd naar je persoonlijke aanbod…</p>
  <p style="margin-top:22px"><a id="door" href="/thuisbatterij-berekenen" style="display:inline-block;background:var(--teal);color:#fff;font-weight:800;text-decoration:none;border-radius:999px;padding:14px 22px">Bekijk mijn aanbod →</a></p></div>
''' + '''<script>(function(){ var u = new URLSearchParams(location.search), c = (u.get('c') || '').replace(/[^A-Za-z0-9_-]/g, '').slice(0, 20), n = (u.get('n') || '').slice(0, 40);
  var q = new URLSearchParams({utm_source: 'vriendendeal', utm_medium: 'referral', utm_campaign: 'vriendendeal'}); if(c) q.set('utm_content', c); if(n) q.set('door', n);
  var to = '/thuisbatterij-berekenen?' + q.toString(); document.getElementById('door').href = to; location.replace(to); })();</script>
</body></html>'''

JS_DEEL = '''<script>(function(){ var u = new URLSearchParams(location.search), c = (u.get('c') || '').replace(/[^A-Za-z0-9_-]/g, '').slice(0, 20), n = (u.get('n') || '').slice(0, 40);
  var link = location.origin + '/vriendendeal?c=' + encodeURIComponent(c) + (n ? '&n=' + encodeURIComponent(n) : '');
  var tekst = __TEKST__;
  document.getElementById('code').textContent = c ? 'Code ' + c : ''; if(n) document.getElementById('hoi').textContent = 'Hoi ' + n;
  document.getElementById('link').textContent = link;
  document.getElementById('wa').href = 'https://wa.me/?text=' + encodeURIComponent(tekst + '\\n' + link);
  document.getElementById('fb').href = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(link);
  document.getElementById('li').href = 'https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(link);
  var nb = document.getElementById('native'); if(navigator.share){ nb.hidden = false; nb.onclick = function(){ navigator.share({title: 'Vriendenkorting op je thuisbatterij', text: tekst, url: link}).catch(function(){}); }; }
  document.getElementById('kopie').onclick = function(){ var b = this; (navigator.clipboard ? navigator.clipboard.writeText(tekst + '\\n' + link) : Promise.reject()).then(function(){ b.textContent = 'Gekopieerd ✓'; setTimeout(function(){ b.textContent = 'Kopieer je link'; }, 2000); }).catch(function(){ prompt('Kopieer je link:', link); }); };
})();</script>'''

def deel():
    tekst = (f"Hé! Ken je Voltwijk? Ze doen thuisbatterijen: vaste prijs inclusief installatie, met eigen monteurs. Salderen stopt in 2027, dus heb je zonnepanelen, kijk er dan nu naar. Via mijn link krijg je {eur(K)} korting: een 16 kWh voor {eur(P['bat16-1'])}, alles inbegrepen (na btw-teruggave). Eerlijk is eerlijk: ik krijg een bedankje als je klant wordt 🙂")
    t = 'Deel je vriendendeal | Voltwijk'
    d = f'Deel je persoonlijke link: je vrienden krijgen {eur(K)} korting op een thuisbatterij, jij krijgt {eur(BELONING)} per nieuwe klant.'
    knop = 'display:flex;align-items:center;justify-content:center;gap:10px;width:100%;border:0;border-radius:14px;padding:15px 16px;font:800 16px Nunito Sans,system-ui,sans-serif;text-decoration:none;cursor:pointer;margin-top:10px'
    regels = [f'Je krijgt <b>{eur(BELONING)}</b> voor elke vriend die via jouw link een thuisbatterij koopt: offerte getekend en aanbetaling betaald.',
              'We betalen uit zodra de wettelijke bedenktijd van 14 dagen voorbij is. Annuleert iemand binnen die tijd, dan vervalt het bedankje.',
              'Je link telt als je vriend via die link aanvraagt of inplant. Belt iemand liever? Laat hem dan je code noemen.',
              'Er is geen maximum.', 'Was iemand al klant of had hij al een aanvraag lopen, dan telt hij niet mee.',
              'Deel je het in een groep of op social media? Zeg er eerlijk bij dat je een bedankje krijgt. Dat staat al in de tekst hieronder.',
              'Het bedankje is inkomen; wij geven het door aan de Belastingdienst zoals de wet vraagt.']
    return HEAD % (t, d, 'deel') + f'''<div class="w">
  <div style="display:flex;justify-content:space-between;align-items:center"><img src="/merk/kit/logo/voltwijk-logo-kleur.svg" alt="Voltwijk" style="height:28px"><span class="ey" id="code"></span></div>
  <div style="background:linear-gradient(135deg,#10201F,#0F6E6B);color:#fff;border-radius:22px;padding:24px 22px;margin-top:18px">
    <div class="ey" style="color:var(--mint)">Vriendendeal</div>
    <h1 style="color:#fff;font-size:30px;line-height:1.08;margin-top:8px"><span id="hoi">Hoi</span>, deel je link en verdien {eur(BELONING)} per vriend</h1>
    <p style="color:#CFE6E2;margin-top:10px">Je vrienden krijgen <b style="color:#fff">{eur(K)} korting</b> op een thuisbatterij. Een 16 kWh kost ze dan {eur(P['bat16-1'])}, alles inbegrepen (na btw-teruggave). Wordt iemand klant, dan krijg jij {eur(BELONING)}.</p></div>
  <div class="k"><h2 style="font-size:20px">Deel met één tik</h2>
    <p style="color:var(--mute);font-size:14.5px;margin-top:4px">Je vrienden zien een afbeelding met de actie en komen via jouw link direct bij hun aanbod.</p>
    <button id="native" style="{knop};background:var(--dark);color:#fff" hidden>Delen…</button>
    <a id="wa" target="_blank" rel="noopener" style="{knop};background:#25D366;color:#fff">Deel via WhatsApp</a>
    <a id="fb" target="_blank" rel="noopener" style="{knop};background:#1877F2;color:#fff">Deel op Facebook</a>
    <a id="li" target="_blank" rel="noopener" style="{knop};background:#0A66C2;color:#fff">Deel op LinkedIn</a>
    <button id="kopie" style="{knop};background:var(--tint);color:var(--dark)">Kopieer je link</button>
    <p id="link" style="font-size:13px;color:var(--mute);margin-top:10px;word-break:break-all"></p></div>
  <div class="k"><h2 style="font-size:20px">Zo werkt het</h2>
    <ol style="padding-left:20px;margin-top:8px"><li><b>Deel je link</b> in WhatsApp, op Facebook of LinkedIn.</li><li><b>Je vriend kijkt</b> welke batterij past, met {eur(K)} korting, en plant direct in of vraagt een offerte aan.</li><li><b>Wij doen de rest</b>: advies, offerte en installatie door onze eigen monteurs.</li><li><b>Jij krijgt {eur(BELONING)}</b> als hij klant wordt.</li></ol></div>
  <div class="k"><h2 style="font-size:20px">Waarom je het met een gerust hart deelt</h2>
    <ul style="padding-left:20px;margin-top:8px"><li>16 kWh thuisbatterij voor {eur(P['bat16-1'])} met korting, inclusief hybride omvormer, installatie en aansluiten.</li><li>Vaste prijs vooraf, geen verrassingen achteraf.</li><li>12.500+ installaties en een 4,7 / 5 op Google.</li><li>Eigen monteurs en 2 jaar installatiegarantie.</li><li>Ook zonnepanelen, airco's, laadpalen, meterkasten en boilers.</li></ul></div>
  <div class="k"><h2 style="font-size:20px">De afspraken</h2><ol style="padding-left:20px;margin-top:8px;font-size:14.5px">{''.join(f'<li style="margin-bottom:4px">{r}</li>' for r in regels)}</ol></div>
  <p style="text-align:center;font-size:13px;color:var(--mute);margin-top:20px">Vragen? Bel of app <a href="https://wa.me/31853335687" style="color:var(--teal);font-weight:800">085 333 56 87</a> · Voltwijk B.V., Zevenbergen</p></div>
''' + JS_DEEL.replace('__TEKST__', json.dumps(tekst, ensure_ascii=False)) + '''
</body></html>'''

open('vriendendeal.html', 'w', encoding='utf-8').write(vriendendeal())
open('deel.html', 'w', encoding='utf-8').write(deel())
print('vriendendeal: vriendendeal.html en deel.html gebouwd')
