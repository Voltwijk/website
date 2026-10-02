#!/usr/bin/env python3
# Cookiemelding als duidelijk venster midden in beeld (in plaats van een klein blokje in de hoek).
# Veilig om opnieuw te draaien: python3 tools/cookie.py   (zit in tools/publish.sh)
# - Vervangt de inhoud van <div id="vwCookie"> op alle pagina's; de bestaande knoppen (data-ck="1"/"0") en het
#   script dat de keuze opslaat, blijven werken.
# - Weigeren is net zo makkelijk als accepteren (AVG/ePrivacy): beide knoppen staan even groot naast elkaar.
import glob, os, re

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

INNER = '''
    <div class="ck-ic" aria-hidden="true"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a4 4 0 0 0 5 5 4 4 0 0 0 4.8 4.8z"/><circle cx="8.5" cy="10.5" r="1"/><circle cx="12" cy="15.5" r="1"/><circle cx="15.5" cy="12.5" r="1"/></svg></div>
    <div class="ck-title" id="vwCookieT">Mogen we cookies gebruiken?</div>
    <p>We gebruiken functionele cookies zodat de site goed werkt. Met jouw toestemming meten we ook anoniem welke pagina's bezoekers nuttig vinden, zodat we de site en ons advies kunnen verbeteren. We gebruiken geen advertentietracking en verkopen nooit gegevens.</p>
    <div class="ck-btns"><button type="button" class="ck-yes" data-ck="1">Accepteren</button><button type="button" class="ck-no" data-ck="0">Alleen noodzakelijk</button></div>
    <div class="ck-more">Je kunt je keuze altijd aanpassen. Lees ons <a href="/cookiebeleid">cookiebeleid</a> en <a href="/privacybeleid">privacybeleid</a>.</div>
  '''

STYLE = '''<!-- vw-cookie:start --><style>
#vwCookie{left:50% !important;top:50% !important;right:auto !important;bottom:auto !important;width:min(520px,calc(100vw - 32px)) !important;max-height:calc(100vh - 32px);overflow:auto;
  background:#fff !important;color:var(--ink) !important;border-radius:24px !important;padding:30px 30px 24px !important;text-align:center;z-index:200 !important;
  box-shadow:0 0 0 100vmax rgba(16,32,31,.55),0 40px 80px -30px rgba(0,0,0,.6) !important;transform:translate(-50%,-46%) !important;}
#vwCookie.is-open{transform:translate(-50%,-50%) !important;}
#vwCookie .ck-ic{width:56px;height:56px;border-radius:16px;background:var(--surface-tint);color:var(--primary);display:flex;align-items:center;justify-content:center;margin:0 auto 14px;}
#vwCookie .ck-title{display:block !important;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:700;font-size:24px !important;line-height:1.15;color:var(--ink);}
#vwCookie p{margin:10px 0 20px !important;font-size:15px !important;line-height:1.6 !important;color:var(--ink-soft) !important;}
#vwCookie .ck-btns{display:grid !important;grid-template-columns:1fr 1fr;gap:10px;}
#vwCookie .ck-btns button{width:100%;padding:16px 18px !important;border-radius:999px;font:800 15.5px 'Nunito Sans',system-ui,sans-serif !important;cursor:pointer;}
#vwCookie .ck-yes{background:var(--primary) !important;color:#fff !important;border:0 !important;}
#vwCookie .ck-yes:hover{background:var(--primary-dark) !important;}
#vwCookie .ck-no{background:#fff !important;color:var(--ink) !important;border:1.5px solid var(--border) !important;}
#vwCookie .ck-no:hover{border-color:var(--ink) !important;}
#vwCookie .ck-more{font-size:12.5px;color:var(--ink-faint);margin-top:14px;line-height:1.5;}
#vwCookie .ck-more a{color:var(--primary);}
@media (max-width:480px){#vwCookie{padding:24px 18px 18px !important;}#vwCookie .ck-btns{grid-template-columns:1fr;}#vwCookie .ck-title{font-size:21px !important;}}
</style><!-- vw-cookie:end -->'''

n = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read(); o = s
    if '<div id="vwCookie"' not in s: continue
    s = re.sub(r'(<div id="vwCookie"[^>]*>).*?(\n  </div>)', lambda m: m.group(1).replace('aria-label="Cookies"', 'aria-modal="true" aria-labelledby="vwCookieT"') + INNER.rstrip() + m.group(2), s, count=1, flags=re.S)
    s = re.sub(r'\n?<!-- vw-cookie:start -->.*?<!-- vw-cookie:end -->', '', s, flags=re.S)
    s = s.replace('</head>', STYLE + '\n</head>', 1)
    if s != o: open(f, 'w', encoding='utf-8').write(s); n += 1
print('cookie.py: cookiemelding bijgewerkt op', n, "pagina's")
