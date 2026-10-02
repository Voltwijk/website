# Dagelijks websiteoverzicht per e-mail (Voltwijk-huisstijl).
# Periode: gisteren 23:00 tot vandaag 23:00 (Nederlandse tijd), vergeleken met de 24 uur daarvoor.
# Bronnen: Google Analytics 4 (verplicht) en Netlify Forms (optioneel, voor het echte aantal aanvragen).
#
# Omgevingsvariabelen:
#   GA_SERVICE_ACCOUNT_JSON   sleutel van het service-account (JSON, base64 of pad)
#   GA_PROPERTY_ID            bijv. 556067391
#   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS   mailserver (poort 465 = SSL, anders STARTTLS)
#   MAIL_TO (standaard info@voltwijk.nl), MAIL_FROM (standaard SMTP_USER)
#   NETLIFY_TOKEN, NETLIFY_SITE (optioneel; site-naam, standaard tubular-lily-f28975)
#
#   python3 tools/daily_report.py            maakt het rapport en verstuurt het
#   python3 tools/daily_report.py --preview  schrijft alleen rapport.html (niets versturen)
#   python3 tools/daily_report.py --only-at-23   verstuurt alleen als het in Nederland tussen 23:00 en 23:59 is
#                                              (GitHub draait in UTC; zo klopt het in zomer- én wintertijd)
import os, sys, json, html, datetime, smtplib, ssl, urllib.request, urllib.error
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(__file__))
import ga

TZ = ZoneInfo('Europe/Amsterdam')
PROP = os.environ.get('GA_PROPERTY_ID', '556067391')
LOGO = 'https://voltwijk.nl/brand/voltwijk-logo-wit-mail.png'
C = {'primary': '#0F6E6B', 'dark': '#10201F', 'mint': '#6FD6C8', 'ink': '#10201F', 'soft': '#54615F', 'line': '#E6ECEA', 'bg': '#F5F7F5', 'tint': '#E4F0EF', 'up': '#0F6E6B', 'down': '#C6402E'}
EVENTS = [('bestelling_aangevraagd', 'Bestellingen'), ('afspraak_gepland', 'Afspraken ingepland'), ('generate_lead', 'Aanvragen via formulier'),
          ('whatsapp_klik', 'Klik op WhatsApp'), ('bel_klik', 'Klik op bellen'), ('nieuwsbrief_aanmelding', 'Nieuwsbrief-aanmeldingen'),
          ('plan_balk_klik', 'Klik op "Plan nu"'), ('afspraak_start', 'Afsprakenvenster geopend')]
FORMS = {'bestelling': 'Bestellingen', 'energiescan': 'Energiescan-aanmeldingen', 'offerte': 'Offerteaanvragen', 'contact': 'Contactberichten',
         'terugbellen': 'Terugbelverzoeken', 'nieuwsbrief': 'Nieuwsbrief', 'gids': 'Gids-downloads'}
DAG = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']
MND = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']
esc = lambda s: html.escape(str(s))

def window(end):
    start = end - datetime.timedelta(hours=24)
    hours, t = [], start
    while t < end:
        hours.append(t.strftime('%Y%m%d%H')); t += datetime.timedelta(hours=1)
    return start, end, hours

def report(tok, hours, dims, mets, limit=50, extra=None):
    d0 = datetime.datetime.strptime(hours[0], '%Y%m%d%H').date(); d1 = datetime.datetime.strptime(hours[-1], '%Y%m%d%H').date()
    body = {'dateRanges': [{'startDate': str(d0), 'endDate': str(d1)}], 'dimensions': [{'name': d} for d in dims],
            'metrics': [{'name': m} for m in mets], 'limit': limit,
            'dimensionFilter': {'filter': {'fieldName': 'dateHour', 'inListFilter': {'values': hours}}}}
    if extra: body.update(extra)
    r = ga.call(tok, f'https://analyticsdata.googleapis.com/v1beta/properties/{PROP}:runReport', body)
    return [([v['value'] for v in row.get('dimensionValues', [])], [float(v['value']) for v in row.get('metricValues', [])]) for row in r.get('rows', [])]

def totals(tok, hours):
    rows = report(tok, hours, [], ['activeUsers', 'sessions', 'screenPageViews', 'engagedSessions', 'newUsers'])
    return rows[0][1] if rows else [0, 0, 0, 0, 0]

