#!/usr/bin/env python3
# De ene calculator van de site: /thuisbatterij-berekenen (voor bezoekers, Google en advertenties).
# Veilig om opnieuw te draaien: python3 tools/funnel.py   (zit in tools/publish.sh)
#
# Wat het doet:
# 1. Bouwt thuisbatterij-berekenen.html op de pagina-schil van een artikel (cookiemelding, WhatsApp, afspraken),
#    maar zonder hoofdmenu: bovenaan logo, Google-score en telefoon. Daarin de calculator in stappen:
#    zonnepanelen -> verbruik -> extra's -> aansluiting -> wat je belangrijk vindt -> postcode -> advies met vaste prijs
#    -> aanvraag (Netlify-formulier 'thuisbatterij-advies', komt via de webhook in het CRM) -> afspraak plannen.
# 2. Haalt op alle andere pagina's de oude calculators weg (prijscalculator #calculator en de batterijkeuzehulp)
#    en zet er een vaste blok voor in de plaats:
#    - thuisbatterij en algemene pagina's: knop naar de calculator;
#    - pagina's over andere producten (zonnepanelen, warmtepomp, airco, ...): offerte/afspraak voor dat product,
#      met de thuisbatterij als tweede optie. Zo raakt niemand die iets anders zoekt de weg kwijt.
# 3. Zet alle links naar de oude calculator (/bereken-je-prijs, #calculator, #batterijkeuze) om.
# Prijzen komen uit tools/battery.py (PAKKETTEN).
import glob, html, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from battery import PAKKETTEN  # noqa: E402

SHELL = 'artikel-isde-subsidie-2026.html'
SLUG = 'thuisbatterij-berekenen'
URL = '/' + SLUG
TITLE = 'Thuisbatterij berekenen: advies en vaste prijs in 1 minuut | Voltwijk'
DESC = ('Bereken in 1 minuut welke thuisbatterij bij jouw huis past, wat hij kost en wat je bespaart als salderen stopt. '
        'Vaste prijs inclusief installatie door onze eigen monteurs. Vanaf € ' + f"{min(p['prijs'] for p in PAKKETTEN):,}".replace(',', '.') + ' excl. btw.')
TEL, TEL_HREF, WA = '085 333 56 87', 'tel:+31853335687', 'https://wa.me/31853335687'
esc = lambda s: html.escape(s, quote=True)
def eur(n): return '€ ' + f'{int(n):,}'.replace(',', '.')
VANAF = min(p['prijs'] for p in PAKKETTEN)

# Productpagina's van andere producten: daar geen batterijcalculator maar een offerte voor dat product.
ANDERS = {
    'product-zonnepanelen.html': 'zonnepanelen', 'product-warmtepomp.html': 'een warmtepomp', 'product-airco.html': 'een airco',
    'product-laadpaal.html': 'een laadpaal', 'product-boiler.html': 'een elektrische boiler', 'product-meterkast.html': 'een nieuwe meterkast',
}
# Artikelen en lokale pagina's over andere producten herkennen we aan de bestandsnaam
ANDERS_RE = re.compile(r'^artikel-.*(airco|warmtepomp|laadpaal|laden|boiler|cv-ketel|cop-en-scop|isde|inductie|groepen|meterkast|zonnepanelen|omvormer)')
BATTERIJ_RE = re.compile(r'thuisbatterij|batterij|salder|terugle|dynamisch|ems|negatieve|stroomstoring|capaciteitstarief|energiebelasting|netcongestie|vergelijking')

FAQ = [
 ('Hoe nauwkeurig is de berekening?',
  'De calculator geeft een eerlijke indicatie op basis van je antwoorden en gemiddelde stroomprijzen. Wat je echt bespaart, hangt af '
  'van je verbruikspatroon, je panelen en je energiecontract. In het adviesgesprek rekenen we het samen na met je jaarafrekening.'),
 ('Wat verandert er als salderen in 2027 stopt?',
  'Vanaf 1 januari 2027 mag je teruggeleverde stroom niet meer wegstrepen tegen stroom die je later gebruikt. Je krijgt alleen nog een '
  'terugleververgoeding, en veel leveranciers rekenen terugleverkosten. Met een thuisbatterij bewaar je je zonnestroom van overdag '
  'en gebruik je hem zelf, \'s avonds en \'s nachts.'),
 ('Wat zit er in de prijs?',
  'De batterij en hybride omvormer, montage en bekabeling, een eigen groep in de meterkast, het instellen van de app en uitleg bij de '
  'oplevering. Door onze eigen monteurs, met 2 jaar garantie op de installatie. Is er meerwerk nodig, bijvoorbeeld omdat je meterkast '
  'vol zit, dan hoor je dat altijd vooraf, met de prijs erbij.'),
 ('Kan ik de btw terugvragen?',
  'Vaak wel. Gebruik je de batterij met een dynamisch energiecontract en een energiemanagementsysteem om stroom in en te verkopen, '
  'dan kun je je als btw-ondernemer aanmelden en de 21% btw terugvragen. Dat betekent wel wat administratie. Lees de voorwaarden op '
  'belastingdienst.nl (zoek op "thuisbatterij en btw") of vraag het na bij je boekhouder.'),
 ('Ik weet niet of ik 1-fase of 3-fase heb.',
  'Geen probleem. Kies "weet ik niet", dan checken we het samen met een foto van je meterkast. Bij 3-fase wordt het de 16 kWh-batterij '
  'met 8 kW omvormer, bij 1-fase de 10 of 16 kWh met een 1-fase omvormer.'),
 ('Heb ik zonnepanelen nodig?',
  'Nee, maar je haalt er dan minder uit. Zonder panelen bespaar je vooral met een dynamisch contract: laden als stroom goedkoop is, '
  'gebruiken als hij duur is. Zonnepanelen leggen we ook, dus we kunnen beide in één keer regelen.'),
 ('Moet ik nu al iets betalen?',
  'Nee. Je aanvraag is vrijblijvend. Pas nadat we je situatie hebben gecheckt en de installatie samen hebben bevestigd, volgt een '
  'aanbetaling van € 350. Die gaat van de totaalprijs af.'),
]
TRUST = [('12.500+', 'installaties'), ('4,7 / 5', 'op Google'), ('Eigen monteurs', 'geen onderaannemers'),
         ('Vaste prijs', 'inclusief installatie'), ('2 jaar', 'garantie op de installatie')]
STEPS = [
 ('Bereken', 'Zes korte vragen. Je ziet direct welke batterij past, wat hij kost en wat je ongeveer bespaart.'),
 ('Adviesgesprek', 'We bellen je of komen langs. We checken je meterkast (een foto via WhatsApp helpt) en rekenen het samen na.'),
 ('Installatie', 'Onze eigen monteurs plaatsen de batterij, sluiten hem aan op een eigen groep en stellen de app in.'),
 ('Besparen', 'Je gebruikt je eigen zonnestroom ook \'s avonds. Klaar voor het einde van salderen op 1 januari 2027.'),
]

