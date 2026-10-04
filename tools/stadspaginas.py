#!/usr/bin/env python3
"""Lokale pagina's voor Noord-Brabant, Zuid-Holland, Noord-Holland, Utrecht en Zeeland.

Draai vanuit de repo-root: python3 tools/stadspaginas.py   (zit in tools/publish.sh, vóór funnel.py en seo.py)

Maakt drie soorten pagina's:
1. Product in een stad, bijvoorbeeld /airco-breda en /thuisbatterij-utrecht.
   Alleen voor steden waar mensen daar echt op zoeken (Semrush-volume, tools/data/productsteden.json).
2. Een pagina per gemeente (/installateur-<gemeente>), met alle woonplaatsen van die gemeente
   en energiecijfers van het CBS. Bestaande, met de hand geschreven plaatspagina's (tools/local_pages.py) blijven staan.
3. Een overzicht per provincie (/werkgebied-<provincie>), met alle gemeenten en woonplaatsen.

Alleen controleerbare feiten: de cijfers per gemeente komen uit CBS Kerncijfers wijken en buurten 2024
(tools/data/gemeenten.json). Geen verzonnen projecten, reviews of reistijden. De netbeheerder hangt af van het adres,
dus die noemen we niet per gemeente.
"""
import hashlib, html, json, os, re, sys, urllib.parse
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); os.chdir(ROOT)
sys.path.insert(0, 'tools'); sys.dont_write_bytecode = True
from battery import PAKKETTEN, VANAF, eur

SHELL = 'artikel-isde-subsidie-2026.html'
G = json.load(open('tools/data/gemeenten.json', encoding='utf-8'))
PS = json.load(open('tools/data/productsteden.json', encoding='utf-8'))
PROVINCIES = ['Noord-Brabant', 'Zuid-Holland', 'Noord-Holland', 'Utrecht', 'Zeeland']
esc = lambda s: html.escape(str(s), quote=True)
def nl(n): return f'{int(round(n)):,}'.replace(',', '.')
def kies(seed, opties):  # vaste, maar per pagina verschillende formulering
    return opties[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(opties)]

# ---------- namen en slugs ----------
TOON = {"'s-Gravenhage": 'Den Haag', 'Middelburg (Z.)': 'Middelburg', 'Bergen (NH.)': 'Bergen (NH)', 'Rijswijk (ZH.)': 'Rijswijk'}
def toon(g): return TOON.get(g, g)
def slug(s):
    s = s.lower().replace("'s-", 's-').replace(' (z.)', '').replace(' (nh.)', '-nh').replace(' (zh.)', '').replace(' (nh)', '-nh')
    s = (s.replace('â', 'a').replace('é', 'e').replace('ë', 'e').replace('ï', 'i').replace('ü', 'u').replace('ö', 'o'))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')
# zoekwoord-stad -> gemeente
STAD_GEM = {'den haag': "'s-Gravenhage", 'den bosch': "'s-Hertogenbosch", 'zevenbergen': 'Moerdijk', 'middelburg': 'Middelburg (Z.)',
            'rijswijk': 'Rijswijk (ZH.)', 'zaandam': 'Zaanstad', 'hoofddorp': 'Haarlemmermeer', 'spijkenisse': 'Nissewaard',
            'naaldwijk': 'Westland', 'ijmuiden': 'Velsen', 'oud-beijerland': 'Hoeksche Waard', 'hellevoetsluis': 'Voorne aan Zee', 'veghel': 'Meierijstad'}
STAD_TOON = {'den haag': 'Den Haag', 'den bosch': 'Den Bosch', 'ijmuiden': 'IJmuiden', 'capelle aan den ijssel': 'Capelle aan den IJssel',
             'alphen aan den rijn': 'Alphen aan den Rijn', 'bergen op zoom': 'Bergen op Zoom', 'etten-leur': 'Etten-Leur', 'de bilt': 'De Bilt',
             'den helder': 'Den Helder', 'oud-beijerland': 'Oud-Beijerland'}
def stad_toon(s): return STAD_TOON.get(s, ' '.join(w.capitalize() if w not in ('aan', 'den', 'op', 'de') else w for w in s.split(' ')))
def gem_van(stad):
    if stad in STAD_GEM: return STAD_GEM[stad]
    for g in G:
        if g.lower() == stad: return g
    for g, v in G.items():
        if any(w.lower() == stad for w in v['woonplaatsen']): return g
    raise KeyError(stad)

# bestaande, met de hand gemaakte plaatspagina's niet overschrijven
BESTAAND = {f[len('installateur-'):-5] for f in os.listdir('.') if f.startswith('installateur-') and f.endswith('.html') and '<!-- vw-stad:' not in open(f, encoding='utf-8').read()}
def gem_slug(g): return slug(toon(g))
def gem_url(g):
    s = gem_slug(g)
    return f'/installateur-{s}'

