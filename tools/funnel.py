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

CSS = '''<style>
/* Calculator op één pagina: donkere kop met stappen, daaronder een rustig wit vlak met één vraag tegelijk. */
.tb-band{background:var(--dark);padding:22px 0 0;}
.tb-solo .tb-band{padding-top:84px;}
.tb-steps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;max-width:1080px;margin:0 auto;padding:0 16px;}
.tb-steps div{font-size:13px;font-weight:800;color:#6E8783;padding:10px 0 12px;border-bottom:3px solid #23403C;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tb-steps div.done{color:var(--mint);border-color:var(--mint);}
.tb-steps div.on{color:#fff;border-color:var(--accent);}
.tb-steps div b{font-family:'Bricolage Grotesque',system-ui,sans-serif;margin-right:6px;}
.tb-main{max-width:1080px;margin:0 auto;padding:44px 16px 40px;min-height:560px;display:flex;flex-direction:column;}
.tb-solo .tb-main{min-height:calc(100vh - 150px);min-height:calc(100svh - 150px);}
.tb-wrap{background:#fff;}
.tb-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;}
.tb-h{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:clamp(28px,3.6vw,40px);line-height:1.08;letter-spacing:-.02em;color:var(--ink);text-wrap:balance;margin:0;}
.tb-sub{font-size:16.5px;color:var(--ink-faint);line-height:1.55;margin-top:10px;max-width:640px;}
.tb-reset{border:0;background:none;font:700 14px 'Nunito Sans',sans-serif;color:var(--ink);cursor:pointer;display:inline-flex;gap:6px;align-items:center;white-space:nowrap;padding:6px 0;}
.tb-content{margin-top:28px;}
.tb-opts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;max-width:820px;}
.tb-opts.three{grid-template-columns:repeat(3,minmax(0,1fr));max-width:none;}
.tb-opt{position:relative;display:flex;align-items:center;gap:16px;text-align:left;border:1.5px solid var(--border);background:#fff;border-radius:18px;padding:20px 18px;cursor:pointer;font:inherit;color:inherit;transition:border-color .15s,box-shadow .15s,transform .15s;}
.tb-opt:hover{border-color:var(--accent);transform:translateY(-1px);box-shadow:0 12px 26px -18px rgba(198,64,46,.55);}
.tb-opt[aria-pressed="true"]{border-color:var(--accent);background:#FFF7F5;box-shadow:inset 0 0 0 1px var(--accent);}
.tb-opt .ic{flex:none;width:48px;height:48px;border-radius:14px;background:var(--surface-tint);color:var(--primary);display:flex;align-items:center;justify-content:center;}
.tb-opt[aria-pressed="true"] .ic{background:var(--accent);color:#fff;}
.tb-opt b{display:block;font-size:16.5px;line-height:1.25;color:var(--ink);}
.tb-opt .d{display:block;font-size:13.5px;color:var(--ink-faint);margin-top:3px;line-height:1.4;}
.tb-opt.multi::after{content:"";position:absolute;top:14px;right:14px;width:20px;height:20px;border-radius:6px;border:1.5px solid var(--border);background:#fff;}
.tb-opt.multi[aria-pressed="true"]::after{background:var(--accent) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5'/%3E%3C/svg%3E") center/12px no-repeat;border-color:var(--accent);}
.tb-field{display:grid;gap:7px;}
.tb-field label{font-size:14px;font-weight:800;color:var(--ink);}
.tb-field input{width:100%;border:1.5px solid var(--border);border-radius:14px;padding:16px;font:600 17px 'Nunito Sans',system-ui,sans-serif;color:var(--ink);background:#fff;}
.tb-field input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px rgba(15,110,107,.15);}
.tb-row{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:14px;max-width:560px;}
.tb-num{display:flex;align-items:center;border:1.5px solid var(--border);border-radius:18px;overflow:hidden;width:max-content;max-width:100%;}
.tb-num button{width:68px;height:68px;border:0;background:var(--surface-tint);color:var(--ink);font:700 28px/1 'Bricolage Grotesque',system-ui,sans-serif;cursor:pointer;}
.tb-num output{min-width:140px;text-align:center;font:700 36px/1 'Bricolage Grotesque',system-ui,sans-serif;color:var(--ink);}
.tb-num output small{display:block;font:700 11px 'Nunito Sans',sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);margin-top:5px;}
.tb-range{width:100%;max-width:560px;margin-top:20px;accent-color:var(--accent);}
.tb-hint{font-size:14px;color:var(--ink-soft);line-height:1.5;background:var(--bg);border-radius:14px;padding:13px 15px;margin-top:16px;max-width:560px;}
.tb-err{color:var(--accent-deep);font-size:14px;font-weight:700;margin-top:10px;}
.tb-foot2{margin-top:auto;padding-top:28px;}
.tb-bar{display:flex;align-items:center;justify-content:space-between;gap:16px;border-top:1px solid var(--border);padding-top:22px;margin-top:36px;}
.tb-back{border:0;background:none;font:800 15px 'Nunito Sans',sans-serif;color:var(--ink);cursor:pointer;padding:12px 4px;}
.tb-back[hidden]{visibility:hidden;display:block;}
.tb-go{text-align:right;}
.tb-go small{display:block;font-size:12.5px;color:var(--ink-faint);margin-top:8px;}
.tb-btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;border:0;border-radius:999px;background:var(--accent);color:#fff;font:800 16px/1 'Nunito Sans',system-ui,sans-serif;padding:18px 30px;cursor:pointer;text-decoration:none;box-shadow:0 16px 30px -16px rgba(198,64,46,.9);transition:background .15s,transform .15s;}
.tb-btn:hover{background:var(--accent-deep);transform:translateY(-1px);}
.tb-btn:disabled{opacity:.45;cursor:not-allowed;box-shadow:none;transform:none;}
.tb-btn.full{width:100%;}
.tb-load{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;text-align:center;color:var(--ink-soft);min-height:340px;}
.tb-spin{width:48px;height:48px;border-radius:50%;border:4px solid var(--surface-tint);border-top-color:var(--accent);animation:tbspin .8s linear infinite;}
.tb-load ul{list-style:none;padding:0;margin:6px 0 0;display:grid;gap:6px;font-size:14.5px;}
.tb-load li{opacity:.35;transition:opacity .3s;} .tb-load li.ok{opacity:1;} .tb-load li.ok::before{content:"✓ ";color:var(--primary);font-weight:800;}
@keyframes tbspin{to{transform:rotate(360deg);}}

/* systeemadvies */
.tb-sys{max-width:560px;margin:4px auto 0;border:2px solid var(--accent);border-radius:22px;overflow:hidden;background:#FFFBF9;}
.tb-sys .img{background:#F4F7F4;height:220px;display:flex;align-items:center;justify-content:center;position:relative;}
.tb-sys .img img{height:190px;width:auto;object-fit:contain;}
.tb-sys .img .badge{position:absolute;left:18px;bottom:18px;width:44px;height:44px;border-radius:12px;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;}
.tb-sys .bd{padding:22px 26px 24px;}
.tb-sys .t{display:flex;justify-content:space-between;align-items:center;gap:10px;}
.tb-sys .t b{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:21px;color:var(--ink);}
.tb-sys .t i{width:26px;height:26px;border-radius:50%;background:var(--accent) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5'/%3E%3C/svg%3E") center/14px no-repeat;flex:none;}
.tb-sys p{font-size:15px;color:var(--ink-soft);margin-top:6px;}
.tb-ck{list-style:none;padding:0;margin:14px 0 0;display:grid;gap:9px;}
.tb-ck li{display:flex;gap:10px;font-size:15px;line-height:1.45;color:var(--ink-soft);}
.tb-ck li::before{content:"";flex:none;width:20px;height:20px;margin-top:1px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230F6E6B' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='9.5'/%3E%3Cpath d='M7.5 12.5l3 3 6-6.5'/%3E%3C/svg%3E") center/20px no-repeat;}

/* aanbod */
.tb-offer{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:44px;align-items:start;margin-top:26px;}
.tb-gal{position:sticky;top:90px;}
.tb-gal .main{position:relative;background:#F4F7F4;border-radius:22px;aspect-ratio:4/3;overflow:hidden;}
.tb-gal .main img{width:100%;height:100%;object-fit:cover;display:block;}
.tb-gal .main img.fit{object-fit:contain;padding:6%;}
.tb-gal .nav{position:absolute;top:50%;transform:translateY(-50%);width:44px;height:44px;border-radius:50%;border:0;background:#fff;box-shadow:0 6px 18px -8px rgba(0,0,0,.4);cursor:pointer;font-size:20px;color:var(--ink);display:flex;align-items:center;justify-content:center;}
.tb-gal .prev{left:14px;} .tb-gal .next{right:14px;}
.tb-gal .cap{position:absolute;left:14px;bottom:12px;background:rgba(16,32,31,.78);color:#fff;font-size:12px;font-weight:700;border-radius:8px;padding:5px 9px;}
.tb-thumbs{display:flex;gap:10px;justify-content:center;margin-top:12px;}
.tb-thumbs button{width:64px;height:64px;border-radius:12px;border:2px solid transparent;background:#F4F7F4;padding:0;overflow:hidden;cursor:pointer;}
.tb-thumbs button[aria-pressed="true"]{border-color:var(--accent);}
.tb-thumbs img{width:100%;height:100%;object-fit:cover;display:block;}
.tb-note{font-size:12px;color:var(--ink-faint);text-align:center;margin-top:8px;}
.tb-of .lab{font-size:12.5px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--accent-deep);}
.tb-of h2{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:clamp(26px,3vw,34px);line-height:1.1;margin-top:8px;color:var(--ink);}
.tb-of .s{font-size:15px;color:var(--ink-faint);margin-top:6px;}
.tb-sizes{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;}
.tb-sizes button{position:relative;border:1.5px solid var(--border);background:#fff;border-radius:14px;padding:10px 14px;font:700 14px 'Nunito Sans',sans-serif;color:var(--ink);cursor:pointer;text-align:left;}
.tb-sizes button small{display:block;font-weight:600;font-size:12px;color:var(--ink-faint);}
.tb-sizes button[aria-pressed="true"]{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent);}
.tb-sizes button em{position:absolute;top:-9px;right:10px;background:var(--accent);color:#fff;font-style:normal;font-size:10.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;border-radius:999px;padding:2px 7px;}
.tb-why{background:var(--bg);border-radius:18px;padding:18px 20px;margin-top:18px;}
.tb-why b{display:block;font-size:16px;color:var(--ink);}
.tb-kpi{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:16px;}
.tb-kpi div{border:1px solid var(--border);border-radius:16px;padding:12px 14px;}
.tb-kpi span{display:block;font-size:12.5px;font-weight:700;color:var(--ink-faint);}
.tb-kpi b{display:block;font:700 20px/1.2 'Bricolage Grotesque',system-ui,sans-serif;margin-top:4px;color:var(--ink);font-variant-numeric:tabular-nums;}
.tb-price{margin-top:20px;padding-top:18px;border-top:1px solid var(--border);}
.tb-price .v{font-size:13px;color:var(--ink-faint);}
.tb-price .p{font:700 44px/1.05 'Bricolage Grotesque',system-ui,sans-serif;color:var(--accent-deep);margin-top:2px;}
.tb-price .p small{font:700 15px 'Nunito Sans',sans-serif;color:var(--ink-soft);margin-left:8px;}
.tb-price .i{font-size:13.5px;color:var(--ink-soft);margin-top:6px;line-height:1.5;}
.tb-of .tb-btn{margin-top:18px;}
.tb-risk{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:12px;font-size:13px;color:var(--ink-soft);justify-content:center;}
.tb-risk span::before{content:"✓ ";color:var(--primary);font-weight:800;}
.tb-urg{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;}
.tb-urg span{background:#FFF1EE;color:var(--accent-deep);font-size:13px;font-weight:800;border-radius:999px;padding:6px 12px;}
.tb-urg span.g{background:var(--surface-tint);color:var(--primary);}
.tb-proof{display:flex;align-items:center;justify-content:center;gap:8px 18px;flex-wrap:wrap;margin-top:16px;font-size:13px;font-weight:700;color:var(--ink-soft);}
.tb-proof i{font-style:normal;color:#F5B400;letter-spacing:1px;}
.tb-inc{margin-top:18px;border:1px solid var(--border);border-radius:16px;padding:4px 16px;}
.tb-inc summary{cursor:pointer;font-weight:800;font-size:14.5px;padding:12px 0;color:var(--ink);}
.tb-inc ul{margin:0 0 12px;}

/* gegevens en bedankt */
.tb-form{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:40px;align-items:start;margin-top:26px;}
.tb-form form{display:grid;gap:14px;max-width:520px;}
.tb-form .chk{display:flex;gap:10px;align-items:flex-start;font-size:14.5px;color:var(--ink-soft);cursor:pointer;}
.tb-form .chk input{width:20px;height:20px;accent-color:var(--accent);flex:none;margin-top:1px;}
.tb-sum{background:var(--bg);border-radius:20px;padding:20px;}
.tb-sum .r{display:grid;grid-template-columns:84px minmax(0,1fr);gap:14px;align-items:center;}
.tb-sum img{width:84px;height:84px;border-radius:14px;object-fit:cover;background:#fff;}
.tb-sum b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:18px;color:var(--ink);line-height:1.2;}
.tb-sum .pp{font:700 22px 'Bricolage Grotesque',system-ui,sans-serif;color:var(--accent-deep);margin-top:4px;}
.tb-sum .tb-ck{margin-top:16px;} .tb-sum .tb-ck li{font-size:14px;}
.tb-small{font-size:12.5px;color:var(--ink-faint);line-height:1.5;}
.tb-ok{max-width:640px;margin:20px auto 0;text-align:center;}
.tb-ok .big{width:72px;height:72px;border-radius:50%;background:var(--surface-tint);color:var(--primary);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;}
.tb-ok p{font-size:16px;color:var(--ink-soft);line-height:1.6;margin-top:10px;}
.tb-book{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:24px;text-align:left;}
.tb-book a,.tb-book button{display:flex;flex-direction:column;gap:4px;border:1.5px solid var(--border);border-radius:16px;padding:16px;background:#fff;font:inherit;color:inherit;text-decoration:none;cursor:pointer;text-align:left;}
.tb-book a:hover,.tb-book button:hover{border-color:var(--accent);}
.tb-book b{font-size:15px;color:var(--ink);} .tb-book span{font-size:13px;color:var(--ink-faint);line-height:1.4;}
.tb-mob{display:none;}
@media (max-width:900px){
 .tb-offer,.tb-form{grid-template-columns:1fr;gap:22px;}.tb-gal{position:static;}
 .tb-opts.three{grid-template-columns:1fr;}
}
@media (max-width:640px){
 .tb-solo .tb-band{padding-top:72px;}.tb-steps{gap:4px;}.tb-steps div{font-size:11px;padding:8px 0 10px;}.tb-steps div span{display:none;}.tb-steps div.on span{display:inline;}
 .tb-main{padding-top:26px;}.tb-sub{font-size:15px;}.tb-content{margin-top:20px;}
 .tb-opts{grid-template-columns:1fr;gap:10px;}.tb-opt{padding:15px 14px;}.tb-opt .ic{width:42px;height:42px;}
 .tb-row{grid-template-columns:1fr;}
 .tb-bar{position:sticky;bottom:0;background:#fff;margin:24px -16px 0;padding:12px 16px calc(12px + env(safe-area-inset-bottom,0px));box-shadow:0 -10px 24px -18px rgba(0,0,0,.35);}
 .tb-bar .tb-btn{padding:16px 22px;}.tb-go small{display:none;}
 .tb-sys .img{height:180px;}.tb-sys .img img{height:150px;}
 .tb-price .p{font-size:38px;}.tb-book{grid-template-columns:1fr;}.tb-thumbs button{width:54px;height:54px;}
 .tb-reset span{display:none;}
}
@media (min-width:641px){#tbOfGo{display:none;}}
@media (prefers-reduced-motion:reduce){.tb-opt,.tb-btn{transition:none;}.tb-spin{animation:none;}}
</style>'''

