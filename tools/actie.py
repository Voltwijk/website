# Advertentiepagina /thuisbatterij-actie (voor Meta-advertenties). Veilig om opnieuw te draaien.
#   python3 tools/actie.py
# - Pagina-schil van een artikel (zoals tools/energiescan.py), maar zonder hoofdmenu en zonder groot footer-menu:
#   bovenaan alleen het logo en het telefoonnummer, onderaan alleen de bedrijfsgegevens.
# - noindex: het is een advertentiepagina, geen zoekpagina (tools/seo.py laat hem daardoor uit de sitemap).
# - De keuzehulp zelf komt uit tools/battery.py (op de plek van <!--vw-batterijkeuze-plek-->);
#   het verborgen Netlify-formulier 'bestelling' komt uit tools/order.py.
# Draai daarna: tools/seo.py, booking.py, order.py, analytics.py en battery.py (gebeurt allemaal in tools/publish.sh).
import os, re, html
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)
SHELL = 'artikel-isde-subsidie-2026.html'
SLUG = 'thuisbatterij-actie'
TITLE = 'Thuisbatterij 16 kWh voor € 4.600 incl. installatie | Voltwijk'
DESC = ('Thuisbatterij van 16 kWh met 6 kW hybride omvormer voor € 4.600, inclusief installatie en btw. '
        'Zie in 4 vragen welke batterij bij jou past.')
TEL, TEL_HREF, WA = '085 333 56 87', 'tel:+31853335687', 'https://wa.me/31853335687'
esc = lambda s: html.escape(s, quote=True)

FAQ = [
 ('Wat verandert er als salderen in 2027 stopt?',
  'De salderingsregeling stopt op 1 januari 2027. Stroom die je dan teruglevert, mag je niet meer wegstrepen tegen stroom die je '
  'later afneemt. Je krijgt alleen de terugleververgoeding van je energieleverancier. Met een thuisbatterij bewaar je je zonnestroom '
  'van overdag en gebruik je die zelf, \'s avonds en \'s nachts. Wat dat voor jou betekent, hangt af van je panelen en je verbruik. '
  'Dat rekenen we graag samen met je jaarafrekening door.'),
 ('Ik heb een 1-fase of 3-fase aansluiting. Maakt dat uit?',
  'Ja. De 16 kWh-batterij voor € 4.600 is voor een 1-fase aansluiting (met 6 kW omvormer). Heb je 3-fase, dan wordt het de 16 kWh '
  'met 8 kW omvormer voor € 5.700. Die verdeelt het vermogen over alle drie de fasen. Bij een klein verbruik past soms de 10 kWh-batterij '
  'voor € 4.200 beter. Weet je niet welke aansluiting je hebt? Geen probleem: dat checken we samen voordat er iets vastligt.'),
 ('Kan er meerwerk bij komen?',
  'In de prijs zitten de batterij en omvormer, montage en bekabeling, een eigen groep in de meterkast, het instellen van de app en uitleg '
  'bij oplevering. Soms is je meterkast niet klaar voor een extra groep, bijvoorbeeld als er geen ruimte meer is. Dat zien we bij de check '
  'van je meterkast. Is er meerwerk nodig, dan hoor je dat altijd vooraf, met de prijs erbij. Jij beslist of je doorgaat.'),
 ('Moet ik nu al iets betalen?',
  'Nee. Je aanvraag is vrijblijvend. Pas nadat we je meterkast hebben gecheckt en de installatie samen hebben bevestigd, volgt een '
  'aanbetaling van € 350. Die gaat van de totaalprijs af.'),
 ('Wie komt de batterij installeren?',
  'Onze eigen monteurs, vanuit Zevenbergen. Geen onderaannemers. Op de installatie krijg je 2 jaar garantie.'),
]

