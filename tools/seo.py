# Zet titels, meta descriptions, Open Graph en structured data (JSON-LD) op alle pagina's
# en genereert sitemap.xml. Veilig om opnieuw te draaien.
import glob, re, json, html, datetime, os, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, 'tools'); sys.dont_write_bytecode = True
from battery import PAKKETTEN  # thuisbatterij-pakketten: één bron voor prijzen
SITE = 'https://voltwijk.nl'
TODAY = datetime.datetime.now(__import__('zoneinfo').ZoneInfo('Europe/Amsterdam')).date().isoformat()  # Nederlandse datum
BIZ_ID = SITE + '/#bedrijf'
T = {  # titel, description
 'index': ('Thuisbatterij, zonnepanelen en warmtepomp met vaste prijs | Voltwijk',
           'Thuisbatterij van 10 of 16 kWh vanaf € 3.900 excl. btw, inclusief installatie door eigen monteurs uit Zevenbergen. Ook zonnepanelen, airco en warmtepompen.'),
 'product-zonnepanelen': ('Zonnepanelen laten plaatsen – vanaf € 3.999 | Voltwijk',
           'Full-black zonnepanelen vanaf € 3.999 voor 12 panelen, inclusief installatie door eigen monteurs. Vaste prijs vooraf, 25 jaar productgarantie.'),
 'product-batterij': ('Thuisbatterij 10 of 16 kWh – vanaf € 3.900 | Voltwijk',
           'Thuisbatterij van 10 of 16 kWh met hybride omvormer, vanaf € 3.900 excl. btw, inclusief installatie. Bereken in 1 minuut welke batterij bij jouw verbruik past.'),
 'product-warmtepomp': ('Warmtepomp laten installeren – vanaf € 6.750 | Voltwijk',
           'Lucht/water-warmtepomp vanaf € 6.750 inclusief installatie. ISDE-subsidie direct verrekend, geplaatst door ons eigen team. Plan een gratis adviesgesprek.'),
 'product-airco': ('Airco laten installeren – vanaf € 1.899 | Voltwijk',
           'Split-unit airco vanaf € 1.899 inclusief installatie: koelen in de zomer, zuinig bijverwarmen in de tussenseizoenen. Vaste prijs vooraf.'),
 'product-boiler': ('Elektrische boiler laten installeren – vanaf € 1.199 | Voltwijk',
           'Elektrische boiler van 200 liter, energielabel A+, vanaf € 1.199 inclusief installatie. Warm water zonder gas, ideaal met zonnepanelen.'),
 'product-laadpaal': ('Laadpaal thuis laten installeren – vanaf € 1.299 | Voltwijk',
           'Slimme 11 kW laadpaal vanaf € 1.299 inclusief installatie. Laad op de goedkoopste uren, werkt met vrijwel elke elektrische auto.'),
 'product-meterkast': ('Meterkast aanpassen of verzwaren – vanaf € 649 | Voltwijk',
           'Meterkast aanpassen of uitbreiden vanaf € 649, klaar voor zonnepanelen, thuisbatterij, laadpaal of warmtepomp. NEN 1010, vaste prijs vooraf.'),
 'producten': ('Alle producten & vaste prijzen | Voltwijk',
           'Bekijk al onze producten met vaste prijzen inclusief installatie: zonnepanelen, thuisbatterij, warmtepomp, airco, elektrische boiler, laadpaal en meterkast.'),
}
T.update({  # kortere titels (Google toont ~60 tekens)
 'artikel-airco-als-bijverwarming': ('Airco als bijverwarming: bespaar je op gas? | Voltwijk', None),
 'artikel-capaciteitstarief-en-meterkast': ('Capaciteitstarief en je meterkast | Voltwijk', None),
 'artikel-dynamisch-contract-en-batterij': ('Dynamisch contract en thuisbatterij | Voltwijk', None),
 'artikel-elektrische-boiler-vs-gas': ('Elektrische boiler of gasboiler in 2026? | Voltwijk', None),
 'artikel-laadpaal-slim-laden': ('Laadpaal thuis: zo laad je slim en goedkoop | Voltwijk', None),
 'artikel-meterkast-onderschatte-stap': ('Meterkast: de vergeten stap bij batterij en laadpaal | Voltwijk',
   'Voordat een thuisbatterij of laadpaal geplaatst kan worden, moet je meterkast het aankunnen. Waarom deze stap zo vaak vergeten wordt.'),
 'artikel-salderingsregeling-2027': ('Salderingsregeling stopt in 2027: wat verandert er? | Voltwijk', None),
 'artikel-thuisbatterij-na-salderen': ('Thuisbatterij na het salderen: loont het? | Voltwijk', None),
 'artikel-waarom-je-monteur-ertoe-doet': ('Waarom je monteur ertoe doet: garantie en keurmerken | Voltwijk', None),
 'artikel-zonnepanelen-zonder-salderen-batterij-of-teruglevering': ('Zonnepanelen zonder salderen: batterij of terugleveren? | Voltwijk',
   'Nu salderen verdwijnt: haal je meer uit je zonnepanelen met een thuisbatterij, met terugleveren, of met allebei? Zo maak je de keuze.'),
 'cookiebeleid': ('Cookiebeleid | Voltwijk', 'Welke cookies Voltwijk gebruikt, waarvoor, en hoe je ze zelf beheert of uitzet. Geen advertentietracking.'),
})
PRODUCT = {  # slug: (naam, prijs, afbeelding)
 'product-zonnepanelen': ('Zonnepanelen (12 panelen)', 3999, 'zonnepanelen-installatie'),
 'product-batterij': ('Thuisbatterij', 3900, 'batterij-installatie'),
 'product-warmtepomp': ('Warmtepomp', 6750, 'warmtepomp-installatie'),
 'product-airco': ('Airconditioning', 1899, 'airco-installatie'),
 'product-boiler': ('Elektrische boiler', 1199, 'boiler-installatie'),
 'product-laadpaal': ('Laadpaal', 1299, 'laadpaal-installatie'),
 'product-meterkast': ('Meterkastaanpassing', 649, 'product-meterkast'),
}
BIZ = {
 "@context": "https://schema.org", "@type": ["HomeAndConstructionBusiness", "Electrician"], "@id": BIZ_ID,
 "name": "Voltwijk", "legalName": "Voltwijk B.V.", "url": SITE + "/",
 "logo": SITE + "/brand/voltwijk-icoon-512.png", "image": SITE + "/images/og-voltwijk.jpg",
 "telephone": "+31853335687", "email": "info@voltwijk.nl", "priceRange": "€€",
 "address": {"@type": "PostalAddress", "streetAddress": "Schoenmakerij 15a", "postalCode": "4762 AS",
             "addressLocality": "Zevenbergen", "addressCountry": "NL"},
 "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
   "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "09:00", "closes": "17:30"}],
 "areaServed": {"@type": "AdministrativeArea", "name": "West-Brabant"},
 "sameAs": ["https://instagram.com/voltwijk", "https://www.tiktok.com/@voltwijk"]
}
SELLER = {"@type": "HomeAndConstructionBusiness", "@id": BIZ_ID, "name": "Voltwijk", "url": SITE + "/"}
def future_draft(slug):  # artikel met een datum in de toekomst = concept, niet publiceren (zie articles.py)
    p = 'content/artikelen/' + slug + '.md'
    if not os.path.exists(p): return False
    m = re.search(r'^date:\s*(\S+)', open(p, encoding='utf-8').read(), re.M)
    return bool(m) and m.group(1) > TODAY