PAGE_CSS = '''<style>
.tb-page{padding-top:0 !important;background:#fff;}
#waWidget{display:none !important;}
.tb-topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;}
.tb-topbar .vw-logo{height:20px;}
.tb-tel{display:inline-flex;align-items:center;gap:8px;font-weight:800;font-size:15px;color:inherit;text-decoration:none;white-space:nowrap;}
.tb-foot{background:var(--dark);color:#C9D6D3;padding:18px 0;font-size:13px;line-height:1.7;}
.tb-foot .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px 24px;}
.tb-foot a{color:#C9D6D3;}
.vwp{display:none !important;}
</style>'''

IC.update({
 'reset': '<path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 21v-5h5"/>',
 'tool': '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9z"/>',
 'pin': '<path d="M12 21s-7-6.3-7-11.5A7 7 0 0 1 19 9.5C19 14.7 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
})

# Per pakket: wat het is, waarom het sterk is, en welke foto's de klant ziet. Alleen feiten uit de datasheets.
PK_TXT = {
 'bat10': {'naam': 'FoxESS P100 all-in-one', 'kort': 'Omvormer en batterij in één strakke kast.',
   'feat': ['10,24 kWh opslag, waarvan 95% bruikbaar', 'Veilige LFP-cellen, getest op 6.000 laadcycli', 'Noodstroom: schakelt bij een storing binnen enkele milliseconden om', 'Waterdicht (IP66), kan ook in garage of schuur'],
   'foto': [('/images/calc-foxess-woning.webp', 'FoxESS P100 aan de buitenmuur', ''), ('/images/product-batterij.webp', 'Thuisbatterij', 'fit'), ('/images/thuisbatterij-bijkeuken.webp', 'Netjes weggewerkt in huis', '')]},
 'bat16-1': {'naam': 'Dyness LFP-batterij met Solis hybride omvormer', 'kort': 'De meeste opslag voor een woning met 1-fase aansluiting.',
   'feat': ['16 kWh opslag, ruim anderhalf keer het 10 kWh-pakket', 'Solis 6 kW hybride omvormer, ook geschikt voor je zonnepanelen', 'Veilige LFP-cellen', 'Werkt met dynamische contracten en energiemanagementsystemen'],
   'foto': [('/images/calc-dyness-schuin-1.webp', 'Dyness LFP-batterij, 16 kWh', 'fit'), ('/images/calc-dyness-voor.webp', 'Dyness LFP-batterij, vooraanzicht', 'fit'), ('/images/calc-dyness-schuin-2.webp', 'Dyness LFP-batterij, zijaanzicht', 'fit'), ('/images/calc-solis-1fase.webp', 'Solis 6 kW hybride omvormer (1-fase)', 'fit')]},
 'bat16-3': {'naam': 'Dyness LFP-batterij met Solis hybride omvormer', 'kort': 'Meer vermogen, verdeeld over drie fasen.',
   'feat': ['16 kWh opslag', 'Solis 8 kW hybride omvormer, verdeelt het vermogen over drie fasen', 'Veilige LFP-cellen', 'Geschikt bij een warmtepomp, laadpaal of dynamisch contract'],
   'foto': [('/images/calc-dyness-schuin-1.webp', 'Dyness LFP-batterij, 16 kWh', 'fit'), ('/images/calc-dyness-voor.webp', 'Dyness LFP-batterij, vooraanzicht', 'fit'), ('/images/calc-dyness-schuin-2.webp', 'Dyness LFP-batterij, zijaanzicht', 'fit'), ('/images/calc-solis-3fase.webp', 'Solis 8 kW hybride omvormer (3-fase)', 'fit')]},
}
INBEGREPEN = ['Batterij en hybride omvormer', 'Montage en bekabeling door onze eigen monteurs', 'Een eigen groep in de meterkast', 'Aanmelden bij de netbeheerder', 'App ingesteld en uitleg bij de oplevering', '2 jaar garantie op de installatie']

