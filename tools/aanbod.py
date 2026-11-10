#!/usr/bin/env python3
"""Productpagina's: wat we echt installeren, met merk, foto, specificaties en prijs (excl. én incl. btw).

Draai vanuit de repo-root:  python3 tools/aanbod.py   (zit in tools/publish.sh; veilig om vaker te draaien)

Wat het doet:
1. Zet op elke product-*.html de sectie "Wat we installeren" (tussen <!-- vw-aanbod:start/end -->), vlak voor het
   offerte- of calculatorblok, met onderaan: ook andere merken mogelijk, vraag een offerte aan.
2. Werkt in PRODUCTS (in alle pagina's) per product de kop, opsomming, prijs, beschrijving en specificaties bij,
   zodat die overeenkomen met wat we leveren. De thuisbatterij-pakketten voor de calculator staan in tools/battery.py.

Bron van merken, typen, specificaties en prijzen: de prijslijst in het CRM (netlify/lib/prijslijst.mjs in Voltwijk/CRM).
Prijzen zijn excl. btw, inclusief installatie. Zonnepanelen: 0% btw. Geen claims toevoegen die niet in de prijslijst staan.
Na wijzigingen ook `node tools/prerender-products.js` draaien (lokale server op poort 8765).
"""
import glob, json, os, re

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
IMG = '/images/producten/'

def eur(x):
    s = f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return '€ ' + (s[:-3] if s.endswith(',00') else s)
def incl(x): return round(x * 1.21 + 1e-9, 2)
def nb(t): return re.sub(r'€ (?=\d)', '€&nbsp;', t)

