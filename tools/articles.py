# Bouwt artikelpagina's uit content/artikelen/*.md, voegt "Lees ook"-blokken toe aan alle
# artikelen en bouwt het overzicht op /inzichten opnieuw op. Veilig om opnieuw te draaien.
# Daarna altijd: python3 tools/seo.py  (titels/OG/JSON-LD/sitemap)
import glob, re, html, os, math, json
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)
SHELL = 'artikel-isde-subsidie-2026.html'
PRODUCTS = {
 'batterij': ('Thuisbatterij', 'vanaf € 3.499', '/product-batterij', '/images/thumb-batterij.webp'),
 'zonnepanelen': ('Zonnepanelen', 'vanaf € 3.999', '/product-zonnepanelen', '/images/thumb-zonnepanelen.webp'),
 'warmtepomp': ('Warmtepomp', 'vanaf € 6.750', '/product-warmtepomp', '/images/thumb-warmtepomp.webp'),
 'airco': ('Airconditioning', 'vanaf € 1.899', '/product-airco', '/images/thumb-airco.webp'),
 'boiler': ('Elektrische boiler', 'vanaf € 1.199', '/product-boiler', '/images/thumb-boiler.webp'),
 'laadpaal': ('Laadpaal', 'vanaf € 1.299', '/product-laadpaal', '/images/thumb-laadpaal.webp'),
 'meterkast': ('Meterkastaanpassing', 'vanaf € 649', '/product-meterkast', '/images/thumb-meterkast.webp'),
}
CATLABEL = {'batterij':'Thuisbatterij','zonnepanelen':'Zonnepanelen','warmtepomp':'Warmtepomp','airco':'Airco','boiler':'Boiler','laadpaal':'Laadpaal','meterkast':'Meterkast','algemeen':'Algemeen'}
HERO = {  # afwisselende beelden per product
 'batterij': ['batterij-installatie','batterij-zolder','product-batterij'],
 'zonnepanelen': ['zonnepanelen-installatie','zonnepanelen-dak','artikel-zonnepanelen-prijs'],
 'warmtepomp': ['warmtepomp-installatie','warmtepomp-tuinmuur','warmtepomp-app'],
 'airco': ['airco-installatie','airco-sfeer','product-airco'],
 'boiler': ['boiler-installatie','product-boiler','hoe-het-werkt-3-v2'],
 'laadpaal': ['laadpaal-installatie','product-laadpaal','hoe-het-werkt-2'],
 'meterkast': ['monteur-aan-het-werk','product-meterkast','monteur-en-klant'],
}
# bestaande (handgeschreven) artikelen: product-koppeling
EXISTING = {
 'artikel-thuisbatterij-na-salderen':'batterij', 'artikel-dynamisch-contract-en-batterij':'batterij',
 'artikel-salderingsregeling-2027':'zonnepanelen', 'artikel-zonnepanelen-zonder-salderen-batterij-of-teruglevering':'zonnepanelen',
 'artikel-zonnepanelen-prijs':'zonnepanelen', 'artikel-isde-subsidie-2026':'warmtepomp', 'artikel-warmtepomp-geluid':'warmtepomp',
 'artikel-warmtepomp-sturing':'warmtepomp', 'artikel-vergelijking':'warmtepomp', 'artikel-airco-als-bijverwarming':'airco',
 'artikel-elektrische-boiler-vs-gas':'boiler', 'artikel-laadpaal-slim-laden':'laadpaal', 'artikel-meterkast-onderschatte-stap':'meterkast',
 'artikel-capaciteitstarief-en-meterkast':'meterkast', 'artikel-waarom-je-monteur-ertoe-doet':'algemeen',
}
ALSO = {  # extra relevantie over productgrenzen heen
 'artikel-salderingsregeling-2027':['batterij'], 'artikel-zonnepanelen-zonder-salderen-batterij-of-teruglevering':['batterij'],
 'artikel-vergelijking':['airco','boiler'], 'artikel-meterkast-onderschatte-stap':['batterij','laadpaal'],
 'artikel-capaciteitstarief-en-meterkast':['laadpaal','warmtepomp'], 'artikel-boiler-opwarmen-met-zonnestroom':['zonnepanelen'],
 'artikel-ems-energiemanagementsysteem-thuisbatterij':['zonnepanelen'], 'artikel-3-fase-aansluiting-aanvragen':['laadpaal','warmtepomp'],
 'artikel-load-balancing-laadpaal':['meterkast'], 'artikel-1-fase-of-3-fase-laden':['meterkast'],
 'artikel-btw-thuisbatterij-terugvragen':['zonnepanelen'], 'artikel-btw-zonnepanelen-nultarief':['batterij'],
 'artikel-warmtepompboiler-of-elektrische-boiler':['warmtepomp'], 'artikel-groepenkast-aardlekschakelaars-uitgelegd':['laadpaal'],
}
esc = lambda s: html.escape(s, quote=True)