CSS = '''<style>
.tb-page{padding-top:0 !important;}
.tb-hero{background:var(--dark);color:#fff;padding:104px 0 64px;position:relative;overflow:hidden;}
.tb-hero::before{content:"";position:absolute;inset:0;background:radial-gradient(900px 420px at 85% 0%,rgba(111,214,200,.16),transparent 60%);pointer-events:none;}
.tb-grid{position:relative;display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:48px;align-items:start;}
.tb-intro{padding-top:28px;}
.tb-intro .kicker{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--mint);}
.tb-intro h1{font-size:clamp(32px,4.4vw,52px);line-height:1.04;margin-top:14px;color:#fff;}
.tb-intro .l{font-size:17px;color:#D3DFDC;margin-top:16px;line-height:1.6;max-width:520px;}
.tb-ticks{list-style:none;margin:22px 0 0;padding:0;display:grid;gap:10px;}
.tb-ticks li{display:flex;gap:10px;align-items:flex-start;font-size:15px;color:#E6EEEC;line-height:1.45;}
.tb-ticks li::before{content:"";flex:none;width:20px;height:20px;border-radius:50%;margin-top:1px;background:var(--mint) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2310201F' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5'/%3E%3C/svg%3E") center/13px no-repeat;}
.tb-prices{display:flex;flex-wrap:wrap;gap:8px;margin-top:26px;}
.tb-prices span{border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:7px 13px;font-size:13px;color:#D3DFDC;}
.tb-prices b{color:#fff;margin-left:4px;}
.tb-prices small{display:block;flex-basis:100%;font-size:12px;color:var(--dark-text-muted);margin-top:2px;}

.tb-card{background:#fff;color:var(--ink);border-radius:26px;box-shadow:0 40px 80px -36px rgba(0,0,0,.6);overflow:hidden;scroll-margin-top:20px;}
.tb-prog{height:6px;background:var(--surface-tint);}
.tb-prog i{display:block;height:100%;width:0;background:var(--primary);border-radius:0 6px 6px 0;transition:width .35s ease;}
.tb-body{padding:28px 30px 30px;min-height:470px;display:flex;flex-direction:column;}
.tb-top{display:flex;align-items:center;justify-content:space-between;gap:12px;font-size:13px;color:var(--ink-faint);font-weight:700;}
.tb-back{border:0;background:none;color:var(--primary);font:inherit;font-weight:800;cursor:pointer;padding:4px 0;}
.tb-back[hidden]{display:none;}
.tb-q{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:clamp(22px,2.4vw,28px);line-height:1.15;margin:14px 0 4px;letter-spacing:-.01em;text-wrap:balance;}
.tb-sub{font-size:14.5px;color:var(--ink-faint);line-height:1.5;margin-bottom:18px;}
.tb-opts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;}
.tb-opts.one{grid-template-columns:1fr;}
.tb-opt{position:relative;display:flex;align-items:center;gap:14px;text-align:left;border:1.5px solid var(--border);background:#fff;border-radius:18px;padding:16px;cursor:pointer;font:inherit;color:inherit;transition:border-color .15s,box-shadow .15s,transform .15s;}
.tb-opt:hover{border-color:var(--primary);transform:translateY(-1px);box-shadow:0 10px 24px -16px rgba(15,110,107,.6);}
.tb-opt[aria-pressed="true"]{border-color:var(--primary);background:var(--surface-tint);box-shadow:inset 0 0 0 1px var(--primary);}
.tb-opt .ic{flex:none;width:46px;height:46px;border-radius:14px;background:var(--surface-tint);color:var(--primary);display:flex;align-items:center;justify-content:center;}
.tb-opt[aria-pressed="true"] .ic{background:var(--primary);color:#fff;}
.tb-opt b{display:block;font-size:15.5px;line-height:1.25;}
.tb-opt span.d{display:block;font-size:13px;color:var(--ink-faint);margin-top:2px;line-height:1.35;}
.tb-opt.multi::after{content:"";position:absolute;top:12px;right:12px;width:18px;height:18px;border-radius:6px;border:1.5px solid var(--border);background:#fff;}
.tb-opt.multi[aria-pressed="true"]::after{background:var(--primary) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5'/%3E%3C/svg%3E") center/12px no-repeat;border-color:var(--primary);}
.tb-next{margin-top:auto;padding-top:20px;}
.tb-btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;width:100%;border:0;border-radius:999px;background:var(--primary);color:#fff;font:800 16px/1 'Nunito Sans',system-ui,sans-serif;padding:18px 24px;cursor:pointer;text-decoration:none;box-shadow:0 14px 30px -16px rgba(15,110,107,.9);transition:background .15s;}
.tb-btn:hover{background:var(--primary-dark);}
.tb-btn:disabled{opacity:.45;cursor:not-allowed;box-shadow:none;}
.tb-btn.mint{background:var(--mint);color:var(--dark);}
.tb-num{display:flex;align-items:center;gap:0;border:1.5px solid var(--border);border-radius:18px;overflow:hidden;width:max-content;max-width:100%;}
.tb-num button{width:64px;height:64px;border:0;background:var(--surface-tint);color:var(--ink);font:700 28px/1 'Bricolage Grotesque',system-ui,sans-serif;cursor:pointer;}
.tb-num output{min-width:130px;text-align:center;font:700 34px/1 'Bricolage Grotesque',system-ui,sans-serif;}
.tb-num output small{display:block;font:700 11px 'Nunito Sans',sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);margin-top:5px;}
.tb-range{width:100%;margin-top:18px;accent-color:var(--primary);}
.tb-link{border:0;background:none;color:var(--primary);font:inherit;font-weight:800;font-size:14px;cursor:pointer;padding:0;margin-top:14px;text-align:left;}
.tb-field{display:grid;gap:6px;}
.tb-field label{font-size:13.5px;font-weight:800;}
.tb-field input{width:100%;border:1.5px solid var(--border);border-radius:14px;padding:15px 16px;font:600 16px 'Nunito Sans',system-ui,sans-serif;color:var(--ink);background:#fff;}
.tb-field input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px rgba(15,110,107,.15);}
.tb-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;}
.tb-hint{font-size:13px;color:var(--ink-faint);line-height:1.5;background:var(--bg);border-radius:14px;padding:12px 14px;margin-top:14px;}
.tb-err{color:var(--accent-deep);font-size:13.5px;font-weight:700;margin-top:10px;}
.tb-load{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;text-align:center;color:var(--ink-soft);}
.tb-spin{width:46px;height:46px;border-radius:50%;border:4px solid var(--surface-tint);border-top-color:var(--primary);animation:tbspin .8s linear infinite;}
@keyframes tbspin{to{transform:rotate(360deg);}}

/* advies */
.tb-res .tag{display:inline-flex;align-items:center;gap:6px;background:var(--surface-tint);color:var(--primary);font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;border-radius:999px;padding:6px 11px;}
.tb-prod{display:grid;grid-template-columns:120px minmax(0,1fr);gap:18px;align-items:center;margin-top:14px;}
.tb-prod img{width:120px;height:120px;object-fit:cover;border-radius:18px;background:var(--bg);}
.tb-prod h2{font-size:clamp(21px,2.3vw,26px);line-height:1.15;}
.tb-prod p{font-size:13.5px;color:var(--ink-faint);margin-top:4px;}
.tb-price{display:flex;align-items:baseline;flex-wrap:wrap;gap:4px 10px;margin-top:18px;padding:16px 18px;border-radius:18px;background:var(--bg);}
.tb-price b{font:700 38px/1 'Bricolage Grotesque',system-ui,sans-serif;}
.tb-price span{font-size:13.5px;color:var(--ink-soft);}
.tb-price small{flex-basis:100%;font-size:12.5px;color:var(--ink-faint);}
.tb-kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:12px;}
.tb-kpis div{border:1px solid var(--border);border-radius:16px;padding:12px 13px;}
.tb-kpis span{display:block;font-size:12px;font-weight:700;color:var(--ink-faint);line-height:1.3;}
.tb-kpis b{display:block;font:700 19px/1.2 'Bricolage Grotesque',system-ui,sans-serif;margin-top:5px;font-variant-numeric:tabular-nums;}
.tb-why{list-style:none;padding:0;margin:16px 0 0;display:grid;gap:8px;}
.tb-why li{display:flex;gap:10px;font-size:14px;line-height:1.45;color:var(--ink-soft);}
.tb-why li::before{content:"";flex:none;width:18px;height:18px;border-radius:50%;margin-top:1px;background:var(--surface-tint) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230F6E6B' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5'/%3E%3C/svg%3E") center/12px no-repeat;}
.tb-alt{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;align-items:center;font-size:13px;color:var(--ink-faint);}
.tb-alt button{border:1.5px solid var(--border);background:#fff;border-radius:999px;padding:8px 12px;font:700 13px 'Nunito Sans',sans-serif;color:var(--ink);cursor:pointer;}
.tb-alt button[aria-pressed="true"]{border-color:var(--primary);background:var(--surface-tint);}
.tb-form{margin-top:22px;padding-top:20px;border-top:1px solid var(--border);display:grid;gap:12px;}
.tb-form h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:21px;line-height:1.2;}
.tb-form .chk{display:flex;gap:10px;align-items:flex-start;font-size:14px;color:var(--ink-soft);cursor:pointer;}
.tb-form .chk input{width:20px;height:20px;accent-color:var(--primary);flex:none;margin-top:1px;}
.tb-small{font-size:12.5px;color:var(--ink-faint);line-height:1.5;text-align:center;}
.tb-ok{text-align:center;padding:10px 0;}
.tb-ok .big{width:64px;height:64px;border-radius:50%;background:var(--surface-tint);color:var(--primary);display:flex;align-items:center;justify-content:center;margin:0 auto 14px;}
.tb-ok h2{font-size:clamp(24px,2.6vw,30px);}
.tb-ok p{font-size:15px;color:var(--ink-soft);line-height:1.6;margin:10px auto 0;max-width:440px;}
.tb-book{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:22px;text-align:left;}
.tb-book a,.tb-book button{display:flex;flex-direction:column;gap:3px;border:1.5px solid var(--border);border-radius:16px;padding:14px;background:#fff;font:inherit;color:inherit;text-decoration:none;cursor:pointer;text-align:left;}
.tb-book a:hover,.tb-book button:hover{border-color:var(--primary);}
.tb-book b{font-size:14.5px;} .tb-book span{font-size:12.5px;color:var(--ink-faint);line-height:1.35;}

/* onder de calculator */
.tb-sec{padding-top:84px;}
.tb-sec .pill{margin-bottom:12px;}
.tb-h2{font-size:clamp(26px,3.2vw,38px);line-height:1.1;max-width:760px;}
.tb-lead{font-size:16.5px;color:var(--ink-soft);line-height:1.6;margin-top:12px;max-width:640px;}
.tb-trust{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:-30px;position:relative;}
.tb-trust div{background:#fff;border:1px solid var(--border);border-radius:18px;padding:14px 16px;box-shadow:0 18px 40px -30px rgba(16,32,31,.4);}
.tb-trust b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:19px;color:var(--ink);}
.tb-trust span{font-size:12.5px;color:var(--ink-soft);}
.tb-2027{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0;border-radius:24px;overflow:hidden;border:1px solid var(--border);margin-top:26px;}
.tb-2027 > div{padding:26px;background:#fff;}
.tb-2027 > div + div{background:var(--dark);color:#fff;}
.tb-2027 .w{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-faint);}
.tb-2027 > div + div .w{color:var(--mint);}
.tb-2027 h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:22px;margin:8px 0 10px;}
.tb-2027 p{font-size:15px;line-height:1.6;color:var(--ink-soft);}
.tb-2027 > div + div p{color:#D3DFDC;}
.tb-pk{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:26px;}
.tb-pk > div{background:#fff;border:1px solid var(--border);border-radius:22px;padding:22px;display:flex;flex-direction:column;gap:6px;}
.tb-pk > div.hl{border:2px solid var(--primary);}
.tb-pk .lab{font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--primary);min-height:16px;}
.tb-pk h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:24px;line-height:1.1;}
.tb-pk .s{font-size:14px;color:var(--ink-soft);min-height:2.9em;}
.tb-pk .p{font:700 30px/1 'Bricolage Grotesque',system-ui,sans-serif;margin-top:10px;}
.tb-pk .p small{display:block;font:600 12.5px 'Nunito Sans',sans-serif;color:var(--ink-faint);margin-top:6px;}
.tb-pk ul{list-style:none;padding:0;margin:10px 0 14px;display:grid;gap:6px;font-size:14px;color:var(--ink-soft);}
.tb-pk ul li::before{content:"✓";color:var(--primary);font-weight:800;margin-right:8px;}
.tb-pk .tb-btn{margin-top:auto;padding:15px 18px;font-size:14.5px;}
.tb-steps{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:26px;}
.tb-steps div{background:#fff;border:1px solid var(--border);border-radius:20px;padding:20px;}
.tb-steps .n{font:700 30px/1 'Bricolage Grotesque',system-ui,sans-serif;color:var(--primary);}
.tb-steps b{display:block;font-size:16px;margin-top:10px;}
.tb-steps p{font-size:14px;color:var(--ink-soft);line-height:1.55;margin-top:6px;}
.tb-other{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px;margin-top:84px;padding:24px 26px;border-radius:22px;background:var(--surface-tint);}
.tb-other h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:20px;}
.tb-other p{font-size:14.5px;color:var(--ink-soft);margin-top:4px;}
.tb-other .links{display:flex;flex-wrap:wrap;gap:8px;}
.tb-other .links a{background:#fff;border-radius:999px;padding:9px 14px;font-size:13.5px;font-weight:800;color:var(--ink);text-decoration:none;border:1px solid var(--border);}
.tb-faq{max-width:780px;}
.tb-faq .faq summary{font-size:15.5px;}
.tb-faq .faq p{font-size:14.5px;line-height:1.65;max-width:none;}
.tb-end{margin-top:84px;background:var(--dark);border-radius:28px;padding:40px;color:#fff;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px;}
.tb-end h2{color:#fff;font-size:clamp(24px,3vw,32px);}
.tb-end p{color:#C9D6D3;font-size:15px;margin-top:6px;}
.tb-end .tb-btn{width:auto;}
.tb-topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;}
.tb-topbar .vw-logo{height:20px;}
.tb-topbar .r{display:flex;align-items:center;gap:20px;}
.tb-g{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:700;white-space:nowrap;}
.tb-g i{font-style:normal;color:#F5B400;letter-spacing:1px;}
.tb-tel{display:inline-flex;align-items:center;gap:8px;font-weight:800;font-size:15px;color:inherit;text-decoration:none;white-space:nowrap;}
.tb-foot{background:var(--dark);color:#C9D6D3;padding:32px 0 28px;font-size:13px;line-height:1.7;}
.tb-foot .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px 24px;}
.tb-foot a{color:#C9D6D3;}
.tb-sticky{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:70;display:none;}
.tb-sticky.on{display:block;}
.vwp{display:none !important;}
@media (max-width:1000px){.tb-trust{grid-template-columns:repeat(3,minmax(0,1fr));}.tb-steps{grid-template-columns:repeat(2,minmax(0,1fr));}.tb-pk{grid-template-columns:1fr;max-width:520px;}}
@media (max-width:900px){.tb-hero{padding-top:84px;}.tb-grid{grid-template-columns:1fr;gap:22px;}.tb-intro{padding-top:6px;}.tb-ticks,.tb-prices{display:none;}.tb-intro .l{font-size:15.5px;margin-top:10px;}.tb-hero{padding-bottom:48px;}}
@media (max-width:640px){
 .tb-body{padding:22px 18px 22px;min-height:440px;}.tb-opts{grid-template-columns:1fr;gap:10px;}.tb-opt{padding:13px 14px;}.tb-opt .ic{width:40px;height:40px;border-radius:12px;}
 .tb-kpis{grid-template-columns:1fr 1fr;}.tb-kpis div:last-child{grid-column:1/-1;}.tb-prod{grid-template-columns:84px minmax(0,1fr);}.tb-prod img{width:84px;height:84px;}
 .tb-book{grid-template-columns:1fr;}.tb-row{grid-template-columns:1fr;}
 .tb-trust{grid-template-columns:repeat(2,minmax(0,1fr));margin-top:-24px;}.tb-trust div:last-child{grid-column:1/-1;}
 .tb-2027{grid-template-columns:1fr;}.tb-steps{grid-template-columns:1fr;}.tb-end{padding:28px 22px;}.tb-end .tb-btn{width:100%;}
 .tb-g{display:none;}.tb-foot{padding-bottom:96px;}.tb-sec{padding-top:64px;}
}
@media (prefers-reduced-motion:reduce){.tb-prog i,.tb-opt{transition:none;}.tb-spin{animation:none;}}
</style>'''

