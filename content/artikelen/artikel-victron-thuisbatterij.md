title: Victron thuisbatterij: hoe werkt een Victron-systeem en voor wie is het?
seo_title: Victron thuisbatterij: zo werkt het | Voltwijk
description: Victron thuisbatterij uitgelegd: hoe MultiPlus-II, Cerbo GX en een losse batterij samenwerken, wat ESS doet, noodstroom en voor wie het past.
category: Thuisbatterij
product: batterij
date: 2026-10-08
image: batterij-installatie
lead: Een Victron thuisbatterij is geen kant-en-klaar pakket, maar een systeem van losse onderdelen. Een omvormer-lader (MultiPlus-II of Quattro), een Cerbo GX als brein en een losse laagvolt-batterij werken samen in de ESS-modus. Dat geeft veel vrijheid en noodstroom, maar vraagt ook meer kennis bij het ontwerpen en instellen.
summary: Victron Energy is een Nederlands bedrijf uit Almere, opgericht in 1975 || Een Victron-thuisbatterij bestaat uit een MultiPlus-II of Quattro, een Cerbo GX en een losse 48V-batterij, vaak van een ander merk || In de ESS-modus staat het systeem AC-gekoppeld naast je bestaande omvormer en kan het noodstroom leveren op aparte groepen || Sterk in flexibiliteit en uitleesbaarheid; meer onderdelen en instellingen dan een kant-en-klaar hybride systeem
sources: Victron Energy – Dynamic ESS|https://www.victronenergy.com/blog/2024/04/23/dynamic-energy-storage-system-save-energy-costs-automatically/ || Victron Energy – Handleiding MultiPlus-II GX|https://www.victronenergy.com.au/upload/documents/Manual-MultiPlus-II-GX-EN-(p).pdf || Victron Energy – Datasheet ESS-toepassing Quattro (NL)|https://www.victronenergy.nl/upload/documents/Datasheet-ESS-application-Quattro-48V-8-10-15kVA-NL.pdf || Victron Energy – Thuisbatterijsystemen|https://www.victronenergy.com.au/energy-storage/home-battery-systems || Victron Community – AC-gekoppelde omvormers bij netuitval|https://community.victronenergy.com/t/ac-coupled-pv-inverters-stop-working-when-ess-loses-grid-connection/50331 || Victron Community – De factor 1.0-regel|https://community.victronenergy.com/t/the-factor-1-0-rule/15839?page=2
---
Wie zich verdiept in thuisbatterijen, komt de naam Victron snel tegen. Op forums en in technische video's wordt het merk veel genoemd. Toch werkt een Victron-systeem anders dan de meeste thuisbatterijen die je in een folder ziet. Je koopt geen kast met alles erin, maar je stelt een systeem samen uit losse onderdelen.

In dit artikel lees je hoe dat werkt, wat ESS is, hoe het zit met noodstroom en voor wie zo'n systeem logisch is.

## Wie is Victron Energy?

Victron Energy is een **Nederlands bedrijf**, opgericht in 1975 en gevestigd in **Almere**. Het begon met stroomvoorziening aan boord van schepen. Inmiddels zit Victron-apparatuur ook in campers, off-grid installaties en woningen. Die achtergrond zie je terug in de producten: robuust, modulair en met veel instelmogelijkheden.

Victron maakt vooral de **omvormers, laders en regelapparatuur**. De batterij zelf komt vaak van een ander merk.

## Uit welke onderdelen bestaat een Victron thuisbatterij?

Een Victron-systeem voor thuis bestaat meestal uit drie hoofdonderdelen:

| Onderdeel | Wat het doet |
|---|---|
| **MultiPlus-II** of **Quattro** | Omvormer en lader in één. Zet wisselstroom uit je huis om in gelijkstroom voor de batterij, en andersom. De Quattro is een zwaardere variant. |
| **Cerbo GX** (of een ander GX-apparaat) | Het brein en communicatiecentrum. Stuurt het systeem aan en verbindt het met internet en het VRM-portaal. |
| **Batterij** | Een losse **laagvolt-batterij** (48 volt), van Victron zelf of van een ander merk dat met Victron kan communiceren. |

Daarnaast hoort er een **energiemeter** bij je netaansluiting. Die meet of je huis stroom afneemt of teruglevert. Op basis daarvan beslist het systeem of de batterij laadt of ontlaadt.

Er bestaat ook een MultiPlus-II **GX**: daar zit het GX-deel al in de omvormer. Dan heb je geen losse Cerbo nodig.

