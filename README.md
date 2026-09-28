# Voltwijk website

Statische website voor Voltwijk B.V. (thuisbatterijen, zonnepanelen, warmtepompen,
airco, elektrische boilers, laadpalen, meterkastaanpassingen). Gebouwd als losse
HTML-pagina's, bedoeld om als static site op Netlify te draaien onder voltwijk.nl.

## Structuur

- `index.html` — homepage (`/home` wordt via `netlify.toml` doorgestuurd naar `/`).
- `product-*.html` — losse productpagina's (airco, batterij, boiler, laadpaal,
  meterkast, warmtepomp, zonnepanelen).
- `artikel-*.html` — kennisbank-/bloginhoud (12 artikelen).
- Overige pagina's: `hoe-het-werkt.html`, `producten.html`, `reviews.html`,
  `garantie.html`, `over-ons.html`, `contact.html`, `bereken-je-prijs.html`,
  `inzichten.html`, `veelgestelde-vragen.html`, `algemene-voorwaarden.html`,
  `privacybeleid.html`, `cookiebeleid.html`.
- `images/` — alle foto's, logo's en keurmerken (voorheen als base64 in elke pagina
  ingebakken).
- `videos/` — klantreview-video's (mp4, al gecomprimeerd naar 1080p/h264, 2–6MB per
  stuk) + poster-JPG's. Gebruikt op de homepage, de airco-productpagina en de
  batterij-productpagina.

## Belangrijk: hoe deze site is opgebouwd

Dit is **geen build-systeem** — het zijn losse, op zichzelf staande HTML-bestanden.
Elke pagina bevat zijn eigen kopie van:
- de volledige navigatie/footer/WhatsApp-widget markup,
- het complete `PRODUCTS`-datablok (alle 7 producten, afbeeldingen via `/images/`),
- alle gedeelde CSS en JS-helpers (reveal-animaties, calculator, lead-formulieren, etc.)

Dat betekent: **een wijziging aan bijvoorbeeld het telefoonnummer, de navigatie, of
een productprijs moet los in alle 35 bestanden doorgevoerd worden.** Dit is de
grootste makkelijke verbetering die met een echte projectstructuur (shared
partials/includes, een build-stap die ze samenvoegt, of een framework als Astro/11ty)
opgelost kan worden.

## Bekende openstaande issues

1. **Geen refactor naar gedeelde componenten** — zie hierboven. Aanrader: eerst een
   simpele build-stap (bv. met een template-engine of gewoon een Node-script dat
   header/footer/PRODUCTS-data injecteert) voordat er nog veel meer content bij komt.

## Formulieren (Netlify Forms)

Alle formulieren versturen via Netlify Forms (`vwLeadSubmit` in elke pagina). De
formulierdefinities staan verborgen onderaan `index.html`:

| Formulier     | Waar                                   | Velden |
|---------------|----------------------------------------|--------|
| `contact`     | /contact, homepage                     | onderwerp, naam, email, telefoon, bericht |
| `terugbellen` | /contact (#terugbellen)                | naam, telefoon, moment |
| `offerte`     | prijscalculator (elke productpagina, /bereken-je-prijs, homepage) | naam, email, telefoon, postcode, huistype, producten, prijsindicatie |
| `nieuwsbrief` | footer                                 | email |
| `gids`        | homepage (#gids)                       | email |

Eenmalig in Netlify: **Forms → Enable form detection**, daarna opnieuw deployen, en
onder **Forms → Form notifications** een e-mailmelding instellen. Nieuwe velden moeten
ook in de verborgen definitie in `index.html` staan, anders negeert Netlify ze.

## Site-brede gegevens

- **Telefoonnummer**: 085 333 56 87 (`tel:+31853335687`), al correct verwerkt in
  header, footer en de floating call/WhatsApp-knop.
- **WhatsApp**: `https://wa.me/31853335687`
- **Adres**: Voltwijk B.V., Schoenmakerij 15a, 4762 AS Zevenbergen.
- **Domein**: voltwijk.nl, geregistreerd bij Vimexx, DNS al omgezet naar Netlify
  (A-record `@` → `75.2.60.5`, CNAME `www` → `apex-loadbalancer.netlify.com`).
  Mail-gerelateerde DNS-records (smtp/mail/pop/ftp + SPF/DKIM/DMARC) zijn ongemoeid
  gelaten zodat e-mail via Vimexx blijft werken.

## Deployen

Dit is een pure static site: geen build-commando nodig. In Netlify simpelweg de
publish directory op de root van deze map zetten (of `.`), zonder build command.

## Logo & huisstijl

Het logo is het woordmerk **VOLTWIJK** (Manrope Bold, omgezet naar vectoren) waarin de W bestaat uit twee V's — volt en wijk — met een koraalrood punt waar ze samenkomen. Losse bestanden staan in `brand/`:

| Bestand | Gebruik |
|---|---|
| `brand/voltwijk-logo.svg` | Woordmerk op lichte achtergrond |
| `brand/voltwijk-logo-wit.svg` | Woordmerk op donkere achtergrond |
| `brand/voltwijk-logo-zwart.svg` | Eénkleurig (stempel, gravure, borduren) |
| `brand/voltwijk-icoon.svg` / `-512.png` | Beeldmerk (de W) in vlak — profielfoto's, app-icoon |
| `brand/voltwijk-w.svg` | Beeldmerk zonder vlak |

Kleuren: inkt `#10201F`, teal `#0F6E6B`, mint `#6FD6C8`, koraal `#FF6B5B`. Favicons: `favicon.svg`, `favicon-32.png`, `favicon.ico`, `apple-touch-icon.png`.

## SEO & snelheid (tools/)

- `python3 tools/seo.py`: zet titels, meta descriptions, Open Graph en structured data (JSON-LD) op alle pagina's en maakt `sitemap.xml` opnieuw. Draai na nieuwe pagina's of prijswijzigingen (prijzen staan bovenin het script).
- `node tools/prerender-products.js` (lokale server op poort 8765): zet de productinhoud als statische HTML in `product-*.html`, voor Google en om verspringen te voorkomen. Draai na wijzigingen aan `PRODUCTS` of de productlayout.
- Afbeeldingen worden als `.webp` geladen; de `.jpg`-versies blijven voor deelafbeeldingen (Open Graph).

## Lokale pagina's (werkgebied)
`python3 tools/local_pages.py` bouwt `installateur-<plaats>.html` (14 plaatsen), het overzicht `/werkgebied`
en de WERKGEBIED-kolom in de footer van alle pagina's. Plaatsen en teksten staan in `CITIES` in het script;
gebruik alleen controleerbare feiten per plaats. Draai daarna `python3 tools/seo.py`.

## Indexeren
- Google: sitemap indienen en "Indexering aanvragen" in Search Console (kan alleen de eigenaar).
- Bing en andere zoekmachines: na een live deploy `python3 tools/indexnow.py` draaien (IndexNow).
- Search Console-gegevens: `python3 tools/gsc.py submit|sitemaps|report|inspect-all` met de sleutel van het
  service-account in `GSC_SERVICE_ACCOUNT_JSON` (zie de uitleg bovenin het script).

## Acties
- `python3 tools/energiescan.py [aan|vol|uit]` beheert de Gratis Energiescanweek Moerdijk: `/energiescan` (Netlify-formulier
  `energiescan`), `/energiescan-bedankt` (noindex) en de banner op de homepage. Daarna `python3 tools/seo.py`.
  Flyer, persbericht en Google-afbeelding staan in `brand/energiescan/`.

## Afspraken plannen (Cal.com)
`python3 tools/booking.py` zet de Cal.com-afspraakplanner (cal.com/voltwijk) op alle pagina's: knoppen met `data-book="huis|video|bel"` openen een venster met de agenda, na een offerte- of contactaanvraag verschijnt "Plan direct je gratis adviesgesprek" (naam en e-mail al ingevuld), en de contactpagina krijgt het blok `#afspraak`. Een geboekte afspraak telt in Google Analytics als `afspraak_gepland`. Links wijzigen? Pas `TYPES` bovenin het script aan en draai het opnieuw. Uitzetten: `python3 tools/booking.py uit`.

## Online bestellen (calculator)
`python3 tools/order.py` zet in stap 3 van de prijscalculator (homepage, /bereken-je-prijs en productpagina's) de knop "Bestel direct". De klant vult gegevens in, kiest een installatiedatum (ma–vr, vanaf 6 dagen) en doet een technische check (foto's of videocheck). De bestelling komt binnen via Netlify Forms als formulier `bestelling` (met foto's) en telt in Google Analytics als `bestelling_aangevraagd`. De klant betaalt nu niets; na de orderbevestiging volgt de aanbetaling (`AANBETALING`, nu € 350) via een betaallink, het restant na installatie.
Zet `CAL = True` zodra het Cal.com-afspraaktype `cal.com/voltwijk/installatie` bestaat: klanten kiezen dan een echte dag uit de agenda (max. 3 per dag, instellen in Cal.com) en de bestelling wordt na het boeken verstuurd.
`tools/order.py` zet ook op elke pagina de planbalk ("Installatie al vanaf …  Plan nu"), vult elk element met `data-vw-first` met de eerst mogelijke installatiedatum, en vinkt op een productpagina dat product alvast aan in de calculator. Klanten kunnen tot 8 foto's toevoegen (velden `foto_1` t/m `foto_8`, automatisch verkleind).

## Dagoverzicht per e-mail
`.github/workflows/dagoverzicht.yml` draait elke avond en stuurt om 23:00 (NL-tijd) via `tools/daily_report.py` een overzicht van de afgelopen 24 uur (23:00–23:00) naar info@voltwijk.nl: bezoekers, acties (bestellingen, afspraken, aanvragen), bezoeken per uur, bronnen, pagina's en, met `NETLIFY_TOKEN`, alle formulierinzendingen. Nodig in GitHub → Settings → Secrets and variables → Actions: `GA_SERVICE_ACCOUNT_JSON`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` (optioneel `NETLIFY_TOKEN`). Voorbeeld bekijken zonder te versturen: `python3 tools/daily_report.py --preview`. Losse cijfers: `python3 tools/ga.py report 556067391 7`.

## Dagelijkse blog
Elke ochtend schrijft een automatische Claude-sessie één artikel volgens `content/REDACTIE.md`, met onderwerpen uit `content/redactieplan.md` of actueel nieuws. Artikelen ondersteunen nu `date:`, `updated:` en `sources:` (bronnenlijst + datePublished in de structured data). Bouwen en controleren: `bash tools/publish.sh`.