# ---------------------------------------------------------------- aanbod per productpagina
# kaart: merk, naam, foto's, punten, prijs (excl. btw), vanaf (meerdere uitvoeringen), btw (21 of 0)
AANBOD = {
 'batterij': {
  'kop': 'Welke thuisbatterijen we installeren',
  'intro': 'Vaste prijzen inclusief hybride omvormer, installatie door onze eigen monteurs, aansluiten in de meterkast en de slimme sturing (EMS). De btw krijg je in veel gevallen terug; dat regelen wij.',
  'kaarten': [
   {'merk': 'FoxESS', 'naam': '10 kWh, alles-in-één (1-fase)', 'foto': ['foxess-p100.webp'], 'prijs': 4500,
    'punten': ['FoxESS P100, 10,24 kWh (± 9,7 kWh bruikbaar)', 'Omvormer 5 kW ingebouwd', 'Wandmontage, IP66', '10 jaar garantie op de batterij']},
   {'merk': 'Dyness + Solis', 'naam': '16 kWh (1-fase)', 'foto': ['dyness.webp', 'solis-1fase-vrij.webp'], 'prijs': 5000, 'badge': 'Meest gekozen',
    'punten': ['Dyness PowerBrick Plus, 16,07 kWh (± 15,3 kWh bruikbaar)', 'Solis hybride omvormer 5 kW', 'Uit te breiden tot ± 32 kWh', '10 jaar fabrieksgarantie op batterij en omvormer']},
   {'merk': 'Dyness + Solis', 'naam': '16 kWh (3-fase)', 'foto': ['dyness.webp', 'solis-3fase-vrij.webp'], 'prijs': 5850, 'vanaf': True,
    'punten': ['Dyness PowerBrick Plus, 16,07 kWh', 'Solis hybride omvormer 8 kW (€ 5.850), 10 kW (€ 6.150) of 12 kW (€ 6.350)', 'Uit te breiden tot ± 32 kWh', '10 jaar fabrieksgarantie op batterij en omvormer']},
   {'merk': 'FoxESS', 'naam': '21 kWh (3-fase)', 'foto': ['foxess-cq7.webp', 'foxess-p3.webp'], 'prijs': 7400,
    'punten': ['3 x FoxESS CQ7, samen ± 21 kWh', 'FoxESS P3 hybride omvormer 10 kW', 'Uit te breiden per module van ± 7 kWh', '10 jaar productgarantie']},
   {'merk': 'FoxESS', 'naam': '28 kWh (3-fase)', 'foto': ['foxess-cq7.webp', 'foxess-p3.webp'], 'prijs': 8700,
    'punten': ['4 x FoxESS CQ7, samen ± 28 kWh', 'FoxESS P3 hybride omvormer 10 kW', 'Uit te breiden per module van ± 7 kWh', '10 jaar productgarantie']},
   {'merk': 'Dyness + Solis', 'naam': '32 kWh (3-fase)', 'foto': ['dyness.webp', 'dyness.webp', 'solis-3fase-vrij.webp'], 'prijs': 8250, 'vanaf': True,
    'punten': ['2 x Dyness PowerBrick Plus (± 30 kWh bruikbaar)', 'Solis hybride omvormer 8 kW (€ 8.250), 10 kW (€ 8.450) of 12 kW (€ 8.600)', 'Voor warmtepomp of elektrische auto', '10 jaar fabrieksgarantie op batterij en omvormer']},
   {'merk': 'FoxESS', 'naam': '35 kWh (3-fase)', 'foto': ['foxess-cq7.webp', 'foxess-p3.webp'], 'prijs': 10100,
    'punten': ['5 x FoxESS CQ7, samen ± 35 kWh', 'FoxESS P3 hybride omvormer 12 kW', 'Uit te breiden per module van ± 7 kWh', '10 jaar productgarantie']},
  ],
  'cta': ('/contact', 'Vraag een offerte aan'),
 },
 'warmtepomp': {
  'kop': 'Welke warmtepompen we installeren',
  'intro': 'Hybride (samen met je cv-ketel) of volledig elektrisch (de cv-ketel gaat eruit). Prijzen inclusief installatie en inregelen; de ISDE-subsidie vragen wij voor je aan en komt daar nog vanaf.',
  'kaarten': [
   {'merk': 'LG', 'naam': 'Therma V hybride', 'foto': ['/images/product-warmtepomp.webp'], 'prijs': 8650, 'vanaf': True, 'fotoAlg': True,
    'punten': ['5 kW (€ 8.650), 7 kW (€ 8.950) of 9 kW (€ 9.250)', 'Werkt samen met je bestaande cv-ketel', 'Gemiddeld ± 70% minder gas voor verwarming (RVO 2024)', 'ISDE € 2.600 tot € 3.025']},
   {'merk': 'Vaillant', 'naam': 'aroTHERM plus hybride', 'foto': ['vaillant-arotherm-plus.webp'], 'prijs': 9750, 'vanaf': True,
    'punten': ['3,5 kW (€ 9.750), 5 kW (€ 9.900) of 7 kW (€ 10.250)', 'Met je bestaande Vaillant-cv-ketel (eBUS)', 'R290, regeling met myVAILLANT-app', 'ISDE € 2.350 tot € 2.800']},
   {'merk': 'LG', 'naam': 'Therma V R290 volledig elektrisch', 'foto': ['/images/product-warmtepomp.webp'], 'prijs': 12300, 'vanaf': True, 'fotoAlg': True,
    'punten': ['5,5 tot 16 kW, 1- of 3-fase', 'Met boiler van 200 liter en buffervat', 'Koudemiddel R290, hoge watertemperatuur', 'ISDE € 2.575 tot € 3.925']},
   {'merk': 'Vaillant', 'naam': 'aroTHERM plus volledig elektrisch', 'foto': ['vaillant-arotherm-plus.webp', 'vaillant-unitower.webp'], 'prijs': 13950, 'vanaf': True,
    'punten': ['3,5 tot 12 kW, 1- of 3-fase', 'uniTOWER met boiler van 190 liter', 'Koudemiddel R290, myVAILLANT-app', 'ISDE € 2.350 tot € 3.925']},
  ],
 },
 'airco': {
  'kop': "Welke airco's we installeren",
  'intro': 'LG-airco’s die koelen én verwarmen, met wifi en de LG ThinQ-app. Prijzen inclusief binnen- en buitenunit, koelleidingen, condensafvoer, elektrische aansluiting en montage door F-gassen-gecertificeerde monteurs.',
  'kaarten': [
   {'merk': 'LG', 'naam': 'DUALCOOL single-split', 'foto': ['lg-dualcool-voor.webp'], 'prijs': 1750, 'vanaf': True,
    'punten': ['2,5 kW (€ 1.750), 3,5 kW (€ 1.800), 5,0 kW (€ 2.100) of 7,0 kW (€ 2.300)', 'Energielabel A++ koelen / A+ verwarmen', 'Koudemiddel R32', 'Eigen buitenunit per airco']},
   {'merk': 'LG', 'naam': 'DUALCOOL Deluxe 3,5 kW', 'foto': ['lg-dualcool-voor.webp'], 'prijs': 2000,
    'punten': ['Single-split, koelen en verwarmen', 'LG ThinQ-app (wifi ingebouwd)', 'Koudemiddel R32']},
   {'merk': 'LG', 'naam': 'ARTCOOL mat zwart 3,5 kW', 'foto': [], 'prijs': 2250,
    'punten': ['Energielabel A+++ koelen / A+++ verwarmen', 'Single-split, koelen en verwarmen', 'LG ThinQ-app (wifi ingebouwd)']},
   {'merk': 'LG', 'naam': 'Multi-split', 'foto': ['lg-dualcool-voor.webp'], 'prijs': 3600, 'vanaf': True,
    'punten': ['Eén buitenunit voor meerdere kamers', '2 units (€ 3.600), 3 units (€ 5.050) of 4 units (€ 6.700)', 'Binnenunits DUALCOOL 2,5 kW', 'LG ThinQ-app']},
  ],
 },
 'zonnepanelen': {
  'kop': 'Welke zonnepanelen we installeren',
  'intro': 'Jinko-panelen met een Solis hybride omvormer, zodat je later makkelijk een thuisbatterij aansluit. Prijzen inclusief montagesysteem, bekabeling, installatie en aanmelding bij de netbeheerder. Op zonnepanelen betaal je 0% btw.',
  'kaarten': [
   {'merk': 'Jinko + Solis', 'naam': 'Schuin dak', 'foto': ['jinko-paneel-vrij.webp', 'solis-1fase-vrij.webp'], 'prijs': 3450, 'vanaf': True, 'btw': 0,
    'punten': ['Jinko Tiger Neo 470 Wp, glas-glas, full black', '6 panelen € 3.450, 12 panelen € 4.850, 20 panelen € 7.250', 'Van 6 tot 30 panelen', 'Solis hybride omvormer, 10 jaar fabrieksgarantie']},
   {'merk': 'Jinko + Solis', 'naam': 'Plat dak', 'foto': ['jinko-paneel-vrij.webp', 'solis-3fase-vrij.webp'], 'prijs': 3660, 'vanaf': True, 'btw': 0,
    'punten': ['Zelfde panelen en omvormer, met montagesysteem voor plat dak', '€ 35 per paneel extra ten opzichte van een schuin dak', 'Van 6 tot 30 panelen', 'Solis hybride omvormer, 10 jaar fabrieksgarantie']},
   {'merk': 'Jinko + FoxESS', 'naam': '12 panelen op de FoxESS-batterij', 'foto': ['jinko-paneel-vrij.webp', 'foxess-p100.webp'], 'prijs': 4100, 'btw': 0,
    'punten': ['12 x Jinko Tiger Neo 470 Wp', 'Rechtstreeks op de FoxESS 10 kWh: geen aparte omvormer nodig', 'Alleen samen met een FoxESS-batterij']},
  ],
 },
 'laadpaal': {
  'kop': 'Welke laadpalen we installeren',
  'intro': 'Prijzen inclusief tot 6 meter kabel, een eigen groep met beveiliging en installatie. Elke meter kabel extra kost € 25 excl. btw.',
  'kaarten': [
   {'merk': 'Anker', 'naam': 'SOLIX V1 Smart EV Charger', 'foto': [], 'prijs': 1074.38,
    'punten': ['Tot 22 kW, 1- of 3-fase, type 2', 'Laden op zonnestroom en load balancing met de meegeleverde Anker Smart Meter', 'App en OCPP']},
   {'merk': 'Zaptec', 'naam': 'Go 2', 'foto': ['/images/product-laadpaal.webp'], 'prijs': 1322.31,
    'punten': ['Tot 22 kW, 1- of 3-fase, type 2', 'MID-gecertificeerde meter: geschikt voor verrekenen met je werkgever', 'Zaptec-app']},
   {'merk': 'FoxESS', 'naam': 'A7300P1 7,3 kW', 'foto': [], 'prijs': 1000,
    'punten': ['7,3 kW, 1-fase, type 2', 'Alleen naast een FoxESS-batterij', 'Samen met de batterij in één app (FoxCloud)']},
  ],
 },
 'boiler': {
  'kop': 'Welke boilers we installeren',
  'intro': 'Elektrische boilers van Ariston, inclusief inlaatcombinatie, ophangbeugel of statief, aansluiten en installatie. Slim op te warmen met zonnestroom of op goedkope uren.',
  'kaarten': [
   {'merk': 'Ariston', 'naam': 'Elektrische boiler 150 liter', 'foto': ['/images/product-boiler.webp'], 'prijs': 1487.60, 'fotoAlg': True,
    'punten': ['Voor 3 à 4 personen (alleen douchen)', '1,8 kW, 1-fase', 'Ruim 4 uur van koud naar ± 60 °C']},
   {'merk': 'Ariston', 'naam': 'Elektrische boiler 200 liter', 'foto': ['/images/product-boiler.webp'], 'prijs': 1694.21, 'fotoAlg': True,
    'punten': ['Voor 4 à 5 personen of met bad', '2,2 kW, 1-fase', '± 5 uur van koud naar ± 60 °C']},
  ],
 },
 'meterkast': {
  'kop': 'Meterkast vervangen',
  'intro': 'Een nieuwe groepenkast, aangelegd door onze eigen monteurs. We kijken vooraf naar foto’s van je huidige meterkast en zeggen eerlijk of vervangen nodig is.',
  'kaarten': [
   {'merk': 'Groepenkast', 'naam': '1-fase, tot 8 groepen', 'foto': ['/images/product-meterkast.webp'], 'prijs': 700, 'fotoAlg': True,
    'punten': ['Nieuwe 1-fase groepenkast, inclusief installatie', 'Elke groep extra € 70 excl. btw']},
   {'merk': 'Groepenkast', 'naam': '3-fase, tot 8 groepen', 'foto': ['/images/product-meterkast.webp'], 'prijs': 850, 'fotoAlg': True,
    'punten': ['Nieuwe 3-fase groepenkast, inclusief installatie', 'Elke groep extra € 70 excl. btw']},
  ],
 },
}