### Laagvolt in plaats van hoogvolt

Veel kant-en-klare thuisbatterijen werken met **hoogvolt**: een stapel modules met samen een paar honderd volt. Victron werkt met **laagvolt**, rond 48 volt. Dat heeft gevolgen voor de keuze. Niet elke batterij past. De batterij moet laagvolt zijn en met de Victron-apparatuur kunnen praten. Zo werkt bijvoorbeeld Dyness met Victron, maar alleen met de laagvolt-series. Lees meer in [Dyness thuisbatterij](/artikel-dyness-thuisbatterij).

### 1-fase of 3-fase

Eén MultiPlus-II werkt op één fase. Heb je een 3-fase aansluiting en wil je op alle fasen opslaan en noodstroom, dan komen er **drie units**, één per fase. Die worden samen ingesteld als één systeem.

## Wat is ESS?

ESS staat voor **Energy Storage System**. Het is de werkstand van Victron voor een systeem dat aan het stroomnet hangt. In ESS doet het systeem in de basis dit:

1. Overdag levert je zonnepaneelomvormer stroom. Wat je huis niet direct gebruikt, gaat in de batterij.
2. 's Avonds en 's nachts levert de batterij stroom aan je huis, zodat je minder van het net afneemt.
3. Is de batterij vol, dan gaat het overschot het net op.

Je kunt in ESS onder meer kiezen of je vooral je eigen verbruik wilt optimaliseren, of dat de batterij altijd vol blijft als reserve voor stroomuitval.

### Dynamic ESS

Sinds Venus OS versie 3.30 (de software op het GX-apparaat) heeft Victron ook **Dynamic ESS**. Die stand plant het laden en ontladen op basis van **stroomprijzen, de verwachte zonneopbrengst en je verbruikspatroon**. Dat is vooral interessant als je een dynamisch energiecontract hebt. Lees daarover meer in [dynamisch contract en thuisbatterij](/artikel-dynamisch-contract-en-batterij).

## Hoe werkt een Victron-systeem naast je bestaande zonnepanelen?

Een Victron-systeem staat **AC-gekoppeld** naast je zonnepanelen. Je bestaande omvormer blijft gewoon zitten. Er is geen batterij-ingang op die omvormer nodig. De MultiPlus-II wordt op een eigen groep in de meterkast aangesloten en laadt de batterij met het overschot dat de meter ziet.

Bij Victron kan je zonnepaneelomvormer op twee plekken zitten:

| Plaats van je PV-omvormer | Bij stroomuitval |
|---|---|
| **Aan de netkant** (AC-in, gewoon in je groepenkast) | Je PV-omvormer valt uit, zoals altijd bij een storing. De batterij levert nog wel stroom aan de noodstroomgroepen. |
| **Achter de Victron** (op AC-out) | De Victron maakt zelf een stroomnet; je PV-omvormer kan blijven draaien en de batterij bijladen. |

De tweede optie klinkt aantrekkelijk, maar heeft grenzen. Victron werkt daarbij met de **factor 1.0-regel**: het vermogen van de zonnepanelen achter de Victron mag niet groter zijn dan wat de omvormer-lader aankan. De PV-omvormer moet ook goed reageren op de frequentie die de Victron gebruikt om hem terug te regelen als de batterij vol is. Dit vraagt nauwkeurig ontwerp. Meer over AC-koppeling in het algemeen lees je in [thuisbatterij bij bestaande zonnepanelen](/artikel-thuisbatterij-bij-bestaande-zonnepanelen).

## Hoe zit het met noodstroom?

Noodstroom is een sterk punt van Victron. De MultiPlus-II heeft een uitgang (AC-out) waar je groepen op aansluit die bij een storing moeten blijven werken. Valt het net weg, dan schakelt de MultiPlus-II **binnen ongeveer 20 milliseconden** om. Dat is zo snel dat de meeste apparaten, zoals een computer of router, gewoon doorwerken.

Let wel op:

- **Alleen de groepen op AC-out** krijgen noodstroom. Welke dat zijn, kies je bij de installatie.
- **Het vermogen is begrensd** door de omvormer. Grote verbruikers tegelijk (oven, kookplaat, warmtepomp) passen er vaak niet op.
- Bij 3-fase moet je kiezen hoe het systeem reageert als één fase wegvalt.

Meer over noodstroom in het algemeen lees je in [thuisbatterij met noodstroom](/artikel-thuisbatterij-noodstroom).

## Waarom is Victron populair bij techneuten en doe-het-zelvers?

