# Bouwt lokale landingspagina's (installateur-<plaats>.html), het overzicht /werkgebied en de
# WERKGEBIED-kolom in de footer van alle pagina's. Veilig om opnieuw te draaien.
# Daarna altijd: python3 tools/seo.py  (titels/OG/JSON-LD/sitemap)
# Let op: alleen controleerbare feiten per plaats. Netbeheerder hangt af van het exacte adres,
# dat staat ook zo op de pagina's.
import re, html, os, sys, urllib.parse
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.dont_write_bytecode = True
from battery import PAKKETTEN, VANAF, eur  # de drie batterijpakketten (één bron: tools/battery.py)
SHELL = 'artikel-isde-subsidie-2026.html'
esc = lambda s: html.escape(s, quote=True)
def inline(t):
    t = esc(t).replace('&#x27;', "'")
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    return re.sub(r'\[([^\]]+)\]\((/[^)\s]*)\)', r'<a href="\2">\1</a>', t)

PRODUCTS = [
 ('Zonnepanelen', 'vanaf € 3.999', '/product-zonnepanelen', 'thumb-zonnepanelen'),
 ('Thuisbatterij', 'vanaf € 4.200 excl. btw', '/product-batterij', 'thumb-batterij'),
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
  intro='Zevenbergen is onze thuisbasis: ons kantoor zit aan de Schoenmakerij. Vanuit hier installeren we zonnepanelen, thuisbatterijen, warmtepompen en laadpalen in de hele gemeente Moerdijk en omgeving, altijd met ons eigen team en een vaste prijs vooraf.',
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
  faq=('Hoe snel kunnen jullie in Etten-Leur installeren?', 'Na de offerte plannen we samen een installatiedatum. Etten-Leur ligt dicht bij ons kantoor in Zevenbergen, dus ook voor een vraag achteraf of service na de installatie zijn we dichtbij.'),
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
         ('ISDE-subsidie', 'Voor een warmtepomp kun je ISDE-subsidie krijgen. We helpen je met de aanvraag; die doe je na de installatie bij RVO.'),
         ('Boiler op zonnestroom', 'Heb je zonnepanelen? Dan kun je een elektrische boiler overdag laten opwarmen met je eigen stroom. Na 2027 is dat extra interessant.')],
  faq=('Helpen jullie met de ISDE-subsidie voor mijn warmtepomp in Oosterhout?', 'Ja. We helpen je met de ISDE-aanvraag. Die doe je na de installatie bij RVO; wij zorgen dat je de gegevens over je warmtepomp en de installatie bij de hand hebt.'),
  near=['Dorst', 'Den Hout', 'Oosteind', 'Dongen', 'Made', 'Raamsdonksveer'],
  buren=['breda', 'zevenbergen', 'tilburg', 'dordrecht'],
  arts=['artikel-isde-subsidie-2026', 'artikel-is-mijn-huis-geschikt-voor-een-warmtepomp', 'artikel-boiler-opwarmen-met-zonnestroom']),
 dict(slug='dordrecht', name='Dordrecht', region='Drechtsteden', nb='Stedin', img='monteur-en-klant',
  intro='Dordrecht, de oudste stad van Holland, is vanuit Zevenbergen dichtbij. Van een monument in de binnenstad tot een eengezinswoning in Stadspolders of Sterrenburg: we installeren er zonnepanelen, thuisbatterijen, warmtepompen en laadpalen met ons eigen team. Vraag gerust of we bij jou kunnen installeren.',
  local=[('Netbeheerder Stedin', 'In Dordrecht is Stedin de netbeheerder, niet Enexis zoals in Brabant. Voor jou verandert er niets: wij regelen de aanmelding en een eventuele verzwaring bij Stedin.'),
         ('Monumenten in de binnenstad', 'De historische binnenstad heeft veel monumenten. Daar is voor zonnepanelen of een buitenunit vaak een vergunning nodig. We zoeken vooraf uit wat voor jouw pand geldt.'),
         ('Vanuit Zevenbergen', 'Ons kantoor zit in Zevenbergen, en vanuit daar komen we ook naar Dordrecht en de plaatsen eromheen. Laat ons weten waar je woont, dan hoor je of we bij jou kunnen installeren.'),
         ('Meer zelf gebruiken', 'Met een thuisbatterij en een energiemanagementsysteem (EMS) gebruik je meer van je eigen zonnestroom. Dat wordt belangrijker nu het salderen in 2027 stopt.')],
  faq=('Wie is de netbeheerder in Dordrecht?', 'In Dordrecht is Stedin de netbeheerder voor stroom. Wij regelen de aanmelding van je zonnepanelen of thuisbatterij en eventuele aanpassingen aan je aansluiting rechtstreeks met Stedin.'),
  near=['Zwijndrecht', 'Papendrecht', 'Sliedrecht', 'Hendrik-Ido-Ambacht', 'Alblasserdam', '\'s-Gravendeel'],
  buren=['zevenbergen', 'rotterdam', 'breda', 'oosterhout'],
  arts=['artikel-ems-energiemanagementsysteem-thuisbatterij', 'artikel-thuisbatterij-na-salderen', 'artikel-salderingsregeling-2027']),
 dict(slug='tilburg', name='Tilburg', region='Midden-Brabant', nb='Enexis', img='batterij-installatie',
  intro='Vanuit Zevenbergen komen we ook naar Tilburg, van de Reeshof tot het centrum. We installeren er zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen, met ons eigen team en een vaste prijs vooraf. Vraag gerust of we bij jou kunnen installeren.',
  local=[('Netbeheerder Enexis', 'In Tilburg is Enexis de netbeheerder. Wij melden je installatie aan en vragen een zwaardere aansluiting aan als je warmtepomp of laadpaal dat nodig heeft.'),
         ('Woningen uit de jaren \'80 en \'90', 'Wijken als de Reeshof zijn grotendeels gebouwd vanaf de jaren \'80. Die woningen zijn vaak redelijk geïsoleerd en daardoor geschikt voor een hybride warmtepomp, of met extra maatregelen voor een volledige.'),
         ('Thuisbatterij met dynamisch contract', 'Met een dynamisch energiecontract laad je je batterij op als stroom goedkoop is en gebruik je hem als stroom duur is. We leggen eerlijk uit wanneer dat loont.'),
         ('Laadpaal thuis', 'Een slimme 11 kW laadpaal laadt de meeste elektrische auto\'s in een nacht vol. Met slim laden gebruik je de goedkoopste uren.')],
  faq=('Hoeveel kost een thuisbatterij in Tilburg?', 'Een thuisbatterij kost bij ons vanaf € 4.200 excl. btw, inclusief installatie. Met de batterijcalculator zie je binnen een minuut welke batterij bij jouw woning past en wat hij kost.'),
  near=['Berkel-Enschot', 'Udenhout', 'Goirle', 'Oisterwijk', 'Hilvarenbeek', 'Dongen'],
  buren=['breda', 'oosterhout', 's-hertogenbosch', 'eindhoven'],
  arts=['artikel-dynamisch-contract-en-batterij', 'artikel-hybride-of-volledige-warmtepomp', 'artikel-laadpaal-slim-laden']),
 dict(slug='s-hertogenbosch', name='\'s-Hertogenbosch', region='Noordoost-Brabant', nb='Enexis', img='warmtepomp-installatie',
  intro='Vanuit Zevenbergen komen we ook naar \'s-Hertogenbosch, van de historische binnenstad tot nieuwbouw in De Groote Wielen. We installeren er zonnepanelen, thuisbatterijen, warmtepompen en laadpalen, met ons eigen team en een vaste prijs die je vooraf al kent. Vraag gerust of we bij jou kunnen installeren.',
  local=[('Beschermde binnenstad', 'Voor een huis in de binnenstad of een monument is voor zonnepanelen of een buitenunit vaak een vergunning nodig. We zoeken uit wat voor jouw adres geldt en regelen de aanvraag.'),
         ('Netbeheerder Enexis', 'In \'s-Hertogenbosch is Enexis de netbeheerder. De aanmelding en eventuele aanpassingen aan je aansluiting regelen wij.'),
         ('Nieuwbouw: vaak al all-electric', 'Nieuwere woningen, zoals in De Groote Wielen, hebben vaak al een warmtepomp. Dan liggen zonnepanelen uitbreiden of een thuisbatterij meer voor de hand. We kijken wat jouw installatie al kan.'),
         ('Stil buiten', 'Een buitenunit moet binnen de geluidsnorm op de erfgrens blijven. We kiezen een stille unit en een plek waar ook je buren er geen last van hebben.')],
  faq=('Installeren jullie ook in Rosmalen en Vught?', 'Vraag het ons gerust. Vanuit Zevenbergen komen we ook naar \'s-Hertogenbosch en plaatsen eromheen, zoals Rosmalen, Vught, Vlijmen en Berlicum. Laat ons weten waar je woont, dan hoor je of we bij jou kunnen installeren.'),
  near=['Rosmalen', 'Vught', 'Vlijmen', 'Berlicum', 'Sint-Michielsgestel', 'Den Dungen'],
  buren=['tilburg', 'eindhoven', 'utrecht'],
  arts=['artikel-warmtepomp-geluid', 'artikel-ems-energiemanagementsysteem-thuisbatterij', 'artikel-isde-subsidie-2026']),
 dict(slug='eindhoven', name='Eindhoven', region='Zuidoost-Brabant', nb='Enexis', img='laadpaal-installatie',
  intro='Vanuit Zevenbergen komen we ook naar Eindhoven. We installeren er zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen, met ons eigen team en een vaste prijs vooraf, zonder onderaannemers. Vraag gerust of we bij jou kunnen installeren.',
  local=[('Netbeheerder Enexis', 'In Eindhoven is Enexis de netbeheerder. Wij regelen de aanmelding van je installatie en een 3-fase-aansluiting als dat nodig is.'),
         ('Elektrisch rijden', 'Rijd je elektrisch en heb je een eigen oprit? Een slimme laadpaal met load balancing laadt veilig en goedkoop, ook als er thuis tegelijk veel aanstaat.'),
         ('Nieuwbouw in Meerhoven en omgeving', 'In nieuwere wijken is de meterkast vaak al ruim en hangt er soms al een warmtepomp. Zonnepanelen en een thuisbatterij zijn dan de volgende stap.'),
         ('Meterkast eerst', 'Wil je veel tegelijk, zoals panelen, een laadpaal en een warmtepomp? Dan is een goede meterkast de basis. We kijken vooraf wat er nodig is.')],
  faq=('Kan ik in Eindhoven een laadpaal en zonnepanelen tegelijk laten plaatsen?', 'Ja, en dat is vaak slim: we kijken dan in één keer naar je meterkast en je aansluiting. Met slim laden kun je je auto laden met je eigen zonnestroom.'),
  near=['Veldhoven', 'Best', 'Son en Breugel', 'Nuenen', 'Geldrop', 'Waalre'],
  buren=['tilburg', 's-hertogenbosch'],
  arts=['artikel-load-balancing-laadpaal', 'artikel-3-fase-aansluiting-aanvragen', 'artikel-capaciteitstarief-en-meterkast']),
 dict(slug='rotterdam', name='Rotterdam', region='Zuid-Holland', nb='Stedin', img='zonnepanelen-dak',
  intro='Rotterdam heeft van alles: jaren-30-woningen in Blijdorp en Kralingen, eengezinswoningen in de buitenwijken en veel appartementen met een plat dak. Vanuit Zevenbergen komen we ook naar Rotterdam; vraag gerust of we bij jou kunnen installeren. We installeren er zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen met ons eigen team en een vaste prijs vooraf.',
  local=[('Plat dak? Geen probleem', 'Op een plat dak plaatsen we de panelen op een frame, vaak in een oost-west-opstelling. Daardoor passen er meer panelen op het dak en is de opbrengst over de dag gelijkmatiger.'),
         ('Netbeheerder Stedin', 'In Rotterdam is Stedin de netbeheerder. Wij doen de aanmelding bij Stedin en regelen een zwaardere aansluiting als dat nodig is.'),
         ('Appartement of VvE', 'Woon je in een appartement? Voor panelen of een buitenunit op een gedeeld dak is toestemming van de VvE nodig. We helpen met de informatie die de VvE nodig heeft om te beslissen.'),
         ('Jaren-30-woningen', 'Oudere woningen zijn vaak minder goed geïsoleerd. Een hybride warmtepomp is dan meestal de slimste eerste stap. We rekenen eerlijk voor je door wat het oplevert.')],
  faq=('Kunnen jullie zonnepanelen op een plat dak in Rotterdam leggen?', 'Ja. Op platte daken plaatsen we de panelen op een frame, vaak oost-west. Hoeveel ballast of bevestiging er nodig is, hangt af van het dak. Dat bekijken we vooraf.'),
  near=['Capelle aan den IJssel', 'Schiedam', 'Vlaardingen', 'Barendrecht', 'Ridderkerk', 'Rhoon'],
  buren=['dordrecht', 'den-haag', 'utrecht', 'zevenbergen'],
  arts=['artikel-hybride-of-volledige-warmtepomp', 'artikel-hoeveel-zonnepanelen-nodig', 'artikel-thuisbatterij-na-salderen']),
 dict(slug='den-haag', name='Den Haag', region='Zuid-Holland', nb='Stedin', img='omvormers-afwerking',
  intro='Vanuit Zevenbergen komen we ook naar Den Haag; vraag gerust of we bij jou kunnen installeren. We installeren er zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen, met ons eigen team en een vaste prijs vooraf, en we houden rekening met wat er in jouw wijk wel en niet mag.',
  local=[('Beschermd stadsgezicht', 'Den Haag heeft relatief veel wijken met een beschermd stadsgezicht. Zijn de panelen daar vanaf de straat zichtbaar, dan is vaak een vergunning nodig. We checken het vooraf voor jouw adres.'),
         ('Netbeheerder Stedin', 'In Den Haag is Stedin de netbeheerder. De aanmelding en eventuele aanpassingen aan je aansluiting regelen wij rechtstreeks met Stedin.'),
         ('Dichtbij de kust', 'In de buurt van de zee kiezen we materialen en bevestigingen die tegen zilte lucht en harde wind kunnen, voor panelen én buitenunits.'),
         ('Airco in een bovenwoning', 'In een bovenwoning onder een plat dak kan het in de zomer erg warm worden. Een airco koelt snel en verwarmt in het voor- en najaar ook zuinig bij.')],
  faq=('Heb ik in Den Haag een vergunning nodig voor zonnepanelen?', 'Meestal niet, maar wel bij een monument of in een beschermd stadsgezicht als de panelen vanaf de straat zichtbaar zijn. Wij zoeken het voor jouw adres uit en regelen de aanvraag als dat nodig is.'),
  near=['Scheveningen', 'Ypenburg', 'Rijswijk', 'Voorburg', 'Leidschendam', 'Wassenaar', 'Delft'],
  buren=['rotterdam', 'utrecht'],
  arts=['artikel-airco-als-bijverwarming', 'artikel-zonnepanelen-prijs', 'artikel-salderingsregeling-2027']),
 dict(slug='utrecht', name='Utrecht', region='Utrecht', nb='Stedin', img='batterij-zolder',
  intro='Vanuit Zevenbergen komen we ook naar Utrecht, van de binnenstad tot Leidsche Rijn. We installeren er zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen, met ons eigen team en een vaste prijs vooraf. Vraag gerust of we bij jou kunnen installeren.',
  local=[('Leidsche Rijn: vaak al elektrisch', 'Veel woningen in Leidsche Rijn hebben stadsverwarming of zijn gasloos gebouwd. Dan draait het vooral om meer zelf gebruiken: extra panelen, een thuisbatterij of een slimme boiler.'),
         ('Netbeheerder Stedin', 'In Utrecht is Stedin de netbeheerder. Wij regelen de aanmelding en, als dat nodig is, een zwaardere aansluiting.'),
         ('Beschermde binnenstad', 'De binnenstad van Utrecht is een beschermd stadsgezicht. Voor zonnepanelen die vanaf de straat zichtbaar zijn, is daar vaak een vergunning nodig. We zoeken het voor je uit.'),
         ('Batterij met een EMS', 'Een energiemanagementsysteem (EMS) stuurt je batterij, warmtepomp en laadpaal zo dat je zo veel mogelijk eigen stroom gebruikt.')],
  faq=('Loont een thuisbatterij in Utrecht als ik al een warmtepomp heb?', 'Vaak wel. Een warmtepomp verbruikt veel stroom, juist ook in de avond en in de winter. Met een batterij gebruik je meer van je eigen zonnestroom. Hoeveel het oplevert, rekenen we eerlijk voor je door.'),
  near=['Leidsche Rijn', 'Vleuten', 'De Meern', 'Nieuwegein', 'Houten', 'Zeist', 'Maarssen'],
  buren=['rotterdam', 'den-haag', 'amsterdam', 's-hertogenbosch'],
  arts=['artikel-ems-energiemanagementsysteem-thuisbatterij', 'artikel-thuisbatterij-hoe-groot', 'artikel-dynamisch-contract-en-batterij']),
 dict(slug='amsterdam', name='Amsterdam', region='Noord-Holland', nb='Liander', img='monteur-aan-het-werk',
  intro='Vanuit Zevenbergen komen we ook naar Amsterdam; vraag gerust of we bij jou kunnen installeren. Van een eengezinswoning in Noord of Nieuw-West tot een appartement op IJburg: we installeren zonnepanelen, thuisbatterijen, warmtepompen, airco\'s en laadpalen voor een vaste prijs vooraf.',
  local=[('Netbeheerder Liander', 'In Amsterdam is Liander de netbeheerder. Wij doen de aanmelding bij Liander en regelen een zwaardere aansluiting als dat nodig is.'),
         ('Monumenten en de grachtengordel', 'In de grachtengordel en bij monumenten gelden strenge regels voor wat er op het dak mag. We zoeken vooraf uit wat voor jouw pand kan, zodat je niet voor verrassingen komt te staan.'),
         ('Appartement of VvE', 'Veel Amsterdammers wonen in een appartement. Voor panelen op een gedeeld dak of een buitenunit aan de gevel is toestemming van de VvE nodig. We leveren de informatie die daarvoor nodig is.'),
         ('Laadpaal alleen op eigen terrein', 'Een laadpaal thuis kan alleen op eigen grond, zoals een oprit of garage. Heb je die niet, dan ben je aangewezen op een openbare laadpaal. Dat zeggen we je gewoon eerlijk.')],
  faq=('Kan ik in een Amsterdams appartement een thuisbatterij laten plaatsen?', 'Dat kan vaak wel, zolang er een veilige, droge plek is, bijvoorbeeld een bergruimte, en je aansluiting geschikt is. We kijken vooraf mee en zeggen eerlijk of het in jouw situatie loont.'),
  near=['Amstelveen', 'Diemen', 'Zaandam', 'Landsmeer', 'Ouder-Amstel', 'Purmerend'],
  buren=['utrecht', 'den-haag'],
  arts=['artikel-wat-doet-een-thuisbatterij', 'artikel-airco-als-bijverwarming', 'artikel-3-fase-aansluiting-aanvragen']),
]
ART.update({'artikel-thuisbatterij-hoe-groot': 'Hoe groot moet je thuisbatterij zijn?',
            'artikel-wat-doet-een-thuisbatterij': 'Wat doet een thuisbatterij?',
            'artikel-airco-als-bijverwarming': 'Airco als bijverwarming',
            'artikel-boiler-opwarmen-met-zonnestroom': 'Je boiler opwarmen met zonnestroom',
            'artikel-load-balancing-laadpaal': 'Load balancing bij je laadpaal'})
