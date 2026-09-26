# Actiepagina "Gratis Energiescanweek Moerdijk": /energiescan (met Netlify-formulier), /energiescan-bedankt
# en een banner op de homepage. Veilig om opnieuw te draaien.
#   python3 tools/energiescan.py          actie aan
#   python3 tools/energiescan.py vol      formulier dicht, "alle plekken zijn vergeven"
#   python3 tools/energiescan.py uit      banner van de homepage (pagina's blijven bestaan)
# Daarna: python3 tools/seo.py
import os, re, sys, html
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)
MODE = (sys.argv[1] if len(sys.argv) > 1 else 'aan').lower()
SHELL = 'artikel-isde-subsidie-2026.html'
MAX = 60
DATES = '26 t/m 31 oktober'
DAYS = ['Maandag 26 oktober', 'Dinsdag 27 oktober', 'Woensdag 28 oktober', 'Donderdag 29 oktober', 'Vrijdag 30 oktober', 'Zaterdag 31 oktober']
KERNEN = ['Zevenbergen', 'Klundert', 'Fijnaart', 'Willemstad', 'Moerdijk', 'Zevenbergschen Hoek', 'Standdaarbuiten',
          'Noordhoek', 'Langeweg', 'Heijningen', 'Helwijk', 'Oudemolen']
esc = lambda s: html.escape(s, quote=True)

