# Bouwt lokale landingspagina's (installateur-<plaats>.html), het overzicht /werkgebied en de
# WERKGEBIED-kolom in de footer van alle pagina's. Veilig om opnieuw te draaien.
# Daarna altijd: python3 tools/seo.py  (titels/OG/JSON-LD/sitemap)
# Let op: alleen controleerbare feiten per plaats. Netbeheerder hangt af van het exacte adres,
# dat staat ook zo op de pagina's.
import re, html, os, urllib.parse
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)
SHELL = 'artikel-isde-subsidie-2026.html'
esc = lambda s: html.escape(s, quote=True)
def inline(t):
    t = esc(t).replace('&#x27;', "'")
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    return re.sub(r'\[([^\]]+)\]\((/[^)\s]*)\)', r'<a href="\2">\1</a>', t)

PRODUCTS = [
 ('Zonnepanelen', 'vanaf € 3.999', '/product-zonnepanelen', 'thumb-zonnepanelen'),
 ('Thuisbatterij', 'vanaf € 3.499', '/product-batterij', 'thumb-batterij'),
 ('Warmtepomp', 'vanaf € 6.750', '/product-warmtepomp', 'thumb-warmtepomp'),
 ('Airconditioning', 'vanaf € 1.899', '/product-airco', 'thumb-airco'),
 ('Elektrische boiler', 'vanaf € 1.199', '/product-boiler', 'thumb-boiler'),
 ('Laadpaal', 'vanaf € 1.299', '/product-laadpaal', 'thumb-laadpaal'),
 ('Meterkastaanpassing', 'vanaf € 649', '/product-meterkast', 'thumb-meterkast'),
]
ART = {  # slug: titel (voor de 'lees ook'-links)
 'artikel-salderingsregeling-2027': 'Salderingsregeling stopt in 2027: wat betekent dat?',
 'artikel-thuisbatterij-na-salderen': 'Thuisbatterij na het salderen',
 'artikel-hoeveel-zonnepanelen-nodig': 'Hoeveel zonnepanelen heb ik nodig?',
 'artikel-is-mijn-huis-geschikt-voor-een-warmtepomp': 'Is mijn huis geschikt voor een warmtepomp?',
 'artikel-hybride-of-volledige-warmtepomp': 'Hybride of volledige warmtepomp?',
 'artikel-warmtepomp-geluid': 'Warmtepomp en geluid',
 'artikel-isde-subsidie-2026': 'ISDE-subsidie 2026',
 'artikel-3-fase-aansluiting-aanvragen': 'Een 3-fase-aansluiting aanvragen',
 'artikel-laadpaal-slim-laden': 'Slim laden met je laadpaal',
 'artikel-meterkast-vervangen-signalen': 'Signalen dat je meterkast aan vervanging toe is',
 'artikel-capaciteitstarief-en-meterkast': 'Capaciteitstarief en je meterkast',
 'artikel-dynamisch-contract-en-batterij': 'Dynamisch contract en thuisbatterij',
 'artikel-zonnepanelen-prijs': 'Wat kosten zonnepanelen?',
 'artikel-ems-energiemanagementsysteem-thuisbatterij': 'Een EMS bij je thuisbatterij',
 'artikel-omvormer-of-micro-omvormers': 'Omvormer of micro-omvormers?',
}
NB = {
 'Enexis': 'Enexis Netbeheer',
 'Stedin': 'Stedin',
 'Liander': 'Liander',
}
# slug, naam, regio, netbeheerder, beeld, intro, [(kop, tekst)], extra-FAQ (v, a), omliggende kernen, buursteden, artikelen
CITIES = [
 dict(slug='zevenbergen', name='Zevenbergen', region='West-Brabant', nb='Enexis', img='monteur-dak',
  intro='Zevenbergen is onze thuisbasis: ons kantoor zit aan de Schoenmakerij. Vanuit hier installeren we zonnepanelen, thuisbatterijen, warmtepompen en laadpalen in de hele gemeente Moerdijk en de rest van het land, altijd met ons eigen team en een vaste prijs vooraf.',
  local=[('Om de hoek', 'Wonen in Zevenbergen of een van de andere kernen van de gemeente Moerdijk? Dan zit je dicht bij ons kantoor. Een vraag stellen, iets laten zien of even langskomen voor advies is dan zo geregeld.'),
         ('Netbeheerder Enexis', 'In de gemeente Moerdijk is Enexis de netbeheerder. Is er voor jouw installatie een zwaardere aansluiting nodig, bijvoorbeeld 3-fase voor een warmtepomp of laadpaal, dan vragen wij die voor je aan.'),
         ('Vestingstadje Willemstad', 'Willemstad is een beschermd stadsgezicht. Daar gelden voor zonnepanelen die vanaf de straat zichtbaar zijn vaak extra regels. We kijken vooraf met je mee en regelen een vergunning als dat nodig is.'),
         ('Na 2027 geen salderen meer', 'Ook in Moerdijk stopt de salderingsregeling op 1 januari 2027. Heb je al panelen, dan is een thuisbatterij de logische volgende stap om je eigen stroom zelf te gebruiken.')],
  faq=('Kan ik bij jullie in Zevenbergen langskomen?', 'Ja, ons kantoor zit aan de Schoenmakerij 15a in Zevenbergen. Laat wel even van tevoren weten dat je komt, dan zorgen we dat er iemand is die je vragen kan beantwoorden. Bellen of appen kan ook: 085 333 5687.'),
  near=['Klundert', 'Fijnaart', 'Willemstad', 'Moerdijk', 'Zevenbergschen Hoek', 'Standdaarbuiten', 'Noordhoek', 'Langeweg'],
  buren=['breda', 'etten-leur', 'roosendaal', 'dordrecht', 'oosterhout'],
  arts=['artikel-thuisbatterij-na-salderen', 'artikel-salderingsregeling-2027', 'artikel-is-mijn-huis-geschikt-voor-een-warmtepomp']),
 dict(slug='breda', name='Breda', region='West-Brabant', nb='Enexis', img='zonnepanelen-dak',
  intro='Van een jaren-30-woning in Ginneken tot een rijtjeshuis in de Haagse Beemden: in Breda zien we alle soorten woningen. Wij installeren er zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen met ons eigen team, voor een vaste prijs die je vooraf al kent.',
  local=[('Verschillende soorten woningen', 'Oudere woningen in bijvoorbeeld Ginneken of Princenhage hebben vaak een kleinere meterkast en minder isolatie dan nieuwere wijken. Dat bepaalt of een volledige of een hybride warmtepomp beter past. We checken het vooraf, zodat je niet voor verrassingen komt te staan.'),
         ('Netbeheerder Enexis', 'In Breda is Enexis de netbeheerder. Moet je aansluiting worden verzwaard of wil je naar 3-fase? Dat vragen wij voor je aan, dat hoef je niet zelf te doen.'),
         ('Historische binnenstad', 'Woon je in de binnenstad of in een monument? Dan gelden er voor zonnepanelen en buitenunits vaak extra regels. We zoeken uit wat er voor jouw adres geldt en regelen een vergunning als die nodig is.'),
         ('Laadpaal op eigen terrein', 'Heb je een eigen oprit of garage, dan is een laadpaal thuis meestal de goedkoopste manier van laden. Met slim laden laad je op de uren dat stroom het goedkoopst is.')],
  faq=('Installeren jullie ook in de dorpen rond Breda?', 'Ja. We komen in heel Breda en in de omliggende plaatsen, zoals Prinsenbeek, Teteringen, Bavel en Ulvenhout. Met dezelfde vaste prijzen en ons eigen team.'),
  near=['Prinsenbeek', 'Teteringen', 'Bavel', 'Ulvenhout', 'Princenhage', 'Ginneken', 'Haagse Beemden', 'Rijsbergen'],
  buren=['zevenbergen', 'etten-leur', 'oosterhout', 'tilburg', 'roosendaal'],
  arts=['artikel-hybride-of-volledige-warmtepomp', 'artikel-laadpaal-slim-laden', 'artikel-hoeveel-zonnepanelen-nodig']),
 dict(slug='etten-leur', name='Etten-Leur', region='West-Brabant', nb='Enexis', img='monteur-aan-het-werk',
  intro='Etten-Leur ligt op een steenworp afstand van ons kantoor in Zevenbergen. Veel woningen hier zijn eengezinswoningen met een schuin dak: ideaal voor zonnepanelen, en vaak een goede basis voor een thuisbatterij of warmtepomp.',
  local=[('Dichtbij ons kantoor', 'Doordat we zo dichtbij zitten, kunnen we snel schakelen: voor een inspectie, een vraag achteraf of service na de installatie.'),
         ('Netbeheerder Enexis', 'In Etten-Leur is Enexis de netbeheerder. Wij regelen de aanmelding van je zonnepanelen en, als dat nodig is, een verzwaring van je aansluiting.'),
         ('Rijtjeshuis of hoekwoning', 'Bij een rijtjeshuis is de plek van de buitenunit van een warmtepomp belangrijk, vanwege het geluid bij de buren. We kiezen samen een plek die binnen de geluidsnormen blijft.'),
         ('Meterkast klaar voor de toekomst', 'In veel woningen uit de jaren \'70 en \'80 is de meterkast te klein voor zonnepanelen, een laadpaal én een warmtepomp. We kijken vooraf of er groepen bij moeten, zodat alles in één keer goed gaat.')],
  faq=('Hoe snel kunnen jullie in Etten-Leur installeren?', 'De meeste klanten hebben binnen 2 tot 3 weken na de offerte een geplande installatiedatum. Omdat Etten-Leur dicht bij ons kantoor ligt, kunnen we ook een inspectie of servicebezoek meestal snel inplannen.'),
  near=['Etten', 'Leur', 'Hoeven', 'Sprundel', 'Rucphen', 'Zundert'],
  buren=['zevenbergen', 'breda', 'roosendaal', 'bergen-op-zoom'],
  arts=['artikel-warmtepomp-geluid', 'artikel-meterkast-vervangen-signalen', 'artikel-thuisbatterij-na-salderen']),
 dict(slug='roosendaal', name='Roosendaal', region='West-Brabant', nb='Enexis', img='zonnepanelen-installatie',
  intro='In Roosendaal en de omliggende dorpen installeren we zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen. Altijd met ons eigen team en een vaste prijs, zodat je vooraf precies weet waar je aan toe bent.',
  local=[('Netbeheerder Enexis', 'In Roosendaal is Enexis de netbeheerder. De aanmelding van je installatie en eventuele aanpassingen aan je aansluiting regelen wij.'),
         ('Van gas af, stap voor stap', 'Nog niet klaar voor een volledige warmtepomp? Een hybride warmtepomp of een elektrische boiler is een betaalbare eerste stap om minder gas te gebruiken.'),
         ('Zonnepanelen plus batterij', 'Vanaf 2027 stopt het salderen. Wie nu zonnepanelen neemt, doet er goed aan meteen te kijken of een thuisbatterij loont. We rekenen het eerlijk voor je door.'),
         ('Airco als bijverwarming', 'Een moderne airco koelt in de zomer en verwarmt zuinig in het voor- en najaar. Dat is een goede aanvulling, zeker in woningen zonder vloerverwarming.')],
  faq=('Komen jullie ook in Wouw, Nispen en Oud Gastel?', 'Ja. We installeren in heel Roosendaal en in de dorpen eromheen, zoals Wouw, Nispen, Heerle en Oud Gastel. Met een vaste prijs vooraf en ons eigen team.'),
  near=['Nispen', 'Wouw', 'Heerle', 'Wouwse Plantage', 'Oud Gastel', 'Stampersgat'],
  buren=['bergen-op-zoom', 'etten-leur', 'zevenbergen', 'breda'],
  arts=['artikel-hybride-of-volledige-warmtepomp', 'artikel-airco-als-bijverwarming', 'artikel-salderingsregeling-2027']),
 dict(slug='bergen-op-zoom', name='Bergen op Zoom', region='West-Brabant', nb='Enexis', img='omvormers-afwerking',
  intro='In Bergen op Zoom en omgeving verzorgen we de complete installatie van zonnepanelen, thuisbatterijen, warmtepompen en laadpalen: van advies en vergunning tot aanmelding bij de netbeheerder. Met ons eigen team en een vaste prijs vooraf.',
  local=[('Historische binnenstad', 'De binnenstad van Bergen op Zoom kent veel monumentale panden. Voor zonnepanelen op een monument of in een beschermd gebied is vaak een vergunning nodig. We zoeken het voor je uit en regelen de aanvraag.'),
         ('Netbeheerder Enexis', 'In Bergen op Zoom is Enexis de netbeheerder. Wij melden je installatie aan en regelen een verzwaring als dat nodig is.'),
         ('Micro-omvormers bij schaduw', 'Heb je schaduw op een deel van je dak, bijvoorbeeld door bomen of een dakkapel? Dan kunnen micro-omvormers of optimizers meer opbrengst geven. We adviseren wat bij jouw dak past.'),
         ('Laadpaal met load balancing', 'Een laadpaal met load balancing verdeelt het vermogen automatisch, zodat je hoofdzekering niet uitvalt als tegelijk de oven en de wasmachine aanstaan.')],
  faq=('Mag ik zonnepanelen op mijn huis in de binnenstad van Bergen op Zoom?', 'Dat hangt af van je adres. Bij een monument of in een beschermd stadsgezicht is vaak een omgevingsvergunning nodig, vooral als de panelen vanaf de straat te zien zijn. Wij checken het vooraf en regelen de aanvraag als dat nodig is.'),
  near=['Halsteren', 'Lepelstraat', 'Hoogerheide', 'Woensdrecht', 'Ossendrecht', 'Tholen'],
  buren=['roosendaal', 'etten-leur', 'zevenbergen'],
  arts=['artikel-omvormer-of-micro-omvormers', 'artikel-load-balancing-laadpaal', 'artikel-zonnepanelen-prijs']),
 dict(slug='oosterhout', name='Oosterhout', region='West-Brabant', nb='Enexis', img='warmtepomp-tuinmuur',
  intro='Oosterhout ligt vlak bij Breda en een kort stuk rijden van ons kantoor in Zevenbergen. We installeren hier zonnepanelen, thuisbatterijen, warmtepompen, boilers en laadpalen, met ons eigen team en een vaste prijs vooraf.',
  local=[('Netbeheerder Enexis', 'In Oosterhout is Enexis de netbeheerder. Het contact met de netbeheerder, zoals de aanmelding of een 3-fase-aansluiting, nemen wij van je over.'),
         ('Is je huis klaar voor een warmtepomp?', 'Hoe goed je huis geïsoleerd is, bepaalt welke warmtepomp past. We kijken naar je woning en je verbruik en adviseren eerlijk of een hybride of volledige warmtepomp beter uitpakt.'),
         ('ISDE-subsidie', 'Voor een warmtepomp kun je ISDE-subsidie krijgen. Wij verrekenen die direct in je prijs en regelen de aanvraag.'),
         ('Boiler op zonnestroom', 'Heb je zonnepanelen? Dan kun je een elektrische boiler overdag laten opwarmen met je eigen stroom. Na 2027 is dat extra interessant.')],
  faq=('Regelen jullie de ISDE-subsidie voor mijn warmtepomp in Oosterhout?', 'Ja. We verrekenen de ISDE-subsidie direct in je prijs en doen de aanvraag voor je. Je hoeft niet zelf formulieren in te vullen.'),
  near=['Dorst', 'Den Hout', 'Oosteind', 'Dongen', 'Made', 'Raamsdonksveer'],
  buren=['breda', 'zevenbergen', 'tilburg', 'dordrecht'],
  arts=['artikel-isde-subsidie-2026', 'artikel-is-mijn-huis-geschikt-voor-een-warmtepomp', 'artikel-boiler-opwarmen-met-zonnestroom']),
 dict(slug='dordrecht', name='Dordrecht', region='Drechtsteden', nb='Stedin', img='monteur-en-klant',
  intro='Dordrecht, de oudste stad van Holland, ligt net over het water vanaf ons kantoor in Zevenbergen. Van een monument in de binnenstad tot een eengezinswoning in Stadspolders of Sterrenburg: we installeren er zonnepanelen, thuisbatterijen, warmtepompen en laadpalen met ons eigen team.',
  local=[('Netbeheerder Stedin', 'In Dordrecht is Stedin de netbeheerder, niet Enexis zoals in Brabant. Voor jou verandert er niets: wij regelen de aanmelding en een eventuele verzwaring bij Stedin.'),
         ('Monumenten in de binnenstad', 'De historische binnenstad heeft veel monumenten. Daar is voor zonnepanelen of een buitenunit vaak een vergunning nodig. We zoeken vooraf uit wat voor jouw pand geldt.'),
         ('Vol stroomnet?', 'Stedin heeft in delen van Dordrecht en de Hoeksche Waard netcongestie gemeld voor grote teruglevering door bedrijven. Voor een gewone woningaansluiting met zonnepanelen geldt dat niet. Een thuisbatterij helpt wel om minder terug te leveren.'),
         ('Meer zelf gebruiken', 'Met een thuisbatterij en een energiemanagementsysteem (EMS) gebruik je meer van je eigen zonnestroom. Dat wordt belangrijker nu het salderen in 2027 stopt.')],
  faq=('Wie is de netbeheerder in Dordrecht?', 'In Dordrecht is Stedin de netbeheerder voor stroom. Wij regelen de aanmelding van je zonnepanelen of thuisbatterij en eventuele aanpassingen aan je aansluiting rechtstreeks met Stedin.'),
  near=['Zwijndrecht', 'Papendrecht', 'Sliedrecht', 'Hendrik-Ido-Ambacht', 'Alblasserdam', '\'s-Gravendeel'],
  buren=['zevenbergen', 'rotterdam', 'breda', 'oosterhout'],
  arts=['artikel-ems-energiemanagementsysteem-thuisbatterij', 'artikel-thuisbatterij-na-salderen', 'artikel-salderingsregeling-2027']),
 dict(slug='tilburg', name='Tilburg', region='Midden-Brabant', nb='Enexis', img='batterij-installatie',
  intro='In Tilburg, van de Reeshof tot het centrum, installeren we zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen. Met ons eigen team, een vaste prijs vooraf en zonder gedoe met onderaannemers.',
  local=[('Netbeheerder Enexis', 'In Tilburg is Enexis de netbeheerder. Wij melden je installatie aan en vragen een zwaardere aansluiting aan als je warmtepomp of laadpaal dat nodig heeft.'),
         ('Woningen uit de jaren \'80 en \'90', 'Wijken als de Reeshof zijn grotendeels gebouwd vanaf de jaren \'80. Die woningen zijn vaak redelijk geïsoleerd en daardoor geschikt voor een hybride warmtepomp, of met extra maatregelen voor een volledige.'),
         ('Thuisbatterij met dynamisch contract', 'Met een dynamisch energiecontract laad je je batterij op als stroom goedkoop is en gebruik je hem als stroom duur is. We leggen eerlijk uit wanneer dat loont.'),
         ('Laadpaal thuis', 'Een slimme 11 kW laadpaal laadt de meeste elektrische auto\'s in een nacht vol. Met slim laden gebruik je de goedkoopste uren.')],
  faq=('Hoeveel kost een thuisbatterij in Tilburg?', 'Een thuisbatterij kost bij ons vanaf € 3.499 inclusief installatie. Met de prijscalculator zie je binnen een minuut wat het voor jouw woning kost.'),
  near=['Berkel-Enschot', 'Udenhout', 'Goirle', 'Oisterwijk', 'Hilvarenbeek', 'Reeshof'],
  buren=['breda', 'oosterhout', 's-hertogenbosch', 'eindhoven'],
  arts=['artikel-dynamisch-contract-en-batterij', 'artikel-hybride-of-volledige-warmtepomp', 'artikel-laadpaal-slim-laden']),
 dict(slug='s-hertogenbosch', name='\'s-Hertogenbosch', region='Noordoost-Brabant', nb='Enexis', img='warmtepomp-installatie',
  intro='In \'s-Hertogenbosch, van de historische binnenstad tot nieuwbouw in De Groote Wielen, installeren we zonnepanelen, thuisbatterijen, warmtepompen en laadpalen. Met ons eigen team en een vaste prijs die je vooraf al kent.',
  local=[('Beschermde binnenstad', 'Voor een huis in de binnenstad of een monument is voor zonnepanelen of een buitenunit vaak een vergunning nodig. We zoeken uit wat voor jouw adres geldt en regelen de aanvraag.'),
         ('Netbeheerder Enexis', 'In \'s-Hertogenbosch is Enexis de netbeheerder. De aanmelding en eventuele aanpassingen aan je aansluiting regelen wij.'),
         ('Nieuwbouw: vaak al all-electric', 'Nieuwere woningen, zoals in De Groote Wielen, hebben vaak al een warmtepomp. Dan liggen zonnepanelen uitbreiden of een thuisbatterij meer voor de hand. We kijken wat jouw installatie al kan.'),
         ('Stil buiten', 'Een buitenunit moet binnen de geluidsnorm op de erfgrens blijven. We kiezen een stille unit en een plek waar ook je buren er geen last van hebben.')],
  faq=('Installeren jullie ook in Rosmalen en Vught?', 'Ja. We komen in heel \'s-Hertogenbosch, dus ook in Rosmalen, en in plaatsen eromheen zoals Vught, Vlijmen en Berlicum. Met een vaste prijs vooraf.'),
  near=['Rosmalen', 'Vught', 'Vlijmen', 'Berlicum', 'Sint-Michielsgestel', 'Den Dungen'],
  buren=['tilburg', 'eindhoven', 'utrecht'],
  arts=['artikel-warmtepomp-geluid', 'artikel-ems-energiemanagementsysteem-thuisbatterij', 'artikel-isde-subsidie-2026']),
 dict(slug='eindhoven', name='Eindhoven', region='Zuidoost-Brabant', nb='Enexis', img='laadpaal-installatie',
  intro='In Eindhoven en de omliggende plaatsen installeren we zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen. We werken met ons eigen team en een vaste prijs vooraf, zonder onderaannemers.',
  local=[('Netbeheerder Enexis', 'In Eindhoven is Enexis de netbeheerder. Wij regelen de aanmelding van je installatie en een 3-fase-aansluiting als dat nodig is.'),
         ('Elektrisch rijden', 'Rijd je elektrisch en heb je een eigen oprit? Een slimme laadpaal met load balancing laadt veilig en goedkoop, ook als er thuis tegelijk veel aanstaat.'),
         ('Nieuwbouw in Meerhoven en omgeving', 'In nieuwere wijken is de meterkast vaak al ruim en hangt er soms al een warmtepomp. Zonnepanelen en een thuisbatterij zijn dan de volgende stap.'),
         ('Meterkast eerst', 'Wil je veel tegelijk, zoals panelen, een laadpaal en een warmtepomp? Dan is een goede meterkast de basis. We kijken vooraf wat er nodig is.')],
  faq=('Kan ik in Eindhoven een laadpaal en zonnepanelen tegelijk laten plaatsen?', 'Ja, en dat is vaak slim: we kijken dan in één keer naar je meterkast en je aansluiting. Met slim laden kun je je auto laden met je eigen zonnestroom.'),
  near=['Veldhoven', 'Best', 'Son en Breugel', 'Nuenen', 'Geldrop', 'Waalre'],
  buren=['tilburg', 's-hertogenbosch'],
  arts=['artikel-load-balancing-laadpaal', 'artikel-3-fase-aansluiting-aanvragen', 'artikel-capaciteitstarief-en-meterkast']),
 dict(slug='rotterdam', name='Rotterdam', region='Zuid-Holland', nb='Stedin', img='zonnepanelen-dak',
  intro='Rotterdam heeft van alles: jaren-30-woningen in Blijdorp en Kralingen, eengezinswoningen in de buitenwijken en veel appartementen met een plat dak. We installeren er zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen met ons eigen team en een vaste prijs vooraf.',
  local=[('Plat dak? Geen probleem', 'Op een plat dak plaatsen we de panelen op een frame, vaak in een oost-west-opstelling. Daardoor passen er meer panelen op het dak en is de opbrengst over de dag gelijkmatiger.'),
         ('Netbeheerder Stedin', 'In Rotterdam is Stedin de netbeheerder. Wij doen de aanmelding bij Stedin en regelen een zwaardere aansluiting als dat nodig is.'),
         ('Appartement of VvE', 'Woon je in een appartement? Voor panelen of een buitenunit op een gedeeld dak is toestemming van de VvE nodig. We helpen met de informatie die de VvE nodig heeft om te beslissen.'),
         ('Jaren-30-woningen', 'Oudere woningen zijn vaak minder goed geïsoleerd. Een hybride warmtepomp is dan meestal de slimste eerste stap. We rekenen eerlijk voor je door wat het oplevert.')],
  faq=('Kunnen jullie zonnepanelen op een plat dak in Rotterdam leggen?', 'Ja. Op platte daken plaatsen we de panelen op een frame, vaak oost-west. Hoeveel ballast of bevestiging er nodig is, hangt af van het dak. Dat bekijken we vooraf.'),
  near=['Capelle aan den IJssel', 'Schiedam', 'Vlaardingen', 'Barendrecht', 'Ridderkerk', 'Rhoon'],
  buren=['dordrecht', 'den-haag', 'utrecht', 'zevenbergen'],
  arts=['artikel-hybride-of-volledige-warmtepomp', 'artikel-hoeveel-zonnepanelen-nodig', 'artikel-thuisbatterij-na-salderen']),
 dict(slug='den-haag', name='Den Haag', region='Zuid-Holland', nb='Stedin', img='omvormers-afwerking',
  intro='In Den Haag installeren we zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen, van de binnenstad tot Scheveningen en Ypenburg. Met ons eigen team en een vaste prijs vooraf, en we houden rekening met wat er in jouw wijk wel en niet mag.',
  local=[('Beschermd stadsgezicht', 'Den Haag heeft relatief veel wijken met een beschermd stadsgezicht. Zijn de panelen daar vanaf de straat zichtbaar, dan is vaak een vergunning nodig. We checken het vooraf voor jouw adres.'),
         ('Netbeheerder Stedin', 'In Den Haag is Stedin de netbeheerder. De aanmelding en eventuele aanpassingen aan je aansluiting regelen wij rechtstreeks met Stedin.'),
         ('Dichtbij de kust', 'In de buurt van de zee kiezen we materialen en bevestigingen die tegen zilte lucht en harde wind kunnen, voor panelen én buitenunits.'),
         ('Airco in een bovenwoning', 'In een bovenwoning onder een plat dak kan het in de zomer erg warm worden. Een airco koelt snel en verwarmt in het voor- en najaar ook zuinig bij.')],
  faq=('Heb ik in Den Haag een vergunning nodig voor zonnepanelen?', 'Meestal niet, maar wel bij een monument of in een beschermd stadsgezicht als de panelen vanaf de straat zichtbaar zijn. Wij zoeken het voor jouw adres uit en regelen de aanvraag als dat nodig is.'),
  near=['Scheveningen', 'Ypenburg', 'Rijswijk', 'Voorburg', 'Leidschendam', 'Wassenaar', 'Delft'],
  buren=['rotterdam', 'utrecht'],
  arts=['artikel-airco-als-bijverwarming', 'artikel-zonnepanelen-prijs', 'artikel-salderingsregeling-2027']),
 dict(slug='utrecht', name='Utrecht', region='Utrecht', nb='Stedin', img='batterij-zolder',
  intro='In Utrecht, van de binnenstad tot Leidsche Rijn, installeren we zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen. Met ons eigen team en een vaste prijs vooraf.',
  local=[('Leidsche Rijn: vaak al elektrisch', 'Veel woningen in Leidsche Rijn zijn gebouwd zonder gas of hebben al een warmtepomp. Dan draait het vooral om meer zelf gebruiken: extra panelen, een thuisbatterij of een slimme boiler.'),
         ('Netbeheerder Stedin', 'In Utrecht is Stedin de netbeheerder. Wij regelen de aanmelding en, als dat nodig is, een zwaardere aansluiting.'),
         ('Beschermde binnenstad', 'De binnenstad van Utrecht is een beschermd stadsgezicht. Voor zonnepanelen die vanaf de straat zichtbaar zijn, is daar vaak een vergunning nodig. We zoeken het voor je uit.'),
         ('Batterij met een EMS', 'Een energiemanagementsysteem (EMS) stuurt je batterij, warmtepomp en laadpaal zo dat je zo veel mogelijk eigen stroom gebruikt.')],
  faq=('Loont een thuisbatterij in Utrecht als ik al een warmtepomp heb?', 'Vaak wel. Een warmtepomp verbruikt veel stroom, juist ook in de avond en in de winter. Met een batterij gebruik je meer van je eigen zonnestroom. Hoeveel het oplevert, rekenen we eerlijk voor je door.'),
  near=['Leidsche Rijn', 'Vleuten', 'De Meern', 'Nieuwegein', 'Houten', 'Zeist', 'Maarssen'],
  buren=['rotterdam', 'den-haag', 'amsterdam', 's-hertogenbosch'],
  arts=['artikel-ems-energiemanagementsysteem-thuisbatterij', 'artikel-thuisbatterij-hoe-groot', 'artikel-dynamisch-contract-en-batterij']),
 dict(slug='amsterdam', name='Amsterdam', region='Noord-Holland', nb='Liander', img='monteur-aan-het-werk',
  intro='Ook in Amsterdam zijn we actief met ons eigen installatieteam. Van een eengezinswoning in Noord of Nieuw-West tot een appartement op IJburg: we installeren zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen voor een vaste prijs vooraf.',
  local=[('Netbeheerder Liander', 'In Amsterdam is Liander de netbeheerder. Wij doen de aanmelding bij Liander en regelen een zwaardere aansluiting als dat nodig is.'),
         ('Monumenten en de grachtengordel', 'In de grachtengordel en bij monumenten gelden strenge regels voor wat er op het dak mag. We zoeken vooraf uit wat voor jouw pand kan, zodat je niet voor verrassingen komt te staan.'),
         ('Appartement of VvE', 'Veel Amsterdammers wonen in een appartement. Voor panelen op een gedeeld dak of een buitenunit aan de gevel is toestemming van de VvE nodig. We leveren de informatie die daarvoor nodig is.'),
         ('Laadpaal alleen op eigen terrein', 'Een laadpaal thuis kan alleen op eigen grond, zoals een oprit of garage. Heb je die niet, dan ben je aangewezen op een openbare laadpaal. Dat zeggen we je gewoon eerlijk.')],
  faq=('Kan ik in een Amsterdams appartement een thuisbatterij laten plaatsen?', 'Dat kan vaak wel, zolang er in de meterkast of bergruimte een veilige plek is en je aansluiting geschikt is. We kijken vooraf mee en zeggen eerlijk of het in jouw situatie loont.'),
  near=['Amstelveen', 'Diemen', 'Zaandam', 'Landsmeer', 'Ouder-Amstel', 'Purmerend'],
  buren=['utrecht', 'den-haag'],
  arts=['artikel-wat-doet-een-thuisbatterij', 'artikel-airco-als-bijverwarming', 'artikel-3-fase-aansluiting-aanvragen']),
]
ART.update({'artikel-thuisbatterij-hoe-groot': 'Hoe groot moet je thuisbatterij zijn?',
            'artikel-wat-doet-een-thuisbatterij': 'Wat doet een thuisbatterij?',
            'artikel-airco-als-bijverwarming': 'Airco als bijverwarming',
            'artikel-boiler-opwarmen-met-zonnestroom': 'Je boiler opwarmen met zonnestroom',
            'artikel-load-balancing-laadpaal': 'Load balancing bij je laadpaal'})
