# Wekelijkse websitecheck per e-mail (maandagochtend), in Voltwijk-huisstijl.
#  1. Kapotte links: alle pagina's uit de sitemap en alle interne links daarop (live site).
#  2. Indexering: welke pagina's Google wel/niet heeft opgenomen (Search Console, URL-inspectie).
#  3. Zoekprestaties: afgelopen 7 dagen t.o.v. de 7 dagen ervoor, stijgers en dalers.
#  4. Snelheid: PageSpeed-score (mobiel) van de homepage en de batterijcalculator.
# Omgevingsvariabelen: GA_SERVICE_ACCOUNT_JSON (ook voor Search Console) en SMTP_* zoals bij daily_report.py.
#   python3 tools/weekly_check.py            maakt en verstuurt de check
#   python3 tools/weekly_check.py --preview  schrijft alleen weekcheck.html
import os, sys, re, json, html, datetime, urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('GSC_SERVICE_ACCOUNT_JSON', os.environ.get('GA_SERVICE_ACCOUNT_JSON', ''))
import daily_report as dr
C, esc, n = dr.C, dr.esc, dr.n
SITE = os.environ.get('SITE_URL', 'https://voltwijk.nl')
UA = {'User-Agent': 'Mozilla/5.0 (compatible; VoltwijkSiteCheck/1.0)'}

def fetch(url, timeout=25):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e: return e.code, ''
    except Exception as e: return 0, str(e)

def links_check():
    st, sm = fetch(SITE + '/sitemap.xml')
    pages = [u.replace('https://voltwijk.nl', SITE) for u in re.findall(r'<loc>([^<]+)</loc>', sm)]
    found, broken, ext = {}, [], {}
    def page(u):
        s, body = fetch(u)
        return u, s, body
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(page, pages))
    targets = {}
    for u, s, body in res:
        if s != 200: broken.append((u, s, 'pagina uit sitemap'))
        body = re.sub(r'<script\b.*?</script>', '', body, flags=re.S)
        for h in re.findall(r'href="([^"#]+)', body):
            if h.startswith(('mailto:', 'tel:', 'javascript:', 'data:')) or 'wa.me' in h or re.search(r"[+'\s]", h): continue
            full = urllib.parse.urljoin(u, h)
            if full.startswith(SITE): targets.setdefault(full.split('?')[0], u)
            elif '/artikel-' in u and full.startswith('http'): ext.setdefault(full, u)
    internal = [t for t in targets if t not in pages and not re.search(r'\.(css|js|png|jpe?g|webp|svg|ico|xml|txt|pdf|mp4|woff2?)$', t)]
    with ThreadPoolExecutor(8) as ex:
        for t, (s, _) in zip(internal, ex.map(fetch, internal)):
            if s >= 400 or s == 0: broken.append((t, s, 'gelinkt vanaf ' + targets[t].replace(SITE, '')))
    ext_bad = []
    with ThreadPoolExecutor(6) as ex:
        for t, (s, _) in zip(ext, ex.map(lambda x: fetch(x, 15), ext)):
            if s in (404, 410): ext_bad.append((t, s, 'bron in ' + ext[t].replace(SITE, '')))
    return len(pages), len(internal), broken, ext_bad, len(ext)

def gsc():
    import gsc as g
    tok = g.token(g.key())
    sites = g.call(tok, 'GET', g.API + '/sites').get('siteEntry', [])
    prop = next((s['siteUrl'] for s in sites if s['siteUrl'] == 'sc-domain:voltwijk.nl'), None)
    if not prop: return None
    P = urllib.parse.quote(prop, safe='')
    end = datetime.date.today() - datetime.timedelta(days=2)
    def perf(a, b, dims=None, n=250):
        body = {'startDate': str(a), 'endDate': str(b), 'rowLimit': n}
        if dims: body['dimensions'] = dims
        return g.call(tok, 'POST', f'{g.API}/sites/{P}/searchAnalytics/query', body).get('rows', [])
    cur = perf(end - datetime.timedelta(days=6), end); prev = perf(end - datetime.timedelta(days=13), end - datetime.timedelta(days=7))
    qc = {r['keys'][0]: r for r in perf(end - datetime.timedelta(days=6), end, ['query'])}
    qp = {r['keys'][0]: r for r in perf(end - datetime.timedelta(days=13), end - datetime.timedelta(days=7), ['query'])}
    moves = []
    for q, r in qc.items():
        if q in qp and r['impressions'] >= 3:
            moves.append((q, qp[q]['position'], r['position'], r['impressions']))
    moves.sort(key=lambda m: m[1] - m[2])
    new = sorted([(q, r['position'], r['impressions']) for q, r in qc.items() if q not in qp], key=lambda x: -x[2])[:8]
    st, sm = fetch(SITE + '/sitemap.xml')
    urls = re.findall(r'<loc>([^<]+)</loc>', sm)
    def inspect(u):
        try:
            r = g.call(tok, 'POST', 'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect', {'inspectionUrl': u, 'siteUrl': prop, 'languageCode': 'nl'})
            ix = r.get('inspectionResult', {}).get('indexStatusResult', {})
            return u.replace('https://voltwijk.nl', '').replace(SITE, '') or '/', ix.get('verdict', '?'), ix.get('coverageState', '')
        except SystemExit as e:
            return u, 'FOUT', str(e)[:80]
    with ThreadPoolExecutor(4) as ex:
        insp = list(ex.map(inspect, urls))
    tot = lambda rows: (rows[0]['clicks'], rows[0]['impressions'], rows[0]['position']) if rows else (0, 0, 0)
    return {'cur': tot(cur), 'prev': tot(prev), 'up': [m for m in moves if m[1] - m[2] >= 1][:8],
            'down': [m for m in reversed(moves) if m[2] - m[1] >= 1][:8], 'new': new, 'insp': insp,
            'period': f'{(end - datetime.timedelta(days=6)).strftime("%d-%m")} t/m {end.strftime("%d-%m")}'}