ICONS = {'Meterkast-check': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h2M14 11h2M8 15h2M14 15h2"/></svg>', 'Blik op je dak': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/></svg>', 'Salderen stopt in 2027': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>', 'Persoonlijk adviesrapport': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>'}
CSS = '''<style>
.es-hero{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:48px;align-items:center;}
.es-hero .img{border-radius:22px;overflow:hidden;aspect-ratio:4/5;background:var(--bg);}
.es-hero .img img{width:100%;height:100%;object-fit:cover;display:block;}
.es-date{display:inline-flex;align-items:center;gap:10px;margin-top:22px;padding:10px 16px;border-radius:14px;background:var(--dark);color:#fff;font-weight:800;font-size:14.5px;}
.es-date b{color:var(--mint);}
.es-h2{font-size:clamp(24px,3vw,30px);line-height:1.25;}
.es-get{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:22px;}
.es-get > div{background:#fff;border:1px solid var(--border);border-radius:18px;padding:20px 22px;}
.es-get h3{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:17px;margin:0 0 8px;color:var(--ink);}
.es-get p{font-size:14.5px;line-height:1.65;color:var(--ink-soft);}
.es-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:22px;}
.es-steps div{display:flex;gap:14px;align-items:flex-start;}
.es-steps p{font-size:14.5px;line-height:1.6;color:var(--ink-soft);} .es-steps b{display:block;color:var(--ink);margin-bottom:4px;}
.es-form{background:#fff;border:1px solid var(--border);border-radius:22px;padding:32px;box-shadow:0 30px 60px -40px rgba(16,32,31,.45);}
.es-form .row2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;}
.es-form label{display:block;font-size:13px;font-weight:700;color:var(--ink);margin:16px 0 6px;}
.es-form label span{font-weight:400;color:var(--ink-faint);}
.es-form input[type=text],.es-form input[type=email],.es-form input[type=tel],.es-form select,.es-form textarea{width:100%;background:#fff;border:1.5px solid var(--border);border-radius:12px;padding:12px 14px;font-size:14.5px;font-family:inherit;color:var(--ink);}
.es-form textarea{min-height:96px;resize:vertical;}
.es-form input:focus,.es-form select:focus,.es-form textarea:focus{outline:2px solid var(--primary);outline-offset:1px;border-color:var(--primary);}
.es-checks{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px;}
.es-checks label{display:inline-flex;align-items:center;gap:8px;margin:0;padding:9px 13px;border:1.5px solid var(--border);border-radius:999px;font-weight:700;font-size:13.5px;cursor:pointer;}
.es-checks input{accent-color:var(--primary);}
.es-ok{display:flex;gap:10px;align-items:flex-start;font-size:13px !important;font-weight:400 !important;color:var(--ink-soft) !important;line-height:1.5;}
.es-ok input{margin-top:3px;accent-color:var(--primary);}
.es-form button{margin-top:22px;width:100%;justify-content:center;font-size:15px;padding:15px 22px;}
.es-full{padding:22px 24px;border-radius:16px;background:var(--surface-tint);color:var(--ink);font-size:15px;line-height:1.6;}
.es-sec{padding-top:56px;}
.es-kernen{font-size:14.5px;line-height:1.7;color:var(--ink-soft);margin-top:10px;}
@media (max-width:900px){.es-hero{grid-template-columns:1fr;gap:28px;}.es-hero .img{aspect-ratio:16/10;}.es-steps{grid-template-columns:1fr;}}
@media (max-width:640px){.es-get{grid-template-columns:1fr;}.es-form{padding:22px 18px;}.es-form .row2{grid-template-columns:1fr;gap:0;}}
.es-top{position:relative;border-radius:28px;overflow:hidden;min-height:560px;display:flex;align-items:flex-end;background:#10201F;}
.es-top picture,.es-top img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:70% 50%;}
.es-top:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,20,19,.88) 0%,rgba(10,20,19,.62) 34%,rgba(10,20,19,0) 62%),linear-gradient(0deg,rgba(10,20,19,.55) 0%,rgba(10,20,19,0) 40%);}
.es-top .in{position:relative;z-index:1;padding:48px;max-width:540px;color:#fff;}
.es-top .pill{background:rgba(255,255,255,.14);color:#fff;}
.es-top h1{color:#fff;}
.es-top p.l{font-size:17px;color:#DDE7E5;margin-top:16px;line-height:1.6;}
.es-top .es-date{background:#FF6B5B;color:#10201F;}
.es-top .es-date b{color:#10201F;}
.es-top .small{font-size:13px;color:#B8C7C4;margin-top:14px;}
.es-trust{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:18px;}
.es-trust div{background:#fff;border:1px solid var(--border);border-radius:16px;padding:14px 16px;}
.es-trust b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:19px;color:var(--ink);}
.es-trust span{font-size:13px;color:var(--ink-soft);}
.es-get .ic{width:42px;height:42px;border-radius:12px;background:var(--mint-tint);color:var(--primary);display:flex;align-items:center;justify-content:center;margin-bottom:14px;}
.es-get div.card{transition:transform .2s,border-color .2s;} .es-get div.card:hover{transform:translateY(-3px);border-color:var(--primary);}
.es-band{background:var(--dark);border-radius:26px;padding:40px;color:#fff;}
.es-band h2{color:#fff;}
.es-days{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin-top:22px;}
.es-days div{background:var(--dark-surface);border:1px solid #2A3F3D;border-radius:16px;padding:16px 12px;text-align:center;}
.es-days b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:15px;}
.es-days em{display:block;font-style:normal;font-size:30px;font-weight:800;color:var(--mint);margin:4px 0 2px;font-family:'Bricolage Grotesque',system-ui,sans-serif;}
.es-days span{font-size:12px;color:var(--dark-text-muted);}
.es-band .es-steps p{color:#C9D6D3;} .es-band .es-steps b{color:#fff;} .es-band .step-num{background:var(--mint);color:var(--dark);}
.es-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}
.es-chips span{padding:7px 13px;border-radius:999px;background:#fff;border:1px solid var(--border);font-size:13px;font-weight:700;color:var(--ink);}
@media (max-width:900px){.es-top{min-height:0;display:block;}.es-top picture,.es-top img.bg{position:relative;height:auto;aspect-ratio:3/2;}
.es-top:after{display:none;}.es-top .in{padding:28px 22px 30px;max-width:none;}.es-trust{grid-template-columns:repeat(2,minmax(0,1fr));}.es-days{grid-template-columns:repeat(3,minmax(0,1fr));}.es-band{padding:28px 20px;}}
</style>'''

FAQ = [
 ('Is het echt helemaal gratis?', 'Ja. Het bezoek en het adviesrapport kosten je niets en je zit nergens aan vast. Wil je daarna iets laten installeren, dan krijg je daar een aparte offerte voor. Of je die aanneemt, bepaal je zelf.'),
 ('Gaan jullie me iets verkopen?', 'Nee. Tijdens het bezoek geven we advies, geen verkooppraatje. Vaak is het eerlijke antwoord ook dat iets (nog) niet loont. Dat zeggen we dan gewoon.'),
 ('Wie komt er langs?', 'Een adviseur of monteur uit ons eigen team. Geen callcenter of tussenpersoon.'),
 ('Hoe lang duurt het bezoek?', 'Reken op ongeveer 45 minuten. We kijken naar je meterkast, je dak en je energieverbruik en beantwoorden je vragen.'),
 ('Wat heb ik na afloop?', 'Binnen een paar werkdagen ontvang je per mail een kort persoonlijk adviesrapport: wat bij jouw huis past, wat het ongeveer kost en wat het oplevert. En wat je beter (nog) niet kunt doen.'),
 ('Ik woon niet in de gemeente Moerdijk. Kan ik ook meedoen?', 'Deze week is alleen voor inwoners van de gemeente Moerdijk. Woon je ergens anders, dan kun je altijd je prijs berekenen of ons een appje sturen voor advies.'),
 ('Kan het ook \'s avonds of op zaterdag?', 'Ja. We komen overdag, in de avond en op zaterdag. Geef bij je aanmelding je voorkeur op, dan bellen we je om een tijd af te spreken.'),
]

def form_html():
    if MODE == 'vol':
        return (f'<div class="es-full"><strong>Alle {MAX} plekken zijn vergeven.</strong> Bedankt voor de enorme belangstelling! '
                'Wil je toch advies? Stuur ons een appje of <a href="/bereken-je-prijs" style="color:var(--primary);font-weight:700;">bereken je prijs</a>.</div>')
    kern = ''.join(f'<option>{esc(k)}</option>' for k in KERNEN)
    days = '<option>Maakt niet uit</option>' + ''.join(f'<option>{esc(d)}</option>' for d in DAYS)
    topics = ''.join(f'<label><input type="checkbox" name="interesse_{k.lower().replace(" ", "_")}" value="ja"> {esc(k)}</label>'
                     for k in ['Zonnepanelen', 'Thuisbatterij', 'Warmtepomp', 'Airco', 'Boiler', 'Laadpaal', 'Meterkast', 'Weet ik nog niet'])
    return f'''<form class="es-form" name="energiescan" method="POST" action="/energiescan-bedankt" data-netlify="true" netlify-honeypot="bot-field">
      <input type="hidden" name="form-name" value="energiescan">
      <p style="display:none;"><label>Niet invullen: <input name="bot-field"></label></p>
      <div class="vw-heading" style="font-size:22px;">Meld je aan</div>
      <p style="font-size:14px;color:var(--ink-soft);margin-top:6px;">Vol = vol: we komen bij maximaal {MAX} huishoudens.</p>
      <div class="row2"><div><label for="es-naam">Naam</label><input id="es-naam" type="text" name="naam" autocomplete="name" required></div>
      <div><label for="es-tel">Telefoonnummer</label><input id="es-tel" type="tel" name="telefoon" autocomplete="tel" required></div></div>
      <label for="es-mail">E-mailadres <span>(voor je adviesrapport)</span></label><input id="es-mail" type="email" name="email" autocomplete="email" required>
      <div class="row2"><div><label for="es-straat">Straat en huisnummer</label><input id="es-straat" type="text" name="adres" autocomplete="street-address" required></div>
      <div><label for="es-pc">Postcode</label><input id="es-pc" type="text" name="postcode" autocomplete="postal-code" required pattern="\\s*[0-9]{{4}}\\s*[A-Za-z]{{2}}\\s*" title="Bijvoorbeeld 4761 AB"></div></div>
      <label for="es-kern">Woonplaats</label><select id="es-kern" name="woonplaats" required><option value="">Kies je woonplaats</option>{kern}</select>
      <div class="row2"><div><label for="es-dag">Voorkeursdag</label><select id="es-dag" name="voorkeursdag">{days}</select></div>
      <div><label for="es-dd">Dagdeel</label><select id="es-dd" name="dagdeel"><option>Maakt niet uit</option><option>Ochtend</option><option>Middag</option><option>Avond</option></select></div></div>
      <label>Waar heb je vragen over? <span>(optioneel)</span></label><div class="es-checks">{topics}</div>
      <label for="es-vraag">Je vraag of situatie <span>(optioneel)</span></label><textarea id="es-vraag" name="vraag" placeholder="Bijvoorbeeld: we hebben 10 panelen uit 2016 en twijfelen over een thuisbatterij."></textarea>
      <label class="es-ok"><input type="checkbox" name="akkoord" value="ja" required> Ik ga ermee akkoord dat Voltwijk mijn gegevens gebruikt om het bezoek in te plannen en mij het adviesrapport te sturen. Zie het <a href="/privacybeleid" style="color:var(--primary);">privacybeleid</a>.</label>
      <button type="submit" class="btn-primary">Plan mijn gratis energiescan →</button>
    </form>'''

def main_html():
    get = ''.join(f'<div class="card"><div class="ic">{ICONS[h]}</div><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in [
        ('Meterkast-check', 'Is je meterkast klaar voor zonnepanelen, een thuisbatterij, laadpaal of warmtepomp? Of moeten er eerst groepen bij?'),
        ('Blik op je dak', 'Is je dak geschikt voor zonnepanelen, hoeveel passen er en wat leveren ze ongeveer op?'),
        ('Salderen stopt in 2027', 'Wat betekent het einde van de salderingsregeling voor jouw huishouden, en is een thuisbatterij dan slim?'),
        ('Persoonlijk adviesrapport', 'Na het bezoek krijg je per mail een kort rapport: wat past bij jouw huis, wat het kost en wat het oplevert.')])
    faq = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in FAQ)
    days = ''.join(f'<div><b>{d.split()[0][:2]}</b><em>{d.split()[1]}</em><span>okt</span></div>' for d in DAYS)
    chips = ''.join(f'<span>{esc(k)}</span>' for k in KERNEN)
    return f"""<div class="blk-light" style="padding-top:40px;">
  {CSS}
  <div class="wrap reveal" style="max-width:1120px;padding-top:40px;">
    <div class="es-top">
      <picture><source media="(max-width:900px)" srcset="/images/energiescan-warmtepomp-m.webp"><img class="bg" fetchpriority="high" src="/images/energiescan-warmtepomp.webp" alt="Bewoner naast de warmtepomp aan de gevel van zijn huis" width="1500" height="1000"></picture>
      <div class="in">
        <div class="pill">Gemeente Moerdijk · {esc(DATES)}</div>
        <h1 class="vw-heading" style="font-size:clamp(32px,4.8vw,52px);margin-top:14px;line-height:1.05;hyphens:manual;-webkit-hyphens:manual;">Gratis Energie&shy;scan&shy;week Moerdijk</h1>
        <p class="l">Twijfel je over zonnepanelen, een thuisbatterij of een warmtepomp? Of wat het einde van het salderen in 2027 voor jou betekent? We komen gratis bij je langs voor eerlijk advies. Zonder verkooppraatje en zonder verplichtingen.</p>
        <div class="es-date">📅 <span>Ma 26 t/m za 31 oktober · <b>ook 's avonds en op zaterdag</b></span></div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:22px;"><a href="#aanmelden" class="btn-primary" style="text-decoration:none;background:var(--mint);color:var(--dark);">{'Bekijk de status' if MODE == 'vol' else 'Meld je gratis aan'} →</a></div>
        <p class="small">Maximaal {MAX} huishoudens · vol = vol</p>
      </div>
    </div>
    <div class="es-trust">
      <div><b>100% gratis</b><span>geen verplichtingen</span></div>
      <div><b>±45 minuten</b><span>bij jou aan de keukentafel</span></div>
      <div><b>Eigen team</b><span>geen verkopers of callcenter</span></div>
      <div><b>12.500+</b><span>installaties uitgevoerd</span></div>
    </div>
  </div>
  <div class="wrap reveal es-sec" style="max-width:1120px;">
    <div class="pill">Wat je krijgt</div>
    <h2 class="vw-heading es-h2" style="margin-top:12px;">Eerlijk advies over jouw huis, niet over ons assortiment</h2>
    <div class="es-get">{get}</div>
  </div>
  <div class="wrap reveal es-sec" style="max-width:1120px;">
    <div class="es-band">
      <div class="pill" style="background:rgba(255,255,255,.1);color:var(--mint);">De week</div>
      <h2 class="vw-heading es-h2" style="margin-top:12px;">Zes dagen, ochtend tot avond</h2>
      <div class="es-days">{days}</div>
      <div class="es-steps" style="margin-top:34px;">
        <div><div class="step-num">1</div><p><b>Meld je aan</b>Vul het formulier in. Het kost een minuut.</p></div>
        <div><div class="step-num">2</div><p><b>Wij bellen je</b>We spreken een tijd af die jou uitkomt: overdag, 's avonds of op zaterdag.</p></div>
        <div><div class="step-num">3</div><p><b>Bezoek en rapport</b>Een adviseur uit ons eigen team komt ±45 minuten langs. Daarna krijg je je adviesrapport per mail.</p></div>
      </div>
    </div>
  </div>
  <div class="wrap reveal es-sec" id="aanmelden" style="max-width:1120px;scroll-margin-top:90px;">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:40px;align-items:start;">
      <div>{form_html()}</div>
      <div>
        <h2 class="vw-heading es-h2">Veelgestelde vragen</h2>
        <div class="faq" style="margin-top:18px;">{faq}</div>
        <h2 class="vw-heading es-h2" style="font-size:20px;margin-top:32px;">Voor heel de gemeente Moerdijk</h2>
        <div class="es-chips">{chips}</div>
      </div>
    </div>
  </div>
  <div style="height:80px;"></div>
</div>
"""

