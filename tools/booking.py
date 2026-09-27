# Online afspraken plannen via Cal.com (cal.com/voltwijk) op de hele site.
# - Elke link of knop met data-book="huis|video|bel" (of leeg = eerst kiezen) opent een venster met de Cal.com-agenda.
# - Na een verstuurd offerte- of contactformulier verschijnt direct "Plan meteen je afspraak", met naam en e-mail al ingevuld.
# - Contactpagina krijgt een blok met de drie afspraaksoorten (#afspraak).
# - Een geboekte afspraak wordt in Google Analytics gemeten als 'afspraak_gepland' (alleen met toestemming).
# De Cal.com-scripts laden pas als iemand echt een afspraak wil plannen.
# Gebruik:  python3 tools/booking.py        (uit = python3 tools/booking.py uit)
import glob, os, re, sys
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
OFF = len(sys.argv) > 1 and sys.argv[1] == 'uit'

TYPES = [  # sleutel, Cal.com-link, titel, duur/omschrijving
    ('huis', 'voltwijk/gratis-adviesgesprek-aan-huis', 'Adviesgesprek aan huis', '60 min · een adviseur komt bij je langs en kijkt naar je woning, meterkast en dak'),
    ('video', 'voltwijk/videogesprek-met-een-adviseur', 'Videogesprek', '30 min · laat via je camera je meterkast of dak zien, zonder dat er iemand langskomt'),
    ('bel', 'voltwijk/bellen', 'Belafspraak', '15 min · we bellen je op het moment dat jou uitkomt'),
]
ICONS = {
    'huis': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/></svg>',
    'video': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="14" height="12" rx="2.5"/><path d="m16 10.5 6-3.5v10l-6-3.5"/></svg>',
    'bel': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
}
JS_TYPES = ','.join("%s:{link:'%s',t:'%s',d:'%s'}" % (k, l, t, d) for k, l, t, d in TYPES)
JS_ICONS = ','.join("%s:'%s'" % (k, v) for k, v in ICONS.items())

