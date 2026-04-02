"""
export_utils.py - تصدير PDF و Excel
نظام قياس جاهزية الأقسام الحيوية اليومية
"""
import io
import os
from datetime import datetime

# ─── تصدير Excel ──────────────────────────────────────────────────────────────

def export_excel(report: dict, hospital_name: str = "مستشفى الولادة والأطفال") -> bytes:
    """تصدير التقرير كملف Excel"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import (Font, Alignment, PatternFill, Border, Side,
                                      GradientFill)
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise RuntimeError("مكتبة openpyxl غير مثبتة. شغّل: pip install openpyxl")

    wb = Workbook()
    ws = wb.active
    ws.title = "مؤشر التحضير"
    ws.sheet_view.rightToLeft = True

    # ألوان
    HEADER_COLOR = "1B4F8A"
    SUB_HEADER   = "2E86C1"
    GREEN_COLOR  = "1E8449"
    RED_COLOR    = "C0392B"
    ORANGE_COLOR = "D35400"
    LIGHT_BLUE   = "D6EAF8"
    LIGHT_GREEN  = "D5F5E3"
    LIGHT_RED    = "FADBD8"
    LIGHT_ORANGE = "FDEBD0"
    WHITE        = "FFFFFF"
    GRAY_LIGHT   = "F2F3F4"

    def style_cell(cell, bold=False, size=11, color="000000", bg=None,
                   align="center", wrap=False, border=True):
        cell.font = Font(name="Cairo", bold=bold, size=size, color=color)
        cell.alignment = Alignment(horizontal=align, vertical="center",
                                   wrapText=wrap, readingOrder=2)
        if bg:
            cell.fill = PatternFill("solid", fgColor=bg)
        if border:
            thin = Side(style="thin", color="CCCCCC")
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def merge_style(ws, r1, c1, r2, c2, value, bold=False, size=12,
                    color="FFFFFF", bg=HEADER_COLOR, align="center"):
        ws.merge_cells(start_row=r1, start_column=c1,
                       end_row=r2, end_column=c2)
        cell = ws.cell(r1, c1, value)
        style_cell(cell, bold=bold, size=size, color=color, bg=bg,
                   align=align, wrap=True)

    # ─── عنوان رئيسي ───────────────────────────────────────────────────────
    report_date = report.get("report_date", "")
    shift       = report.get("shift", "")
    try:
        dt = datetime.strptime(report_date, "%Y-%m-%d")
        ar_days = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
        day_name = ar_days[dt.weekday()]
        date_display = f"{dt.day}/{dt.month}/{dt.year} - {day_name}"
    except Exception:
        date_display = report_date

    merge_style(ws, 1, 1, 1, 9,
                f"مؤشر التحضير اليومي - {hospital_name}",
                bold=True, size=16)
    merge_style(ws, 2, 1, 2, 9,
                f"التاريخ: {date_display}   |   الشفت: {shift}",
                size=12, bg=SUB_HEADER)

    row = 4

    # ─── قسم كوادر الشفت ───────────────────────────────────────────────────
    merge_style(ws, row, 1, row, 9, "أولاً: القوى العاملة الحيوية",
                bold=True, size=13, bg="1A5276")
    row += 1

    headers = ["#", "القسم", "المسؤول", "رقم التواصل",
               "البيان المطلوب", "العدد / الحالة", "مؤشر التحضير", "ملاحظات"]
    cols_w  = [5, 30, 22, 16, 30, 18, 22, 25]
    for c, (h, w) in enumerate(zip(headers, cols_w), 1):
        ws.column_dimensions[get_column_letter(c)].width = w
        cell = ws.cell(row, c, h)
        style_cell(cell, bold=True, color="FFFFFF", bg=SUB_HEADER, size=11)
    row += 1

    readiness_map = {
        "جاهز":              ("✔ جاهز",              LIGHT_GREEN,  GREEN_COLOR),
        "لم يتم التجاوب":   ("⚠ لم يتم التجاوب",   LIGHT_RED,    RED_COLOR),
        "تحت الاستجابة":    ("⏳ تحت الاستجابة",    LIGHT_ORANGE, ORANGE_COLOR),
    }

    for idx, s in enumerate(report.get("staff", []), 1):
        readiness = s.get("readiness", "جاهز")
        r_text, r_bg, r_color = readiness_map.get(readiness,
                                 ("جاهز", LIGHT_GREEN, GREEN_COLOR))
        row_bg = WHITE if idx % 2 == 0 else GRAY_LIGHT
        values = [idx, s.get("department",""), s.get("responsible_name",""),
                  s.get("phone",""), s.get("requirement",""),
                  s.get("count_value",""), r_text, s.get("notes","")]
        for c, v in enumerate(values, 1):
            cell = ws.cell(row, c, v)
            bg = r_bg if c == 7 else row_bg
            fc = r_color if c == 7 else "000000"
            style_cell(cell, bg=bg, color=fc, size=10,
                       align="center" if c in (1,4,6,7) else "right")
        row += 1

    row += 1

    # ─── قسم السعة السريرية ────────────────────────────────────────────────
    merge_style(ws, row, 1, row, 9, "ثانياً: السعة السريرية",
                bold=True, size=13, bg="1A5276")
    row += 1

    bed_headers = ["#", "القسم / الوحدة", "إجمالي الأسرة",
                   "مشغول", "متاح", "نسبة الإشغال", "الحالة"]
    bed_widths  = [5, 45, 18, 14, 14, 18, 16]
    for c, (h, w) in enumerate(zip(bed_headers, bed_widths), 1):
        ws.column_dimensions[get_column_letter(c)].width = w
        cell = ws.cell(row, c, h)
        style_cell(cell, bold=True, color="FFFFFF", bg=SUB_HEADER, size=11)
    row += 1

    total_beds_sum = total_occ_sum = 0
    for idx, b in enumerate(report.get("beds", []), 1):
        total  = b.get("total_beds", 0) or 0
        occ    = b.get("occupied", 0) or 0
        avail  = total - occ
        pct    = round((occ / total * 100) if total > 0 else 0, 1)
        total_beds_sum += total
        total_occ_sum  += occ

        if pct >= 95:
            status, s_bg, s_fc = "⚠ ممتلئ",  LIGHT_RED,    RED_COLOR
        elif pct >= 80:
            status, s_bg, s_fc = "تنبيه",     LIGHT_ORANGE, ORANGE_COLOR
        else:
            status, s_bg, s_fc = "✔ متاح",   LIGHT_GREEN,  GREEN_COLOR

        row_bg = WHITE if idx % 2 == 0 else GRAY_LIGHT
        values = [idx, b.get("unit_name",""), total, occ, avail,
                  f"{pct}%", status]
        for c, v in enumerate(values, 1):
            cell = ws.cell(row, c, v)
            if c == 7:
                style_cell(cell, bg=s_bg, color=s_fc, size=10)
            elif c == 6:
                if pct >= 95:
                    style_cell(cell, bg=LIGHT_RED, color=RED_COLOR,
                               bold=True, size=10)
                elif pct >= 80:
                    style_cell(cell, bg=LIGHT_ORANGE, color=ORANGE_COLOR,
                               bold=True, size=10)
                else:
                    style_cell(cell, bg=row_bg, size=10)
            else:
                style_cell(cell, bg=row_bg, size=10,
                           align="right" if c == 2 else "center")
        row += 1

    # إجمالي
    total_avail = total_beds_sum - total_occ_sum
    total_pct   = round((total_occ_sum/total_beds_sum*100)
                        if total_beds_sum > 0 else 0, 1)
    merge_style(ws, row, 1, row, 2, "الإجمالي",
                bold=True, bg="1A5276", size=11)
    for c, v in enumerate([total_beds_sum, total_occ_sum,
                            total_avail, f"{total_pct}%", ""], 3):
        cell = ws.cell(row, c, v)
        style_cell(cell, bold=True, bg=LIGHT_BLUE, size=11)
    row += 2

    # ─── قسم أجهزة التنفس ──────────────────────────────────────────────────
    merge_style(ws, row, 1, row, 9, "ثالثاً: القدرة الحرجة (أجهزة التنفس الصناعي)",
                bold=True, size=13, bg="1A5276")
    row += 1

    vents = report.get("vents", {})
    on_v   = vents.get("on_vent", 0) or 0
    ready  = vents.get("ready_devices", 0) or 0
    total_d= vents.get("total_devices", 0) or 0
    avail_d= total_d - on_v
    pct_v  = round((ready/total_d*100) if total_d > 0 else 0, 1)

    vent_data = [
        ("مرضى على أجهزة التنفس", str(on_v), LIGHT_BLUE, "1A5276"),
        ("أجهزة جاهزة للاستخدام",  str(ready), LIGHT_GREEN, GREEN_COLOR),
        ("إجمالي الأجهزة",          str(total_d), LIGHT_BLUE, "1A5276"),
        ("الأجهزة المتاحة",         str(avail_d), LIGHT_GREEN, GREEN_COLOR),
        ("نسبة الجاهزية",           f"{pct_v}%",
         LIGHT_GREEN if pct_v >= 75 else (LIGHT_ORANGE if pct_v >= 50 else LIGHT_RED),
         GREEN_COLOR if pct_v >= 75 else (ORANGE_COLOR if pct_v >= 50 else RED_COLOR)),
    ]

    for label, val, bg, fc in vent_data:
        cell_l = ws.cell(row, 1, label)
        cell_v = ws.cell(row, 2, val)
        style_cell(cell_l, bold=True, bg=LIGHT_BLUE, size=11, align="right")
        style_cell(cell_v, bold=True, bg=bg, color=fc, size=14)
        ws.merge_cells(start_row=row, start_column=3,
                       end_row=row, end_column=9)
        row += 1

    # المسؤول
    resp_name  = vents.get("responsible_name", "")
    resp_phone = vents.get("responsible_phone", "")
    if resp_name:
        merge_style(ws, row, 1, row, 2,
                    f"المسؤول: {resp_name}  |  {resp_phone}",
                    bold=True, bg="154360", size=11)
        row += 1

    row += 1

    # ─── تذييل ─────────────────────────────────────────────────────────────
    merge_style(ws, row, 1, row, 9,
                f"إدارة التأهب للطوارئ والكوارث - مدينة الملك سلمان الطبية  |  "
                f"تم الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                size=10, bg="1A5276")

    # ضبط ارتفاع الصفوف
    for r in range(1, row+1):
        ws.row_dimensions[r].height = 22

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


# ─── تصدير PDF ────────────────────────────────────────────────────────────────

def build_report_html(report: dict, hospital_name: str,
                      hospital_subtitle: str,
                      logo_b64: str = "", emergency_logo_b64: str = "") -> str:
    """بناء HTML للتقرير (يُستخدم للـ PDF وطباعة الصفحة)"""
    report_date = report.get("report_date", "")
    shift       = report.get("shift", "")
    try:
        dt = datetime.strptime(report_date, "%Y-%m-%d")
        ar_days = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
        ar_months = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                     "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]
        day_name = ar_days[dt.weekday()]
        date_str = f"{dt.day} {ar_months[dt.month-1]} {dt.year}"
    except Exception:
        day_name = ""
        date_str = report_date

    readiness_styles = {
        "جاهز":            ("ready",    "✔ جاهز"),
        "لم يتم التجاوب": ("not-resp", "⚠ لم يتم التجاوب"),
        "تحت الاستجابة":  ("partial",  "⏳ تحت الاستجابة"),
    }

    # فحص الجاهزية الكلية
    staff_list = report.get("staff", [])
    all_ready = all(s.get("readiness","جاهز") == "جاهز" for s in staff_list)
    has_not_resp = any(s.get("readiness") == "لم يتم التجاوب" for s in staff_list)
    overall_class = "ready" if all_ready else ("not-resp" if has_not_resp else "partial")
    overall_text  = ("✔ جاهز" if all_ready else
                     ("⚠ لم يتم التجاوب" if has_not_resp else "⏳ تحت الاستجابة"))

    # إجمالي الأسرة
    beds = report.get("beds", [])
    total_beds = sum(b.get("total_beds", 0) or 0 for b in beds)
    total_occ  = sum(b.get("occupied", 0) or 0 for b in beds)
    total_avail= total_beds - total_occ
    total_pct  = round((total_occ/total_beds*100) if total_beds > 0 else 0, 1)

    # أجهزة التنفس
    vents   = report.get("vents", {})
    on_v    = vents.get("on_vent", 0) or 0
    ready_v = vents.get("ready_devices", 0) or 0
    total_v = vents.get("total_devices", 0) or 0
    avail_v = total_v - on_v
    pct_v   = round((ready_v/total_v*100) if total_v > 0 else 0, 1)
    vent_class = ("vent-green" if pct_v >= 75 else
                  ("vent-orange" if pct_v >= 50 else "vent-red"))

    logo_html = (f'<img src="data:image/png;base64,{logo_b64}" class="logo-img" alt="شعار">'
                 if logo_b64 else
                 '<div class="logo-placeholder">شعار المستشفى</div>')
    emg_logo_html = (f'<img src="data:image/png;base64,{emergency_logo_b64}" '
                     f'class="logo-img" alt="شعار الطوارئ">'
                     if emergency_logo_b64 else
                     '<div class="logo-placeholder">إدارة التأهب</div>')

    # بناء صفوف كوادر الشفت
    staff_rows = ""
    for idx, s in enumerate(staff_list, 1):
        rd = s.get("readiness", "جاهز")
        cls, txt = readiness_styles.get(rd, ("ready", rd))
        staff_rows += f"""
        <tr class="row-{'even' if idx%2==0 else 'odd'}">
          <td class="tc">{idx}</td>
          <td class="tr">{s.get('department','')}</td>
          <td class="tr">{s.get('responsible_name','')}</td>
          <td class="tc">{s.get('phone','')}</td>
          <td class="tr">{s.get('requirement','')}</td>
          <td class="tc bold">{s.get('count_value','')}</td>
          <td class="tc"><span class="badge {cls}">{txt}</span></td>
          <td class="tr small">{s.get('notes','')}</td>
        </tr>"""

    # بناء صفوف الأسرة
    bed_rows = ""
    for idx, b in enumerate(beds, 1):
        total = b.get("total_beds", 0) or 0
        occ   = b.get("occupied", 0) or 0
        avail = total - occ
        pct   = round((occ/total*100) if total > 0 else 0, 1)
        if pct >= 95:
            pcls = "pct-red"
        elif pct >= 80:
            pcls = "pct-orange"
        else:
            pcls = "pct-green"
        bar_w = min(100, int(pct))
        bed_rows += f"""
        <tr class="row-{'even' if idx%2==0 else 'odd'}">
          <td class="tc">{idx}</td>
          <td class="tr">{b.get('unit_name','')}</td>
          <td class="tc">{total}</td>
          <td class="tc">{occ}</td>
          <td class="tc">{avail}</td>
          <td class="tc">
            <div class="bar-wrap">
              <div class="bar-fill {pcls}" style="width:{bar_w}%"></div>
              <span class="bar-txt">{pct}%</span>
            </div>
          </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<style>
  @import url('data:text/css,');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: 'Cairo', 'Tahoma', 'Arial Unicode MS', Arial, sans-serif;
    font-size: 10pt;
    color: #1a1a1a;
    background: #fff;
    direction: rtl;
  }}
  .page {{
    width: 100%;
    padding: 8mm;
  }}
  /* ─── Header ─── */
  .header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, #1B4F8A 0%, #2E86C1 100%);
    color: #fff;
    padding: 8px 12px;
    border-radius: 8px;
    margin-bottom: 6px;
  }}
  .header-center {{ text-align: center; flex: 1; }}
  .header-center h1 {{ font-size: 14pt; font-weight: bold; margin-bottom: 2px; }}
  .header-center .subtitle {{ font-size: 8pt; opacity: 0.9; }}
  .header-center .date-line {{ font-size: 9pt; margin-top: 3px; }}
  .logo-img {{ width: 60px; height: 60px; object-fit: contain; }}
  .logo-placeholder {{ width: 60px; height: 60px; background: rgba(255,255,255,0.2);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 7pt; text-align: center; padding: 4px; }}
  .badge-overall {{
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-weight: bold; font-size: 10pt; margin-top: 4px;
  }}
  .badge-overall.ready    {{ background:#1E8449; color:#fff; }}
  .badge-overall.not-resp {{ background:#C0392B; color:#fff; }}
  .badge-overall.partial  {{ background:#D35400; color:#fff; }}

  /* ─── Section titles ─── */
  .sec-title {{
    background: #1A5276; color: #fff; font-weight: bold;
    padding: 5px 10px; font-size: 10pt; border-radius: 4px;
    margin: 5px 0 3px;
  }}

  /* ─── Tables ─── */
  table {{ width: 100%; border-collapse: collapse; font-size: 8.5pt; }}
  th {{
    background: #2E86C1; color: #fff; padding: 4px 6px;
    text-align: center; font-weight: bold;
    border: 1px solid #1B4F8A;
  }}
  td {{ padding: 3px 5px; border: 1px solid #ddd; }}
  tr.row-odd  {{ background: #F8F9FA; }}
  tr.row-even {{ background: #FFFFFF; }}
  .tc {{ text-align: center; }}
  .tr {{ text-align: right;  }}
  .bold {{ font-weight: bold; }}
  .small {{ font-size: 7.5pt; }}

  /* ─── Badges ─── */
  .badge {{ display:inline-block; padding:2px 8px; border-radius:10px;
    font-size: 8pt; font-weight: bold; }}
  .badge.ready    {{ background:#D5F5E3; color:#1E8449; }}
  .badge.not-resp {{ background:#FADBD8; color:#C0392B; animation: none; }}
  .badge.partial  {{ background:#FDEBD0; color:#D35400; }}

  /* ─── Progress bars ─── */
  .bar-wrap {{ position: relative; background:#eee; border-radius:4px;
    height: 14px; width: 100%; }}
  .bar-fill {{ height: 100%; border-radius:4px; }}
  .bar-fill.pct-green  {{ background:#1E8449; }}
  .bar-fill.pct-orange {{ background:#D35400; }}
  .bar-fill.pct-red    {{ background:#C0392B; }}
  .bar-txt {{ position:absolute; left:50%; top:0; transform:translateX(-50%);
    font-size:7pt; font-weight:bold; color:#fff; line-height:14px; }}

  /* ─── Vent section ─── */
  .vent-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 6px;
    margin: 4px 0;
  }}
  .vent-card {{
    text-align: center; padding: 6px; border-radius: 6px;
    background: #D6EAF8;
  }}
  .vent-card .vc-num {{ font-size: 18pt; font-weight: bold; }}
  .vent-card .vc-lbl {{ font-size: 7pt; color: #555; }}
  .vent-card.vent-green  {{ background:#D5F5E3; }}
  .vent-card.vent-green .vc-num {{ color: #1E8449; }}
  .vent-card.vent-orange {{ background:#FDEBD0; }}
  .vent-card.vent-orange .vc-num {{ color: #D35400; }}
  .vent-card.vent-red    {{ background:#FADBD8; }}
  .vent-card.vent-red    .vc-num {{ color: #C0392B; }}
  .vent-resp {{
    background:#154360; color:#fff; padding:4px 10px;
    border-radius:4px; font-size:8.5pt; margin-top:4px;
    display:inline-block;
  }}

  /* ─── Footer ─── */
  .footer {{
    display: flex; align-items: center; justify-content: space-between;
    background: #1A5276; color: #fff; padding: 5px 12px;
    border-radius: 6px; margin-top: 6px; font-size: 8pt;
  }}
  .total-row td {{ background: #D6EAF8; font-weight: bold; }}
  .pct-red-cell {{ background:#FADBD8 !important; color:#C0392B; font-weight:bold; }}
  .pct-orange-cell {{ background:#FDEBD0 !important; color:#D35400; font-weight:bold; }}
  .pct-green-cell  {{ background:#D5F5E3 !important; color:#1E8449; font-weight:bold; }}
</style>
</head>
<body>
<div class="page">

<!-- ═══ HEADER ═══ -->
<div class="header">
  {logo_html}
  <div class="header-center">
    <h1>{hospital_name}</h1>
    <div class="subtitle">{hospital_subtitle}</div>
    <div class="date-line">
      <strong>تقرير جاهزية الأقسام الحيوية</strong> &nbsp;|&nbsp;
      {date_str} - {day_name} &nbsp;|&nbsp; الشفت: <strong>{shift}</strong>
    </div>
    <span class="badge-overall {overall_class}">{overall_text}</span>
  </div>
  {emg_logo_html}
</div>

<!-- ═══ SECTION 1: STAFF ═══ -->
<div class="sec-title">أولاً: القوى العاملة الحيوية</div>
<table>
  <thead>
    <tr>
      <th style="width:4%">#</th>
      <th style="width:20%">القسم</th>
      <th style="width:16%">المسؤول</th>
      <th style="width:13%">رقم التواصل</th>
      <th style="width:20%">البيان المطلوب</th>
      <th style="width:10%">العدد/الحالة</th>
      <th style="width:13%">مؤشر التحضير</th>
      <th style="width:14%">ملاحظات</th>
    </tr>
  </thead>
  <tbody>{staff_rows}</tbody>
</table>

<!-- ═══ SECTION 2+3 split ═══ -->
<div style="display:flex; gap:8px; margin-top:4px;">

  <!-- Beds -->
  <div style="flex:3;">
    <div class="sec-title">ثانياً: السعة السريرية</div>
    <table>
      <thead>
        <tr>
          <th style="width:5%">#</th>
          <th style="width:40%">القسم / الوحدة</th>
          <th style="width:12%">الإجمالي</th>
          <th style="width:12%">مشغول</th>
          <th style="width:12%">متاح</th>
          <th style="width:19%">الإشغال%</th>
        </tr>
      </thead>
      <tbody>
        {bed_rows}
        <tr class="total-row">
          <td class="tc" colspan="2"><strong>الإجمالي</strong></td>
          <td class="tc"><strong>{total_beds}</strong></td>
          <td class="tc"><strong>{total_occ}</strong></td>
          <td class="tc"><strong>{total_avail}</strong></td>
          <td class="tc {'pct-red-cell' if total_pct>=95 else ('pct-orange-cell' if total_pct>=80 else 'pct-green-cell')}">
            <strong>{total_pct}%</strong>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Vents -->
  <div style="flex:2;">
    <div class="sec-title">ثالثاً: القدرة الحرجة (أجهزة التنفس)</div>
    <div class="vent-grid">
      <div class="vent-card">
        <div class="vc-num" style="color:#1A5276">{on_v}</div>
        <div class="vc-lbl">مرضى على Vent</div>
      </div>
      <div class="vent-card vent-green">
        <div class="vc-num">{ready_v}</div>
        <div class="vc-lbl">أجهزة جاهزة</div>
      </div>
      <div class="vent-card">
        <div class="vc-num" style="color:#1A5276">{total_v}</div>
        <div class="vc-lbl">إجمالي الأجهزة</div>
      </div>
      <div class="vent-card vent-green">
        <div class="vc-num">{avail_v}</div>
        <div class="vc-lbl">الأجهزة المتاحة</div>
      </div>
      <div class="vent-card {vent_class}">
        <div class="vc-num">{pct_v}%</div>
        <div class="vc-lbl">نسبة الجاهزية</div>
      </div>
    </div>
    {'<div class="vent-resp">المسؤول: ' + vents.get("responsible_name","") + ' &nbsp;|&nbsp; ' + vents.get("responsible_phone","") + '</div>' if vents.get("responsible_name") else ""}
  </div>
</div>

<!-- ═══ FOOTER ═══ -->
<div class="footer">
  {emg_logo_html}
  <span>إدارة التأهب للطوارئ والكوارث - مدينة الملك سلمان الطبية</span>
  <span>تاريخ الطباعة: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
  {logo_html}
</div>

</div>
</body>
</html>"""
    return html


def export_pdf(report: dict, hospital_name: str = "مستشفى الولادة والأطفال",
               hospital_subtitle: str = "", logo_b64: str = "",
               emergency_logo_b64: str = "") -> bytes:
    """تصدير التقرير كملف PDF"""
    html = build_report_html(report, hospital_name, hospital_subtitle,
                             logo_b64, emergency_logo_b64)

    # محاولة WeasyPrint أولاً
    try:
        import weasyprint
        pdf = weasyprint.HTML(string=html).write_pdf()
        return pdf
    except ImportError:
        pass
    except Exception as e:
        print(f"WeasyPrint error: {e}")

    # الرجوع إلى pdfkit
    try:
        import pdfkit
        options = {
            'page-size': 'A3',
            'orientation': 'Landscape',
            'encoding': 'UTF-8',
            'no-outline': None,
            'quiet': '',
        }
        pdf = pdfkit.from_string(html, False, options=options)
        return pdf
    except ImportError:
        pass
    except Exception as e:
        print(f"pdfkit error: {e}")

    # إذا لم تتوفر مكتبات PDF، إرجاع HTML كـ fallback
    # (سيُعرض في المتصفح عبر print)
    raise RuntimeError(
        "لم يتم تثبيت مكتبة PDF. يرجى تثبيت weasyprint أو pdfkit.\n"
        "pip install weasyprint\nأو: pip install pdfkit"
    )