def inline(t):
    t = esc(t).replace('&#x27;', "'")
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\[([^\]]+)\]\((/[^)\s]*)\)', r'<a href="\2">\1</a>', t)
    return t

def slugify(t):
    t = t.lower()
    for a, b in (('ë','e'),('é','e'),('è','e'),('ï','i'),('ö','o'),('ü','u'),('à','a'),('€','euro')): t = t.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:60]

def md(body):
    out, toc, i = [], [], 0
    lines = body.split('\n')
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.startswith('## '):
            h = l[3:].strip(); a = slugify(h); toc.append((a, h)); out.append(f'<h2 id="{a}">{inline(h)}</h2>'); i += 1; continue
        if l.startswith('### '):
            out.append(f'<h3>{inline(l[4:].strip())}</h3>'); i += 1; continue
        if l.startswith('> '):
            out.append(f'<div class="art-callout">{inline(l[2:].strip())}</div>'); i += 1; continue
        if l.lstrip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            rows = [r for r in rows if not all(re.fullmatch(r':?-{2,}:?', c) for c in r)]
            th = ''.join(f'<th>{inline(c)}</th>' for c in rows[0])
            tb = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in rows[1:])
            out.append(f'<div class="art-table"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'); continue
        if re.match(r'^\s*(- |\d+\. )', l):
            ordered = bool(re.match(r'^\s*\d+\. ', l)); items = []
            while i < len(lines) and re.match(r'^\s*(- |\d+\. )', lines[i]):
                items.append(re.sub(r'^\s*(- |\d+\. )', '', lines[i])); i += 1
            tag = 'ol' if ordered else 'ul'
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>'); continue
        para = [l.strip()]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#|>|\||\s*- |\s*\d+\. )', lines[i]):
            para.append(lines[i].strip()); i += 1
        out.append(f'<p>{inline(" ".join(para))}</p>')
    return '\n'.join(out), toc

def parse(path):
    raw = open(path, encoding='utf-8').read().replace('\r', '')
    head, body = raw.split('\n---\n', 1)
    meta = {}
    for l in head.strip().split('\n'):
        if ':' in l: k, v = l.split(':', 1); meta[k.strip()] = v.strip()
    faq = []
    if re.search(r'^faq:\s*$', body, re.M):
        body, fq = re.split(r'^faq:\s*$', body, maxsplit=1, flags=re.M)
        for m in re.finditer(r'^Q:\s*(.+?)\s*\nA:\s*(.+?)(?=\nQ:|\Z)', fq.strip(), re.S | re.M):
            faq.append((m.group(1).strip(), ' '.join(m.group(2).split())))
    meta['slug'] = os.path.basename(path)[:-3]
    meta['body'], meta['faq'] = body.strip(), faq
    return meta