# ---------------------------------------------------------------- PRODUCTS (op alle pagina's)
def P(x): return eur(x) + ' excl. btw'
PROD = {
 'zonnepanelen': {
  'bullets': ['Jinko Tiger Neo 470 Wp: glas-glas en full black', 'Solis hybride omvormer: klaar voor een thuisbatterij', '0% btw, inclusief aanmelding bij de netbeheerder'],
  'price': 'vanaf € 3.450 (6 panelen)',
  'description': 'Jinko-panelen met een Solis hybride omvormer, afgestemd op jouw dak en verbruik. Elk paneel wordt gemonteerd door ons eigen team, inclusief aanmelding bij je netbeheerder.',
  'specs': [['Paneel', 'Jinko Tiger Neo 470 Wp'], ['Type', 'glas-glas, full black'], ['Omvormer', 'Solis hybride, 1- of 3-fase'], ['Aantal', '6 tot 30 panelen'], ['Prijs', '€ 3.450 (6) tot € 10.250 (30), 0% btw'], ['Garantie omvormer', '10 jaar']]},
 'warmtepomp': {
  'bullets': ['Hybride (met je cv-ketel) of volledig elektrisch', 'LG Therma V en Vaillant aroTHERM plus', 'ISDE-subsidie vragen wij voor je aan'],
  'price': 'vanaf ' + P(8650),
  'description': 'Een hybride warmtepomp werkt samen met je cv-ketel en bespaart gemiddeld zo’n 70% gas voor verwarming; een volledig elektrische vervangt de cv-ketel helemaal. Geplaatst door onze eigen monteurs; de ISDE-subsidie vragen wij voor je aan.',
  'specs': [['Merken', 'LG Therma V, Vaillant aroTHERM plus'], ['Hybride', 'vanaf ' + P(8650)], ['Volledig elektrisch', 'vanaf ' + P(12300)], ['Vermogen', '3,5 tot 16 kW'], ['ISDE-subsidie', '€ 2.350 tot € 3.925'], ['Bediening', 'met app']]},
 'airco': {
  'bullets': ['LG DUALCOOL: koelen én verwarmen, met wifi en app', 'Single-split of multi-split voor meerdere kamers', 'Montage door F-gassen-gecertificeerde monteurs'],
  'price': 'vanaf ' + P(1750),
  'description': 'Onze LG-airco koelt in de zomer en verwarmt efficiënt in het voor- en najaar. Geplaatst door onze eigen, F-gassen-gecertificeerde monteurs.',
  'image': IMG + 'lg-dualcool-voor.webp',
  'specs': [['Merk', 'LG'], ['Vermogen', '2,5 tot 7,0 kW'], ['Energielabel', 'A++ koelen / A+ verwarmen (DUALCOOL)'], ['Koudemiddel', 'R32'], ['Bediening', 'LG ThinQ-app'], ['Multi-split', '2 tot 4 binnenunits']]},
 'laadpaal': {
  'bullets': ['Anker SOLIX V1 of Zaptec Go 2: tot 22 kW', 'Slim laden, met app', 'Tot 6 meter kabel en een eigen groep inbegrepen'],
  'price': 'vanaf ' + P(1074.38),
  'description': 'Onze laadpaal wordt tegen de gevel of op een paal bij de oprit gemonteerd, met een eigen groep in de meterkast. Met de app volg je je laadsessies.',
  'specs': [['Merken', 'Anker, Zaptec, FoxESS'], ['Laadvermogen', 'tot 22 kW (3-fase)'], ['Connector', 'type 2'], ['Kabel', 'tot 6 meter inbegrepen'], ['MID-meter', 'Zaptec Go 2']]},
 'boiler': {
  'bullets': ['Ariston elektrische boiler, 150 of 200 liter', 'Slim opwarmen op zonnestroom of goedkope uren', 'Inclusief inlaatcombinatie en installatie'],
  'price': 'vanaf ' + P(1487.60),
  'description': 'Een elektrische boiler verwarmt je water zonder gasaansluiting. Met zonnepanelen erbij warm je overdag op, het goedkoopste moment.',
  'specs': [['Merk', 'Ariston'], ['Inhoud', '150 of 200 liter'], ['Vermogen', '1,8 of 2,2 kW, 1-fase'], ['Opwarmtijd', '± 4 tot 5 uur'], ['Inbegrepen', 'inlaatcombinatie en installatie']]},
 'meterkast': {
  'price': 'vanaf ' + P(700),
  'specs': [['Groepenkast', '1-fase of 3-fase'], ['Groepen', 'tot 8 inbegrepen'], ['Groep extra', '€ 70 excl. btw'], ['Prijs', '€ 700 (1-fase) of € 850 (3-fase) excl. btw']]},
}