JS = r'''<script>
(function(){
  var PK = __PK__, IC = __IC__, INC = __INC__, PRIJS = 0.28, SPREAD = 0.08, KWH_PANEEL = 340, EFF = 0.9, UTIL = 0.8;
  var MF = [2.6,4.6,8.1,11.4,13.3,13.2,13.1,11.6,8.8,6.2,3.3,2.2], CF = [10,9,8.9,7.8,7.4,6.8,6.9,7.1,7.5,8.6,9.6,10.4], DG = [31,28,31,30,31,30,31,31,30,31,30,31];
  var main = document.getElementById('tbMain'), stepsEl = document.getElementById('tbSteps');
  var st = {panelen:null, aantal:12, verbruik:null, extra:{}, fase:null, doel:null, postcode:'', huisnummer:'', keuze:null, foto:0}, hist = [], cur = 'adres', started = false;
  /* scherm -> fase in de stappenbalk */
  var FASE = {adres:0, panelen:1, aantal:1, verbruik:1, extra:1, doel:2, fase:3, laden:3, systeem:3, aanbod:4, gegevens:4, klaar:5};
  var NAMEN = ['Adres','Situatie','Doel','Systeem','Aanbod'];
  try{ var u = new URLSearchParams(location.search), t = {}; ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid','fbclid'].forEach(function(k){ if(u.get(k)) t[k] = u.get(k); });
    if(Object.keys(t).length) sessionStorage.setItem('vwUtm', JSON.stringify(t)); }catch(e){}
  function utm(){ try{ return JSON.parse(sessionStorage.getItem('vwUtm') || '{}'); }catch(e){ return {}; } }
  function track(n, p){ try{ if(window.vwTrack) vwTrack(n, p || {}); }catch(e){} }
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function fmt(n){ return Math.round(n).toLocaleString('nl-NL'); }
  function eur(n){ return '€ ' + fmt(n); }
  function ic(k){ return '<span class="ic">' + IC[k] + '</span>'; }
  function opt(k, val, title, d, icon, multi){ var on = multi ? !!st[k][val] : String(st[k]) === String(val);
    return '<button type="button" class="tb-opt' + (multi ? ' multi' : '') + '" data-k="' + k + '" data-v="' + val + '" aria-pressed="' + on + '">' + ic(icon) + '<span><b>' + title + '</b>' + (d ? '<span class="d">' + d + '</span>' : '') + '</span></button>'; }
  function volgorde(){ return ['adres','panelen'].concat(st.panelen === 'ja' ? ['aantal'] : [], ['verbruik','extra','doel','fase','laden','systeem','aanbod','gegevens','klaar']); }
  function nextOf(s){ var l = volgorde(); return l[l.indexOf(s) + 1]; }
  function go(next){ if(!started){ started = true; track('calc_start', {pagina: location.pathname}); } hist.push(cur); cur = next; render(true); track('calc_stap', {stap: next}); }
  function back(){ if(!hist.length) return; cur = hist.pop(); if(cur === 'laden') cur = hist.pop() || 'fase'; render(true); }
  function steps(){ var f = FASE[cur]; stepsEl.innerHTML = NAMEN.map(function(n, i){ return '<div class="' + (i < f ? 'done' : i === f ? 'on' : '') + '"><b>' + (i + 1) + '</b><span>' + n + '</span></div>'; }).join(''); }
  function head(h, sub, reset){ return '<div class="tb-head"><div><h1 class="tb-h">' + h + '</h1>' + (sub ? '<p class="tb-sub">' + sub + '</p>' : '') + '</div>' +
      (reset ? '<button type="button" class="tb-reset" id="tbReset">' + IC.reset.replace(/width="22" height="22"/, 'width="18" height="18"') + '<span>Opnieuw beginnen</span></button>' : '') + '</div>'; }
  function bar(label, id, note, disabled){ return '<div class="tb-bar"><button type="button" class="tb-back" id="tbBack"' + (hist.length ? '' : ' hidden') + '>Terug</button>' +
      (label ? '<div class="tb-go"><button type="button" class="tb-btn" id="' + id + '"' + (disabled ? ' disabled' : '') + '>' + label + '</button>' + (note ? '<small>' + note + '</small>' : '') + '</div>' : '') + '</div>'; }

  function render(scroll){
    var h = ''; steps();
    if(cur === 'adres'){
      h = head(document.querySelector('.tb-solo') ? 'Bereken welke thuisbatterij bij jouw huis past' : 'Begin met je adres', 'Vul je postcode en huisnummer in. Daarna stellen we je nog vijf korte vragen en zie je direct je advies en vaste prijs.') +
        '<div class="tb-content"><div class="tb-row"><div class="tb-field"><label for="tbPc">Postcode</label><input id="tbPc" autocomplete="postal-code" placeholder="4762 AS" value="' + esc(st.postcode) + '" maxlength="7"></div>' +
        '<div class="tb-field"><label for="tbHn">Huisnummer</label><input id="tbHn" inputmode="numeric" placeholder="15" value="' + esc(st.huisnummer) + '" maxlength="8"></div></div>' +
        '<div id="tbAdrErr" class="tb-err" hidden></div><p class="tb-hint">Met je adres zien we wanneer onze monteurs bij jou kunnen installeren. Je zit nergens aan vast.</p></div>' +
        bar('Start mijn advies →', 'tbAdrGo', 'Duurt ongeveer 1 minuut');
    } else if(cur === 'panelen'){
      h = head('Heb je zonnepanelen?', 'Dan weten we hoeveel zonnestroom je kunt opslaan.') + '<div class="tb-content"><div class="tb-opts three">' +
        opt('panelen','ja','Ja, ik heb zonnepanelen','Ik wil mijn stroom van overdag bewaren','zon') +
        opt('panelen','straks','Nog niet, maar ik wil ze erbij','We nemen panelen mee in je advies','plus') +
        opt('panelen','nee','Nee, alleen een batterij','Besparen met een dynamisch contract','geen') + '</div></div>' + bar();
    } else if(cur === 'aantal'){
      h = head('Hoeveel zonnepanelen heb je?', 'Een schatting is goed genoeg.') + '<div class="tb-content">' +
        '<div class="tb-num"><button type="button" data-n="-1" aria-label="Minder panelen">−</button><output id="tbN">' + st.aantal + '<small>panelen</small></output><button type="button" data-n="1" aria-label="Meer panelen">+</button></div>' +
        '<input class="tb-range" type="range" id="tbNr" min="4" max="40" value="' + st.aantal + '" aria-label="Aantal panelen">' +
        '<p class="tb-hint">Dat is ongeveer <b id="tbOpw">' + fmt(st.aantal * KWH_PANEEL) + ' kWh</b> zonnestroom per jaar.</p></div>' + bar('Volgende →', 'tbNext');
    } else if(cur === 'verbruik'){
      var vb = st.verbruik, eigen = vb && [2300,3500,4800].indexOf(vb) < 0;
      h = head('Hoeveel stroom gebruik je per jaar?', 'Staat op je jaarafrekening. Weet je het niet, kies dan je huishouden.') + '<div class="tb-content"><div class="tb-opts">' +
        opt('verbruik',2300,'1 of 2 personen','ca. 2.300 kWh per jaar','p1') + opt('verbruik',3500,'3 of 4 personen','ca. 3.500 kWh per jaar','p2') +
        opt('verbruik',4800,'5 personen of meer','ca. 4.800 kWh per jaar','p3') +
        '<button type="button" class="tb-opt" id="tbEigen" aria-pressed="' + !!eigen + '">' + ic('kwh') + '<span><b>Ik weet het precies</b><span class="d">Vul je verbruik in</span></span></button></div>' +
        '<div id="tbEigenBox"' + (eigen ? '' : ' hidden') + ' style="margin-top:16px;max-width:320px;"><div class="tb-field"><label for="tbKwh">Verbruik per jaar (kWh)</label><input id="tbKwh" type="number" inputmode="numeric" min="500" max="30000" step="100" value="' + (eigen && vb > 0 ? vb : '') + '" placeholder="bijvoorbeeld 3200"></div></div></div>' +
        bar(eigen ? 'Volgende →' : '', 'tbKwhGo');
    } else if(cur === 'extra'){
      h = head('Heb je (straks) een van deze?', 'Die gebruiken veel stroom, ook \'s avonds. Kies alles wat geldt.') + '<div class="tb-content"><div class="tb-opts">' +
        opt('extra','ev','Elektrische auto','of binnenkort','auto',1) + opt('extra','wp','Warmtepomp','hybride of volledig','wp',1) +
        opt('extra','airco','Airco','koelen en verwarmen','airco',1) +
        '<button type="button" class="tb-opt" id="tbGeen" aria-pressed="' + !!(st.extraGezien && !Object.keys(st.extra).some(function(k){ return st.extra[k]; })) + '">' + ic('leeg') + '<span><b>Geen van deze</b></span></button></div></div>' +
        bar('Volgende →', 'tbNext');
    } else if(cur === 'doel'){
      h = head('Wat vind je het belangrijkst?', 'Dan stemmen we je advies daarop af.') + '<div class="tb-content"><div class="tb-opts">' +
        opt('doel','besparen','Zoveel mogelijk besparen','Mijn eigen zonnestroom zelf gebruiken','euro') + opt('doel','2027','Klaar zijn voor 2027','Als salderen stopt','kal') +
        opt('doel','noodstroom','Stroom bij een storing','Noodstroom als het net uitvalt','stroom') + opt('doel','handel','Slim handelen','Met een dynamisch energiecontract','handel') + '</div></div>' + bar();
    } else if(cur === 'fase'){
      h = head('Wat voor aansluiting heb je?', 'Dat bepaalt welke omvormer bij je past.') + '<div class="tb-content"><div class="tb-opts three">' +
        opt('fase','1','1-fase','De meeste woningen. Eén hoofdschakelaar, meestal 1 x 35 A.','f1') +
        opt('fase','3','3-fase','Drie hoofdzekeringen, of 3 x 25 A op je energierekening.','f3') +
        opt('fase','?','Weet ik niet','We checken het samen met een foto van je meterkast.','vraag') + '</div></div>' + bar();
    } else if(cur === 'laden'){
      h = '<div class="tb-load"><div class="tb-spin"></div><b style="font-size:19px;color:var(--ink);">We stellen je advies samen…</b><ul><li id="l1">Jouw verbruik en zonnestroom</li><li id="l2">De juiste omvormer voor je aansluiting</li><li id="l3">Je vaste prijs en besparing</li></ul></div>';
      [1,2,3].forEach(function(i){ setTimeout(function(){ var el = document.getElementById('l' + i); if(el) el.className = 'ok'; }, i * 380); });
      setTimeout(function(){ if(cur !== 'laden') return; cur = 'systeem'; st.keuze = advies(); st.foto = 0; track('calc_advies', {batterij: st.keuze}); render(false); }, 1400);
    } else if(cur === 'systeem'){ h = systeem(); }
    else if(cur === 'aanbod'){ h = aanbod(); }
    else if(cur === 'gegevens'){ h = gegevens(); }
    else if(cur === 'klaar'){ h = klaar(); }
    main.innerHTML = h; wire();
    if(scroll){ var y = document.getElementById('calculator').getBoundingClientRect().top + window.scrollY - (document.querySelector('.tb-solo') ? 0 : 64); if(Math.abs(window.scrollY - y) > 40) window.scrollTo({top: Math.max(0, y), behavior: 'smooth'}); }
  }

  function wire(){
    var b = document.getElementById('tbBack'); if(b) b.onclick = back;
    var rs = document.getElementById('tbReset'); if(rs) rs.onclick = function(){ hist = []; cur = 'panelen'; st.keuze = null; render(true); };
    main.querySelectorAll('.tb-opt[data-k]').forEach(function(el){ el.onclick = function(){
      var k = el.dataset.k, v = el.dataset.v; if(k === 'verbruik') v = +v;
      if(k === 'extra'){ st.extra[v] = !st.extra[v]; st.extraGezien = true; render(false); return; }
      st[k] = v; render(false); setTimeout(function(){ go(nextOf(cur)); }, 180); }; });
    var nx = document.getElementById('tbNext'); if(nx) nx.onclick = function(){ if(cur === 'extra') st.extraGezien = true; go(nextOf(cur)); };
    main.querySelectorAll('[data-n]').forEach(function(el){ el.onclick = function(){ setN(st.aantal + (+el.dataset.n)); }; });
    var r = document.getElementById('tbNr'); if(r) r.oninput = function(){ setN(+r.value); };
    var e = document.getElementById('tbEigen'); if(e) e.onclick = function(){ st.verbruik = -1; render(false); var k = document.getElementById('tbKwh'); k.value = ''; k.focus(); };
    var kg = document.getElementById('tbKwhGo'); if(kg) kg.onclick = function(){ var v = +document.getElementById('tbKwh').value; if(v >= 500 && v <= 30000){ st.verbruik = Math.round(v); go(nextOf(cur)); } else document.getElementById('tbKwh').focus(); };
    var kw = document.getElementById('tbKwh'); if(kw) kw.onkeydown = function(ev){ if(ev.key === 'Enter' && kg) kg.click(); };
    var g = document.getElementById('tbGeen'); if(g) g.onclick = function(){ st.extra = {}; st.extraGezien = true; go(nextOf(cur)); };
    var ag = document.getElementById('tbAdrGo'); if(ag) ag.onclick = adres;
    ['tbPc','tbHn'].forEach(function(id){ var x = document.getElementById(id); if(x) x.onkeydown = function(ev){ if(ev.key === 'Enter') adres(); }; });
    var sg = document.getElementById('tbSysGo'); if(sg) sg.onclick = function(){ go('aanbod'); };
    var og = document.querySelectorAll('[data-offerte]'); og.forEach(function(x){ x.onclick = function(){ track('offerte_klik', {batterij: st.keuze}); go('gegevens'); }; });
    main.querySelectorAll('[data-size]').forEach(function(el){ el.onclick = function(){ st.keuze = el.dataset.size; st.foto = 0; render(false); track('calc_wissel', {batterij: st.keuze}); }; });
    main.querySelectorAll('[data-foto]').forEach(function(el){ el.onclick = function(){ st.foto = +el.dataset.foto; foto(); }; });
    var pv = document.getElementById('tbPrev'), nv = document.getElementById('tbNextF'), n = (PK[st.keuze] || {foto: []}).foto.length;
    if(pv) pv.onclick = function(){ st.foto = (st.foto + n - 1) % n; foto(); };
    if(nv) nv.onclick = function(){ st.foto = (st.foto + 1) % n; foto(); };
    var f = document.getElementById('tbForm'); if(f) f.addEventListener('submit', verstuur);
    var nm = document.getElementById('tbNaam'); if(nm && !('ontouchstart' in window)) nm.focus();
  }
  function setN(n){ st.aantal = Math.max(4, Math.min(40, n)); var o = document.getElementById('tbN'); if(o) o.firstChild.textContent = st.aantal;
    var r = document.getElementById('tbNr'); if(r) r.value = st.aantal; var w = document.getElementById('tbOpw'); if(w) w.textContent = fmt(st.aantal * KWH_PANEEL) + ' kWh'; }
  function adres(){ var pc = document.getElementById('tbPc').value.trim().toUpperCase().replace(/^(\d{4})\s*([A-Z]{2})$/, '$1 $2'), hn = document.getElementById('tbHn').value.trim(), er = document.getElementById('tbAdrErr');
    if(!/^\d{4} [A-Z]{2}$/.test(pc)){ er.textContent = 'Vul je postcode in, bijvoorbeeld 4762 AS.'; er.hidden = false; return; }
    if(!/^\d+/.test(hn)){ er.textContent = 'Vul je huisnummer in.'; er.hidden = false; return; }
    st.postcode = pc; st.huisnummer = hn;
    /* buiten de losse calculatorpagina (bijv. de homepage): verder in een eigen scherm met alleen de calculator */
    if(!document.querySelector('.tb-solo')){
      try{ sessionStorage.setItem('vwCalcStart', JSON.stringify({postcode: pc, huisnummer: hn})); }catch(e){}
      track('calc_start', {pagina: location.pathname}); location.href = '/thuisbatterij-berekenen'; return;
    }
    go('panelen'); }

  /* ---------- advies en besparing (indicatie) ---------- */
  function verbruik(){ var v = st.verbruik > 0 ? st.verbruik : 3500; if(st.extra.ev) v += 2000; if(st.extra.wp) v += 2500; if(st.extra.airco) v += 400; return v; }
  function opwek(){ return st.panelen === 'ja' ? st.aantal * KWH_PANEEL : st.panelen === 'straks' ? 12 * KWH_PANEEL : 0; }
  function advies(){ if(st.fase === '3') return 'bat16-3';
    return (verbruik() >= 3200 || st.extra.ev || st.extra.wp || st.doel === 'handel' || opwek() >= 4400) ? 'bat16-1' : 'bat10'; }
  function reken(id){
    var p = PK[id], use = p.kwh * 0.95, C = verbruik(), P = opwek(), tot = {direct:0, extra:0, arb:0};
    for(var i = 0; i < 12; i++){
      var prod = P * MF[i] / 98.4, cons = C * CF[i] / 100, direct = Math.min(prod, cons * .35), sur = prod - direct, rest = cons - direct;
      var cap = use * DG[i] * UTIL, extra = Math.min(sur * EFF, rest, cap), arb = Math.min(Math.max(0, cap - extra), rest - extra);
      tot.direct += direct; tot.extra += extra; tot.arb += arb;
    }
    var dyn = st.doel === 'handel' || st.panelen === 'nee';
    tot.besparing = tot.extra * PRIJS + (dyn ? tot.arb * (SPREAD - (1 / EFF - 1) * (PRIJS - SPREAD)) : 0);
    tot.zelfZonder = P ? tot.direct / P : 0; tot.zelfMet = P ? Math.min(.95, (tot.direct + tot.extra / EFF) / P) : 0;
    return tot;
  }
  function range(v){ return eur(Math.floor(v * .85 / 10) * 10) + ' – ' + fmt(Math.ceil(v * 1.15 / 10) * 10); }
  function waarom(id){
    var p = PK[id], w = [];
    w.push(p.fase === '3-fase' ? 'Je hebt een 3-fase aansluiting. De 8 kW omvormer verdeelt het vermogen over alle drie de fasen.' :
      st.fase === '?' ? 'We gaan uit van een 1-fase aansluiting. Blijkt het 3-fase, dan wordt het de 16 kWh met 8 kW omvormer.' : 'Past bij je 1-fase aansluiting, met een ' + p.kw + ' kW hybride omvormer.');
    if(st.panelen === 'ja') w.push('Je ' + st.aantal + ' panelen maken ongeveer ' + fmt(opwek()) + ' kWh per jaar. Een groot deel daarvan komt overdag, als je weinig gebruikt. Die stroom bewaar je nu voor de avond.');
    if(st.panelen === 'straks') w.push('Zonnepanelen leggen we ook. We rekenen hier met 12 panelen; in het gesprek rekenen we panelen en batterij samen door.');
    if(st.panelen === 'nee') w.push('Zonder zonnepanelen bespaar je vooral met een dynamisch contract: laden als stroom goedkoop is, gebruiken als hij duur is.');
    if(st.extra.ev || st.extra.wp) w.push('Met ' + [st.extra.ev && 'een elektrische auto', st.extra.wp && 'een warmtepomp'].filter(Boolean).join(' en ') + ' gebruik je \'s avonds veel stroom. Dan loont meer opslag.');
    if(st.doel === 'noodstroom') w.push('Valt de stroom uit, dan levert de batterij noodstroom aan je huis.');
    if(st.doel === 'handel') w.push('Werkt met dynamische contracten en slimme energiemanagementsystemen, zodat je kunt handelen.');
    if((st.doel === '2027' || st.doel === 'besparen') && st.panelen !== 'nee') w.push('Vanaf 1 januari 2027 stopt salderen. Elke kWh die je zelf gebruikt in plaats van teruglevert, is dan meer waard.');
    return w;
  }
  function ck(list){ return '<ul class="tb-ck">' + list.map(function(t){ return '<li>' + esc(t) + '</li>'; }).join('') + '</ul>'; }
  function systeem(){
    var id = st.keuze, p = PK[id];
    return head('Dit past bij jouw situatie', 'Op basis van je antwoorden past deze batterij het best bij jouw woning en wat je belangrijk vindt.', true) +
      '<div class="tb-content"><div class="tb-sys"><div class="img"><img src="' + ((p.foto.filter(function(x){ return x[2] === 'fit'; })[0] || ['/images/product-batterij.webp'])[0]) + '" alt="" onerror="this.style.display=\'none\'"><span class="badge">' + IC.tool + '</span></div>' +
      '<div class="bd"><div class="t"><b>Thuisbatterij ' + p.kwh + ' kWh · ' + p.fase + '</b><i></i></div><p>' + esc(p.kort) + '</p>' + ck(p.feat.slice(0, 3).concat(['Installatie door onze eigen monteurs inbegrepen'])) + '</div></div></div>' +
      bar('Bekijk jouw aanbod →', 'tbSysGo', 'Vrijblijvend: je ziet eerst je aanbod en de prijs.');
  }
  function galerij(p){
    var f = p.foto[st.foto] || p.foto[0];
    return '<div class="tb-gal"><div class="main"><img id="tbFoto" class="' + (f[2] || '') + '" src="' + f[0] + '" alt="' + esc(f[1]) + '"><span class="cap" id="tbCap">' + esc(f[1]) + '</span>' +
      (p.foto.length > 1 ? '<button type="button" class="nav prev" id="tbPrev" aria-label="Vorige foto">‹</button><button type="button" class="nav next" id="tbNextF" aria-label="Volgende foto">›</button>' : '') + '</div>' +
      '<div class="tb-thumbs">' + p.foto.map(function(x, i){ return '<button type="button" data-foto="' + i + '" aria-label="' + esc(x[1]) + '" aria-pressed="' + (i === st.foto) + '"><img src="' + x[0] + '" alt="" loading="lazy"></button>'; }).join('') + '</div>' +
      '<p class="tb-note">Foto\'s ter illustratie. De uitvoering kan afwijken.</p></div>';
  }
  function foto(){ var p = PK[st.keuze], f = p.foto[st.foto], im = document.getElementById('tbFoto'); if(!im) return;
    im.src = f[0]; im.alt = f[1]; im.className = f[2] || ''; document.getElementById('tbCap').textContent = f[1];
    main.querySelectorAll('[data-foto]').forEach(function(b){ b.setAttribute('aria-pressed', String(+b.dataset.foto === st.foto)); }); }
  function dagenTot2027(){ var d = Math.ceil((new Date(2027, 0, 1) - new Date()) / 864e5); return d > 0 ? d : 0; }
  function aanbod(){
    var id = st.keuze, p = PK[id], r = reken(id), adv = advies(), d27 = dagenTot2027();
    var sizes = Object.keys(PK).map(function(k){ var x = PK[k]; return '<button type="button" data-size="' + k + '" aria-pressed="' + (k === id) + '">' + (k === adv ? '<em>Advies</em>' : '') + x.kwh + ' kWh · ' + x.fase + '<small>' + eur(x.prijs) + ' excl. btw</small></button>'; }).join('');
    var kpi = '<div class="tb-kpi"><div><span>Geschatte besparing</span><b>' + (r.besparing > 25 ? range(r.besparing) + '<small style="font:600 12px Nunito Sans,sans-serif;color:var(--ink-faint);"> /jaar</small>' : 'Samen bekijken') + '</b></div>' +
      '<div><span>' + (opwek() ? 'Eigen zonnestroom zelf gebruikt' : 'Bruikbare opslag') + '</span><b>' + (opwek() ? Math.round(r.zelfZonder * 100) + '% → ' + Math.round(r.zelfMet * 100) + '%' : 'ca. ' + fmt(p.kwh * .95) + ' kWh') + '</b></div></div>';
    return head('Jouw aanbod', '', true) +
      '<div class="tb-offer">' + galerij(p) +
      '<div class="tb-of"><div class="lab">' + (id === adv ? 'Past het best bij jou' : 'Jouw keuze') + '</div><h2>Thuisbatterij ' + p.kwh + ' kWh met ' + p.kw + ' kW omvormer</h2><p class="s">' + esc(p.naam) + ' · ' + p.fase + '</p>' +
      '<div class="tb-sizes" role="group" aria-label="Kies je opslag">' + sizes + '</div>' +
      '<div class="tb-why"><b>Waarom dit systeem voor jou?</b>' + ck(waarom(id)) + '</div>' + ck(p.feat) + kpi +
      '<div class="tb-price"><div class="v">Vaste prijs, inclusief installatie</div><div class="p">' + eur(p.prijs) + '<small>excl. btw</small></div>' +
      '<div class="i">' + eur(p.prijs * 1.21) + ' incl. btw. Met een dynamisch contract kun je de btw vaak terugvragen. Is er meerwerk nodig, dan hoor je dat altijd vooraf.</div></div>' +
      '<div class="tb-urg"><span class="g">Installatie al vanaf <b data-vw-first></b></span>' + (d27 ? '<span>Salderen stopt over ' + d27 + ' dagen</span>' : '') + '</div>' +
      '<button type="button" class="tb-btn full" data-offerte>Vraag vrijblijvend jouw offerte aan →</button>' +
      '<div class="tb-risk"><span>Je betaalt nu niets</span><span>Gratis technische check</span><span>Eigen monteurs</span></div>' +
      '<div class="tb-proof"><span><i>★★★★★</i> 4,7 / 5 op Google</span><span>12.500+ installaties</span><span>2 jaar installatiegarantie</span></div>' +
      '<details class="tb-inc"><summary>Wat zit er in de prijs?</summary>' + ck(INC) + '</details>' +
      '<p class="tb-small" style="margin-top:14px;">Besparing is een indicatie vanaf 2027, bij € 0,28 per kWh en zonder salderen. In het adviesgesprek rekenen we het na met je jaarafrekening.</p>' +
      '</div></div>' + bar('Vraag offerte aan →', 'tbOfGo');
  }
  function gegevens(){
    var p = PK[st.keuze];
    return head('Bijna klaar. Waar mogen we je offerte naartoe sturen?', 'We bellen je om je situatie kort te checken. Daarna krijg je je offerte met vaste prijs. Je zit nergens aan vast.') +
      '<div class="tb-form"><form id="tbForm" name="thuisbatterij-advies" novalidate>' +
      '<p hidden><label>Niet invullen <input name="bot-field"></label></p>' +
      '<div class="tb-field"><label for="tbNaam">Voor- en achternaam</label><input id="tbNaam" name="naam" autocomplete="name" required></div>' +
      '<div class="tb-field"><label for="tbTel">Telefoonnummer</label><input id="tbTel" name="telefoon" type="tel" autocomplete="tel" inputmode="tel" required></div>' +
      '<div class="tb-field"><label for="tbMail">E-mailadres</label><input id="tbMail" name="email" type="email" autocomplete="email" required></div>' +
      (st.panelen !== 'ja' ? '<label class="chk"><input type="checkbox" id="tbZp"' + (st.panelen === 'straks' ? ' checked' : '') + '> Neem ook zonnepanelen mee in mijn offerte</label>' : '') +
      '<div id="tbFormErr" class="tb-err" hidden></div>' +
      '<button type="submit" class="tb-btn full">Verstuur mijn aanvraag →</button>' +
      '<p class="tb-small" style="text-align:center;">Gratis en vrijblijvend. We gebruiken je gegevens alleen voor deze aanvraag. Zie ons <a href="/privacybeleid" style="color:inherit;">privacybeleid</a>.</p></form>' +
      '<div class="tb-sum"><div class="r"><img src="' + p.foto[0][0] + '" alt=""><div><b>Thuisbatterij ' + p.kwh + ' kWh · ' + p.fase + '</b><div class="pp">' + eur(p.prijs) + ' <small style="font:600 13px Nunito Sans,sans-serif;color:var(--ink-faint);">excl. btw</small></div></div></div>' +
      ck(['Vaste prijs, inclusief installatie', 'Installatie al vanaf ' + (window.vwFirstDate || 'binnen enkele weken'), 'Je betaalt nu niets', '4,7 / 5 op Google, 12.500+ installaties']) + '</div></div>' + bar();
  }
  function verstuur(e){
    e.preventDefault(); var f = e.target, er = document.getElementById('tbFormErr'), v = function(n){ return (f.elements[n].value || '').trim(); };
    var fout = !v('naam') ? 'Vul je naam in.' : !/^[+0-9 ()-]{10,}$/.test(v('telefoon')) ? 'Vul een geldig telefoonnummer in.' : !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v('email')) ? 'Vul een geldig e-mailadres in.' : '';
    if(fout){ er.textContent = fout; er.hidden = false; return; }
    var p = PK[st.keuze], r = reken(st.keuze), zp = document.getElementById('tbZp'), btn = f.querySelector('button[type=submit]'), t = utm();
    var velden = {'form-name':'thuisbatterij-advies', 'bot-field':v('bot-field'), naam:v('naam'), telefoon:v('telefoon'), email:v('email'),
      postcode:st.postcode, huisnummer:st.huisnummer, advies:'Thuisbatterij ' + p.kwh + ' kWh + ' + p.kw + ' kW omvormer (' + p.fase + ')' + (st.keuze !== advies() ? ' (zelf gekozen; advies was ' + PK[advies()].kwh + ' kWh ' + PK[advies()].fase + ')' : ''), prijs:eur(p.prijs) + ' excl. btw',
      zonnepanelen:st.panelen === 'ja' ? 'ja, ca. ' + st.aantal + ' panelen' : st.panelen === 'straks' ? 'nog niet, wil ze erbij' : 'nee',
      ook_zonnepanelen:zp && zp.checked ? 'ja' : '', verbruik:fmt(st.verbruik > 0 ? st.verbruik : 3500) + ' kWh',
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
    var p = PK[st.keuze];
    return '<div class="tb-ok"><div class="big">' + IC.kal.replace('width="22" height="22"', 'width="32" height="32"') + '</div><h1 class="tb-h">Bedankt, ' + esc((st.naam || '').split(' ')[0]) + '! Je aanvraag is binnen.</h1>' +
      '<p>We bellen je zo snel mogelijk over je thuisbatterij van ' + p.kwh + ' kWh. Wil je niet wachten? Plan meteen zelf een moment dat jou uitkomt.</p>' +
      '<div class="tb-book"><button type="button" data-book="bel"><b>Belafspraak</b><span>15 minuten, wij bellen jou</span></button><button type="button" data-book="huis"><b>Adviseur aan huis</b><span>we kijken naar je meterkast en woning</span></button>' +
      '<a href="https://wa.me/31853335687?text=' + encodeURIComponent('Hoi Voltwijk, ik heb net een offerte voor een thuisbatterij aangevraagd. Hier een foto van mijn meterkast:') + '" target="_blank" rel="noopener"><b>Foto meterkast sturen</b><span>via WhatsApp, dan gaat het nog sneller</span></a></div></div>';
  }
  /* adres al ingevuld op een andere pagina? Dan meteen door naar de volgende vraag */
  if(document.querySelector('.tb-solo')){ try{ var s0 = JSON.parse(sessionStorage.getItem('vwCalcStart') || 'null');
    if(s0 && s0.postcode){ st.postcode = s0.postcode; st.huisnummer = s0.huisnummer; sessionStorage.removeItem('vwCalcStart'); hist = ['adres']; cur = 'panelen'; started = true; track('calc_stap', {stap: 'panelen'}); } }catch(e){} }
  render(false);
  /* knop onderaan het aanbod (mobiel) wijst ook naar de offerte */
  document.addEventListener('click', function(ev){ var t = ev.target.closest && ev.target.closest('#tbOfGo'); if(t){ track('offerte_klik', {batterij: st.keuze}); go('gegevens'); } });
})();
</script>'''

