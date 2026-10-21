// Gem heads that replace the noon's dot. Centre ≈ (512,160). Each gem: solid silhouette + cut lines (rendered as knock-outs in mono, highlights in luxe).
const gems = {
  diamond: {
    shape: 'M480 116 H544 L574 148 L512 214 L450 148 Z',
    cuts: 'M450 148 H574 M480 116 L496 148 L512 116 L528 148 L544 116 M496 148 L512 214 L528 148 M466 148 L512 214 M558 148 L512 214'
  },
  pearl: {
    shape: 'M512 116 a46 46 0 1 0 0.01 0 Z',
    cuts: 'M484 150 a30 30 0 0 1 22 -24',
    cutW: 5
  },
  drop: {
    shape: 'M512 92 C528 118 556 140 556 168 A44 44 0 0 1 468 168 C468 140 496 118 512 92 Z',
    cuts: 'M512 120 C522 136 536 150 536 168 A24 24 0 0 1 488 168 C488 150 502 136 512 120 Z M512 92 L512 120 M468 168 L488 168 M556 168 L536 168 M480 200 L496 186 M544 200 L528 186 M512 212 L512 192'
  }
};
const body = require('fs').readFileSync('body.d','utf8');
function mono(name, color, bg, id) {
  const g = gems[name], w = g.cutW || 3.2;
  return `<mask id="m-${id}" maskUnits="userSpaceOnUse" x="380" y="60" width="460" height="1100"><rect x="380" y="60" width="460" height="1100" fill="#fff"/><path d="${g.cuts}" fill="none" stroke="#000" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/></mask>
  <path fill="${color}" fill-rule="evenodd" d="${body}"/><g transform="translate(512 165) scale(1.22) translate(-512 -165)"><path fill="${color}" d="${g.shape}" mask="url(#m-${id})"/></g>`;
}
function luxe(name, id) {
  const g = gems[name];
  const fill = name === 'pearl' ? `url(#pearl-${id})` : `url(#ice-${id})`;
  const defs = `<radialGradient id="pearl-${id}" cx=".38" cy=".34" r=".75"><stop offset="0" stop-color="#fff"/><stop offset=".45" stop-color="#EFE8E2"/><stop offset=".8" stop-color="#C4B6B2"/><stop offset="1" stop-color="#8E7E80"/></radialGradient>
  <linearGradient id="ice-${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".35" stop-color="#DCE3EA"/><stop offset=".55" stop-color="#F8FAFC"/><stop offset=".75" stop-color="#B9C3CE"/><stop offset="1" stop-color="#EEF2F6"/></linearGradient>
  <linearGradient id="gold-${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9C7F4C"/><stop offset=".3" stop-color="#E9D6A6"/><stop offset=".5" stop-color="#B89A64"/><stop offset=".7" stop-color="#F2E2B8"/><stop offset="1" stop-color="#A88A55"/></linearGradient>`;
  const cutStroke = name === 'pearl' ? `stroke="#fff" stroke-opacity=".9" stroke-width="5"` : `stroke="#8C99A8" stroke-opacity=".55" stroke-width="1.6"`;
  return `<defs>${defs}</defs><path fill="url(#gold-${id})" fill-rule="evenodd" d="${body}"/><g transform="translate(512 165) scale(1.22) translate(-512 -165)"><path d="${g.shape}" fill="${fill}"/><path d="${g.cuts}" fill="none" ${cutStroke} stroke-linecap="round" stroke-linejoin="round"/>${name!=='pearl'?`<path d="${g.shape}" fill="none" stroke="#9AA6B4" stroke-width="1.4"/>`:''}</g>`;
}
module.exports = { gems, mono, luxe, body };
