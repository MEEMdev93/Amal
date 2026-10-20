const { stroke } = require('./nib.js');
const { sparkle } = require('./word.js');
// one noon bowl, centred on x=0, opening toward -y (up) ; rotated 4x about origin
function noon(inward, L=13) {
  const k = inward ? 1 : -1;
  const pts = [[-24,k*24,0.08],[-29,k*34,0.7],[-27,k*48,1],[-14,k*60,1],[14,k*60,1],[27,k*48,1],[29,k*34,0.7],[24,k*24,0.08]];
  return pts;
}
function rot(pts, deg){const a=deg*Math.PI/180,c=Math.cos(a),s=Math.sin(a);return pts.map(([x,y,w])=>[x*c-y*s,x*s+y*c,w]);}
function mark(inward){
  let d='';
  for(const r of [0,90,180,270]){
    // rotate geometry but keep nib angle relative to the bowl so all four petals match
    const base = noon(inward);
    const s = stroke(base, 13, 62*Math.PI/180);
    d += `<path transform="rotate(${r})" d="${s}"/>`;
    const dy = inward ? 30 : 30;
    d += `<path transform="rotate(${r})" d="${sparkle(0, inward?38:-38, 7)}"/>`;
  }
  d += `<path d="${sparkle(0,0,15)}"/>`;
  return d;
}
module.exports={mark};
if(require.main===module){
  const svg=(inner)=>`<svg xmlns="http://www.w3.org/2000/svg" viewBox="-90 -90 180 180" style="width:420px"><rect x="-90" y="-90" width="180" height="180" fill="#343B26"/><g fill="#EEEAE5">${inner}</g></svg>`;
  require('fs').writeFileSync('markA.svg',svg(mark(true)));
  require('fs').writeFileSync('markB.svg',svg(mark(false)));
  require('fs').writeFileSync('mview.html',`<body style="margin:0;background:#222;display:flex;gap:20px;padding:20px"><img src="markA.svg"><img src="markB.svg"><img src="word.svg" style="width:500px;background:#2E1A31"></body>`);
}