IC = {
 'zon': '<path d="M12 3v2M12 19v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M3 12h2M19 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/><circle cx="12" cy="12" r="4"/>',
 'geen': '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
 'plus': '<path d="M12 5v14M5 12h14"/><circle cx="12" cy="12" r="10"/>',
 'p1': '<circle cx="12" cy="8" r="3.5"/><path d="M5.5 20a6.5 6.5 0 0 1 13 0"/>',
 'p2': '<circle cx="9" cy="8" r="3"/><circle cx="16.5" cy="9" r="2.5"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0M14 20a4.5 4.5 0 0 1 7 0"/>',
 'p3': '<circle cx="7" cy="8" r="2.6"/><circle cx="17" cy="8" r="2.6"/><circle cx="12" cy="10" r="2.6"/><path d="M2.5 19a4.5 4.5 0 0 1 9 0M12.5 19a4.5 4.5 0 0 1 9 0M7.5 20a4.5 4.5 0 0 1 9 0"/>',
 'kwh': '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
 'auto': '<path d="M5 17h14v-5l-2-5H7l-2 5z"/><circle cx="8" cy="17" r="2"/><circle cx="16" cy="17" r="2"/><path d="M5 12h14"/>',
 'wp': '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="10" cy="12" r="4"/><path d="M17 9v6"/>',
 'airco': '<rect x="2" y="5" width="20" height="8" rx="2"/><path d="M6 17c0 1.5 1 2 2 2M12 16v4M18 17c0 1.5-1 2-2 2"/>',
 'leeg': '<circle cx="12" cy="12" r="9"/><path d="M8 12h8"/>',
 'f1': '<path d="M12 3v18"/><path d="M8 7h8"/>',
 'f3': '<path d="M6 3v18M12 3v18M18 3v18"/>',
 'vraag': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14M12 17.5v.01"/>',
 'euro': '<path d="M17 6.5A7 7 0 1 0 17 17.5"/><path d="M4 10h9M4 14h9"/>',
 'stroom': '<path d="M12 2v6M8 4.5v4M16 4.5v4M6 8h12v4a6 6 0 0 1-12 0zM12 18v4"/>',
 'handel': '<path d="M3 17l5-5 4 4 8-8"/><path d="M15 8h5v5"/>',
 'kal': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
}
def svg(k, s=22): return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                          f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{IC[k]}</svg>')