def zet_veld(blok, veld, waarde):
    """Vervang veld: '...' of veld:[...] binnen één product in PRODUCTS (JS-objectnotatie)."""
    w = json.dumps(waarde, ensure_ascii=False)
    STR = r"""(?:'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")"""
    if isinstance(waarde, str):
        pat = re.compile(r"(\b" + veld + r":)" + STR)
    elif veld == 'specs':
        pat = re.compile(r"(\b" + veld + r":)\[(?:\[\s*" + STR + r"\s*,\s*" + STR + r"\s*\]\s*,?\s*)*\]")
    else:
        pat = re.compile(r"(\b" + veld + r":)\[(?:\s*" + STR + r"\s*,?)*\s*\]")
    n = len(pat.findall(blok))
    if n != 1: raise SystemExit(f'PRODUCTS: veld {veld} niet precies één keer gevonden ({n})')
    return pat.sub(lambda m: m.group(1) + w, blok)

def products(s):
    if 'var PRODUCTS = {' not in s: return s
    for key, velden in PROD.items():
        m = re.search(r'\n  ' + key + r': \{\n.*?\n  \}', s, re.S)
        if not m: continue
        blok = m.group(0)
        for veld, waarde in velden.items(): blok = zet_veld(blok, veld, waarde)
        s = s[:m.start()] + blok + s[m.end():]
    return s

