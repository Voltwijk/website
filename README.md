# Voltwijk website

Statische website voor Voltwijk B.V. (thuisbatterijen, zonnepanelen, warmtepompen,
airco, elektrische boilers, laadpalen, meterkastaanpassingen). Gebouwd als losse
HTML-pagina's, bedoeld om als static site op Netlify te draaien onder voltwijk.nl.

## Structuur

- `index.html` / `home.html` — homepage (identieke kopie; Netlify serveert `index.html`
  als root, `home.html` staat er ook zodat interne links naar "home" blijven werken).
- `product-*.html` — losse productpagina's (airco, batterij, boiler, laadpaal,
  meterkast, warmtepomp, zonnepanelen).
- `artikel-*.html` — kennisbank-/bloginhoud (12 artikelen).
- Overige pagina's: `hoe-het-werkt.html`, `producten.html`, `reviews.html`,
  `garantie.html`, `over-ons.html`, `contact.html`, `bereken-je-prijs.html`,
  `inzichten.html`, `veelgestelde-vragen.html`, `algemene-voorwaarden.html`,
  `privacybeleid.html`, `cookiebeleid.html`.
- `videos/` — klantreview-video's (mp4, al gecomprimeerd naar 1080p/h264, 2–6MB per
  stuk) + poster-JPG's. Gebruikt op de homepage, de airco-productpagina en de
  batterij-productpagina.

## Belangrijk: hoe deze site is opgebouwd

Dit is **geen build-systeem** — het zijn losse, op zichzelf staande HTML-bestanden.
Elke pagina bevat zijn eigen kopie van:
- de volledige navigatie/footer/WhatsApp-widget markup,
- het complete `PRODUCTS`-datablok (alle 7 producten, inclusief base64-afbeeldingen),
- alle gedeelde CSS en JS-helpers (reveal-animaties, calculator, lead-formulieren, etc.)

Dat betekent: **een wijziging aan bijvoorbeeld het telefoonnummer, de navigatie, of
een productprijs moet los in alle 35 bestanden doorgevoerd worden.** Dit is de
grootste makkelijke verbetering die met een echte projectstructuur (shared
partials/includes, een build-stap die ze samenvoegt, of een framework als Astro/11ty)
opgelost kan worden.

## Bekende openstaande issues

1. **5 kapotte afbeeldingen in de "Hoe het werkt"-sectie**, in `hoe-het-werkt.html`
   én gedupliceerd in `home.html`/`index.html`. Ze verwijzen naar
   `/_blob/<hash>`-paden — dat was een Claude-artifact-intern asset-formaat dat nooit
   met echte bestanden is gevuld, dus de `<img>`-tags zijn kapot. De 5 stappen zijn:
   1. Besparingscheck
   2. Adviesgesprek
   3. Aanbod & planning
   4. Installatie
   5. Klaar voor de toekomst

   Zoek naar `_blob/` in deze bestanden om de exacte `<img data-img="...">`
   / `media:{type:'img', src:'...'}`-plekken te vinden. Er zijn nog geen echte foto's
   voor deze stappen aangeleverd — de klant levert die zelf aan.

2. **Overige productfoto's**: de meeste productfoto's (in `PRODUCTS.<slug>.image`)
   zijn al echte, werkende base64-afbeeldingen. Alleen de 5 "hoe het werkt"-stappen
   hierboven zijn nog kapot.

3. **Geen refactor naar gedeelde componenten** — zie hierboven. Aanrader: eerst een
   simpele build-stap (bv. met een template-engine of gewoon een Node-script dat
   header/footer/PRODUCTS-data injecteert) voordat er nog veel meer content bij komt.

## Site-brede gegevens

- **Telefoonnummer**: 085 333 56 87 (`tel:+31853335687`), al correct verwerkt in
  header, footer en de floating call/WhatsApp-knop.
- **WhatsApp**: `https://wa.me/31853335687`
- **Adres**: Voltwijk B.V., Schoenmakerij 18a, 4762 AS Zevenbergen.
- **Domein**: voltwijk.nl, geregistreerd bij Vimexx, DNS al omgezet naar Netlify
  (A-record `@` → `75.2.60.5`, CNAME `www` → `apex-loadbalancer.netlify.com`).
  Mail-gerelateerde DNS-records (smtp/mail/pop/ftp + SPF/DKIM/DMARC) zijn ongemoeid
  gelaten zodat e-mail via Vimexx blijft werken.

## Deployen

Dit is een pure static site: geen build-commando nodig. In Netlify simpelweg de
publish directory op de root van deze map zetten (of `.`), zonder build command.