# ---------- producten ----------
P = {
 'thuisbatterij': dict(naam='Thuisbatterij', kort='thuisbatterij', lid='een thuisbatterij', prijs=f'vanaf {eur(VANAF)} excl. btw', url='/product-batterij',
    img='batterij-installatie', alt='Thuisbatterij met hybride omvormer, geïnstalleerd door Voltwijk',
    punten=['10 of 16 kWh opslag met hybride omvormer', 'Voor 1-fase én 3-fase aansluitingen', 'Vaste prijs inclusief installatie en aanmelding'],
    lees=[('artikel-thuisbatterij-na-salderen', 'Thuisbatterij na het salderen'), ('artikel-thuisbatterij-hoe-groot', 'Hoe groot moet je thuisbatterij zijn?'),
          ('artikel-thuisbatterij-bij-bestaande-zonnepanelen', 'Thuisbatterij bij bestaande zonnepanelen')]),
 'zonnepanelen': dict(naam='Zonnepanelen', kort='zonnepanelen', lid='zonnepanelen', prijs='vanaf € 3.999 (12 panelen)', url='/product-zonnepanelen',
    img='zonnepanelen-installatie', alt='Zonnepanelen op een dak, geïnstalleerd door Voltwijk',
    punten=['Full-black panelen van 440 Wp, rendement tot 22,8%', '25 jaar productgarantie op de panelen', 'Ontwerp op maat voor jouw dak'],
    lees=[('artikel-hoeveel-zonnepanelen-nodig', 'Hoeveel zonnepanelen heb ik nodig?'), ('artikel-zonnepanelen-prijs', 'Wat kosten zonnepanelen?'),
          ('artikel-zonnepanelen-rendabel-na-2027', 'Zijn zonnepanelen na 2027 nog rendabel?')]),
 'airco': dict(naam='Airco', kort='airco', lid='een airco', prijs='vanaf € 1.899', url='/product-airco',
    img='airco-installatie', alt='Split-unit airco, geïnstalleerd door Voltwijk',
    punten=['Split-unit met energielabel A+++', 'Koelt in de zomer, verwarmt in voor- en najaar', 'Binnenunit van 19 dB(A): fluisterstil'],
    lees=[('artikel-airco-als-bijverwarming', 'Airco als bijverwarming'), ('artikel-wat-kost-een-airco-aan-stroom', 'Wat kost een airco aan stroom?'),
          ('artikel-airco-plaatsen-regels-vergunning', 'Airco plaatsen: regels en vergunning')]),
 'warmtepomp': dict(naam='Warmtepomp', kort='warmtepomp', lid='een warmtepomp', prijs='vanaf € 6.750', url='/product-warmtepomp',
    img='warmtepomp-installatie', alt='Warmtepomp buitenunit, geïnstalleerd door Voltwijk',
    punten=['Lucht/water-warmtepomp, COP tot 4,7', 'ISDE-subsidie (tot € 2.550) vragen wij voor je aan', 'Ook hybride, naast je cv-ketel'],
    lees=[('artikel-is-mijn-huis-geschikt-voor-een-warmtepomp', 'Is mijn huis geschikt voor een warmtepomp?'), ('artikel-hybride-of-volledige-warmtepomp', 'Hybride of volledige warmtepomp?'),
          ('artikel-isde-subsidie-2026', 'ISDE-subsidie 2026')]),
}
ORDER = ['thuisbatterij', 'zonnepanelen', 'airco', 'warmtepomp']
def ps_url(p, stad): return f'/{p}-{slug(stad)}'

# ---------- lokale tekst uit CBS-cijfers ----------
def cijfers(g):
    c = G[g]['cbs']
    return dict(inw=c['AantalInwoners'], won=c['Woningvoorraad'], koop=c['Koopwoningen'], egw=c['PercentageEengezinswoning'],
                lev=c['GemiddeldeElektriciteitslevering'], terug=c['GemiddeldeElektriciteitsteruglevering'], gas=c['GemiddeldAardgasverbruik'],
                zon=c['WoningenMetZonnestroom'], gasvrij=c['AardgasvrijeWoningen'], vrij=c['PercentageVrijstaandeWoningEengezins'], twee=c['PercentageTweeOnderEenKapWoningEe'])
BRON = 'Bron: CBS, Kerncijfers wijken en buurten 2024 (gemiddelden per woning in de gemeente).'