def pk_js():
    out = {}
    for p in PAKKETTEN:
        t = PK_TXT.get(p['id'], {})
        out[p['id']] = {'kwh': p['kwh'], 'kw': p['kw'], 'fase': p['fase'], 'prijs': p['prijs'], 'naam': t.get('naam', ''), 'kort': t.get('kort', ''),
                        'feat': t.get('feat', []), 'foto': t.get('foto', [])}
    return json.dumps(out, ensure_ascii=False)

def component(solo=False):
    """De calculator zelf: stappenbalk + vraagvlak. Staat op /thuisbatterij-berekenen (solo) en op de homepage."""
    icjson = json.dumps({k: svg(k) for k in IC}, ensure_ascii=False)
    js = JS.replace('__PK__', pk_js()).replace('__IC__', icjson).replace('__INC__', json.dumps(INBEGREPEN, ensure_ascii=False))
    return (CSS + f'''
  <div class="tb-wrap{' tb-solo' if solo else ''}" id="calculator" style="scroll-margin-top:64px;">
  <div class="tb-band"><div class="tb-steps" id="tbSteps" aria-label="Stappen"></div></div>
  <div class="tb-main" aria-live="polite"><div id="tbMain" style="display:flex;flex-direction:column;flex:1;"><noscript>Zet JavaScript aan om de calculator te gebruiken, of bel ons op {TEL}.</noscript></div></div>
  </div>
''' + js)