PK_TXT = {
 'bat10': ('Compact', 'Voor een klein huishouden of een paar panelen.', ['FoxESS all-in-one, 10 kWh', '5 kW hybride omvormer', 'Noodstroom bij stroomuitval']),
 'bat16-1': ('Meest gekozen', 'De meeste opslag voor een 1-fase aansluiting.', ['Dyness LFP-batterij, 16 kWh', 'Solis 6 kW hybride omvormer', 'Werkt met dynamische contracten']),
 'bat16-3': ('Voor 3-fase', 'Meer vermogen, verdeeld over drie fasen.', ['Dyness LFP-batterij, 16 kWh', 'Solis 8 kW hybride omvormer', 'Geschikt bij warmtepomp of laadpaal']),
}

JS = r'''<script>
(function(){
  var PK = __PK__, IC = __IC__, PRIJS = 0.28, SPREAD = 0.08, KWH_PANEEL = 340, EFF = 0.9, UTIL = 0.8;
  var MF = [2.6,4.6,8.1,11.4,13.3,13.2,13.1,11.6,8.8,6.2,3.3,2.2], CF = [10,9,8.9,7.8,7.4,6.8,6.9,7.1,7.5,8.6,9.6,10.4], DG = [31,28,31,30,31,30,31,31,30,31,30,31];
  var card = document.getElementById('calculator'), body = document.getElementById('tbBody'), bar = document.getElementById('tbBar');
  var st = {panelen:null, aantal:12, verbruik:null, extra:{}, fase:null, doel:null, postcode:'', huisnummer:'', keuze:null}, hist = [], cur = 'panelen', started = false;
  try{ var u = new URLSearchParams(location.search), t = {}; ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid','fbclid'].forEach(function(k){ if(u.get(k)) t[k] = u.get(k); });
    if(Object.keys(t).length) sessionStorage.setItem('vwUtm', JSON.stringify(t)); }catch(e){}
  function utm(){ try{ return JSON.parse(sessionStorage.getItem('vwUtm') || '{}'); }catch(e){ return {}; } }
  function track(n, p){ try{ if(window.vwTrack) vwTrack(n, p || {}); }catch(e){} }
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function fmt(n){ return Math.round(n).toLocaleString('nl-NL'); }
  function ic(k){ return '<span class="ic">' + IC[k] + '</span>'; }
  function opt(k, val, title, d, icon, multi){ var on = multi ? !!st[k][val] : st[k] === val;
    return '<button type="button" class="tb-opt' + (multi ? ' multi' : '') + '" data-k="' + k + '" data-v="' + val + '" aria-pressed="' + on + '">' + ic(icon) + '<span><b>' + title + '</b>' + (d ? '<span class="d">' + d + '</span>' : '') + '</span></button>'; }
  var ORDER = ['panelen','aantal','verbruik','extra','fase','doel','adres'];
  function steps(){ return ORDER.filter(function(s){ return s !== 'aantal' || st.panelen === 'ja'; }); }
  function head(q, sub){ var list = ORDER.filter(function(s){ return s !== 'aantal'; }), i = list.indexOf(cur === 'aantal' ? 'panelen' : cur);
    var part = cur === 'aantal' ? .5 : 0;
    bar.style.width = Math.round(((i < 0 ? list.length : i + part) + 1) / (list.length + 1) * 100) + '%';
    return '<div class="tb-top"><button type="button" class="tb-back" id="tbBack"' + (hist.length ? '' : ' hidden') + '>← Terug</button><span>' + (i < 0 ? 'Jouw advies' : 'Vraag ' + (i + 1) + ' van ' + list.length) + '</span></div>' +
      '<h2 class="tb-q">' + q + '</h2>' + (sub ? '<p class="tb-sub">' + sub + '</p>' : ''); }
  function go(next){ if(!started){ started = true; track('calc_start', {pagina: location.pathname}); } hist.push(cur); cur = next; render(true); track('calc_stap', {stap: next}); }
  function back(){ if(!hist.length) return; cur = hist.pop(); render(true); }
  function nextOf(s){ var l = steps(); return l[l.indexOf(s) + 1] || 'laden'; }

  function render(scroll){
    var h = '';
    if(cur === 'panelen'){
      h = head('Heb je zonnepanelen?', 'Dan bepalen we hoeveel zonnestroom je kunt opslaan.') + '<div class="tb-opts one">' +
        opt('panelen','ja','Ja, ik heb zonnepanelen','Je slaat je eigen stroom van overdag op','zon') +
        opt('panelen','straks','Nog niet, maar ik wil ze erbij','Dan nemen we panelen mee in je advies','plus') +
        opt('panelen','nee','Nee, alleen een batterij','Je bespaart dan vooral met een dynamisch contract','geen') + '</div>';
    } else if(cur === 'aantal'){
      h = head('Hoeveel zonnepanelen heb je?', 'Een schatting is goed genoeg.') +
        '<div class="tb-num"><button type="button" data-n="-1" aria-label="Minder panelen">−</button><output id="tbN">' + st.aantal + '<small>panelen</small></output><button type="button" data-n="1" aria-label="Meer panelen">+</button></div>' +
        '<input class="tb-range" type="range" id="tbNr" min="4" max="40" value="' + st.aantal + '" aria-label="Aantal panelen">' +
        '<p class="tb-hint">Dat is ongeveer <b id="tbOpw">' + fmt(st.aantal * KWH_PANEEL) + ' kWh</b> zonnestroom per jaar.</p>' +
        '<div class="tb-next"><button type="button" class="tb-btn" data-go>Volgende →</button></div>';
    } else if(cur === 'verbruik'){
      var vb = st.verbruik, eigen = vb && [2300,3500,4800].indexOf(vb) < 0;
      h = head('Hoeveel stroom gebruik je per jaar?', 'Staat op je jaarafrekening. Weet je het niet, kies dan je huishouden.') + '<div class="tb-opts">' +
        opt('verbruik',2300,'1 of 2 personen','ca. 2.300 kWh','p1') + opt('verbruik',3500,'3 of 4 personen','ca. 3.500 kWh','p2') +
        opt('verbruik',4800,'5 personen of meer','ca. 4.800 kWh','p3') +
        '<button type="button" class="tb-opt" id="tbEigen" aria-pressed="' + !!eigen + '">' + ic('kwh') + '<span><b>Ik weet het precies</b><span class="d">Vul je verbruik in</span></span></button></div>' +
        '<div id="tbEigenBox"' + (eigen ? '' : ' hidden') + ' style="margin-top:14px;"><div class="tb-field"><label for="tbKwh">Verbruik per jaar (kWh)</label><input id="tbKwh" type="number" inputmode="numeric" min="500" max="30000" step="100" value="' + (eigen ? vb : '') + '" placeholder="bijvoorbeeld 3200"></div>' +
        '<div class="tb-next"><button type="button" class="tb-btn" id="tbKwhGo">Volgende →</button></div></div>';
    } else if(cur === 'extra'){
      h = head('Heb je (straks) een van deze?', 'Die gebruiken veel stroom, ook \'s avonds. Kies alles wat geldt.') + '<div class="tb-opts">' +
        opt('extra','ev','Elektrische auto','of je krijgt er binnenkort een','auto',1) + opt('extra','wp','Warmtepomp','hybride of volledig','wp',1) +
        opt('extra','airco','Airco','koelen en verwarmen','airco',1) +
        '<button type="button" class="tb-opt" id="tbGeen" aria-pressed="' + (st.extraGezien && !Object.keys(st.extra).some(function(k){ return st.extra[k]; })) + '">' + ic('leeg') + '<span><b>Geen van deze</b></span></button></div>' +
        '<div class="tb-next"><button type="button" class="tb-btn" data-go>Volgende →</button></div>';
    } else if(cur === 'fase'){
      h = head('Wat voor aansluiting heb je?', 'Dat bepaalt welke omvormer je nodig hebt.') + '<div class="tb-opts one">' +
        opt('fase','1','1-fase','De meeste woningen. Eén hoofdschakelaar, meestal 1 x 35 A.','f1') +
        opt('fase','3','3-fase','Drie hoofdzekeringen of 3 x 25 A op je energierekening.','f3') +
        opt('fase','?','Weet ik niet','Geen probleem, we checken het samen met een foto van je meterkast.','vraag') + '</div>';
    } else if(cur === 'doel'){
      h = head('Wat vind je het belangrijkst?', 'Dan stemmen we het advies daarop af.') + '<div class="tb-opts">' +
        opt('doel','besparen','Zoveel mogelijk besparen','Eigen zonnestroom zelf gebruiken','euro') +
        opt('doel','2027','Klaar zijn voor 2027','Als salderen stopt','kal') +
        opt('doel','noodstroom','Stroom bij een storing','Noodstroom als het net uitvalt','stroom') +
        opt('doel','handel','Slim handelen','Met een dynamisch energiecontract','handel') + '</div>';
    } else if(cur === 'adres'){
      h = head('Waar komt de batterij?', 'Dan zien we wanneer onze monteurs bij jou kunnen installeren.') +
        '<div class="tb-row"><div class="tb-field"><label for="tbPc">Postcode</label><input id="tbPc" autocomplete="postal-code" placeholder="4762 AS" value="' + esc(st.postcode) + '" maxlength="7"></div>' +
        '<div class="tb-field"><label for="tbHn">Huisnummer</label><input id="tbHn" inputmode="numeric" placeholder="15" value="' + esc(st.huisnummer) + '" maxlength="8"></div></div>' +
        '<div id="tbAdrErr" class="tb-err" hidden></div>' +
        '<div class="tb-next"><button type="button" class="tb-btn" id="tbAdrGo">Bekijk mijn advies en prijs →</button><p class="tb-small" style="margin-top:10px;">Je ziet je advies direct. Je zit nergens aan vast.</p></div>';
    } else if(cur === 'laden'){
      bar.style.width = '100%';
      h = '<div class="tb-load"><div class="tb-spin"></div><b style="font-size:17px;color:var(--ink);">Je advies wordt berekend…</b><span>We vergelijken onze drie batterijen met jouw situatie.</span></div>';
      setTimeout(function(){ cur = 'advies'; st.keuze = advies(); track('calc_advies', {batterij: st.keuze}); render(false); }, 1100);
    } else if(cur === 'advies'){ h = resultaat(); }
    else if(cur === 'klaar'){ h = klaar(); }
    body.innerHTML = h; wire();
    if(scroll){ var r = card.getBoundingClientRect(); if(r.top < 0 || r.top > innerHeight * .5) card.scrollIntoView({behavior: 'smooth', block: 'start'}); }
  }

  function wire(){
    var b = document.getElementById('tbBack'); if(b) b.onclick = back;
    body.querySelectorAll('.tb-opt[data-k]').forEach(function(el){ el.onclick = function(){
      var k = el.dataset.k, v = el.dataset.v; if(k === 'verbruik') v = +v;
      if(k === 'extra'){ st.extra[v] = !st.extra[v]; st.extraGezien = true; render(false); return; }
      st[k] = v; render(false); setTimeout(function(){ go(nextOf(cur)); }, 160); }; });
    body.querySelectorAll('[data-go]').forEach(function(el){ el.onclick = function(){ if(cur === 'extra') st.extraGezien = true; go(nextOf(cur)); }; });
    body.querySelectorAll('[data-n]').forEach(function(el){ el.onclick = function(){ setN(st.aantal + (+el.dataset.n)); }; });
    var r = document.getElementById('tbNr'); if(r) r.oninput = function(){ setN(+r.value); };
    var e = document.getElementById('tbEigen'); if(e) e.onclick = function(){ document.getElementById('tbEigenBox').hidden = false; e.setAttribute('aria-pressed', 'true'); document.getElementById('tbKwh').focus(); };
    var kg = document.getElementById('tbKwhGo'); if(kg) kg.onclick = function(){ var v = +document.getElementById('tbKwh').value; if(v >= 500 && v <= 30000){ st.verbruik = Math.round(v); go(nextOf(cur)); } else document.getElementById('tbKwh').focus(); };
    var g = document.getElementById('tbGeen'); if(g) g.onclick = function(){ st.extra = {}; st.extraGezien = true; go(nextOf(cur)); };
    var ag = document.getElementById('tbAdrGo'); if(ag) ag.onclick = adres;
    ['tbPc','tbHn'].forEach(function(id){ var x = document.getElementById(id); if(x) x.onkeydown = function(ev){ if(ev.key === 'Enter') adres(); }; });
    body.querySelectorAll('[data-alt]').forEach(function(el){ el.onclick = function(){ st.keuze = el.dataset.alt; render(false); track('calc_wissel', {batterij: st.keuze}); }; });
    var f = document.getElementById('tbForm'); if(f) f.addEventListener('submit', verstuur);
  }
  function setN(n){ st.aantal = Math.max(4, Math.min(40, n)); var o = document.getElementById('tbN'); if(o) o.firstChild.textContent = st.aantal;
    var r = document.getElementById('tbNr'); if(r) r.value = st.aantal; var w = document.getElementById('tbOpw'); if(w) w.textContent = fmt(st.aantal * KWH_PANEEL) + ' kWh'; }
  function adres(){ var pc = document.getElementById('tbPc').value.trim().toUpperCase().replace(/^(\d{4})\s*([A-Z]{2})$/, '$1 $2'), hn = document.getElementById('tbHn').value.trim(), er = document.getElementById('tbAdrErr');
    if(!/^\d{4} [A-Z]{2}$/.test(pc)){ er.textContent = 'Vul je postcode in, bijvoorbeeld 4762 AS.'; er.hidden = false; return; }
    if(!/^\d+/.test(hn)){ er.textContent = 'Vul je huisnummer in.'; er.hidden = false; return; }
    st.postcode = pc; st.huisnummer = hn; go('laden'); }

  /* ---------- advies en besparing (indicatie) ---------- */
  function verbruik(){ var v = st.verbruik || 3500; if(st.extra.ev) v += 2000; if(st.extra.wp) v += 2500; if(st.extra.airco) v += 400; return v; }
  function opwek(){ return st.panelen === 'ja' ? st.aantal * KWH_PANEEL : st.panelen === 'straks' ? 12 * KWH_PANEEL : 0; }
  function advies(){
    if(st.fase === '3') return 'bat16-3';
    var groot = verbruik() >= 3200 || st.extra.ev || st.extra.wp || st.doel === 'handel' || opwek() >= 4400;
    return groot ? 'bat16-1' : 'bat10';
  }
  function reken(id){
    var p = PK[id], use = p.kwh * 0.95, C = verbruik(), P = opwek(), tot = {direct:0, extra:0, arb:0, prod:P};
    for(var i = 0; i < 12; i++){
      var prod = P * MF[i] / 98.4, cons = C * CF[i] / 100, direct = Math.min(prod, cons * .35), sur = prod - direct, rest = cons - direct;
      var cap = use * DG[i] * UTIL, extra = Math.min(sur * EFF, rest, cap), arb = Math.min(Math.max(0, cap - extra), rest - extra);
      tot.direct += direct; tot.extra += extra; tot.arb += arb;
    }
    var dyn = st.doel === 'handel' || st.panelen === 'nee';
    var besparing = tot.extra * PRIJS + (dyn ? tot.arb * (SPREAD - (1 / EFF - 1) * (PRIJS - SPREAD)) : 0);
    tot.besparing = besparing; tot.dyn = dyn;
    tot.zelfZonder = P ? tot.direct / P : 0; tot.zelfMet = P ? (tot.direct + tot.extra / EFF) / P : 0;
    return tot;
  }
  function range(v){ var lo = Math.floor(v * .85 / 10) * 10, hi = Math.ceil(v * 1.15 / 10) * 10; return '€ ' + fmt(lo) + ' – ' + fmt(hi); }
  function waarom(id){
    var p = PK[id], w = [];
    w.push(p.fase === '3-fase' ? 'Je hebt een 3-fase aansluiting: de 8 kW omvormer verdeelt het vermogen over alle drie de fasen.' :
      st.fase === '?' ? 'We gaan uit van een 1-fase aansluiting. Blijkt het 3-fase, dan wordt het de 16 kWh met 8 kW omvormer (' + '€ ' + fmt(PK['bat16-3'].prijs) + ').' :
      'Past bij je 1-fase aansluiting, met een ' + p.kw + ' kW hybride omvormer.');
    if(st.panelen === 'ja') w.push('Met ' + st.aantal + ' panelen maak je ongeveer ' + fmt(opwek()) + ' kWh per jaar. Een groot deel daarvan komt overdag, als je weinig gebruikt.');
    if(st.panelen === 'straks') w.push('Zonnepanelen leggen we ook. Voor deze berekening gaan we uit van 12 panelen; in het adviesgesprek rekenen we panelen en batterij samen door.');
    if(st.panelen === 'nee') w.push('Zonder zonnepanelen bespaar je vooral met een dynamisch contract: laden als stroom goedkoop is, gebruiken als hij duur is.');
    if(st.extra.ev || st.extra.wp) w.push('Met ' + [st.extra.ev && 'een elektrische auto', st.extra.wp && 'een warmtepomp'].filter(Boolean).join(' en ') + ' gebruik je \'s avonds veel stroom. Dan loont meer opslag.');
    if(st.doel === 'noodstroom') w.push('Valt de stroom uit, dan levert de batterij noodstroom aan je huis.');
    if(st.doel === 'handel') w.push('Werkt met dynamische contracten en slimme energiemanagementsystemen, zodat je kunt handelen.');
    if((st.doel === '2027' || st.doel === 'besparen') && st.panelen !== 'nee') w.push('Vanaf 1 januari 2027 stopt salderen. Elke kWh die je zelf gebruikt in plaats van teruglevert, is dan meer waard.');
    return w;
  }
  function resultaat(){
    var id = st.keuze, p = PK[id], r = reken(id), alt = Object.keys(PK);
    bar.style.width = '100%';
    var kp = [
      ['Geschatte besparing', r.besparing > 25 ? range(r.besparing) + '<span style="font:600 12px Nunito Sans,sans-serif;color:var(--ink-faint);"> per jaar</span>' : 'Bespreken we samen'],
      [opwek() ? 'Eigen zonnestroom zelf gebruikt' : 'Opslag', opwek() ? Math.round(r.zelfZonder * 100) + '% → ' + Math.round(Math.min(.95, r.zelfMet) * 100) + '%' : p.kwh + ' kWh'],
      ['Installatie al vanaf', '<span data-vw-first></span>']];
    return '<div class="tb-res">' + head('Dit is je advies') .replace('<h2 class="tb-q">Dit is je advies</h2>', '') +
      '<span class="tag">Past het best bij jou</span>' +
      '<div class="tb-prod"><img src="/images/thumb-batterij.webp" alt="" width="120" height="120"><div><h2 class="vw-heading">Thuisbatterij ' + p.kwh + ' kWh met ' + p.kw + ' kW omvormer</h2><p>' + esc(p.merk) + ' · ' + p.fase + ' · vaste prijs inclusief installatie</p></div></div>' +
      '<div class="tb-price"><b>€ ' + fmt(p.prijs) + '</b><span>incl. installatie, excl. btw</span><small>€ ' + fmt(p.prijs * 1.21) + ' incl. btw. Gebruik je een dynamisch contract, dan kun je de btw vaak terugvragen.</small></div>' +
      '<div class="tb-kpis">' + kp.map(function(k){ return '<div><span>' + k[0] + '</span><b>' + k[1] + '</b></div>'; }).join('') + '</div>' +
      '<ul class="tb-why">' + waarom(id).map(function(t){ return '<li>' + esc(t) + '</li>'; }).join('') + '</ul>' +
      '<div class="tb-alt"><span>Vergelijk:</span>' + alt.map(function(a){ return '<button type="button" data-alt="' + a + '" aria-pressed="' + (a === id) + '">' + PK[a].kwh + ' kWh ' + PK[a].fase + ' · € ' + fmt(PK[a].prijs) + '</button>'; }).join('') + '</div>' +
      '<form class="tb-form" id="tbForm" name="thuisbatterij-advies" novalidate><h3>Vraag je gratis adviesgesprek aan</h3>' +
      '<p style="font-size:14px;color:var(--ink-soft);line-height:1.5;margin-top:-4px;">We bellen je om je situatie te checken en het advies samen door te rekenen. Daarna krijg je een offerte met vaste prijs.</p>' +
      '<p hidden><label>Niet invullen <input name="bot-field"></label></p>' +
      '<div class="tb-field"><label for="tbNaam">Naam</label><input id="tbNaam" name="naam" autocomplete="name" required></div>' +
      '<div class="tb-row"><div class="tb-field"><label for="tbTel">Telefoon</label><input id="tbTel" name="telefoon" type="tel" autocomplete="tel" inputmode="tel" required></div>' +
      '<div class="tb-field"><label for="tbMail">E-mail</label><input id="tbMail" name="email" type="email" autocomplete="email" required></div></div>' +
      (st.panelen !== 'ja' ? '<label class="chk"><input type="checkbox" id="tbZp"' + (st.panelen === 'straks' ? ' checked' : '') + '> Neem ook zonnepanelen mee in mijn advies</label>' : '') +
      '<div id="tbFormErr" class="tb-err" hidden></div>' +
      '<button type="submit" class="tb-btn">Vraag gratis adviesgesprek aan →</button>' +
      '<p class="tb-small">Gratis en vrijblijvend · je betaalt nu niets · wij bellen je, geen callcenter</p></form>' +
      '<p class="tb-small" style="margin-top:14px;">Besparing is een indicatie vanaf 2027, bij € 0,28 per kWh en zonder salderen. In het gesprek rekenen we het na met je jaarafrekening.</p></div>';
  }
  function verstuur(e){
    e.preventDefault(); var f = e.target, er = document.getElementById('tbFormErr'), v = function(n){ return (f.elements[n].value || '').trim(); };
    var fout = !v('naam') ? 'Vul je naam in.' : !/^[+0-9 ()-]{10,}$/.test(v('telefoon')) ? 'Vul een geldig telefoonnummer in.' : !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v('email')) ? 'Vul een geldig e-mailadres in.' : '';
    if(fout){ er.textContent = fout; er.hidden = false; return; }
    var p = PK[st.keuze], r = reken(st.keuze), zp = document.getElementById('tbZp'), btn = f.querySelector('button[type=submit]'), t = utm();
    var velden = {'form-name':'thuisbatterij-advies', 'bot-field':v('bot-field'), naam:v('naam'), telefoon:v('telefoon'), email:v('email'),
      postcode:st.postcode, huisnummer:st.huisnummer, advies:'Thuisbatterij ' + p.kwh + ' kWh + ' + p.kw + ' kW omvormer (' + p.fase + ')', prijs:'€ ' + fmt(p.prijs) + ' excl. btw',
      zonnepanelen:st.panelen === 'ja' ? 'ja, ca. ' + st.aantal + ' panelen' : st.panelen === 'straks' ? 'nog niet, wil ze erbij' : 'nee',
      ook_zonnepanelen:zp && zp.checked ? 'ja' : '', verbruik:fmt(st.verbruik || 3500) + ' kWh',
      extra:['ev','wp','airco'].filter(function(k){ return st.extra[k]; }).map(function(k){ return {ev:'elektrische auto', wp:'warmtepomp', airco:'airco'}[k]; }).join(', ') || 'geen',
      aansluiting:st.fase === '?' ? 'weet ik niet' : st.fase + '-fase', belangrijk:{besparen:'zoveel mogelijk besparen', '2027':'klaar zijn voor 2027', noodstroom:'noodstroom', handel:'slim handelen'}[st.doel] || '',
      geschatte_besparing:r.besparing > 25 ? range(r.besparing) + ' per jaar' : '', pagina:location.pathname,
      bron:[t.utm_source, t.utm_medium, t.utm_campaign].filter(Boolean).join(' / '), utm_content:t.utm_content || '', gclid:t.gclid || '', fbclid:t.fbclid || ''};
    var bd = Object.keys(velden).map(function(k){ return encodeURIComponent(k) + '=' + encodeURIComponent(velden[k]); }).join('&');
    var txt = btn.innerHTML; btn.disabled = true; btn.innerHTML = 'Versturen…'; er.hidden = true;
    fetch('/', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:bd}).then(function(res){
      if(!res.ok) throw new Error(res.status);
      track('aanvraag_batterij', {value:p.prijs, currency:'EUR', batterij:st.keuze});
      st.naam = v('naam'); hist = []; cur = 'klaar'; render(true);
    }).catch(function(){
      btn.disabled = false; btn.innerHTML = txt; er.hidden = false;
      er.innerHTML = 'Versturen lukte niet. Bel ons op <a href="tel:+31853335687" style="color:inherit;">085 333 56 87</a> of app via <a href="https://wa.me/31853335687" style="color:inherit;">WhatsApp</a>.';
    });
  }
  function klaar(){
    bar.style.width = '100%'; var p = PK[st.keuze];
    return '<div class="tb-ok"><div class="big">' + IC.kal.replace('width="22" height="22"', 'width="30" height="30"') + '</div><h2 class="vw-heading">Bedankt, ' + esc((st.naam || '').split(' ')[0]) + '! Je aanvraag is binnen.</h2>' +
      '<p>We bellen je zo snel mogelijk over de thuisbatterij van ' + p.kwh + ' kWh. Wil je niet wachten? Plan meteen zelf een moment dat jou uitkomt.</p>' +
      '<div class="tb-book"><button type="button" data-book="bel"><b>Belafspraak</b><span>15 min, wij bellen jou</span></button><button type="button" data-book="huis"><b>Adviseur aan huis</b><span>we kijken naar je meterkast en woning</span></button>' +
      '<a href="https://wa.me/31853335687?text=' + encodeURIComponent('Hoi Voltwijk, ik heb net een advies voor een thuisbatterij aangevraagd. Hier een foto van mijn meterkast:') + '" target="_blank" rel="noopener"><b>Foto meterkast sturen</b><span>via WhatsApp, dan gaat het nog sneller</span></a></div></div>';
  }
  render(false);
  document.querySelectorAll('[data-tb-start]').forEach(function(a){ a.addEventListener('click', function(e){ e.preventDefault(); card.scrollIntoView({behavior: 'smooth', block: 'start'}); var p = a.getAttribute('data-tb-start'); if(p && cur === 'advies' && PK[p]){ st.keuze = p; render(false); } }); });
  var sticky = document.getElementById('tbSticky');
  if(sticky && 'IntersectionObserver' in window){ var vis = true; new IntersectionObserver(function(es){ vis = es[0].isIntersecting; sticky.classList.toggle('on', !vis && innerWidth < 900 && cur !== 'klaar'); }).observe(card); }
})();
</script>'''