ART.update({'artikel-thuisbatterij-plaatsen-waar': 'Waar plaats je een thuisbatterij?',
            'artikel-thuisbatterij-zonder-zonnepanelen': 'Thuisbatterij zonder zonnepanelen',
            'artikel-thuisbatterij-bij-bestaande-zonnepanelen': 'Thuisbatterij bij bestaande zonnepanelen',
            'artikel-thuisbatterij-1-fase-aansluiting': 'Thuisbatterij op een 1-fase aansluiting',
            'artikel-thuisbatterij-terugverdientijd': 'Terugverdientijd van een thuisbatterij',
            'artikel-airco-plaatsen-regels-vergunning': 'Airco plaatsen: heb je een vergunning nodig?',
            'artikel-checklist-salderen-2027': 'Checklist salderen 2027',
            'artikel-zonnepanelen-oost-west-of-zuid': 'Zonnepanelen oost-west of zuid?',
            'artikel-groepen-bijplaatsen-meterkast': 'Groepen bijplaatsen in je meterkast',
            'artikel-terugleverkosten-uitgelegd': 'Terugleverkosten uitgelegd',
            'artikel-zonnepanelen-rendabel-na-2027': 'Zijn zonnepanelen nog rendabel na 2027?',
            'artikel-warmtepomp-en-zonnepanelen-combineren': 'Warmtepomp en zonnepanelen combineren',
            'artikel-meterkast-onderschatte-stap': 'Meterkast: de vergeten stap bij batterij en laadpaal'})