def netlify(start, end):
    tok = os.environ.get('NETLIFY_TOKEN', '').strip()
    if not tok: return None
    site = os.environ.get('NETLIFY_SITE', 'tubular-lily-f28975')
    def get(url):
        req = urllib.request.Request('https://api.netlify.com/api/v1/' + url, headers={'Authorization': 'Bearer ' + tok})
        return json.load(urllib.request.urlopen(req))
    try:
        sid = next((s['id'] for s in get('sites?filter=all&per_page=100') if s.get('name') == site or site in (s.get('url') or '')), None)
        if not sid: return None
        forms = {f['id']: f['name'] for f in get(f'sites/{sid}/forms')}
        out, subs = {}, get(f'sites/{sid}/submissions?per_page=100')
        for s in subs:
            t = datetime.datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).astimezone(TZ)
            if start <= t < end:
                name = forms.get(s.get('form_id'), s.get('form_name', '?'))
                out.setdefault(name, []).append(s)
        return out
    except Exception as e:
        print('Netlify overgeslagen:', e); return None

def delta(a, b):
    if not b: return f'<span style="color:{C["soft"]};font-size:12px;">nieuw</span>' if a else ''
    p = round((a - b) / b * 100)
    col = C['up'] if p >= 0 else C['down']
    return f'<span style="color:{col};font-size:12px;font-weight:700;">{"▲" if p >= 0 else "▼"} {abs(p)}%</span>'

def n(x): return f'{int(round(x)):,}'.replace(',', '.')