BY = {c['slug']: c for c in CITIES}
GROUPS = [('West-Brabant en Drechtsteden', ['zevenbergen', 'breda', 'etten-leur', 'roosendaal', 'bergen-op-zoom', 'oosterhout', 'dordrecht']),
          ('Rest van Brabant', ['tilburg', 's-hertogenbosch', 'eindhoven']),
          ('Randstad', ['rotterdam', 'den-haag', 'utrecht', 'amsterdam'])]

CSS = '''<style>
.lp-hero{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:48px;align-items:center;}
.lp-hero .img{border-radius:22px;overflow:hidden;aspect-ratio:4/3;background:var(--bg);}
.lp-hero .img img{width:100%;height:100%;object-fit:cover;display:block;}
.lp-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:40px;}
.lp-stat{background:#fff;border:1px solid var(--border);border-radius:16px;padding:16px 18px;}
.lp-stat b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:20px;color:var(--ink);}
.lp-stat span{font-size:13px;color:var(--ink-soft);}
.lp-h2{font-size:clamp(24px,3vw,30px);line-height:1.25;}
.lp-prod{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px;margin-top:22px;}
.lp-prod a{display:flex;align-items:center;gap:12px;padding:12px;border-radius:16px;background:#fff;border:1px solid var(--border);text-decoration:none;color:var(--ink);transition:border-color .2s,transform .2s;}
.lp-prod a:hover{border-color:var(--primary);transform:translateY(-2px);}
.lp-prod img{width:56px;height:56px;border-radius:10px;object-fit:cover;flex-shrink:0;background:var(--bg);}
.lp-prod b{display:block;font-size:14.5px;} .lp-prod span{font-size:13px;color:var(--primary);font-weight:700;}
.lp-local{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:22px;}
.lp-local div{background:#fff;border:1px solid var(--border);border-radius:18px;padding:20px 22px;}
.lp-local h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:17px;margin:0 0 8px;color:var(--ink);}
.lp-local p{font-size:14.5px;line-height:1.65;color:var(--ink-soft);}
.lp-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:22px;}
.lp-steps div{display:flex;gap:14px;align-items:flex-start;}
.lp-steps p{font-size:14.5px;line-height:1.6;color:var(--ink-soft);} .lp-steps b{display:block;color:var(--ink);margin-bottom:4px;}
.lp-near{font-size:14.5px;line-height:1.7;color:var(--ink-soft);}
.lp-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;}
.lp-chips a{padding:8px 14px;border-radius:999px;border:1px solid var(--border);background:#fff;color:var(--ink);font-weight:700;font-size:13.5px;text-decoration:none;}
.lp-chips a:hover{border-color:var(--primary);color:var(--primary);}
.lp-arts a{display:block;padding:14px 0;border-top:1px solid var(--border);color:var(--ink);font-weight:700;text-decoration:none;font-size:15px;}
.lp-arts a:hover{color:var(--primary);} .lp-arts a:last-child{border-bottom:1px solid var(--border);}
.lp-cta{background:var(--dark);color:#fff;border-radius:24px;padding:36px;display:flex;gap:24px;align-items:center;justify-content:space-between;flex-wrap:wrap;}
.lp-cta p{color:var(--dark-text-muted);margin-top:8px;font-size:15px;}
.lp-sec{padding-top:56px;}
.lp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin-top:18px;}
.lp-grid a{display:block;padding:18px 20px;border-radius:16px;background:#fff;border:1px solid var(--border);text-decoration:none;color:var(--ink);transition:border-color .2s,transform .2s;}
.lp-grid a:hover{border-color:var(--primary);transform:translateY(-2px);}
.lp-grid b{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:18px;display:block;} .lp-grid span{font-size:13px;color:var(--ink-soft);}
@media (max-width:900px){.lp-hero{grid-template-columns:1fr;gap:28px;}.lp-stats{grid-template-columns:repeat(2,minmax(0,1fr));}.lp-steps{grid-template-columns:1fr;}}
@media (max-width:640px){.lp-local{grid-template-columns:1fr;}.lp-cta{padding:26px 22px;}}
</style>'''