# Kernen in West-Brabant rond Zevenbergen. Feiten nagezocht in september 2026 (o.a. erfgoedregister en
# beleidsregel zonnepanelen van de gemeente Moerdijk, rijksmonumentenregister, sites van de gemeenten).
# Bewust weggelaten: afstanden, rijtijden, inwonertallen en alles wat niet goed te controleren was.
CITIES += [
 dict(slug='klundert', name='Klundert', region='West-Brabant', nb='Enexis', img='thuisbatterij-bijkeuken', gemeente='Moerdijk',
  intro='Klundert is een oud vestingstadje in de gemeente Moerdijk, dezelfde gemeente als ons kantoor in Zevenbergen. Binnen de oude vestingwerken staan historische panden, daaromheen liggen nieuwere woonwijken. Voor allebei installeren we thuisbatterijen, zonnepanelen en airco\'s, met ons eigen team en een vaste prijs vooraf.',
  local=[('Beschermd stadsgezicht', 'De oude kern van Klundert is een rijksbeschermd stadsgezicht. De vestingwerken en het oude stadhuis zijn rijksmonument. Zonnepanelen die vanaf de straat te zien zijn, of een buitenunit aan de gevel, hebben daar vaak een vergunning nodig. We zoeken vooraf uit wat voor jouw adres geldt.'),
         ('Een batterij zie je niet van buiten', 'Een thuisbatterij staat binnen, bijvoorbeeld in de garage, de bijkeuken of op zolder. Aan de buitenkant van je huis verandert niets. Woon je in een rijksmonument, dan checken we ook of er voor werk binnen een vergunning nodig is.'),
         ('Netbeheerder Enexis', 'In Klundert is Enexis in de regel de netbeheerder; je exacte adres is bepalend. Wij melden je batterij en zonnepanelen aan en regelen een zwaardere aansluiting als dat nodig is.'),
         ('Buiten de vesting', 'In de woonwijken rond de oude kern gelden meestal de gewone regels, en mogen zonnepanelen vaak zonder vergunning. Samen met een thuisbatterij gebruik je meer van je eigen stroom als het salderen op 1 januari 2027 stopt.')],
  faq=('Mag ik in de vesting van Klundert een thuisbatterij laten plaatsen?', 'Meestal wel. Een thuisbatterij staat binnen en is van buiten niet te zien. Alleen bij een rijksmonument kan ook voor werk binnen een vergunning nodig zijn. Dat zoeken we vooraf voor je uit.'),
  near=['Zevenbergen', 'Noordhoek', 'Moerdijk', 'Fijnaart', 'Oudemolen', 'Willemstad'],
  buren=['zevenbergen', 'willemstad', 'fijnaart', 'moerdijk', 'etten-leur'],
  arts=['artikel-thuisbatterij-plaatsen-waar', 'artikel-thuisbatterij-na-salderen', 'artikel-airco-plaatsen-regels-vergunning']),
 dict(slug='willemstad', name='Willemstad', region='West-Brabant', nb='Enexis', img='batterij-zolder', gemeente='Moerdijk',
  intro='Willemstad is een vestingstad aan het Hollandsch Diep en hoort, net als ons kantoor in Zevenbergen, bij de gemeente Moerdijk. In de vesting gelden strengere regels dan in veel andere wijken. We zoeken ze per adres voor je uit en installeren thuisbatterijen, zonnepanelen en airco\'s met ons eigen team.',
  local=[('Beschermd stadsgezicht', 'De vesting Willemstad is een rijksbeschermd stadsgezicht en telt tientallen rijksmonumenten. Alles wat je aan de buitenkant van je huis verandert, vraagt daar extra zorg.'),
         ('Regels voor zonnepanelen', 'De gemeente Moerdijk heeft een aparte beleidsregel voor zonnepanelen op monumenten en in het beschermd stadsgezicht Willemstad. De vesting is daarin verdeeld in zones. In de zone met de hoogste waarde mogen panelen alleen op het achterste dakvlak. We kijken in welke zone je woont en regelen de vergunning als die nodig is.'),
         ('Thuisbatterij: van buiten onzichtbaar', 'Een thuisbatterij staat binnen, bijvoorbeeld in de bijkeuken, de garage of op zolder. Aan het straatbeeld verandert niets. Bij een rijksmonument checken we wel of ook voor werk binnen een vergunning nodig is.'),
         ('Netbeheerder Enexis', 'In Willemstad is Enexis in de regel de netbeheerder; je exacte adres is bepalend. De aanmelding van je batterij of panelen en een eventuele verzwaring regelen wij.')],
  faq=('Heb ik in Willemstad een vergunning nodig voor zonnepanelen?', 'In de vesting en bij een monument vaak wel. De gemeente Moerdijk heeft daarvoor een beleidsregel met zones: in het deel met de hoogste waarde mogen panelen alleen op het achterste dakvlak. Ook net buiten de vesting kan die regel gelden. Wij checken het voor jouw adres en regelen de aanvraag.'),
  near=['Helwijk', 'Heijningen', 'Fijnaart', 'Klundert'],
  buren=['zevenbergen', 'klundert', 'fijnaart', 'steenbergen'],
  arts=['artikel-thuisbatterij-zonder-zonnepanelen', 'artikel-thuisbatterij-plaatsen-waar', 'artikel-airco-plaatsen-regels-vergunning']),
 dict(slug='fijnaart', name='Fijnaart', region='West-Brabant', nb='Enexis', img='monteur-dak', gemeente='Moerdijk',
  intro='Fijnaart is een polderdorp in de gemeente Moerdijk, net als ons kantoor in Zevenbergen. Het dorp ontstond in 1548 midden in de polder, met de kerk in het centrum. Hier installeren we thuisbatterijen, zonnepanelen en airco\'s met ons eigen team en een vaste prijs vooraf.',
  local=[('Dorp in de polder', 'De oude kern van Fijnaart is aangelegd rond de kerk, met een gracht eromheen en de Voorstraat richting de dijk. Daaromheen liggen woonwijken uit latere jaren. Welk dak en welke meterkast je hebt, bepaalt wat er past. Dat bekijken we per huis.'),
         ('Open land, veel wind', 'In het open polderland vangt een dak veel wind. De bevestiging van zonnepanelen moet daarop berekend zijn. Daar letten onze monteurs bij de montage op.'),
         ('Netbeheerder Enexis', 'In Fijnaart is Enexis in de regel de netbeheerder; je exacte adres is bepalend. Wij melden je installatie aan en regelen een zwaardere aansluiting als dat nodig is.'),
         ('Al zonnepanelen?', 'Dan is een thuisbatterij de logische volgende stap nu het salderen op 1 januari 2027 stopt. Waar je op let bij een bestaande installatie, lees je in [ons artikel over een batterij bij bestaande panelen](/artikel-thuisbatterij-bij-bestaande-zonnepanelen).')],
  faq=('Komen jullie ook in Heijningen en Oudemolen?', 'Ja. Heijningen en Oudemolen horen net als Fijnaart bij de gemeente Moerdijk. We installeren daar met dezelfde vaste prijzen en ons eigen team.'),
  near=['Heijningen', 'Oudemolen', 'Klundert', 'Willemstad', 'Standdaarbuiten'],
  buren=['zevenbergen', 'klundert', 'willemstad', 'oudenbosch', 'steenbergen'],
  arts=['artikel-thuisbatterij-bij-bestaande-zonnepanelen', 'artikel-checklist-salderen-2027', 'artikel-zonnepanelen-oost-west-of-zuid']),
 dict(slug='moerdijk', name='Moerdijk', region='West-Brabant', nb='Enexis', img='monteur-aan-het-werk', gemeente='Moerdijk',
  intro='Het dorp Moerdijk ligt aan het Hollandsch Diep, bij de Moerdijkbruggen en naast het haven- en industriegebied. Het is een van de kernen van de gemeente Moerdijk, waar ook ons kantoor in Zevenbergen staat. We installeren hier thuisbatterijen, zonnepanelen en airco\'s met ons eigen team en een vaste prijs vooraf.',
  local=[('Woningen uit de wederopbouw', 'Het dorp werd in 1944 zwaar beschadigd en daarna grotendeels herbouwd. Veel huizen stammen daardoor uit de jaren \'50. De meterkast is in woningen van die leeftijd vaak niet gemaakt voor een batterij, zonnepanelen en een laadpaal tegelijk. We kijken vooraf of er een groep bij moet.'),
         ('Netbeheerder Enexis', 'In Moerdijk is Enexis in de regel de netbeheerder; je exacte adres is bepalend. Wij regelen de aanmelding en, als dat nodig is, een zwaardere aansluiting.'),
         ('Batterij en een dynamisch contract', 'Met een dynamisch energiecontract laad je je batterij op als stroom goedkoop is en gebruik je hem als stroom duur is. We rekenen eerlijk voor je uit of dat bij jouw verbruik iets oplevert.'),
         ('De hele gemeente Moerdijk', 'We komen in alle kernen van de gemeente: van Zevenbergen, [Klundert](/installateur-klundert) en [Willemstad](/installateur-willemstad) tot [Fijnaart](/installateur-fijnaart), Zevenbergschen Hoek en Langeweg.')],
  faq=('Gaat deze pagina over het dorp of de gemeente Moerdijk?', 'Vooral over het dorp Moerdijk, maar we installeren in de hele gemeente. Voor Zevenbergen, Klundert, Willemstad en Fijnaart hebben we een eigen pagina.'),
  near=['Zevenbergschen Hoek', 'Langeweg', 'Zevenbergen', 'Klundert', 'Noordhoek', 'Lage Zwaluwe'],
  buren=['zevenbergen', 'klundert', 'made', 'breda'],
  arts=['artikel-meterkast-vervangen-signalen', 'artikel-groepen-bijplaatsen-meterkast', 'artikel-dynamisch-contract-en-batterij']),
 dict(slug='oudenbosch', name='Oudenbosch', region='West-Brabant', nb='Enexis', img='batterij-installatie', gemeente='Halderberge',
  intro='Oudenbosch is de hoofdplaats van de gemeente Halderberge, bekend om de basiliek en de gebouwen van het vroegere instituut Saint-Louis. Rond dat historische centrum liggen woonwijken van allerlei leeftijden. We installeren hier thuisbatterijen, zonnepanelen en airco\'s met ons eigen team en een vaste prijs vooraf.',
  local=[('Monumenten in het centrum', 'De basiliek en meerdere gebouwen van Saint-Louis zijn rijksmonument. Woon je in een monument, dan kan voor zonnepanelen of een buitenunit een vergunning nodig zijn. We zoeken het per adres uit.'),
         ('Netbeheerder Enexis', 'In Halderberge is Enexis in de regel de netbeheerder; je exacte adres is bepalend. Wij melden je installatie aan en regelen een zwaardere aansluiting als dat nodig is.'),
         ('1-fase of 3-fase?', 'Heb je een 1-fase aansluiting, dan past de batterij van 10 of 16 kWh met een 5 of 6 kW omvormer. Bij 3-fase wordt het de 16 kWh met 8 kW omvormer. Welke aansluiting je hebt, checken we vooraf in je meterkast.'),
         ('Airco erbij', 'Een split-airco koelt in de zomer en verwarmt zuinig in het voor- en najaar. Met zonnepanelen en een thuisbatterij draait hij voor een deel op je eigen stroom.')],
  faq=('Komen jullie ook in Hoeven, Oud Gastel en Bosschenhoofd?', 'Ja. We installeren in heel Halderberge: Oudenbosch, Hoeven, Oud Gastel, Bosschenhoofd en Stampersgat. Met dezelfde vaste prijzen en ons eigen team.'),
  near=['Bosschenhoofd', 'Hoeven', 'Oud Gastel', 'Stampersgat', 'Standdaarbuiten'],
  buren=['roosendaal', 'etten-leur', 'zevenbergen', 'fijnaart', 'steenbergen'],
  arts=['artikel-thuisbatterij-1-fase-aansluiting', 'artikel-airco-als-bijverwarming', 'artikel-thuisbatterij-hoe-groot']),
 dict(slug='steenbergen', name='Steenbergen', region='West-Brabant', nb='Enexis', img='zonnepanelen-installatie', gemeente='Steenbergen',
  intro='Steenbergen is een oude vestingstad, met de Gummaruskerk als herkenningspunt en een jachthaven in het centrum. De gemeente heeft zes kernen, van Dinteloord tot Nieuw-Vossemeer. We installeren er thuisbatterijen, zonnepanelen en airco\'s met ons eigen team en een vaste prijs vooraf.',
  local=[('Historisch centrum', 'In het centrum staan oudere panden, en de Gummaruskerk is rijksmonument. Bij een monument of in een beschermd gebied kan voor zonnepanelen of een buitenunit een vergunning nodig zijn. We zoeken vooraf uit wat voor jouw adres geldt.'),
         ('Netbeheerder Enexis', 'In de gemeente Steenbergen is Enexis in de regel de netbeheerder; je exacte adres is bepalend. De aanmelding en een eventuele verzwaring regelen wij.'),
         ('Minder terugleveren', 'Veel energieleveranciers rekenen terugleverkosten. Met een thuisbatterij sla je je overschot op en lever je minder terug. Hoe dat zit, lees je in [ons artikel over terugleverkosten](/artikel-terugleverkosten-uitgelegd).'),
         ('Ook in de dorpen', 'In Dinteloord, Kruisland, Nieuw-Vossemeer, Welberg en De Heen installeren we met dezelfde vaste prijzen. Of je nu in een rijtjeshuis woont of vrijstaand: de prijs weet je vooraf.')],
  faq=('Installeren jullie ook in Dinteloord en Nieuw-Vossemeer?', 'Ja. We komen in alle zes kernen van de gemeente Steenbergen: Steenbergen, Dinteloord, Kruisland, Nieuw-Vossemeer, Welberg en De Heen. Met ons eigen team en een vaste prijs vooraf.'),
  near=['Welberg', 'Dinteloord', 'Kruisland', 'Nieuw-Vossemeer', 'De Heen', 'Halsteren'],
  buren=['bergen-op-zoom', 'roosendaal', 'oudenbosch', 'willemstad'],
  arts=['artikel-terugleverkosten-uitgelegd', 'artikel-thuisbatterij-terugverdientijd', 'artikel-zonnepanelen-rendabel-na-2027']),
 dict(slug='made', name='Made', region='West-Brabant', nb='Enexis', img='thuisbatterij-bijkeuken', gemeente='Drimmelen',
  intro='Made is de hoofdplaats van de gemeente Drimmelen: het gemeentehuis staat hier. De gemeente ligt tegen de Biesbosch aan en bestaat uit zes dorpen. In Made en de dorpen eromheen installeren we thuisbatterijen, zonnepanelen en airco\'s met ons eigen team.',
  local=[('Zes dorpen, één gemeente', 'De gemeente Drimmelen bestaat uit Made, Drimmelen, Terheijden, Wagenberg, Lage Zwaluwe en Hooge Zwaluwe. In al die dorpen installeren we met dezelfde vaste prijzen.'),
         ('Netbeheerder Enexis', 'In Drimmelen is Enexis in de regel de netbeheerder; je exacte adres is bepalend. Wij melden je batterij en zonnepanelen aan en regelen een verzwaring als dat nodig is.'),
         ('Een goede plek voor de batterij', 'Een thuisbatterij kan in de garage, de bijkeuken of op zolder. Belangrijk is een droge plek die niet te warm of te koud wordt, met een korte route naar de meterkast. We kiezen de plek samen met je.'),
         ('Warmtepomp of airco erbij?', 'Een warmtepomp of airco gebruikt ook \'s avonds stroom. Met een batterij van 16 kWh vang je meer van dat verbruik op met je eigen zonnestroom.')],
  faq=('Komen jullie ook in Terheijden, Wagenberg en de Zwaluwes?', 'Ja. We installeren in de hele gemeente Drimmelen: Made, Drimmelen, Terheijden, Wagenberg, Lage Zwaluwe en Hooge Zwaluwe. Met dezelfde vaste prijzen en ons eigen team.'),
  near=['Drimmelen', 'Terheijden', 'Wagenberg', 'Lage Zwaluwe', 'Hooge Zwaluwe', 'Helkant'],
  buren=['oosterhout', 'breda', 'geertruidenberg', 'moerdijk', 'zevenbergen'],
  arts=['artikel-thuisbatterij-plaatsen-waar', 'artikel-thuisbatterij-hoe-groot', 'artikel-warmtepomp-en-zonnepanelen-combineren']),
 dict(slug='zundert', name='Zundert', region='West-Brabant', nb='Enexis', img='monteur-en-klant', gemeente='Zundert',
  intro='Zundert is de geboorteplaats van Vincent van Gogh en het hart van een grote boomteeltregio. De gemeente bestaat uit Zundert, Rijsbergen, Wernhout, Klein-Zundert en Achtmaal. We installeren er thuisbatterijen, zonnepanelen en airco\'s met ons eigen team en een vaste prijs vooraf.',
  local=[('Dorp en buitengebied', 'Naast de dorpskernen heeft de gemeente veel buitengebied, met kwekerijen en boerderijen. Heb je een schuur of bijgebouw, dan kan de batterij daar soms ook staan, als de plek droog is en de kabel naar de meterkast goed te leggen is.'),
         ('Netbeheerder Enexis', 'In Zundert is Enexis in de regel de netbeheerder; je exacte adres is bepalend. Wij regelen de aanmelding en, als dat nodig is, een zwaardere aansluiting.'),
         ('Batterij zonder zonnepanelen?', 'Ook zonder eigen panelen kan een thuisbatterij iets opleveren, bijvoorbeeld met een dynamisch contract. Of dat voor jou loont, rekenen we eerlijk voor je door.'),
         ('Na 2027 geen salderen meer', 'Op 1 januari 2027 stopt de salderingsregeling. Stroom die je teruglevert, levert dan minder op. Met een thuisbatterij gebruik je meer van je eigen zonnestroom zelf.')],
  faq=('Installeren jullie ook in Rijsbergen en Wernhout?', 'Ja. We komen in de hele gemeente Zundert: Zundert, Rijsbergen, Wernhout, Klein-Zundert en Achtmaal. Met dezelfde vaste prijzen en ons eigen team.'),
  near=['Rijsbergen', 'Wernhout', 'Klein-Zundert', 'Achtmaal', 'Sprundel'],
  buren=['breda', 'etten-leur', 'rucphen', 'roosendaal'],
  arts=['artikel-thuisbatterij-zonder-zonnepanelen', 'artikel-thuisbatterij-plaatsen-waar', 'artikel-salderingsregeling-2027']),
 dict(slug='rucphen', name='Rucphen', region='West-Brabant', nb='Enexis', img='batterij-zolder', gemeente='Rucphen',
  intro='De gemeente Rucphen bestaat uit vijf kernen: Rucphen, Sint Willebrord, Sprundel, Schijf en Zegge. Sint Willebrord is daarvan de grootste. In alle vijf installeren we thuisbatterijen, zonnepanelen en airco\'s met ons eigen team en een vaste prijs vooraf.',
  local=[('Welke batterij past?', 'Dat hangt af van je verbruik, het aantal zonnepanelen en je aansluiting. Met weinig verbruik is 10 kWh vaak genoeg. Heb je een elektrische auto, een warmtepomp of een dynamisch contract, dan past 16 kWh meestal beter.'),
         ('Netbeheerder Enexis', 'In de gemeente Rucphen is Enexis in de regel de netbeheerder; je exacte adres is bepalend. De aanmelding en een eventuele verzwaring regelen wij.'),
         ('Wat levert het op?', 'Hoe snel een thuisbatterij zich terugverdient, hangt af van je verbruik en je energiecontract. We rekenen het eerlijk voor je door. Zelf rekenen kan ook, met [ons artikel over de terugverdientijd](/artikel-thuisbatterij-terugverdientijd).'),
         ('Vijf dorpen, één prijs', 'Of je nu in Rucphen, Sint Willebrord, Sprundel, Schijf of Zegge woont: je krijgt dezelfde vaste prijs en hetzelfde eigen team.')],
  faq=('Komen jullie ook in Sint Willebrord en Sprundel?', 'Ja. We installeren in alle vijf kernen van de gemeente Rucphen: Rucphen, Sint Willebrord, Sprundel, Schijf en Zegge. Met dezelfde vaste prijzen en ons eigen team.'),
  near=['Sint Willebrord', 'Sprundel', 'Schijf', 'Zegge', 'Hoeven'],
  buren=['etten-leur', 'roosendaal', 'zundert', 'oudenbosch'],
  arts=['artikel-thuisbatterij-hoe-groot', 'artikel-thuisbatterij-terugverdientijd', 'artikel-dynamisch-contract-en-batterij']),
 dict(slug='geertruidenberg', name='Geertruidenberg', label='Geertruidenberg en Raamsdonksveer', area=['Geertruidenberg', 'Raamsdonksveer', 'Raamsdonk'],
  region='West-Brabant', nb='Enexis', img='monteur-dak', gemeente='Geertruidenberg',
  intro='De gemeente Geertruidenberg bestaat uit drie kernen: de oude vestingstad Geertruidenberg, Raamsdonksveer en Raamsdonk. Raamsdonksveer is de grootste, met de meeste woonwijken en winkels. In alle drie installeren we thuisbatterijen, zonnepanelen en airco\'s met ons eigen team.',
  local=[('Beschermd stadsgezicht', 'De historische kern van Geertruidenberg, met de vestingwerken, de Markt en de straten eromheen, is een rijksbeschermd stadsgezicht. Zonnepanelen of een buitenunit die vanaf de straat te zien zijn, hebben daar vaak een vergunning nodig. Een thuisbatterij staat binnen en zie je van buiten niet.'),
         ('Raamsdonksveer en Raamsdonk', 'In de woonwijken van Raamsdonksveer en Raamsdonk gelden meestal de gewone regels, en mogen zonnepanelen vaak zonder vergunning. We checken het voor jouw adres.'),
         ('Netbeheerder Enexis', 'In de gemeente Geertruidenberg is Enexis in de regel de netbeheerder; je exacte adres is bepalend. Wij melden je installatie aan en regelen een zwaardere aansluiting als dat nodig is.'),
         ('Meterkast eerst', 'Wil je een batterij én bijvoorbeeld een laadpaal of warmtepomp? Dan kijken we eerst of je meterkast genoeg groepen heeft. Moet er iets bij, dan hoor je dat vooraf.')],
  faq=('Installeren jullie ook in Raamsdonksveer en Raamsdonk?', 'Ja. We installeren in de hele gemeente Geertruidenberg: in de vesting, in Raamsdonksveer en in Raamsdonk. Met dezelfde vaste prijzen en ons eigen team.'),
  near=['Raamsdonksveer', 'Raamsdonk', 'Made', 'Oosterhout', 'Dongen'],
  buren=['oosterhout', 'made', 'breda'],
  arts=['artikel-airco-plaatsen-regels-vergunning', 'artikel-thuisbatterij-plaatsen-waar', 'artikel-meterkast-onderschatte-stap']),
]

