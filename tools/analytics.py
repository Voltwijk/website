# Zet Google Analytics 4 op alle pagina's, maar laadt het pas nadat de bezoeker in de cookiemelding
# "Akkoord" (analytics) heeft gekozen. Zonder toestemming wordt er niets geladen en niets gemeten.
# Meet naast paginabezoeken ook: klik op WhatsApp, klik op bellen, verzonden formulieren (offerte/nieuwsbrief).
# Gebruik:  python3 tools/analytics.py G-XXXXXXXXXX     (leeg ID of 'uit' verwijdert het blok weer)
import glob, os, re, sys
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
gid = (sys.argv[1] if len(sys.argv) > 1 else '').strip()
if gid and gid != 'uit' and not re.fullmatch(r'G-[A-Z0-9]{4,}', gid): sys.exit('Ongeldig meet-ID: ' + gid)
BLOCK = '''<!-- vw-analytics:start -->
<script>
(function(){
  var ID = '%s', loaded = false;
  function ok(){ var c = window.vwConsent; if(!c){ try{ c = JSON.parse(localStorage.getItem('vwConsent')); }catch(e){} } return !!(c && c.analytics); }
  function load(){
    if(loaded || !ok()) return; loaded = true;
    window.dataLayer = window.dataLayer || []; window.gtag = function(){ dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', ID, { allow_google_signals: false, allow_ad_personalization_signals: false });
    var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID; document.head.appendChild(s);
  }
  function ev(name, params){ if(loaded && window.gtag) gtag('event', name, params || {}); }
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a[href]'); if(!a) return;
    var h = a.getAttribute('href');
    if(h.indexOf('wa.me') > -1) ev('whatsapp_klik', { pagina: location.pathname });
    else if(h.indexOf('tel:') === 0) ev('bel_klik', { pagina: location.pathname });
  }, true);
  document.addEventListener('submit', function(e){
    var f = e.target; var soort = f.closest && f.closest('#leadNewsletter') ? 'nieuwsbrief' : 'aanvraag';
    ev(soort === 'nieuwsbrief' ? 'nieuwsbrief_aanmelding' : 'generate_lead', { pagina: location.pathname, soort: soort });
  }, true);
  window.vwTrack = ev;
  window.addEventListener('vw:consent', load);
  load();
})();
</script>
<!-- vw-analytics:end -->'''
n = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    s2 = re.sub(r'\n?<!-- vw-analytics:start -->.*?<!-- vw-analytics:end -->', '', s, flags=re.S)
    if gid and gid != 'uit':
        s2 = s2.replace('</body>', BLOCK % gid + '\n</body>', 1) if '</body>' in s2 else s2.rstrip('\n') + '\n' + BLOCK % gid + '\n'
    if s2 != s: open(f, 'w', encoding='utf-8').write(s2); n += 1
print(('Google Analytics ' + gid if gid and gid != 'uit' else 'Analytics verwijderd') + ' op', n, "pagina's")