# ---------------------------------------------------------------- sectie
CSS = '''<style id="vw-aanbod-css">
.vwa{padding:64px 0 24px;}
.vwa h2{font-family:'Bricolage Grotesque','Bricolage Fallback',system-ui,sans-serif;font-weight:800;font-size:clamp(28px,4vw,40px);letter-spacing:-.02em;line-height:1.08;color:var(--ink);margin:6px 0 10px;}
.vwa .in{color:var(--ink-soft);font-size:16px;line-height:1.6;max-width:760px;}
.vwa-top{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;}
.vwa-nav{display:flex;gap:8px;flex-shrink:0;}
.vwa-nav button{width:46px;height:46px;border-radius:50%;border:1px solid var(--border);background:#fff;color:var(--ink);font-size:20px;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;transition:background .2s,opacity .2s;}
.vwa-nav button:hover{background:var(--surface-tint);}
.vwa-nav button:disabled{opacity:.35;cursor:default;}
.vwa-nav[hidden]{display:none;}
.vwa-g{display:flex;gap:18px;margin-top:28px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-behavior:smooth;padding:2px 2px 16px;scrollbar-width:thin;-webkit-overflow-scrolling:touch;}
.vwa-g>.vwa-k:first-child{margin-left:auto;}
.vwa-g>.vwa-k:last-child{margin-right:auto;}
.vwa-k{position:relative;display:flex;flex-direction:column;flex:0 0 calc((100% - 54px) / 4);min-width:250px;scroll-snap-align:start;background:#fff;border:1px solid var(--border);border-radius:22px;overflow:hidden;}
.vwa-f{height:200px;display:flex;align-items:flex-end;justify-content:center;gap:10px;padding:22px 18px 16px;background:#F4F7F4;border-bottom:1px solid var(--border);}
.vwa-f img{max-height:100%;max-width:62%;object-fit:contain;mix-blend-mode:multiply;}
.vwa-f img+img{max-width:38%;max-height:72%;}
.vwa-f.leeg{align-items:center;background:var(--surface-tint);color:var(--primary);font-weight:800;font-size:15px;}
.vwa-b{display:flex;flex-direction:column;gap:6px;padding:18px 20px 20px;flex:1;}
.vwa-m{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--primary);}
.vwa-n{font-family:'Bricolage Grotesque','Bricolage Fallback',system-ui,sans-serif;font-weight:800;font-size:21px;line-height:1.15;color:var(--ink);}
.vwa ul{list-style:none;margin:6px 0 4px;padding:0;display:flex;flex-direction:column;gap:6px;}
.vwa li{position:relative;padding-left:20px;font-size:14px;line-height:1.45;color:var(--ink-soft);}
.vwa li:before{content:"";position:absolute;left:2px;top:6px;width:10px;height:6px;border-left:2.5px solid var(--primary);border-bottom:2.5px solid var(--primary);transform:rotate(-45deg);}
.vwa-p{margin-top:auto;padding-top:12px;border-top:1px dashed var(--border);}
.vwa-p b{display:block;font-family:'Bricolage Grotesque','Bricolage Fallback',system-ui,sans-serif;font-weight:800;font-size:26px;color:var(--ink);letter-spacing:-.01em;}
.vwa-p small{display:block;font-size:13px;color:var(--ink-faint);font-weight:700;}
.vwa-badge{position:absolute;top:14px;left:14px;background:var(--accent,#FF6B5B);color:#fff;font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;padding:5px 10px;border-radius:999px;}
.vwa-alg{position:absolute;top:14px;right:14px;font-size:11px;color:var(--ink-faint);background:var(--bg);border-radius:999px;padding:3px 9px;}
.vwa-x{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px;margin-top:22px;padding:22px 24px;border-radius:22px;background:var(--surface-tint);}
.vwa-x b{display:block;font-family:'Bricolage Grotesque','Bricolage Fallback',system-ui,sans-serif;font-size:20px;color:var(--ink);}
.vwa-x span{color:var(--ink-soft);font-size:15px;}
.vwa-x a{display:inline-flex;align-items:center;background:var(--primary);color:#fff;font-weight:800;font-size:15px;padding:13px 22px;border-radius:999px;text-decoration:none;white-space:nowrap;}
@media (max-width:600px){.vwa{padding-top:44px;}.vwa-f{height:170px;}.vwa-k{flex-basis:80%;}.vwa-nav{display:none;}}
</style>'''

