# Google Search Console via een service-account (geen extra pakketten nodig).
# De sleutel (JSON van het service-account) staat in de omgevingsvariabele GSC_SERVICE_ACCOUNT_JSON
# (ruwe JSON of base64). Het e-mailadres van het service-account moet in Search Console als gebruiker
# met "Volledig" of "Eigenaar" zijn toegevoegd.
#   python3 tools/gsc.py sites                  eigendommen waar het account bij kan
#   python3 tools/gsc.py submit                 sitemap.xml indienen
#   python3 tools/gsc.py sitemaps               status van ingediende sitemaps
#   python3 tools/gsc.py report [dagen]         top zoekwoorden en pagina's (standaard 28 dagen)
#   python3 tools/gsc.py inspect <url> [...]    indexstatus van losse pagina's
#   python3 tools/gsc.py inspect-all            indexstatus van alle URL's uit sitemap.xml
import os, sys, json, time, base64, re, datetime, urllib.request, urllib.parse
import subprocess, tempfile
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
SITEMAP = 'https://voltwijk.nl/sitemap.xml'
API = 'https://www.googleapis.com/webmasters/v3'

def key():
    raw = os.environ.get('GSC_SERVICE_ACCOUNT_JSON', '').strip()
    if not raw: sys.exit('GSC_SERVICE_ACCOUNT_JSON ontbreekt')
    if not raw.startswith('{'): raw = base64.b64decode(raw).decode()
    return json.loads(raw)

def token(k):
    b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b'=')
    now = int(time.time())
    head = b64(json.dumps({'alg': 'RS256', 'typ': 'JWT'}).encode())
    claim = b64(json.dumps({'iss': k['client_email'], 'scope': 'https://www.googleapis.com/auth/webmasters',
                            'aud': 'https://oauth2.googleapis.com/token', 'iat': now, 'exp': now + 3600}).encode())
    with tempfile.NamedTemporaryFile('w', suffix='.pem') as f:  # ondertekenen met openssl (RS256)
        f.write(k['private_key']); f.flush()
        sig = b64(subprocess.run(['openssl', 'dgst', '-sha256', '-sign', f.name], input=head + b'.' + claim,
                                 capture_output=True, check=True).stdout)
    data = urllib.parse.urlencode({'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                                   'assertion': (head + b'.' + claim + b'.' + sig).decode()}).encode()
    try:
        return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', data))['access_token']
    except urllib.error.HTTPError as e:
        sys.exit(f'Inloggen met service-account mislukt ({e.code}): {e.read().decode()[:300]}')

def call(tok, method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            t = r.read(); return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        sys.exit(f'{e.code} {e.read().decode()[:400]}')

def site(tok):
    sites = call(tok, 'GET', API + '/sites').get('siteEntry', [])
    for pref in ('sc-domain:voltwijk.nl', 'https://voltwijk.nl/', 'https://www.voltwijk.nl/'):
        for s in sites:
            if s['siteUrl'] == pref: return s['siteUrl'], s['permissionLevel']
    sys.exit('Geen toegang tot voltwijk.nl. Gevonden: ' + json.dumps(sites))

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'sites'
    tok = token(key())
    if cmd == 'sites':
        print(json.dumps(call(tok, 'GET', API + '/sites'), indent=1)); return
    prop, perm = site(tok); P = urllib.parse.quote(prop, safe='')
    print('Eigendom:', prop, '| rechten:', perm)
    if cmd == 'submit':
        call(tok, 'PUT', f'{API}/sites/{P}/sitemaps/{urllib.parse.quote(SITEMAP, safe="")}'); print('Ingediend:', SITEMAP)
    elif cmd == 'sitemaps':
        for s in call(tok, 'GET', f'{API}/sites/{P}/sitemaps').get('sitemap', []):
            c = s.get('contents', [{}])[0]
            print(s['path'], '| laatst gelezen:', s.get('lastDownloaded', '-'), '| ingediend:', c.get('submitted'),
                  '| fouten:', s.get('errors'), '| waarschuwingen:', s.get('warnings'))
    elif cmd == 'report':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 28
        end = datetime.date.today() - datetime.timedelta(days=2); start = end - datetime.timedelta(days=days)
        for dim in ('query', 'page'):
            rows = call(tok, 'POST', f'{API}/sites/{P}/searchAnalytics/query',
                        {'startDate': str(start), 'endDate': str(end), 'dimensions': [dim], 'rowLimit': 40}).get('rows', [])
            print(f'\n== Top {dim} ({start} t/m {end}) ==  klikken | vertoningen | CTR | positie')
            for r in rows:
                print(f"{r['keys'][0][:70]:70} {r['clicks']:6.0f} {r['impressions']:8.0f} {r['ctr']*100:5.1f}% {r['position']:5.1f}")
            if not rows: print('(nog geen gegevens)')
    elif cmd in ('inspect', 'inspect-all'):
        urls = sys.argv[2:] if cmd == 'inspect' else re.findall(r'<loc>([^<]+)</loc>', open('sitemap.xml', encoding='utf-8').read())
        for u in urls:
            r = call(tok, 'POST', 'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect',
                     {'inspectionUrl': u, 'siteUrl': prop, 'languageCode': 'nl'})
            ix = r.get('inspectionResult', {}).get('indexStatusResult', {})
            print(f"{u:70} {ix.get('verdict','?'):8} {ix.get('coverageState','')}")
    else:
        sys.exit('Onbekend commando: ' + cmd)

main()