def main_html():
    return f'''<div class="blk-light tb-page">
  {PAGE_CSS}
  {component(True)}
  <form name="thuisbatterij-advies" data-netlify="true" netlify-honeypot="bot-field" hidden>
    <input name="bot-field"><input name="naam"><input name="telefoon"><input name="email"><input name="postcode"><input name="huisnummer">
    <input name="advies"><input name="prijs"><input name="zonnepanelen"><input name="ook_zonnepanelen"><input name="verbruik"><input name="extra">
    <input name="aansluiting"><input name="belangrijk"><input name="geschatte_besparing"><input name="pagina"><input name="bron"><input name="utm_content"><input name="gclid"><input name="fbclid">
  </form>
</div>
'''

def nav_html(logo):
    return f'''<div id="siteNav">
    <div class="wrap nav-inner tb-topbar">
      <a href="/" aria-label="Voltwijk, naar de homepage" class="vw-heading" style="display:inline-flex;align-items:center;color:inherit;">{logo}</a>
      <div class="r"><a class="tb-tel" href="{TEL_HREF}" aria-label="Bel Voltwijk: {TEL}"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg><span>{TEL}</span></a></div>
    </div>
  </div>'''


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

NAV_L = ('<a href="/product-batterij" style="color:inherit;text-decoration:none;">THUISBATTERIJ</a>'
         '<a href="/product-zonnepanelen" style="color:inherit;text-decoration:none;">ZONNEPANELEN</a>'
         '<a href="/producten" style="color:inherit;text-decoration:none;">ALLE PRODUCTEN</a>')