- **Alles is uit te lezen en in te stellen.** Via het VRM-portaal en de app zie je elk detail. Het systeem is ook lokaal te koppelen aan bijvoorbeeld Home Assistant.
- **Vrije keuze in batterij.** Je bent niet gebonden aan één batterijmerk, zolang de batterij laagvolt is en met Victron communiceert.
- **Uitbreidbaar.** Je kunt later extra batterijen, units of laadregelaars toevoegen.
- **Veel documentatie en een grote community.** Handleidingen en forums zijn openbaar.

Op Nederlandse forums staan dan ook veel zelfbouwprojecten. Let op: een systeem dat aan het net hangt, moet voldoen aan de installatievoorschriften en de netcode. De instellingen moeten kloppen en het systeem moet worden aangemeld bij je netbeheerder.

## Victron of een kant-en-klaar hybride systeem?

| | Victron (ESS) | Kant-en-klaar hybride systeem |
|---|---|---|
| Opbouw | Losse onderdelen: omvormer-lader, GX, batterij, meter | Hybride omvormer en batterij als set |
| Batterijkeuze | Vrij, binnen laagvolt en compatibiliteit | Wat de fabrikant goedkeurt |
| Instellen | Veel opties, meer kennis nodig | Grotendeels voorgeprogrammeerd |
| Noodstroom | Sterk, snelle omschakeling | Verschilt per merk en model |
| Uitlezen en koppelen | Zeer uitgebreid | Meestal via de app van de fabrikant |
| Onderdelen en bekabeling | Meer | Minder |

Kort gezegd: Victron past bij je als je **zelf wilt meekijken, uitbreiden en finetunen**, of als **noodstroom** voor jou zwaar weegt. Wil je vooral een batterij die gewoon zijn werk doet, met weinig keuzes en één app, dan is een kant-en-klaar hybride systeem vaak eenvoudiger.

## Hoe Voltwijk helpt

Voltwijk werkt met een vaste combinatie: een Dyness LFP-batterij met een Solis hybride omvormer. Bij bestaande zonnepanelen zetten we die batterij met eigen omvormer AC-gekoppeld naast je huidige omvormer, van elk merk. Dat kan als pakket van 10 kWh / 5 kW 1-fase voor € 4.950, 16 kWh / 6 kW 1-fase voor € 5.450 of 16 kWh / 8 kW 3-fase voor € 5.950, alle prijzen excl. btw en inclusief installatie door onze eigen monteurs. Twijfel je tussen Victron en een kant-en-klaar systeem? Kijk bij "Bereken welke thuisbatterij past" of plan een gratis adviesgesprek. Meer over onze batterij lees je op de pagina [thuisbatterij](/product-batterij).

faq:
Q: Is Victron een Nederlands merk?
A: Ja. Victron Energy is in 1975 opgericht en gevestigd in Almere. Het bedrijf verkoopt wereldwijd, maar het hoofdkantoor staat in Nederland.
Q: Welke onderdelen heb je nodig voor een Victron thuisbatterij?
A: Een omvormer-lader (MultiPlus-II of Quattro), een GX-apparaat zoals de Cerbo GX, een 48V-batterij die met Victron kan communiceren en een energiemeter bij je netaansluiting. Bij 3-fase komen er drie omvormer-laders, één per fase.
Q: Kan een Victron-systeem naast mijn bestaande omvormer?
A: Ja. In de ESS-modus staat het systeem AC-gekoppeld naast je zonnepanelen. Je bestaande omvormer blijft zitten; de Victron laadt de batterij met het overschot dat de meter meet.
Q: Geeft een Victron thuisbatterij noodstroom?
A: Ja, op de groepen die op de uitgang (AC-out) van de MultiPlus-II zijn aangesloten. Bij een storing schakelt hij binnen ongeveer 20 milliseconden om. Het vermogen is wel begrensd door de omvormer.
Q: Werkt Victron met een dynamisch energiecontract?
A: Ja. Met Dynamic ESS plant het systeem laden en ontladen op basis van stroomprijzen, zonneverwachting en je verbruik. Daarvoor is Venus OS 3.30 of nieuwer nodig op het GX-apparaat.
Q: Kan ik een Victron thuisbatterij zelf installeren?
A: Veel techneuten bouwen zelf, maar een systeem aan het net moet voldoen aan de installatievoorschriften en de netcode, en worden aangemeld bij je netbeheerder. Laat het aansluiten op de meterkast door een vakkundige installateur doen.