SIZES = '(max-width: 900px) 100vw, 760px'  # hoofdbeeld: schermbreed op mobiel, hooguit ~760px op desktop
def variants(src):
    """Kleinere webp-variant (1080 px breed) van een groot hoofdbeeld voor srcset; maakt hem aan als hij ontbreekt."""
    p = src.lstrip('/')
    if not p.endswith('.webp') or not os.path.exists(p): return []
    try: from PIL import Image
    except ImportError: return []
    im = Image.open(p); W, H = im.size; out = []
    for w in (1080,):
        if W < w + 160: continue
        vp = p[:-5] + '-%d.webp' % w
        if not os.path.exists(vp):
            im.convert('RGB').resize((w, round(H * w / W)), Image.LANCZOS).save(vp, 'WEBP', quality=80, method=6)
        out.append(('/' + vp, w))
    return out + [(src, W)] if out else []
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',',':')) + '</script>'
def text(s): return html.unescape(re.sub(r'<[^>]+>', ' ', s)).strip()
urls = []
for f in sorted(glob.glob('*.html')):
    slug = f[:-5]
    if slug == '404' or future_draft(slug): continue
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'\n?<!-- seo:start -->.*?<!-- seo:end -->', '', s, flags=re.S)
    url = SITE + ('/' if slug == 'index' else '/' + slug)
    if slug in T:
        t, d = T[slug]
        s = re.sub(r'<title>.*?</title>', '<title>' + html.escape(t, quote=False) + '</title>', s, count=1, flags=re.S)
        if d: s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + html.escape(d) + '">', s, count=1)
    title = text(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
    dm = re.search(r'<meta name="description" content="([^"]*)"', s); desc = html.unescape(dm.group(1)) if dm else ''
    if slug in PRODUCT: img = '/images/' + PRODUCT[slug][2] + '.jpg'
    elif slug.startswith('artikel-'):
        m = re.search(r'/images/([\w-]+)\.webp', s[s.find('<h1'):] if '<h1' in s else s)
        img = '/images/' + m.group(1) + '.jpg' if m and os.path.exists('images/' + m.group(1) + '.jpg') else '/images/og-voltwijk.jpg'
    else: img = '/images/og-voltwijk.jpg'
    tags = [
      '<meta property="og:type" content="%s">' % ('article' if slug.startswith('artikel-') else 'website'),
      '<meta property="og:site_name" content="Voltwijk">', '<meta property="og:locale" content="nl_NL">',
      '<meta property="og:title" content="%s">' % html.escape(title), '<meta property="og:description" content="%s">' % html.escape(desc),
      '<meta property="og:url" content="%s">' % url, '<meta property="og:image" content="%s">' % (SITE + img),
      '<meta name="twitter:card" content="summary_large_image">']
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
    data = []
    if slug == 'index':
        data += [BIZ, {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "name": "Voltwijk",
                       "url": SITE + "/", "inLanguage": "nl-NL", "publisher": {"@id": BIZ_ID}}]
    elif slug == 'contact':
        data.append(BIZ)
    if slug in PRODUCT:
        name, price, im = PRODUCT[slug]
        offer = {"@type": "Offer", "price": str(price), "priceCurrency": "EUR", "availability": "https://schema.org/InStock",
                 "url": url, "seller": SELLER}
        if slug == 'product-batterij':  # drie pakketten, prijzen uit tools/battery.py
            prijzen = [p['prijs'] for p in PAKKETTEN]
            offer = {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": str(min(prijzen)), "highPrice": str(max(prijzen)),
                     "offerCount": len(PAKKETTEN), "availability": "https://schema.org/InStock", "url": url, "seller": SELLER,
                     "offers": [{"@type": "Offer", "name": 'Thuisbatterij ' + p['naam'] + ' (' + p['fase'] + ')',
                                 "description": "Vaste prijs inclusief installatie, exclusief btw", "price": str(p['prijs']), "priceCurrency": "EUR", "priceSpecification": {"@type": "UnitPriceSpecification", "price": str(p['prijs']), "priceCurrency": "EUR", "valueAddedTaxIncluded": False},
                                 "availability": "https://schema.org/InStock", "url": url, "seller": SELLER} for p in PAKKETTEN]}
        data.append({"@context": "https://schema.org", "@type": "Product", "name": name, "description": desc,
          "image": SITE + '/images/' + im + '.jpg', "brand": {"@type": "Brand", "name": "Voltwijk"}, "offers": offer})
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Producten", "item": SITE + "/producten"})
        crumbs.append({"@type": "ListItem", "position": 3, "name": name, "item": url})
    elif slug.startswith('artikel-'):
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
        head = text(h1.group(1)) if h1 else title.replace(' — Voltwijk', '')
        data.append({"@context": "https://schema.org", "@type": "Article", "headline": head[:110], "description": desc,
          "image": SITE + img, "inLanguage": "nl-NL", "mainEntityOfPage": url,
          "author": {"@type": "Organization", "name": "Voltwijk", "url": SITE + "/"}, "publisher": SELLER})
        pub = re.search(r'<meta property="article:published_time" content="([^"]+)"', s)
        if pub:
            mod = re.search(r'<meta property="article:modified_time" content="([^"]+)"', s)
            data[-1]["datePublished"] = pub.group(1); data[-1]["dateModified"] = mod.group(1) if mod else pub.group(1)
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Inzichten", "item": SITE + "/inzichten"})
        crumbs.append({"@type": "ListItem", "position": 3, "name": head[:80], "item": url})
    elif slug.startswith('installateur-'):
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
        city = text(h1.group(1)).split(' in ', 1)[-1] if h1 else slug[13:]
        svc = {"@context": "https://schema.org", "@type": "Service", "name": text(h1.group(1)) if h1 else title,
          "serviceType": "Installatie van zonnepanelen, thuisbatterijen, warmtepompen en laadpalen", "description": desc,
          "provider": SELLER, "areaServed": {"@type": "City", "name": city}, "url": url}
        area = re.search(r'<h1[^>]*\bdata-area="([^"]*)"[^>]*\bdata-gemeente="([^"]*)"', s)
        if area:  # West-Brabant-pagina's (tools/local_pages.py): thuisbatterij voorop, plaats(en) binnen de gemeente
            pvm = re.search(r'<h1[^>]*\bdata-provincie="([^"]*)"', s)
            gem = {"@type": "AdministrativeArea", "name": "Gemeente " + html.unescape(area.group(2)),
                   "containedInPlace": {"@type": "AdministrativeArea", "name": html.unescape(pvm.group(1)) if pvm else "Noord-Brabant"}}
            places = [{"@type": "City", "name": html.unescape(a), "containedInPlace": gem} for a in area.group(1).split('|')]
            svc["serviceType"] = "Installatie van thuisbatterijen, zonnepanelen en airco's"
            svc["areaServed"] = places[0] if len(places) == 1 else places
            svc["offers"] = [{"@type": "Offer", "name": p["label"], "price": str(p["prijs"]), "priceCurrency": "EUR",
                              "url": SITE + "/product-batterij", "seller": SELLER} for p in PAKKETTEN]
        data.append(svc)
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Werkgebied", "item": SITE + "/werkgebied"})
        crumbs.append({"@type": "ListItem", "position": 3, "name": city, "item": url})
    elif re.search(r'<h1[^>]*\bdata-dienst=', s):  # product in een stad (tools/stadspaginas.py)
        m = re.search(r'<h1[^>]*\bdata-dienst="([^"]*)" data-plaats="([^"]*)" data-gemeente="([^"]*)" data-provincie="([^"]*)"', s)
        dienst, plaats, gem, pv = (html.unescape(x) for x in m.groups())
        data.append({"@context": "https://schema.org", "@type": "Service", "name": f"{dienst} in {plaats}", "serviceType": dienst,
          "description": desc, "provider": SELLER, "url": url,
          "areaServed": {"@type": "City", "name": plaats, "containedInPlace": {"@type": "AdministrativeArea", "name": "Gemeente " + gem,
                         "containedInPlace": {"@type": "AdministrativeArea", "name": pv}}}})
        pv_slug = '/werkgebied-' + re.sub(r'[^a-z0-9]+', '-', pv.lower()).strip('-')
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Werkgebied", "item": SITE + "/werkgebied"})
        crumbs.append({"@type": "ListItem", "position": 3, "name": pv, "item": SITE + pv_slug})
        crumbs.append({"@type": "ListItem", "position": 4, "name": f"{dienst} in {plaats}", "item": url})
    elif slug.startswith('werkgebied-'):
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Werkgebied", "item": SITE + "/werkgebied"})
        crumbs.append({"@type": "ListItem", "position": 3, "name": title.replace(' | Voltwijk', ''), "item": url})
    elif slug != 'index':
        crumbs.append({"@type": "ListItem", "position": 2, "name": title.replace(' — Voltwijk', '').replace(' | Voltwijk', ''), "item": url})
    if 'name="robots" content="noindex"' not in s:  # zichtbare FAQ's (uitklapvragen) als FAQPage
        qa = re.findall(r'<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>', re.sub(r'<script\b.*?</script>', '', s, flags=re.S), re.S)
        qa = [(text(q), text(a)) for q, a in qa if "'+" not in q and text(q) and text(a)]
        if qa:
            data.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    if len(crumbs) > 1:
        data.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs})
    # het hoofdbeeld (LCP) al laden terwijl de lange HTML nog binnenkomt
    lcp = re.search(r'<img\b[^>]*\bfetchpriority="high"[^>]*\bsrc="(/images/[^"\']+)"[^>]*>', re.sub(r'<script\b.*?</script>', '', s, flags=re.S))
    if lcp and 'rel="preload" as="image"' not in s:
        # productpagina's niet: daar tekent JavaScript het hoofdbeeld opnieuw (zonder srcset), dan zou het twee keer laden
        srcset = '' if slug in PRODUCT else ', '.join('%s %dw' % v for v in variants(lcp.group(1)))
        tag = lcp.group(0); new = re.sub(r'^<img srcset="[^"]*" sizes="[^"]*" ', '<img ', tag)
        if srcset: new = new.replace('<img ', '<img srcset="%s" sizes="%s" ' % (srcset, SIZES), 1)
        if new != tag and tag in s: s = s.replace(tag, new, 1)
        if srcset:
            tags.append('<link rel="preload" as="image" href="%s" imagesrcset="%s" imagesizes="%s" fetchpriority="high">' % (lcp.group(1), srcset, SIZES))
        else:
            tags.append('<link rel="preload" as="image" href="%s" fetchpriority="high">' % lcp.group(1))
    block = '\n<!-- seo:start -->\n' + '\n'.join(tags) + '\n' + '\n'.join(ld(x) for x in data) + '\n<!-- seo:end -->'
    s, k = re.subn(r'(<link rel="canonical"[^>]*>)', lambda m: m.group(1) + block, s, count=1)
    assert k == 1, f
    open(f, 'w', encoding='utf-8').write(s)
    pri = '1.0' if slug == 'index' else ('0.9' if slug in PRODUCT or slug in ('producten','thuisbatterij-berekenen') else ('0.8' if slug.startswith('installateur-') or slug.startswith('werkgebied') or re.match(r'(airco|zonnepanelen|thuisbatterij|warmtepomp)-', slug) else ('0.3' if slug in ('privacybeleid','cookiebeleid','algemene-voorwaarden') else '0.7')))
    if 'name="robots" content="noindex"' not in s: urls.append((url, pri))
with open('sitemap.xml', 'w', encoding='utf-8') as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u, p in urls: fh.write('  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (u, TODAY, p))
    fh.write('</urlset>\n')
print(len(urls), 'pages')
