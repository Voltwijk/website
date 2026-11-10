#!/usr/bin/env python3
"""Black Friday-actie: balk bovenaan elke pagina met de actieprijzen van de thuisbatterij.

Gebruik (vanuit de repo-root):
  python3 tools/blackfriday.py       zet de balk op alle pagina's (veilig om vaker te draaien)
  python3 tools/blackfriday.py uit   haalt de balk weer weg

Let op: geen doorgestreepte 'van'-prijs gebruiken. Bij een kortingsclaim moet de 'van'-prijs de laagste prijs
van de afgelopen 30 dagen zijn, en de actieprijzen staan al sinds oktober 2026 in de advertenties.
Prijzen komen uit tools/battery.py (PAKKETTEN).
"""
import glob, os, re, sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, 'tools')
UIT = len(sys.argv) > 1 and sys.argv[1] == 'uit'

src = open('tools/battery.py', encoding='utf-8').read()
PRIJS = {(p[0], p[1]): p[2] for p in re.findall(r"'kwh': (\d+), 'kw': \d+, 'fase': '(\d)-fase', 'prijs': (\d+)", src)}
def eur(n): return '€ ' + f'{int(n):,}'.replace(',', '.')
P10, P16 = eur(PRIJS[('10', '1')]), eur(PRIJS[('16', '1')])

BAR = f'''<!-- vw-bf:start -->
<style>
.vwbf{{display:block;background:#000;color:#fff;text-decoration:none;font-family:'Nunito Sans','Nunito Fallback',system-ui,sans-serif;font-size:14.5px;line-height:1.35;text-align:center;padding:10px 16px;}}
.vwbf b{{color:#FF6B5B;letter-spacing:.08em;margin-right:8px;}}
.vwbf u{{text-decoration:none;font-weight:800;white-space:nowrap;margin-left:8px;border-bottom:2px solid #FF6B5B;}}
.vwbf:hover u{{color:#FF6B5B;}}
.vwbf .l{{display:inline;}}
@media (max-width:760px){{.vwbf{{font-size:13px;padding:9px 12px;}} .vwbf .l{{display:none;}}}}
</style>
<a class="vwbf" href="/thuisbatterij-berekenen" data-bf=""><b>BLACK FRIDAY-ACTIE</b>Thuisbatterij 10 kWh {P10}<span class="l"> · 16 kWh {P16}</span> excl. btw, incl. installatie en EMS <u>Bereken je prijs →</u></a>
<!-- vw-bf:end -->
'''

n = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    s2 = re.sub(r'<!-- vw-bf:start -->.*?<!-- vw-bf:end -->\n?', '', s, flags=re.S)
    if not UIT and '  <!-- NAV -->' in s2:
        s2 = s2.replace('  <!-- NAV -->', BAR + '  <!-- NAV -->', 1)
    if s2 != s:
        open(f, 'w', encoding='utf-8').write(s2); n += 1
print(('Black Friday-balk weggehaald van' if UIT else 'Black Friday-balk op'), n, "pagina's")
