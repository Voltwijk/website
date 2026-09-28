# Controleert alle artikelen in content/artikelen vóór publicatie. Stopt met een fout als iets niet klopt.
#   python3 tools/check_articles.py
import glob, os, re, sys
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, 'tools')
from articles import parse, PRODUCTS
BANNED = ['voltier', 'zonne-installaties noord']
errs = []
pages = {f[:-5] for f in glob.glob('*.html')}
for p in sorted(glob.glob('content/artikelen/*.md')):
    a = parse(p); s = a['slug']; raw = open(p, encoding='utf-8').read().lower()
    e = lambda m: errs.append(f'{s}: {m}')
    for k in ('title', 'seo_title', 'description', 'category', 'product', 'lead', 'summary'):
        if not a.get(k): e(f'veld "{k}" ontbreekt')
    if a.get('product') not in PRODUCTS: e(f'onbekend product "{a.get("product")}"')
    if len(a.get('seo_title', '')) > 60: e(f'seo_title te lang ({len(a["seo_title"])} > 60)')
    if not 110 <= len(a.get('description', '')) <= 160: e(f'description {len(a.get("description", ""))} tekens (moet 110-160)')
    if a.get('date') and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', a['date']): e('date moet JJJJ-MM-DD zijn')
    if a.get('category') == 'Nieuws' and not a.get('sources'): e('nieuwsartikel zonder bronnen')
    for b in BANNED:
        if b in raw: e(f'verboden naam "{b}" gevonden')
    words = len(re.sub(r'[#*|>\-\[\]()]', ' ', a['body']).split())
    if a.get('date') and words < 700: e(f'te kort ({words} woorden, minimaal 700)')
    if a.get('date') and len(a['faq']) < 3: e('minimaal 3 veelgestelde vragen')
    for link in re.findall(r'\]\((/[^)\s#]*)', a['body']):
        if link.strip('/') and link.strip('/') not in pages and not os.path.exists('content/artikelen/' + link.strip('/') + '.md'): e(f'interne link bestaat niet: {link}')
if errs:
    print('\n'.join(errs)); sys.exit(1)
print('Alle', len(glob.glob('content/artikelen/*.md')), 'artikelen OK')