def foto(f): return f if f.startswith('/') else IMG + f
def kaart(k):
    btw = k.get('btw', 21)
    fotos = k['foto']
    if fotos:
        f = '<div class="vwa-f">' + ''.join(f'<img src="{foto(x)}" alt="{k["merk"]} {k["naam"]}" loading="lazy"' + (' style="mix-blend-mode:normal"' if x.startswith('/images/product-') else '') + '>' for x in fotos[:3]) + '</div>'
    else:
        f = f'<div class="vwa-f leeg">{k["merk"]}</div>'
    va = 'vanaf ' if k.get('vanaf') else ''
    prijs = nb(f'<b>{va}{eur(k["prijs"])}</b><small>{"0% btw" if btw == 0 else "excl. btw · " + eur(incl(k["prijs"])) + " incl. btw"}, inclusief installatie</small>')
    return ('<div class="vwa-k">' + (f'<span class="vwa-badge">{k["badge"]}</span>' if k.get('badge') else '') +
            ('<span class="vwa-alg">voorbeeldfoto</span>' if k.get('fotoAlg') else '') + f +
            f'<div class="vwa-b"><span class="vwa-m">{k["merk"]}</span><span class="vwa-n">{k["naam"]}</span>'
            '<ul>' + ''.join(f'<li>{nb(p)}</li>' for p in k['punten']) + '</ul>'
            f'<div class="vwa-p">{prijs}</div></div></div>')

