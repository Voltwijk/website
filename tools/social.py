# Blok "Volg Voltwijk op social media" met drie eigen video's (zelf gehost, geen Instagram-embed)
# en knoppen naar @voltwijk op Instagram en TikTok. Staat op de homepage en Over ons.
import re, os
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
VIDEOS = [
 ('social-3', 'Klant over zijn zonnepanelen', 'Hoe bevalt het, zelf je stroom opwekken?'),
 ('social-1', 'Straatquiz: weet jij wat dit is?', 'Voor 10 euro: herkennen voorbijgangers dit onderdeel van een zonne-installatie?'),
 ('social-2', 'Straatquiz: paneelbeugel', 'Herken jij een beugel voor zonnepanelen?'),
]
IG = 'https://www.instagram.com/voltwijk'
TT = 'https://www.tiktok.com/@voltwijk'
ig_svg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>'
tt_svg = '<svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 5.8A4.3 4.3 0 0 1 15.5 3h-3.1v12.4a2.6 2.6 0 1 1-2.6-2.6c.3 0 .5 0 .8.1V9.7a5.8 5.8 0 1 0 4.9 5.7V9.1a7.4 7.4 0 0 0 4.3 1.4V7.4a4.3 4.3 0 0 1-3.2-1.6z"/></svg>'
cards = ''.join(f'''<figure class="soc-card"><video controls playsinline preload="none" poster="/videos/{v}-poster.webp" aria-label="{t}"><source src="/videos/{v}.mp4" type="video/mp4"></video><figcaption><b>{t}</b><span>{d}</span></figcaption></figure>''' for v, t, d in VIDEOS)
BLOCK = f'''<!-- social:start -->
<div class="soc-sec"><div class="wrap reveal" style="padding-top:80px;padding-bottom:80px;">
  <style>
  .soc-sec{{background:var(--surface-tint);}}
  .soc-head{{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;}}
  .soc-btns{{display:flex;gap:10px;flex-wrap:wrap;}}
  .soc-btn{{display:inline-flex;align-items:center;gap:8px;padding:11px 18px;border-radius:999px;background:var(--dark);color:#fff;text-decoration:none;font-weight:800;font-size:14px;transition:transform .2s;}}
  .soc-btn.alt{{background:#fff;color:var(--ink);border:1px solid var(--border);}}
  .soc-btn:hover{{transform:translateY(-1px);}} .soc-btn:focus-visible{{outline:2px solid var(--primary);outline-offset:3px;}}
  .soc-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin-top:32px;align-items:start;}}
  .soc-card{{margin:0;background:#fff;border-radius:20px;border:1px solid var(--border);overflow:hidden;min-width:0;}}
  .soc-card video{{display:block;width:100%;aspect-ratio:9/16;object-fit:cover;background:var(--dark);}}
  .soc-card figcaption{{padding:14px 16px 16px;display:flex;flex-direction:column;gap:4px;}}
  .soc-card figcaption b{{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:15.5px;color:var(--ink);}}
  .soc-card figcaption span{{font-size:13px;color:var(--ink-soft);line-height:1.5;}}
  @media (max-width:860px){{ .soc-grid{{grid-template-columns:repeat(3,76%);overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:8px;}} .soc-card{{scroll-snap-align:start;}} }}
  </style>
  <div class="soc-head">
    <div><div class="pill">Social media</div><h2 style="font-size:clamp(28px,4vw,38px);margin-top:16px;">Volg Voltwijk op social media</h2>
    <p style="font-size:15px;color:var(--ink-soft);margin-top:8px;max-width:520px;line-height:1.6;">Klanten aan het woord, straatquizzen en een kijkje achter de schermen bij onze monteurs. Volg ons voor tips en nieuwe projecten.</p></div>
    <div class="soc-btns"><a class="soc-btn" href="{IG}" target="_blank" rel="noopener">{ig_svg}@voltwijk op Instagram</a><a class="soc-btn alt" href="{TT}" target="_blank" rel="noopener">{tt_svg}@voltwijk op TikTok</a></div>
  </div>
  <div class="soc-grid">{cards}</div>
  <script>(function(){{var vs=document.querySelectorAll('.soc-card video');vs.forEach(function(v){{v.addEventListener('play',function(){{vs.forEach(function(o){{if(o!==v)o.pause();}});}});}});}})();</script>
</div></div>
<!-- social:end -->
'''
ANCHOR = {'index.html': '  <div class="blk-mesh">\n  <!-- GARANTIE & ZEKERHEID', 'over-ons.html': '<div class="site-footer"'}
for f in ['index.html', 'over-ons.html']:
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'<!-- social:start -->.*?<!-- social:end -->\n\n?', '', s, flags=re.S)
    assert ANCHOR[f] in s, f
    s = s.replace(ANCHOR[f], BLOCK + '\n' + ANCHOR[f], 1)
    open(f, 'w', encoding='utf-8').write(s)
print('ok')