# West-Brabant: thuisbatterij voorop (H1, titel, description, volgorde). De overige plaatsen houden hun tekst.
WB_EXTRA = {
 'zevenbergen': dict(gemeente='Moerdijk', buren=['klundert', 'willemstad', 'fijnaart', 'moerdijk', 'breda', 'etten-leur', 'roosendaal', 'oosterhout']),
 'breda': dict(gemeente='Breda', buren=['zevenbergen', 'etten-leur', 'oosterhout', 'made', 'zundert', 'roosendaal']),
 'etten-leur': dict(gemeente='Etten-Leur', buren=['zevenbergen', 'breda', 'roosendaal', 'rucphen', 'zundert', 'oudenbosch'],
   h1='Thuisbatterij en zonnepanelen in Etten-Leur',
   title='Thuisbatterij & zonnepanelen installeren in Etten-Leur',
   desc='Thuisbatterij of zonnepanelen in Etten-Leur? Batterij 10 kWh € 4.200, 16 kWh € 4.600 of 16 kWh 3-fase € 5.700, excl. btw en incl. installatie.'),
 'roosendaal': dict(gemeente='Roosendaal', buren=['bergen-op-zoom', 'etten-leur', 'oudenbosch', 'rucphen', 'steenbergen', 'zevenbergen']),
 'bergen-op-zoom': dict(gemeente='Bergen op Zoom', buren=['roosendaal', 'steenbergen', 'etten-leur', 'zevenbergen']),
 'oosterhout': dict(gemeente='Oosterhout', buren=['breda', 'geertruidenberg', 'made', 'zevenbergen', 'tilburg']),
}
for c in CITIES:
    if c['slug'] in WB_EXTRA: c.update(WB_EXTRA[c['slug']])
    c['wb'] = 'gemeente' in c
    if c['slug'] == 'zevenbergen':  # Willemstad heeft nu een eigen pagina
        c['local'] = [(h, t + ' Meer op onze [pagina over Willemstad](/installateur-willemstad).' if h == 'Vestingstadje Willemstad' else t) for h, t in c['local']]