def crumbs(items):
    out = []
    for i, (label, href) in enumerate(items):
        if i: out.append('<span aria-hidden="true">/</span>')
        out.append(f'<a href="{href}" style="color:var(--primary);text-decoration:none;">{esc(label)}</a>' if href else f'<span>{esc(label)}</span>')
    return '<nav aria-label="Kruimelpad" style="font-size:13px;font-weight:700;color:var(--ink-faint);display:flex;gap:8px;flex-wrap:wrap;align-items:center;">' + ''.join(out) + '</nav>'

STATS = '''<div class="lp-stats">
      <div class="lp-stat"><b>12.500+</b><span>installaties uitgevoerd</span></div>
      <div class="lp-stat"><b>4,7 / 5</b><span>gemiddeld op Google</span></div>
      <div class="lp-stat"><b>Eigen monteurs</b><span>geen onderaannemers</span></div>
      <div class="lp-stat"><b>Vaste prijs</b><span>vooraf, geen verrassingen</span></div>
    </div>'''
WA = 'https://wa.me/31853335687?text='

def cta(title, sub):
    return f'''<div class="wrap reveal lp-sec" style="max-width:1000px;padding-bottom:80px;"><div class="lp-cta">
      <div><div class="vw-heading" style="font-size:clamp(22px,2.6vw,28px);color:#fff;">{esc(title)}</div><p>{esc(sub)}</p></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;"><a href="/bereken-je-prijs" class="btn-primary" style="background:var(--mint);color:var(--dark);text-decoration:none;">Bereken je prijs →</a><a href="/contact" class="btn-secondary" style="border-color:#fff;color:#fff;text-decoration:none;">Neem contact op</a></div>
    </div></div>'''

