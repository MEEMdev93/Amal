"""
database.py - نظام قياس جاهزية الأقسام الحيوية اليومية
مستشفى الولادة والأطفال بالمدينة المنورة
"""
import sqlite3
import os
from datetime import datetime, timedelta, date
import hashlib
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "emergency.db")

def get_db():
    """إنشاء اتصال بقاعدة البيانات"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def hash_password(password: str) -> str:
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    conn = get_db()
    cur = conn.cursor()

    # جدول المستخدمين
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','operator','viewer')),
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # جدول دليل الكوادر
    cur.execute("""
        CREATE TABLE IF NOT EXISTS staff_directory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            phone TEXT,
            role_title TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # جدول قوالب الأقسام
    cur.execute("""
        CREATE TABLE IF NOT EXISTS departments_template (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            requirement_label TEXT,
            sort_order INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        )
    """)

    # جدول قوالب وحدات الأسرة
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bed_units_template (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_name TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        )
    """)

    # جدول التقارير اليومية
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_report (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT UNIQUE NOT NULL,
            shift TEXT NOT NULL CHECK(shift IN ('صباحي','مسائي','ليلي')),
            created_by INTEGER,
            updated_by INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY(created_by) REFERENCES users(id),
            FOREIGN KEY(updated_by) REFERENCES users(id)
        )
    """)

    # جدول كوادر الشفت اليومية
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            department TEXT NOT NULL,
            responsible_name TEXT,
            phone TEXT,
            requirement TEXT,
            count_value TEXT,
            readiness TEXT DEFAULT 'جاهز',
            notes TEXT,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY(report_id) REFERENCES daily_report(id) ON DELETE CASCADE
        )
    """)

    # جدول السعة السريرية اليومية
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_beds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            unit_name TEXT NOT NULL,
            total_beds INTEGER DEFAULT 0,
            occupied INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY(report_id) REFERENCES daily_report(id) ON DELETE CASCADE
        )
    """)

    # جدول أجهزة التنفس اليومية
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_vents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL UNIQUE,
            on_vent INTEGER DEFAULT 0,
            ready_devices INTEGER DEFAULT 0,
            total_devices INTEGER DEFAULT 0,
            responsible_name TEXT,
            responsible_phone TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_report(id) ON DELETE CASCADE
        )
    """)

    # جدول الإعدادات
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()

    # إدراج البيانات الافتراضية
    _seed_users(conn)
    _seed_departments(conn)
    _seed_bed_units(conn)
    _seed_staff_directory(conn)
    _seed_test_data(conn)
    _seed_settings(conn)

    conn.close()
    print("✅ تم تهيئة قاعدة البيانات بنجاح")

def _seed_users(conn):
    """إنشاء المستخدمين الافتراضيين"""
    cur = conn.cursor()
    users = [
        ("admin",    "مدير النظام",          "admin",    hash_password("Admin@1234")),
        ("operator", "مشغّل البيانات",       "operator", hash_password("Op@1234")),
        ("viewer",   "مستعرض التقارير",      "viewer",   hash_password("View@1234")),
    ]
    for username, full_name, role, pwd_hash in users:
        cur.execute(
            "INSERT OR IGNORE INTO users (username, full_name, role, password_hash) VALUES (?,?,?,?)",
            (username, full_name, role, pwd_hash)
        )
    conn.commit()

def _seed_departments(conn):
    """إنشاء قوالب الأقسام الافتراضية"""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM departments_template")
    if cur.fetchone()[0] > 0:
        return
    departments = [
        ("الإدارة الطبية والمدراء المناوبين", "عدد الأطباء بالفترة", 1),
        ("التمريض",                           "عدد التمريض بالفترة", 2),
        ("العلاج التنفسي",                    "عدد RT بالفترة",      3),
        ("الصيانة",                           "جاهزية الأجهزة / لا أعطال مؤثرة", 4),
        ("الأمن والسلامة",                    "جاهزية السلامة / المخارج / الإنذار", 5),
        ("طوارئ الأطفال",                     "عدد الأطباء في الشفت", 6),
        ("إدارة الأسرة",                      "مطابقة عدد الأسرة",   7),
    ]
    for name, req, order in departments:
        cur.execute(
            "INSERT OR IGNORE INTO departments_template (name, requirement_label, sort_order) VALUES (?,?,?)",
            (name, req, order)
        )
    conn.commit()

def _seed_bed_units(conn):
    """إنشاء قوالب وحدات الأسرة الافتراضية"""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bed_units_template")
    if cur.fetchone()[0] > 0:
        return
    units = [
        ("قسم العناية المركزة - العناية المركزة للأطفال (PICU)",  1),
        ("عناية مركزة أطفال - غرفة عزل",                         2),
        ("قسم العناية المركزة - وحدة العناية المركزة للبالغين (ICU)", 3),
        ("عناية مركزة بالغين - غرفة عزل",                        4),
        ("أقسام النساء والولادة - قسم النساء والولادة",           5),
        ("قسم النساء والولادة - غرفة عزل",                       6),
        ("قسم الأطفال - طب الأطفال العام",                       7),
        ("قسم الأطفال - غرفة عزل",                               8),
    ]
    for name, order in units:
        cur.execute(
            "INSERT OR IGNORE INTO bed_units_template (unit_name, sort_order) VALUES (?,?)",
            (name, order)
        )
    conn.commit()

def _seed_staff_directory(conn):
    """إنشاء دليل الكوادر الافتراضي"""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM staff_directory")
    if cur.fetchone()[0] > 0:
        return
    staff = [
        ("د. محمد العتيبي",     "الإدارة الطبية والمدراء المناوبين", "0501234567", "مدير طبي مناوب"),
        ("د. سارة المالكي",     "الإدارة الطبية والمدراء المناوبين", "0501234568", "طبيبة مناوبة"),
        ("أ. فاطمة الغامدي",    "التمريض",                           "0507654321", "رئيسة تمريض"),
        ("أ. نورة الشهري",      "التمريض",                           "0507654322", "ممرضة أولى"),
        ("أ. ريان المدني",      "العلاج التنفسي",                    "0533961766", "أخصائي علاج تنفسي"),
        ("أ. خالد الدوسري",     "العلاج التنفسي",                    "0533961767", "أخصائي علاج تنفسي"),
        ("م. عبدالله القحطاني", "الصيانة",                           "0512345678", "مهندس صيانة"),
        ("م. سلطان العمري",     "الصيانة",                           "0512345679", "فني صيانة"),
        ("أ. أحمد الزهراني",    "الأمن والسلامة",                    "0598765432", "مسؤول الأمن"),
        ("أ. يوسف البقمي",      "الأمن والسلامة",                    "0598765433", "مشرف سلامة"),
        ("د. عمر الحربي",       "طوارئ الأطفال",                     "0556789012", "طبيب طوارئ أطفال"),
        ("د. مريم السبيعي",     "طوارئ الأطفال",                     "0556789013", "طبيبة طوارئ أطفال"),
        ("أ. هند المطيري",      "إدارة الأسرة",                      "0534567890", "مسؤولة إدارة الأسرة"),
    ]
    for name, dept, phone, title in staff:
        cur.execute(
            "INSERT OR IGNORE INTO staff_directory (name, department, phone, role_title) VALUES (?,?,?,?)",
            (name, dept, phone, title)
        )
    conn.commit()

def _seed_test_data(conn):
    """إدراج بيانات تجريبية لـ 7 أيام سابقة"""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM daily_report")
    if cur.fetchone()[0] >= 7:
        return

    shifts = ["صباحي", "مسائي", "ليلي"]
    readiness_opts = ["جاهز", "جاهز", "جاهز", "لم يتم التجاوب", "تحت الاستجابة"]

    departments_data = [
        ("الإدارة الطبية والمدراء المناوبين", "د. محمد العتيبي",  "0501234567", "عدد الأطباء بالفترة"),
        ("التمريض",                           "أ. فاطمة الغامدي", "0507654321", "عدد التمريض بالفترة"),
        ("العلاج التنفسي",                    "أ. ريان المدني",   "0533961766", "عدد RT بالفترة"),
        ("الصيانة",                           "م. عبدالله القحطاني","0512345678","جاهزية الأجهزة / لا أعطال مؤثرة"),
        ("الأمن والسلامة",                    "أ. أحمد الزهراني", "0598765432", "جاهزية السلامة / المخارج / الإنذار"),
        ("طوارئ الأطفال",                     "د. عمر الحربي",    "0556789012", "عدد الأطباء في الشفت"),
        ("إدارة الأسرة",                      "أ. هند المطيري",   "0534567890", "مطابقة عدد الأسرة"),
    ]

    beds_data = [
        ("قسم العناية المركزة - العناية المركزة للأطفال (PICU)",  27, 24),
        ("عناية مركزة أطفال - غرفة عزل",                         3,  1),
        ("قسم العناية المركزة - وحدة العناية المركزة للبالغين (ICU)", 7, 7),
        ("عناية مركزة بالغين - غرفة عزل",                        1,  0),
        ("أقسام النساء والولادة - قسم النساء والولادة",           174,163),
        ("قسم النساء والولادة - غرفة عزل",                       5,  2),
        ("قسم الأطفال - طب الأطفال العام",                       190,166),
        ("قسم الأطفال - غرفة عزل",                               9,  5),
    ]

    today = date.today()
    for i in range(7, 0, -1):
        report_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        shift = shifts[i % 3]

        # تحقق من وجود التقرير
        cur.execute("SELECT id FROM daily_report WHERE report_date=?", (report_date,))
        existing = cur.fetchone()
        if existing:
            continue

        cur.execute(
            "INSERT INTO daily_report (report_date, shift, created_by, updated_by, notes) VALUES (?,?,1,1,?)",
            (report_date, shift, f"بيانات تجريبية - يوم {i}")
        )
        report_id = cur.lastrowid

        # إدراج كوادر الشفت
        for idx, (dept, name, phone, req) in enumerate(departments_data):
            count_vals = ["3", "12", "4", "جاهز", "جاهز", "5", "متطابق"]
            readiness = random.choice(readiness_opts)
            cur.execute("""
                INSERT INTO daily_staff (report_id, department, responsible_name, phone,
                    requirement, count_value, readiness, sort_order)
                VALUES (?,?,?,?,?,?,?,?)
            """, (report_id, dept, name, phone, req, count_vals[idx], readiness, idx+1))

        # إدراج السعة السريرية مع تباين بسيط
        for idx, (unit, total, occ) in enumerate(beds_data):
            variation = random.randint(-3, 3)
            occupied = max(0, min(total, occ + variation))
            cur.execute("""
                INSERT INTO daily_beds (report_id, unit_name, total_beds, occupied, sort_order)
                VALUES (?,?,?,?,?)
            """, (report_id, unit, total, occupied, idx+1))

        # إدراج بيانات أجهزة التنفس
        on_vent = random.randint(48, 56)
        ready = random.randint(140, 150)
        cur.execute("""
            INSERT INTO daily_vents (report_id, on_vent, ready_devices, total_devices,
                responsible_name, responsible_phone)
            VALUES (?,?,?,172,?,?)
        """, (report_id, on_vent, ready, "أ / ريان المدني", "0533961766"))

    conn.commit()

def _seed_settings(conn):
    """إنشاء الإعدادات الافتراضية"""
    cur = conn.cursor()
    defaults = [
        ("hospital_name",     "مستشفى الولادة والأطفال بالمدينة المنورة"),
        ("hospital_subtitle", "إدارة التأهب للطوارئ والكوارث بمدينة الملك سلمان الطبية"),
        ("hospital_logo",     ""),
        ("emergency_logo",    ""),
    ]
    for key, value in defaults:
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()

# ─── دوال مساعدة ─────────────────────────────────────────────────────────────

def get_setting(key: str, default: str = "") -> str:
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key: str, value: str):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()

def get_departments_template():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM departments_template WHERE active=1 ORDER BY sort_order"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_bed_units_template():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM bed_units_template WHERE active=1 ORDER BY sort_order"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_report_by_date(report_date: str):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM daily_report WHERE report_date=?", (report_date,)
    ).fetchone()
    if not row:
        conn.close()
        return None
    report = dict(row)
    report["staff"] = [dict(r) for r in conn.execute(
        "SELECT * FROM daily_staff WHERE report_id=? ORDER BY sort_order", (report["id"],)
    ).fetchall()]
    report["beds"] = [dict(r) for r in conn.execute(
        "SELECT * FROM daily_beds WHERE report_id=? ORDER BY sort_order", (report["id"],)
    ).fetchall()]
    vent = conn.execute(
        "SELECT * FROM daily_vents WHERE report_id=?", (report["id"],)
    ).fetchone()
    report["vents"] = dict(vent) if vent else {}
    conn.close()
    return report

def get_report_by_id(report_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM daily_report WHERE id=?", (report_id,)).fetchone()
    if not row:
        conn.close()
        return None
    report = dict(row)
    report["staff"] = [dict(r) for r in conn.execute(
        "SELECT * FROM daily_staff WHERE report_id=? ORDER BY sort_order", (report_id,)
    ).fetchall()]
    report["beds"] = [dict(r) for r in conn.execute(
        "SELECT * FROM daily_beds WHERE report_id=? ORDER BY sort_order", (report_id,)
    ).fetchall()]
    vent = conn.execute(
        "SELECT * FROM daily_vents WHERE report_id=?", (report_id,)
    ).fetchone()
    report["vents"] = dict(vent) if vent else {}
    conn.close()
    return report

def get_reports_range(start_date: str, end_date: str):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM daily_report WHERE report_date BETWEEN ? AND ? ORDER BY report_date",
        (start_date, end_date)
    ).fetchall()
    result = []
    for row in rows:
        r = dict(row)
        r["staff"] = [dict(x) for x in conn.execute(
            "SELECT * FROM daily_staff WHERE report_id=? ORDER BY sort_order", (r["id"],)
        ).fetchall()]
        r["beds"] = [dict(x) for x in conn.execute(
            "SELECT * FROM daily_beds WHERE report_id=? ORDER BY sort_order", (r["id"],)
        ).fetchall()]
        vent = conn.execute(
            "SELECT * FROM daily_vents WHERE report_id=?", (r["id"],)
        ).fetchone()
        r["vents"] = dict(vent) if vent else {}
        result.append(r)
    conn.close()
    return result
