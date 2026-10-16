import json
P=json.load(open('parts.json'))
GREEN='#0E2E2A'; CREAM='#F1E9DA'; GOLD='#E0A43A'
SCHEMES={
 'full-dark':  dict(main=CREAM,mic=GOLD,tag=GOLD,bg=GREEN),
 'full-light': dict(main=GREEN,mic=GOLD,tag='#B9832A',bg=None),
 'transparent-cream': dict(main=CREAM,mic=GOLD,tag=GOLD,bg=None),
 'mono-green': dict(main=GREEN,mic=GREEN,tag=GREEN,bg=None),
 'mono-cream': dict(main=CREAM,mic=CREAM,tag=CREAM,bg=None),
 'mono-black': dict(main='#000',mic='#000',tag='#000',bg=None),
}
def p(k,c): return f'<path fill="{c}" fill-rule="evenodd" d="{P[k]}"/>'
def icon(s): return p('icon_cream',s['main'])+p('icon_gold',s['mic'])
def word(s): return p('word_cream',s['main'])
def tag(s): return p('tag_gold',s['tag'])
# Layouts: (viewBox, body-builder)
def stacked(s): return '450 641 3100 2743', icon(s)+word(s)+tag(s)
def iconly(s):  return '1265 641 1470 1462', icon(s)
def wordmark(s):return '450 2300 3101 1084', word(s)+tag(s)
def horizontal(s):
    # icon (x1365..2635,y741..2003) scaled to sit right of wordmark (x550..3451,y2400..3011)
    k=1.0
    ty=2838-1800*k; tx=3451+110-1365*k
    body=word(s)+tag(s)+f'<g transform="translate({tx:.1f} {ty:.1f}) scale({k})">{icon(s)}</g>'
    right=tx+2635*k
    top=min(ty+741*k,2400)
    bottom=max(ty+2003*k,3284)
    return f'450 {top-100:.0f} {right+100-450:.0f} {bottom+100-(top-100):.0f}', body
LAYOUTS=dict(stacked=stacked,icon=iconly,wordmark=wordmark,horizontal=horizontal)
def svg(layout,scheme):
    s=SCHEMES[scheme]; vb,body=LAYOUTS[layout](s)
    x,y,w,h=map(float,vb.split())
    bg=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{s["bg"]}"/>' if s['bg'] else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w:.0f}" height="{h:.0f}">{bg}{body}</svg>'
if __name__=='__main__':
    for L in LAYOUTS:
        for S in SCHEMES:
            open(f'out/logo/nabd-alqassim-{L}-{S}.svg','w').write(svg(L,S))
    # square social avatar as original
    s=SCHEMES['full-dark']; _,b=stacked(s)
    open('out/logo/nabd-alqassim-avatar.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4000 4000" width="4000" height="4000"><rect width="4000" height="4000" fill="{GREEN}"/>{b}</svg>')
    print('ok')