def city_faq(c):
    n, nb = c['name'], c['nb']
    qa = [c['faq'],
          (f'Wat kost de installatie in {n}?', f'Je betaalt in {n} een vaste prijs die je vooraf kent: zonnepanelen vanaf € 3.999, een thuisbatterij vanaf € 3.499 en een warmtepomp vanaf € 6.750, inclusief installatie. Met de prijscalculator zie je binnen een minuut de prijs voor jouw woning.'),
          (f'Wie regelt de netbeheerder en de vergunning in {n}?', f'Dat doen wij. In {n} is {NB[nb]} de netbeheerder (het precieze adres is bepalend). Wij regelen de aanmelding, een eventuele verzwaring van je aansluiting, een vergunning als die nodig is en bij een warmtepomp de ISDE-subsidie.'),
          (f'Werken jullie in {n} met onderaannemers?', 'Nee. Alle installaties doen we met onze eigen monteurs. Daardoor weten we zeker dat het werk goed is en heb je één aanspreekpunt, ook na de installatie.'),
          ('Hoe snel kan de installatie plaatsvinden?', 'De meeste klanten hebben binnen 2 tot 3 weken na de offerte een geplande installatiedatum. Bij de prijscheck zie je een indicatie voor jouw adres.')]
    return qa

def city_main(c):
    n = c['name']
    local = ''.join(f'<div><h3>{esc(h)}</h3><p>{inline(t)}</p></div>' for h, t in c['local'])
    prods = ''.join(f'<a href="{u}"><img loading="lazy" decoding="async" src="/images/{im}.webp" alt="{esc(p)}"><div><b>{esc(p)}</b><span>{esc(pr)}</span></div></a>' for p, pr, u, im in PRODUCTS)
    arts = ''.join(f'<a href="/{a}">{esc(ART[a])} →</a>' for a in c['arts'] if os.path.exists(a + '.html'))
    faq = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in city_faq(c))
    buren = ''.join(f'<a href="/installateur-{b}">{esc(BY[b]["name"])}</a>' for b in c['buren'])
    near = ', '.join(c['near'][:-1]) + ' en ' + c['near'][-1]
    wa = WA + urllib.parse.quote(f'Hoi Voltwijk, ik woon in {n} en heb een vraag')
    return f'''<div class="blk-light" style="padding-top:40px;">
  {CSS}
  <div class="wrap reveal" style="max-width:1000px;padding-top:48px;">
    {crumbs([('Werkgebied', '/werkgebied'), (n, None)])}
    <div class="lp-hero" style="margin-top:18px;">
      <div>
        <div class="pill">Werkgebied · {esc(c['region'])}</div>
        <h1 class="vw-heading" style="font-size:clamp(30px,4.6vw,44px);margin-top:14px;line-height:1.15;">Zonnepanelen, thuisbatterij en warmtepomp in {esc(n)}</h1>
        <p style="font-size:17px;color:var(--ink-soft);margin-top:16px;line-height:1.65;">{esc(c['intro'])}</p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:24px;"><a href="/bereken-je-prijs" class="btn-primary" style="text-decoration:none;">Bereken je prijs →</a><a href="{wa}" target="_blank" rel="noopener" class="btn-secondary" style="text-decoration:none;">Stuur een appje</a></div>
      </div>
      <div class="img"><img fetchpriority="high" src="/images/{c['img']}.webp" alt="Installatie door een Voltwijk-monteur" width="800" height="600"></div>
    </div>
    {STATS}
  </div>
  <div class="wrap reveal lp-sec" style="max-width:1000px;">
    <h2 class="vw-heading lp-h2">Wat we in {esc(n)} installeren</h2>
    <p style="font-size:15.5px;color:var(--ink-soft);margin-top:10px;line-height:1.6;max-width:680px;">Vaste prijzen vooraf, inclusief installatie door ons eigen team.</p>
    <div class="lp-prod">{prods}</div>
  </div>
  <div class="wrap reveal lp-sec" style="max-width:1000px;">
    <h2 class="vw-heading lp-h2">Goed om te weten in {esc(n)}</h2>
    <div class="lp-local">{local}</div>
  </div>
  <div class="wrap reveal lp-sec" style="max-width:1000px;">
    <h2 class="vw-heading lp-h2">Zo gaat het</h2>
    <div class="lp-steps">
      <div><div class="step-num">1</div><p><b>Bereken je prijs</b>Vul je postcode en woningtype in en zie binnen een minuut je vaste prijs.</p></div>
      <div><div class="step-num">2</div><p><b>Wij regelen de rest</b>Netbeheerder, vergunning en subsidie: wij nemen het papierwerk van je over.</p></div>
      <div><div class="step-num">3</div><p><b>Installatie door ons eigen team</b>Meestal binnen 2 tot 3 weken na de offerte ingepland. Je betaalt pas als alles naar wens werkt.</p></div>
    </div>
  </div>
  <div class="wrap reveal lp-sec" style="max-width:1000px;">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:40px;">
      <div>
        <h2 class="vw-heading lp-h2">Veelgestelde vragen over {esc(n)}</h2>
        <div class="faq" style="margin-top:18px;">{faq}</div>
      </div>
      <div>
        <h2 class="vw-heading lp-h2" style="font-size:22px;">Handig om te lezen</h2>
        <div class="lp-arts" style="margin-top:14px;">{arts}</div>
        <h2 class="vw-heading lp-h2" style="font-size:22px;margin-top:36px;">Ook in de buurt</h2>
        <p class="lp-near" style="margin-top:10px;">We installeren ook in {esc(near)}.</p>
        <div class="lp-chips">{buren}<a href="/werkgebied">Alle plaatsen →</a></div>
      </div>
    </div>
  </div>
  {cta(f'Benieuwd wat het in {n} kost?', 'Bereken binnen een minuut je vaste prijs. Liever eerst persoonlijk advies? Ons eigen team denkt graag met je mee.')}
</div>
'''

