// دور التسميع — يستقبل إشعارات الزوم (Webhooks) ويرتب الطالبات حسب وقت الدخول تلقائياً.
// بدون أي مكتبات خارجية: يحتاج Node 18 أو أحدث فقط.
'use strict';

const http = require('http');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT) || 3000;
const SECRET = process.env.ZOOM_WEBHOOK_SECRET_TOKEN || '';
const PASSWORD = process.env.TEACHER_PASSWORD || '';
// رقم اجتماع الحلقة (اختياري) حتى ما تختلط اجتماعات ثانية في نفس الحساب
const MEETING_ID = (process.env.MEETING_ID || '').replace(/\D/g, '');
// أسماء تُستثنى من الدور (المعلمة مثلاً)، مفصولة بفواصل
const IGNORE = (process.env.IGNORE_NAMES || '').split(',').map(norm).filter(Boolean);
const DATA_FILE = process.env.DATA_FILE || path.join(__dirname, 'data.json');

if (!SECRET) console.warn('تنبيه: ZOOM_WEBHOOK_SECRET_TOKEN غير مضبوط، لن يُقبل أي إشعار من الزوم.');
if (!PASSWORD) console.warn('تنبيه: TEACHER_PASSWORD غير مضبوط، صفحة المعلمة مفتوحة لأي أحد عنده الرابط.');

function norm(s) {
  return String(s || '')
    .normalize('NFKC')
    .replace(/[ً-ْـ]/g, '') // التشكيل والتطويل
    .replace(/[أإآ]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}

// ---------- الحالة ----------
let state = { meetingId: null, startedAt: null, seq: 0, current: null, students: [] };
try { state = { ...state, ...JSON.parse(fs.readFileSync(DATA_FILE, 'utf8')) }; } catch (_) {}
let saveTimer = null;
function save() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    fs.writeFile(DATA_FILE, JSON.stringify(state, null, 2), () => {});
  }, 200);
}

const find = (id) => state.students.find((s) => s.id === id);
const waiting = () => state.students.filter((s) => s.status === 'waiting');

function startNext() {
  // أول طالبة في الانتظار وموجودة حالياً في الاجتماع
  const next = waiting().find((s) => s.present) || null;
  state.current = next ? next.id : null;
  if (next) next.status = 'now';
}

function newSession(meetingId) {
  state = { meetingId: meetingId || null, startedAt: Date.now(), seq: 0, current: null, students: [] };
}

function onJoin(name, time) {
  const key = norm(name);
  if (!key || IGNORE.includes(key)) return;
  const existing = state.students.find((s) => s.key === key);
  if (existing) {
    // رجعت بعد انقطاع: تحتفظ بدورها الأصلي
    existing.present = true;
    existing.rejoins = (existing.rejoins || 0) + 1;
  } else {
    state.seq += 1;
    state.students.push({
      id: state.seq, n: state.seq, key, name: String(name).trim(),
      joinedAt: time, present: true, status: 'waiting', later: false, rejoins: 0,
    });
    state.students.sort((a, b) => a.joinedAt - b.joinedAt || a.id - b.id);
    state.students.forEach((s, i) => { s.n = i + 1; });
  }
  if (state.current == null) startNext();
}

function onLeave(name) {
  const s = state.students.find((x) => x.key === norm(name));
  if (s) s.present = false;
}

function act(action, id) {
  const s = id != null ? find(Number(id)) : null;
  switch (action) {
    case 'next': {
      const c = state.current != null && find(state.current);
      if (c) { c.status = 'done'; c.doneAt = Date.now(); }
      state.current = null; startNext(); break;
    }
    case 'later': {
      const target = s || (state.current != null && find(state.current));
      if (!target) break;
      state.students.splice(state.students.indexOf(target), 1);
      target.status = 'waiting'; target.later = true;
      state.students.push(target);
      if (state.current === target.id) { state.current = null; startNext(); }
      break;
    }
    case 'now': {
      if (!s || s.status !== 'waiting') break;
      const c = state.current != null && find(state.current);
      if (c) c.status = 'waiting';
      s.status = 'now'; state.current = s.id; break;
    }
    case 'remove': {
      if (!s) break;
      state.students.splice(state.students.indexOf(s), 1);
      if (state.current === s.id) { state.current = null; startNext(); }
      break;
    }
    case 'add': break; // يُعالج في المسار نفسه
    case 'reset': newSession(state.meetingId); break;
    default: return false;
  }
  return true;
}