def speed():
    out = []
    for path in ['/', '/thuisbatterij-berekenen']:
        q = urllib.parse.urlencode({'url': SITE + path, 'strategy': 'mobile', 'category': 'performance'})
        s, body = fetch('https://www.googleapis.com/pagespeedonline/v5/runPagespeed?' + q, 90)
        try:
            lh = json.loads(body)['lighthouseResult']; a = lh['audits']
            out.append((path, round(lh['categories']['performance']['score'] * 100), a['largest-contentful-paint']['displayValue'], a['cumulative-layout-shift']['displayValue']))
        except Exception:
            out.append((path, None, '-', '-'))
    return out

def build():
    npages, nlinks, broken, ext_bad, next_ = links_check()
    try: g = gsc()
    except SystemExit as e: g = None; print('Search Console overgeslagen:', e)
    sp = speed()
    sec = lambda title, inner, sub='': (f'<tr><td style="padding:22px 28px 0;"><div style="font-size:17px;font-weight:800;color:{C["ink"]};">{title}</div>'
                                        + (f'<div style="font-size:12.5px;color:{C["soft"]};margin-top:2px;">{sub}</div>' if sub else '') + f'<div style="margin-top:10px;">{inner}</div></td></tr>')
    def rows(items):
        if not items: return f'<div style="font-size:13.5px;color:{C["soft"]};">Niets te melden.</div>'
        return '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">' + ''.join(
            '<tr>' + ''.join(f'<td style="padding:7px 0;border-bottom:1px solid {C["line"]};font-size:13px;color:{C["ink"]};{"text-align:right;font-weight:700;white-space:nowrap;padding-left:10px;" if j else "word-break:break-all;"}">{esc(v)}</td>' for j, v in enumerate(it)) + '</tr>' for it in items) + '</table>'
    ok = lambda good, txt: f'<span style="display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:800;background:{C["tint"] if good else "#FDE8E4"};color:{C["primary"] if good else C["down"]};">{txt}</span>'
    parts, todo = [], []
    parts.append(sec('Kapotte links', ok(not broken, 'Alles in orde' if not broken else f'{len(broken)} probleem/problemen') + f'<div style="font-size:12.5px;color:{C["soft"]};margin:6px 0 8px;">{npages} pagina\'s met al hun interne links gecontroleerd, plus {next_} bronlinks in artikelen.</div>'
                     + rows([(b[0].replace(SITE, '') or '/', b[1] or 'geen antwoord', b[2]) for b in broken]) + (('<div style="margin-top:10px;font-size:13px;font-weight:700;">Bronlinks die niet meer bestaan</div>' + rows([(b[0], b[1], b[2]) for b in ext_bad])) if ext_bad else '')))
    if broken: todo.append(f'{len(broken)} kapotte link(s) repareren')
    if g:
        notidx = [(u, st) for u, v, st in g['insp'] if v != 'PASS']
        idx = len(g['insp']) - len(notidx)
        states = {}
        for _, st in notidx: states[st or 'Onbekend'] = states.get(st or 'Onbekend', 0) + 1
        parts.append(sec('Opgenomen in Google', ok(idx >= len(g['insp']) * 0.9, f'{idx} van {len(g["insp"])} pagina\'s geïndexeerd') + '<div style="height:8px;"></div>'
                         + rows(sorted(states.items(), key=lambda x: -x[1])) + (f'<div style="margin-top:10px;font-size:13px;font-weight:700;">Voorbeelden nog niet opgenomen</div>' + rows([(u, '') for u, _ in notidx[:8]]) if notidx else ''),
                         'Nieuwe pagina\'s hebben vaak 1–3 weken nodig. Blijft een pagina lang hangen, dan kijken we ernaar.'))
        c, p = g['cur'], g['prev']
        kpi = lambda label, a, b, fmt=n, inv=False: (f'<td width="33%" style="padding:6px;"><div style="background:#fff;border:1px solid {C["line"]};border-radius:14px;padding:12px;">'
                                                     f'<div style="font-size:12px;color:{C["soft"]};">{label}</div><div style="font-size:22px;font-weight:800;color:{C["ink"]};margin-top:2px;">{fmt(a)}</div>'
                                                     f'<div style="font-size:12px;color:{C["soft"]};">vorige week {fmt(b)}</div></div></td>')
        pos = lambda x: f'{x:.1f}'.replace('.', ',') if x else '–'
        parts.append(sec('Zoekprestaties in Google', f'<table width="100%" cellpadding="0" cellspacing="0"><tr>{kpi("Klikken", c[0], p[0])}{kpi("Vertoningen", c[1], p[1])}{kpi("Gem. positie", c[2], p[2], pos)}</tr></table>'
                         + '<div style="margin-top:12px;font-size:13px;font-weight:700;">Gestegen</div>' + rows([(q, f'{pos(a)} → {pos(b)}') for q, a, b, i in g['up']])
                         + '<div style="margin-top:12px;font-size:13px;font-weight:700;">Gedaald</div>' + rows([(q, f'{pos(a)} → {pos(b)}') for q, a, b, i in g['down']])
                         + '<div style="margin-top:12px;font-size:13px;font-weight:700;">Nieuw gevonden op</div>' + rows([(q, f'positie {pos(p_)}') for q, p_, i in g['new']]),
                         g['period'] + ' vergeleken met de week ervoor · lagere positie = beter'))
    parts.append(sec('Snelheid op mobiel', rows([(p or '/', f'score {s}' if s is not None else 'niet gemeten', f'laden {l}', f'verschuiving {c}') for p, s, l, c in sp]),
                     'Google PageSpeed. 90+ is uitstekend, 50–89 kan beter, onder 50 is slecht.'))
    if any(s is not None and s < 50 for _, s, _, _ in sp): todo.append('snelheid op mobiel is laag')
    today = datetime.datetime.now(dr.TZ)
    head = 'Alles in orde deze week.' if not todo else 'Aandacht nodig: ' + '; '.join(todo) + '.'
    body = f'''<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Voltwijk weekcheck</title></head>
<body style="margin:0;padding:0;background:{C["bg"]};font-family:'Nunito Sans',Segoe UI,Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:{C["bg"]};"><tr><td align="center" style="padding:24px 12px;">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;background:#fff;border-radius:22px;overflow:hidden;border:1px solid {C["line"]};">
<tr><td style="background:{C["dark"]};padding:26px 28px;">
  <img src="{dr.LOGO}" width="150" alt="VOLTWIJK" style="display:block;border:0;color:#fff;font-size:22px;font-weight:800;letter-spacing:.08em;">
  <div style="font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:{C["mint"]};font-weight:800;margin-top:22px;">Weekcheck website</div>
  <div style="font-size:26px;font-weight:800;color:#fff;margin-top:4px;">Week {today.isocalendar()[1]}</div>
  <div style="margin-top:16px;background:rgba(111,214,200,.14);border-radius:12px;padding:12px 14px;font-size:14px;color:#fff;">{esc(head)}</div>
</td></tr>
{''.join(parts)}
<tr><td style="padding:26px 28px 28px;"><div style="font-size:12px;color:{C["soft"]};line-height:1.6;border-top:1px solid {C["line"]};padding-top:16px;">
<a href="https://search.google.com/search-console?resource_id=sc-domain%3Avoltwijk.nl" style="color:{C["primary"]};font-weight:700;">Open Search Console</a> · <a href="https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fvoltwijk.nl%2F" style="color:{C["primary"]};font-weight:700;">Open PageSpeed</a> · <a href="https://voltwijk.nl" style="color:{C["primary"]};font-weight:700;">voltwijk.nl</a></div></td></tr>
</table><div style="font-size:11px;color:{C["soft"]};margin-top:12px;">Voltwijk B.V. · Schoenmakerij 15a, 4762 AS Zevenbergen</div></td></tr></table></body></html>'''
    subject = f'Voltwijk weekcheck week {today.isocalendar()[1]}: ' + ('alles in orde' if not todo else 'aandacht nodig')
    return subject, body, head

if __name__ == '__main__':
    subject, body, text = build()
    if '--preview' in sys.argv:
        open('weekcheck.html', 'w', encoding='utf-8').write(body); print(subject)
    else:
        dr.send(subject, body, text)