def overview_main():
    groups = ''
    for label, slugs in GROUPS:
        cards = ''.join(f'<a href="/installateur-{s}"><b>{esc(BY[s]["name"])}</b><span>Netbeheerder: {esc(NB[BY[s]["nb"]])}</span></a>' for s in slugs)
        groups += f'<h2 class="vw-heading lp-h2" style="font-size:22px;margin-top:40px;">{esc(label)}</h2><div class="lp-grid">{cards}</div>'
    return f'''<div class="blk-light" style="padding-top:40px;">
  {CSS}
  <div class="wrap reveal" style="max-width:1000px;padding-top:48px;">
    <div class="pill">Werkgebied</div>
    <h1 class="vw-heading" style="font-size:clamp(30px,4.6vw,44px);margin-top:14px;line-height:1.15;">Actief in heel Nederland, met een eigen team</h1>
    <p style="font-size:17px;color:var(--ink-soft);margin-top:16px;line-height:1.65;max-width:700px;">Ons kantoor zit in Zevenbergen, in West-Brabant. Van daaruit installeren we in heel Nederland zonnepanelen, thuisbatterijen, warmtepompen, airco's, boilers en laadpalen. Altijd met een vaste prijs vooraf.</p>
    {STATS}
  </div>
  <div class="wrap reveal lp-sec" style="max-width:1000px;padding-top:24px;">
    {groups}
    <p style="font-size:15px;color:var(--ink-soft);margin-top:32px;line-height:1.6;">Staat jouw plaats er niet tussen? Geen probleem: we komen in heel Nederland. Vul je postcode in bij de <a href="/bereken-je-prijs" style="color:var(--primary);font-weight:700;">prijscalculator</a> en je ziet direct je prijs.</p>
  </div>
  {cta('Zie direct wat het bij jou kost', 'Vul je postcode en woningtype in en zie binnen een minuut je vaste prijs, inclusief installatie.')}
</div>
'''

