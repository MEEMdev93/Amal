// Flat-nib calligraphy: sweep a nib along Catmull-Rom centerlines, emit filled quads as one SVG path.
const NIB_ANGLE = 62 * Math.PI / 180;
function cr(pts, n = 24) {
  const out = [];
  const P = [pts[0], ...pts, pts[pts.length - 1]];
  for (let i = 1; i < P.length - 2; i++) {
    const [p0, p1, p2, p3] = [P[i - 1], P[i], P[i + 1], P[i + 2]];
    for (let t = 0; t < 1; t += 1 / n) {
      const t2 = t * t, t3 = t2 * t;
      const f = k => 0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3);
      out.push([f(0), f(1), f(2)]);
    }
  }
  out.push(pts[pts.length - 1]);
  return out;
}
function stroke(pts, L, ang = NIB_ANGLE) {
  const s = cr(pts);
  const dx = Math.cos(ang), dy = -Math.sin(ang);
  let d = '';
  for (let i = 0; i < s.length - 1; i++) {
    const a = s[i], b = s[i + 1];
    const ha = L * a[2] / 2, hb = L * b[2] / 2;
    let q = [[a[0] + dx * ha, a[1] + dy * ha], [b[0] + dx * hb, b[1] + dy * hb], [b[0] - dx * hb, b[1] - dy * hb], [a[0] - dx * ha, a[1] - dy * ha]];
    let area = 0; for (let j = 0; j < 4; j++) { const p = q[j], r = q[(j + 1) % 4]; area += p[0] * r[1] - r[0] * p[1]; }
    if (area < 0) q.reverse();
    if (Math.abs(area) < 1e-6) continue;
    d += 'M' + q.map(p => p[0].toFixed(2) + ' ' + p[1].toFixed(2)).join('L') + 'Z';
  }
  return d;
}
function rhombus(x, y, r, ang = NIB_ANGLE) {
  // calligraphic dot: square rotated to nib angle
  const c = Math.cos(ang), s = -Math.sin(ang);
  const u = [c * r, s * r], v = [-s * r * 0.9, c * r * 0.9];
  const P = [[x + u[0], y + u[1]], [x + v[0], y + v[1]], [x - u[0], y - u[1]], [x - v[0], y - v[1]]];
  return 'M' + P.map(p => p[0].toFixed(2) + ' ' + p[1].toFixed(2)).join('L') + 'Z';
}
module.exports = { stroke, rhombus };