def sectie(key):
    a = AANBOD[key]
    href, knop = a.get('cta', ('#offerte', 'Vraag een offerte aan'))
    return ('<!-- vw-aanbod:start -->' + CSS + f'<section class="vwa" id="aanbod"><div class="wrap">'
            '<div class="vwa-top"><div><span class="eyebrow">Wat we installeren</span>'
            f'<h2>{a["kop"]}</h2><p class="in">{a["intro"]}</p></div>'
            '<div class="vwa-nav" hidden><button type="button" data-d="-1" aria-label="Vorige">←</button><button type="button" data-d="1" aria-label="Volgende">→</button></div></div>'
            '<div class="vwa-g">' + ''.join(kaart(k) for k in a['kaarten']) + '</div>'
            '<div class="vwa-x"><div><b>Liever een ander merk?</b><span>We installeren ook andere merken. Vraag een offerte aan, dan rekenen we het voor je uit.</span></div>'
            f'<a href="{href}">{knop} →</a></div>'
            +
            '</div></section><script>(function(){var g=document.querySelector(\'.vwa-g\'),n=document.querySelector(\'.vwa-nav\');if(!g||!n)return;var b=n.querySelectorAll(\'button\');function u(){var o=g.scrollWidth>g.clientWidth+4;n.hidden=!o;b[0].disabled=g.scrollLeft<4;b[1].disabled=g.scrollLeft+g.clientWidth>=g.scrollWidth-4;}b.forEach(function(x){x.addEventListener(\'click\',function(){var k=g.querySelector(\'.vwa-k\');g.scrollBy({left:(+x.dataset.d)*((k?k.offsetWidth:280)+18),behavior:\'smooth\'});});});g.addEventListener(\'scroll\',u,{passive:true});window.addEventListener(\'resize\',u);u();})();</script><!-- vw-aanbod:end -->')

n = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    s2 = products(s)
    m = re.match(r'product-([a-z]+)\.html$', f)
    s2 = re.sub(r'<!-- vw-aanbod:start -->.*?<!-- vw-aanbod:end -->\n?', '', s2, flags=re.S)
    if m and m.group(1) in AANBOD and '<!-- vw-funnel-cta:start -->' in s2:
        s2 = s2.replace('<!-- vw-funnel-cta:start -->', sectie(m.group(1)) + '\n<!-- vw-funnel-cta:start -->', 1)
    if s2 != s:
        open(f, 'w', encoding='utf-8').write(s2); n += 1
print('aanbod.py:', n, "pagina's bijgewerkt")