ARTCSS = '''<style>
.art-body{font-size:16px;color:var(--ink-soft);line-height:1.75;}
.art-body p{margin:0 0 18px;}
.art-body h2{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:24px;line-height:1.3;color:var(--ink);margin:44px 0 14px;scroll-margin-top:96px;}
.art-body h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:18px;color:var(--ink);margin:28px 0 10px;}
.art-body ul,.art-body ol{padding-left:22px;margin:0 0 18px;} .art-body li{margin-bottom:8px;}
.art-body a{color:var(--primary);font-weight:700;text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px;}
.art-body strong{color:var(--ink);}
.art-callout{margin:24px 0;padding:18px 22px;border-radius:14px;background:var(--surface-tint);color:var(--ink);font-size:15px;line-height:1.6;border-left:4px solid var(--primary);}
.art-table{overflow-x:auto;margin:22px 0;border-radius:14px;border:1px solid var(--border);background:#fff;}
.art-table table{border-collapse:collapse;width:100%;font-size:14px;min-width:460px;}
.art-table th{background:var(--surface-tint);color:var(--ink);text-align:left;padding:11px 14px;font-weight:700;}
.art-table td{padding:10px 14px;border-top:1px solid var(--border);vertical-align:top;}
.art-sum{margin:30px 0 8px;padding:22px 24px;border-radius:18px;background:var(--dark);color:#fff;}
.art-sum .t{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:700;font-size:15px;color:var(--mint);letter-spacing:.02em;}
.art-sum ul{margin:10px 0 0;padding-left:20px;color:#DDE7E5;font-size:15px;line-height:1.6;} .art-sum li{margin-bottom:6px;}
.art-toc{margin:22px 0 6px;padding:18px 22px;border:1px solid var(--border);border-radius:16px;background:#fff;}
.art-toc .t{font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);}
.art-toc ol{margin:10px 0 0;padding-left:20px;font-size:14.5px;line-height:1.5;} .art-toc li{margin-bottom:6px;}
.art-toc a{color:var(--ink);text-decoration:none;} .art-toc a:hover{color:var(--primary);text-decoration:underline;}
.art-faq{margin-top:44px;} .art-faq h2{margin-top:0;}
.rel-wrap{padding-top:8px;padding-bottom:72px;}
.rel-prod{display:flex;align-items:center;gap:18px;padding:18px;border-radius:18px;background:#fff;border:1px solid var(--border);text-decoration:none;color:var(--ink);transition:transform .2s,box-shadow .2s;}
.rel-prod:hover{transform:translateY(-2px);box-shadow:0 18px 34px -24px rgba(16,32,31,.45);}
.rel-prod img{width:84px;height:84px;border-radius:12px;object-fit:cover;flex-shrink:0;background:var(--bg);}
.rel-prod .k{font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--primary);}
.rel-prod .n{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:700;font-size:18px;margin-top:2px;}
.rel-prod .p{font-size:13.5px;color:var(--ink-soft);margin-top:2px;}
.rel-prod .go{margin-left:auto;font-weight:800;color:var(--primary);font-size:14px;white-space:nowrap;}
.rel-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin-top:16px;}
.rel-list a{display:block;padding:16px 18px;border-radius:14px;background:#fff;border:1px solid var(--border);text-decoration:none;color:var(--ink);font-weight:700;font-size:14.5px;line-height:1.4;transition:border-color .2s,transform .2s;}
.rel-list a:hover{border-color:var(--primary);transform:translateY(-2px);}
.rel-list a span{display:block;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--primary);margin-bottom:6px;}
@media (max-width:560px){ .rel-prod{flex-wrap:wrap;} .rel-prod .go{margin-left:0;} .art-body{font-size:15.5px;} }
</style>'''