def thanks_html():
    return '''<div class="blk-light" style="padding-top:40px;">
  <div class="wrap reveal" style="max-width:680px;padding-top:88px;padding-bottom:110px;text-align:center;">
    <div class="pill" style="margin:0 auto;">Gratis Energiescanweek Moerdijk</div>
    <h1 class="vw-heading" style="font-size:clamp(30px,4.4vw,42px);margin-top:16px;line-height:1.15;">Je aanmelding is binnen!</h1>
    <p style="font-size:17px;color:var(--ink-soft);margin-top:16px;line-height:1.65;">Bedankt. We bellen je binnen twee werkdagen om een tijd af te spreken in de week van 26 t/m 31 oktober. Na het bezoek ontvang je je persoonlijke adviesrapport per mail.</p>
    <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:28px;"><a href="/inzichten" class="btn-secondary" style="text-decoration:none;">Alvast lezen in de kennisbank</a><a href="/" class="btn-primary" style="text-decoration:none;">Naar de homepage</a></div>
  </div>
</div>
'''

def page(shell, main, slug, title, desc, noindex=False):
    s = re.sub(r'<div class="blk-light" style="padding-top:40px;">.*?(?=<div class="site-footer")', lambda m: main + '\n\n', shell, count=1, flags=re.S)
    s = re.sub(r'<title>.*?</title>', '<title>' + esc(title) + '</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + esc(desc) + '">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://voltwijk.nl/{slug}">', s, count=1)
    s = re.sub(r'\n?<!-- seo:start -->.*?<!-- seo:end -->', '', s, flags=re.S)
    s = re.sub(r'\n?<!-- rel:start -->.*?<!-- rel:end -->', '', s, flags=re.S)
    if noindex: s = s.replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"', 1)
    return s

BAND = '''<!-- scan:start --><a href="/energiescan" class="reveal" style="display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap;max-width:760px;margin:36px auto 0;padding:18px 22px;border-radius:18px;background:var(--dark);color:#fff;text-decoration:none;text-align:left;">
      <span><span style="display:block;font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--mint);">Gemeente Moerdijk · 26 t/m 31 oktober</span><span class="vw-heading" style="display:block;font-size:20px;margin-top:4px;">Gratis Energiescanweek: we komen gratis langs voor eerlijk advies</span></span>
      <span style="font-weight:800;font-size:14px;color:var(--mint);white-space:nowrap;">Meld je aan →</span></a><!-- scan:end -->'''

def main():
    shell = open(SHELL, encoding='utf-8').read()
    open('energiescan.html', 'w', encoding='utf-8').write(page(shell, main_html(), 'energiescan',
        'Gratis Energiescanweek Moerdijk (26–31 okt) | Voltwijk',
        'Van 26 t/m 31 oktober komen we gratis bij je langs in de gemeente Moerdijk: meterkast, dak en salderen 2027, met persoonlijk adviesrapport. Maximaal 60 huishoudens.'))
    open('energiescan-bedankt.html', 'w', encoding='utf-8').write(page(shell, thanks_html(), 'energiescan-bedankt',
        'Aanmelding ontvangen | Voltwijk', 'Je aanmelding voor de Gratis Energiescanweek Moerdijk is ontvangen.', noindex=True))
    s = open('index.html', encoding='utf-8').read()
    s = re.sub(r'\s*<!-- scan:start -->.*?<!-- scan:end -->', '', s, flags=re.S)
    if MODE != 'uit':
        anchor = 'geen wisselende onderaannemers, geen verrassingen achteraf.</p>'
        assert s.count(anchor) == 1
        s = s.replace(anchor, anchor + '\n    ' + BAND, 1)
    open('index.html', 'w', encoding='utf-8').write(s)
    print('energiescan:', MODE)

main()