def page(shell, main, slug, title, desc):
    s = re.sub(r'<div class="blk-light" style="padding-top:40px;">.*?(?=<div class="site-footer")', lambda m: main + '\n\n', shell, count=1, flags=re.S)
    s = re.sub(r'<title>.*?</title>', '<title>' + esc(title) + '</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + esc(desc) + '">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://voltwijk.nl/{slug}">', s, count=1)
    s = re.sub(r'\n?<!-- seo:start -->.*?<!-- seo:end -->', '', s, flags=re.S)
    s = re.sub(r'\n?<!-- rel:start -->.*?<!-- rel:end -->', '', s, flags=re.S)
    return s

FOOT_CITIES = ['zevenbergen', 'breda', 'dordrecht', 'rotterdam', 'tilburg', 'eindhoven']
def footer_col():
    links = ''.join(f'\n          <a href="/installateur-{s}" style="color:inherit;text-decoration:none;">{esc(BY[s]["name"])}</a>' for s in FOOT_CITIES)
    return ('<!-- wg:start --><div style="font-size:13px;color:#C9D6D3;display:flex;flex-direction:column;gap:10px;">\n'
            '          <div style="color:var(--mint);font-weight:700;font-size:12px;">WERKGEBIED</div>' + links +
            '\n          <a href="/werkgebied" style="color:inherit;text-decoration:none;">Alle plaatsen →</a>\n        </div><!-- wg:end -->')

def main():
    shell = open(SHELL, encoding='utf-8').read()
    for c in CITIES:
        n = c['name']
        title = f'Thuisbatterij, zonnepanelen & warmtepomp {n} | Voltwijk'
        desc = f'Thuisbatterij, zonnepanelen of warmtepomp in {n}? Vaste prijs vooraf, eigen monteurs, 12.500+ installaties, 4,7/5 op Google.'
        assert len(desc) <= 160, desc
        open(f'installateur-{c["slug"]}.html', 'w', encoding='utf-8').write(page(shell, city_main(c), f'installateur-{c["slug"]}', title, desc))
    open('werkgebied.html', 'w', encoding='utf-8').write(page(shell, overview_main(), 'werkgebied',
        'Werkgebied: installateur in heel Nederland | Voltwijk',
        'Voltwijk installeert zonnepanelen, thuisbatterijen, warmtepompen en laadpalen in heel Nederland, vanuit Zevenbergen. Bekijk je plaats en bereken je vaste prijs.'))
    # footer-kolom op alle pagina's
    col = footer_col(); n = 0
    for f in sorted(os.listdir('.')):
        if not f.endswith('.html'): continue
        s = open(f, encoding='utf-8').read()
        s2 = re.sub(r'<!-- wg:start -->.*?<!-- wg:end -->', lambda m: col, s, flags=re.S)
        if s2 == s and '<!-- wg:start -->' not in s:
            s2 = re.sub(r'(<a href="/contact" style="color:inherit;text-decoration:none;">Contact</a>\s*</div>)', lambda m: m.group(1) + '\n        ' + col, s, count=1)
        if s2 != s: open(f, 'w', encoding='utf-8').write(s2); n += 1
    print(len(CITIES), 'plaatsen + werkgebied; footer bijgewerkt op', n, 'pagina\'s')

main()