def tegels(g):
    c = cijfers(g)
    t = [(nl(c['inw']), 'inwoners'), (nl(c['won']), 'woningen'), (f"{c['zon']}%", 'woningen met zonnepanelen'),
         (f"{nl(c['lev'])} kWh", 'stroom van het net per woning per jaar'), (f"{nl(c['gas'])} m³", 'gas per woning per jaar'), (f"{c['koop']}%", 'koopwoningen')]
    return '<div class="sp-tegels">' + ''.join(f'<div><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in t) + '</div>'

def lokaal_alinea(g, p, plaats):
    """Twee of drie zinnen die met de cijfers van deze gemeente iets zeggen over dit product."""
    c, gm, s = cijfers(g), toon(g), plaats + p
    egw, meer = c['egw'], 100 - c['egw']
    woning = (f'Ruim {egw}% van de woningen in {gm} is een eengezinswoning' if egw >= 60 else
              f'In {gm} is {meer}% van de woningen een appartement of ander meergezinswoning' if meer >= 50 else
              f'In {gm} is {egw}% van de woningen een eengezinswoning en {meer}% een appartement')
    if p == 'thuisbatterij':
        a = kies(s, [f'In de gemeente {gm} heeft {c["zon"]}% van de woningen al zonnepanelen.', f'{c["zon"]}% van de woningen in {gm} wekt al zelf stroom op met zonnepanelen.'])
        b = (f'Vanaf 1 januari 2027 stopt het salderen. Stroom die je overdag teruglevert, kun je dan niet meer wegstrepen tegen wat je \'s avonds verbruikt. '
             f'Een woning in {gm} haalt gemiddeld {nl(c["lev"])} kWh per jaar van het net: met een thuisbatterij gebruik je meer van je eigen zonnestroom.')
        d = ('Heb je een 3-fase aansluiting, bijvoorbeeld voor een warmtepomp of laadpaal? Dan kies je de 16 kWh-batterij met 8 kW omvormer.' if c['gasvrij'] >= 15 else
             'De meeste woningen hebben een 1-fase aansluiting. Daarvoor is er de 10 of 16 kWh-batterij; bij 3-fase de 16 kWh met 8 kW omvormer.')
        return [a + ' ' + b, d]
    if p == 'zonnepanelen':
        a = kies(s, [f'In {gm} heeft {c["zon"]}% van de woningen zonnepanelen. Dat betekent ook: de meeste daken zijn nog vrij.',
                     f'{c["zon"]}% van de woningen in {gm} heeft al zonnepanelen; voor de rest is het dak nog onbenut.'])
        b = f'Een woning in {gm} haalt gemiddeld {nl(c["lev"])} kWh stroom per jaar van het net. {woning}, '
        b += ('vaak met een eigen dak: ideaal voor panelen.' if egw >= 50 else 'dan heb je voor panelen op het dak vaak de VvE nodig. Wij helpen je met de aanvraag.')
        d = 'Salderen stopt op 1 januari 2027. Combineer je panelen daarom slim met een thuisbatterij, zodat je je eigen stroom zelf gebruikt.'
        return [a + ' ' + b, d]
    if p == 'airco':
        a = (f'{woning}. Een split-unit airco heeft een binnenunit en een buitenunit aan de gevel of op het dak. '
             + ('Bij een eengezinswoning kan de buitenunit meestal zonder vergunning, mits je op de regels voor geluid en plek let.' if egw >= 50 else
                'Woon je in een appartement, dan heb je voor de buitenunit vaak toestemming van de VvE of verhuurder nodig. Wij kijken vooraf mee.'))
        b = kies(s, [f'In {gm} verbruikt een woning gemiddeld {nl(c["gas"])} m³ gas per jaar. Een airco verwarmt in voor- en najaar efficiënter dan je cv-ketel en kan zo gas besparen.',
                     f'Met gemiddeld {nl(c["gas"])} m³ gas per woning per jaar in {gm} is een airco als bijverwarming in voor- en najaar een slimme aanvulling op je cv-ketel.'])
        return [a, b]
    if p == 'warmtepomp':
        a = kies(s, [f'Een woning in {gm} verbruikt gemiddeld {nl(c["gas"])} m³ gas per jaar. {c["gasvrij"]}% van de woningen is al aardgasvrij.',
                     f'In {gm} is {c["gasvrij"]}% van de woningen aardgasvrij; de rest verbruikt gemiddeld {nl(c["gas"])} m³ gas per jaar.'])
        b = (f'{woning}. ' + ('Bij goed geïsoleerde eengezinswoningen kan een volledige warmtepomp; bij oudere woningen is een hybride warmtepomp naast je cv-ketel vaak de beste eerste stap.' if egw >= 50 else
             'In appartementen is een hybride warmtepomp of een collectieve oplossing vaak het meest haalbaar. We kijken samen wat bij jouw woning past.'))
        d = 'Voor een warmtepomp krijg je ISDE-subsidie, tot € 2.550. Die vragen wij voor je aan.'
        return [a, b + ' ' + d]

def gem_alinea(g):
    c, gm, v = cijfers(g), toon(g), G[g]
    plaatsen = v['woonplaatsen']
    a = (f'De gemeente {gm} telt {nl(c["inw"])} inwoners en {nl(c["won"])} woningen'
         + (f', verdeeld over {len(plaatsen)} woonplaatsen.' if len(plaatsen) > 1 else '.'))
    b = kies(g, [f'{c["zon"]}% van de woningen heeft zonnepanelen en {c["gasvrij"]}% is aardgasvrij. Een woning verbruikt hier gemiddeld {nl(c["gas"])} m³ gas en haalt {nl(c["lev"])} kWh stroom van het net per jaar.',
                 f'Gemiddeld haalt een woning in {gm} {nl(c["lev"])} kWh stroom van het net en verbruikt ze {nl(c["gas"])} m³ gas per jaar. {c["zon"]}% van de woningen heeft al zonnepanelen.'])
    d = ('Nu het salderen op 1 januari 2027 stopt, is een thuisbatterij voor de woningen met zonnepanelen de logische volgende stap.' if c['zon'] >= 25 else
         'Er liggen hier nog relatief weinig zonnepanelen. Wie nu panelen neemt, doet dat het slimst meteen samen met een thuisbatterij, omdat het salderen in 2027 stopt.')
    return [a + ' ' + b, d]

# ---------- opmaak ----------
CSS = '''<style>
.sp-hero{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:40px;align-items:center;}
.sp-hero .img img{width:100%;height:auto;border-radius:24px;object-fit:cover;aspect-ratio:4/3;}
.sp-sec{padding-top:56px;}
.sp-h2{font-size:clamp(24px,3vw,32px);line-height:1.15;}
.sp-tegels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:20px;}
.sp-tegels div{background:#fff;border:1px solid var(--border);border-radius:18px;padding:16px 18px;}
.sp-tegels b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:24px;color:var(--ink);}
.sp-tegels span{font-size:13.5px;color:var(--ink-soft);}
.sp-bron{font-size:12.5px;color:var(--ink-faint);margin-top:10px;}
.sp-tekst p{font-size:16px;color:var(--ink-soft);line-height:1.7;margin-top:14px;max-width:760px;}
.sp-ck{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:8px;font-size:15.5px;color:var(--ink);}
.sp-ck li::before{content:"✓";color:var(--primary);font-weight:800;margin-right:8px;}
.sp-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;}
.sp-chips a,.sp-chips span{display:inline-block;border:1px solid var(--border);background:#fff;border-radius:999px;padding:8px 14px;font-size:14px;font-weight:700;color:var(--ink);text-decoration:none;}
.sp-chips a:hover{border-color:var(--primary);color:var(--primary);}
.sp-prods{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:18px;}
.sp-prods a{background:#fff;border:1px solid var(--border);border-radius:18px;padding:18px;text-decoration:none;color:var(--ink);}
.sp-prods a b{display:block;font-size:17px;}.sp-prods a span{display:block;font-size:13.5px;color:var(--ink-soft);margin-top:4px;}
.sp-prods a:hover{border-color:var(--primary);}
.sp-pv h3{font-size:19px;margin-top:26px;}
.sp-pv .sp-chips{margin-top:10px;}
.sp-gm{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:18px;}
.sp-gm>div{background:#fff;border:1px solid var(--border);border-radius:18px;padding:18px 20px;}
.sp-gm h3{font-size:17px;}.sp-gm h3 a{color:var(--ink);text-decoration:none;}.sp-gm h3 a:hover{color:var(--primary);}
.sp-gm p{font-size:13.5px;color:var(--ink-soft);margin-top:6px;line-height:1.55;}
.sp-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:18px;}
.sp-steps>div{background:#fff;border:1px solid var(--border);border-radius:18px;padding:20px;}
.sp-steps b{display:block;font-size:16px;margin-bottom:6px;}.sp-steps p{font-size:14.5px;color:var(--ink-soft);line-height:1.6;}
.lp-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:40px;}
.lp-stat{background:#fff;border:1px solid var(--border);border-radius:16px;padding:16px 18px;}
.lp-stat b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:20px;color:var(--ink);}
.lp-stat span{font-size:13px;color:var(--ink-soft);}
.lp-arts a{display:block;padding:14px 0;border-top:1px solid var(--border);color:var(--ink);font-weight:700;text-decoration:none;font-size:15px;}
.lp-arts a:hover{color:var(--primary);} .lp-arts a:last-child{border-bottom:1px solid var(--border);}
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
@media (max-width:900px){.lp-stats{grid-template-columns:repeat(2,minmax(0,1fr));}}
@media (max-width:640px){.lp-pk{grid-template-columns:1fr;}.lp-bat{padding:22px 18px;}}
@media (max-width:860px){.sp-hero{grid-template-columns:1fr;}.sp-tegels{grid-template-columns:repeat(2,minmax(0,1fr));}.sp-prods{grid-template-columns:repeat(2,minmax(0,1fr));}.sp-gm,.sp-steps{grid-template-columns:1fr;}}
</style>'''
STATS = '''<div class="lp-stats">
      <div class="lp-stat"><b>12.500+</b><span>installaties uitgevoerd</span></div>
      <div class="lp-stat"><b>4,7 / 5</b><span>gemiddeld op Google</span></div>
      <div class="lp-stat"><b>Eigen monteurs</b><span>geen onderaannemers</span></div>
      <div class="lp-stat"><b>Vaste prijs</b><span>vooraf, geen verrassingen</span></div>
    </div>'''
WA = 'https://wa.me/31853335687?text='

def crumbs(items):
    out = []
    for i, (lab, href) in enumerate(items):
        if i: out.append('<span aria-hidden="true">/</span>')
        out.append(f'<a href="{href}" style="color:var(--primary);text-decoration:none;">{esc(lab)}</a>' if href else f'<span>{esc(lab)}</span>')
    return '<nav aria-label="Kruimelpad" style="font-size:13px;font-weight:700;color:var(--ink-faint);display:flex;gap:8px;flex-wrap:nowrap;white-space:nowrap;overflow-x:auto;scrollbar-width:none;align-items:center;">' + ''.join(out) + '</nav>'

def faq_html(qa): return ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in qa)
def lees_html(items): return ''.join(f'<a href="/{a}">{esc(t)} →</a>' for a, t in items if os.path.exists(a + '.html'))
def prov_url(pv): return '/werkgebied-' + slug(pv)
STAP1 = {'thuisbatterij': 'Bereken online welke thuisbatterij past, of plan een gratis adviesgesprek: aan huis of telefonisch.',
         None: 'Bereken je thuisbatterij online, vraag een offerte aan of plan een gratis adviesgesprek: aan huis of telefonisch.'}
