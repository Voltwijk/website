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
