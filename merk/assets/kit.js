/* Voltwijk merkkit: visitekaartjes en e-mailhandtekening.
   Gedeeld door het brandbook (/merk) en de printrender (tools/brandkit/render.cjs).
   Kaartjes zijn in mm opgebouwd: 85 x 55 mm netto, met optionele afloop (--b). */
(function(){
  var L = window.VW_LOGOS || {};
  var n = 0;
  // unieke id's per ingevoegde svg (clipPaths botsen anders als hetzelfde logo vaker op de pagina staat)
  function svg(key){
    var s = L[key] || ''; n++;
    return s.replace(/id="(\w+)"/g, 'id="$1_' + n + '"').replace(/url\(#(\w+)\)/g, 'url(#$1_' + n + ')');
  }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  var DEF = {
    naam: 'Voornaam Achternaam',
    functie: 'Energieadviseur',
    telefoon: '085 333 56 87',
    mobiel: '',
    email: 'info@voltwijk.nl',
    web: 'voltwijk.nl',
    adres: 'Schoenmakerij 15a, 4762 AS Zevenbergen'
  };
  function data(d){ var o = {}; for(var k in DEF) o[k] = (d && d[k] != null && String(d[k]).trim() !== '') ? String(d[k]).trim() : DEF[k]; if(d && d.mobiel === '') o.mobiel = ''; return o; }

  function rows(d, cls){
    var r = [['T', d.telefoon]];
    if(d.mobiel) r.push(['M', d.mobiel]);
    r.push(['E', d.email], ['W', d.web]);
    return '<div class="vwc-rows ' + (cls || '') + '">' + r.map(function(x){ return '<div><i>' + x[0] + '</i><span>' + esc(x[1]) + '</span></div>'; }).join('') + '</div>';
  }
  var QR = '<img class="vwc-qr" alt="QR-code naar voltwijk.nl" src="' + (window.VW_KIT_BASE || '') + 'kit/qr-visitekaartje.svg">';

  var CARDS = {
    a: { naam: 'Avond', tekst: 'Donkergroen met wit logo. Rustig en premium: de standaardkaart voor adviesgesprekken.',
      front: function(d){ return '<div class="vwc-fill" style="background:#10201F"></div>' +
        '<div class="vwc-wm">' + svg('w_mono') + '</div>' +
        '<div class="vwc-safe vwc-a-f"><div class="vwc-logo">' + svg('wit') + '</div><div class="vwc-tag">Thuisbatterij &middot; Zonnepanelen &middot; Airco</div></div>'; },
      back: function(d){ return '<div class="vwc-fill" style="background:#F5F7F5"></div>' +
        '<div class="vwc-safe vwc-a-b"><div class="vwc-mark">' + svg('w') + '</div>' +
        '<div class="vwc-who"><b>' + esc(d.naam) + '</b><span>' + esc(d.functie) + '</span></div>' +
        rows(d) + '<div class="vwc-adr">' + esc(d.adres) + '</div>' + QR + '</div>'; } },
    b: { naam: 'Teal', tekst: 'Onze hoofdkleur met een groot beeldmerk. Valt op op een beurs of bij een energiescan.',
      front: function(d){ return '<div class="vwc-fill" style="background:#0F6E6B"></div>' +
        '<div class="vwc-big">' + svg('w_mono') + '</div>' +
        '<div class="vwc-safe vwc-b-f"><div class="vwc-logo">' + svg('wit') + '</div><div class="vwc-tag">Vaste prijs. Eigen monteurs.</div></div>'; },
      back: function(d){ return '<div class="vwc-fill" style="background:#FFFFFF"></div><div class="vwc-strip"></div>' +
        '<div class="vwc-safe vwc-b-b"><div class="vwc-who"><b>' + esc(d.naam) + '</b><span>' + esc(d.functie) + '</span></div>' +
        '<div class="vwc-logo-s">' + svg('kleur') + '</div>' + rows(d) + '<div class="vwc-adr">' + esc(d.adres) + '</div></div>'; } },
    c: { naam: 'Licht', tekst: 'Lichte voorkant met het logo in kleur, donkere achterkant. Fris en duidelijk.',
      front: function(d){ return '<div class="vwc-fill" style="background:#F5F7F5"></div>' +
        '<div class="vwc-safe vwc-c-f"><div class="vwc-logo">' + svg('kleur') + '</div><div class="vwc-line"></div>' +
        '<div class="vwc-tag">Thuisbatterij, zonnepanelen en airco<br>uit Zevenbergen</div></div>'; },
      back: function(d){ return '<div class="vwc-fill" style="background:#10201F"></div>' +
        '<div class="vwc-safe vwc-c-b"><div class="vwc-who"><b>' + esc(d.naam) + '</b><span>' + esc(d.functie) + '</span></div>' +
        rows(d, 'on-dark') + '<div class="vwc-adr">' + esc(d.adres) + '</div><div class="vwc-qrtile">' + QR + '</div></div>'; } }
  };

  // bleed: afloop in mm (0 voor schermweergave met ronde hoeken, 3 voor de drukker)
  function card(variant, side, d, bleed){
    var c = CARDS[variant]; if(!c) return '';
    var b = bleed || 0;
    return '<div class="vwc vwc-' + variant + (b ? ' vwc-print' : '') + '" style="--b:' + b + 'mm">' + c[side](data(d)) + '</div>';
  }

  // E-mailhandtekening: tabellen en inline stijlen, zodat Gmail, Outlook en Apple Mail hem goed tonen.
  function signature(d){
    d = data(d);
    var base = 'https://voltwijk.nl/merk/kit/mail/';
    var f = "font-family:'Nunito Sans',Arial,Helvetica,sans-serif;";
    var tel = d.telefoon.replace(/[^+0-9]/g, '').replace(/^0/, '+31');
    var mob = d.mobiel ? d.mobiel.replace(/[^+0-9]/g, '').replace(/^0/, '+31') : '';
    var line = function(label, val, href){ return '<tr><td style="' + f + 'font-size:12px;line-height:18px;color:#54615F;padding:0 8px 0 0;font-weight:700;">' + label + '</td><td style="' + f + 'font-size:12px;line-height:18px;"><a href="' + href + '" style="color:#10201F;text-decoration:none;">' + esc(val) + '</a></td></tr>'; };
    return '<table cellpadding="0" cellspacing="0" border="0" role="presentation" style="border-collapse:collapse;' + f + 'color:#10201F;">' +
      '<tr><td style="padding:0 0 10px 0;">' +
        '<div style="' + f + 'font-size:15px;line-height:20px;font-weight:800;color:#10201F;">' + esc(d.naam) + '</div>' +
        '<div style="' + f + 'font-size:12px;line-height:18px;color:#0F6E6B;font-weight:700;">' + esc(d.functie) + ' &middot; Voltwijk</div>' +
      '</td></tr>' +
      '<tr><td style="padding:0 0 10px 0;"><table cellpadding="0" cellspacing="0" border="0" role="presentation">' +
        line('T', d.telefoon, 'tel:' + tel) + (d.mobiel ? line('M', d.mobiel, 'tel:' + mob) : '') +
        line('E', d.email, 'mailto:' + d.email) + line('W', d.web, 'https://' + d.web.replace(/^https?:\/\//, '')) +
      '</table></td></tr>' +
      '<tr><td style="padding:10px 0 0 0;border-top:2px solid #6FD6C8;">' +
        '<a href="https://voltwijk.nl" style="text-decoration:none;"><img src="' + base + 'voltwijk-logo-mail.png" width="150" height="24" alt="Voltwijk" style="display:block;border:0;width:150px;height:24px;"></a>' +
        '<div style="' + f + 'font-size:11px;line-height:16px;color:#54615F;padding-top:6px;">Thuisbatterij, zonnepanelen en airco &middot; vaste prijs, eigen monteurs<br>' + esc(d.adres) + '</div>' +
      '</td></tr></table>';
  }

  window.VWKit = { card: card, cards: CARDS, signature: signature, defaults: DEF, svg: svg, esc: esc };
})();