STEPS = '''<div class="sp-steps">
      <div><b>1. Aanvraag of gesprek</b><p>__STAP1__</p></div>
      <div><b>2. Vaste prijs vooraf</b><p>Je krijgt een offerte met een vaste prijs, inclusief installatie. Is er meerwerk nodig, dan hoor je dat altijd vooraf.</p></div>
      <div><b>3. Installatie</b><p>We plannen samen een datum. Aanmelding bij de netbeheerder regelen wij. Op de installatie krijg je 2 jaar garantie.</p></div>
    </div>'''
def funnel_plek(): return '<!-- vw-funnel-cta:start --><!-- vw-funnel-cta:end -->'

def knoppen(p, wa_tekst):
    if p == 'thuisbatterij':
        hoofd = '<a href="/thuisbatterij-berekenen" class="btn-primary" style="text-decoration:none;">Bereken je thuisbatterij →</a>'
    elif p:
        hoofd = '<a href="#offerte" class="btn-primary" style="text-decoration:none;">Vraag een offerte aan →</a>'
    else:
        hoofd = '<a href="/thuisbatterij-berekenen" class="btn-primary" style="text-decoration:none;">Bereken je thuisbatterij →</a>'
    return (f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:24px;">{hoofd}'
            f'<a href="/contact" data-book="" class="btn-secondary" style="text-decoration:none;">Plan gratis adviesgesprek</a>'
            f'<a href="{WA + urllib.parse.quote(wa_tekst)}" target="_blank" rel="noopener" class="btn-secondary" style="text-decoration:none;">App ons</a></div>')

# ---------- 1. product in een stad ----------
PSI = {}  # (product, gemeente) -> [stad]
for x in PS: PSI.setdefault(x['product'], []).append(x['stad'])
def ps_bestaat(p, stad): return stad in PSI.get(p, [])

def ps_titel(p, stad):
    n, st = P[p]['naam'], stad_toon(stad)
    opts = {'thuisbatterij': [f'Thuisbatterij {st} – vanaf {eur(VANAF)} | Voltwijk', f'Thuisbatterij {st} – vanaf {eur(VANAF)}', f'Thuisbatterij {st} | Voltwijk'],
            'zonnepanelen': [f'Zonnepanelen {st} – vanaf € 3.999 | Voltwijk', f'Zonnepanelen {st} – vanaf € 3.999', f'Zonnepanelen {st} | Voltwijk'],
            'airco': [f'Airco {st} – vanaf € 1.899 incl. installatie', f'Airco {st} – vanaf € 1.899 | Voltwijk', f'Airco {st} | Voltwijk'],
            'warmtepomp': [f'Warmtepomp {st} – vanaf € 6.750 | Voltwijk', f'Warmtepomp {st} – vanaf € 6.750', f'Warmtepomp {st} | Voltwijk']}[p]
    for t in opts:
        if len(t) <= 60: return t
    return opts[-1][:60]
def ps_desc(p, stad):
    st = stad_toon(stad)
    d = {'thuisbatterij': f'Thuisbatterij in {st}: 10 kWh {eur(PAKKETTEN[0]["prijs"])}, 16 kWh {eur(PAKKETTEN[1]["prijs"])} of 16 kWh 3-fase {eur(PAKKETTEN[2]["prijs"])}, excl. btw en incl. installatie. Bereken welke past.',
         'zonnepanelen': f'Zonnepanelen in {st} laten installeren: full-black panelen, vaste prijs vanaf € 3.999 voor 12 panelen incl. installatie. Vraag een offerte aan.',
         'airco': f'Airco laten plaatsen in {st}: split-unit A+++, koelen en verwarmen, vanaf € 1.899 incl. installatie door eigen monteurs. Vraag een offerte aan.',
         'warmtepomp': f'Warmtepomp in {st}: lucht/water of hybride, vanaf € 6.750 incl. installatie. ISDE-subsidie tot € 2.550 vragen wij voor je aan.'}[p]
    return d if len(d) <= 160 else d[:157].rsplit(' ', 1)[0] + '…'