def build_page(a, shell, catalog):
    prod = a['product']; pname, price, purl, pthumb = PRODUCTS[prod]
    same = [c for c in catalog if c['product'] == prod]
    img = HERO[prod][same.index(next(c for c in same if c['slug'] == a['slug'])) % len(HERO[prod])]
    body, toc = md(a['body'])
    words = len(re.sub(r'<[^>]+>', ' ', body).split()) + sum(len((q + ' ' + x).split()) for q, x in a['faq'])
    mins = max(3, math.ceil(words / 200))
    summ = ''.join(f'<li>{inline(x.strip())}</li>' for x in a.get('summary', '').split('||') if x.strip())
    tocs = ''.join(f'<li><a href="#{i}">{inline(h)}</a></li>' for i, h in toc)
    faq = ''
    if a['faq']:
        faq = '<div class="art-faq"><h2 id="veelgestelde-vragen">Veelgestelde vragen</h2><div class="faq" style="margin-top:14px;">' + ''.join(
            f'<details><summary>{inline(q)}</summary><p>{inline(x)}</p></details>' for q, x in a['faq']) + '</div></div>'
    main = f'''<div class="blk-light" style="padding-top:40px;">
  {ARTCSS}
  <div class="wrap reveal" style="max-width:760px;padding-top:48px;padding-bottom:0;">
    <nav aria-label="Kruimelpad" style="font-size:13px;font-weight:700;color:var(--ink-faint);display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
      <a href="/inzichten" style="color:var(--primary);text-decoration:none;">Inzichten</a><span aria-hidden="true">/</span>
      <a href="/inzichten#{prod}" style="color:var(--primary);text-decoration:none;">{CATLABEL[prod]}</a>
    </nav>
    <div class="pill" style="margin-top:18px;">{esc(a.get('category', CATLABEL[prod]))}</div>
    <h1 class="vw-heading" style="font-size:clamp(28px,4.4vw,40px);margin-top:14px;line-height:1.2;">{inline(a['title'])}</h1>
    <p style="font-size:17px;color:var(--ink-soft);margin-top:14px;line-height:1.6;max-width:640px;">{inline(a.get('lead', ''))}</p>
    <div style="margin-top:16px;font-size:12.5px;color:var(--ink-soft);">Inzichten · {esc(CATLABEL[prod])} · {mins} min leestijd</div>
  </div>
  <div class="wrap reveal" style="max-width:760px;padding-top:28px;">
    <div style="border-radius:20px;overflow:hidden;aspect-ratio:16/9;background:var(--bg);"><img fetchpriority="high" src="/images/{img}.webp" alt="{esc(a['title'])}" style="width:100%;height:100%;object-fit:cover;display:block;"></div>
  </div>
  <div class="wrap" style="max-width:700px;padding-top:8px;padding-bottom:40px;">
    {'<div class="art-sum"><div class="t">In het kort</div><ul>' + summ + '</ul></div>' if summ else ''}
    {'<nav class="art-toc" aria-label="Inhoud"><div class="t">In dit artikel</div><ol>' + tocs + ('<li><a href="#veelgestelde-vragen">Veelgestelde vragen</a></li>' if faq else '') + '</ol></nav>' if len(toc) > 2 else ''}
    <article class="art-body" style="margin-top:28px;">
{body}
    </article>
    {faq}
  </div>
</div>
'''
    s = shell
    s = re.sub(r'<div class="blk-light" style="padding-top:40px;">.*?(?=<div class="site-footer")', lambda m: main + '\n\n', s, count=1, flags=re.S)
    s = re.sub(r'<title>.*?</title>', '<title>' + esc(a.get('seo_title') or a['title'] + ' | Voltwijk') + '</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + esc(a['description']) + '">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://voltwijk.nl/{a["slug"]}">', s, count=1)
    s = re.sub(r'\n?<!-- seo:start -->.*?<!-- seo:end -->', '', s, flags=re.S)
    s = re.sub(r'\n?<!-- rel:start -->.*?<!-- rel:end -->', '', s, flags=re.S)
    return s

def related_block(slug, prod, catalog):
    if prod == 'algemeen':
        pool = [c for c in catalog if c['slug'] != slug][:6]; card = ''
    else:
        pname, price, purl, pthumb = PRODUCTS[prod]
        prim = [c for c in catalog if c['product'] == prod and c['slug'] != slug]
        sec = [c for c in catalog if prod in c.get('also', []) and c['slug'] != slug and c not in prim]
        pool = (prim + sec)[:6]
        card = f'''<a class="rel-prod" href="{purl}"><img loading="lazy" decoding="async" src="{pthumb}" alt="{esc(pname)}"><div><div class="k">Direct regelen</div><div class="n">{esc(pname)} · {esc(price)}</div><div class="p">Vaste prijs, inclusief installatie door ons eigen team.</div></div><span class="go">Bekijk {esc(pname.lower())} →</span></a>'''
    items = ''.join(f'<a href="/{c["slug"]}"><span>{esc(CATLABEL[c["product"]])}</span>{esc(c["title"])}</a>' for c in pool)
    lab = 'Lees ook' if prod == 'algemeen' else 'Meer over ' + CATLABEL[prod].lower()
    return f'''<!-- rel:start --><div class="blk-light"><div class="wrap rel-wrap" style="max-width:760px;">{card}
<h2 class="vw-heading" style="font-size:22px;margin-top:40px;">{esc(lab)}</h2><div class="rel-list">{items}</div>
<p style="margin-top:18px;font-size:14px;"><a href="/inzichten{'#' + prod if prod != 'algemeen' else ''}" style="color:var(--primary);font-weight:800;text-decoration:none;">Alle artikelen{'' if prod == 'algemeen' else ' over ' + esc(CATLABEL[prod].lower())} →</a></p></div></div><!-- rel:end -->
'''

def card_html(c):
    return f'''<a href="/{c['slug']}" class="card tilt-card ins-card" data-cat="{c['product']}" style="padding:0;overflow:hidden;text-decoration:none;color:inherit;">
          <div style="aspect-ratio:4/3;overflow:hidden;background:var(--bg);"><img loading="lazy" decoding="async" src="{c['img']}" alt="{esc(c['title'])}" style="width:100%;height:100%;object-fit:cover;display:block;"></div>
          <div style="padding:20px 22px 24px;">
            <div style="font-size:11px;font-weight:700;letter-spacing:.05em;color:var(--primary);text-transform:uppercase;">{esc(CATLABEL[c['product']])}</div>
            <h3 class="vw-heading" style="font-size:16.5px;margin-top:8px;line-height:1.35;">{esc(c['title'])}</h3>
            <p style="font-size:13px;color:var(--ink-soft);margin-top:10px;line-height:1.55;">{esc(c['excerpt'])}</p>
            <span style="margin-top:14px;display:inline-flex;align-items:center;gap:6px;font-weight:700;font-size:13px;color:var(--primary);">Lees meer →</span>
          </div>
        </a>'''

def main():
    shell = open(SHELL, encoding='utf-8').read()
    new = [parse(p) for p in sorted(glob.glob('content/artikelen/*.md'))]
    catalog = []
    # bestaande artikelen: titel + beeld + samenvatting uit hun eigen pagina
    for slug, prod in EXISTING.items():
        s = open(slug + '.html', encoding='utf-8').read()
        t = html.unescape(re.sub(r'<[^>]+>', '', re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1))).strip()
        lead = re.search(r'</h1>\s*<p[^>]*>(.*?)</p>', s, re.S)
        im = re.search(r'<img[^>]*src="(/images/[^"]+)"', s[s.find('</h1>'):])
        catalog.append({'slug': slug, 'product': prod, 'title': t, 'excerpt': html.unescape(re.sub(r'<[^>]+>', '', lead.group(1))).strip() if lead else '',
                        'img': im.group(1) if im else '/images/og-voltwijk.jpg', 'also': ALSO.get(slug, []), 'new': False})
    for a in new:
        catalog.append({'slug': a['slug'], 'product': a['product'], 'title': a['title'], 'excerpt': a['description'], 'also': ALSO.get(a['slug'], []), 'new': True})
    for a in new:  # beeld per nieuw artikel (moet na catalogus-opbouw)
        same = [c for c in catalog if c['product'] == a['product']]
        idx = same.index(next(c for c in same if c['slug'] == a['slug']))
        next(c for c in catalog if c['slug'] == a['slug'])['img'] = '/images/' + HERO[a['product']][idx % len(HERO[a['product']])] + '.webp'
    # nieuwe pagina's schrijven
    for a in new:
        open(a['slug'] + '.html', 'w', encoding='utf-8').write(build_page(a, shell, catalog))
    # "Meer over ..."-blok op alle artikelen
    for c in catalog:
        f = c['slug'] + '.html'; s = open(f, encoding='utf-8').read()
        s = re.sub(r'\n?<!-- rel:start -->.*?<!-- rel:end -->\n?', '\n', s, flags=re.S)
        s = s.replace('<div class="site-footer"', related_block(c['slug'], c['product'], catalog) + '\n<div class="site-footer"', 1)
        if 'class="rel-prod"' in s and '.rel-prod{' not in s:
            s = s.replace('<!-- rel:start -->', '<!-- rel:start -->' + ARTCSS, 1)
        open(f, 'w', encoding='utf-8').write(s)
    # overzicht /inzichten
    s = open('inzichten.html', encoding='utf-8').read()
    order = ['batterij','zonnepanelen','warmtepomp','airco','boiler','laadpaal','meterkast','algemeen']
    chips = '<button type="button" class="ins-chip is-on" data-f="alle">Alle</button>' + ''.join(
        f'<button type="button" class="ins-chip" data-f="{k}">{CATLABEL[k]}</button>' for k in order if any(c['product'] == k for c in catalog))
    cards = '\n'.join(card_html(c) for c in sorted(catalog, key=lambda c: (not c['new'], order.index(c['product']))))
    grid = f'''<!-- ins:start --><div class="wrap reveal" style="padding-top:32px;padding-bottom:88px;">
      <style>.ins-chips{{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-bottom:28px;}}
      .ins-chip{{border:1px solid var(--border);background:#fff;color:var(--ink);border-radius:999px;padding:9px 16px;font:700 13.5px 'Nunito Sans',system-ui,sans-serif;cursor:pointer;}}
      .ins-chip.is-on{{background:var(--dark);border-color:var(--dark);color:#fff;}} .ins-chip:focus-visible{{outline:2px solid var(--primary);outline-offset:2px;}}</style>
      <div class="ins-chips" role="toolbar" aria-label="Filter op onderwerp">{chips}</div>
      <div class="grid-3" id="insGrid">
{cards}
      </div>
      <script>(function(){{var chips=[].slice.call(document.querySelectorAll('.ins-chip')),cards=[].slice.call(document.querySelectorAll('.ins-card'));
      function f(k){{chips.forEach(function(c){{c.classList.toggle('is-on',c.getAttribute('data-f')===k);}});cards.forEach(function(c){{c.style.display=(k==='alle'||c.getAttribute('data-cat')===k)?'':'none';}});}}
      chips.forEach(function(c){{c.addEventListener('click',function(){{var k=c.getAttribute('data-f');f(k);try{{history.replaceState(null,'',k==='alle'?location.pathname:'#'+k);}}catch(e){{}}}});}});
      var h=location.hash.slice(1);if(h&&document.querySelector('.ins-chip[data-f="'+h+'"]'))f(h);}})();</script>
    </div><!-- ins:end -->'''
    if '<!-- ins:start -->' in s:
        s = re.sub(r'<!-- ins:start -->.*?<!-- ins:end -->', lambda m: grid, s, flags=re.S)
    else:
        s = re.sub(r'<div class="wrap reveal" style="padding-top:40px;padding-bottom:88px;">\s*<div class="grid-3">.*?</div>\s*</div>(?=\s*</div>\s*<div class="site-footer")', lambda m: grid, s, count=1, flags=re.S)
    assert '<!-- ins:start -->' in s, 'inzichten grid niet gevonden'
    open('inzichten.html', 'w', encoding='utf-8').write(s)
    json.dump([{k: c[k] for k in ('slug','product','title')} for c in catalog], open('content/catalogus.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(new), 'nieuwe artikelen,', len(catalog), 'totaal')

main()
