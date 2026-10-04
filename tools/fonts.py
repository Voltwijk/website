# Lettertypen zelf hosten in plaats van via Google Fonts: scheelt twee externe verbindingen
# (fonts.googleapis.com + fonts.gstatic.com) en een render-blokkerend stylesheet op elke pagina.
# De woff2-bestanden in /fonts zijn de Latin-subsets die Google zelf serveert (SIL Open Font License).
# Fallback-lettertypen met aangepaste maten beperken het verspringen van tekst als het webfont binnenkomt.
# Geen preload: gemeten concurreert die met de hoofdafbeelding (LCP); dankzij de fallback-maten verspringt er niets.
# Ook in dit blok: een CSS-regel die ruimte vrijhoudt voor de later ingevulde installatiedatum.
# Veilig om opnieuw te draaien.
import os, re
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)

GOOGLE = re.compile(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*'
                    r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*'
                    r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">')
BLOCK = re.compile(r'<!-- vw-fonts:start -->.*?<!-- vw-fonts:end -->', re.S)
UR = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'
NEW = ('<!-- vw-fonts:start -->'
       '<style>'
       "@font-face{font-family:'Bricolage Grotesque';font-style:normal;font-weight:400 800;font-stretch:100%;font-display:swap;"
       f"src:url(/fonts/bricolage-grotesque-v9-latin.woff2) format('woff2');unicode-range:{UR};}}"
       "@font-face{font-family:'Nunito Sans';font-style:normal;font-weight:400 800;font-stretch:100%;font-display:swap;"
       f"src:url(/fonts/nunito-sans-v19-latin.woff2) format('woff2');unicode-range:{UR};}}"
       "@font-face{font-family:'Bricolage Fallback';src:local('Arial'),local('Liberation Sans'),local('Helvetica');size-adjust:101.7%;ascent-override:91.4%;descent-override:26.5%;line-gap-override:0%;}"
       "@font-face{font-family:'Nunito Fallback';src:local('Arial'),local('Liberation Sans'),local('Helvetica');size-adjust:98.7%;ascent-override:102.4%;descent-override:35.8%;line-gap-override:0%;}"
       # ruimte voor de installatiedatum die pas na het laden wordt ingevuld (tools/order.py), zodat de hero niet verspringt
       '[data-vw-first]:empty::before{content:"wo 14 okt";visibility:hidden;}'
       '</style><!-- vw-fonts:end -->')
# Fallback direct na het webfont in elke font-family-lijst (CSS en inline styles)
FAM = [(re.compile(r"(['\"]Bricolage Grotesque['\"])(?!\s*,\s*['\"]?Bricolage Fallback)"), r"\1,'Bricolage Fallback'"),
       (re.compile(r"(['\"]Nunito Sans['\"])(?!\s*,\s*['\"]?Nunito Fallback)"), r"\1,'Nunito Fallback'")]

n = 0
for f in sorted(os.listdir('.')):
    if not f.endswith('.html'): continue
    s = open(f, encoding='utf-8').read(); o = s
    if BLOCK.search(s): s = BLOCK.sub(lambda m: NEW, s)
    else: s = GOOGLE.sub(lambda m: NEW, s)
    head, sep, rest = s.partition('<!-- vw-fonts:end -->')
    if sep:
        for rx, rp in FAM:
            # alleen in font-family-declaraties, niet in de @font-face-namen zelf
            rest = re.sub(r"\bfont(?:-family)?:[^;\"}]*", lambda m: rx.sub(rp, m.group(0)), rest)
        s = head + sep + rest
    if s != o: open(f, 'w', encoding='utf-8').write(s); n += 1
print(f'fonts.py: zelfgehoste lettertypen op {n} pagina\'s bijgewerkt')