# Etten-Leur: een sectie die precies de zoekvraag beantwoordt (kop, inleiding, stappen, slot)
EXTRA = {
 'etten-leur': ('Zonnepanelen of een thuisbatterij laten installeren in Etten-Leur: zo gaat het',
   'Kort gezegd: je kiest wat je wilt, wij kijken naar je dak en meterkast, en onze eigen monteurs installeren alles voor een vaste prijs. Een thuisbatterij kost vanaf ' + eur(VANAF) + ' excl. btw en zonnepanelen vanaf € 3.999 voor 12 panelen, allebei inclusief installatie.',
   ['**Kies wat je wilt.** Alleen zonnepanelen, alleen een thuisbatterij of allebei. Met de [batterijcalculator](/thuisbatterij-berekenen) zie je welke batterij past en wat hij kost.',
    '**We checken je dak en meterkast.** Ligging, schaduw en ruimte op het dak, en of je aansluiting 1-fase of 3-fase is. Moet er iets bij, dan hoor je dat vooraf.',
    '**Onze eigen monteurs installeren.** Geen onderaannemers. Wij melden je installatie aan bij de netbeheerder; in Etten-Leur is dat in de regel Enexis.',
    '**Uitleg bij de oplevering.** Je krijgt uitleg over de app en 2 jaar garantie op de installatie.'],
   'Heb je al zonnepanelen? Dan is een thuisbatterij de logische volgende stap nu het salderen op 1 januari 2027 stopt. Lees ook [waar je op let bij een batterij naast bestaande panelen](/artikel-thuisbatterij-bij-bestaande-zonnepanelen).'),
}
WB_ORDER = ['Thuisbatterij', 'Zonnepanelen', 'Airconditioning', 'Warmtepomp', 'Elektrische boiler', 'Laadpaal', 'Meterkastaanpassing']
BY = {c['slug']: c for c in CITIES}
# /werkgebied: West-Brabant per gemeente (pagina's + overige kernen van die gemeente), daarna de rest
WB_GEMEENTEN = [
 ('Moerdijk', ['zevenbergen', 'klundert', 'willemstad', 'fijnaart', 'moerdijk'], ['Zevenbergschen Hoek', 'Standdaarbuiten', 'Heijningen', 'Langeweg', 'Noordhoek', 'Helwijk']),
 ('Breda', ['breda'], ['Prinsenbeek', 'Teteringen', 'Bavel', 'Ulvenhout']),
 ('Etten-Leur', ['etten-leur'], []),
 ('Roosendaal', ['roosendaal'], ['Nispen', 'Wouw', 'Heerle', 'Wouwse Plantage']),
 ('Halderberge', ['oudenbosch'], ['Hoeven', 'Oud Gastel', 'Bosschenhoofd', 'Stampersgat']),
 ('Steenbergen', ['steenbergen'], ['Dinteloord', 'Kruisland', 'Nieuw-Vossemeer', 'Welberg', 'De Heen']),
 ('Bergen op Zoom', ['bergen-op-zoom'], ['Halsteren', 'Lepelstraat']),
 ('Rucphen', ['rucphen'], ['Sint Willebrord', 'Sprundel', 'Schijf', 'Zegge']),
 ('Zundert', ['zundert'], ['Rijsbergen', 'Wernhout', 'Klein-Zundert', 'Achtmaal']),
 ('Drimmelen', ['made'], ['Terheijden', 'Wagenberg', 'Drimmelen', 'Lage Zwaluwe', 'Hooge Zwaluwe']),
 ('Geertruidenberg', ['geertruidenberg'], ['Raamsdonk']),
 ('Oosterhout', ['oosterhout'], ['Dorst', 'Den Hout', 'Oosteind']),
]
GROUPS = [('Drechtsteden', ['dordrecht']),
          ('Rest van Brabant', ['tilburg', 's-hertogenbosch', 'eindhoven']),
          ('Randstad', ['rotterdam', 'den-haag', 'utrecht', 'amsterdam'])]
