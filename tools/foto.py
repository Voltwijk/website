#!/usr/bin/env python3
"""Haalt een rechtenvrije Pexels-foto op en maakt er een hoofdfoto voor een artikel van.

Gebruik:  python3 tools/foto.py <pexels-id> [<artikel-slug> ...]

- Downloadt https://images.pexels.com/photos/<id>/... (Pexels-licentie: gratis, ook commercieel,
  geen naamsvermelding verplicht) en slaat hem op als images/foto-<id>.webp (1600 px) en .jpg (1200 px, voor delen).
- Zet bij elk opgegeven artikel `image: foto-<id>` in de kop van content/artikelen/<slug>.md.
- Registreert de bron in content/fotobronnen.md.
Daarna: bash tools/publish.sh
"""
import io, os, re, sys, urllib.request
from PIL import Image

W = 1600
UA = {'User-Agent': 'Mozilla/5.0 (voltwijk.nl foto-tool)'}


def fetch(pid):
    url = f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w={W}'
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
    im = Image.open(io.BytesIO(data)).convert('RGB')
    if im.width < 1000 or im.width <= im.height:
        sys.exit(f'Foto {pid} is te klein of staand ({im.width}x{im.height}); kies een liggende foto.')
    if im.width > W:
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    base = f'images/foto-{pid}'
    im.save(base + '.webp', 'WEBP', quality=72, method=6)
    og = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)  # deelafbeelding (og:image)
    og.save(base + '.jpg', 'JPEG', quality=78, optimize=True, progressive=True)
    return im.size


def set_image(slug, name):
    p = f'content/artikelen/{slug}.md'
    if not os.path.exists(p):
        p = f'content/artikelen/artikel-{slug}.md'
    s = open(p, encoding='utf-8').read()
    head, sep, body = s.partition('\n---\n')
    if re.search(r'^image:', head, re.M):
        head = re.sub(r'^image:.*$', f'image: {name}', head, flags=re.M)
    else:
        head = re.sub(r'^(product:.*)$', r'\1\nimage: ' + name, head, count=1, flags=re.M)
    open(p, 'w', encoding='utf-8').write(head + sep + body)
    return os.path.basename(p)[:-3]


def credit(pid, slugs):
    p = 'content/fotobronnen.md'
    lines = open(p, encoding='utf-8').read().splitlines() if os.path.exists(p) else [
        '# Fotobronnen', '',
        'Hoofdfoto\'s van artikelen die niet van Voltwijk zelf zijn. Alle foto\'s komen van Pexels',
        '(Pexels-licentie: gratis te gebruiken, ook commercieel, naamsvermelding niet verplicht).', '',
        '| bestand | bron | gebruikt bij |', '|---|---|---|']
    row = f'| foto-{pid} | https://www.pexels.com/photo/{pid}/ |'
    for i, l in enumerate(lines):
        if l.startswith(row):
            used = sorted(set(x.strip() for x in l[len(row):].strip(' |').split(',') if x.strip()) | set(slugs))
            lines[i] = f'{row} {", ".join(used)} |'
            break
    else:
        lines.append(f'{row} {", ".join(sorted(slugs))} |')
    open(p, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        sys.exit(__doc__)
    pid, slugs = sys.argv[1], sys.argv[2:]
    if not os.path.exists(f'images/foto-{pid}.webp'):
        print('foto-%s: %dx%d' % ((pid,) + fetch(pid)))
    done = [set_image(s, f'foto-{pid}') for s in slugs]
    credit(pid, done)
    for s in done:
        print(f'{s}: image: foto-{pid}')
