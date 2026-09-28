# Google Analytics 4 (Data API) via een service-account, zonder extra pakketten.
# De sleutel staat in GA_SERVICE_ACCOUNT_JSON (ruwe JSON, base64 of een pad naar het .json-bestand).
# Het e-mailadres van het service-account moet in GA als "Kijker" op de property staan.
#   python3 tools/ga.py properties                      properties waar het account bij kan (Admin API)
#   python3 tools/ga.py report <property-id> [dagen]    bezoekers per dag, bronnen, pagina's, gebeurtenissen
#   python3 tools/ga.py hours <property-id> [dagen]     bezoekers per uur (voor pieken na een post)
import os, sys, json, time, base64, subprocess, tempfile, urllib.request, urllib.parse, urllib.error

def key():
    raw = os.environ.get('GA_SERVICE_ACCOUNT_JSON', '').strip()
    if not raw: sys.exit('GA_SERVICE_ACCOUNT_JSON ontbreekt')
    if not raw.startswith('{'):
        raw = open(raw).read() if os.path.exists(raw) else base64.b64decode(raw).decode()
    return json.loads(raw)

def token(k):
    b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b'=')
    now = int(time.time())
    head = b64(json.dumps({'alg': 'RS256', 'typ': 'JWT'}).encode())
    claim = b64(json.dumps({'iss': k['client_email'], 'scope': 'https://www.googleapis.com/auth/analytics.readonly',
                            'aud': 'https://oauth2.googleapis.com/token', 'iat': now, 'exp': now + 3600}).encode())
    with tempfile.NamedTemporaryFile('w', suffix='.pem') as f:
        f.write(k['private_key']); f.flush()
        sig = b64(subprocess.run(['openssl', 'dgst', '-sha256', '-sign', f.name], input=head + b'.' + claim,
                                 capture_output=True, check=True).stdout)
    data = urllib.parse.urlencode({'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                                   'assertion': (head + b'.' + claim + b'.' + sig).decode()}).encode()
    try:
        return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', data))['access_token']
    except urllib.error.HTTPError as e:
        sys.exit(f'Inloggen mislukt ({e.code}): {e.read().decode()[:300]}')

def call(tok, url, body=None):
    req = urllib.request.Request(url, method='POST' if body is not None else 'GET',
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        sys.exit(f'{e.code} {e.read().decode()[:500]}')

def run(tok, prop, dims, mets, days, limit=50, order=None, flt=None):
    body = {'dateRanges': [{'startDate': f'{days}daysAgo', 'endDate': 'today'}],
            'dimensions': [{'name': d} for d in dims], 'metrics': [{'name': m} for m in mets], 'limit': limit}
    if order: body['orderBys'] = order
    if flt: body['dimensionFilter'] = flt
    r = call(tok, f'https://analyticsdata.googleapis.com/v1beta/properties/{prop}:runReport', body)
    return [([v['value'] for v in row['dimensionValues']], [v['value'] for v in row['metricValues']]) for row in r.get('rows', [])]

def table(title, rows, heads):
    print(f'\n== {title} ==')
    print(' | '.join(heads))
    for d, m in rows: print(' | '.join(d + m))
    if not rows: print('(geen gegevens)')

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'properties'
    tok = token(key())
    if cmd == 'properties':
        r = call(tok, 'https://analyticsadmin.googleapis.com/v1beta/accountSummaries')
        for a in r.get('accountSummaries', []):
            for p in a.get('propertySummaries', []): print(a.get('displayName'), '|', p['displayName'], '|', p['property'].split('/')[-1])
        return
    prop = sys.argv[2]; days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    if cmd == 'report':
        table('Per dag', run(tok, prop, ['date'], ['activeUsers', 'sessions', 'screenPageViews'], days, order=[{'dimension': {'dimensionName': 'date'}}]), ['datum', 'gebruikers', 'sessies', 'weergaven'])
        table('Bron / medium', run(tok, prop, ['sessionSourceMedium'], ['sessions', 'activeUsers', 'engagedSessions'], days, order=[{'metric': {'metricName': 'sessions'}, 'desc': True}], limit=25), ['bron', 'sessies', 'gebruikers', 'betrokken'])
        table('Pagina\'s', run(tok, prop, ['pagePath'], ['screenPageViews', 'activeUsers'], days, order=[{'metric': {'metricName': 'screenPageViews'}, 'desc': True}], limit=25), ['pagina', 'weergaven', 'gebruikers'])
        table('Gebeurtenissen', run(tok, prop, ['eventName'], ['eventCount'], days, order=[{'metric': {'metricName': 'eventCount'}, 'desc': True}], limit=30), ['gebeurtenis', 'aantal'])
        table('Apparaat', run(tok, prop, ['deviceCategory'], ['activeUsers'], days), ['apparaat', 'gebruikers'])
        table('Plaats', run(tok, prop, ['city'], ['activeUsers'], days, order=[{'metric': {'metricName': 'activeUsers'}, 'desc': True}], limit=15), ['plaats', 'gebruikers'])
    elif cmd == 'hours':
        table('Per uur', run(tok, prop, ['dateHour', 'sessionSource'], ['sessions'], days, order=[{'dimension': {'dimensionName': 'dateHour'}}], limit=500), ['datum-uur', 'bron', 'sessies'])
    else:
        sys.exit('Onbekend commando: ' + cmd)

if __name__ == "__main__":
    main()