GET = [
 ('Thuisbatterij van 16 kWh', 'Met een 6 kW hybride omvormer, voor een 1-fase aansluiting. Past een andere batterij beter, dan zie je dat in de keuzehulp.'),
 ('Complete installatie', 'Montage en bekabeling, en aansluiten op een eigen groep in de meterkast. Door onze eigen monteurs.'),
 ('App en uitleg', 'We stellen de app voor je in en leggen bij de oplevering uit hoe alles werkt.'),
 ('Vaste prijs vooraf', '€ 4.600 inclusief installatie en btw. Is er meerwerk nodig, dan hoor je dat altijd vooraf.'),
]
STEPS = [
 ('Doe de keuzehulp', 'Vier korte vragen. Je ziet direct welke batterij past en wat die kost. Vraag je hem aan, dan betaal je nog niets.'),
 ('We bellen je', 'We checken samen je meterkast (een foto via WhatsApp helpt) en plannen een installatiedatum die jou uitkomt.'),
 ('Bevestiging', 'Klopt alles, dan bevestigen we de installatie. Daarna volgt een aanbetaling van € 350, die van de totaalprijs afgaat.'),
 ('Installatie', 'Onze monteurs plaatsen en sluiten de batterij aan, stellen de app in en leggen alles uit.'),
]
TRUST = [('12.500+', 'installaties'), ('4,7 / 5', 'op Google'), ('Eigen monteurs', 'geen onderaannemers'),
         ('2 jaar', 'garantie op de installatie'), ('Zevenbergen', 'gevestigd in West-Brabant')]

CSS = '''<style>
.ta-hero{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:44px;align-items:center;}
.ta-hero h1{font-size:clamp(30px,4.4vw,48px);line-height:1.08;margin-top:14px;}
.ta-hero .l{font-size:17px;color:var(--ink-soft);margin-top:14px;line-height:1.6;}
.ta-price{display:flex;align-items:baseline;flex-wrap:wrap;gap:6px 12px;margin-top:20px;}
.ta-price b{font:700 44px/1 'Bricolage Grotesque',system-ui,sans-serif;color:var(--ink);}
.ta-price span{font-size:14px;color:var(--ink-soft);}
.ta-cta{display:flex;flex-wrap:wrap;align-items:center;gap:12px 18px;margin-top:22px;}
.ta-cta .btn-primary{text-decoration:none;font-size:15px;padding:15px 24px;}
.ta-cta a.tel{font-weight:800;color:var(--primary);text-decoration:none;font-size:15px;}
.ta-img{border-radius:24px;overflow:hidden;aspect-ratio:4/3;background:var(--bg);}
.ta-img img{width:100%;height:100%;object-fit:cover;display:block;}
.ta-trust{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:28px;}
.ta-trust div{background:#fff;border:1px solid var(--border);border-radius:16px;padding:12px 14px;}
.ta-trust b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:18px;color:var(--ink);}
.ta-trust span{font-size:12.5px;color:var(--ink-soft);}
.ta-sec{padding-top:72px;}
.ta-h2{font-size:clamp(24px,3vw,32px);line-height:1.2;}
.ta-get{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:22px;}
.ta-get div{background:#fff;border:1px solid var(--border);border-radius:18px;padding:20px;}
.ta-get h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:17px;margin:0 0 6px;color:var(--ink);}
.ta-get p,.ta-steps p{font-size:14.5px;line-height:1.6;color:var(--ink-soft);}
.ta-steps{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:22px;counter-reset:s;}
.ta-steps div{display:flex;flex-direction:column;gap:10px;}
.ta-steps b{display:block;color:var(--ink);margin-bottom:2px;font-size:15.5px;}
.ta-faq{max-width:760px;}
.ta-faq .faq summary{font-size:15.5px;}
.ta-faq .faq p{font-size:14.5px;line-height:1.65;max-width:none;}
.ta-end{margin-top:72px;background:var(--dark);border-radius:26px;padding:36px;color:#fff;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px;}
.ta-end h2{color:#fff;font-size:clamp(22px,2.6vw,28px);}
.ta-end p{color:#C9D6D3;font-size:15px;margin-top:6px;}
.ta-end .row{display:flex;flex-wrap:wrap;gap:10px;}
.ta-end .btn-primary{background:var(--mint);color:var(--dark);text-decoration:none;}
.ta-end .btn-secondary{color:#fff;border-color:rgba(255,255,255,.5);text-decoration:none;}
.ta-top{display:flex;align-items:center;justify-content:space-between;gap:16px;}
.ta-top .vw-logo{height:20px;}
.ta-tel{display:inline-flex;align-items:center;gap:8px;font-weight:800;font-size:15px;color:inherit;text-decoration:none;white-space:nowrap;}
.ta-tel small{font-weight:600;font-size:12.5px;opacity:.75;}
.ta-foot{background:var(--dark);color:#C9D6D3;padding:32px 0 28px;font-size:13px;line-height:1.7;}
.ta-foot .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px 24px;}
.ta-foot a{color:#C9D6D3;}
.vwp{display:none !important;}
html body.vwp-up #waWidget{bottom:20px !important;}
@media (max-width:1000px){.ta-trust{grid-template-columns:repeat(3,minmax(0,1fr));}.ta-get,.ta-steps{grid-template-columns:repeat(2,minmax(0,1fr));}}
@media (max-width:900px){.ta-hero{grid-template-columns:1fr;gap:24px;}.ta-img{aspect-ratio:16/9;}}
@media (max-width:640px){.ta-trust{grid-template-columns:repeat(2,minmax(0,1fr));}.ta-trust div:last-child{grid-column:1/-1;}.ta-get,.ta-steps{grid-template-columns:1fr;}
 .ta-price b{font-size:38px;}.ta-cta .btn-primary{width:100%;justify-content:center;}.ta-sec{padding-top:56px;}.ta-end{padding:26px 20px;}
 .ta-tel small{display:none;}.ta-img{display:none;}.ta-foot{padding-bottom:96px;}
 .ta-trust{display:flex;flex-wrap:wrap;gap:6px;margin-top:20px;}.ta-trust div,.ta-trust div:last-child{padding:6px 11px;border-radius:999px;}
 .ta-trust b{display:inline;font-size:13.5px;}.ta-trust span{font-size:12.5px;margin-left:4px;}.ta-hero .l{font-size:16px;}}
</style>'''

