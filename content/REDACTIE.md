# Redactie: elke dag één artikel op voltwijk.nl

Dit is de vaste werkwijze voor de dagelijkse blog. Volg hem stap voor stap. Doel: bovenaan Google komen op onderwerpen waar Voltwijk-klanten naar zoeken, en die lezers laten doorklikken naar "Bereken je prijs & plan direct".

## 1. Onderwerp kiezen (max. 10 minuten)

1. Lees `content/redactieplan.md`. Pak het bovenste onderwerp met status `open`, **tenzij** er actueel nieuws is dat voorgaat (zie hieronder).
2. Check actueel nieuws met WebSearch (2–3 zoekopdrachten, bijv. "salderen 2027 nieuws", "thuisbatterij nieuws", "warmtepomp subsidie nieuws", "netbeheerder nieuws huishoudens", "energiebelasting"). Actueel nieuws gaat voor als het:
   - van de afgelopen 7 dagen is,
   - direct gevolgen heeft voor huishoudens met zonnepanelen, thuisbatterij, warmtepomp, airco, boiler, laadpaal of meterkast,
   - nog niet in een bestaand artikel staat (`ls content/artikelen`, en zoek met grep op het kernwoord).
3. Lees `content/zoekdata.md` (elke nacht bijgewerkt uit Google Search Console). Staat onder "Kansen" een zoekwoord met duidelijk meer vertoningen dan de rest (en nog geen artikel dat precies die vraag beantwoordt), dan krijgt dat voorrang. Zolang de aantallen erg klein zijn (onder ~20 vertoningen), volg je gewoon het redactieplan.
4. **Nooit** een onderwerp kiezen dat al een artikel heeft. Wel mag je een bestaand artikel bijwerken als het verouderd is (zie stap 6).

Voorkeur (wat het snelst in Google scoort voor een jonge site):
- Specifieke vragen met koopintentie ("thuisbatterij 3-fase of 1-fase", "warmtepomp geluid buren").
- Lokaal + onderwerp ("netcongestie West-Brabant", "subsidie zonnepanelen Moerdijk" als die bestaat).
- Nieuws dat huishoudens raakt, uitgelegd in gewone taal, binnen 1–3 dagen na het nieuws.
- Niet: brede termen als "zonnepanelen" of "warmtepomp" (daar winnen grote sites).

## 2. Feiten verzamelen (de belangrijkste stap)

- Zoek elk feit, bedrag, percentage en elke datum na met WebSearch. Gebruik bij voorkeur officiële bronnen: rijksoverheid.nl, rvo.nl, belastingdienst.nl, acm.nl, netbeheernederland.nl, enexis.nl, liander.nl, stedin.net, consumentenbond.nl, milieucentraal.nl.
- **Een feit komt alleen in het artikel als minstens twee onafhankelijke bronnen het bevestigen, of één officiële bron.** Anders laat je het weg of schrijf je het algemeen ("de vergoeding verschilt per leverancier").
- Veel sites zijn via WebFetch niet bereikbaar; dan gelden de zoekresultaten van meerdere bronnen als bevestiging.
- Verzin nooit cijfers, reviews, klantverhalen, citaten of statistieken over Voltwijk. Toegestaan over Voltwijk: 12.500+ installaties, 4,7/5 op Google, eigen monteurs, vaste prijs inclusief installatie, 2 jaar garantie op de installatie, gevestigd in Zevenbergen.
- Prijzen van Voltwijk komen uit de calculator: thuisbatterij vanaf € 3.499, zonnepanelen vanaf € 3.999, warmtepomp vanaf € 6.750, airco vanaf € 1.899, boiler vanaf € 1.199, laadpaal vanaf € 1.299, meterkast vanaf € 649. Noem geen andere Voltwijk-prijzen.
- Noem de namen "Voltier" en "Zonne-installaties Noord" nooit.
- Geen negatieve uitspraken over concurrenten. Merken van apparaten neutraal noemen.

## 3. Schrijven

Bestand: `content/artikelen/artikel-<slug>.md` (slug: kort, met het zoekwoord, alleen a-z, 0-9 en streepjes).

```
title: <H1, bevat het zoekwoord, max. ~90 tekens>
seo_title: <max. 60 tekens, eindigt op " | Voltwijk">
description: <110–160 tekens, zoekwoord vooraan, belofte + wat de lezer leert>
category: <Nieuws | Thuisbatterij | Zonnepanelen | Warmtepomp | Airco | Boiler | Laadpaal | Meterkast>
product: <batterij | zonnepanelen | warmtepomp | airco | boiler | laadpaal | meterkast>
date: <vandaag, JJJJ-MM-DD>
lead: <2–3 zinnen: direct antwoord op de vraag>
summary: <4 kernpunten, gescheiden door ||>
sources: <Naam bron|https://url || Naam bron|https://url>
---
<tekst in markdown: ## koppen, lijsten, tabellen met |, **vet**, [interne link](/pad)>

faq:
Q: <vraag zoals mensen hem googelen>
A: <kort, compleet antwoord>
```

Regels:
- 900–1.500 woorden. Nederlands, je/jij, eerlijk en rustig, geen verkooppraatje. Korte zinnen.
- Beantwoord de hoofdvraag in de eerste alinea's. Elke `##`-kop is een vraag of duidelijke deelvraag (die komen in de inhoudsopgave).
- Minstens één tabel of stappenlijst als dat logisch is.
- 3–5 interne links naar bestaande artikelen of productpagina's (`/product-batterij` enz.). Alleen pagina's die bestaan.
- 4–6 FAQ's met de vragen die mensen echt stellen (kijk bij "Mensen vragen ook" in de zoekresultaten).
- Eindig met één korte alinea over hoe Voltwijk helpt (geen harde verkoop). De knop "Bereken je prijs & plan direct" komt er automatisch onder.
- `sources` is verplicht bij Nieuws en sterk aangeraden bij alle andere artikelen.

## 4. Bouwen en controleren

```
bash tools/publish.sh
```

Dat controleert alle artikelen (`tools/check_articles.py`) en bouwt de site. Faalt het, los de fout op en draai opnieuw.

Controleer daarna zelf:
- `git status`: alleen verwachte bestanden gewijzigd (nieuw .md, de nieuwe .html, inzichten.html, sitemap.xml, andere artikelpagina's i.v.m. "Meer over"-blok).
- Lees het artikel nog één keer kritisch: klopt elk getal met de bronnen? Staat er iets in wat niet onderbouwd is? Weghalen.

## 5. Publiceren

1. Werk `content/redactieplan.md` bij: zet het onderwerp op `klaar (<datum>, <slug>)` en voeg 1–2 nieuwe onderwerpideeën toe die je tegenkwam.
2. Commit met een duidelijke Engelse commitboodschap, push naar je werkbranch, maak een PR naar `main` in Voltwijk/website en merge die direct (de eigenaar heeft gevraagd alles direct te mergen).
3. Netlify publiceert automatisch.

## 6. Onderhoud (bij rustig nieuws, max. 1× per week in plaats van een nieuw artikel)

Werk een bestaand artikel bij als er iets veranderd is (nieuwe tarieven, regels, subsidiebedragen): pas de tekst aan, zet `updated: <datum>` in de kop, en publiceer zoals hierboven.
