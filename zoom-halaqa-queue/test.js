// يشغّل الخادم ويرسل له إشعارات زوم وهمية موقّعة للتأكد أن الترتيب صحيح.
'use strict';
const { spawn } = require('child_process');
const crypto = require('crypto');
const os = require('os'); const path = require('path'); const assert = require('assert');
const SECRET = 'test-secret', PASS = 'pw', PORT = 3917;
const DATA = path.join(os.tmpdir(), 'halaqa-test-' + Date.now() + '.json');
const srv = spawn(process.execPath, [path.join(__dirname, 'server.js')], {
  env: { ...process.env, PORT, ZOOM_WEBHOOK_SECRET_TOKEN: SECRET, TEACHER_PASSWORD: PASS, IGNORE_NAMES: 'المعلمة', DATA_FILE: DATA },
  stdio: 'inherit',
});
const base = `http://127.0.0.1:${PORT}`;
const auth = { Authorization: 'Basic ' + Buffer.from('t:' + PASS).toString('base64') };
async function zoom(body, badSig) {
  const raw = JSON.stringify(body); const ts = String(Math.floor(Date.now() / 1000));
  const sig = 'v0=' + crypto.createHmac('sha256', badSig ? 'x' : SECRET).update(`v0:${ts}:${raw}`).digest('hex');
  return fetch(base + '/zoom/webhook', { method: 'POST', body: raw, headers: { 'content-type': 'application/json', 'x-zm-request-timestamp': ts, 'x-zm-signature': sig } });
}
const joined = (name, t) => zoom({ event: 'meeting.participant_joined', payload: { object: { id: '123', participant: { user_name: name, join_time: t } } } });
const left = (name) => zoom({ event: 'meeting.participant_left', payload: { object: { id: '123', participant: { user_name: name } } } });
const state = async () => {
  const r = await fetch(base + '/events', { headers: auth }); const reader = r.body.getReader();
  const { value } = await reader.read(); reader.cancel();
  return JSON.parse(Buffer.from(value).toString().replace(/^data: /, ''));
};
const action = (action, id) => fetch(base + '/api/action', { method: 'POST', headers: { ...auth, 'content-type': 'application/json' }, body: JSON.stringify({ action, id }) });
(async () => {
  await new Promise((r) => setTimeout(r, 400));
  try {
    const v = await (await zoom({ event: 'endpoint.url_validation', payload: { plainToken: 'abc' } })).json();
    assert.strictEqual(v.encryptedToken, crypto.createHmac('sha256', SECRET).update('abc').digest('hex'));
    assert.strictEqual((await zoom({ event: 'x' }, true)).status, 401, 'bad signature rejected');
    assert.strictEqual((await fetch(base + '/')).status, 401, 'page needs password');

    await joined('المعلمة', '2026-11-15T17:00:00Z');
    await joined('نورة', '2026-11-15T17:00:05Z');
    await joined('سارة', '2026-11-15T17:00:02Z');   // وصل إشعارها متأخر لكنها دخلت قبل نورة
    await joined('ريم', '2026-11-15T17:00:09Z');
    let s = await state();
    assert.deepStrictEqual(s.students.map((x) => x.name), ['سارة', 'نورة', 'ريم'], 'ordered by join time, teacher ignored');
    assert.strictEqual(s.students.find((x) => x.id === s.current).name, 'نورة', 'first arrival event becomes current');

    await left('ريم'); await joined('ريم', '2026-11-15T17:05:00Z');
    s = await state();
    assert.strictEqual(s.students.length, 3); assert.strictEqual(s.students.find((x) => x.name === 'ريم').rejoins, 1, 'rejoin keeps spot');

    await action('next'); s = await state();
    assert.strictEqual(s.students.find((x) => x.id === s.current).name, 'سارة');
    await left('ريم'); await action('next'); s = await state();
    assert.strictEqual(s.current, null, 'absent student skipped');
    console.log('✓ كل الاختبارات نجحت');
  } catch (e) { console.error('✗', e.message); process.exitCode = 1; }
  srv.kill(); try { require('fs').unlinkSync(DATA); } catch (_) {}
})();