BLOCK = '''<!-- vw-cal:start -->
<style>
.vwb-ov{position:fixed;inset:0;z-index:9999;background:rgba(8,32,31,.62);display:flex;align-items:center;justify-content:center;padding:20px;opacity:0;transition:opacity .2s;}
.vwb-ov.open{opacity:1;}
.vwb-panel{background:#fff;border-radius:24px;width:100%;max-width:1000px;max-height:calc(100vh - 40px);display:flex;flex-direction:column;overflow:hidden;box-shadow:0 40px 90px -30px rgba(0,0,0,.55);}
.vwb-head{display:flex;align-items:center;gap:14px;padding:18px 22px;border-bottom:1px solid #E6ECEA;}
.vwb-head b{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:19px;color:#10201F;flex:1;line-height:1.25;}
.vwb-x,.vwb-back{background:#F1F5F4;border:none;border-radius:999px;cursor:pointer;color:#10201F;font:700 13.5px 'Nunito Sans',system-ui,sans-serif;}
.vwb-x{width:38px;height:38px;font-size:22px;line-height:1;flex-shrink:0;}
.vwb-back{padding:9px 14px;}
.vwb-body{overflow:auto;flex:1;-webkit-overflow-scrolling:touch;}
.vwb-choose{padding:26px 22px 28px;}
.vwb-choose p{margin:0 0 18px;color:#233532;font-size:15px;line-height:1.55;}
.vwb-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;}
.vwb-opt{display:flex;flex-direction:column;gap:8px;text-align:left;padding:20px;border-radius:18px;border:2px solid #E6ECEA;background:#fff;cursor:pointer;font-family:'Nunito Sans',system-ui,sans-serif;color:#10201F;transition:border-color .15s,transform .15s,box-shadow .15s;text-decoration:none;}
.vwb-opt:hover,.vwb-opt:focus-visible{border-color:#0F6E6B;transform:translateY(-2px);box-shadow:0 18px 34px -24px rgba(15,110,107,.7);outline:none;}
.vwb-ic{width:44px;height:44px;border-radius:14px;background:#E4F0EF;color:#0F6E6B;display:flex;align-items:center;justify-content:center;}
.vwb-opt b{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:17px;}
.vwb-opt .vwb-d{font-size:13.5px;color:#54615F;line-height:1.5;}
.vwb-opt em{font-style:normal;font-weight:800;font-size:13.5px;color:#0F6E6B;margin-top:auto;padding-top:4px;}
.vwb-free{display:inline-block;font-size:11.5px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:#0F6E6B;background:#D6EAE8;border-radius:999px;padding:4px 10px;}
.vwb-cal{min-height:560px;position:relative;}
.vwb-load{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#54615F;font:600 14px 'Nunito Sans',system-ui,sans-serif;}
.vwb-foot{padding:12px 22px;border-top:1px solid #E6ECEA;font:13px 'Nunito Sans',system-ui,sans-serif;color:#54615F;display:flex;gap:10px 18px;flex-wrap:wrap;justify-content:space-between;}
.vwb-foot a{color:#0F6E6B;font-weight:700;}
.vwb-done{padding:48px 26px;text-align:center;font-family:'Nunito Sans',system-ui,sans-serif;color:#233532;}
.vwb-done b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:24px;color:#10201F;margin:14px 0 8px;}
.vwb-after{margin-top:14px;padding:16px;border-radius:16px;background:#fff;border:1px solid #E6ECEA;color:#10201F;font-family:'Nunito Sans',system-ui,sans-serif;text-align:left;width:100%;box-sizing:border-box;}
.vwb-after b{display:block;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:16px;}
.vwb-after small{display:block;font-size:13px;color:#54615F;margin-top:4px;font-weight:400;}
.vwb-btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}
.vwb-btns button{display:inline-flex;align-items:center;gap:7px;border:2px solid #0F6E6B;background:#fff;color:#0F6E6B;border-radius:999px;padding:9px 14px;font:800 13.5px 'Nunito Sans',system-ui,sans-serif;cursor:pointer;}
.vwb-btns button:first-child{background:#0F6E6B;color:#fff;}
.vwb-btns svg{width:17px;height:17px;}
body.vwb-lock{overflow:hidden;}
@media (max-width:720px){
  .vwb-ov{padding:0;align-items:stretch;}
  .vwb-panel{max-height:none;height:100%;border-radius:0;}
  .vwb-grid{grid-template-columns:1fr;gap:10px;}
  .vwb-opt{flex-direction:row;flex-wrap:wrap;align-items:center;padding:14px 16px;gap:4px 12px;}
  .vwb-opt .vwb-ic{width:40px;height:40px;}
  .vwb-opt b{flex:1;}
  .vwb-opt .vwb-d{flex-basis:100%;}
  .vwb-opt em{display:none;}
  .vwb-head{padding:14px 16px;}
  .vwb-choose{padding:20px 16px;}
}
</style>
<script>
(function(){
  var T = {__TYPES__}, IC = {__ICONS__}, lead = {}, ov, n = 0, booked = false;
  function esc(s){ return String(s||'').replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function track(name, p){ try{ if(window.vwTrack) vwTrack(name, p); }catch(e){} }
  // Onthoud naam/e-mail/telefoon uit een verstuurd formulier, zodat de agenda die al invult.
  document.addEventListener('submit', function(e){
    var f = e.target; if(!f || !f.querySelectorAll) return;
    f.querySelectorAll('input,textarea').forEach(function(el){
      if(el.type === 'hidden' || el.name === 'bot-field' || !el.value) return;
      var k = el.name || ({email:'email', tel:'telefoon', text:'naam'})[el.type];
      if(k === 'naam' || k === 'email' || k === 'telefoon') lead[k] = el.value.trim();
    });
  }, true);
  function loadCal(){
    if(window.Cal) return;
    (function (C, A, L) { var p = function (a, ar) { a.q.push(ar); }; var d = C.document; C.Cal = C.Cal || function () { var cal = C.Cal; var ar = arguments; if (!cal.loaded) { cal.ns = {}; cal.q = cal.q || []; d.head.appendChild(d.createElement("script")).src = A; cal.loaded = true; } if (ar[0] === L) { var api = function () { p(api, arguments); }; var namespace = ar[1]; api.q = api.q || []; if (typeof namespace === "string") { cal.ns[namespace] = cal.ns[namespace] || api; p(cal.ns[namespace], ar); p(cal, ["initNamespace", namespace]); } else p(cal, ar); return; } p(cal, ar); }; })(window, "https://app.cal.com/embed/embed.js", "init");
  }
  function close(){
    if(!ov) return; ov.classList.remove('open'); document.body.classList.remove('vwb-lock');
    var o = ov; ov = null; setTimeout(function(){ o.remove(); }, 200);
  }
  function shell(title){
    if(!ov){
      ov = document.createElement('div'); ov.className = 'vwb-ov';
      ov.innerHTML = '<div class="vwb-panel" role="dialog" aria-modal="true" aria-labelledby="vwbTitle"><div class="vwb-head"><b id="vwbTitle"></b><button type="button" class="vwb-x" aria-label="Sluiten">×</button></div><div class="vwb-body"></div></div>';
      ov.addEventListener('click', function(e){ if(e.target === ov || e.target.closest('.vwb-x')) close(); });
      document.body.appendChild(ov); document.body.classList.add('vwb-lock');
      requestAnimationFrame(function(){ ov && ov.classList.add('open'); });
      ov.querySelector('.vwb-x').focus();
    }
    ov.querySelector('#vwbTitle').textContent = title;
    return ov.querySelector('.vwb-body');
  }
  function choose(){
    var b = shell('Plan je gratis afspraak');
    b.innerHTML = '<div class="vwb-choose"><p><span class="vwb-free">Gratis &amp; vrijblijvend</span><br><br>Kies hoe je ons het liefst spreekt. Je ziet direct wanneer we tijd hebben en je krijgt meteen een bevestiging per mail.</p><div class="vwb-grid">' +
      Object.keys(T).map(function(k){ return '<button type="button" class="vwb-opt" data-vwb="'+k+'"><span class="vwb-ic">'+IC[k]+'</span><b>'+T[k].t+'</b><span class="vwb-d">'+T[k].d+'</span><em>Kies een moment →</em></button>'; }).join('') +
      '</div></div>';
    b.querySelectorAll('[data-vwb]').forEach(function(x){ x.addEventListener('click', function(){ open(x.getAttribute('data-vwb'), true); }); });
  }
  function open(k, fromChoice){
    if(!T[k]){ choose(); track('afspraak_start', {pagina: location.pathname}); return; }
    var t = T[k], id = 'vwbCal' + (++n), ns = 'vw' + n;
    var b = shell(t.t + ' plannen');
    b.innerHTML = '<div class="vwb-cal" id="'+id+'"><div class="vwb-load">Agenda laden…</div></div>';
    var foot = document.createElement('div'); foot.className = 'vwb-foot';
    foot.innerHTML = (fromChoice ? '<button type="button" class="vwb-back">← Andere soort afspraak</button>' : '<span>Liever anders? Bel <a href="tel:+31853335687">085 333 56 87</a> of <a href="https://wa.me/31853335687" target="_blank" rel="noopener">app ons</a>.</span>') +
      '<span>Laadt de agenda niet? <a href="https://cal.com/'+t.link+'" target="_blank" rel="noopener">Open hem in een nieuw venster</a></span>';
    b.appendChild(foot);
    var back = foot.querySelector('.vwb-back'); if(back) back.addEventListener('click', choose);
    track('afspraak_start', {soort: k, pagina: location.pathname});
    var cfg = {theme: 'light', layout: 'month_view'};
    if(lead.naam) cfg.name = lead.naam;
    if(lead.email) cfg.email = lead.email;
    if(lead.telefoon && k === 'bel') cfg.attendeePhoneNumber = lead.telefoon.replace(/^0(?=\\d)/, '+31').replace(/[\\s-]/g, '');
    loadCal();
    Cal('init', ns, {origin: 'https://cal.com'});
    Cal.ns[ns]('inline', {elementOrSelector: '#' + id, calLink: t.link, layout: 'month_view', config: cfg});
    Cal.ns[ns]('ui', {theme: 'light', hideEventTypeDetails: false, layout: 'month_view', cssVarsPerTheme: {light: {'cal-brand': '#0F6E6B'}}});
    var done = function(){
      if(booked) return; booked = true; setTimeout(function(){ booked = false; }, 3000);
      track('afspraak_gepland', {soort: k, pagina: location.pathname});
    };
    Cal.ns[ns]('on', {action: 'bookingSuccessfulV2', callback: done});
    Cal.ns[ns]('on', {action: 'bookingSuccessful', callback: done});
    Cal.ns[ns]('on', {action: 'linkReady', callback: function(){ var l = document.querySelector('#' + id + ' .vwb-load'); if(l) l.remove(); }});
  }
  window.vwBook = open;
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') close(); });
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('[data-book]'); if(!a) return;
    e.preventDefault(); open(a.getAttribute('data-book'));
  });
  // Na een verstuurde offerte- of contactaanvraag: direct een afspraak laten inplannen.
  var AFTER = {leadCalc: 'Je aanvraag is binnen. Wil je meteen een moment vastleggen?', leadContact: 'Wil je meteen een moment vastleggen om te praten?'};
  function addAfter(block){
    var msg = AFTER[block.id]; if(!msg || block.querySelector('.vwb-after')) return;
    var s = block.querySelector('.lead-success'); if(!s) return;
    var d = document.createElement('div'); d.className = 'vwb-after';
    d.innerHTML = '<b>Plan direct je gratis adviesgesprek</b><small>' + esc(msg) + ' Kies zelf dag en tijd, dan hoef je niet op ons telefoontje te wachten.</small><div class="vwb-btns">' +
      Object.keys(T).map(function(k){ return '<button type="button" data-book="'+k+'">'+IC[k]+T[k].t+'</button>'; }).join('') + '</div>';
    s.style.flexWrap = 'wrap'; s.appendChild(d);
  }
  new MutationObserver(function(ms){
    ms.forEach(function(m){ if(m.target.getAttribute && m.target.getAttribute('data-sent') === '1') addAfter(m.target); });
  }).observe(document.documentElement, {subtree: true, attributes: true, attributeFilter: ['data-sent']});
})();
</script>
<!-- vw-cal:end -->'''.replace('__TYPES__', JS_TYPES).replace('__ICONS__', JS_ICONS)