def build(end):
    tok = ga.token(ga.key())
    start, end, hours = window(end)
    _, _, prev_hours = window(start)
    cur, prev = totals(tok, hours), totals(tok, prev_hours)
    ev = {r[0][0]: r[1][0] for r in report(tok, hours, ['eventName'], ['eventCount'])}
    evp = {r[0][0]: r[1][0] for r in report(tok, prev_hours, ['eventName'], ['eventCount'])}
    src = report(tok, hours, ['sessionSourceMedium'], ['sessions', 'activeUsers'], 10, {'orderBys': [{'metric': {'metricName': 'sessions'}, 'desc': True}]})
    pages = report(tok, hours, ['pagePath'], ['screenPageViews', 'activeUsers'], 10, {'orderBys': [{'metric': {'metricName': 'screenPageViews'}, 'desc': True}]})
    dev = report(tok, hours, ['deviceCategory'], ['activeUsers'])
    city = report(tok, hours, ['city'], ['activeUsers'], 8, {'orderBys': [{'metric': {'metricName': 'activeUsers'}, 'desc': True}]})
    per_hour = {r[0][0]: r[1][0] for r in report(tok, hours, ['dateHour'], ['sessions'], 30)}
    forms = netlify(start, end)

    def card(label, val, d):
        return (f'<td width="25%" style="padding:6px;"><div style="background:#fff;border:1px solid {C["line"]};border-radius:14px;padding:14px 12px;">'
                f'<div style="font-size:12px;color:{C["soft"]};">{label}</div><div style="font-size:26px;font-weight:800;color:{C["ink"]};margin-top:4px;">{n(val)}</div><div>{d}</div></div></td>')
    kpis = ''.join(card(l, cur[i], delta(cur[i], prev[i])) for l, i in [('Bezoekers', 0), ('Bezoeken', 1), ('Paginaweergaven', 2), ('Nieuwe bezoekers', 4)])

    def rows(items, cols):
        if not items: return f'<tr><td colspan="{len(cols)}" style="padding:10px 0;color:{C["soft"]};font-size:13px;">Geen gegevens in deze periode.</td></tr>'
        return ''.join('<tr>' + ''.join(f'<td style="padding:8px 0;border-bottom:1px solid {C["line"]};font-size:13.5px;color:{C["ink"]};{"text-align:right;font-weight:700;" if j else ""}">{esc(v)}</td>' for j, v in enumerate(it)) + '</tr>' for it in items)
    def section(title, inner, sub=''):
        return (f'<tr><td style="padding:22px 28px 0;"><div style="font-size:17px;font-weight:800;color:{C["ink"]};">{title}</div>'
                + (f'<div style="font-size:12.5px;color:{C["soft"]};margin-top:2px;">{sub}</div>' if sub else '') + f'<div style="margin-top:10px;">{inner}</div></td></tr>')
    table = lambda body: f'<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">{body}</table>'

    conv = [(label, ev.get(k, 0), evp.get(k, 0)) for k, label in EVENTS if ev.get(k) or evp.get(k)]
    conv_html = table(rows([(l, f'{n(a)}  ') for l, a, b in conv], ['a', 'b'])) if conv else f'<div style="font-size:13.5px;color:{C["soft"]};">Geen acties gemeten in deze periode.</div>'
    if forms is not None:
        fl = [(FORMS.get(k, k), n(len(v))) for k, v in sorted(forms.items(), key=lambda x: -len(x[1]))]
        forms_html = table(rows(fl, ['a', 'b'])) if fl else f'<div style="font-size:13.5px;color:{C["soft"]};">Geen nieuwe inzendingen.</div>'
        orders = forms.get('bestelling', [])
        if orders:
            forms_html += '<div style="margin-top:12px;">' + ''.join(
                f'<div style="background:{C["tint"]};border-radius:12px;padding:10px 12px;margin-top:6px;font-size:13px;color:{C["ink"]};"><b>{esc(o.get("data", {}).get("ordernummer", ""))}</b> · {esc(o.get("data", {}).get("naam", ""))} · {esc(o.get("data", {}).get("producten", ""))} · {esc(o.get("data", {}).get("totaalprijs", ""))} · {esc(o.get("data", {}).get("installatiedatum", ""))}</div>'
                for o in orders) + '</div>'
    else:
        forms_html = None

    mx = max(per_hour.values() or [1]) or 1
    bars = ''.join(
        f'<td valign="bottom" style="padding:0 1px;"><div title="{h[8:]}:00" style="height:{max(3, int(56 * per_hour.get(h, 0) / mx))}px;background:{C["primary"] if per_hour.get(h) else C["line"]};border-radius:3px 3px 0 0;"></div></td>'
        for h in hours)
    labels = ''.join(f'<td style="font-size:10px;color:{C["soft"]};text-align:center;">{h[8:] if int(h[8:]) % 3 == 2 else ""}</td>' for h in hours)
    chart = f'<table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed;"><tr style="height:60px;">{bars}</tr><tr>{labels}</tr></table>'

    fb = sum(r[1][0] for r in src if 'facebook' in r[0][0].lower() or 'instagram' in r[0][0].lower())
    def s_label(s):
        low = s.lower()
        for k, v in [('facebook', 'Facebook'), ('instagram', 'Instagram'), ('google / organic', 'Google (zoeken)'), ('bing', 'Bing'), ('flyer', 'Flyer (QR-code)'), ('(direct)', 'Direct / onbekend'), ('(not set)', 'Onbekend')]:
            if k in low: return v
        return s
    def p_label(p):
        return {'/': 'Homepage', '/energiescan': 'Energiescan', '/thuisbatterij-berekenen': 'Thuisbatterij berekenen', '/contact': 'Contact'}.get(p, p)
    def merged(items, fn):
        out = {}
        for r in items: out[fn(r[0][0])] = out.get(fn(r[0][0]), 0) + r[1][0]
        return out
    title_date = f'{DAG[end.weekday()]} {end.day} {MND[end.month - 1]}'
    period = f'{start.strftime("%d-%m %H:%M")} t/m {end.strftime("%d-%m %H:%M")}'
    highlights = []
    pl = lambda x, a, b: f'{n(x)} {a if round(x) == 1 else b}'
    if ev.get('bestelling_aangevraagd'): highlights.append(pl(ev['bestelling_aangevraagd'], 'bestelling', 'bestellingen') + ' aangevraagd')
    if ev.get('afspraak_gepland'): highlights.append(pl(ev['afspraak_gepland'], 'afspraak', 'afspraken') + ' ingepland')
    if fb: highlights.append(pl(fb, 'bezoek', 'bezoeken') + ' via Facebook/Instagram')
    hl = ' · '.join(highlights) or 'Rustige dag zonder bestellingen of afspraken.'

    parts = [section('Wat leverde het op?', conv_html, 'Gemeten acties op de website (alleen bezoekers die cookies accepteerden)')]
    if forms_html is not None: parts.append(section('Binnengekomen via formulieren', forms_html, 'Alle inzendingen in Netlify, ook zonder cookies'))
    parts += [section('Bezoeken per uur', chart, 'Van 23:00 tot 23:00'),
              section('Waar kwamen bezoekers vandaan?', table(rows([(k, n(v)) for k, v in sorted(merged(src, s_label).items(), key=lambda x: -x[1])], ['a', 'b']))),
              section('Meest bekeken pagina\'s', table(rows([(p_label(r[0][0]), n(r[1][0])) for r in pages], ['a', 'b']))),
              section('Apparaat en plaats', table(rows([({'mobile': 'Mobiel', 'desktop': 'Computer', 'tablet': 'Tablet'}.get(r[0][0], r[0][0]), n(r[1][0])) for r in dev], ['a', 'b']))
                      + '<div style="height:10px;"></div>' + table(rows([(r[0][0] if r[0][0] != '(not set)' else 'Onbekend', n(r[1][0])) for r in city], ['a', 'b'])))]

    body = f'''<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Voltwijk dagoverzicht</title></head>
<body style="margin:0;padding:0;background:{C["bg"]};font-family:'Nunito Sans',Segoe UI,Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:{C["bg"]};"><tr><td align="center" style="padding:24px 12px;">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;background:#fff;border-radius:22px;overflow:hidden;border:1px solid {C["line"]};">
<tr><td style="background:{C["dark"]};padding:26px 28px;">
  <img src="{LOGO}" width="150" alt="VOLTWIJK" style="display:block;border:0;color:#fff;font-size:22px;font-weight:800;letter-spacing:.08em;">
  <div style="font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:{C["mint"]};font-weight:800;margin-top:22px;">Dagoverzicht website</div>
  <div style="font-size:26px;font-weight:800;color:#fff;margin-top:4px;">{esc(title_date.capitalize())}</div>
  <div style="font-size:13px;color:#B8C7C4;margin-top:4px;">{period} · vergeleken met de 24 uur ervoor</div>
  <div style="margin-top:16px;background:rgba(111,214,200,.14);border-radius:12px;padding:12px 14px;font-size:14px;color:#fff;">{esc(hl)}</div>
</td></tr>
<tr><td style="padding:18px 22px 0;"><table width="100%" cellpadding="0" cellspacing="0"><tr>{kpis}</tr></table></td></tr>
{''.join(parts)}
<tr><td style="padding:26px 28px 28px;">
  <div style="font-size:12px;color:{C["soft"]};line-height:1.6;border-top:1px solid {C["line"]};padding-top:16px;">Google Analytics telt alleen bezoekers die cookies accepteren; het echte aantal ligt hoger. Cijfers van de laatste uren kunnen de volgende dag nog iets aanvullen.<br>
  <a href="https://analytics.google.com/analytics/web/#/p{PROP}/reports/intelligenthome" style="color:{C["primary"]};font-weight:700;">Open Google Analytics</a> · <a href="https://app.netlify.com/projects/tubular-lily-f28975/forms" style="color:{C["primary"]};font-weight:700;">Open formulieren</a> · <a href="https://voltwijk.nl" style="color:{C["primary"]};font-weight:700;">voltwijk.nl</a></div>
</td></tr></table>
<div style="font-size:11px;color:{C["soft"]};margin-top:12px;">Voltwijk B.V. · Schoenmakerij 15a, 4762 AS Zevenbergen</div>
</td></tr></table></body></html>'''
    subject = f'Voltwijk dagoverzicht {end.day} {MND[end.month - 1]}: ' + pl(cur[0], 'bezoeker', 'bezoekers') + (', ' + pl(ev['bestelling_aangevraagd'], 'bestelling', 'bestellingen') if ev.get('bestelling_aangevraagd') else '')
    text = f'Voltwijk dagoverzicht {period}\nBezoekers: {n(cur[0])} | Bezoeken: {n(cur[1])} | Paginaweergaven: {n(cur[2])}\n{hl}\n'
    return subject, body, text

