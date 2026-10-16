import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import sys,json
FONT='fonts/Kufam-700.ttf'; TEXT=sys.argv[1] if len(sys.argv)>1 else 'نبض القصيم'
blob=hb.Blob.from_file_path(FONT); face=hb.Face(blob); font=hb.Font(face)
buf=hb.Buffer(); buf.add_str(TEXT); buf.guess_segment_properties(); hb.shape(font,buf,{})
tt=TTFont(FONT); gs=tt.getGlyphSet(); order=tt.getGlyphOrder()
upm=tt['head'].unitsPerEm
def draw(pen):
    x=0
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        g=order[info.codepoint]
        tp=TransformPen(pen,(1,0,0,-1,x+pos.x_offset,-pos.y_offset))  # flip y; baseline at 0
        gs[g].draw(tp); x+=pos.x_advance
    return x
bp=BoundsPen(gs); adv=draw(bp); print('bounds',bp.bounds,'adv',adv,'upm',upm,file=sys.stderr)
sp=SVGPathPen(gs); draw(sp); print(json.dumps({'d':sp.getCommands(),'bounds':bp.bounds,'upm':upm}))
