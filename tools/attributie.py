# Herkomst van een aanvraag (UTM-codes, gclid, fbclid) op elke pagina onthouden en meesturen met elk
# leadformulier (contact, terugbellen, offerte, gesprek/voorkeur, energiescan). De batterijcalculator stuurt
# deze velden zelf al mee (tools/funnel.py, zelfde sessionStorage-sleutel 'vwUtm').
# De velden (bron, utm_content, gclid, fbclid) staan ook in de verborgen formulierdefinities in index.html,
# anders laat Netlify ze vallen. Veilig om opnieuw te draaien.
import os, re
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)

JS = r'''<!-- vw-utm:start --><script>
(function(){
  var K = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid','fbclid'];
  function lees(){ try{ return JSON.parse(sessionStorage.getItem('vwUtm') || '{}') || {}; }catch(e){ return {}; } }
  try{ var u = new URLSearchParams(location.search), t = {}; K.forEach(function(k){ if(u.get(k)) t[k] = u.get(k).slice(0, 200); });
    if(Object.keys(t).length) sessionStorage.setItem('vwUtm', JSON.stringify(t)); }catch(e){}
  function velden(){ var t = lees(); return {bron: [t.utm_source, t.utm_medium, t.utm_campaign].filter(Boolean).join(' / '), utm_content: t.utm_content || '', gclid: t.gclid || '', fbclid: t.fbclid || ''}; }
  window.vwHerkomst = velden;
  var GEEN = /(^|&)form-name=(nieuwsbrief|gids)(&|$)/;
  /* fetch('/') met een Netlify-formulier: herkomst toevoegen als die er nog niet in zit */
  if(window.fetch){ var of = window.fetch;
    window.fetch = function(url, o){
      try{ if((url === '/' || url === location.origin + '/') && o && String(o.method).toUpperCase() === 'POST' && typeof o.body === 'string'
            && /(^|&)form-name=/.test(o.body) && !GEEN.test(o.body) && !/(^|&)bron=/.test(o.body)){
          var v = velden(); if(v.bron || v.gclid || v.fbclid || v.utm_content)
            o = Object.assign({}, o, {body: o.body + Object.keys(v).map(function(k){ return '&' + encodeURIComponent(k) + '=' + encodeURIComponent(v[k]); }).join('')});
      } }catch(e){}
      return of.apply(this, [url, o]);
    };
  }
  /* gewone formulieren (energiescan): verborgen velden vullen vlak voor het versturen */
  document.addEventListener('submit', function(e){ try{ var f = e.target, v = velden();
    Object.keys(v).forEach(function(k){ var el = f.querySelector && f.querySelector('input[type=hidden][name="' + k + '"]'); if(el && !el.value) el.value = v[k]; }); }catch(x){} }, true);
})();
</script><!-- vw-utm:end -->'''

BLOCK = re.compile(r'<!-- vw-utm:start -->.*?<!-- vw-utm:end -->', re.S)
n = 0
for f in sorted(os.listdir('.')):
    if not f.endswith('.html') or f == '404.html': continue
    s = open(f, encoding='utf-8').read(); o = s
    if BLOCK.search(s): s = BLOCK.sub(lambda m: JS, s)
    elif '</body>' in s: s = s.replace('</body>', JS + '\n</body>', 1)
    else: s = s.rstrip('\n') + '\n' + JS + '\n'
    if s != o: open(f, 'w', encoding='utf-8').write(s); n += 1
print(f'attributie.py: herkomst (UTM/gclid/fbclid) meesturen op {n} pagina\'s bijgewerkt')
