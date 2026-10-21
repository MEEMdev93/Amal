import numpy as np, potrace
from PIL import Image, ImageFilter
im = Image.open('/root/.claude/uploads/3c6ebe54-1bb0-5f23-879f-747fcb5a7eab/600642db-image.jpg').convert('L')
a = np.array(im)
print(im.size)
dark = a < 110
dark[:, :20] = False; dark[:, -30:] = False
ys, xs = np.where(dark); print('bbox', xs.min(), xs.max(), ys.min(), ys.max())
# dot region
dy, dx = np.where(dark[:250]); print('dot', dx.min(), dx.max(), dy.min(), dy.max())
S = 4
big = im.resize((im.width*S, im.height*S), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.5))
b = np.array(big) < 110
b[:, :20*S] = False; b[:, -30*S:] = False
b[:250*S] = False   # drop the round dot; it gets replaced by a gem
bm = potrace.Bitmap(~b)
path = bm.trace(turdsize=40, alphamax=1.1, opticurve=True, opttolerance=0.25)
d = ''
for c in path:
    sp = c.start_point; d += f'M{sp.x/S:.1f} {sp.y/S:.1f}'
    for s in c.segments:
        if s.is_corner: d += f'L{s.c.x/S:.1f} {s.c.y/S:.1f}L{s.end_point.x/S:.1f} {s.end_point.y/S:.1f}'
        else: d += f'C{s.c1.x/S:.1f} {s.c1.y/S:.1f} {s.c2.x/S:.1f} {s.c2.y/S:.1f} {s.end_point.x/S:.1f} {s.end_point.y/S:.1f}'
    d += 'Z'
open('body.d','w').write(d); print(len(d))
