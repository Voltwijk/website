// Tijdelijke diagnose: kan Netlify de mailserver bereiken? Wordt na de test weer verwijderd.
import net from 'node:net';
import tls from 'node:tls';
const probe = (host, port, mode) => new Promise(res => {
  const t0 = Date.now(); let banner = '';
  const done = (ok, info) => { try { s.destroy(); } catch {} res({ host, port, mode, ok, ms: Date.now() - t0, info: String(info || '').slice(0, 160) }); };
  const s = mode === 'tls' ? tls.connect({ host, port, servername: host, rejectUnauthorized: false }) : net.connect({ host, port });
  s.setTimeout(8000, () => done(false, 'timeout'));
  s.on('error', e => done(false, e.code || e.message));
  s.on('data', d => { banner += d; if (/\r?\n/.test(banner)) done(true, banner.trim() + (mode === 'tls' ? ' | cert: ' + JSON.stringify((s.getPeerCertificate() || {}).subject || {}) + ' ' + ((s.getPeerCertificate() || {}).subjectaltname || '') : '')); });
});
export default async () => {
  const r = await Promise.all([
    probe('mail.voltwijk.nl', 465, 'tls'), probe('mail.voltwijk.nl', 587, 'plain'), probe('mail.voltwijk.nl', 25, 'plain'),
    probe('smtp-relay.brevo.com', 587, 'plain')
  ]);
  return new Response(JSON.stringify(r, null, 1), { headers: { 'content-type': 'application/json' } });
};