def nav_html(logo):
    return f'''<div id="siteNav">
    <div class="wrap nav-inner ta-top">
      <span class="vw-heading" style="display:inline-flex;align-items:center;">{logo}</span>
      <a class="ta-tel" href="{TEL_HREF}" aria-label="Bel Voltwijk: {TEL}"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg><span>{TEL}</span> <small>ma–vr 9:00–17:30</small></a>
    </div>
  </div>'''

def main_html():
    trust = ''.join(f'<div><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in TRUST)
    get = ''.join(f'<div><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in GET)
    steps = ''.join(f'<div><span class="step-num">{i}</span><p><b>{esc(h)}</b>{esc(t)}</p></div>' for i, (h, t) in enumerate(STEPS, 1))
    faq = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in FAQ)
    return f'''<div class="blk-light" style="padding-top:40px;">
  {CSS}
  <div class="wrap" style="max-width:1120px;padding-top:56px;">
    <div class="ta-hero">
      <div>
        <div class="pill">Thuisbatterij · vaste prijs</div>
        <h1 class="vw-heading">Thuisbatterij van 16&nbsp;kWh voor €&nbsp;4.600, inclusief installatie</h1>
        <p class="l">Met een 6 kW hybride omvormer, voor een 1-fase aansluiting. Geïnstalleerd door onze eigen monteurs uit Zevenbergen. Twijfel je welke batterij bij jou past? De keuzehulp hieronder laat het in vier vragen zien.</p>
        <div class="ta-price"><b>€ 4.600</b><span>vaste prijs, inclusief installatie en btw</span></div>
        <div class="ta-cta"><a href="#batterijkeuze" class="btn-primary">Start de keuzehulp →</a><a class="tel" href="{TEL_HREF}">of bel {TEL}</a></div>
      </div>
      <div class="ta-img"><img fetchpriority="high" src="/images/batterij-installatie.webp" alt="Thuisbatterij met hybride omvormer, geplaatst op een zolder" width="1400" height="1050"></div>
    </div>
    <div class="ta-trust">{trust}</div>
  </div>
<!--vw-batterijkeuze-plek-->
  <div class="wrap ta-sec" style="max-width:1120px;padding-top:24px;">
    <div class="pill">Wat je krijgt</div>
    <h2 class="vw-heading ta-h2" style="margin-top:12px;">Alles geregeld voor één vaste prijs</h2>
    <div class="ta-get">{get}</div>
  </div>
  <div class="wrap ta-sec" style="max-width:1120px;">
    <div class="pill">Hoe het gaat</div>
    <h2 class="vw-heading ta-h2" style="margin-top:12px;">Van keuzehulp tot werkende batterij, in vier stappen</h2>
    <div class="ta-steps">{steps}</div>
  </div>
  <div class="wrap ta-sec ta-faq">
    <h2 class="vw-heading ta-h2">Veelgestelde vragen</h2>
    <div class="faq" style="margin-top:18px;">{faq}</div>
  </div>
  <div class="wrap" style="max-width:1120px;">
    <div class="ta-end">
      <div><h2 class="vw-heading">Welke batterij past bij jou?</h2><p>Doe de keuzehulp, of stel je vraag gewoon even via WhatsApp.</p></div>
      <div class="row"><a href="#batterijkeuze" class="btn-primary">Naar de keuzehulp →</a><a href="{WA}?text=Hoi%20Voltwijk%2C%20ik%20heb%20een%20vraag%20over%20een%20thuisbatterij" target="_blank" rel="noopener" class="btn-secondary">App ons</a></div>
    </div>
  </div>
  <div style="height:80px;"></div>
</div>
'''

FOOT = f'''<div class="ta-foot">
    <div class="wrap">
      <span><b style="color:#fff;">Voltwijk B.V.</b> · Schoenmakerij 15a, 4762 AS Zevenbergen · <a href="{TEL_HREF}">{TEL}</a> · <a href="mailto:info@voltwijk.nl">info@voltwijk.nl</a></span>
      <span><a href="/privacybeleid">Privacy</a> · <a href="/cookiebeleid">Cookies</a> · <a href="/algemene-voorwaarden">Voorwaarden</a></span>
    </div>
  </div>

'''

def main():
    shell = open(SHELL, encoding='utf-8').read()
    logo = re.search(r'<svg[^>]*class="vw-logo".*?</svg>', shell, re.S).group(0)
    s = shell
    s, k1 = re.subn(r'<div id="siteNav">.*?(?=\n\n\n?<div class="blk-light" style="padding-top:40px;">)', lambda m: nav_html(logo), s, count=1, flags=re.S)
    s, k2 = re.subn(r'<div class="blk-light" style="padding-top:40px;">.*?(?=<div class="site-footer")', lambda m: main_html() + '\n', s, count=1, flags=re.S)
    s, k3 = re.subn(r'<div class="site-footer".*?(?=<!-- FLOATING CONTACT)', lambda m: FOOT, s, count=1, flags=re.S)
    assert k1 == k2 == k3 == 1, ('schil niet herkend', k1, k2, k3)
    s = re.sub(r'<title>.*?</title>', '<title>' + esc(TITLE) + '</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + esc(DESC) + '">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://voltwijk.nl/{SLUG}">', s, count=1)
    s = re.sub(r'\n?<meta property="article:(published|modified)_time"[^>]*>', '', s)
    for tag in ('seo', 'rel', 'vw-cal', 'vw-plan', 'vw-order', 'vw-analytics'):
        s = re.sub(r'\n?<!-- ' + tag + r':start -->.*?<!-- ' + tag + r':end -->', '', s, flags=re.S)
    s = re.sub(r'\n?<!--vw-batterijkeuze-->.*?<!--/vw-batterijkeuze-->', '', s, flags=re.S)
    s = s.replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"', 1)
    # geen afleiding: WhatsApp-tekst over de thuisbatterij
    s = s.replace("var topic = TOPIC[slug];", "var topic = TOPIC[slug] || (slug === '" + SLUG + "' ? 'een thuisbatterij' : '');", 1)
    open(SLUG + '.html', 'w', encoding='utf-8').write(s)
    print('actie:', SLUG + '.html')

if __name__ == '__main__':
    main()