def nav_html(logo):
    return f'''<div id="siteNav">
    <div class="wrap nav-inner tb-topbar">
      <a href="/" aria-label="Voltwijk, naar de homepage" class="vw-heading" style="display:inline-flex;align-items:center;color:inherit;">{logo}</a>
      <div class="r"><a class="tb-tel" href="{TEL_HREF}" aria-label="Bel Voltwijk: {TEL}"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg><span>{TEL}</span></a></div>
    </div>
  </div>'''

def pk_js():
    out = {}
    merk = {'bat10': 'FoxESS all-in-one', 'bat16-1': 'Dyness LFP + Solis', 'bat16-3': 'Dyness LFP + Solis'}
    for p in PAKKETTEN: out[p['id']] = {'kwh': p['kwh'], 'kw': p['kw'], 'fase': p['fase'], 'prijs': p['prijs'], 'merk': merk.get(p['id'], '')}
    return json.dumps(out, ensure_ascii=False)

def main_html():
    icjson = json.dumps({k: svg(k) for k in IC}, ensure_ascii=False)
    # Eén ding op de pagina: de calculator, groot en in het midden. Geen prijzen, blokken of andere afleiding eromheen.
    return f'''<div class="blk-light tb-page">
  {CSS}
  <style>
  .tb-page{{padding-top:0 !important;background:var(--dark);}}
  .tb-solo{{min-height:100vh;min-height:100svh;display:flex;flex-direction:column;align-items:center;padding:96px 16px 40px;
    background:radial-gradient(900px 480px at 50% -10%,rgba(111,214,200,.16),transparent 65%),var(--dark);}}
  .tb-solo .wrapc{{width:100%;max-width:720px;}}
  .tb-solo h1{{color:#fff;text-align:center;font-size:clamp(28px,4vw,44px);line-height:1.08;}}
  .tb-solo .sub{{color:#C9D6D3;text-align:center;font-size:16.5px;margin:12px auto 26px;max-width:520px;line-height:1.55;}}
  .tb-solo .tb-card{{box-shadow:0 50px 100px -40px rgba(0,0,0,.7);}}
  .tb-solo .tb-body{{padding:34px 38px 36px;min-height:520px;}}
  .tb-solo .tb-q{{font-size:clamp(24px,2.8vw,32px);}}
  .tb-solo .tb-opt{{padding:20px 18px;}}
  .tb-solo .tb-opt b{{font-size:17px;}}
  .tb-mini{{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 18px;margin-top:20px;color:#9FB0AD;font-size:13px;font-weight:700;}}
  .tb-mini i{{font-style:normal;color:#F5B400;letter-spacing:1px;margin-right:4px;}}
  #waWidget{{display:none !important;}}
  #vwCookie{{padding:12px 14px !important;}}#vwCookie .ck-title{{display:none;}}
  #vwCookie p{{margin:0 0 10px !important;font-size:12px !important;line-height:1.45 !important;}}
  #vwCookie .ck-btns{{flex-wrap:nowrap;}}#vwCookie .ck-btns button{{flex:1;padding:10px 12px !important;font-size:13px !important;}}
  .tb-foot{{padding:18px 0;}}
  @media (max-width:640px){{.tb-solo{{padding-top:80px;}}.tb-solo .sub{{font-size:15px;margin-bottom:18px;}}.tb-solo .tb-body{{padding:24px 18px 24px;min-height:460px;}}.tb-solo .tb-opt{{padding:15px 14px;}}}}
  </style>
  <div class="tb-solo">
    <div class="wrapc">
      <h1 class="vw-heading">Welke thuisbatterij past bij jouw huis?</h1>
      <p class="sub">Beantwoord 6 korte vragen en zie direct je advies en vaste prijs, inclusief installatie.</p>
      <div class="tb-card" id="calculator" aria-live="polite">
        <div class="tb-prog"><i id="tbBar"></i></div>
        <div class="tb-body" id="tbBody"><noscript>Zet JavaScript aan om de calculator te gebruiken, of bel ons op {TEL}.</noscript></div>
      </div>
      <div class="tb-mini"><span><i>★★★★★</i>4,7 / 5 op Google</span><span>12.500+ installaties</span><span>Eigen monteurs</span></div>
    </div>
  </div>
  <form name="thuisbatterij-advies" data-netlify="true" netlify-honeypot="bot-field" hidden>
    <input name="bot-field"><input name="naam"><input name="telefoon"><input name="email"><input name="postcode"><input name="huisnummer">
    <input name="advies"><input name="prijs"><input name="zonnepanelen"><input name="ook_zonnepanelen"><input name="verbruik"><input name="extra">
    <input name="aansluiting"><input name="belangrijk"><input name="geschatte_besparing"><input name="pagina"><input name="bron"><input name="utm_content"><input name="gclid"><input name="fbclid">
  </form>
  {JS.replace('__PK__', pk_js()).replace('__IC__', icjson)}
</div>
'''