# Blok op de contactpagina, direct onder de contactkanalen
SECTION = '''<!-- vw-cal-sectie:start -->
      <div class="ct-book reveal" id="afspraak" style="scroll-margin-top:96px;">
        <div>
          <div class="pill">Nieuw · online plannen</div>
          <h2 style="font-size:clamp(24px,3vw,30px);margin-top:14px;">Plan zelf direct een gratis afspraak</h2>
          <p style="font-size:14.5px;color:var(--ink-soft);margin-top:8px;line-height:1.55;max-width:560px;">Kies wat jou het beste uitkomt en zie meteen wanneer we tijd hebben. Je krijgt direct een bevestiging per mail.</p>
        </div>
        <div class="ct-book-grid">
%s
        </div>
      </div>
      <style>
        .ct-book{margin-top:28px;padding:30px;border-radius:24px;background:#fff;border:1px solid var(--border);}
        .ct-book-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:22px;}
        .ct-bk{display:flex;flex-direction:column;gap:8px;padding:20px;border-radius:18px;border:2px solid var(--border);text-decoration:none;color:var(--ink);transition:border-color .15s,transform .15s,box-shadow .15s;}
        .ct-bk:hover,.ct-bk:focus-visible{border-color:var(--primary);transform:translateY(-2px);box-shadow:0 18px 34px -24px rgba(15,110,107,.7);outline:none;}
        .ct-bk .ct-bk-ic{width:44px;height:44px;border-radius:14px;background:var(--surface-tint);color:var(--primary);display:flex;align-items:center;justify-content:center;}
        .ct-bk b{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:17px;}
        .ct-bk span{font-size:13.5px;color:var(--ink-faint);line-height:1.5;}
        .ct-bk em{font-style:normal;font-weight:800;font-size:13.5px;color:var(--primary);margin-top:auto;padding-top:4px;}
        @media (max-width:760px){ .ct-book{padding:22px 18px;} .ct-book-grid{grid-template-columns:1fr;gap:10px;} }
      </style>
<!-- vw-cal-sectie:end -->''' % '\n'.join(
    '          <a class="ct-bk" href="https://cal.com/%s" data-book="%s"><span class="ct-bk-ic">%s</span><b>%s</b><span>%s</span><em>Kies een moment →</em></a>' % (l, k, ICONS[k], t, d)
    for k, l, t, d in TYPES)

n = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    s2 = re.sub(r'\n?<!-- vw-cal:start -->.*?<!-- vw-cal:end -->', '', s, flags=re.S)
    s2 = re.sub(r'\n?<!-- vw-cal-sectie:start -->.*?<!-- vw-cal-sectie:end -->', '', s2, flags=re.S)
    if not OFF:
        s2 = s2.rstrip('\n') + '\n' + BLOCK + '\n'
    if not OFF and f == 'contact.html':
        anchor = '      </div>\n    </div>\n\n    <div class="wrap" style="padding-top:88px;padding-bottom:88px;">'
        assert anchor in s2, 'ankerpunt contactpagina niet gevonden'
        s2 = s2.replace(anchor, '      </div>\n' + SECTION + anchor[len('      </div>'):], 1)
    if s2 != s: open(f, 'w', encoding='utf-8').write(s2); n += 1
print(('Afspraken plannen verwijderd' if OFF else "Afspraken plannen (Cal.com) op") + ' ' + str(n) + " pagina's")
