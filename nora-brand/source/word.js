const { stroke, rhombus } = require('./nib.js');
const L = 20, A = 62*Math.PI/180, ALIF = 28*Math.PI/180;
const alif = [[22,-118,0.25],[23,-108,0.85],[22,-70,1],[20,-30,1],[22,-6,0.9],[30,2,0.4]];
const raa  = [[94,-34,0.3],[92,-28,1],[88,-16,1],[80,2,1],[62,18,0.95],[24,34,0.85],[-30,42,0.7],[-86,36,0.42],[-128,20,0.12]];
const waw  = [[251,-44,0.3],[251,-32,0.9],[248,-4,1],[236,2,1],[226,2,1],[190,2,1],[156,1,1],[138,-4,0.95],[128,-20,0.9],[136,-40,0.85],[156,-38,0.9],[160,-18,1],[152,6,1],[140,24,0.85],[124,36,0.45],[112,40,0.12]];
const noon = [[250,-32,0.35],[250,-22,0.9],[248,-4,1],[236,2,1],[226,2,1]];
const parts = [stroke(alif,L,ALIF),stroke(raa,L,A),stroke(waw,L,A)];

// hairline flourish crossing the raa swash, with a jewel diamond
// sparkle above the alif: نورا comes from نور, light
const sparkle = (x,y,r)=>`M${x} ${y-r}C${x+r*.12} ${y-r*.12} ${x+r*.12} ${y-r*.12} ${x+r} ${y}C${x+r*.12} ${y+r*.12} ${x+r*.12} ${y+r*.12} ${x} ${y+r}C${x-r*.12} ${y+r*.12} ${x-r*.12} ${y+r*.12} ${x-r} ${y}C${x-r*.12} ${y-r*.12} ${x-r*.12} ${y-r*.12} ${x} ${y-r}Z`;
// the dot of the noon is drawn as a spark of light
const dot = sparkle(232,-64,19);
const jewel = 'M-138 15 m-6 0 l6 -6 l6 6 l-6 6 z';
module.exports = { parts, dot, jewel, sparkle };
if (require.main === module) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-160 -140 430 200"><g fill="#EEEAE5">${parts.map(d=>`<path d="${d}"/>`).join('')}<path d="${dot}"/><path d="${jewel}"/></g></svg>`;
  require('fs').writeFileSync('word.svg', svg);
}