def ps_faq(p, stad, g):
    st, gm, v = stad_toon(stad), toon(g), G[g]
    andere = [w for w in v['woonplaatsen'] if w.lower() != stad][:12]
    qa = []
    if p == 'thuisbatterij':
        qa.append((f'Wat kost een thuisbatterij in {st}?', f'Een thuisbatterij kost bij ons {eur(PAKKETTEN[0]["prijs"])} (10 kWh), {eur(PAKKETTEN[1]["prijs"])} (16 kWh, 1-fase) of {eur(PAKKETTEN[2]["prijs"])} (16 kWh, 3-fase), exclusief btw en inclusief installatie. In {st} betaal je dezelfde vaste prijs als overal.'))
        qa.append(('Heb ik zonnepanelen nodig voor een thuisbatterij?', 'Nee, maar met zonnepanelen haal je er het meeste uit: je slaat je eigen stroom op. Zonder panelen kun je met een dynamisch contract goedkope stroom opslaan voor later.'))
    elif p == 'zonnepanelen':
        qa.append((f'Wat kosten zonnepanelen in {st}?', f'Zonnepanelen kosten bij ons vanaf € 3.999 voor 12 full-black panelen, inclusief omvormer en installatie. Hoeveel panelen je nodig hebt, hangt af van je verbruik en je dak; dat rekenen we samen uit.'))
        qa.append(('Zijn zonnepanelen na 2027 nog rendabel?', 'Ja, maar anders dan nu. Na het einde van het salderen loont het vooral om je eigen stroom zelf te gebruiken. Daarom combineren veel klanten panelen met een thuisbatterij.'))
    elif p == 'airco':
        qa.append((f'Wat kost een airco in {st}?', f'Een split-unit airco kost bij ons vanaf € 1.899, inclusief installatie door onze eigen monteurs. De precieze prijs hangt af van het aantal ruimtes en de afstand tussen binnen- en buitenunit.'))
        qa.append(('Heb ik een vergunning nodig voor een airco?', 'Voor een buitenunit bij een eengezinswoning meestal niet, maar er zijn regels voor geluid en plaatsing, en in een monument of beschermd stadsgezicht gelden extra regels. Bij een appartement heb je vaak toestemming van de VvE nodig. Wij kijken het vooraf voor je na.'))
    elif p == 'warmtepomp':
        qa.append((f'Wat kost een warmtepomp in {st}?', f'Een warmtepomp kost bij ons vanaf € 6.750, inclusief installatie. Daar gaat de ISDE-subsidie nog af (tot € 2.550), die wij voor je aanvragen.'))
        qa.append(('Hybride of volledige warmtepomp?', 'Bij een goed geïsoleerde woning kan een volledige warmtepomp je cv-ketel vervangen. Bij een oudere woning is een hybride warmtepomp naast je cv-ketel vaak de beste eerste stap. In het adviesgesprek kijken we wat bij jouw huis past.'))
    if andere:
        qa.append((f'Komen jullie ook buiten {st}?', f'Ja. In de gemeente {gm} installeren we ook in {", ".join(andere)}. En daarbuiten in heel {v["provincie"]}.'))
    qa.append(('Wie regelt de aanmelding bij de netbeheerder?', 'Dat doen wij. Welke netbeheerder je hebt, hangt af van je adres. Moet je aansluiting zwaarder, bijvoorbeeld 3-fase, dan regelen we dat ook.'))
    return qa