FOOT = f'''<div class="tb-foot">
    <div class="wrap">
      <span><b style="color:#fff;">Voltwijk B.V.</b> · Schoenmakerij 15a, 4762 AS Zevenbergen · <a href="{TEL_HREF}">{TEL}</a> · <a href="mailto:info@voltwijk.nl">info@voltwijk.nl</a></span>
      <span><a href="/privacybeleid">Privacy</a> · <a href="/cookiebeleid">Cookies</a> · <a href="/algemene-voorwaarden">Voorwaarden</a></span>
    </div>
  </div>

'''

def build_page():
    shell = open(SHELL, encoding='utf-8').read()
    logo = re.search(r'<svg[^>]*class="vw-logo".*?</svg>', shell, re.S).group(0)
    s = shell
    s, k1 = re.subn(r'<div id="siteNav">.*?(?=\n\n\n?<div class="blk-light" style="padding-top:40px;">)', lambda m: nav_html(logo), s, count=1, flags=re.S)
    s, k2 = re.subn(r'<div class="blk-light" style="padding-top:40px;">.*?(?=<div class="site-footer")', lambda m: main_html() + '\n', s, count=1, flags=re.S)
    s, k3 = re.subn(r'<div class="site-footer".*?(?=<style>@keyframes waPulse)', lambda m: FOOT, s, count=1, flags=re.S)
    assert k1 == k2 == k3 == 1, ('schil niet herkend', k1, k2, k3)
    s = re.sub(r'<title>.*?</title>', '<title>' + esc(TITLE) + '</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + esc(DESC) + '">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://voltwijk.nl/{SLUG}">', s, count=1)
    s = re.sub(r'\n?<meta property="article:(published|modified)_time"[^>]*>', '', s)
    s = re.sub(r'\n?<meta name="robots" content="noindex">', '', s)
    for tag in ('seo', 'rel', 'vw-cal', 'vw-plan', 'vw-order', 'vw-analytics', 'vw-funnel-cta'):
        s = re.sub(r'\n?<!-- ' + tag + r':start -->.*?<!-- ' + tag + r':end -->', '', s, flags=re.S)
    s = re.sub(r'\n?<!--vw-batterijkeuze-->.*?<!--/vw-batterijkeuze-->', '', s, flags=re.S)
    s = s.replace('bereken: "/bereken-je-prijs"', 'bereken: "' + URL + '"')
    s = s.replace("var topic = TOPIC[slug];", "var topic = TOPIC[slug] || (slug === '" + SLUG + "' ? 'een thuisbatterij' : '');", 1)
    open(SLUG + '.html', 'w', encoding='utf-8').write(s)

# ---------- de rest van de site ----------
def band(f):
    """Het blok dat op de plek van de oude calculator komt."""
    prod = ANDERS.get(f)
    if prod:
        return f'''<!-- vw-funnel-cta:start --><div id="offerte" class="wrap reveal" style="padding-top:56px;padding-bottom:64px;scroll-margin-top:70px;">
  <div style="background:var(--dark);color:#fff;border-radius:28px;padding:clamp(26px,4vw,44px);display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:28px;align-items:center;" class="vwf-grid">
    <div><div style="font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--mint);">Vaste prijs · eigen monteurs</div>
      <h2 class="vw-heading" style="color:#fff;font-size:clamp(26px,3.2vw,38px);margin-top:10px;line-height:1.1;">Offerte voor {esc(prod)}?</h2>
      <p style="color:#C9D6D3;font-size:15.5px;line-height:1.6;margin-top:12px;max-width:520px;">Plan een gratis adviesgesprek. We kijken naar je woning en meterkast en sturen je een offerte met een vaste prijs, inclusief installatie.</p>
      <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:20px;"><a href="/contact" data-book="" class="btn-primary" style="background:var(--mint);color:var(--dark);text-decoration:none;">Plan gratis adviesgesprek →</a><a href="{WA}?text=Hoi%20Voltwijk%2C%20ik%20wil%20graag%20een%20offerte" target="_blank" rel="noopener" class="btn-secondary" style="color:#fff;border-color:rgba(255,255,255,.5);text-decoration:none;">App ons</a></div></div>
    <a href="{URL}" style="display:block;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);border-radius:20px;padding:20px;color:#fff;text-decoration:none;">
      <span style="font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--mint);">Ook interessant</span>
      <b class="vw-heading" style="display:block;font-size:20px;margin-top:6px;">Bewaar je zonnestroom met een thuisbatterij</b>
      <span style="display:block;font-size:14px;color:#C9D6D3;margin-top:6px;line-height:1.5;">Salderen stopt op 1 januari 2027. Bereken in 1 minuut welke batterij past. Vanaf {eur(VANAF).replace(' ', '&nbsp;')} incl. installatie, excl. btw.</span>
      <span style="display:inline-block;font-weight:800;font-size:14px;color:var(--mint);margin-top:12px;">Bereken je thuisbatterij →</span></a>
  </div>
  <style>@media (max-width:820px){{.vwf-grid{{grid-template-columns:1fr !important;}}}}</style>
</div><!-- vw-funnel-cta:end -->'''
    return f'''<!-- vw-funnel-cta:start --><div id="calculator" class="wrap reveal" style="padding-top:56px;padding-bottom:64px;scroll-margin-top:70px;">
  <a href="{URL}" class="vwf-band" style="display:grid;grid-template-columns:minmax(0,1.4fr) auto;gap:24px;align-items:center;background:var(--dark);color:#fff;border-radius:28px;padding:clamp(26px,4vw,44px);text-decoration:none;">
    <span><span style="display:block;font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--mint);">Thuisbatterij berekenen · 1 minuut</span>
      <span class="vw-heading" style="display:block;font-size:clamp(26px,3.2vw,38px);margin-top:10px;line-height:1.1;">Welke thuisbatterij past bij jouw huis?</span>
      <span style="display:block;color:#C9D6D3;font-size:15.5px;line-height:1.6;margin-top:12px;max-width:560px;">Zes korte vragen. Je ziet direct je advies, de vaste prijs inclusief installatie en wat je ongeveer bespaart als salderen stopt. Vanaf {eur(VANAF).replace(' ', '&nbsp;')} excl. btw.</span></span>
    <span class="btn-primary" style="background:var(--mint);color:var(--dark);white-space:nowrap;">Bereken je thuisbatterij →</span>
  </a>
  <style>@media (max-width:820px){{.vwf-band{{grid-template-columns:1fr !important;}}.vwf-band .btn-primary{{justify-content:center;}}}}</style>
</div><!-- vw-funnel-cta:end -->'''

def remove_div(s, start):
    """Verwijder het <div> dat op positie start begint, inclusief alle geneste divs."""
    depth, i = 0, start
    for m in re.finditer(r'<div\b|</div>', s[start:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0: return s[:start], s[start + m.end():]
    raise ValueError('div niet gesloten')

def anders(f):
    return f in ANDERS or (ANDERS_RE.search(f) and not BATTERIJ_RE.search(f))

def patch(f, s):
    s = re.sub(r'<!-- vw-funnel-cta:start -->.*?<!-- vw-funnel-cta:end -->', '<!--vw-calc-plek-->', s, flags=re.S)
    m = re.search(r'<div id="calculator"', s)
    if m:
        a, b = remove_div(s, m.start()); s = a + '<!--vw-calc-plek-->' + b
    s = re.sub(r'\n?<!--vw-batterijkeuze-->.*?<!--/vw-batterijkeuze-->', '', s, flags=re.S)
    if '<!--vw-calc-plek-->' in s:
        s = s.replace('<!--vw-calc-plek-->', band(f), 1).replace('<!--vw-calc-plek-->', '')
    s = s.replace('<!--vw-batterijkeuze-plek-->', '')
    # links naar de oude calculators
    s = s.replace('href="/bereken-je-prijs"', f'href="{URL}"').replace('href="https://voltwijk.nl/bereken-je-prijs"', f'href="https://voltwijk.nl{URL}"')
    s = s.replace('href="/product-batterij#batterijkeuze"', f'href="{URL}"').replace('href="/thuisbatterij-actie"', f'href="{URL}"')
    s = s.replace('href="#batterijkeuze"', f'href="{URL}"')
    if f in ANDERS: s = s.replace('href="#calculator"', 'href="#offerte"')
    s = re.sub(r'href="/(product-[a-z]+)#calculator"', lambda m: f'href="/{m.group(1)}#offerte"' if m.group(1) + '.html' in ANDERS else f'href="{URL}"', s)
    s = s.replace('bereken: "/bereken-je-prijs"', 'bereken: "' + URL + '"')
    s = s.replace("title:'Besparingscheck', desc:'Vul je postcode en woningtype in en zie binnen een minuut een eerste inschatting van je vaste prijs en besparing — nog voordat je ergens voor kiest.', cta:{label:'Check je besparing'",
                  "title:'Bereken je thuisbatterij', desc:'Beantwoord zes korte vragen en zie binnen een minuut welke thuisbatterij past, wat hij kost en wat je ongeveer bespaart. Je zit nergens aan vast.', cta:{label:'Bereken je thuisbatterij'")
    if f not in ANDERS: s = s.replace('href="#calculator"', f'href="{URL}"')
    # knoppen en menu
    s = s.replace('>BEREKEN JE PRIJS<', '>THUISBATTERIJ BEREKENEN<')
    if anders(f):
        s = s.replace('>Bereken je prijs &amp; plan direct →<', '>Plan gratis adviesgesprek →<').replace('>Prijs berekenen &amp; inplannen →<', '>Vraag een offerte aan →<')
    else:
        s = s.replace('>Bereken je prijs &amp; plan direct →<', '>Bereken je thuisbatterij →<').replace('>Prijs berekenen &amp; inplannen →<', '>Bereken je thuisbatterij →<')
    s = s.replace('>bereken je prijs<', '>bereken welke thuisbatterij past<').replace('>Bereken je prijs<', '>Bereken je thuisbatterij<').replace('>bereken direct je prijs<', '>bereken welke thuisbatterij past<')
    s = s.replace('>prijscalculator<', '>batterijcalculator<')
    s = s.replace('>Welke batterij past bij mij? →<', '>Bereken je thuisbatterij →<').replace('📅 In 4 vragen je advies en prijs', '📅 In 1 minuut je advies en vaste prijs')
    s = s.replace('>batterijcalculator</a> of de <a href="' + URL + '">batterijkeuzehulp</a> zie je', '>batterijcalculator</a> zie je')
    s = s.replace('Met de batterijkeuzehulp zie je in vier vragen welke batterij bij je past', 'Met de batterijcalculator zie je in een minuut welke batterij bij je past')
    # productkaarten in PRODUCTS (JS): batterij naar de calculator, de rest naar het offerteblok
    s = s.replace("cta:'Bereken welke batterij past'", "cta:'Bereken je thuisbatterij'").replace("cta:'Prijs berekenen &amp; inplannen'", "cta:'Vraag een offerte aan'")
    s = s.replace("'<a href=\"#calculator\" class=\"btn-primary\" style=\"background:'+p.accent+';color:var(--dark);text-decoration:none;\">'+p.cta+' →</a>'",
                  "'<a href=\"'+(p.cta==='Bereken je thuisbatterij'?'" + URL + "':'#offerte')+'\" class=\"btn-primary\" style=\"background:'+p.accent+';color:var(--dark);text-decoration:none;\">'+p.cta+' →</a>'")
    return s

def main():
    build_page()
    n = 0
    for f in sorted(glob.glob('*.html')):
        if f in (SLUG + '.html',): continue
        s = open(f, encoding='utf-8').read(); s2 = patch(f, s)
        if s2 != s: open(f, 'w', encoding='utf-8').write(s2); n += 1
    for old in ('bereken-je-prijs.html', 'thuisbatterij-actie.html'):
        if os.path.exists(old): os.remove(old)
    print(f'funnel: {SLUG}.html gebouwd, {n} pagina\'s bijgewerkt')

if __name__ == '__main__':
    main()
