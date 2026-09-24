# Verwerkt het W-merkteken (twee V's + koraal punt) subtiel door de site:
#  - klein merkje vóór elke .pill-label (in de tekstkleur van het label)
#  - groot, bijna onzichtbaar watermerk rechtsonder in de footer
#  - klein "eindteken" onder elk artikel (.vw-endmark, via tools/articles.py)
# Veilig om opnieuw te draaien.
import glob, re, os, urllib.parse
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
P = 'M444 0 23 1440H276L563 400L849 1438L1102 1440L1389 400L1675 1440H1928L1508 0H1270L975 1024L682 0Z'
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -200 1950 1660"><g transform="translate(0 1440) scale(1 -1)">'
       f'<path d="{P}"/><circle cx="976" cy="1440" r="176"/></g></svg>')
MASK = 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe='') + '")'
DOT = 'radial-gradient(circle var(--vwm-dot,1.2px) at 50.05% 12%, #FF6B5B 98%, transparent 100%)'
CSS = f'''/* vw-brandmark:start */
:root{{--vwm-mask:{MASK};}}
.pill::before{{content:"";width:13px;height:11px;flex-shrink:0;--vwm-dot:1.3px;background:{DOT},currentColor;-webkit-mask:var(--vwm-mask) center/contain no-repeat;mask:var(--vwm-mask) center/contain no-repeat;opacity:.9;}}
.site-footer::after{{content:"";position:absolute;right:-60px;bottom:-70px;width:420px;height:358px;pointer-events:none;z-index:0;background:rgba(255,255,255,.035);-webkit-mask:var(--vwm-mask) center/contain no-repeat;mask:var(--vwm-mask) center/contain no-repeat;}}
.site-footer > *{{position:relative;z-index:1;}}
.vw-endmark{{display:flex;align-items:center;gap:14px;margin:8px auto 36px;max-width:220px;color:var(--primary);}}
.vw-endmark::before,.vw-endmark::after{{content:"";flex:1;height:1px;background:var(--border);}}
.vw-endmark span{{width:22px;height:19px;flex-shrink:0;--vwm-dot:2.2px;background:{DOT},currentColor;-webkit-mask:var(--vwm-mask) center/contain no-repeat;mask:var(--vwm-mask) center/contain no-repeat;}}
@media (max-width:700px){{.site-footer::after{{width:260px;height:222px;right:-40px;bottom:60px;}}}}
/* vw-brandmark:end */
'''
n = 0
for f in glob.glob('*.html'):
    s = open(f, encoding='utf-8').read(); o = s
    s = re.sub(r'/\* vw-brandmark:start \*/.*?/\* vw-brandmark:end \*/\n', '', s, flags=re.S)
    s = s.replace('<style>', '<style>\n' + CSS, 1)
    if s != o: open(f, 'w', encoding='utf-8').write(s); n += 1
print(n, 'pagina\'s')