def label(c): return c.get('label', c['name'])

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
.lp-sub{font-size:14px;font-weight:700;color:var(--primary);margin-top:10px;}
.lp-bat{background:#fff;border:1px solid var(--border);border-radius:22px;padding:26px 28px;}
.lp-bat>p{font-size:15px;color:var(--ink-soft);margin-top:8px;line-height:1.6;max-width:680px;}
.lp-pk{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:20px;}
.lp-pk div{border:1px solid var(--border);border-radius:16px;padding:16px 18px;background:var(--bg);}
.lp-pk b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:22px;color:var(--ink);}
.lp-pk span{display:block;font-size:13.5px;color:var(--ink-soft);margin-top:2px;line-height:1.45;}
.lp-pk strong{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:24px;color:var(--ink);margin-top:12px;}
.lp-pk small{font-size:12.5px;color:var(--ink-faint);}
.lp-bat-foot{display:flex;gap:10px 18px;align-items:center;flex-wrap:wrap;margin-top:20px;font-size:14px;}
.lp-bat-foot a.lp-more{color:var(--primary);font-weight:700;text-decoration:none;}
.lp-extra{max-width:760px;}
.lp-extra p{font-size:15.5px;line-height:1.7;color:var(--ink-soft);margin-top:12px;}
.lp-extra ol{margin:14px 0 0;padding-left:22px;font-size:15.5px;line-height:1.7;color:var(--ink-soft);}
.lp-extra li{margin-top:6px;} .lp-extra a{color:var(--primary);font-weight:700;} .lp-extra strong{color:var(--ink);}
.lp-local p a{color:var(--primary);font-weight:700;}
.lp-gm{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px;margin-top:18px;}
.lp-gm>div{background:#fff;border:1px solid var(--border);border-radius:18px;padding:18px 20px;}
.lp-gm h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:17px;margin:0;color:var(--ink);}
.lp-gm .lp-chips{margin-top:10px;} .lp-gm p{font-size:13.5px;color:var(--ink-soft);margin-top:10px;line-height:1.55;}
@media (max-width:900px){.lp-hero{grid-template-columns:1fr;gap:28px;}.lp-stats{grid-template-columns:repeat(2,minmax(0,1fr));}.lp-steps{grid-template-columns:1fr;}}
@media (max-width:640px){.lp-local{grid-template-columns:1fr;}.lp-cta{padding:26px 22px;}.lp-pk{grid-template-columns:1fr;}.lp-bat{padding:22px 18px;}}
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
      <div style="display:flex;gap:10px;flex-wrap:wrap;"><a href="/thuisbatterij-berekenen" class="btn-primary" style="background:var(--mint);color:var(--dark);text-decoration:none;">Bereken je thuisbatterij →</a><a href="/contact" data-book="" class="btn-secondary" style="border-color:#fff;color:#fff;text-decoration:none;">Plan gratis adviesgesprek</a></div>
    </div></div>'''

def city_faq(c):
    n, nb = label(c), c['nb']
    p = {x['id']: x for x in PAKKETTEN}
    kost = ((f'Wat kost een thuisbatterij in {n}?', f'Een thuisbatterij kost bij ons {eur(p["bat10"]["prijs"])} (10 kWh), {eur(p["bat16-1"]["prijs"])} (16 kWh, 1-fase) of {eur(p["bat16-3"]["prijs"])} (16 kWh, 3-fase), exclusief btw en inclusief installatie. Zonnepanelen kosten vanaf € 3.999 en een airco vanaf € 1.899. Met de batterijcalculator zie je in een minuut welke batterij bij je past.')
            if c['wb'] else
            (f'Wat kost de installatie in {n}?', f'Je betaalt in {n} een vaste prijs die je vooraf kent: zonnepanelen vanaf € 3.999, een thuisbatterij vanaf € 4.200 excl. btw en een warmtepomp vanaf € 6.750, inclusief installatie. Met de batterijcalculator zie je binnen een minuut welke batterij bij jouw woning past en wat hij kost.'))
    nbq = ((f'Wie regelt de netbeheerder en de vergunning in {n}?', f'Dat doen wij. In {n} is {NB[nb]} in de regel de netbeheerder (je exacte adres is bepalend). Wij regelen de aanmelding, een eventuele verzwaring van je aansluiting, een vergunning als die nodig is. Bij een warmtepomp helpen we je met de ISDE-aanvraag.')
           if c['wb'] else
           (f'Wie regelt de netbeheerder en de vergunning in {n}?', f'Dat doen wij. In {n} is {NB[nb]} de netbeheerder (het precieze adres is bepalend). Wij regelen de aanmelding, een eventuele verzwaring van je aansluiting, een vergunning als die nodig is. Bij een warmtepomp helpen we je met de ISDE-aanvraag.'))
    qa = [c['faq'], kost, nbq,
          (f'Werken jullie in {n} met onderaannemers?', 'Nee. Alle installaties doen we met onze eigen monteurs. Daardoor weten we zeker dat het werk goed is en heb je één aanspreekpunt, ook na de installatie.'),
          ('Hoe snel kan de installatie plaatsvinden?', 'Na de offerte plannen we samen een installatiedatum. In de batterijcalculator zie je na het invullen van je adres vanaf wanneer we bij jou kunnen installeren.')]
    return qa

def battery_block(n=None):
    """Compact blok met de drie batterijpakketten (op alle plaatspagina's en /werkgebied)."""
    cards = ''.join(f'<div><b>{p["kwh"]} kWh</b><span>{p["kw"]} kW hybride omvormer · {esc(p["fase"])}</span>'
                    f'<strong>{esc(eur(p["prijs"]))}</strong><small>incl. installatie, excl. btw</small></div>' for p in PAKKETTEN)
    kop = f'Thuisbatterij in {esc(n)}: drie vaste pakketten' if n else 'Thuisbatterij: drie vaste pakketten'
    return f'''<div class="wrap reveal lp-sec" style="max-width:1000px;"><div class="lp-bat">
    <h2 class="vw-heading lp-h2">{kop}</h2>
    <p>Een batterij van 10 of 16 kWh met hybride omvormer, geplaatst door onze eigen monteurs. Welke past, hangt af van je verbruik, je zonnepanelen en je aansluiting (1-fase of 3-fase). Op de installatie krijg je 2 jaar garantie.</p>
    <div class="lp-pk">{cards}</div>
    <div class="lp-bat-foot"><a href="/thuisbatterij-berekenen" class="btn-primary" style="text-decoration:none;">Bereken je thuisbatterij →</a><a class="lp-more" href="/product-batterij">Meer over de thuisbatterij</a></div>
  </div></div>'''

def extra_block(c):
    if c['slug'] not in EXTRA: return ''
    kop, intro, stappen, slot = EXTRA[c['slug']]
    li = ''.join(f'<li>{inline(s)}</li>' for s in stappen)
    return f'''<div class="wrap reveal lp-sec" style="max-width:1000px;"><div class="lp-extra">
    <h2 class="vw-heading lp-h2">{esc(kop)}</h2>
    <p>{inline(intro)}</p>
    <ol>{li}</ol>
    <p>{inline(slot)}</p>
  </div></div>'''

def h1_of(c):
    if not c['wb']: return f'Zonnepanelen, thuisbatterij en warmtepomp in {c["name"]}'
    return c.get('h1', f'Thuisbatterij in {label(c)}')

def title_of(c):
    n = c['name']
    if not c['wb']: return f'Thuisbatterij, zonnepanelen & warmtepomp {n} | Voltwijk'
    if 'title' in c: return c['title']
    v = eur(VANAF)
    for t in (f'Thuisbatterij {n} – vanaf {v} excl. btw | Voltwijk',
              f'Thuisbatterij {n}: vanaf {v} excl. btw',
              f'Thuisbatterij {n} – vanaf {v} | Voltwijk'):
        if len(t) <= 60: return t
    raise ValueError(n)

def desc_of(c):
    n = c['name']
    if not c['wb']: return f'Thuisbatterij, zonnepanelen of warmtepomp in {n}? Vaste prijs vooraf, eigen monteurs, 12.500+ installaties, 4,7/5 op Google.'
    if 'desc' in c: return c['desc']
    p = {x['id']: x for x in PAKKETTEN}
    d = (f'Thuisbatterij in {label(c)}: 10 kWh {eur(p["bat10"]["prijs"])}, 16 kWh {eur(p["bat16-1"]["prijs"])} of 16 kWh 3-fase '
         f'{eur(p["bat16-3"]["prijs"])}, excl. btw, incl. installatie door eigen monteurs. Ook zonnepanelen en airco.')
    if len(d) > 160: d = d.replace(' door eigen monteurs', '')
    if len(d) > 160: d = d.replace(' Ook zonnepanelen en airco.', '')
    return d

def city_main(c):
    n, lab, wb = c['name'], label(c), c['wb']
    local = ''.join(f'<div><h3>{esc(h)}</h3><p>{inline(t)}</p></div>' for h, t in c['local'])
    plist = sorted(PRODUCTS, key=lambda x: WB_ORDER.index(x[0])) if wb else PRODUCTS
    prods = ''.join(f'<a href="{u}"><img loading="lazy" decoding="async" src="/images/{im}.webp" alt="{esc(p)}"><div><b>{esc(p)}</b><span>{esc(pr)}</span></div></a>' for p, pr, u, im in plist)
    arts = ''.join(f'<a href="/{a}">{esc(ART[a])} →</a>' for a in c['arts'] if os.path.exists(a + '.html'))
    faq = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in city_faq(c))
    buren = ''.join(f'<a href="/installateur-{b}">{esc(BY[b]["name"])}</a>' for b in c['buren'])
    near = ', '.join(c['near'][:-1]) + ' en ' + c['near'][-1]
    wa = WA + urllib.parse.quote(f'Hoi Voltwijk, ik woon in {n} en heb een vraag')
    h1attr = (' data-area="' + esc('|'.join(c.get('area', [n]))) + '" data-gemeente="' + esc(c['gemeente']) + '"') if wb else ''
    sub = f'\n        <p class="lp-sub">Vaste prijs vanaf {esc(eur(VANAF))} excl. btw, inclusief installatie · ook zonnepanelen en airco</p>' if wb else ''
    prod_kop = f'Ook zonnepanelen en airco in {esc(lab)}' if wb else f'Wat we in {esc(n)} installeren'
    return f'''<div class="blk-light" style="padding-top:40px;">
  {CSS}
  <div class="wrap reveal" style="max-width:1000px;padding-top:48px;">
    {crumbs([('Werkgebied', '/werkgebied'), (lab, None)])}
    <div class="lp-hero" style="margin-top:18px;">
      <div>
        <div class="pill">Werkgebied · {esc(c['region'])}</div>
        <h1 class="vw-heading"{h1attr} style="font-size:clamp(30px,4.6vw,44px);margin-top:14px;line-height:1.15;">{esc(h1_of(c))}</h1>{sub}
        <p style="font-size:17px;color:var(--ink-soft);margin-top:16px;line-height:1.65;">{esc(c['intro'])}</p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:24px;"><a href="/thuisbatterij-berekenen" class="btn-primary" style="text-decoration:none;">Bereken je thuisbatterij →</a><a href="{wa}" target="_blank" rel="noopener" class="btn-secondary" style="text-decoration:none;">Stuur een appje</a></div>
      </div>
      <div class="img"><img fetchpriority="high" src="/images/{c['img']}.webp" alt="Installatie door een Voltwijk-monteur" width="800" height="600"></div>
    </div>
    {STATS}
  </div>
  {battery_block(lab)}
  {extra_block(c)}
  <div class="wrap reveal lp-sec" style="max-width:1000px;">
    <h2 class="vw-heading lp-h2">{prod_kop}</h2>
    <p style="font-size:15.5px;color:var(--ink-soft);margin-top:10px;line-height:1.6;max-width:680px;">Vaste prijzen vooraf, inclusief installatie door ons eigen team.</p>
    <div class="lp-prod">{prods}</div>
  </div>
  <div class="wrap reveal lp-sec" style="max-width:1000px;">
    <h2 class="vw-heading lp-h2">Goed om te weten in {esc(lab)}</h2>
    <div class="lp-local">{local}</div>
  </div>
  <div class="wrap reveal lp-sec" style="max-width:1000px;">
    <h2 class="vw-heading lp-h2">Zo gaat het</h2>
    <div class="lp-steps">
      <div><div class="step-num">1</div><p><b>Bereken of plan</b>Bereken in 1 minuut welke thuisbatterij past, of plan een gratis adviesgesprek voor een ander product.</p></div>
      <div><div class="step-num">2</div><p><b>Wij regelen de rest</b>Netbeheerder en vergunning regelen wij, en bij de ISDE-aanvraag voor een warmtepomp helpen we je.</p></div>
      <div><div class="step-num">3</div><p><b>Installatie door ons eigen team</b>Na de offerte plannen we samen een installatiedatum. Op de installatie krijg je 2 jaar garantie.</p></div>
    </div>
  </div>
  <div class="wrap reveal lp-sec" style="max-width:1000px;">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:40px;">
      <div>
        <h2 class="vw-heading lp-h2">Veelgestelde vragen over {esc(lab)}</h2>
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
  {cta(f'Een thuisbatterij in {n}?', 'Bereken in 1 minuut welke thuisbatterij bij je past, met vaste prijs inclusief installatie. Voor zonnepanelen, een warmtepomp of iets anders plan je een gratis adviesgesprek.')}
