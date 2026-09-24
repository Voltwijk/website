# Zet titels, meta descriptions, Open Graph en structured data (JSON-LD) op alle pagina's
# en genereert sitemap.xml. Veilig om opnieuw te draaien.
import glob, re, json, html, datetime, os
SITE = 'https://voltwijk.nl'
TODAY = datetime.date.today().isoformat()
BIZ_ID = SITE + '/#bedrijf'
T = {  # titel, description
 'index': ('Zonnepanelen, thuisbatterij & warmtepomp | Voltwijk',
           'Zonnepanelen, thuisbatterij, warmtepomp, airco of laadpaal met een vaste prijs vooraf, geïnstalleerd door ons eigen team. Bereken direct je prijs.'),
 'product-zonnepanelen': ('Zonnepanelen laten plaatsen – vanaf € 3.999 | Voltwijk',
           'Full-black zonnepanelen vanaf € 3.999 voor 12 panelen, inclusief installatie door eigen monteurs. Vaste prijs vooraf, 25 jaar productgarantie.'),
 'product-batterij': ('Thuisbatterij laten installeren – vanaf € 3.499 | Voltwijk',
           'Thuisbatterij vanaf € 3.499 inclusief installatie. Sla je zonnestroom op voor als salderen stopt in 2027. Vaste prijs, 10 jaar garantie.'),
 'product-warmtepomp': ('Warmtepomp laten installeren – vanaf € 6.750 | Voltwijk',
           'Lucht/water-warmtepomp vanaf € 6.750 inclusief installatie. ISDE-subsidie direct verrekend, geplaatst door ons eigen team. Bereken je prijs.'),
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
 'bereken-je-prijs': ('Bereken direct je vaste prijs | Voltwijk',
           'Vul je postcode en woningtype in en zie binnen een minuut je vaste prijs voor zonnepanelen, thuisbatterij, warmtepomp en meer, inclusief installatie.'),
}
PRODUCT = {  # slug: (naam, prijs, afbeelding)
 'product-zonnepanelen': ('Zonnepanelen (12 panelen)', 3999, 'zonnepanelen-installatie'),
 'product-batterij': ('Thuisbatterij', 3499, 'batterij-installatie'),
 'product-warmtepomp': ('Warmtepomp', 6750, 'warmtepomp-installatie'),
 'product-airco': ('Airconditioning', 1899, 'airco-installatie'),
 'product-boiler': ('Elektrische boiler', 1199, 'boiler-installatie'),
 'product-laadpaal': ('Laadpaal', 1299, 'laadpaal-installatie'),
 'product-meterkast': ('Meterkastaanpassing', 649, 'product-meterkast'),
}
BIZ = {
 "@context": "https://schema.org", "@type": "Electrician", "@id": BIZ_ID,
 "name": "Voltwijk", "legalName": "Voltwijk B.V.", "url": SITE + "/",
 "logo": SITE + "/brand/voltwijk-icoon-512.png", "image": SITE + "/images/og-voltwijk.jpg",
 "telephone": "+31853335687", "email": "info@voltwijk.nl", "priceRange": "€€",
 "address": {"@type": "PostalAddress", "streetAddress": "Schoenmakerij 15a", "postalCode": "4762 AS",
             "addressLocality": "Zevenbergen", "addressCountry": "NL"},
 "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
   "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "09:00", "closes": "17:30"}],
 "sameAs": ["https://instagram.com/voltwijk", "https://www.tiktok.com/@voltwijk"]
}
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',',':')) + '</script>'
def text(s): return html.unescape(re.sub(r'<[^>]+>', ' ', s)).strip()
urls = []
for f in sorted(glob.glob('*.html')):
    slug = f[:-5]
    if slug == '404': continue
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'\n?<!-- seo:start -->.*?<!-- seo:end -->', '', s, flags=re.S)
    url = SITE + ('/' if slug == 'index' else '/' + slug)
    if slug in T:
        t, d = T[slug]
        s = re.sub(r'<title>.*?</title>', '<title>' + html.escape(t, quote=False) + '</title>', s, count=1, flags=re.S)
        s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + html.escape(d) + '">', s, count=1)
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
        data.append({"@context": "https://schema.org", "@type": "Product", "name": name, "description": desc,
          "image": SITE + '/images/' + im + '.jpg', "brand": {"@type": "Brand", "name": "Voltwijk"},
          "offers": {"@type": "Offer", "price": str(price), "priceCurrency": "EUR", "availability": "https://schema.org/InStock",
                     "url": url, "seller": {"@id": BIZ_ID}}})
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Producten", "item": SITE + "/producten"})
        crumbs.append({"@type": "ListItem", "position": 3, "name": name, "item": url})
    elif slug.startswith('artikel-'):
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
        head = text(h1.group(1)) if h1 else title.replace(' — Voltwijk', '')
        data.append({"@context": "https://schema.org", "@type": "Article", "headline": head[:110], "description": desc,
          "image": SITE + img, "inLanguage": "nl-NL", "mainEntityOfPage": url,
          "author": {"@type": "Organization", "name": "Voltwijk", "url": SITE + "/"}, "publisher": {"@id": BIZ_ID}})
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Inzichten", "item": SITE + "/inzichten"})
        crumbs.append({"@type": "ListItem", "position": 3, "name": head[:80], "item": url})
    elif slug != 'index':
        crumbs.append({"@type": "ListItem", "position": 2, "name": title.replace(' — Voltwijk', '').replace(' | Voltwijk', ''), "item": url})
    if slug == 'veelgestelde-vragen':
        qa = re.findall(r'<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>', s, re.S)
        qa = [(text(q), text(a)) for q, a in qa if "'+" not in q]
        if qa:
            data.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    if len(crumbs) > 1:
        data.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs})
    block = '\n<!-- seo:start -->\n' + '\n'.join(tags) + '\n' + '\n'.join(ld(x) for x in data) + '\n<!-- seo:end -->'
    s, k = re.subn(r'(<link rel="canonical"[^>]*>)', lambda m: m.group(1) + block, s, count=1)
    assert k == 1, f
    open(f, 'w', encoding='utf-8').write(s)
    pri = '1.0' if slug == 'index' else ('0.9' if slug in PRODUCT or slug in ('producten','bereken-je-prijs') else ('0.3' if slug in ('privacybeleid','cookiebeleid','algemene-voorwaarden') else '0.7'))
    urls.append((url, pri))
with open('sitemap.xml', 'w', encoding='utf-8') as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u, p in urls: fh.write('  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (u, TODAY, p))
    fh.write('</urlset>\n')
print(len(urls), 'pages')
