const { mono, luxe } = require('./gems.js');
const VB = '380 70 460 1080';
const rows = [['#EEEAE5','#4B2A4E'],['#4B2A4E','#E2CC9A'],['#343B26','#EEEAE5']];
const cols = [['diamond','ألماسة','DIAMOND'],['pearl','لؤلؤة','PEARL'],['drop','فص قطرة','PEAR-CUT GEM']];
let i = 0, cells = '';
for (const [bg, fg] of rows) for (const [n] of cols) { i++; cells += `<div class="c" style="background:${bg}"><svg viewBox="${VB}">${mono(n, fg, bg, 'a'+i)}</svg></div>`; }
for (const [n] of cols) { i++; cells += `<div class="c" style="background:radial-gradient(circle at 50% 40%,#3A2240,#1F1222)"><svg viewBox="${VB}">${luxe(n, 'l'+i)}</svg></div>`; }
const head = cols.map(c => `<div class="h"><b>${c[1]}</b><span>${c[2]}</span></div>`).join('');
const html = `<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel&family=Amiri:wght@700&display=swap">
<style>body{margin:0;background:#160C18;color:#EEEAE5;font-family:Amiri,serif;direction:rtl;width:1500px}
.top{padding:50px 60px 20px;display:flex;justify-content:space-between;align-items:baseline}.top h1{margin:0;font-size:44px}.top span{font-family:Cinzel,serif;letter-spacing:.3em;font-size:13px;color:#E2CC9A;direction:ltr}
.g{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;padding:20px 60px 60px}.h{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid #B89A64;padding-bottom:8px}.h b{font-size:30px}.h span{font-family:Cinzel,serif;font-size:12px;letter-spacing:.3em;color:#E2CC9A;direction:ltr}
.c{height:440px;border-radius:6px;display:grid;place-items:center}.c svg{height:380px}</style>
<div class="top"><h1>رمز النون · خيارات الجوهرة</h1><span>NOURA · MONOGRAM OPTIONS</span></div><div class="g">${head}${cells}</div>`;
require('fs').writeFileSync('sheet.html', html);