// ---------- البث المباشر للصفحة (SSE) ----------
const clients = new Set();
function publicState() {
  return {
    startedAt: state.startedAt, current: state.current,
    students: state.students.map(({ key, ...rest }) => rest),
  };
}
function broadcast() {
  save();
  const msg = `data: ${JSON.stringify(publicState())}\n\n`;
  for (const res of clients) res.write(msg);
}
setInterval(() => { for (const res of clients) res.write(': ping\n\n'); }, 25000);

// ---------- أدوات ----------
function readBody(req, limit = 1e6) {
  return new Promise((resolve, reject) => {
    let size = 0; const chunks = [];
    req.on('data', (c) => { size += c.length; if (size > limit) { reject(new Error('too large')); req.destroy(); } else chunks.push(c); });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}
const hmac = (msg) => crypto.createHmac('sha256', SECRET).update(msg).digest('hex');
function safeEqual(a, b) {
  const x = Buffer.from(String(a)); const y = Buffer.from(String(b));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}
function authorized(req) {
  if (!PASSWORD) return true;
  const h = req.headers.authorization || '';
  if (!h.startsWith('Basic ')) return false;
  const pass = Buffer.from(h.slice(6), 'base64').toString('utf8').split(':').slice(1).join(':');
  return safeEqual(pass, PASSWORD);
}
function send(res, code, body, type = 'application/json; charset=utf-8') {
  res.writeHead(code, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(typeof body === 'string' ? body : JSON.stringify(body));
}

// ---------- الخادم ----------
const page = fs.readFileSync(path.join(__dirname, 'public', 'index.html'), 'utf8');

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  try {
    // إشعارات الزوم
    if (req.method === 'POST' && url.pathname === '/zoom/webhook') {
      const raw = await readBody(req);
      if (!SECRET) return send(res, 503, { error: 'secret not configured' });
      const ts = req.headers['x-zm-request-timestamp'];
      const sig = req.headers['x-zm-signature'];
      if (!ts || !sig || !safeEqual(sig, 'v0=' + hmac(`v0:${ts}:${raw}`))) return send(res, 401, { error: 'bad signature' });
      if (Math.abs(Date.now() / 1000 - Number(ts)) > 300) return send(res, 401, { error: 'stale request' });

      const body = JSON.parse(raw);
      if (body.event === 'endpoint.url_validation') {
        const plainToken = body.payload.plainToken;
        return send(res, 200, { plainToken, encryptedToken: hmac(plainToken) });
      }
      send(res, 200, { ok: true }); // الزوم يبي رد خلال 3 ثواني

      const obj = (body.payload && body.payload.object) || {};
      const mid = String(obj.id || '').replace(/\D/g, '');
      if (MEETING_ID && mid !== MEETING_ID) return;
      const p = obj.participant || {};
      if (body.event === 'meeting.started') {
        newSession(mid); broadcast();
      } else if (body.event === 'meeting.participant_joined') {
        if (state.meetingId && mid && state.meetingId !== mid && !MEETING_ID) newSession(mid);
        if (!state.meetingId) state.meetingId = mid;
        const t = Date.parse(p.join_time) || body.event_ts || Date.now();
        onJoin(p.user_name, t); broadcast();
      } else if (body.event === 'meeting.participant_left') {
        onLeave(p.user_name); broadcast();
      }
      return;
    }

    if (url.pathname === '/health') return send(res, 200, { ok: true });

    // كل ما يلي لصفحة المعلمة ويحتاج كلمة المرور
    if (!authorized(req)) {
      res.writeHead(401, { 'WWW-Authenticate': 'Basic realm="halaqa", charset="UTF-8"' });
      return res.end('تحتاجين كلمة المرور');
    }

    if (req.method === 'GET' && url.pathname === '/') return send(res, 200, page, 'text/html; charset=utf-8');

    if (req.method === 'GET' && url.pathname === '/events') {
      res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-store', Connection: 'keep-alive' });
      res.write(`data: ${JSON.stringify(publicState())}\n\n`);
      clients.add(res);
      req.on('close', () => clients.delete(res));
      return;
    }

    if (req.method === 'POST' && url.pathname === '/api/action') {
      const { action, id, name } = JSON.parse((await readBody(req, 1e4)) || '{}');
      if (action === 'add') { onJoin(name, Date.now()); broadcast(); return send(res, 200, { ok: true }); }
      if (!act(action, id)) return send(res, 400, { error: 'unknown action' });
      broadcast();
      return send(res, 200, { ok: true });
    }

    send(res, 404, { error: 'not found' });
  } catch (e) {
    console.error(e);
    if (!res.headersSent) send(res, 400, { error: 'bad request' });
  }
});

server.listen(PORT, () => console.log(`دور التسميع يعمل على المنفذ ${PORT}`));