def ps_main(p, stad):
    g, d, st = gem_van(stad), P[p], stad_toon(stad)
    v, pv = G[g], G[gem_van(stad)]['provincie']
    alineas = ''.join(f'<p>{esc(a)}</p>' for a in lokaal_alinea(g, p, stad))
    ook = ''.join(f'<a href="{ps_url(q, stad)}">{esc(P[q]["naam"])} in {esc(st)}</a>' for q in ORDER if q != p and ps_bestaat(q, stad))
    buren = [x for x in PSI[p] if x != stad and G[gem_van(x)]['regio'] == v['regio']][:8]
    if len(buren) < 4: buren += [x for x in PSI[p] if x != stad and x not in buren and G[gem_van(x)]['provincie'] == pv][:8 - len(buren)]
    buren_html = ''.join(f'<a href="{ps_url(p, x)}">{esc(d["naam"])} {esc(stad_toon(x))}</a>' for x in buren)
    gem_link = f'<a href="{gem_url(g)}">Alles over {esc(toon(g))}</a>'
    h1 = f'{d["naam"]} in {st}'
    attrs = f' data-dienst="{esc(d["naam"])}" data-plaats="{esc(st)}" data-gemeente="{esc(toon(g))}" data-provincie="{esc(pv)}"'
    sub = {'thuisbatterij': f'Vaste prijs {eur(VANAF)} – {eur(PAKKETTEN[-1]["prijs"])} excl. btw, inclusief installatie',
           'zonnepanelen': 'Vanaf € 3.999 voor 12 panelen, inclusief installatie', 'airco': 'Vanaf € 1.899, inclusief installatie',
           'warmtepomp': 'Vanaf € 6.750, inclusief installatie · ISDE-subsidie tot € 2.550'}[p]
    intro = {'thuisbatterij': f'Een thuisbatterij in {st} laten installeren? Wij plaatsen batterijen van 10 en 16 kWh met hybride omvormer, voor een vaste prijs inclusief installatie. Klaar voor het einde van het salderen op 1 januari 2027.',
             'zonnepanelen': f'Zonnepanelen in {st} laten installeren? Wij ontwerpen het systeem op maat voor jouw dak en installeren het met onze eigen monteurs, voor een vaste prijs die je vooraf weet.',
             'airco': f'Een airco in {st} laten plaatsen? Onze split-unit koelt in de zomer en verwarmt efficiënt in voor- en najaar. Geïnstalleerd door onze eigen monteurs, voor een vaste prijs.',
             'warmtepomp': f'Een warmtepomp in {st}? Wij installeren lucht/water- en hybride warmtepompen, regelen de ISDE-subsidie voor je en werken met een vaste prijs vooraf.'}[p]
    punten = ''.join(f'<li>{esc(x)}</li>' for x in d['punten'])
    bat = ''
    if p == 'thuisbatterij':
        cards = ''.join(f'<div><b>{x["kwh"]} kWh</b><span>{x["kw"]} kW hybride omvormer · {esc(x["fase"])}</span><strong>{esc(eur(x["prijs"]))}</strong><small>incl. installatie, excl. btw</small></div>' for x in PAKKETTEN)
        bat = f'''<div class="wrap reveal sp-sec" style="max-width:1000px;"><div class="lp-bat"><h2 class="vw-heading sp-h2">Drie vaste pakketten in {esc(st)}</h2>
    <p>Welke batterij past, hangt af van je verbruik, je zonnepanelen en je aansluiting. Met de batterijcalculator zie je het in 1 minuut.</p><div class="lp-pk">{cards}</div></div></div>'''
    return f'''<!-- vw-stad:product --><div class="blk-light" style="padding-top:40px;">
  {CSS}
  <div class="wrap reveal" style="max-width:1000px;padding-top:48px;">
    {crumbs([('Werkgebied', '/werkgebied'), (pv, prov_url(pv)), (toon(g), gem_url(g)), (d['naam'], None)])}
    <div class="sp-hero" style="margin-top:18px;">
      <div>
        <div class="pill">{esc(d['naam'])} · {esc(pv)}</div>
        <h1 class="vw-heading"{attrs} style="font-size:clamp(30px,4.6vw,44px);margin-top:14px;line-height:1.15;">{esc(h1)}</h1>
        <p class="lp-sub">{esc(sub)}</p>
        <p style="font-size:17px;color:var(--ink-soft);margin-top:16px;line-height:1.65;">{esc(intro)}</p>
        <ul class="sp-ck">{punten}</ul>
        {knoppen(p, f'Hoi Voltwijk, ik woon in {st} en heb een vraag over {d["lid"]}')}
      </div>
      <div class="img"><img fetchpriority="high" src="/images/{d['img']}.webp" alt="{esc(d['alt'])}" width="800" height="600"></div>
    </div>
    {STATS}
  </div>
  {bat}
  <div class="wrap reveal sp-sec sp-tekst" style="max-width:1000px;">
    <h2 class="vw-heading sp-h2">{esc(d['naam'])} in {esc(st)}: wat je moet weten</h2>
    {alineas}
    {tegels(g)}
    <p class="sp-bron">{esc(BRON)}</p>
  </div>
  {funnel_plek()}
  <div class="wrap reveal sp-sec" style="max-width:1000px;">
    <h2 class="vw-heading sp-h2">Zo gaat het</h2>
    {STEPS.replace('__STAP1__', STAP1.get(p, 'Vraag een offerte aan voor ' + d['lid'] + ' of plan een gratis adviesgesprek: aan huis of telefonisch.'))}
  </div>
  <div class="wrap reveal sp-sec" style="max-width:1000px;padding-bottom:80px;">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:40px;">
      <div><h2 class="vw-heading sp-h2">Veelgestelde vragen</h2><div class="faq" style="margin-top:18px;">{faq_html(ps_faq(p, stad, g))}</div></div>
      <div>
        <h2 class="vw-heading sp-h2" style="font-size:22px;">Handig om te lezen</h2><div class="lp-arts" style="margin-top:14px;">{lees_html(d['lees'])}</div>
        <h2 class="vw-heading sp-h2" style="font-size:22px;margin-top:32px;">Meer in {esc(st)}</h2><div class="sp-chips">{ook}{gem_link}</div>
        <h2 class="vw-heading sp-h2" style="font-size:22px;margin-top:32px;">{esc(d['naam'])} in de buurt</h2><div class="sp-chips">{buren_html}<a href="{prov_url(pv)}">Heel {esc(pv)} →</a></div>
      </div>
    </div>
  </div>
</div>
'''

# ---------- 2. gemeente ----------
def gem_faq(g):
    gm, v = toon(g), G[g]
    pl = v['woonplaatsen']
    qa = [(f'In welke plaatsen in de gemeente {gm} komen jullie?', f'In alle woonplaatsen: {", ".join(pl)}.' if len(pl) > 1 else f'In heel {gm}.'),
          (f'Wat kost een thuisbatterij in {gm}?', f'Een thuisbatterij kost bij ons {eur(PAKKETTEN[0]["prijs"])} (10 kWh), {eur(PAKKETTEN[1]["prijs"])} (16 kWh, 1-fase) of {eur(PAKKETTEN[2]["prijs"])} (16 kWh, 3-fase), exclusief btw en inclusief installatie. Zonnepanelen vanaf € 3.999, een airco vanaf € 1.899 en een warmtepomp vanaf € 6.750.'),
          ('Wie regelt de aanmelding bij de netbeheerder?', 'Dat doen wij. Welke netbeheerder je hebt, hangt af van je adres. Moet je aansluiting zwaarder, bijvoorbeeld 3-fase, dan regelen we dat ook.'),
          ('Hoe plan ik een adviesgesprek?', 'Via de knop "Plan gratis adviesgesprek". Afhankelijk van je postcode komt een adviseur bij je langs of bellen we je. Je kiest zelf het moment.')]
    return qa