NAV_R = ('<a href="/over-ons" style="color:inherit;text-decoration:none;">OVER ONS</a>'
         '<a href="/contact" style="color:inherit;text-decoration:none;">CONTACT</a>'
         '<a href="/contact" data-book="" class="nav-book" style="color:inherit;text-decoration:none;">GRATIS ADVIESGESPREK</a>')
NAV_M = ('<a href="/product-batterij">THUISBATTERIJ</a>\n      <a href="' + URL + '">THUISBATTERIJ BEREKENEN</a>\n      <a href="/product-zonnepanelen">ZONNEPANELEN</a>\n'
         '      <a href="/producten">ALLE PRODUCTEN</a>\n      <a href="/hoe-het-werkt">HOE HET WERKT</a>\n      <a href="/reviews">REVIEWS</a>\n'
         '      <a href="/inzichten">KENNISBANK</a>\n      <a href="/over-ons">OVER ONS</a>\n      <a href="/contact">CONTACT</a>\n'
         '      <a href="/contact" data-book="">GRATIS ADVIESGESPREK</a>\n')
NAV_CSS = ('<style id="vw-navbook">.nav-book{border:1.5px solid currentColor;border-radius:999px;padding:8px 14px;white-space:nowrap;}'
           '#siteNav.is-stuck .nav-book,#siteNav.on-light .nav-book{background:var(--primary);border-color:var(--primary);color:#fff !important;}'
           '@media (max-width:1180px){#siteNav .nav-links a[href="/producten"]{display:none;}}</style>')