def send(subject, body, text):
    host, user, pw = os.environ['SMTP_HOST'], os.environ['SMTP_USER'], os.environ['SMTP_PASS']
    port = int(os.environ.get('SMTP_PORT', '465'))
    to = os.environ.get('MAIL_TO', 'info@voltwijk.nl'); frm = os.environ.get('MAIL_FROM', user)
    m = EmailMessage(); m['Subject'] = subject; m['From'] = formataddr(('Voltwijk website', frm)); m['To'] = to
    m['Message-ID'] = make_msgid(domain=frm.split('@')[-1])
    m.set_content(text); m.add_alternative(body, subtype='html')
    ctx = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=ctx, timeout=60) as s: s.login(user, pw); s.send_message(m)
    else:
        with smtplib.SMTP(host, port, timeout=60) as s: s.starttls(context=ctx); s.login(user, pw); s.send_message(m)
    print('Verstuurd naar', to)

if __name__ == '__main__':
    now = datetime.datetime.now(TZ)
    if '--only-at-23' in sys.argv and now.hour != 23:
        print('Niet rond 23:00 in Nederland (nu', now.strftime('%H:%M'), '), overslaan.'); sys.exit(0)
    end = now.replace(hour=23, minute=0, second=0, microsecond=0)
    if now < end - datetime.timedelta(minutes=30): end -= datetime.timedelta(days=1)
    subject, body, text = build(end)
    if '--preview' in sys.argv:
        open('rapport.html', 'w', encoding='utf-8').write(body); print(subject); print('rapport.html geschreven')
    else:
        send(subject, body, text)