def gem_main(g):
    gm, v = toon(g), G[g]
    pv = v['provincie']
    alineas = ''.join(f'<p>{esc(a)}</p>' for a in gem_alinea(g))
    # productpagina's van steden in deze gemeente
    eigen = [(q, s) for q in ORDER for s in PSI.get(q, []) if gem_van(s) == g]
    prods = ''.join(f'<a href="{ps_url(q, s) if (q, s) in eigen else P[q]["url"]}"><b>{esc(P[q]["naam"])}{" in " + esc(stad_toon(s)) if (q, s) in eigen else ""}</b><span>{esc(P[q]["prijs"])}</span></a>'
                    for q, s in ([(q, next((s for qq, s in eigen if qq == q), None)) for q in ORDER]))
    plaatsen = ''.join(f'<span>{esc(w)}</span>' for w in v['woonplaatsen'])
    buren = [x for x in G if x != g and G[x]['regio'] == v['regio']]
    buren_html = ''.join(f'<a href="{gem_url(x)}">{esc(toon(x))}</a>' for x in sorted(buren, key=lambda x: -G[x]['cbs']['AantalInwoners'])[:10])
    h1 = f'Thuisbatterij, zonnepanelen en airco in {gm}'
    attrs = f' data-area="{esc("|".join(v["woonplaatsen"][:20]))}" data-gemeente="{esc(gm)}" data-provincie="{esc(pv)}"'
    intro = kies('i' + g, [f'Woon je in de gemeente {gm}? Wij installeren hier thuisbatterijen, zonnepanelen, airco\'s en warmtepompen, met onze eigen monteurs en een vaste prijs die je vooraf weet.',
                           f'Een thuisbatterij, zonnepanelen, airco of warmtepomp in {gm}? Je krijgt van ons een vaste prijs vooraf, inclusief installatie door onze eigen monteurs.'])
    cards = ''.join(f'<div><b>{x["kwh"]} kWh</b><span>{x["kw"]} kW hybride omvormer · {esc(x["fase"])}</span><strong>{esc(eur(x["prijs"]))}</strong><small>incl. installatie, excl. btw</small></div>' for x in PAKKETTEN)
    return f'''<!-- vw-stad:gemeente --><div class="blk-light" style="padding-top:40px;">
  {CSS}
  <div class="wrap reveal" style="max-width:1000px;padding-top:48px;">
    {crumbs([('Werkgebied', '/werkgebied'), (pv, prov_url(pv)), (gm, None)])}
    <div class="sp-hero" style="margin-top:18px;">
      <div>
        <div class="pill">Werkgebied · {esc(pv)}</div>
        <h1 class="vw-heading"{attrs} style="font-size:clamp(30px,4.6vw,44px);margin-top:14px;line-height:1.15;">{esc(h1)}</h1>
        <p class="lp-sub">Vaste prijs vanaf {esc(eur(VANAF))} excl. btw, inclusief installatie</p>
        <p style="font-size:17px;color:var(--ink-soft);margin-top:16px;line-height:1.65;">{esc(intro)}</p>
        {knoppen(None, f'Hoi Voltwijk, ik woon in {gm} en heb een vraag')}
      </div>
      <div class="img"><img fetchpriority="high" src="/images/{kies('img' + g, ['monteur-dak', 'zonnepanelen-dak', 'monteur-en-klant', 'thuisbatterij-bijkeuken'])}.webp" alt="Installatie door een Voltwijk-monteur" width="800" height="600"></div>
    </div>
    {STATS}
  </div>
  <div class="wrap reveal sp-sec" style="max-width:1000px;"><div class="lp-bat"><h2 class="vw-heading sp-h2">Thuisbatterij in {esc(gm)}: drie vaste pakketten</h2>
    <p>Een batterij van 10 of 16 kWh met hybride omvormer. Welke past, hangt af van je verbruik, je zonnepanelen en je aansluiting.</p><div class="lp-pk">{cards}</div></div></div>
  <div class="wrap reveal sp-sec" style="max-width:1000px;">
    <h2 class="vw-heading sp-h2">Wat we in {esc(gm)} installeren</h2>
    <div class="sp-prods">{prods}</div>
  </div>
  <div class="wrap reveal sp-sec sp-tekst" style="max-width:1000px;">
    <h2 class="vw-heading sp-h2">Wonen en energie in {esc(gm)}</h2>
    {alineas}
    {tegels(g)}
    <p class="sp-bron">{esc(BRON)}</p>
  </div>
  <div class="wrap reveal sp-sec" style="max-width:1000px;">
    <h2 class="vw-heading sp-h2">Hier komen we in de gemeente {esc(gm)}</h2>
    <div class="sp-chips">{plaatsen}</div>
  </div>
  {funnel_plek()}
  <div class="wrap reveal sp-sec" style="max-width:1000px;">
    <h2 class="vw-heading sp-h2">Zo gaat het</h2>
    {STEPS.replace('__STAP1__', STAP1[None])}
  </div>
  <div class="wrap reveal sp-sec" style="max-width:1000px;padding-bottom:80px;">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:40px;">
      <div><h2 class="vw-heading sp-h2">Veelgestelde vragen over {esc(gm)}</h2><div class="faq" style="margin-top:18px;">{faq_html(gem_faq(g))}</div></div>
      <div>
        <h2 class="vw-heading sp-h2" style="font-size:22px;">Ook in de regio {esc(v['regio'])}</h2><div class="sp-chips">{buren_html}<a href="{prov_url(pv)}">Heel {esc(pv)} →</a></div>
      </div>
    </div>
  </div>
</div>
'''

# ---------- 3. provincie ----------
def prov_main(pv):
    gms = sorted([g for g in G if G[g]['provincie'] == pv], key=toon)
    n_pl = sum(len(G[g]['woonplaatsen']) for g in gms)
    blokken = ''.join(f'<div><h3><a href="{gem_url(g)}">{esc(toon(g))}</a></h3><p>{esc(", ".join(G[g]["woonplaatsen"]))}</p></div>' for g in gms)
    per_p = ''
    for q in ORDER:
        st = [s for s in PSI.get(q, []) if G[gem_van(s)]['provincie'] == pv]
        if st: per_p += f'<h3 class="vw-heading">{esc(P[q]["naam"])}</h3><div class="sp-chips">' + ''.join(f'<a href="{ps_url(q, s)}">{esc(P[q]["naam"])} {esc(stad_toon(s))}</a>' for s in sorted(st)) + '</div>'
    andere = ''.join(f'<a href="{prov_url(x)}">{esc(x)}</a>' for x in PROVINCIES if x != pv)
    return f'''<!-- vw-stad:provincie --><div class="blk-light" style="padding-top:40px;">
  {CSS}
  <div class="wrap reveal" style="max-width:1000px;padding-top:48px;">
    {crumbs([('Werkgebied', '/werkgebied'), (pv, None)])}
    <div class="pill" style="margin-top:18px;">Werkgebied</div>
    <h1 class="vw-heading" style="font-size:clamp(30px,4.6vw,44px);margin-top:14px;line-height:1.15;">Thuisbatterij, zonnepanelen en airco in {esc(pv)}</h1>
    <p style="font-size:17px;color:var(--ink-soft);margin-top:16px;line-height:1.65;max-width:720px;">We installeren in alle {len(gms)} gemeenten van {esc(pv)}: samen {n_pl} steden en dorpen. Overal met dezelfde vaste prijzen, inclusief installatie door onze eigen monteurs.</p>
    {knoppen(None, f'Hoi Voltwijk, ik woon in {pv} en heb een vraag')}
    {STATS}
  </div>
  <div class="wrap reveal sp-sec sp-pv" style="max-width:1000px;">
    <h2 class="vw-heading sp-h2">Per product</h2>
    {per_p}
  </div>
  <div class="wrap reveal sp-sec" style="max-width:1000px;">
    <h2 class="vw-heading sp-h2">Alle gemeenten en woonplaatsen</h2>
    <div class="sp-gm">{blokken}</div>
    <h2 class="vw-heading sp-h2" style="font-size:22px;margin-top:40px;">Andere provincies</h2><div class="sp-chips">{andere}</div>
  </div>
  {funnel_plek()}
</div>
'''