</div>
'''

def overview_main():
    gm = ''
    for g, slugs, ook in WB_GEMEENTEN:
        chips = ''.join(f'<a href="/installateur-{s}">{esc(label(BY[s]))}</a>' for s in slugs)
        extra = f'<p>Ook: {esc(", ".join(ook))}.</p>' if ook else ''
        gm += f'<div><h3>Gemeente {esc(g)}</h3><div class="lp-chips">{chips}</div>{extra}</div>'
    groups = ''
    for lab, slugs in GROUPS:
        cards = ''.join(f'<a href="/installateur-{s}"><b>{esc(BY[s]["name"])}</b><span>Netbeheerder: {esc(NB[BY[s]["nb"]])}</span></a>' for s in slugs)
        groups += f'<h2 class="vw-heading lp-h2" style="font-size:22px;margin-top:40px;">{esc(lab)}</h2><div class="lp-grid">{cards}</div>'
    return f'''<div class="blk-light" style="padding-top:40px;">
  {CSS}
  <div class="wrap reveal" style="max-width:1000px;padding-top:48px;">
    <div class="pill">Werkgebied · West-Brabant</div>
    <h1 class="vw-heading" style="font-size:clamp(30px,4.6vw,44px);margin-top:14px;line-height:1.15;">Thuisbatterij en zonnepanelen in West-Brabant</h1>
    <p style="font-size:17px;color:var(--ink-soft);margin-top:16px;line-height:1.65;max-width:700px;">Ons kantoor zit in Zevenbergen, midden in West-Brabant. Van daaruit installeren we thuisbatterijen, zonnepanelen en airco's in de hele regio, met ons eigen team en een vaste prijs vooraf. Hieronder vind je de plaatsen per gemeente.</p>
    {STATS}
  </div>
  {battery_block()}
  <div class="wrap reveal lp-sec" style="max-width:1000px;">
    <h2 class="vw-heading lp-h2">West-Brabant: onze thuisbasis</h2>
    <p style="font-size:15.5px;color:var(--ink-soft);margin-top:10px;line-height:1.6;max-width:680px;">Per gemeente de plaatsen met een eigen pagina. In de andere kernen van die gemeenten installeren we ook, met dezelfde vaste prijzen. Netbeheerder is in West-Brabant in de regel Enexis; je exacte adres is bepalend.</p>
    <div class="lp-gm">{gm}</div>
  </div>
  <div class="wrap reveal lp-sec" style="max-width:1000px;padding-top:24px;">
    <h2 class="vw-heading lp-h2" style="margin-top:16px;">Andere plaatsen</h2>
    {groups}
    <p style="font-size:15px;color:var(--ink-soft);margin-top:32px;line-height:1.6;">Staat jouw plaats er niet tussen? Vul je postcode in bij de <a href="/thuisbatterij-berekenen" style="color:var(--primary);font-weight:700;">batterijcalculator</a> of <a href="/contact" style="color:var(--primary);font-weight:700;">neem contact op</a>, dan hoor je snel of we bij jou kunnen komen.</p>
  </div>
  {cta('Welke thuisbatterij past bij jou?', 'Bereken in 1 minuut je advies en vaste prijs, inclusief installatie. Voor zonnepanelen, een warmtepomp of iets anders plan je een gratis adviesgesprek.')}
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

