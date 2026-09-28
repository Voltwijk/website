# Meldt URL's aan bij IndexNow (Bing, Yandex, Seznam e.a.), zodat nieuwe en gewijzigde pagina's snel worden opgepikt.
#   python3 tools/indexnow.py                 alle URL's uit sitemap.xml
#   python3 tools/indexnow.py <base> <head>   alleen pagina's die tussen twee git-commits zijn gewijzigd
#   python3 tools/indexnow.py https://voltwijk.nl/pagina ...   losse URL's
# De sleutel staat als bestand in de root (4917db7a337963de06e28a59e8d178a7.txt) zodat zoekmachines kunnen controleren dat wij de eigenaar zijn.
import re, json, sys, subprocess, urllib.request, os
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
KEY = '4917db7a337963de06e28a59e8d178a7'
site = re.findall(r'<loc>([^<]+)</loc>', open('sitemap.xml', encoding='utf-8').read())
args = sys.argv[1:]
if args and args[0].startswith('http'):
    urls = args
elif len(args) == 2:
    files = subprocess.run(['git', 'diff', '--name-only', args[0], args[1], '--', '*.html'], capture_output=True, text=True, check=True).stdout.split()
    want = {'https://voltwijk.nl/' + ('' if f == 'index.html' else f[:-5]) for f in files if '/' not in f}
    urls = [u for u in site if u in want]
else:
    urls = site
if not urls:
    print('Geen gewijzigde pagina\'s om aan te melden'); sys.exit(0)
body = json.dumps({'host': 'voltwijk.nl', 'key': KEY, 'keyLocation': 'https://voltwijk.nl/%s.txt' % KEY, 'urlList': urls[:10000]}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
with urllib.request.urlopen(req, timeout=30) as r: print(r.status, len(urls), 'URL\'s aangemeld')
for u in urls[:20]: print(' ', u)