# ---------- pagina's schrijven ----------
def page(shell, main, sl, title, desc):
    s = re.sub(r'<div class="blk-light" style="padding-top:40px;">.*?(?=<div class="site-footer")', lambda m: main + '\n\n', shell, count=1, flags=re.S)
    s = re.sub(r'<title>.*?</title>', '<title>' + esc(title) + '</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + esc(desc) + '">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://voltwijk.nl/{sl}">', s, count=1)
    s = re.sub(r'\n?<!-- seo:start -->.*?<!-- seo:end -->', '', s, flags=re.S)
    s = re.sub(r'\n?<!-- rel:start -->.*?<!-- rel:end -->', '', s, flags=re.S)
    s = re.sub(r'<meta property="article:[a-z_]+" content="[^"]*">\n?', '', s)
    return s

PROV_BLOK = '<!-- vw-provincies:start -->{}<!-- vw-provincies:end -->'
def werkgebied_blok():
    chips = ''.join(f'<a href="{prov_url(pv)}"><b>{esc(pv)}</b><span>{sum(1 for g in G if G[g]["provincie"] == pv)} gemeenten</span></a>' for pv in PROVINCIES)
    return ('<div class="wrap reveal lp-sec" style="max-width:1000px;"><h2 class="vw-heading lp-h2">Ons werkgebied: vijf provincies</h2>'
            '<p style="font-size:15.5px;color:var(--ink-soft);margin-top:10px;line-height:1.6;max-width:680px;">We installeren in alle steden en dorpen van Noord-Brabant, Zuid-Holland, Noord-Holland, Utrecht en Zeeland. Kies je provincie voor alle gemeenten en woonplaatsen.</p>'
            f'<div class="lp-grid" style="margin-top:18px;">{chips}</div></div>')

def main():
    shell = open(SHELL, encoding='utf-8').read()
    gemaakt = set(); n_ps = n_gm = 0
    for x in PS:
        p, stad = x['product'], x['stad']
        sl = f'{p}-{slug(stad)}'
        t, d = ps_titel(p, stad), ps_desc(p, stad)
        assert len(d) <= 160, d
        open(sl + '.html', 'w', encoding='utf-8').write(page(shell, ps_main(p, stad), sl, t, d)); gemaakt.add(sl); n_ps += 1
    for g in G:
        s = gem_slug(g)
        if s in BESTAAND: continue
        sl = 'installateur-' + s
        gm = toon(g)
        t = next(x for x in (f'Thuisbatterij en zonnepanelen {gm} | Voltwijk', f'Thuisbatterij en zonnepanelen {gm}', f'Thuisbatterij {gm} | Voltwijk', f'Thuisbatterij {gm}') if len(x) <= 60)
        d = f'Thuisbatterij, zonnepanelen, airco of warmtepomp in {gm}? Vaste prijs vooraf, inclusief installatie door eigen monteurs. Thuisbatterij vanaf {eur(VANAF)} excl. btw.'
        if len(d) > 160: d = f'Thuisbatterij, zonnepanelen of airco in {gm}: vaste prijs inclusief installatie. Thuisbatterij vanaf {eur(VANAF)} excl. btw.'
        open(sl + '.html', 'w', encoding='utf-8').write(page(shell, gem_main(g), sl, t, d)); gemaakt.add(sl); n_gm += 1
    for pv in PROVINCIES:
        sl = prov_url(pv)[1:]
        t = f'Thuisbatterij en zonnepanelen in {pv} | Voltwijk'
        if len(t) > 60: t = f'Thuisbatterij en zonnepanelen {pv}'
        d = f'Thuisbatterij, zonnepanelen, airco en warmtepomp in heel {pv}: alle gemeenten en woonplaatsen, met vaste prijzen inclusief installatie.'
        open(sl + '.html', 'w', encoding='utf-8').write(page(shell, prov_main(pv), sl, t, d)); gemaakt.add(sl)
    # opruimen: eerder gemaakte pagina's die niet meer in de lijst staan
    weg = 0
    for f in os.listdir('.'):
        if f.endswith('.html') and f[:-5] not in gemaakt and '<!-- vw-stad:' in open(f, encoding='utf-8').read(): os.remove(f); weg += 1
    # /werkgebied: blok met de vijf provincies
    if os.path.exists('werkgebied.html'):
        w = open('werkgebied.html', encoding='utf-8').read()
        blok = PROV_BLOK.format(werkgebied_blok())
        w2 = re.sub(r'<!-- vw-provincies:start -->.*?<!-- vw-provincies:end -->', lambda m: blok, w, flags=re.S)
        if w2 == w and '<!-- vw-provincies:start -->' not in w:
            w2 = w.replace('<div class="wrap reveal lp-sec" style="max-width:1000px;">', blok + '\n  <div class="wrap reveal lp-sec" style="max-width:1000px;">', 1)
        if w2 != w: open('werkgebied.html', 'w', encoding='utf-8').write(w2)
    print(f'stadspaginas: {n_ps} product-in-stad, {n_gm} gemeenten, {len(PROVINCIES)} provincies; {weg} oude verwijderd; {len(BESTAAND)} bestaande plaatspagina\'s ongemoeid')

if __name__ == '__main__':
    main()