FOOT_CITIES = ['zevenbergen', 'breda', 'etten-leur', 'roosendaal', 'oosterhout', 'bergen-op-zoom']
def footer_col():
    links = ''.join(f'\n          <a href="/installateur-{s}" style="color:inherit;text-decoration:none;">{esc(BY[s]["name"])}</a>' for s in FOOT_CITIES)
    return ('<!-- wg:start --><div style="font-size:13px;color:#C9D6D3;display:flex;flex-direction:column;gap:10px;">\n'
            '          <div style="color:var(--mint);font-weight:700;font-size:12px;">WERKGEBIED</div>' + links +
            '\n          <a href="/werkgebied" style="color:inherit;text-decoration:none;">Alle plaatsen →</a>\n        </div><!-- wg:end -->')

def main():
    shell = open(SHELL, encoding='utf-8').read()
    for c in CITIES:
        for b in c['buren']: assert b in BY, (c['slug'], b)
        title, desc = title_of(c), desc_of(c)
        assert len(title) <= 60 or not c['wb'], title
        assert len(desc) <= 160, desc
        open(f'installateur-{c["slug"]}.html', 'w', encoding='utf-8').write(page(shell, city_main(c), f'installateur-{c["slug"]}', title, desc))
    open('werkgebied.html', 'w', encoding='utf-8').write(page(shell, overview_main(), 'werkgebied',
        'Werkgebied: thuisbatterij en zonnepanelen in West-Brabant',
        'Thuisbatterij, zonnepanelen en airco in heel West-Brabant, vanuit ons kantoor in Zevenbergen. Bekijk je plaats per gemeente en zie je vaste prijs.'))
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
