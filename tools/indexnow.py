# Meldt alle URL's uit sitemap.xml aan bij IndexNow (Bing, Yandex, Seznam e.a.). Draai na een live deploy:
#   python3 tools/indexnow.py
# De sleutel staat als bestand in de root (4917db7a337963de06e28a59e8d178a7.txt) zodat zoekmachines kunnen controleren dat wij de eigenaar zijn.
import re, json, urllib.request, os
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
KEY = '4917db7a337963de06e28a59e8d178a7'
urls = re.findall(r'<loc>([^<]+)</loc>', open('sitemap.xml', encoding='utf-8').read())
body = json.dumps({'host': 'voltwijk.nl', 'key': KEY, 'keyLocation': 'https://voltwijk.nl/%s.txt' % KEY, 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
with urllib.request.urlopen(req, timeout=30) as r: print(r.status, len(urls), 'URL\'s aangemeld')
