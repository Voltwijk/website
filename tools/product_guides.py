# Voegt per product een blok "Goed om te weten" toe met korte, bruikbare antwoorden
# en een link naar het uitgebreide artikel. Past de PRODUCTS-data en de productlayout
# aan in alle pagina's. Veilig om opnieuw te draaien. Daarna: node tools/prerender-products.js
import glob, re, json, os
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
G = {
 'batterij': [
  ['Wat doet een thuisbatterij?', 'Hij slaat de stroom op die je zonnepanelen overdag over hebben, en geeft die ’s avonds en ’s nachts weer af aan je huis. Zo gebruik je meer van je eigen stroom en koop je minder in.', 'artikel-wat-doet-een-thuisbatterij'],
  ['Wat doet het EMS?', 'Het energiemanagementsysteem is het brein van de batterij. Het kijkt naar de zonverwachting, je verbruik en (met een dynamisch contract) de uurprijzen, en beslist wanneer de batterij laadt, ontlaadt of wacht.', 'artikel-ems-energiemanagementsysteem-thuisbatterij'],
  ['Krijg je de btw terug?', 'Nee. Op zonnepanelen geldt 0% btw, maar een thuisbatterij valt daar niet onder: je betaalt 21% btw en als particulier kun je die niet terugvragen.', 'artikel-btw-thuisbatterij-terugvragen'],
  ['Hoe groot moet je batterij zijn?', 'Vuistregel: ongeveer zo groot als wat je ’s avonds en ’s nachts verbruikt, en niet groter dan het overschot dat je overdag echt hebt. Groter is niet automatisch beter.', 'artikel-thuisbatterij-hoe-groot'],
  ['Loont een batterij als salderen stopt?', 'Vanaf 2027 is stroom die je teruglevert minder waard. Met een batterij gebruik je die stroom zelf, en juist dan wordt opslaan interessanter.', 'artikel-thuisbatterij-na-salderen'],
  ['Batterij en een dynamisch contract', 'Met uurprijzen kan de batterij laden als stroom goedkoop is en ontladen als hij duur is. Dat levert ook op dagen zonder zon iets op.', 'artikel-dynamisch-contract-en-batterij'],
 ],
 'zonnepanelen': [
  ['Betaal je btw op zonnepanelen?', 'Nee. Sinds 2023 geldt 0% btw op zonnepanelen én de installatie, voor panelen op of bij je woning. Je hoeft dus niets meer terug te vragen.', 'artikel-btw-zonnepanelen-nultarief'],
  ['Hoeveel panelen heb je nodig?', 'Vuistregel: een paneel van 440 Wp levert op een goed zuiddak in Nederland zo’n 375 tot 400 kWh per jaar. Deel je jaarverbruik daardoor, en reken een toekomstige warmtepomp of auto mee.', 'artikel-hoeveel-zonnepanelen-nodig'],
  ['Wat verandert er als salderen stopt?', 'Vanaf 1 januari 2027 mag je teruggeleverde stroom niet meer wegstrepen tegen je verbruik. Zelf verbruiken wordt daardoor belangrijker dan zoveel mogelijk terugleveren.', 'artikel-salderingsregeling-2027'],
  ['Omvormer, optimizers of micro-omvormers?', 'Op een dak zonder schaduw volstaat meestal één omvormer. Heb je schaduw of meerdere dakvlakken, dan halen optimizers of micro-omvormers meer uit elk paneel.', 'artikel-omvormer-of-micro-omvormers'],
  ['Batterij of alles terugleveren?', 'Na 2027 levert terugleveren minder op. Of een batterij voor jou loont, hangt af van wanneer je stroom gebruikt en hoeveel je overhoudt.', 'artikel-zonnepanelen-zonder-salderen-batterij-of-teruglevering'],
  ['Wat kosten zonnepanelen nu?', 'Panelen zijn de afgelopen jaren flink goedkoper geworden. Bij ons betaal je een vaste prijs vooraf, inclusief installatie en aanmelding bij je netbeheerder.', 'artikel-zonnepanelen-prijs'],
 ],
 'warmtepomp': [
  ['Hybride of volledig elektrisch?', 'Een hybride warmtepomp werkt samen met je cv-ketel en past in bijna elk huis. Volledig elektrisch vervangt de ketel helemaal, maar vraagt om goede isolatie en een lage aanvoertemperatuur.', 'artikel-hybride-of-volledige-warmtepomp'],
  ['Is je huis geschikt?', 'Een simpele test: zet je cv-ketel in de winter op 55 °C aanvoertemperatuur. Blijft het binnen warm genoeg, dan is je huis vaak geschikt.', 'artikel-is-mijn-huis-geschikt-voor-een-warmtepomp'],
  ['Wat betekenen COP en SCOP?', 'De COP is hoeveel warmte je krijgt per kWh stroom, op één meetpunt. Onze warmtepomp haalt 4,7 bij A7/W35: 1 kWh stroom wordt bijna 5 kWh warmte. De SCOP is het realistischere seizoensgemiddelde.', 'artikel-cop-en-scop-uitgelegd'],
  ['Welke subsidie krijg je?', 'Voor warmtepompen geldt de ISDE-subsidie. Je vraagt die aan ná de installatie; voor onze 6 kW warmtepomp is dat indicatief tot € 2.550.', 'artikel-isde-subsidie-2026'],
  ['Maakt een warmtepomp veel geluid?', 'Moderne buitenunits zijn stil, en er gelden wettelijke geluidsgrenzen op de erfgrens. De plek van de buitenunit maakt het grootste verschil.', 'artikel-warmtepomp-geluid'],
  ['Mag de netbeheerder je warmtepomp aansturen?', 'Bij drukte op het stroomnet kan een warmtepomp tijdelijk worden teruggeregeld. Wat dat betekent voor je comfort, lees je hier.', 'artikel-warmtepomp-sturing'],
 ],
 'airco': [
  ['Wat kost een airco aan stroom?', 'Minder dan veel mensen denken: een zuinige airco levert per kWh stroom meerdere kWh koeling of warmte. In het artikel staat een rekenvoorbeeld voor zomer en tussenseizoen.', 'artikel-wat-kost-een-airco-aan-stroom'],
  ['Welk vermogen heb je nodig?', 'Dat hangt af van de grootte van de kamer, de isolatie en de zon op de ramen. Te klein koelt niet genoeg, te groot schakelt steeds aan en uit.', 'artikel-welk-vermogen-airco'],
  ['Kun je ermee verwarmen?', 'Ja, als zuinige bijverwarming in het voor- en najaar. Het vervangt je cv-ketel niet volledig, maar kan wel veel gas besparen.', 'artikel-airco-als-bijverwarming'],
  ['Onderhoud en F-gassen', 'Filters maak je zelf schoon. Installatie en werk aan het koelcircuit mag alleen een F-gassen-gecertificeerd bedrijf doen, dus doe-het-zelfsets zijn geen goed idee.', 'artikel-airco-onderhoud-en-f-gassen'],
  ['Airco, warmtepomp of zonneboiler?', 'Ze lossen elk een ander probleem op. Deze vergelijking helpt je kiezen wat bij jouw huis past.', 'artikel-vergelijking'],
 ],
 'boiler': [
  ['Welke inhoud heb je nodig?', 'Dat hangt vooral af van het aantal personen en hoe lang en vaak je doucht. In het artikel staat een vuistregel per huishouden.', 'artikel-welke-boilerinhoud-heb-ik-nodig'],
  ['Warmtepompboiler of gewone elektrische boiler?', 'Een warmtepompboiler haalt warmte uit de lucht en is ongeveer drie keer zo zuinig als een gewone elektrische boiler. Onze boiler is van dit type (COP 3,1).', 'artikel-warmtepompboiler-of-elektrische-boiler'],
  ['Opwarmen met je eigen zonnestroom', 'Laat de boiler midden op de dag opwarmen, als je panelen het meest leveren. Zo werkt je boiler als een batterij voor warmte.', 'artikel-boiler-opwarmen-met-zonnestroom'],
  ['Elektrisch of op gas?', 'Wat is goedkoper in 2026? We zetten de kosten en de voor- en nadelen naast elkaar.', 'artikel-elektrische-boiler-vs-gas'],
 ],
 'laadpaal': [
  ['1-fase of 3-fase laden?', 'Op 1-fase laad je met maximaal zo’n 3,7 kW, op 3-fase tot 11 kW. Je auto bepaalt ook wat er maximaal in kan.', 'artikel-1-fase-of-3-fase-laden'],
  ['Laadkosten vergoed door je werkgever?', 'Dat kan, als de geladen kWh aantoonbaar zijn. Daarvoor is een MID-gecertificeerde meter nodig; we bespreken vooraf of je dat wilt.', 'artikel-laadkosten-werkgever-vergoeding-mid-meter'],
  ['Wat is load balancing?', 'Het laadvermogen past zich automatisch aan aan wat de rest van je huis verbruikt, zodat je hoofdzekering niet doorslaat. Soms voorkom je zo een zwaardere aansluiting.', 'artikel-load-balancing-laadpaal'],
  ['Slim laden op de goedkoopste uren', 'Je auto hoeft pas ’s ochtends vol. Door te laden als stroom goedkoop is of je panelen leveren, bespaar je zonder dat je er iets van merkt.', 'artikel-laadpaal-slim-laden'],
 ],
 'meterkast': [
  ['Heb je een 3-fase aansluiting nodig?', 'Voor een 11 kW-laadpaal, een grote warmtepomp of veel zonnepanelen vaak wel. Die vraag je aan bij je netbeheerder; wachttijd en kosten verschillen per regio.', 'artikel-3-fase-aansluiting-aanvragen'],
  ['Groepen en aardlekschakelaars', 'Grote apparaten krijgen een eigen groep, en elke groep hoort achter een aardlekschakelaar. Een laadpaal heeft daarnaast bescherming tegen gelijkstroom-lekstromen nodig.', 'artikel-groepenkast-aardlekschakelaars-uitgelegd'],
  ['Wanneer moet je meterkast vervangen?', 'Oude smeltzekeringen, geen of te weinig aardlekschakelaars, of groepen die regelmatig uitvallen? Dan is vervangen verstandig, zeker als er een laadpaal of warmtepomp bij komt.', 'artikel-meterkast-vervangen-signalen'],
  ['Waarom begint het vaak in de meterkast?', 'Een thuisbatterij of laadpaal klinkt simpel, maar vraagt vaak iets van je groepenkast. Daarom kijken we er altijd vooraf naar.', 'artikel-meterkast-onderschatte-stap'],
  ['Capaciteitstarief en een vol stroomnet', 'Wat een zwaardere aansluiting betekent voor je vaste kosten, en waarom slim verdelen soms beter is.', 'artikel-capaciteitstarief-en-meterkast'],
 ],
}
missing = [x[2] for v in G.values() for x in v if not os.path.exists(x[2] + '.html')]
if missing: raise SystemExit('ontbrekende artikelen: ' + ', '.join(missing))
TPL_ANCHOR = "    '<div class=\"wrap reveal\" style=\"padding-top:88px;padding-bottom:88px;\">' +\n      '<h2 style=\"font-size:22px;\">Vaak samen besteld</h2>' +"
GUIDE_TPL = """    (p.guide ? '<div class="blk-light"><div class="wrap reveal" style="padding-top:88px;padding-bottom:40px;">' +
      '<div class="pill">Goed om te weten</div>' +
      '<h2 style="font-size:clamp(24px,3.4vw,32px);margin-top:12px;max-width:640px;">Alles over '+(p.guideName||p.name.toLowerCase())+', eerlijk uitgelegd</h2>' +
      '<p style="font-size:15px;color:var(--ink-soft);margin-top:10px;max-width:620px;line-height:1.6;">De vragen die we het vaakst krijgen, kort beantwoord. Wil je het precies weten? Elk onderwerp heeft een uitgebreid artikel.</p>' +
      '<div class="guide-grid">'+p.guide.map(function(g){ return '<a class="guide-card" href="/'+g[2]+'"><h3>'+g[0]+'</h3><p>'+g[1]+'</p><span>Lees het hele artikel →</span></a>'; }).join('')+'</div>' +
      '<p style="margin-top:22px;font-size:14px;"><a href="/inzichten#'+slug+'" style="color:var(--primary);font-weight:800;text-decoration:none;">Alle artikelen over '+(p.guideName||p.name.toLowerCase())+' →</a></p>' +
    '</div></div>' : '') +

"""
GUIDE_CSS = ".guide-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;margin-top:28px;} .guide-card{display:flex;flex-direction:column;padding:22px 22px 20px;border-radius:18px;background:#fff;border:1px solid var(--border);text-decoration:none;color:var(--ink);transition:transform .2s,box-shadow .2s,border-color .2s;} .guide-card:hover{transform:translateY(-3px);border-color:var(--primary);box-shadow:0 22px 40px -28px rgba(16,32,31,.5);} .guide-card h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:17px;line-height:1.3;margin:0;} .guide-card p{font-size:14px;color:var(--ink-soft);line-height:1.6;margin:10px 0 14px;flex:1;} .guide-card span{font-size:13.5px;font-weight:800;color:var(--primary);} .guide-card:focus-visible{outline:2px solid var(--primary);outline-offset:3px;}\n"
NAMES = {'batterij':'de thuisbatterij','zonnepanelen':'zonnepanelen','warmtepomp':'de warmtepomp','airco':'airco’s','boiler':'de elektrische boiler','laadpaal':'de laadpaal','meterkast':'de meterkast'}
n = 0
for f in glob.glob('*.html'):
    s = open(f, encoding='utf-8').read(); o = s
    if 'var PRODUCTS' not in s: continue
    for k, items in G.items():
        blk = re.search(r'\n  ' + k + r': \{\n', s)
        if not blk: continue
        start = blk.end()
        # verwijder eerdere guide-regels
        endm = re.search(r'\n  \}', s[start:]); seg = s[start:start + endm.start()]
        seg2 = re.sub(r'\n    guideName:.*', '', re.sub(r'\n    guide:\[.*', '', seg))
        seg2 = seg2 + ',\n    guideName:' + json.dumps(NAMES[k], ensure_ascii=False) + ',\n    guide:' + json.dumps(items, ensure_ascii=False)
        seg2 = seg2.replace(',,', ',')
        s = s[:start] + seg2 + s[start + endm.start():]
    if TPL_ANCHOR in s and 'p.guide ?' not in s:
        s = s.replace(TPL_ANCHOR, GUIDE_TPL + TPL_ANCHOR, 1)
    if '.guide-grid{' not in s:
        s = s.replace('<style>', '<style>\n' + GUIDE_CSS, 1)
    if s != o: open(f, 'w', encoding='utf-8').write(s); n += 1
print(n, 'bestanden bijgewerkt')
