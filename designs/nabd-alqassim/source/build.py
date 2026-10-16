import os, json
from gen_logos import svg, SCHEMES
GREEN='#0E2E2A'; CREAM='#F1E9DA'; GOLD='#E0A43A'; INK='#1B2B28'; DEEP='#082220'; OASIS='#2F6B5E'
C=json.load(open('contact.json'))
def logo(layout,scheme,style=''):
    s=svg(layout,scheme).replace('<svg ',f'<svg style="{style}" ',1)
    return s
def pulse_d(x0,x1,y,bx,u=1.0):
    # flat line with the brand blip (small rise, deep fall) at bx; u = blip unit
    pts=[(0,0),(0.87,-1.95),(2.08,2.28),(2.97,0)]
    seg=' '.join(f'L{bx+px*u:.2f} {y+py*u:.2f}' for px,py in pts)
    return f'M{x0} {y} L{bx} {y} {seg} L{x1} {y}'
FONTS="""<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{direction:rtl}
.kufi{font-family:'Reem Kufi',sans-serif}
body{font-family:'Tajawal',sans-serif;color:%s;-webkit-print-color-adjust:exact;print-color-adjust:exact}
</style>"""%INK
def page(w,h,unit,inner,extra_css='',bg='#fff'):
    return f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">{FONTS}
