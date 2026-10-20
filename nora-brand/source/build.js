const fs=require('fs');
const { stroke } = require('./nib.js');
const w = require('./word.js');
// --- wordmark symbol (viewBox tight) ---
const word = [...w.parts, w.dot, w.jewel].map(d=>`<path d="${d}"/>`).join('');
// --- mark ---
const pts = [[-24,24,0.08],[-29,34,0.7],[-27,48,1],[-14,60,1],[14,60,1],[27,48,1],[29,34,0.7],[24,24,0.08]];
const bowl = stroke(pts,13,62*Math.PI/180);
let mark='';
for(const r of [0,90,180,270]) mark+=`<path transform="rotate(${r})" d="${bowl}"/><path transform="rotate(${r})" d="${w.sparkle(0,38,7)}"/>`;
mark+=`<path d="${w.sparkle(0,0,15)}"/>`;
const sym = `<symbol id="nora-ar" viewBox="-150 -92 412 146">${word}</symbol><symbol id="nora-mark" viewBox="-72 -72 144 144">${mark}</symbol><symbol id="spark" viewBox="-20 -20 40 40"><path d="${w.sparkle(0,0,19)}"/></symbol>`;
fs.writeFileSync('symbols.svg', sym);
// standalone vector files
const out=process.argv[2];
if(out){
  fs.mkdirSync(out,{recursive:true});
  const file=(vb,inner,fill)=>`<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}"><g fill="${fill}" stroke="${fill}" stroke-width="0.4" stroke-linejoin="round">${inner}</g></svg>\n`;
  for(const [n,c] of [['aubergine','#4B2A4E'],['gold','#B89A64'],['cream','#EEEAE5'],['olive','#343B26']]){
    fs.writeFileSync(`${out}/nora-arabic-logo-${n}.svg`, file('-150 -92 412 146',word,c));
    fs.writeFileSync(`${out}/nora-mark-${n}.svg`, file('-72 -72 144 144',mark,c));
  }
}
console.log((sym.length/1024).toFixed(1)+'KB');
