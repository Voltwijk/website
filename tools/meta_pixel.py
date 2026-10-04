#!/usr/bin/env python3
"""Meta-pixel (Facebook/Instagram-advertenties) op alle pagina's, alleen na toestemming.

Instellen: zet het pixel-ID (en eventueel de code voor domeinverificatie) in tools/meta.json en draai
    python3 tools/meta_pixel.py        (zit in tools/publish.sh, na cookie.py; veilig om vaker te draaien)
Leeg pixel_id = alles weer uit: geen pixel, cookiemelding en beleid zonder Meta.

Wat het doet als het pixel-ID is ingevuld:
- laadt de pixel pas als de bezoeker in de cookiemelding "Accepteren" kiest (toestemming versie 2, veld marketing);
  wie eerder toestemming gaf onder de oude tekst (zonder advertentiecookies) krijgt de melding opnieuw;
- meet: PageView, Lead (batterij-aanvraag via de calculator en verzonden offerteformulieren), ViewContent (advies in
  de calculator), Schedule (afspraak gepland), Contact (klik op WhatsApp of bellen) en CalculatorStart (eigen event);
- vult het cookiebeleid en privacybeleid aan met een alinea over Meta.
Domeinverificatie (Business Manager > Merkveiligheid > Domeinen > meta-tag): de code komt als meta-tag op de homepage.
"""
import glob, json, os, re, sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
cfg = json.load(open('tools/meta.json', encoding='utf-8'))
PID = (cfg.get('pixel_id') or '').strip()
DV = (cfg.get('domain_verification') or '').strip()
if PID and not re.fullmatch(r'\d{6,20}', PID): sys.exit('Ongeldig pixel-ID: ' + PID)
if DV and not re.fullmatch(r'[A-Za-z0-9]{10,64}', DV): sys.exit('Ongeldige verificatiecode: ' + DV)
ON = bool(PID)

BLOCK = '''<!-- vw-meta:start -->
<script>
(function(){
  var ID = '%s', on = false, lastLead = 0;
  function ok(){ var c = window.vwConsent; if(!c){ try{ c = JSON.parse(localStorage.getItem('vwConsent')); }catch(e){} } return !!(c && c.marketing); }
  function load(){
    if(on || !ok()) return; on = true;
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;
    s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', ID); fbq('track', 'PageView');
  }
  var MAP = {aanvraag_batterij:'Lead', generate_lead:'Lead', calc_advies:'ViewContent', afspraak_gepland:'Schedule', contact:'Contact'};
  function meta(name, p){
    if(!on || !window.fbq) return;
    if(name === 'calc_start'){ fbq('trackCustom', 'CalculatorStart'); return; }
    var m = MAP[name]; if(!m) return;
    if(m === 'Lead'){ var t = Date.now(); if(t - lastLead < 5000) return; lastLead = t; }
    var d = {}; if(p && p.value){ d.value = p.value; d.currency = 'EUR'; }
    if(p && p.batterij) d.content_name = p.batterij;
    fbq('track', m, d);
  }
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a[href]'); if(!a) return;
    var h = a.getAttribute('href');
    if(h.indexOf('wa.me') > -1 || h.indexOf('tel:') === 0) meta('contact');
  }, true);
  document.addEventListener('submit', function(e){
    var f = e.target; if(f.id === 'tbForm' || f.id === 'bkAanvraag' || (f.checkValidity && !f.checkValidity())) return; // calculator meet zelf na verzenden
    if(f.closest && f.closest('#leadNewsletter')) return;
    meta('generate_lead');
  }, true);
  document.addEventListener('DOMContentLoaded', function(){
    var prev = window.vwTrack;
    window.vwTrack = function(n, p){ try{ if(prev) prev(n, p); }catch(e){} meta(n, p); };
  });
  window.addEventListener('vw:consent', load);
  load();
})();
</script>
<!-- vw-meta:end -->'''