def nav(s):
    """Menu: wat we doen (thuisbatterij, zonnepanelen, alle producten), over ons, contact en een duidelijke knop voor een adviesgesprek."""
    s = re.sub(r'(<div class="nav-links">\s*)<a href="/producten"[^>]*>PRODUCTEN</a><a href="[^"]*"[^>]*>THUISBATTERIJ BEREKENEN</a><a href="/inzichten"[^>]*>KENNISBANK</a>',
               lambda m: m.group(1) + NAV_L, s, count=1)
    s = re.sub(r'(<div class="nav-links" style="justify-content:flex-end;">\s*)<a href="/reviews"[^>]*>REVIEWS</a><a href="/over-ons"[^>]*>OVER ONS</a><a href="/contact"[^>]*>CONTACT</a>',
               lambda m: m.group(1) + NAV_R, s, count=1)
    s = re.sub(r'(<div id="mobileNavPanel" class="mobile-nav-panel">\n\s*)<a href="/producten">PRODUCTEN</a>\n.*?(?=\s*<a href="tel:)',
               lambda m: m.group(1) + NAV_M.rstrip('\n'), s, count=1, flags=re.S)
    if 'id="vw-navbook"' not in s and 'class="nav-book"' in s:
        s = s.replace('<div id="siteNav">', NAV_CSS + '\n  <div id="siteNav">', 1)
    return s

