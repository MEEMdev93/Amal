import numpy as np, potrace, sys
from PIL import Image, ImageFilter
im = Image.open('/tmp/claude-0/-home-user-Amal/3c6ebe54-1bb0-5f23-879f-747fcb5a7eab/images/1.webp').convert('L')
a = np.array(im).astype(float)
ys, xs = np.where(a > 140)
print('bbox', xs.min(), xs.max(), ys.min(), ys.max())
x0, x1, y0, y1 = xs.min()-6, xs.max()+6, ys.min()-6, ys.max()+6
crop = im.crop((x0, y0, x1, y1))
S = 4
big = crop.resize((crop.width*S, crop.height*S), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
b = np.array(big) > 140
def trace(mask, name):
    bm = potrace.Bitmap(~mask)
    path = bm.trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.2)
    d = ''
    for curve in path:
        sp = curve.start_point
        d += f'M{sp.x/S:.2f} {sp.y/S:.2f}'
        for seg in curve.segments:
            if seg.is_corner:
                d += f'L{seg.c.x/S:.2f} {seg.c.y/S:.2f}L{seg.end_point.x/S:.2f} {seg.end_point.y/S:.2f}'
            else:
                d += f'C{seg.c1.x/S:.2f} {seg.c1.y/S:.2f} {seg.c2.x/S:.2f} {seg.c2.y/S:.2f} {seg.end_point.x/S:.2f} {seg.end_point.y/S:.2f}'
        d += 'Z'
    open(name, 'w').write(d)
    print(name, len(d))
W, H = crop.width, crop.height
trace(b, 'full.d')
# split: Latin NOURA sits bottom-right
nx = (588 - x0) * S; ny = (660 - y0) * S
ar = b.copy(); ar[ny:, nx:] = False
la = np.zeros_like(b); la[ny:, nx:] = b[ny:, nx:]
trace(ar, 'ar.d'); trace(la, 'la.d')
# bboxes in crop coords
for n, m in [('ar', ar), ('la', la)]:
    yy, xx = np.where(m); print(n, xx.min()/S, yy.min()/S, xx.max()/S, yy.max()/S)
print('size', W, H)