# toestemming: versie 2 met marketing (alleen als de pixel aan staat)
SAVE_RE = re.compile(r"var c = \{ v:\d, analytics: t\.getAttribute\('data-ck'\) === '1',(?: marketing: t\.getAttribute\('data-ck'\) === '1',)? ts:")
SAVE_ON = "var c = { v:2, analytics: t.getAttribute('data-ck') === '1', marketing: t.getAttribute('data-ck') === '1', ts:"
SAVE_OFF = "var c = { v:1, analytics: t.getAttribute('data-ck') === '1', ts:"
SHOW_OFF = "if(!saved){"
SHOW_ON = "if(!saved || !window.vwConsent || window.vwConsent.v < 2){"

P = '<p style="font-size:14px;color:var(--ink-soft);margin-top:10px;line-height:1.65;">'
COOKIE_P = ('<!--vw-meta-beleid-->' + P + '<strong>Advertenties (alleen na &quot;Accepteren&quot;):</strong> de Meta-pixel van Meta Platforms '
            '(Facebook en Instagram), cookies <em>_fbp</em> en <em>fr</em>, bewaartermijn maximaal 3 maanden. Hiermee meten we of iemand die op '
            'een advertentie van ons klikte daarna een aanvraag doet, een afspraak plant of contact opneemt, zodat we onze advertenties kunnen '
            'verbeteren. Meta kan deze gegevens ook voor eigen doeleinden gebruiken; zie het privacybeleid van Meta. Kies je &quot;Alleen '
            'noodzakelijk&quot;, dan wordt de Meta-pixel niet geladen.</p><!--/vw-meta-beleid-->')
PRIVACY_P = ('<!--vw-meta-beleid-->' + P + 'Alleen als je daar in de cookiemelding toestemming voor geeft, gebruiken we de Meta-pixel om te meten '
             'welke advertenties op Facebook en Instagram tot een aanvraag of afspraak leiden. Voor deze meting zijn Voltwijk en Meta Platforms '
             'Ireland Ltd. gezamenlijk verantwoordelijk. Meer hierover lees je in ons <a href="/cookiebeleid" style="color:var(--primary);'
             'font-weight:700;">cookiebeleid</a>.</p><!--/vw-meta-beleid-->')
BELEID = {
    'cookiebeleid.html': ('Kies je &quot;Alleen noodzakelijk&quot;, dan wordt Google Analytics niet geladen.</p>', COOKIE_P),
    'privacybeleid.html': ('advertentiefuncties staan uit. Meer hierover lees je in ons <a href="/cookiebeleid" style="color:var(--primary);font-weight:700;">cookiebeleid</a>.</p>', PRIVACY_P),
}
DV_TAG = '<meta name="facebook-domain-verification" content="%s">'

n = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read(); o = s
    s = re.sub(r'\n?<!-- vw-meta:start -->.*?<!-- vw-meta:end -->', '', s, flags=re.S)
    s = re.sub(r'<!--vw-meta-beleid-->.*?<!--/vw-meta-beleid-->', '', s, flags=re.S)
    s = re.sub(r'\n?<meta name="facebook-domain-verification" content="[^"]*">', '', s)
    s = SAVE_RE.sub(SAVE_ON if ON else SAVE_OFF, s)
    s = s.replace(SHOW_ON, SHOW_OFF)
    if ON:
        if SAVE_ON in s: s = s.replace(SHOW_OFF, SHOW_ON, 1)
        s = s.replace('</body>', BLOCK % PID + '\n</body>', 1) if '</body>' in s else s.rstrip('\n') + '\n' + BLOCK % PID + '\n'
        if f in BELEID and BELEID[f][0] in s: s = s.replace(BELEID[f][0], BELEID[f][0] + BELEID[f][1], 1)
    if DV and f == 'index.html': s = s.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + DV_TAG % DV, 1)
    if s != o: open(f, 'w', encoding='utf-8').write(s); n += 1
print('meta_pixel.py:', ('pixel ' + PID if ON else 'pixel uit') + (', domeinverificatie aan' if DV else '') + ',', n, "pagina's bijgewerkt")