def patch(f, s):
    s = nav(s)
    if f == 'index.html':
        # homepage: de calculator zelf, direct onder de video; knoppen op de pagina scrollen ernaartoe
        s = re.sub(r'<!-- vw-funnel-cta:start -->.*?<!-- vw-funnel-cta:end -->', '', s, flags=re.S)
        s = re.sub(r'<!-- vw-home-calc:start -->.*?<!-- vw-home-calc:end -->', lambda m: '<!-- vw-home-calc:start -->' + component() + '<!-- vw-home-calc:end -->', s, count=1, flags=re.S)
        s = s.replace(f'href="{URL}"', 'href="#calculator"')
    s = re.sub(r'<!-- vw-funnel-cta:start -->.*?<!-- vw-funnel-cta:end -->', '<!--vw-calc-plek-->', s, flags=re.S)
    m = re.search(r'<div id="calculator"', s)
    if m:
        a, b = remove_div(s, m.start()); s = a + '<!--vw-calc-plek-->' + b
    s = re.sub(r'\n?<!--vw-batterijkeuze-->.*?<!--/vw-batterijkeuze-->', '', s, flags=re.S)
    if '<!--vw-calc-plek-->' in s:
        s = s.replace('<!--vw-calc-plek-->', band(f), 1).replace('<!--vw-calc-plek-->', '')
    s = s.replace('<!--vw-batterijkeuze-plek-->', '')
    # links naar de oude calculators
    s = s.replace('href="/bereken-je-prijs"', f'href="{URL}"' if f != 'index.html' else 'href="#calculator"').replace('href="https://voltwijk.nl/bereken-je-prijs"', f'href="https://voltwijk.nl{URL}"')
    s = s.replace('href="/product-batterij#batterijkeuze"', f'href="{URL}"').replace('href="/thuisbatterij-actie"', f'href="{URL}"')
    s = s.replace('href="#batterijkeuze"', f'href="{URL}"')
    if f in ANDERS: s = s.replace('href="#calculator"', 'href="#offerte"')
    s = re.sub(r'href="/(product-[a-z]+)#calculator"', lambda m: f'href="/{m.group(1)}#offerte"' if m.group(1) + '.html' in ANDERS else f'href="{URL}"', s)
    s = s.replace('bereken: "/bereken-je-prijs"', 'bereken: "' + URL + '"')
    s = s.replace("title:'Besparingscheck', desc:'Vul je postcode en woningtype in en zie binnen een minuut een eerste inschatting van je vaste prijs en besparing — nog voordat je ergens voor kiest.', cta:{label:'Check je besparing', href: VW_URLS.bereken}",
                  "title:'Bereken of vraag aan', desc:'Bereken online in 1 minuut welke thuisbatterij bij je past, of vraag een offerte aan voor zonnepanelen, een warmtepomp of een ander product. Je zit nergens aan vast.', cta:{label:'Bekijk onze producten', href: '/producten'}")
    s = s.replace("title:'Bereken je thuisbatterij', desc:'Beantwoord zes korte vragen en zie binnen een minuut welke thuisbatterij past, wat hij kost en wat je ongeveer bespaart. Je zit nergens aan vast.', cta:{label:'Bereken je thuisbatterij', href: VW_URLS.bereken}",
                  "title:'Bereken of vraag aan', desc:'Bereken online in 1 minuut welke thuisbatterij bij je past, of vraag een offerte aan voor zonnepanelen, een warmtepomp of een ander product. Je zit nergens aan vast.', cta:{label:'Bekijk onze producten', href: '/producten'}")
    if f not in ANDERS and f != 'index.html': s = s.replace('href="#calculator"', f'href="{URL}"')
    # knoppen en menu
    s = s.replace('>BEREKEN JE PRIJS<', '>THUISBATTERIJ BEREKENEN<')
    if anders(f):
        s = s.replace('>Bereken je prijs &amp; plan direct →<', '>Plan gratis adviesgesprek →<').replace('>Prijs berekenen &amp; inplannen →<', '>Vraag een offerte aan →<')
    else:
        s = s.replace('>Bereken je prijs &amp; plan direct →<', '>Bereken je thuisbatterij →<').replace('>Prijs berekenen &amp; inplannen →<', '>Bereken je thuisbatterij →<')
    s = s.replace('>bereken je prijs<', '>bereken welke thuisbatterij past<').replace('>Bereken je prijs<', '>Bereken je thuisbatterij<').replace('>bereken direct je prijs<', '>bereken welke thuisbatterij past<')
    s = s.replace('>prijscalculator<', '>batterijcalculator<')
    s = s.replace('>Welke batterij past bij mij? →<', '>Bereken je thuisbatterij →<')
    # knoppen naar een productpagina horen de tekst van dat product te dragen
    s = re.sub(r'<a href="/product-([a-z]+)"([^>]*)>Bereken je thuisbatterij</a>',
               lambda m: f'<a href="{URL}"{m.group(2)}>Bereken je thuisbatterij</a>' if m.group(1) == 'batterij' else f'<a href="/product-{m.group(1)}#offerte"{m.group(2)}>Vraag een offerte aan</a>', s)
    # onder het overzicht van alle producten en in artikelen over andere producten: een adviesgesprek, geen batterijcalculator
    for h in (URL, '#calculator'):
        s = s.replace(f'<div style="text-align:center;margin-top:36px;">\n      <a href="{h}" class="btn-secondary" style="text-decoration:none;">Bereken je thuisbatterij →</a>',
                      '<div style="text-align:center;margin-top:36px;">\n      <a href="/contact" data-book="" class="btn-secondary" style="text-decoration:none;">Plan gratis adviesgesprek →</a>')
    if anders(f) or f == 'artikel-vergelijking.html':
        s = s.replace(f'<a href="{URL}" class="btn" style="background:#fff;color:var(--primary);display:inline-block;padding:12px 26px;border-radius:100px;font-weight:800;text-decoration:none;font-size:14px;">Bereken je thuisbatterij</a>',
                      '<a href="/contact" data-book="" class="btn" style="background:#fff;color:var(--primary);display:inline-block;padding:12px 26px;border-radius:100px;font-weight:800;text-decoration:none;font-size:14px;">Plan gratis adviesgesprek</a>').replace('📅 In 4 vragen je advies en prijs', '📅 In 1 minuut je advies en vaste prijs')
    s = s.replace('>batterijcalculator</a> of de <a href="' + URL + '">batterijkeuzehulp</a> zie je', '>batterijcalculator</a> zie je')
    s = s.replace('Met de batterijkeuzehulp zie je in vier vragen welke batterij bij je past', 'Met de batterijcalculator zie je in een minuut welke batterij bij je past')
    # productkaarten in PRODUCTS (JS): batterij naar de calculator, de rest naar het offerteblok
    s = s.replace("cta:'Bereken welke batterij past'", "cta:'Bereken je thuisbatterij'").replace("cta:'Prijs berekenen &amp; inplannen'", "cta:'Vraag een offerte aan'")
    s = s.replace("'<a href=\"#calculator\" class=\"btn-primary\" style=\"background:'+p.accent+';color:var(--dark);text-decoration:none;\">'+p.cta+' →</a>'",
                  "'<a href=\"'+(p.cta==='Bereken je thuisbatterij'?'" + URL + "':'#offerte')+'\" class=\"btn-primary\" style=\"background:'+p.accent+';color:var(--dark);text-decoration:none;\">'+p.cta+' →</a>'")
    if f == 'index.html': s = s.replace(f'href="{URL}"', 'href="#calculator"')
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