<style>@page{{size:{w}{unit} {h}{unit};margin:0}} html,body{{width:{w}{unit};height:{h}{unit};background:{bg};overflow:hidden}}
.pg{{position:relative;width:{w}{unit};height:{h}{unit};overflow:hidden;background:{bg}}}{extra_css}</style></head><body><div class="pg">{inner}</div></body></html>"""

ICONS={
 'web':'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18"/>',
 'mail':'<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>',
 'at':'<circle cx="12" cy="12" r="3.6"/><path d="M15.6 12v1.4a2.6 2.6 0 0 0 5.2 0V12a8.8 8.8 0 1 0-3.5 7"/>',
 'pin':'<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
 'phone':'<path d="M6.6 3.5h3l1.5 4-2 1.3a10 10 0 0 0 6.1 6.1l1.3-2 4 1.5v3a2 2 0 0 1-2.2 2A17 17 0 0 1 4.6 5.7a2 2 0 0 1 2-2.2z"/>',
}
def ico(k,color,size): return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICONS[k]}</svg>'
def contacts(color,icolor,size,keys=('web','mail','at','pin')):
    m={'web':C['web'],'mail':C['email'],'at':C['handle'],'pin':C['city'],'phone':C['phone']}
    return ''.join(f'<span class="ci">{ico(k,icolor,size)}<span dir="{"rtl" if k=="pin" else "ltr"}">{m[k]}</span></span>' for k in keys)

# ---------- LETTERHEAD (A4, mm) ----------
def letterhead(with_fields=True, sample=False, show_contacts=True, parts=False):
    W,H=210,297
    band_top=271  # footer band top edge (mm)
    band=f'<svg class="band" viewBox="0 0 {W} 32" preserveAspectRatio="none" style="position:absolute;left:0;top:{band_top-3}mm;width:{W}mm;height:32mm">' \
         f'<path d="{pulse_d(-1,W+1,5,150,2.0)} L{W+1} 40 L-1 40Z" fill="{GREEN}"/>' \
         f'<path d="{pulse_d(-1,W+1,5,150,2.0)}" fill="none" stroke="{GOLD}" stroke-width="0.7" stroke-linejoin="round" transform="translate(0 -1.6)"/></svg>'
    divider=f'<svg viewBox="0 0 174 8" style="position:absolute;right:18mm;top:43mm;width:174mm;height:8mm"><path d="{pulse_d(0,174,4,160.5,0.95)}" fill="none" stroke="{GREEN}" stroke-width="0.35" stroke-linejoin="round" stroke-linecap="round"/><circle cx="174" cy="4" r="0.9" fill="{GOLD}"/></svg>'
    fields=''
    if with_fields:
        rows=''.join(f'<div class="f"><b>{l}</b><span class="ln"></span></div>' for l in ('الرقم','التاريخ','المرفقات'))
        fields=f'<div class="fields">{rows}</div>'
    water=f'<div style="position:absolute;left:-30mm;bottom:34mm;width:96mm;opacity:.035">{logo("icon","mono-green","width:100%;height:auto;display:block")}</div>'
    body=''
    if sample:
        body=f'''<div class="body">
<p class="to">سعادة / ............................................ &nbsp;&nbsp;&nbsp;المحترم</p>
<p>السلام عليكم ورحمة الله وبركاته، وبعد:</p>
<p>يسرّ فريق بودكاست «نبض القصيم» أن يتقدّم إليكم بخالص التحية والتقدير، ويسعدنا دعوتكم للمشاركة ضيفًا في إحدى حلقات البودكاست، التي تُعنى باكتشاف قصص النجاح والإنجاز في منطقة القصيم وتوثيقها، وتقديمها بأسلوب حواري مهني وجاذب.</p>
<p>ونتطلّع من خلال هذا اللقاء إلى إبراز تجربتكم وما أسهمتم به في نهضة المنطقة، ونقل خبراتكم إلى الأجيال الجديدة، بما يعزّز مكانة القصيم وإمكاناتها التنموية والاقتصادية والاجتماعية.</p>
<p>شاكرين لكم تعاونكم، ونسأل الله لكم التوفيق والسداد.</p>
<p class="greet">وتقبّلوا خالص التحية والتقدير،،،</p>
<div class="sign"><b>فريق بودكاست نبض القصيم</b><span>الاسم / التوقيع</span></div>
</div>'''
    css=f'''
.logo{{position:absolute;right:16mm;top:13mm;width:74mm}}
.fields{{position:absolute;left:18mm;top:15mm;width:56mm;display:flex;flex-direction:column;gap:3.2mm;font-size:9.5pt}}
.f{{display:flex;align-items:flex-end;gap:2mm}} .f b{{color:{GREEN};font-weight:700;min-width:15mm}} .f .ln{{flex:1;border-bottom:0.25mm dotted #8b9a95;height:4mm}}
.foot{{position:absolute;left:0;right:0;top:{band_top+7.5}mm;padding:0 18mm;display:flex;justify-content:space-between;align-items:center;color:{CREAM};font-size:8.6pt}}
.ci{{display:inline-flex;align-items:center;gap:1.6mm;white-space:nowrap}}
.slogan{{position:absolute;right:18mm;left:18mm;top:{band_top+16}mm;text-align:center;color:{GOLD};font-family:'Reem Kufi';font-size:10pt}}
.body{{position:absolute;top:58mm;right:22mm;left:22mm;font-size:12pt;line-height:2;text-align:justify;display:flex;flex-direction:column;gap:2.4mm}}
.body .to{{font-weight:700;color:{GREEN}}} .body .greet{{text-align:center;margin-top:2mm}}
.sign{{align-self:flex-end;margin-top:8mm;display:flex;flex-direction:column;align-items:center;gap:6mm;margin-left:6mm}} .sign b{{color:{GREEN}}} .sign span{{color:#7b8a85;font-size:10pt}}
'''
    inner=water+f'<div class="logo">{logo("horizontal","full-light","width:100%;height:auto;display:block")}</div>'+fields+divider+body+band+\
        (f'<div class="foot">{contacts(CREAM,GOLD,"3.6mm")}</div>' if show_contacts else '')+f'<div class="slogan" style="{"" if show_contacts else f"top:{band_top+10.5}mm;font-size:11pt"}">نوثّق قصص النجاح.. من قلب القصيم</div>'
    if parts: return inner,css
    return page(W,H,'mm',inner,css)

# ---------- BUSINESS CARD 90x50mm ----------
def card_front():
    inner=f'''<svg viewBox="0 0 90 50" style="position:absolute;inset:0;width:90mm;height:50mm"><path d="{pulse_d(0,90,41,62,0.9)}" fill="none" stroke="{GOLD}" stroke-width=".3" opacity=".55"/></svg>
<div style="position:absolute;top:7mm;left:0;right:0;display:flex;justify-content:center">{logo("stacked","transparent-cream","height:30mm;width:auto")}</div>'''
    return page(90,50,'mm',inner,'',GREEN)
def card_back():
    css=f'''.n{{position:absolute;right:7mm;top:7mm;display:flex;flex-direction:column;gap:.8mm}} .n b{{font-family:'Reem Kufi';font-weight:600;font-size:13pt;color:{GREEN}}} .n span{{font-size:8pt;color:{OASIS};font-weight:500}}
.cl{{position:absolute;right:7mm;bottom:6.5mm;display:flex;flex-direction:column;gap:1.4mm;font-size:7pt;color:{INK}}} .ci{{display:inline-flex;align-items:center;gap:1.5mm}}
.ic{{position:absolute;left:6mm;top:6mm;width:17mm}}'''
    inner=f'''<div class="n"><b>اسم المقدّم</b><span>مقدّم بودكاست نبض القصيم</span></div>
<div class="ic">{logo("icon","full-light","width:100%;height:auto")}</div>
<svg viewBox="0 0 90 50" style="position:absolute;inset:0;width:90mm;height:50mm"><path d="{pulse_d(7,83,24.5,70,0.55)}" fill="none" stroke="{GOLD}" stroke-width=".35" stroke-linejoin="round" transform="scale(-1 1) translate(-90 0)"/></svg>
<div class="cl">{contacts(INK,GREEN,"2.6mm",('phone','mail','at','web'))}</div>'''
    return page(90,50,'mm',inner,css,CREAM)

# ---------- ENVELOPE DL 220x110mm ----------
def envelope():
    css=f'''.ci{{display:inline-flex;align-items:center;gap:1.5mm}} .rt{{position:absolute;right:12mm;top:10mm;width:62mm}}
.ad{{position:absolute;right:12mm;top:33mm;font-size:8pt;color:#5d6d68;display:flex;flex-direction:column;gap:1mm}}
.to{{position:absolute;left:24mm;top:52mm;width:85mm;font-size:11pt;color:{INK};display:flex;flex-direction:column;gap:5mm}} .to b{{color:{GREEN}}} .to i{{display:block;border-bottom:.25mm dotted #9aa8a3;height:5mm}}'''
    inner=f'''<div class="rt">{logo("horizontal","full-light","width:100%;height:auto")}</div>
<div class="ad">{contacts("#5d6d68",GREEN,"2.8mm",('web','mail','pin'))}</div>
<div class="to"><b>إلى سعادة /</b><i></i><i></i></div>
<svg viewBox="0 0 220 12" preserveAspectRatio="none" style="position:absolute;left:0;bottom:0;width:220mm;height:12mm"><path d="{pulse_d(-1,221,5,175,1.0)} L221 13 L-1 13Z" fill="{GREEN}"/></svg>'''
    return page(220,110,'mm',inner,css)

# ---------- EPISODE COVER (px 1000, render x3) ----------
def episode_cover():
    css=f'''.num{{position:absolute;right:80px;top:70px;font-family:'Reem Kufi';color:{GOLD};font-size:30px;font-weight:500;display:flex;align-items:baseline;gap:14px}} .num b{{font-size:150px;font-weight:700;line-height:.9}}
.t{{position:absolute;right:80px;top:300px;width:520px;font-family:'Reem Kufi';font-weight:600;color:{CREAM};font-size:66px;line-height:1.25;text-wrap:balance}}
.g{{position:absolute;right:80px;top:600px;color:{CREAM};font-size:30px;opacity:.85}} .g b{{color:{GOLD};font-weight:700}}
.ph{{position:absolute;left:70px;top:150px;width:320px;height:420px;border-radius:160px 160px 18px 18px;border:3px solid {GOLD};display:flex;align-items:center;justify-content:center;color:{CREAM};opacity:.75;font-size:24px;background:rgba(241,233,218,.05)}}
.lg{{position:absolute;left:0;right:0;bottom:56px;display:flex;justify-content:center}}'''
    inner=f'''<div class="num">الحلقة<b>01</b></div>
<div class="t">من مزرعة صغيرة إلى علامة تمور عالمية</div>
<div class="g">ضيف الحلقة: <b>اسم الضيف</b></div>
<div class="ph">صورة الضيف</div>
<svg viewBox="0 0 1000 140" style="position:absolute;left:0;top:690px;width:1000px;height:140px"><path d="{pulse_d(0,1000,70,430,24)}" fill="none" stroke="{CREAM}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round" opacity=".9"/></svg>
<div class="lg">{logo("horizontal","transparent-cream","height:120px;width:auto")}</div>'''
    return page(1000,1000,'px',inner,css,GREEN)

# ---------- QUOTE POST 1080x1350 ----------
def quote_post():
    css=f'''.q{{position:absolute;right:90px;top:120px;font-family:'Reem Kufi';font-size:300px;line-height:1;color:{GOLD}}}
.tx{{position:absolute;right:90px;left:90px;top:400px;font-family:'Reem Kufi';font-weight:600;font-size:70px;line-height:1.45;color:{GREEN};text-wrap:balance}}
.by{{position:absolute;right:90px;top:880px;display:flex;flex-direction:column;gap:8px}} .by b{{font-size:38px;color:{GREEN}}} .by span{{font-size:28px;color:{OASIS}}}
.ft{{position:absolute;left:0;right:0;bottom:0;height:210px;background:{GREEN};display:flex;align-items:center;justify-content:space-between;padding:0 90px;color:{CREAM};font-size:28px}}'''
    inner=f'''<div class="q">”</div>
<div class="tx">القصيم أرض تكافئ من يصبر عليها، وكل نجاح فيها بدأ بخطوة صغيرة.</div>
<div class="by"><b>اسم الضيف</b><span>الحلقة 01 · من مزرعة صغيرة إلى علامة تمور عالمية</span></div>
<svg viewBox="0 0 1080 60" style="position:absolute;left:0;bottom:200px;width:1080px;height:60px"><path d="{pulse_d(-2,1082,50,720,20)} L1082 70 L-2 70Z" fill="{GREEN}"/></svg>
<div class="ft"><span>{logo("horizontal","transparent-cream","height:96px;width:auto")}</span><span dir="ltr">{C["handle"]}</span></div>'''
    return page(1080,1350,'px',inner,css,CREAM)

# ---------- STORY 1080x1920 ----------
def story():
    css=f'''.k{{position:absolute;top:200px;left:0;right:0;text-align:center;color:{GOLD};font-size:44px;font-weight:700;}}
.ic{{position:absolute;top:330px;left:0;right:0;display:flex;justify-content:center}}
.t{{position:absolute;top:1010px;left:110px;right:110px;text-align:center;font-family:'Reem Kufi';font-weight:600;color:{CREAM};font-size:84px;line-height:1.3;text-wrap:balance}}
.g{{position:absolute;top:1340px;left:0;right:0;text-align:center;color:{CREAM};font-size:40px;opacity:.85}} .g b{{color:{GOLD}}}
.cta{{position:absolute;top:1480px;left:50%;transform:translateX(-50%);background:{GOLD};color:{GREEN};font-weight:800;font-size:40px;padding:26px 70px;border-radius:999px;white-space:nowrap}}
.lg{{position:absolute;bottom:120px;left:0;right:0;display:flex;justify-content:center}}'''
    inner=f'''<div class="k">حلقة جديدة · الحلقة 01</div>
<div class="ic">{logo("icon","full-dark".replace("full-dark","transparent-cream"),"height:600px;width:auto")}</div>
<div class="t">من مزرعة صغيرة إلى علامة تمور عالمية</div>
<div class="g">مع <b>اسم الضيف</b></div>
<div class="cta">استمع الآن</div>
<div class="lg">{logo("wordmark","transparent-cream","height:120px;width:auto")}</div>'''
    return page(1080,1920,'px',inner,css,GREEN)

# ---------- YOUTUBE THUMB 1280x720 ----------
def thumb():
    css=f'''.ph{{position:absolute;left:0;top:0;width:520px;height:720px;background:{OASIS};display:flex;align-items:center;justify-content:center;color:{CREAM};font-size:30px;opacity:.9}}
.n{{position:absolute;right:70px;top:70px;color:{GOLD};font-family:'Reem Kufi';font-size:40px;font-weight:600}}
.t{{position:absolute;right:70px;top:150px;width:620px;color:{CREAM};font-family:'Reem Kufi';font-weight:700;font-size:78px;line-height:1.25;text-wrap:balance}}
.lg{{position:absolute;right:70px;bottom:56px}}'''
    inner=f'''<div class="ph">صورة الضيف</div>
<svg viewBox="0 0 1280 720" style="position:absolute;inset:0;width:1280px;height:720px"><path d="M520 0 L520 720" stroke="{GOLD}" stroke-width="8"/></svg>
<div class="n">الحلقة 01</div><div class="t">من مزرعة صغيرة إلى علامة تمور عالمية</div>
<div class="lg">{logo("horizontal","transparent-cream","height:110px;width:auto")}</div>'''
    return page(1280,720,'px',inner,css,GREEN)

JOBS=[
 # name, html, W(px viewport), H, scale, pdf?
 ('letterhead/nabd-alqassim-letterhead', letterhead(True), 794,1123,3,True),
 ('letterhead/nabd-alqassim-letterhead-sample', letterhead(True,True), 794,1123,2,True),
 ('letterhead/_bg', letterhead(False), 794,1123,3,False),
 ('print/business-card-front', card_front(), 340,189,6,True),
 ('print/business-card-back', card_back(), 340,189,6,True),
 ('print/envelope-dl', envelope(), 832,416,4,True),
 ('social/episode-cover-3000', episode_cover(),1000,1000,3,False),
 ('social/quote-post-1080x1350', quote_post(),1080,1350,1,False),
 ('social/story-1080x1920', story(),1080,1920,1,False),
 ('social/youtube-thumbnail-1280x720', thumb(),1280,720,1,False),
]
if __name__=='__main__':
  os.makedirs('html',exist_ok=True)
  for n,h,w,hh,s,pdf in JOBS:
    os.makedirs('out/'+os.path.dirname(n),exist_ok=True)
    f='html/'+n.replace('/','__')+'.html'; open(f,'w').write(h)
    print(f'{f}|out/{n}.png|{w}|{hh}|{s}|{"out/"+n+".pdf" if pdf else ""}')
